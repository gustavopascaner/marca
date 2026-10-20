// Presentación de marca: sigue la locución fija (assets/locucion). Lo único que cambia por cliente es cfg.textos (config.json):
// {rubro, nombre:[l1,l2], frase:[l1,l2,l3], titulo, cuerpo, pilares:[p1,p2,p3]}
module.exports=({S,w,H,A,cfg})=>{const T=cfg.textos||{},n=T.nombre||['Tu','marca'],f=T.frase||['Tu propuesta'],pl=T.pilares||['Pilar 1','Pilar 2','Pilar 3'];
S('title','b01',{kick:'PROPUESTA DE IDENTIDAD VISUAL',lines:[n[0],H(n[1]||'')],sub:T.rubro||'',subAt:w('identidad')});
S('title','b02',{kick:'LO QUE NOS CONTASTE',lines:f.map((x,i)=>i===f.length-1?H(x):x),at:f.map((_,i)=>i?w('transmitir'):0)});
S('paleta','b03',{bg:'dark',kick:'LOS COLORES',items:[{k:'accent',t:'Principal',at:w('principal')},{k:'accent2',t:'Acento',at:w('acento')},{k:'light',t:'Fondo claro',at:w('claro')},{k:'dark',t:'Fondo oscuro',at:w('oscuro')}]});
S('tipos','b04',{kick:'LAS TIPOGRAFÍAS',title:T.titulo||n.join(' '),body:T.cuerpo||'',atT:w('títulos'),atB:w('leer')});
S('steps','b05',{kick:'EN MOVIMIENTO',items:[{t:pl[0],at:w('transiciones'),icon:'check'},{t:pl[1],at:w('resaltados'),icon:'arrow'},{t:pl[2],at:w('subtítulos'),icon:'heart'}]});
S('bigword','b06',{kick:'DE AHORA EN ADELANTE',lines:['Tus',H('videos')],sub:'se van a ver así',subAt:w('adelante')});
S('list','b07',{kick:'TU OPINIÓN',title:'Contanos',items:[{t:'Qué te gusta',at:w('gusta'),mark:'check'},{t:'Qué cambiarías',at:w('cambiarías'),mark:'check'},{t:'Si te representa',at:w('representa'),mark:'check'}]});
S('cta',w('cualquier'),{kick:'CUALQUIER COMENTARIO SIRVE',lines:['¿Qué te','parece?'],action:'comment',word:'Te cuento…',btnAt:w('ajustarla')});
};
