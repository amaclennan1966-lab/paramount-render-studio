import {area}from './geometry.js';import {validateRing,validateHole}from './selection.js';
export function editOutline(face,ringIndex,index,operation,point,width,height){
 const rings=[face.ring,...face.holes].map(r=>r.slice(0,-1).map(p=>[...p]));
 const ring=rings[ringIndex];if(!ring||!Number.isInteger(index)||index<0||index>=ring.length)throw Error('Select an outline corner or edge.');
 if(operation==='move')ring[index]=[...point];
 else if(operation==='add')ring.splice(index+1,0,[...point]);
 else if(operation==='remove'){if(ring.length<=3)throw Error('An outline needs at least three corners.');ring.splice(index,1);}
 else throw Error('Unknown outline edit.');
 const outer=validateRing(rings[0],width,height),holes=[];
 for(const points of rings.slice(1)){const hole=validateRing(points,width,height);validateHole(hole,{ring:outer,holes});holes.push(hole);}
 return {...face,ring:outer,holes,area:Math.abs(area(outer)),edited:true};
}
export function nearestOutlineEdge(face,point,radius){
 let result=null,best=radius;
 for(const[ringIndex,ring]of [face.ring,...face.holes].entries())for(let i=0;i<ring.length-1;i++){const[a,b]=[ring[i],ring[i+1]],dx=b[0]-a[0],dy=b[1]-a[1],den=dx*dx+dy*dy;if(!den)continue;const t=Math.max(0,Math.min(1,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/den)),p=[a[0]+t*dx,a[1]+t*dy],d=Math.hypot(point[0]-p[0],point[1]-p[1]);if(d<best){best=d;result={ringIndex,index:i,point:p};}}
 return result;
}
