// Placas a medida de la presentación de marca (se inyectan en engine.html de motion). Toman los colores y tipografías de BR (brand.json).

// SC.paleta: los colores de la marca entran uno por uno, cada uno con su rol y su hex.
// p.items=[{k:'accent'|'accent2'|'light'|'dark'|'mute', t:'rol', at}]
SC.paleta=(p,c)=>{const b=c.box;AL(b,p,c,'left');const k=p.kick?kick(b,p.kick):null;
 const lum=hx=>{const v=[1,3,5].map(i=>parseInt(hx.slice(i,i+2),16)/255).map(x=>x<=.03928?x/12.92:((x+.055)/1.055)**2.4);return .2126*v[0]+.7152*v[1]+.0722*v[2];};
 const wr=h('div','display:flex;flex-direction:column;gap:22px;width:880px;margin-top:34px',b);
 const rows=(p.items||[]).map((it,i)=>{const hx=(BR.colors[it.k]||'#888888').toUpperCase(),ink=lum(hx)>.4?BR.colors.dark:BR.colors.light;
  const r=h('div',`display:flex;align-items:flex-end;justify-content:space-between;height:${i===0?300:190}px;padding:30px 38px;box-sizing:border-box;border-radius:var(--r);background:${hx};color:${ink};box-shadow:0 0 0 3px color-mix(in srgb,var(--fg) 14%,transparent)`,wr);
  h('div',`font-size:${i===0?64:48}px`,r,it.t,'disp');h('div','font-size:30px;opacity:.85',r,hx,'mono');
  return {r,a:it.at??.3+i*.5};});
 return t=>{if(k)fadeUp(k,t,.05);rows.forEach(({r,a})=>{const q=M.pop(P(t,a,.55));r.style.opacity=P(t,a,.12);r.style.transform=`translateY(${(1-q)*60}px) scaleX(${L(.6,1,E.o3(P(t,a,.5)))})`;r.style.transformOrigin='0 50%';});};};

// SC.tipos: tipografía de títulos (grande, con su nombre) y de lectura (párrafo). Solo dos: no hay tipografía de acento.
// p={kick, title:'texto en display', body:'párrafo de muestra', atT, atB}
SC.tipos=(p,c)=>{const b=c.box;AL(b,p,c,'left');const k=p.kick?kick(b,p.kick):null;const F=BR.fonts||{};
 const lab=(txt,par)=>h('div','font-size:28px;color:var(--sub);margin-bottom:14px',par,txt,'mono');
 const A=h('div','margin-top:30px;width:880px',b);lab(`Títulos · ${(F.display||{}).family||''}`,A);
 const big=h('div','font-size:170px;color:var(--hl);line-height:1',A,'Aa','disp');const tt=h('div','font-size:88px;margin-top:10px',A,p.title||'','disp');
 const sep=()=>h('div','height:4px;width:880px;margin:36px 0;background:color-mix(in srgb,var(--fg) 18%,transparent);transform-origin:0 50%',b);
 const ln=sep();
 const B=h('div','width:880px',b);lab(`Lectura · ${(F.body||{}).family||''}`,B);const bd=h('div','font-size:44px;line-height:1.3',B,p.body||'','body');
 const aT=p.atT??.3,aB=p.atB??aT+2.4;
 return t=>{if(k)fadeUp(k,t,.05);fadeUp(A.firstChild,t,aT-.1);popIn(big,t,aT,.6);rise(tt,t,aT+.25);
  ln.style.transform=`scaleX(${E.io(P(t,aB-.3,.5))})`;fadeUp(B.firstChild,t,aB-.1);fadeUp(bd,t,aB+.1);};};
