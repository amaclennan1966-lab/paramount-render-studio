export const CATEGORIES=['Brick','Stone','Roofing','Render','Timber','Paving','Ground','Frames & metal','Other'];
export function categoryForAsset(meta){
 const words=[meta?.name||'',meta?.category||'',...(Array.isArray(meta?.categories)?meta.categories:[]),...(Array.isArray(meta?.tags)?meta.tags:[])].join(' ').toLowerCase();
 if(/roof|slate|shingle|roofing/.test(words))return 'Roofing';
 if(/brick|cinderblock|blockwork|clinker|masonry/.test(words))return 'Brick';
 if(/plaster|stucco|render|wall paint|painted wall/.test(words))return 'Render';
 if(/cobble|paver|paving|asphalt|concrete|driveway|road/.test(words))return 'Paving';
 if(/wood|timber|floorboard|plank|decking|bark/.test(words))return 'Timber';
 if(/metal|steel|zinc|aluminium|iron|copper/.test(words))return 'Frames & metal';
 if(/grass|lawn|soil|ground|gravel|dirt|mud|sand|terrain/.test(words))return 'Ground';
 if(/stone|rock|limestone|sandstone|marble|granite/.test(words))return 'Stone';
 return 'Other';
}
const validId=id=>typeof id==='string'&&/^[a-z0-9_]{3,90}$/.test(id);
const positiveSize=(n,fallback)=>Number.isFinite(Number(n))&&Number(n)>=10&&Number(n)<=100000?Number(n):fallback;
export function catalogFromAPI(data){
 if(!data||typeof data!=='object'||Array.isArray(data))throw Error('The material catalogue has an unexpected format.');
 const out=[];
 for(const [id,m] of Object.entries(data).slice(0,2000)){
  if(!validId(id)||!m||typeof m.name!=='string')continue;
  const name=m.name.trim().slice(0,100);if(!name)continue;
  const group=categoryForAsset(m);
  const version=/^[a-f0-9]{4,32}$/i.test(m.img_version||'')?'&v='+m.img_version:'';
  out.push({id,name,category:group,dimensions:[2000,2000],
   thumbnail:'https://cdn.polyhaven.com/asset_img/thumbs/'+id+'.png?width=180&height=180&format=webp'+version,
   search:[id,name,group,m.category||'',...(Array.isArray(m.tags)?m.tags:[])].join(' ').toLowerCase()});
 }
 return out.sort((a,b)=>a.name.localeCompare(b.name));
}
function validTextureUrl(url,id,suffix){
 return typeof url==='string'&&url==='https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/'+id+'/'+id+'_'+suffix+'_1k.jpg';
}
export async function resolvePolyHavenMaterial(entry,fetcher=fetch){
 if(!entry||!validId(entry.id))throw Error('Invalid Poly Haven material ID.');
 const response=await fetcher('https://api.polyhaven.com/files/'+entry.id,{mode:'cors',signal:AbortSignal.timeout(15000)});
 if(!response.ok)throw Error('Material download information is unavailable. Try again.');
 const maps=await response.json();
 const url=maps?.Diffuse?.['1k']?.jpg?.url;
 const normalUrl=maps?.nor_gl?.['1k']?.jpg?.url;
 if(!validTextureUrl(url,entry.id,'diff'))throw Error('This finish has no supported 1K JPEG texture.');
 if(normalUrl&&!validTextureUrl(normalUrl,entry.id,'nor_gl'))throw Error('Invalid normal-map URL from material provider.');
 return {
  assetId:entry.id,label:entry.name,category:entry.category,provider:'Poly Haven CC0',
  url,...(normalUrl?{normalUrl}:{}),
  tile:positiveSize(entry.dimensions?.[0],2000),
  tileHeight:positiveSize(entry.dimensions?.[1],positiveSize(entry.dimensions?.[0],2000)),
  rough:.8
 };
}
export function validateLibraryFinishes(input){
 if(!input||typeof input!=='object'||Array.isArray(input))throw Error('Invalid saved material library.');
 if(Object.keys(input).length>60)throw Error('Too many saved library materials (maximum 60).');
 const result={};
 for(const [key,raw] of Object.entries(input)){
  const id=key.startsWith('ph_')?key.slice(3):'';
  if(!validId(id)||!raw||raw.assetId!==id||typeof raw.label!=='string'||!raw.label.trim()||raw.label.length>100||
     !CATEGORIES.includes(raw.category)||!validTextureUrl(raw.url,id,'diff')||
     (raw.normalUrl&&!validTextureUrl(raw.normalUrl,id,'nor_gl'))||
     !Number.isFinite(raw.tile)||raw.tile<10||raw.tile>100000||
     !Number.isFinite(raw.tileHeight)||raw.tileHeight<10||raw.tileHeight>100000)throw Error('Invalid saved Poly Haven material: '+key);
  result[key]={assetId:id,label:raw.label,category:raw.category,provider:'Poly Haven CC0',url:raw.url,
   ...(raw.normalUrl?{normalUrl:raw.normalUrl}:{}),tile:raw.tile,tileHeight:raw.tileHeight,rough:.8};
 }
 return result;
}
