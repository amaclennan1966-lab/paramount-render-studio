import * as THREE from 'https://esm.sh/three@0.180.0';
import { OrbitControls } from 'https://esm.sh/three@0.180.0/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'https://esm.sh/three@0.180.0/addons/loaders/GLTFLoader.js';

const el = document.getElementById('viewport');
const status = document.getElementById('status');
const metrics = document.getElementById('metrics');
const reportButton = document.getElementById('report');
const scene = new THREE.Scene(); scene.background = new THREE.Color(0xd7e3ec);
const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 100000);
const renderer = new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:false});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
el.appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;
scene.add(new THREE.HemisphereLight(0xffffff,0x778899,2.2));
const sun=new THREE.DirectionalLight(0xffffff,2.7);sun.position.set(10,22,14);scene.add(sun);
const grid=new THREE.GridHelper(20,20,0x999999,0xbcbcbc);scene.add(grid);
let current=null, manifest=null, objectUrl=null;
function resize(){const w=el.clientWidth,h=el.clientHeight; renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}
new ResizeObserver(resize).observe(el);
function frame(box){const c=box.getCenter(new THREE.Vector3());const size=box.getSize(new THREE.Vector3());const r=Math.max(size.length(),1);camera.position.copy(c).add(new THREE.Vector3(r*.8,r*.55,r*.8));controls.target.copy(c);camera.near=Math.max(r/10000,.001);camera.far=Math.max(r*100,1000);camera.updateProjectionMatrix();controls.update();grid.position.y=box.min.y;}
function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);}animate();
async function sha256(bytes){const digest=await crypto.subtle.digest('SHA-256',bytes);return Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');}
document.getElementById('model').addEventListener('change',async ev=>{
 const f=ev.target.files?.[0];if(!f)return;
 reportButton.disabled=true;status.textContent='Inspecting local model...';
 if(objectUrl)URL.revokeObjectURL(objectUrl);
 if(current){scene.remove(current);current.traverse(o=>{if(o.geometry)o.geometry.dispose();});current=null;}
 try{
  if(!f.name.toLowerCase().endsWith('.glb'))throw Error('For this prototype export a single .glb. External .gltf dependencies are not supported.');
  const bytes=await f.arrayBuffer();const hash=await sha256(bytes);
  objectUrl=URL.createObjectURL(new Blob([bytes],{type:'model/gltf-binary'}));
  const gltf=await new GLTFLoader().loadAsync(objectUrl);
  current=gltf.scene;scene.add(current);current.updateMatrixWorld(true);
  const box=new THREE.Box3().setFromObject(current);if(box.isEmpty())throw Error('Model has no measurable geometry.');
  let meshes=0,triangles=0,materials=new Set(),instances=0;
  current.traverse(o=>{if(o.isMesh){meshes++;let geo=o.geometry;const indices=geo.index?.count??geo.attributes.position?.count??0;triangles+=Math.floor(indices/3)*(o.isInstancedMesh?o.count:1);if(o.isInstancedMesh)instances+=o.count;for(const m of (Array.isArray(o.material)?o.material:[o.material]))if(m)materials.add(m.name||m.uuid);}});
  const v=box.getSize(new THREE.Vector3());
  manifest={version:1,sourceName:f.name,sourceBytes:f.size,sha256:hash,sourceFormat:'GLB (conversion from SKP not verified)',units:'GLB convention: metres; verify SketchUp export scale',boundsMeters:{min:box.min.toArray(),max:box.max.toArray(),size:v.toArray()},meshes,triangles,instancedCopies:instances,materials:[...materials],validation:'PRELIMINARY ONLY — compare against SketchUp source measurements',sourceModified:false};
  metrics.textContent=JSON.stringify(manifest,null,2);status.textContent='Model loaded locally. Verify dimensions against SketchUp.';reportButton.disabled=false;frame(box);
 }catch(e){status.textContent='Import failed: '+e.message;metrics.textContent='';}
});
reportButton.addEventListener('click',()=>{if(!manifest)return;const url=URL.createObjectURL(new Blob([JSON.stringify(manifest,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='paramount-3d-geometry-report.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
