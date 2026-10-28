// PDF de presentación desde el HTML que arma pdf.py, y la hoja para revisarlo (<pdf>.jpg: placas en grilla).
// uso: node pdf.js <dir con index.html> <salida.pdf>   (usa Chrome y puppeteer-core del motor de /motion)
const path=require('path'),os=require('os');
const MSK=path.join(os.homedir(),'.claude','skills','motion');
const puppeteer=require(path.join(MSK,'engine','node_modules','puppeteer-core'));
const {CHROME,fileURL}=require(path.join(MSK,'scripts','platform.js'));
(async()=>{
  const dir=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
  if(!CHROME){console.log('⚠️  sin Chrome: no hay PDF');return}
  const br=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--allow-file-access-from-files']});
  try{
    const p=await br.newPage();
    await p.setViewport({width:1080,height:1920});
    await p.goto(fileURL(path.join(dir,'index.html')),{waitUntil:'networkidle0'});
    await p.evaluate(()=>document.fonts.ready);
    // placas donde algo se sale del cuadro
    const over=await p.evaluate(()=>[...document.querySelectorAll('.slide')].map((s,i)=>{
      const r=s.getBoundingClientRect(),foot=s.querySelector('.foot').getBoundingClientRect();
      const bad=[...s.querySelectorAll('h1,h2,h3,p,li,.btn,.qr,img')].some(e=>{const b=e.getBoundingClientRect();
        return b.width&&(b.bottom>foot.top-6||b.right>r.right-40||b.top<r.top)});
      return bad?i+1:0}).filter(Boolean));
    if(over.length)console.log(`⚠️  placa ${over.join(', ')}: el texto se sale o pisa el pie (acortar en web.json)`);
    await p.pdf({path:out,preferCSSPageSize:true,printBackground:true});
    console.log('✓ pdf:',out);
    const fonts=await p.evaluate(()=>[...document.fonts].filter(f=>f.status==='error').map(f=>f.family));
    if(fonts.length)console.log('⚠️  tipografías que no cargaron:',[...new Set(fonts)].join(', '));
    await p.evaluate(()=>document.body.classList.add('hoja'));
    await p.setViewport({width:1080*4+60*5,height:1920,deviceScaleFactor:.3});
    const jpg=out.replace(/\.pdf$/i,'')+'.jpg';
    await p.screenshot({path:jpg,fullPage:true,type:'jpeg',quality:82});
    console.log('✓ hoja:',jpg);
  }finally{await br.close()}
})().catch(e=>{console.log('⚠️  pdf falló:',e.message);process.exit(0)});
