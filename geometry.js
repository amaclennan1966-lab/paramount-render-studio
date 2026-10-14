export function contains(p,ring){let v=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])v=!v;}return v;}
export function area(r){let a=0;for(let i=0;i<r.length-1;i++)a+=r[i][0]*r[i+1][1]-r[i+1][0]*r[i][1];return a/2;}
export function detectFaces(input){
 if(input.length>6500)throw Error('Too many line segments for browser boundary review. Split the drawing into smaller sheets.');
 const seg=input.filter(s=>Math.hypot(s[1][0]-s[0][0],s[1][1]-s[0][1])>1e-7),splits=seg.map(()=>[0,1]);
 const cross=(a,b)=>a[0]*b[1]-a[1]*b[0];const sub=(a,b)=>[a[0]-b[0],a[1]-b[1]];
 for(let i=0;i<seg.length;i++)for(let j=i+1;j<seg.length;j++){
  const [a,b]=seg[i],[c,d]=seg[j];if(Math.max(a[0],b[0])+1e-7<Math.min(c[0],d[0])||Math.max(c[0],d[0])+1e-7<Math.min(a[0],b[0])||Math.max(a[1],b[1])+1e-7<Math.min(c[1],d[1])||Math.max(c[1],d[1])+1e-7<Math.min(a[1],b[1]))continue;
  const u=sub(b,a),v=sub(d,c),den=cross(u,v),w=sub(c,a);
  if(Math.abs(den)>1e-12){const t=cross(w,v)/den,s=cross(w,u)/den;if(t>=-1e-10&&t<=1+1e-10&&s>=-1e-10&&s<=1+1e-10){splits[i].push(Math.max(0,Math.min(1,t)));splits[j].push(Math.max(0,Math.min(1,s)));}}
  else if(Math.abs(cross(w,u))<1e-8){for(const p of[c,d]){const t=(sub(p,a)[0]*u[0]+sub(p,a)[1]*u[1])/(u[0]**2+u[1]**2);if(t>0&&t<1)splits[i].push(t);}for(const p of[a,b]){const t=(sub(p,c)[0]*v[0]+sub(p,c)[1]*v[1])/(v[0]**2+v[1]**2);if(t>0&&t<1)splits[j].push(t);}}
 }
 const nodes=new Map(),adj=new Map();const key=p=>`${Math.round(p[0]*1e6)},${Math.round(p[1]*1e6)}`;
 for(let i=0;i<seg.length;i++){const [a,b]=seg[i],ts=[...new Set(splits[i])].sort((a,b)=>a-b);for(let j=0;j<ts.length-1;j++){if(ts[j+1]-ts[j]<1e-10)continue;const ps=[ts[j],ts[j+1]].map(t=>[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);const ks=ps.map(key);if(ks[0]===ks[1])continue;for(let k=0;k<2;k++){nodes.set(ks[k],ps[k]);if(!adj.has(ks[k]))adj.set(ks[k],new Set());adj.get(ks[k]).add(ks[1-k]);}}}
 const order=new Map();for(const [k,set]of adj){const p=nodes.get(k);order.set(k,[...set].sort((a,b)=>Math.atan2(nodes.get(a)[1]-p[1],nodes.get(a)[0]-p[0])-Math.atan2(nodes.get(b)[1]-p[1],nodes.get(b)[0]-p[0])));}
 const seen=new Set(),faces=[];
 for(const [a,list]of order)for(const b of list){if(seen.has(a+'>'+b))continue;let u=a,v=b,ring=[],closed=false;for(let n=0;n<20000;n++){const edge=u+'>'+v;if(seen.has(edge))break;seen.add(edge);ring.push(nodes.get(u));const ns=order.get(v),w=ns[(ns.indexOf(u)-1+ns.length)%ns.length];u=v;v=w;if(u===a&&v===b){closed=true;break;}}if(closed){ring.push(ring[0]);const s=area(ring);if(s>.08)faces.push({ring,holes:[],area:s});}}
 faces.sort((a,b)=>a.area-b.area);for(let i=0;i<faces.length;i++){const f=faces[i];for(let j=i+1;j<faces.length;j++){const parent=faces[j];if(f.ring.slice(0,-1).every(p=>contains(p,parent.ring))){parent.holes.push(f.ring);break;}}}return faces.map((f,i)=>({...f,id:i}));
}
export function pathString(f){return [f.ring,...f.holes].map(r=>'M'+r.map(p=>p.join(',')).join('L')+'Z').join('');}
