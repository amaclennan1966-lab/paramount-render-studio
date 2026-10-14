import {area,sourceSegmentsRetained} from './geometry.js';
export function snapPoint(point,segments,radius){
 let best=null,distance=radius;
 for(const s of segments)for(const p of s){const d=Math.hypot(p[0]-point[0],p[1]-point[1]);if(d<distance){best=p;distance=d;}}
 if(best)return [...best];
 for(const[a,b]of segments){const dx=b[0]-a[0],dy=b[1]-a[1],den=dx*dx+dy*dy;if(!den)continue;const t=Math.max(0,Math.min(1,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/den));const p=[a[0]+t*dx,a[1]+t*dy],d=Math.hypot(p[0]-point[0],p[1]-point[1]);if(d<distance){best=p;distance=d;}}
 return best?[...best]:[...point];
}
export function validateRing(points,width,height){
 if(points.length<3||points.length>500)throw Error('Choose at least three corners (maximum 500).');
 if(points.some(p=>p.length!==2||p.some(n=>!Number.isFinite(n))||p[0]<0||p[1]<0||p[0]>width||p[1]>height))throw Error('Keep the boundary inside the drawing sheet.');
 const ring=points.map(p=>[...p]);if(Math.hypot(...ring[0].map((n,i)=>n-ring.at(-1)[i]))>1e-8)ring.push([...ring[0]]);
 if(Math.abs(area(ring))<.08)throw Error('Boundary is too small.');
 const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
 for(let i=0;i<ring.length-1;i++)for(let j=i+2;j<ring.length-1;j++){if(i===0&&j===ring.length-2)continue;const[a,b,c,d]=[ring[i],ring[i+1],ring[j],ring[j+1]];if(cross(a,b,c)*cross(a,b,d)<=0&&cross(c,d,a)*cross(c,d,b)<=0&&Math.max(Math.min(a[0],b[0]),Math.min(c[0],d[0]))<=Math.min(Math.max(a[0],b[0]),Math.max(c[0],d[0]))&&Math.max(Math.min(a[1],b[1]),Math.min(c[1],d[1]))<=Math.min(Math.max(a[1],b[1]),Math.max(c[1],d[1])))throw Error('Boundary crosses itself. Choose corners around the perimeter.');}
 return ring;
}
export function boundaryReview(face,segments){
 const unmatched=[];for(const[ri,ring]of [face.ring,...face.holes].entries())for(let i=0;i<ring.length-1;i++)if(!sourceSegmentsRetained([[ring[i],ring[i+1]]],segments,.001))unmatched.push({ring:ri,edge:i,from:ring[i],to:ring[i+1]});
 return {origin:'polygon_lasso',cad_verified:unmatched.length===0,unmatched_edges:unmatched};
}
export function validateHole(ring,face){
 const inside=(p,r)=>{let yes=false;for(let i=0,j=r.length-1;i<r.length;j=i++){const[a,b]=[r[i],r[j]];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;};
 const edges=r=>r.slice(0,-1).map((p,i)=>[p,r[i+1]]);
 const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
 const intersects=(r,s)=>edges(r).some(([a,b])=>edges(s).some(([c,d])=>cross(a,b,c)*cross(a,b,d)<=0&&cross(c,d,a)*cross(c,d,b)<=0&&Math.max(Math.min(a[0],b[0]),Math.min(c[0],d[0]))<=Math.min(Math.max(a[0],b[0]),Math.max(c[0],d[0]))&&Math.max(Math.min(a[1],b[1]),Math.min(c[1],d[1]))<=Math.min(Math.max(a[1],b[1]),Math.max(c[1],d[1]))));
 if(!ring.slice(0,-1).every(p=>inside(p,face.ring))||intersects(ring,face.ring)||face.holes.some(h=>intersects(ring,h)||inside(ring[0],h)||inside(h[0],ring)))throw Error('Opening must lie fully inside the outline and not overlap another opening.');
}
