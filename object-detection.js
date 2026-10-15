import {area,contains,sourceSegmentsRetained}from './geometry.js';
export const rectangleRing=b=>[[b.x0,b.y0],[b.x1,b.y0],[b.x1,b.y1],[b.x0,b.y1],[b.x0,b.y0]];
export const ringBounds=r=>({x0:Math.min(...r.map(p=>p[0])),y0:Math.min(...r.map(p=>p[1])),x1:Math.max(...r.map(p=>p[0])),y1:Math.max(...r.map(p=>p[1]))});
const inside=(a,b,inset=0)=>a.x0>=b.x0+inset&&a.x1<=b.x1-inset&&a.y0>=b.y0+inset&&a.y1<=b.y1-inset;
const overlap=(a,b)=>a.x0<b.x1&&b.x0<a.x1&&a.y0<b.y1&&b.y0<a.y1;
export function sourceRectangles(segments,scale=100){
 const h=new Map(),v=new Map(),tol=.001,ptmm=72/25.4/scale;
 const add=(map,k,a,b)=>{const key=Math.round(k*1000)/1000;if(!map.has(key))map.set(key,[]);map.get(key).push([Math.min(a,b),Math.max(a,b)]);};
 for(const[a,b]of segments){if(Math.abs(a[1]-b[1])<tol)add(h,a[1],a[0],b[0]);else if(Math.abs(a[0]-b[0])<tol)add(v,a[0],a[1],b[1]);}
 const merge=map=>[...map].flatMap(([k,list])=>{list.sort((a,b)=>a[0]-b[0]);const spans=[];for(const s of list){const last=spans.at(-1);if(last&&s[0]<=last[1]+tol)last[1]=Math.max(last[1],s[1]);else spans.push([...s]);}return spans.map(([a,b])=>({k,a,b}));});
 const hs=merge(h),vs=merge(v),result=[],seen=new Set();
 for(let i=0;i<vs.length;i++)for(let j=i+1;j<vs.length;j++){
  const left=vs[i].k<vs[j].k?vs[i]:vs[j],right=left===vs[i]?vs[j]:vs[i],w=right.k-left.k;if(w<10*ptmm||w>6500*ptmm)continue;
  const low=Math.max(left.a,right.a),high=Math.min(left.b,right.b);if(high-low<80*ptmm)continue;
  const ys=[...new Set(hs.filter(s=>s.a<=left.k+tol&&s.b>=right.k-tol&&s.k>=low-tol&&s.k<=high+tol).map(s=>s.k))].sort((a,b)=>a-b);
  for(let a=0;a<ys.length;a++)for(let b=a+1;b<ys.length;b++){const height=ys[b]-ys[a];if(height<80*ptmm||height>6500*ptmm)continue;const rect={x0:left.k,x1:right.k,y0:ys[a],y1:ys[b]},key=Object.values(rect).join(',');if(seen.has(key))continue;seen.add(key);result.push({...rect,ring:rectangleRing(rect),width:w,height,area:w*height});if(result.length>=18000)return result;}
 }
 return result;
}
export function findObjects(segments,faces,labels=[],scale=100){
 const rects=sourceRectangles(segments,scale),mm=72/25.4/scale,minWindow=300*mm;
 const candidates=[];
 for(const r of rects){
  if(r.width<minWindow||r.height<minWindow||r.width>6500*mm||r.height>4000*mm)continue;
  const children=rects.filter(c=>inside(c,r,.5*mm)&&c.width>=35*mm&&c.height>=35*mm&&c.area<r.area*.95);
  if(!children.some(c=>c.area>=r.area*.5&&Math.max(c.x0-r.x0,r.x1-c.x1,c.y0-r.y0,r.y1-c.y1)<=200*mm))continue;
  const nearLabels=labels.filter(l=>/^[WD]\d+[A-Z]?$/i.test(l.text.trim())&&l.x+l.width/2>=r.x0-r.width*.1&&l.x+l.width/2<=r.x1+r.width*.1&&l.y>=r.y0-r.height*.25&&l.y<=r.y1+600*mm);
  const label=nearLabels.length===1?nearLabels[0].text.trim():null;
  if(nearLabels.length>1)continue;
  const panes=children.filter(c=>!children.some(d=>d!==c&&inside(d,c,-.001)&&d.area<c.area*.97));
  const retained=panes.filter(c=>c.width>70*mm&&c.height>70*mm&&c.width/c.height>.18&&c.width/c.height<5.5);
  if(!retained.length)continue;
  candidates.push({...r,type:label?.toUpperCase().startsWith('D')?'door':label?'window':'unknown',label,panes:retained.map(c=>c.ring),confirmed:!!label,reason:label?'Source label '+label:'Unlabelled nested frame: review before window rendering'});
 }
 // Keep the outside frame of a nested group, never a sash as a separate window.
 const objects=candidates.filter(r=>!candidates.some(p=>p!==r&&inside(r,p,.1*mm)&&p.area>r.area*1.01));
 const doors=rects.filter(r=>r.width>=500*mm&&r.width<=2200*mm&&r.height>=1500*mm&&r.height<=3500*mm&&r.height/r.width>1.3&&!objects.some(o=>inside(r,o)));
 for(const r of doors){if(doors.some(p=>p!==r&&inside(r,p)&&p.area>r.area))continue;objects.push({...r,type:'unknown',label:null,panes:[],confirmed:false,reason:'Door-sized closed outline: preserved pending review'});}
 const pipes=rects.filter(r=>r.width>=10*mm&&r.width<=180*mm&&r.height>=800*mm&&r.height/r.width>8&&!objects.some(o=>inside(r,o)));
 for(const r of pipes){if(pipes.some(p=>p!==r&&inside(r,p)&&p.area>r.area))continue;objects.push({...r,type:'unknown',label:null,panes:[],confirmed:false,reason:'Narrow closed detail: review as pipe or other object'});}
 return objects.slice(0,160).map((o,i)=>({...o,id:'source_'+i,cad_verified:sourceSegmentsRetained(o.ring.slice(0,-1).map((p,i)=>[p,o.ring[i+1]]),segments,.003)}));
}
export function exclusionsFor(face,objects){const box=ringBounds(face.ring);return objects.filter(o=>overlap(box,ringBounds(o.ring))&&!o.disabled).map(o=>({objectId:o.id,type:o.type,ring:o.ring,confirmed:!!o.confirmed,cad_verified:!!o.cad_verified,reason:o.reason}));}
export function visibleProtection(face,point){return (face.exclusions||[]).some(e=>contains(point,e.ring));}
