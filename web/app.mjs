import {el,node,edition,choices,cards,table,pretty,exportCsv,fail} from './ui.mjs';
import {match,difference} from './model.mjs';
let data,picker,rows=[];
const url='https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/page.cfm?Lang=E&DGUIDlist=';
function refreshPicker(q,id,preferred){
  const items=match(picker,el(q).value);
  choices(id,items,preferred);if(!items.length)el(id).add(new Option('No matching geography',''));
}
function value(id,i){
  const r=data.places[id],v=r[6][i],m=data.metrics[i],flag=data.flags[id]?.[m[0]];
  return pretty(v,m[2])+(flag?' ['+flag+']':'');
}
function update(){
  const a=el('left').value,b=el('right').value;
  if(!a||!b){
    el('summary').textContent='Choose a matching place in both lists.';['cards','table'].forEach(id=>el(id).replaceChildren());el('download').disabled=true;el('quality').textContent='';el('source1').hidden=el('source2').hidden=true;return;
  }
  el('source1').hidden=el('source2').hidden=false;el('download').disabled=false;
  const first=data.places[a],second=data.places[b],i=Number(el('feature').value),m=data.metrics[i],diff=difference(first[6][i],second[6][i]);
  cards([[first[0],value(a,i),m[1]],[second[0],value(b,i),m[1]]]);
  el('summary').textContent=diff==null?'A published value is unavailable for this comparison.':second[0]+' minus '+first[0]+' gives '+pretty(diff,m[2]==='%'?'percentage points':m[2])+'.';
  const indices=data.metrics.map((_,i)=>i).filter(i=>el('topic').value==='All indicators'||data.metrics[i][4]===el('topic').value);
  rows=indices.map(i=>[data.metrics[i][1],data.metrics[i][2],first[6][i],data.flags[a]?.[data.metrics[i][0]]||'',second[6][i],data.flags[b]?.[data.metrics[i][0]]||'']);
  table('table',['Indicator',first[0],second[0]],indices.map(i=>[data.metrics[i][1],value(a,i),value(b,i)]));
  el('source1').href=url+a;el('source2').href=url+b;
  el('quality').textContent=[first,second].map(r=>r[0]+' · short-form / long-form total non-response rates: '+(r[3]||'unavailable')+'% / '+(r[4]||'unavailable')+'%; published quality flag '+r[5]+'.').join(' ')+ ' The original profiles explain the geographic flags. x means suppressed for confidentiality, … means not applicable and .. means unavailable.';
}
async function start(){
  let status;[data,status]=await edition();
  el('status').textContent=status.count.toLocaleString('en-CA')+' geographies · 2021 Census Profile · Retrieved '+status.retrieved;
  picker=Object.entries(data.places).map(([id,[name,level,region]])=>[id,[name,level,region,id].filter(Boolean).join(' · ')]).sort((a,b)=>a[1].localeCompare(b[1]));
  choices('feature',data.metrics.map((m,i)=>[String(i),m[1]]),'0');choices('topic',['All indicators',...new Set(data.metrics.map(m=>m[4]))]);
  el('find1').value='Langley';el('find2').value='Halifax';refreshPicker('find1','left','2021A00055915001');refreshPicker('find2','right','2021A00051209034');
  for(const [field,id] of [['find1','left'],['find2','right']])el(field).oninput=()=>{refreshPicker(field,id,el(id).value);update();};
  for(const id of ['feature','topic','left','right'])el(id).onchange=update;
  el('download').onclick=()=>exportCsv(['Indicator','Unit',el('left').value,'Source symbol',el('right').value,'Source symbol'],rows,'census-lens-comparison');
  el('content').hidden=false;update();
}
start().catch(fail);
