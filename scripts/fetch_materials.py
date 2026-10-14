"""Prepare bundled CC0 photographs; API is used at build time, never for drawings."""
import json,urllib.request,hashlib,io,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'material-build';OUT.mkdir(exist_ok=True)
def get(url):
 for attempt in range(3):
  try:return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ParamountRenderStudio/1.0 (CC0 architectural materials)'}),timeout=60).read()
  except Exception:
   if attempt==2:raise
   time.sleep(2)
catalog=json.loads(get('https://api.polyhaven.com/assets?t=textures'))
SPECS=[
 ('sandstone','Sandstone masonry','Stone',['sandstone_brick_wall_01'],['sandstone','wall'],2500),
 ('dark-brick','Weathered brick','Brick',['brick_wall_001','brick_wall_004'],['brick','wall'],1440),
 ('reclaimed-brick','Reclaimed brick','Brick',['brick_wall_003','brick_wall_006'],['brick','wall'],1440),
 ('render','Plaster render','Render',['plastered_wall_04','plastered_wall_02'],['plaster','wall'],2000),
 ('concrete','Concrete','Paving',['concrete_floor_02','concrete_floor_01'],['concrete','floor'],2000),
 ('paving','Stone paving','Paving',['paving_stones_02','paving_stones_01'],['paving'],2000),
 ('gravel','Gravel','Ground',['gravel_floor_02','gravel_floor_01'],['gravel'],2000),
 ('asphalt','Asphalt','Ground',['asphalt_02','asphalt_01'],['asphalt'],2000),
 ('timber','Timber boards','Timber',['brown_planks_03','brown_planks_02'],['planks'],2000),
 ('roof-tiles','Clay roof tiles','Roofing',['roof_tiles_03','roof_tiles_02'],['roof','tiles'],1800)
]
used=set();selected=[]
for alias,label,category,preferred,words,tile in SPECS:
 asset=next((x for x in preferred if x in catalog and x not in used),None)
 if not asset:asset=next((x for x in sorted(catalog) if all(w in (x+' '+catalog[x].get('name','')).lower() for w in words) and x not in used),None)
 if not asset:raise RuntimeError('No verified source asset for '+alias)
 used.add(asset);selected.append((alias,label,category,asset,tile))
print('Selected materials:',json.dumps(selected),flush=True)
def prepare(spec):
 alias,label,category,asset,tile=spec;files=json.loads(get('https://api.polyhaven.com/files/'+asset));maps={}
 for out,key in [('diffuse','Diffuse'),('normal','nor_gl')]:
  if key not in files:
   if out=='normal':continue
   raise RuntimeError(asset+' lacks diffuse photograph')
  size='1k' if '1k' in files[key] else sorted(files[key])[0];formats=files[key][size];fmt=next((x for x in ('jpg','png') if x in formats),None)
  if not fmt:raise RuntimeError(asset+' lacks usable image map')
  source=formats[fmt];data=get(source['url'])
  if hashlib.md5(data).hexdigest()!=source['md5']:raise RuntimeError('Source checksum mismatch '+asset)
  image=Image.open(io.BytesIO(data)).convert('RGB');image.thumbnail((1024,1024),Image.Resampling.LANCZOS);filename=alias+('-normal' if out=='normal' else '')+'.jpg';image.save(OUT/filename,quality=91)
  maps[out]={'file':filename,'source_url':source['url'],'source_md5':source['md5'],'sha256':hashlib.sha256((OUT/filename).read_bytes()).hexdigest()}
 return {'id':alias,'label':label,'category':category,'asset':asset,'source_name':catalog[asset]['name'],'source_page':'https://polyhaven.com/a/'+asset,'license':'CC0 1.0','tile_mm':tile,'repeat_note':'Indicative physical repeat; review against actual product dimensions.','maps':maps}
with ThreadPoolExecutor(max_workers=3) as pool:materials=list(pool.map(prepare,selected))
(OUT/'manifest.json').write_text(json.dumps({'license_url':'https://polyhaven.com/license','materials':materials},indent=2))
print('Bundled',len(materials),'photographic materials; source checksums passed.',flush=True)
