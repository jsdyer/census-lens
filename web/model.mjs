export const normal=s=>s.normalize('NFKD').replace(/\p{M}/gu,'').toLowerCase();
export function match(places,query) {
  const words=normal(query).trim().split(/\s+/).filter(Boolean);
  return places.filter(([,label])=>words.every(w=>normal(label).includes(w)));
}
export function difference(a,b) {return Number.isFinite(a)&&Number.isFinite(b)?b-a:null;}
