export function contains(p,ring){let v=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])v=!v;}return v;}
export function area(r){let a=0;for(let i=0;i<r.length-1;i++)a+=r[i][0]*r[i+1][1]-r[i+1][0]*r[i][1];return a/2;}
export function detectFaces(input){
 if(input.length>30000)throw Error('This detailed sheet has '+input.length.toLocaleString('en-GB')+' line segments. Automatic boundaries were skipped; use Polygon lasso and review openings manually. Original linework is retained.');
 const started=performance.now();let comparisons=0;const guard=()=>{if(++comparisons>2000000||performance.now()-started>10000)throw Error('Automatic boundaries exceeded the detail budget. Use Polygon lasso and review openings manually. Original linework is retained.');};
 const seg=input.filter(s=>Math.hypot(s[1][0]-s[0][0],s[1][1]-s[0][1])>1e-7),splits=seg.map(()=>[0,1]);
 const cross=(a,b)=>a[0]*b[1]-a[1]*b[0];const sub=(a,b)=>[a[0]-b[0],a[1]-b[1]];
 // A bounding-volume tree avoids comparing every pair on detailed CAD sheets.
 // Only the candidate search changes: all intersection and boundary coordinates
 // still come from the original finite segments.
 const bounds=seg.map(([a,b],id)=>({id,x0:Math.min(a[0],b[0]),x1:Math.max(a[0],b[0]),y0:Math.min(a[1],b[1]),y1:Math.max(a[1],b[1])}));
 const build=list=>{const box={x0:Infinity,y0:Infinity,x1:-Infinity,y1:-Infinity};for(const b of list){box.x0=Math.min(box.x0,b.x0);box.x1=Math.max(box.x1,b.x1);box.y0=Math.min(box.y0,b.y0);box.y1=Math.max(box.y1,b.y1);}if(list.length<=8)return {...box,items:list};const axis=box.x1-box.x0>box.y1-box.y0?'x':'y';list.sort((a,b)=>(a[axis+'0']+a[axis+'1'])-(b[axis+'0']+b[axis+'1']));const mid=list.length>>1;return {...box,left:build(list.slice(0,mid)),right:build(list.slice(mid))};};
 const tree=build([...bounds]);
 const overlaps=(a,b)=>a.x1+1e-7>=b.x0&&b.x1+1e-7>=a.x0&&a.y1+1e-7>=b.y0&&b.y1+1e-7>=a.y0;
 const candidates=(node,box,result)=>{if(!overlaps(node,box))return;if(node.items){for(const b of node.items)if(b.id>box.id&&overlaps(b,box))result.push(b.id);}else{candidates(node.left,box,result);candidates(node.right,box,result);}};
 for(let i=0;i<seg.length;i++){const neighbours=[];candidates(tree,bounds[i],neighbours);for(const j of neighbours){
  guard();const [a,b]=seg[i],[c,d]=seg[j];
  const u=sub(b,a),v=sub(d,c),den=cross(u,v),w=sub(c,a);
  if(Math.abs(den)>1e-12){const t=cross(w,v)/den,s=cross(w,u)/den;if(t>=-1e-10&&t<=1+1e-10&&s>=-1e-10&&s<=1+1e-10){splits[i].push(Math.max(0,Math.min(1,t)));splits[j].push(Math.max(0,Math.min(1,s)));}}
  else if(Math.abs(cross(w,u))<1e-8){for(const p of[c,d]){const t=(sub(p,a)[0]*u[0]+sub(p,a)[1]*u[1])/(u[0]**2+u[1]**2);if(t>0&&t<1)splits[i].push(t);}for(const p of[a,b]){const t=(sub(p,c)[0]*v[0]+sub(p,c)[1]*v[1])/(v[0]**2+v[1]**2);if(t>0&&t<1)splits[j].push(t);}}
 }
 }
 const nodes=new Map(),adj=new Map();const key=p=>`${Math.round(p[0]*1e6)},${Math.round(p[1]*1e6)}`;
 for(let i=0;i<seg.length;i++){const [a,b]=seg[i],ts=[...new Set(splits[i])].sort((a,b)=>a-b);for(let j=0;j<ts.length-1;j++){if(ts[j+1]-ts[j]<1e-10)continue;const ps=[ts[j],ts[j+1]].map(t=>[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);const ks=ps.map(key);if(ks[0]===ks[1])continue;for(let k=0;k<2;k++){nodes.set(ks[k],ps[k]);if(!adj.has(ks[k]))adj.set(ks[k],new Set());adj.get(ks[k]).add(ks[1-k]);}}}
 const order=new Map();for(const [k,set]of adj){const p=nodes.get(k);order.set(k,[...set].sort((a,b)=>Math.atan2(nodes.get(a)[1]-p[1],nodes.get(a)[0]-p[0])-Math.atan2(nodes.get(b)[1]-p[1],nodes.get(b)[0]-p[0])));}
 const seen=new Set(),faces=[];
 for(const [a,list]of order)for(const b of list){if(seen.has(a+'>'+b))continue;let u=a,v=b,ring=[],closed=false;for(let n=0;n<20000;n++){const edge=u+'>'+v;if(seen.has(edge))break;seen.add(edge);ring.push(nodes.get(u));const ns=order.get(v),w=ns[(ns.indexOf(u)-1+ns.length)%ns.length];u=v;v=w;if(u===a&&v===b){closed=true;break;}}if(closed){ring.push(ring[0]);const s=area(ring);if(s>.08){faces.push({ring,holes:[],area:s});if(faces.length>12000)throw Error('Too many enclosed hatch areas for automatic boundaries. Use Polygon lasso; original linework is retained.');}}}
 faces.sort((a,b)=>a.area-b.area);const fb=faces.map(f=>{const b={x0:Infinity,y0:Infinity,x1:-Infinity,y1:-Infinity};for(const p of f.ring){b.x0=Math.min(b.x0,p[0]);b.x1=Math.max(b.x1,p[0]);b.y0=Math.min(b.y0,p[1]);b.y1=Math.max(b.y1,p[1]);}return b;});for(let i=0;i<faces.length;i++){if(performance.now()-started>10000)throw Error('Automatic boundary review timed out. Use Polygon lasso; original linework is retained.');const f=faces[i];for(let j=i+1;j<faces.length;j++){const parent=faces[j];if(fb[i].x0<fb[j].x0||fb[i].x1>fb[j].x1||fb[i].y0<fb[j].y0||fb[i].y1>fb[j].y1)continue;if(f.ring.slice(0,-1).every(p=>contains(p,parent.ring))){parent.holes.push(f.ring);break;}}}return faces.map((f,i)=>({...f,id:i}));
}
export function pathString(f){return [f.ring,...f.holes].map(r=>'M'+r.map(p=>p.join(',')).join('L')+'Z').join('');}

// Check each CAD segment against the finite, collinear exported PDF segments.
// A renderer may split a line; the union must cover the entire source span.
export function sourceSegmentsRetained(source,output,tolerance=.001){
 return source.every(([a,b])=>{
  const dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);
  if(length<=tolerance)return true;
  const intervals=[];
  for(const[c,d]of output){
   const distance=p=>Math.abs(dx*(p[1]-a[1])-dy*(p[0]-a[0]))/length;
   if(distance(c)>tolerance||distance(d)>tolerance)continue;
   const project=p=>((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length;
   const u=project(c),v=project(d);intervals.push([Math.min(u,v),Math.max(u,v)]);
  }
  intervals.sort((x,y)=>x[0]-y[0]);let covered=0;
  for(const[start,end]of intervals){if(end<0)continue;if(start>covered+tolerance)break;covered=Math.max(covered,end);if(covered>=length-tolerance)return true;}
  return false;
 });
}
