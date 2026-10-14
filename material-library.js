// UK residential presentation finishes and an optional, on-demand CC0 library.
// The free Poly Haven catalogue is fetched only after the user opens its browser.
// No drawing bytes, geometry, photographs or finish-choice files are sent to Poly Haven.
export const CATEGORIES=[
 'Brick & Block','Stone','Roof','Render & Plaster','Glazing & Frames',
 'Timber','Paving & Concrete','Ground & Landscape','Metal','Other'
];

const brick=(label,tint)=>({label,category:'Brick & Block',file:'brick.jpg',normal:'brick-normal.jpg',tile:1440,tint,rough:.8});
const stone=(label,tint)=>({label,category:'Stone',file:'stone.jpg',normal:'stone-normal.jpg',tile:2500,tint,rough:.83});
const slate=(label,tint)=>({label,category:'Roof',file:'slate.jpg',normal:'slate-normal.jpg',tile:1800,tint,rough:.69});
const colour=(label,category,color,rough=.85)=>({label,category,color,rough});
const glass=(label,tint)=>({label,category:'Glazing & Frames',file:'glass.jpg',tile:2500,tint,rough:.08,mode:2});

export const EXTRA_FINISHES={
 brick_stock_red:brick('Stock brick · warm red',[1.12,.94,.84]),
 brick_deep_red:brick('Brick · deep red',[.86,.77,.76]),
 brick_weathered:brick('Brick · weathered',[.95,.97,.92]),
 brick_brown:brick('Brick · dark brown',[.66,.73,.72]),
 brick_orange:brick('Brick · orange red',[1.24,.97,.75]),
 brick_pale:brick('Brick · pale stock',[1.45,1.32,1.14]),
 sandstone:stone('Stone · warm sandstone',[1.22,1.07,.83]),
 yorkshire_stone:stone('Stone · Yorkshire buff',[1.4,1.25,.92]),
 limestone:stone('Stone · pale limestone',[1.45,1.42,1.28]),
 grey_stone:stone('Stone · grey',[.86,.92,.99]),
 dark_stone:stone('Stone · dark grey',[.7,.75,.82]),
 weathered_stone:stone('Stone · weathered',[.94,.99,.91]),
 slate_dark:slate('Slate · charcoal',[.7,.73,.75]),
 slate_blue:slate('Slate · blue grey',[.76,.86,1.08]),
 slate_warm:slate('Slate · warm grey',[.94,.85,.8]),
 slate_light:slate('Slate · light grey',[1.15,1.18,1.18]),
 white_render:colour('Render · pure white','Render & Plaster','#f7f7f3'),
 offwhite_render:colour('Render · warm white','Render & Plaster','#eeede4'),
 cream_render:colour('Render · cream','Render & Plaster','#e4d7bf'),
 ivory_render:colour('Render · ivory','Render & Plaster','#f2e6cf'),
 sand_render:colour('Render · sandstone','Render & Plaster','#cdbc9d'),
 lightgrey_render:colour('Render · light grey','Render & Plaster','#d2d4d1'),
 greige_render:colour('Render · greige','Render & Plaster','#b6b0a6'),
 darkgrey_render:colour('Render · charcoal','Render & Plaster','#626969'),
 frame_chartwell:colour('Frames · Chartwell green','Glazing & Frames','#9eb29d',.25),
 frame_agate:colour('Frames · agate grey','Glazing & Frames','#afb3a7',.25),
 frame_pebble:colour('Frames · pebble grey','Glazing & Frames','#b5b1a1',.25),
 frame_black:colour('Frames · black','Glazing & Frames','#252729',.22),
 frame_cream:colour('Frames · cream','Glazing & Frames','#f2e8d5',.24),
 frame_brown:colour('Frames · dark brown','Glazing & Frames','#49372e',.25),
 frame_silver:colour('Frames · silver aluminium','Glazing & Frames','#9ca5a8',.24),
 frame_slate:colour('Frames · slate grey','Glazing & Frames','#6c7477',.25),
 frame_green:colour('Frames · heritage green','Glazing & Frames','#536b5d',.25),
 glass_blue:glass('Glazing · cool blue',[.85,.94,1.15]),
 glass_neutral:glass('Glazing · neutral grey',[.9,.94,.95]),
 glass_bronze:glass('Glazing · warm bronze',[1.1,.96,.81]),
 concrete:colour('Concrete · natural','Paving & Concrete','#a7aaa5',.96),
 concrete_light:colour('Concrete · light','Paving & Concrete','#c7c8c2',.96),
 paved_sandstone:stone('Paving · sandstone indicative',[1.16,1.08,.87]),
 soil:colour('Ground · soil','Ground & Landscape','#635845',.98),
 gravel:colour('Ground · gravel colour','Ground & Landscape','#b9b3a3',.98),
 timber_oak:colour('Timber colour · oak','Timber','#ac8354',.6),
 timber_walnut:colour('Timber colour · walnut','Timber','#66503a',.65),
 zinc:colour('Metal · zinc','Metal','#8d9596',.31),
 lead:colour('Metal · lead grey','Metal','#666d72',.4)
};
EXTRA_FINISHES.paved_sandstone.category='Paving & Concrete';

const DEFAULT_GROUPS={
 brick:'Brick & Block',buff:'Brick & Block',stone:'Stone',slate:'Roof',
 glass:'Glazing & Frames',white:'Glazing & Frames',olive:'Glazing & Frames',
 ral7032:'Glazing & Frames',anthracite:'Glazing & Frames',gutter:'Metal',
 wall:'Render & Plaster',grass:'Ground & Landscape'
};
export function groupForFinish(id,finish){
 return finish.category||DEFAULT_GROUPS[id]||'Other';
}
export function categoryForAsset(meta){
 const words=[meta?.name||'',meta?.category||'',...(meta?.categories||[]),...(meta?.tags||[])].join(' ').toLowerCase();
 if(/roof|slate|shingle|roofing/.test(words))return 'Roof';
 if(/brick|cinderblock|blockwork|clinker|masonry/.test(words))return 'Brick & Block';
 if(/plaster|stucco|render|wall paint|painted wall/.test(words))return 'Render & Plaster';
 if(/cobble|paver|paving|asphalt|concrete|driveway|road/.test(words))return 'Paving & Concrete';
 if(/wood|timber|floorboard|plank|decking|bark/.test(words))return 'Timber';
 if(/metal|steel|zinc|aluminium|iron|copper/.test(words))return 'Metal';
 if(/grass|lawn|soil|ground|gravel|dirt|mud|sand|terrain/.test(words))return 'Ground & Landscape';
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
  out.push({id,name,category:group,dimensions:[positiveSize(m.dimensions?.[0],2000),positiveSize(m.dimensions?.[1],positiveSize(m.dimensions?.[0],2000))],
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
 const response=await fetcher('https://api.polyhaven.com/files/'+entry.id,{mode:'cors'});
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
