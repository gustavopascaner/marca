// Capturas de la landing para revisarla: web_desktop.png (1440) y web_mobile.png (390) al lado de <dir>, página completa.
// uso: node captura.js <dir>   (usa Chrome y puppeteer-core del motor de /motion)
const path=require('path'),os=require('os');
const MSK=path.join(os.homedir(),'.claude','skills','motion');
const puppeteer=require(path.join(MSK,'engine','node_modules','puppeteer-core'));
const {CHROME,fileURL}=require(path.join(MSK,'scripts','platform.js'));
(async()=>{
  const dir=path.resolve(process.argv[2]||'.');
  if(!CHROME){console.log('⚠️  sin Chrome: no hay captura');return}
  const br=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--allow-file-access-from-files']});
  try{
    for(const [name,w,h,m] of [['desktop',1440,900,false],['mobile',390,844,true]]){
      const p=await br.newPage();
      await p.setViewport({width:w,height:h,deviceScaleFactor:m?2:1,isMobile:m,hasTouch:m});
      await p.goto(fileURL(path.join(dir,'index.html')),{waitUntil:'networkidle0'});
      await p.evaluate(()=>{document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'));return document.fonts.ready});
      await new Promise(r=>setTimeout(r,900));
      const over=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
      if(over)console.log(`⚠️  ${name}: scroll horizontal (algo se sale del ancho)`);
      const out=path.join(path.dirname(dir),`web_${name}.png`);
      await p.screenshot({path:out,fullPage:true});
      console.log('✓ captura:',out);
    }
  }finally{await br.close()}
})().catch(e=>{console.log('⚠️  captura falló:',e.message);process.exit(0)});
