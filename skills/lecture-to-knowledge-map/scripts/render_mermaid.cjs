#!/usr/bin/env node
// Usage: NODE_PATH=... node render_mermaid.cjs ROOT OUT MERMAID_BROWSER_BUNDLE [CHROME_PATH] [--force]
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const {chromium} = require('playwright');
const hash = x => crypto.createHash('sha256').update(x).digest('hex');
(async () => {
  const [rootArg, outArg, bundleArg, ...options] = process.argv.slice(2);
  if (!rootArg || !outArg || !bundleArg) throw Error('Usage: ROOT OUT MERMAID_BROWSER_BUNDLE [CHROME_PATH] [--force]');
  const root = path.resolve(rootArg), out = path.resolve(outArg), bundle = path.resolve(bundleArg);
  const executablePath = options.find(x => x !== '--force');
  const browser = await chromium.launch({headless:true, ...(executablePath ? {executablePath} : {})});
  try {
    fs.mkdirSync(out, {recursive:true});
    const page = await browser.newPage({viewport:{width:1600,height:1200},deviceScaleFactor:1});
    await page.setContent('<html><body style="margin:24px;background:white;color:#111"><div id="diagram"></div></body></html>');
    await page.addScriptTag({path:bundle});
    const environment = hash(fs.readFileSync(bundle)) + browser.version() + ':default:1600x1200:v1';
    function walk(dir) {
      return fs.readdirSync(dir, {withFileTypes:true}).flatMap(e => {
        const full = path.join(dir, e.name);
        if (e.isSymbolicLink() || full === out || ['.obsidian','tmp','备份','backup','backups'].includes(e.name)) return [];
        return e.isDirectory() ? walk(full) : (e.name.endsWith('.md') ? [full] : []);
      });
    }
    let results=[];
    for (const file of walk(root)) {
      const lines = fs.readFileSync(file,'utf8').split(/\r?\n/);
      let fence=null, body=[];
      for (const line of lines) {
        if (!fence) {
          const m=line.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
          if(m) {fence={char:m[1][0],length:m[1].length,lang:m[2].trim().split(/\s/)[0]};body=[];}
          continue;
        }
        if (!new RegExp('^ {0,3}'+fence.char+'{'+fence.length+',}\\s*$').test(line)) {body.push(line);continue;}
        if(fence.lang==='mermaid') {
          const code=body.join('\n'), key=hash(environment+code), png=path.join(out,key+'.png'), record=path.join(out,key+'.json');
          let result;
          if(!options.includes('--force') && fs.existsSync(record) && fs.existsSync(png) && JSON.parse(fs.readFileSync(record)).imageSha256===hash(fs.readFileSync(png))) {
            result={...JSON.parse(fs.readFileSync(record)),cached:true};
          } else {
            result=await page.evaluate(async code => {
              mermaid.initialize({startOnLoad:false,theme:'default',securityLevel:'strict'});
              await mermaid.parse(code);
              const {svg}=await mermaid.render('diagramSvg',code);
              document.querySelector('#diagram').innerHTML=svg;
              const r=document.querySelector('svg').getBoundingClientRect();
              if(!r.width || !r.height) throw Error('empty diagram');
              return {width:r.width,height:r.height};
            },code);
            await page.locator('#diagram').screenshot({path:png});
            result={...result,image:png,imageSha256:hash(fs.readFileSync(png)),cached:false};
            fs.writeFileSync(record,JSON.stringify(result));
          }
          results.push({file,...result});
        }
        fence=null; body=[];
      }
      if(fence) throw Error('Unclosed fence: '+file);
    }
    fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));
    console.log(JSON.stringify({diagrams:results.length,cached:results.filter(x=>x.cached).length,report:path.join(out,'results.json')}));
  } finally {await browser.close();}
})().catch(e=>{console.error(e.message);process.exit(1)});
