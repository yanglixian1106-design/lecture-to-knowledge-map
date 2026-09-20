#!/usr/bin/env python3
"""Cached PDF preparation, bounded reading, explicit review ledger and note scaffolds."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import time

VERSION = 1

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def pages(spec, count):
    result = set()
    for part in spec.split(','):
        bounds = part.split('-')
        a, b = (int(bounds[0]), int(bounds[-1]))
        if len(bounds) > 2 or a < 1 or b < a or b > count:
            raise ValueError('page range outside PDF')
        result.update(range(a, b + 1))
    return sorted(result)

def prepare(pdf, cache):
    import pypdf
    pdf, cache = Path(pdf).resolve(), Path(cache)
    key = hashlib.sha256((digest(pdf) + f':{VERSION}:{pypdf.__version__}').encode()).hexdigest()
    folder = cache / key
    manifest = folder / 'manifest.json'
    if manifest.exists():
        m = read(manifest)
        if all((folder / x['text']).exists() and digest(folder / x['text']) == x.get('text_sha256') for x in m['pages']):
            return folder, True
    folder.mkdir(parents=True, exist_ok=True)
    reader = pypdf.PdfReader(pdf)
    rows = []
    for n, page in enumerate(reader.pages, 1):
        name = f'page-{n:04}.txt'
        content = page.extract_text() or ''
        (folder / name).write_text(content, encoding='utf-8')
        annotations = []
        for ref in page.get('/Annots', []):
            obj = ref.get_object()
            annotations.append({k: str(obj[k]) for k in ('/Subtype', '/Contents', '/Rect') if k in obj})
        rows.append({'page': n, 'text': name, 'text_sha256': digest(folder / name), 'chars': len(content), 'annotations': annotations})
    if (folder / 'review.json').exists():
        (folder / 'review.json').unlink()  # Rebuilt extraction requires renewed review.
    save(manifest, {'version': VERSION, 'source': str(pdf), 'sha256': digest(pdf), 'pages': rows})
    return folder, False

def render(folder, selected, dpi):
    m = read(folder / 'manifest.json')
    source = Path(m['source'])
    if digest(source) != m['sha256']:
        raise ValueError('source changed; prepare again before rendering')
    tool = shutil.which('pdftoppm')
    if not tool:
        raise ValueError('pdftoppm unavailable')
    renderer = subprocess.run([tool, '-v'], capture_output=True, text=True).stderr.strip()
    rkey = hashlib.sha256(renderer.encode()).hexdigest()[:12]
    results = []
    for n in selected:
        base = folder / f'page-{n:04}-{dpi}-{rkey}'
        output = base.with_suffix('.png')
        stamp = base.with_suffix('.sha256')
        if not output.exists() or not stamp.exists() or stamp.read_text() != digest(output):
            subprocess.run([tool, '-f', str(n), '-l', str(n), '-singlefile', '-r', str(dpi), '-png', str(source), str(base)], check=True, capture_output=True)
            stamp.write_text(digest(output))
        results.append({'page': n, 'path': str(output.resolve()), 'sha256': digest(output)})
    return results

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('preflight')
    s = sub.add_parser('prepare'); s.add_argument('pdf', type=Path); s.add_argument('--cache', type=Path, required=True)
    for cmd in ('read', 'render', 'mark', 'status'):
        s = sub.add_parser(cmd); s.add_argument('folder', type=Path)
        if cmd != 'status': s.add_argument('--pages', required=True)
        if cmd == 'read':
            s.add_argument('--max-chars', type=int, default=16000)
            s.add_argument('--offset', type=int, default=0, help='Single-page continuation only')
        if cmd == 'render': s.add_argument('--dpi', type=int, default=100)
        if cmd == 'mark':
            s.add_argument('--kind', choices=['text', 'visual', 'verified'], required=True)
            s.add_argument('--evidence', required=True)
            s.add_argument('--asset', type=Path)
    s = sub.add_parser('scaffold'); s.add_argument('plan', type=Path); s.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); start = time.monotonic()
    if args.command == 'preflight':
        print(json.dumps({'pypdf': bool(importlib.util.find_spec('pypdf')), 'pdftoppm': shutil.which('pdftoppm'), 'node': shutil.which('node'), 'mmdc': shutil.which('mmdc'), 'chrome': Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').exists(), 'mermaid': 'availability only; run renderer to verify'}, ensure_ascii=False)); return
    if args.command == 'prepare':
        folder, hit = prepare(args.pdf, args.cache)
        print(json.dumps({'folder': str(folder.resolve()), 'cache_hit': hit, 'pages': len(read(folder / 'manifest.json')['pages']), 'seconds': round(time.monotonic() - start, 3)})); return
    if args.command == 'scaffold':
        plan = read(args.plan)
        # Output is exclusively a new staging directory; never replace user notes.
        args.output.mkdir(parents=True, exist_ok=False)
        index = plan['index']
        def safe(name):
            path = (args.output / name).resolve()
            if not path.is_relative_to(args.output.resolve()): raise ValueError('output outside staging')
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        entries = []
        mapping = {}
        for note in plan['notes']:
            target = note['path']; title = note['title']
            nav = f'[[{index.removesuffix(".md")}|返回总目录]]'
            if note.get('chapter'): nav += f' · [[{note["chapter"].removesuffix(".md")}|所属章节]]'
            sources = []
            for src in note.get('sources', []):
                for n in src['pages']:
                    sources.append(f'[[{src["pdf"]}#page={n}]]')
                    mapping.setdefault((src['pdf'], n), []).append(target.removesuffix('.md'))
            body = Path(note['body']).read_text(encoding='utf-8')
            safe(target).write_text(f'# {title}\n\n{nav}\n\n{body}\n\n来源：' + ' · '.join(sources) + '\n', encoding='utf-8')
            entries.append(f'- [[{target.removesuffix(".md")}|{title}]]')
        safe(index).write_text('# ' + plan['title'] + '\n\n' + '\n'.join(entries) + '\n\n[[页码索引]]\n', encoding='utf-8')
        rows = ['# 页码索引', '', f'[[{index.removesuffix(".md")}|返回总目录]]', '', '| 来源 | 笔记 |', '| --- | --- |']
        for source in plan['sources']:
            for n in range(1, source['page_count'] + 1):
                links = ' · '.join(f'[[{t}]]' for t in mapping.get((source['pdf'], n), [])) or '待归类'
                rows.append(f'| [[{source["pdf"]}#page={n}]] | {links} |')
        safe('页码索引.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
        print(f'STAGED: {len(entries)} notes; review before merging'); return
    folder = args.folder
    m = read(folder / 'manifest.json')
    ledger = folder / 'review.json'
    state = read(ledger) if ledger.exists() else {}
    if args.command == 'status':
        pending = {kind: [r['page'] for r in m['pages'] if kind not in state.get(str(r['page']), {})] for kind in ('text', 'visual', 'verified')}
        stale = []
        for n, kinds in state.items():
            for kind, record in kinds.items():
                if record.get('asset') and (not Path(record['asset']).exists() or digest(record['asset']) != record['asset_sha256']): stale.append(f'{n}:{kind}')
        print(json.dumps({'pages': len(m['pages']), 'pending': pending, 'stale_assets': stale, 'source_changed': digest(m['source']) != m['sha256']}, ensure_ascii=False)); return
    selected = pages(args.pages, len(m['pages']))
    if args.command == 'render':
        if not 36 <= args.dpi <= 600: raise ValueError('DPI must be 36..600')
        results = render(folder, selected, args.dpi)
        save(folder / 'render-result.json', results)
        print(json.dumps({'images': len(results), 'manifest': str((folder / 'render-result.json').resolve())})); return
    if args.command == 'mark':
        if digest(m['source']) != m['sha256']: raise ValueError('source changed; prepare again')
        if args.kind == 'visual' and not args.asset: raise ValueError('visual review requires inspected asset')
        for n in selected:
            record = {'evidence': args.evidence}
            if args.asset: record.update(asset=str(args.asset.resolve()), asset_sha256=digest(args.asset))
            state.setdefault(str(n), {})[args.kind] = record
        save(ledger, state); print(f'RECORDED: {len(selected)} pages, {args.kind}'); return
    if args.max_chars < 1 or args.offset < 0: raise ValueError('invalid read limit/offset')
    if args.offset and len(selected) != 1: raise ValueError('offset requires one page')
    used = 0
    delivered = []
    for n in selected:
        content = (folder / m['pages'][n-1]['text']).read_text(encoding='utf-8')
        if used and used + len(content) > args.max_chars:
            print(f'\nCONTINUE: --pages {n}-{selected[-1]} (restrict to original selection)'); break
        offset = args.offset
        piece = content[offset:offset + args.max_chars - used]
        print(f'\n--- PAGE {n}, offset {offset} ---\n{piece}')
        used += len(piece)
        delivered.append(n)
        if offset + len(piece) < len(content):
            print(f'\nCONTINUE: --pages {n} --offset {offset + len(piece)}; then remaining requested pages'); break
    metrics_path = folder / 'metrics.json'
    metrics = read(metrics_path) if metrics_path.exists() else {'read_calls': 0, 'returned_chars': 0, 'page_reads': {}}
    metrics['read_calls'] += 1; metrics['returned_chars'] += used
    # Character and call counters are proxies, never reported as token counts.
    for n in delivered: metrics['page_reads'][str(n)] = metrics['page_reads'].get(str(n), 0) + 1
    save(metrics_path, metrics)

if __name__ == '__main__':
    try: main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f'ERROR: {exc}')
