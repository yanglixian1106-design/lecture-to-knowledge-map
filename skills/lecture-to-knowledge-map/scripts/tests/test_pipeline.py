import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pypdf import PdfWriter

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import lecture_pipeline as lp
from validate_notes import validate

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pdf = self.root / 'slides.pdf'
        self.write_pdf(2)
    def tearDown(self): self.tmp.cleanup()
    def write_pdf(self, count):
        w = PdfWriter()
        for _ in range(count): w.add_blank_page(width=200, height=200)
        w.write(self.pdf)
    def invoke(self, *args):
        out = io.StringIO()
        with patch.object(sys, 'argv', ['pipeline', *map(str,args)]), contextlib.redirect_stdout(out): lp.main()
        return out.getvalue()
    def test_image_only_and_mixed_pages_remain_pending(self):
        from pypdf.generic import DictionaryObject, NameObject, NumberObject, DecodedStreamObject, ArrayObject, TextStringObject
        w=PdfWriter()
        for mixed in (False, True):
            page=w.add_blank_page(width=200,height=200)
            img=DecodedStreamObject(); img.set_data(bytes([255,0,0]))
            img.update({NameObject('/Type'):NameObject('/XObject'),NameObject('/Subtype'):NameObject('/Image'),NameObject('/Width'):NumberObject(1),NameObject('/Height'):NumberObject(1),NameObject('/ColorSpace'):NameObject('/DeviceRGB'),NameObject('/BitsPerComponent'):NumberObject(8)})
            font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
            page[NameObject('/Resources')]=DictionaryObject({NameObject('/XObject'):DictionaryObject({NameObject('/Im1'):w._add_object(img)}),NameObject('/Font'):DictionaryObject({NameObject('/F1'):w._add_object(font)})})
            content=DecodedStreamObject();content.set_data(b'q 80 0 0 80 10 10 cm /Im1 Do Q'+(b' BT /F1 12 Tf 10 150 Td (Mean and variance) Tj ET' if mixed else b''))
            page[NameObject('/Contents')]=w._add_object(content)
            annotation=DictionaryObject({NameObject('/Subtype'):NameObject('/Text'),NameObject('/Contents'):TextStringObject('Preserve this annotation'),NameObject('/Rect'):ArrayObject([NumberObject(x) for x in (0,0,10,10)])})
            page[NameObject('/Annots')]=ArrayObject([w._add_object(annotation)])
        w.write(self.pdf)
        folder,_=lp.prepare(self.pdf,self.root/'cache');m=lp.read(folder/'manifest.json')
        self.assertEqual(m['pages'][0]['chars'],0)
        self.assertGreater(m['pages'][1]['chars'],0)
        self.assertEqual(m['pages'][0]['annotations'][0]['/Contents'],'Preserve this annotation')
        self.assertEqual(json.loads(self.invoke('status',folder))['pending']['visual'],[1,2])

    def test_cache_change_and_corruption(self):
        folder, hit = lp.prepare(self.pdf, self.root / 'cache'); self.assertFalse(hit)
        self.assertTrue(lp.prepare(self.pdf, self.root / 'cache')[1])
        (folder/'page-0001.txt').write_text('corrupted')
        self.assertFalse(lp.prepare(self.pdf, self.root / 'cache')[1])
        self.write_pdf(3)
        changed, hit = lp.prepare(self.pdf, self.root/'cache')
        self.assertNotEqual(folder, changed); self.assertFalse(hit)
    def test_resume_and_asset_invalidation(self):
        folder, _ = lp.prepare(self.pdf, self.root/'cache')
        asset = self.root/'image.png'; asset.write_bytes(b'fixture')
        self.invoke('mark', folder, '--pages','1','--kind','visual','--asset',asset,'--evidence','Inspected')
        state = json.loads(self.invoke('status', folder))
        self.assertEqual(state['pending']['visual'], [2])
        self.assertEqual(state['pending']['text'], [1,2])
        asset.write_bytes(b'changed')
        self.assertEqual(json.loads(self.invoke('status', folder))['stale_assets'], ['1:visual'])
        with self.assertRaises(ValueError): self.invoke('mark', folder,'--pages','2','--kind','visual','--evidence','No asset')
    def test_bounded_read_and_continuation(self):
        folder,_=lp.prepare(self.pdf,self.root/'cache')
        (folder/'page-0001.txt').write_text('abcdefghij')
        a=self.invoke('read',folder,'--pages','1','--max-chars','4')
        b=self.invoke('read',folder,'--pages','1','--max-chars','4','--offset','4')
        self.assertIn('abcd',a); self.assertIn('--offset 4',a); self.assertIn('efgh',b)
        self.assertEqual(lp.read(folder/'metrics.json')['returned_chars'],8)
        self.assertEqual(json.loads(self.invoke('status',folder))['pending']['text'],[1,2])
    def test_escaped_links_bounds_missing_attachment(self):
        notes=self.root/'notes';notes.mkdir()
        index=self.root/'Note.md'; index.write_text('[[notes/A]]')
        note=notes/'A.md'; note.write_text('[[Note]]\n| [[slides.pdf#page=2&selection=0,0,2,7&color=yellow\\|page]] |')
        self.assertEqual(validate(self.root,index,notes)[0],[])
        note.write_text('[[Note]] [[slides.pdf#page=3\\|page]] [[missing.png]]')
        errors,_=validate(self.root,index,notes)
        self.assertTrue(any('outside document' in x for x in errors))
        self.assertTrue(any('missing wiki target' in x for x in errors))
    def test_scaffold_and_no_overwrite(self):
        body=self.root/'body';body.write_text('English definition. 中文解释。')
        plan={'title':'Course','index':'Note.md','sources':[{'pdf':'slides.pdf','page_count':2}], 'notes':[{'path':'notes/A.md','title':'Estimator（估计量）','body':str(body),'sources':[{'pdf':'slides.pdf','pages':[1,2]}]}]}
        spec=self.root/'plan.json';lp.save(spec,plan)
        staging=self.root/'stage';self.invoke('scaffold',spec,'--output',staging)
        (staging/'slides.pdf').write_bytes(self.pdf.read_bytes())
        self.assertEqual(validate(staging,staging/'Note.md',staging)[0],[])
        self.assertIn('#page=2', (staging/'页码索引.md').read_text())
        with self.assertRaises(FileExistsError): self.invoke('scaffold',spec,'--output',staging)
    @unittest.skipUnless(lp.shutil.which('pdftoppm'), 'Poppler unavailable')
    def test_render_cache_and_changed_asset(self):
        folder,_=lp.prepare(self.pdf,self.root/'cache')
        result=lp.render(folder,[1],72);asset=Path(result[0]['path']);stamp=asset.stat().st_mtime_ns
        lp.render(folder,[1],72);self.assertEqual(stamp,asset.stat().st_mtime_ns)
        asset.write_bytes(b'broken');lp.render(folder,[1],72)
        self.assertEqual(lp.digest(asset),result[0]['sha256'])
        self.write_pdf(3)
        with self.assertRaises(ValueError): lp.render(folder,[1],72)

if __name__=='__main__': unittest.main()
