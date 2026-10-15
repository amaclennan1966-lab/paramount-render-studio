"""CI runs real browser imports, materials, original-vector QA and export."""
from pathlib import Path
import http.server,threading,functools,json,ezdxf
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(accept_downloads=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:print('BROWSER:',m.type,m.text,flush=True))
 page.goto(f'http://127.0.0.1:{server.server_port}',wait_until='networkidle',timeout=120000)
 page.set_default_timeout(120000)
 page.wait_for_function('!!window.ParamountApp',timeout=120000)
 page.get_by_role('button',name='Try a sample elevation').click()
 page.wait_for_function('!!window.renderStudioState',timeout=120000)
 summary=page.evaluate('({faces:renderStudioState.faces.length,segments:renderStudioState.segments.length,width:renderStudioState.width,height:renderStudioState.height})')
 assert summary['faces']>=4,summary
 # Wheel zoom anchors a PDF point while preserving its print scale.
 initial_scale=page.evaluate('ParamountApp.getState().scale')
 box=page.locator('#sheet').bounding_box();pointer=[box['x']+box['width']*.6,box['y']+box['height']*.6]
 def point_under_pointer():
  r=page.locator('#sheet').bounding_box();return [(pointer[0]-r['x'])/r['width'],(pointer[1]-r['y'])/r['height']]
 before=point_under_pointer();page.mouse.move(*pointer);page.mouse.wheel(0,-300)
 page.wait_for_function('document.querySelector("#sheet").getBoundingClientRect().width>'+str(box['width']*1.5))
 after=point_under_pointer();assert max(abs(a-b) for a,b in zip(before,after))<.005,(before,after)
 assert page.evaluate('ParamountApp.getState().scale')==initial_scale
 page.mouse.wheel(0,300)
 page.wait_for_function('document.querySelector("#sheet").getBoundingClientRect().width<'+str(box['width']*1.1))
 wheel_width=page.locator('#sheet').bounding_box()['width'];page.mouse.move(100,400);page.mouse.wheel(0,200);page.wait_for_timeout(100)
 assert abs(page.locator('#sheet').bounding_box()['width']-wheel_width)<.1
 page.locator('#fit').click()
 # Space drag pans a zoomed sheet without painting or changing print scale.
 r=page.locator('#viewport').bounding_box();page.mouse.move(r['x']+r['width']*.5,r['y']+r['height']*.5);page.mouse.wheel(0,-300)
 page.wait_for_function('document.querySelector("#sheet").getBoundingClientRect().width>'+str(box['width']*1.5))
 before_pan=page.evaluate('({left:document.querySelector("#viewport").scrollLeft,top:document.querySelector("#viewport").scrollTop,scale:ParamountApp.getState().scale,assignments:JSON.stringify(ParamountApp.getState().assignments)})')
 page.locator('#fit').focus();page.keyboard.down('Space');page.mouse.down();page.mouse.move(r['x']+r['width']*.5-60,r['y']+r['height']*.5-40,steps=4);page.mouse.up();page.keyboard.up('Space')
 after_pan=page.evaluate('({left:document.querySelector("#viewport").scrollLeft,top:document.querySelector("#viewport").scrollTop,scale:ParamountApp.getState().scale,assignments:JSON.stringify(ParamountApp.getState().assignments)})')
 assert after_pan['left']>before_pan['left']+30,(before_pan,after_pan)
 assert after_pan['top']>before_pan['top']+20,(before_pan,after_pan)
 assert after_pan['scale']==before_pan['scale'] and after_pan['assignments']==before_pan['assignments']
 page.locator('#fit').click()
 # Library search/filter and GPU rendering of every added photograph.
 page.select_option('#material-category','Frames & metal')
 page.locator('#material-search').fill('RAL 7035')
 assert page.locator('#palette button').count()==1
 assert page.locator('#palette button').inner_text().startswith('Light grey frames')
 page.locator('#material-search').fill('')
 page.select_option('#material-category','all')
 assert page.locator('#palette button').count()==38
 page.evaluate('''async()=>{const {FINISHES,MaterialRenderer}=await import('./renderer.js');const s=ParamountApp.getState(),id=s.faces.reduce((a,b)=>a.area>b.area?a:b).id,c=document.createElement('canvas'),r=new MaterialRenderer(c);for(const key of Object.keys(FINISHES).filter(k=>k.startsWith('library_'))){await r.draw(s.faces,{[id]:key},s.width,s.height,s.scale,36);const pixels=new Uint8Array(c.width*c.height*4);r.gl.readPixels(0,0,c.width,c.height,r.gl.RGBA,r.gl.UNSIGNED_BYTE,pixels);if(!pixels.some((v,i)=>i%4===3&&v>0)||r.gl.getError()!==r.gl.NO_ERROR)throw Error('Material render failed '+key);}}''')
 # New default glass is pale, smooth and the only built-in glass choice.
 page.select_option('#material-category','Glass')
 assert page.locator('#palette button').count()==1
 assert 'Soft pale glass' in page.locator('#palette button').inner_text()
 import base64
 swatch=page.evaluate('''async()=>{const {MaterialRenderer}=await import('./renderer.js'),c=document.createElement('canvas'),r=new MaterialRenderer(c),face={id:0,ring:[[0,0],[400,0],[400,360],[0,360],[0,0]],holes:[]};await r.draw([face],{0:'glass'},400,360,50,72);for(const[x,y]of [[20,20],[200,180],[380,340]]){const p=new Uint8Array(4);r.gl.readPixels(x,y,1,1,r.gl.RGBA,r.gl.UNSIGNED_BYTE,p);if(p[0]<190||p[1]<195||p[2]<200||Math.max(...p.slice(0,3))-Math.min(...p.slice(0,3))>35)throw Error('Glass is not pale reference-style '+p);}return c.toDataURL('image/png').split(',')[1];}''')
 (ROOT/'browser-smoke-soft-glass.png').write_bytes(base64.b64decode(swatch))
 legacy=page.evaluate('()=>{const s=ParamountApp.getState();return {source_sha256:s.sourceHash,page:s.index,scale:s.scale,assignments:{[s.faces[0].id]:"glass_green"},context:[]};}')
 page.evaluate('async p=>{await ParamountApp.restoreProject(p);}',legacy)
 assert page.evaluate('Object.values(ParamountApp.getState().assignments)[0]')=='glass'
 page.evaluate('async()=>{await ParamountApp.open(new Uint8Array(await(await fetch("./demo.pdf")).arrayBuffer()),"Sample-elevation.pdf");}')
 page.select_option('#material-category','all')
 # Wand previews without committing a finish.
 wall_id=page.evaluate('ParamountApp.getState().faces.reduce((a,b)=>a.area>b.area?a:b).id')
 page.locator(f'#regions path[data-face="{wall_id}"]').dispatch_event('click')
 assert page.locator('#apply-selection').is_visible()
 assert page.evaluate('Object.keys(ParamountApp.getState().assignments).length')==0
 page.locator('#apply-selection').click()
 page.wait_for_function('Object.keys(ParamountApp.getState().assignments).length===1')
 # Local photo crop becomes a custom glass reflection.
 from PIL import Image
 image=Image.new('RGB',(160,100),(70,130,185));image.save(ROOT/'browser-smoke-photo.png')
 page.locator('#material-photo').set_input_files(str(ROOT/'browser-smoke-photo.png'))
 page.locator('#photo-dialog').wait_for(state='visible')
 page.select_option('#photo-use','glass')
 cropbox=page.locator('#photo-crop').bounding_box()
 page.mouse.move(cropbox['x']+20,cropbox['y']+20);page.mouse.down();page.mouse.move(cropbox['x']+cropbox['width']-20,cropbox['y']+cropbox['height']-20);page.mouse.up()
 page.locator('#photo-name').fill('Test sky reflection')
 page.locator('#photo-add').click()
 page.wait_for_function('Object.keys(ParamountApp.getState().customFinishes).length===1')
 photo_id=page.evaluate('Object.keys(ParamountApp.getState().customFinishes)[0]')
 page.locator('#lasso').click()
 def corner(x,y):
  r=page.locator('#regions').bounding_box();s=page.evaluate('({width:ParamountApp.getState().width,height:ParamountApp.getState().height})')
  page.mouse.click(r['x']+x*r['width']/s['width'],r['y']+y*r['height']/s['height'])
 for point in [(60,60),(170,60),(170,150),(60,150)]:corner(*point)
 page.locator('#close-lasso').focus();page.keyboard.press('Enter')
 assert page.locator('#manual-review-label').is_visible()
 assert page.locator('#manual-review').count()==0
 page.locator('#cut-opening').click()
 for point in [(90,85),(120,85),(120,115),(90,115)]:corner(*point)
 page.locator('#close-lasso').click()
 assert page.evaluate('ParamountApp.getState().manualFaces.length')==0
 page.locator('#apply-selection').focus()
 page.keyboard.press('Enter')
 page.wait_for_function('ParamountApp.getState().manualFaces.length===1')
 assert page.evaluate('ParamountApp.getState().manualFaces[0].holes.length')==1
 page.evaluate('document.querySelector("#reflection").value="0.7"')
 page.locator('#reflection').dispatch_event('input')
 # Editing is staged, supports opening handles, and commits without duplicating a mask.
 manual_id=page.evaluate('ParamountApp.getState().manualFaces[0].id')
 before_ring=page.evaluate('ParamountApp.getState().manualFaces[0].ring[0]')
 page.locator('#paint-layers').evaluate('e=>e.open=true')
 page.locator(f'#layer-list button[data-layer="{manual_id}"]').click();page.locator('#edit-outline').click()
 def drag_handle(ring,vertex,point):
  h=page.locator(f'#regions .outline-handle[data-ring="{ring}"][data-vertex="{vertex}"]').bounding_box();r=page.locator('#regions').bounding_box();s=page.evaluate('({w:ParamountApp.getState().width,h:ParamountApp.getState().height})')
  page.mouse.move(h['x']+h['width']/2,h['y']+h['height']/2);page.mouse.down();page.mouse.move(r['x']+point[0]*r['width']/s['w'],r['y']+point[1]*r['height']/s['h'],steps=4);page.mouse.up()
 drag_handle(0,0,(55,55))
 assert page.evaluate('ParamountApp.getState().manualFaces[0].ring[0]')==before_ring
 page.locator('#outline-add').click();corner(112.5,57.5)
 assert page.locator('#regions .outline-handle[data-ring="0"]').count()==5
 page.locator('#outline-remove').click();page.locator('#regions .outline-handle[data-ring="0"][data-vertex="1"]').click()
 assert page.locator('#regions .outline-handle[data-ring="0"]').count()==4
 page.locator('#outline-move').click();drag_handle(1,0,(85,80))
 page.locator('#outline-move').focus();page.keyboard.press('Enter')
 page.wait_for_function('ParamountApp.getState().manualFaces[0].ring[0][0]<58')
 assert page.evaluate('ParamountApp.getState().manualFaces.length')==1
 assert page.evaluate('ParamountApp.getState().manualFaces[0].id')==manual_id
 page.locator(f'#regions path[data-face="{manual_id}"]').dispatch_event('click')
 assert page.locator('#selection-controls').is_visible()
 assert max(abs(a-b) for a,b in zip(page.evaluate('ParamountApp.getState().manualFaces[0].holes[0][0]'),[85,80]))<2
 page.locator('#undo').click()
 assert page.evaluate('ParamountApp.getState().manualFaces[0].ring[0]')==before_ring
 page.locator(f'#layer-list button[data-layer="{manual_id}"]').click();page.locator('#edit-outline').click();drag_handle(0,0,(55,55))
 page.keyboard.press('Escape')
 assert page.evaluate('ParamountApp.getState().manualFaces[0].ring[0]')==before_ring
 assert page.locator('#regions .outline-handle').count()==0
 # Texture size is an area override, retained without changing paper scale.
 page.locator('#paint-layers').evaluate('e=>e.open=true')
 page.locator(f'#layer-list button[data-layer="{wall_id}"]').click()
 before_order=page.evaluate('JSON.stringify(ParamountApp.getState().paintOrder)')
 page.locator('#texture-size').fill('50')
 page.locator('#edit-texture').click()
 page.wait_for_function('(ParamountApp.getState().textureScales['+str(wall_id)+']||1)===.5')
 assert page.evaluate('JSON.stringify(ParamountApp.getState().paintOrder)')==before_order
 page.evaluate('''async()=>{const {MaterialRenderer,FINISHES}=await import('./renderer.js'),s=ParamountApp.getState(),c=document.createElement('canvas'),r=new MaterialRenderer(c),id=s.faces.reduce((a,b)=>a.area>b.area?a:b).id;await r.draw(s.faces,{[id]:'brick'},s.width,s.height,100,36,-45,.5,null,{textureScales:{[id]:1}});const a=r.gl.getUniform(r.program,r.gl.getUniformLocation(r.program,'repeats'))[0];await r.draw(s.faces,{[id]:'brick'},s.width,s.height,100,36,-45,.5,null,{textureScales:{[id]:.5}});const b=r.gl.getUniform(r.program,r.gl.getUniformLocation(r.program,'repeats'))[0];if(Math.abs(b/a-2)>.0001)throw Error('Half-size texture did not double repeats');if(FINISHES.glass.mode!==3||FINISHES.glass.file)throw Error('Default glass should use the diffuse reference style');}''')
 # A later overlapping white mask must cover the earlier photo finish.
 page.select_option('#material-category','Frames & metal')
 page.locator('#palette button[data-material="white"]').click()
 page.locator('#lasso').click()
 for point in [(130,60),(210,60),(210,150),(130,150)]:corner(*point)
 page.locator('#close-lasso').focus();page.keyboard.press('Enter');page.keyboard.press('Enter')
 page.wait_for_function('ParamountApp.getState().manualFaces.length===2')
 overlay_id=page.evaluate('ParamountApp.getState().manualFaces[1].id')
 def pixel(x,y):
  return page.evaluate('''([x,y])=>{const s=ParamountApp.getState(),c=document.querySelector('#finishes'),g=c.getContext('webgl2'),p=new Uint8Array(4);g.readPixels(Math.floor(x*c.width/s.width),Math.floor((s.height-y)*c.height/s.height),1,1,g.RGBA,g.UNSIGNED_BYTE,p);return [...p];}''',[x,y])
 page.wait_for_function('document.querySelector("#layer-list").lastChild!==null')
 # Wait for the scheduled material render to finish via the public API.
 page.evaluate('async()=>{const s=ParamountApp.getState();await ParamountApp.assign(s.manualFaces[1].id,"white");}')
 assert pixel(155,125)[0]>200,pixel(155,125)
 page.locator(f'#layer-list button[data-layer="{overlay_id}"]').click()
 page.locator('#layer-back').click()
 page.wait_for_function('ParamountApp.getState().paintOrder[0]==='+str(overlay_id))
 page.wait_for_timeout(300)
 assert pixel(155,125)[0]<180,pixel(155,125)
 page.locator('#layer-front').click()
 page.wait_for_function('ParamountApp.getState().paintOrder.at(-1)==='+str(overlay_id))
 page.wait_for_timeout(300)
 assert pixel(155,125)[0]>200,pixel(155,125)
 with page.expect_download(timeout=180000) as saved:
  page.locator('#save-project').click()
 saved.value.save_as(ROOT/'browser-smoke-project.json')
 saved_project=json.loads((ROOT/'browser-smoke-project.json').read_text())
 assert saved_project['customFinishes'][photo_id]['mode']==2
 assert saved_project['textureScales'][str(wall_id)]==.5
 assert saved_project['paintOrder'][-1]==overlay_id
 # Round-trip masks, images and settings, then export through native-vector QA.
 page.evaluate('async()=>{await ParamountApp.open(new Uint8Array(await(await fetch("./demo.pdf")).arrayBuffer()),"Sample-elevation.pdf");}')
 page.locator('#restore').set_input_files(str(ROOT/'browser-smoke-project.json'))
 page.wait_for_function('ParamountApp.getState().manualFaces.length===2')
 assert page.evaluate('Object.keys(ParamountApp.getState().customFinishes).length')==1
 page.select_option('#dpi','150')
 with page.expect_download(timeout=180000) as tool_export:
  tools_qa=page.evaluate('async()=>{return (await ParamountApp.exportPDF()).qa;}')
 assert all(tools_qa['checks'].values()),tools_qa
 assert tools_qa['reviewed_rendering_masks'][0]['cad_verified'] is False
 assert tools_qa['reviewed_rendering_masks'][0]['manual_review_confirmed'] is True
 assert tools_qa['photo_materials'][0]['reflection'] is True
 assert tools_qa['finish_draw_order_bottom_to_top'][-1]==overlay_id
 assert tools_qa['texture_size_multipliers'][str(wall_id)]==.5
 tool_export.value.save_as(ROOT/'browser-smoke-tools-export.pdf')
 import fitz
 exported=fitz.open(ROOT/'browser-smoke-tools-export.pdf');pix=exported[0].get_pixmap();assert pix.pixel(155,125)[0]>200,pix.pixel(155,125)
 (ROOT/'browser-smoke-tools-qa.json').write_text(json.dumps(tools_qa,indent=2))
 page.screenshot(path=str(ROOT/'browser-smoke-tools-preview.png'),full_page=True)
 page.select_option('#dpi','150')
 with page.expect_download(timeout=180000) as download:
  qa=page.evaluate('async()=>{const r=await ParamountApp.exportPDF();return r.qa;}')
 assert qa['status']=='REVIEW_REQUIRED',qa
 assert all(qa['checks'].values()),qa
 download.value.save_as(ROOT/'browser-smoke-export.pdf')
 page.screenshot(path=str(ROOT/'browser-smoke-preview.png'),full_page=True)
 assert not errors,errors
 (ROOT/'browser-smoke-qa.json').write_text(json.dumps(qa,indent=2))
 page.evaluate('async()=>{const r=await fetch("./demo.dxf"); await ParamountApp.open(new Uint8Array(await r.arrayBuffer()),"demo.dxf");}')
 assert page.evaluate('ParamountApp.getState().qa.source_bytes_unchanged')
 page.evaluate('async()=>{const s=ParamountApp.getState();await ParamountApp.assign([...s.faces].sort((a,b)=>b.area-a.area)[0].id,"stone");}')
 with page.expect_download(timeout=180000) as dxf_download:
  dxf_qa=page.evaluate('async()=>{return (await ParamountApp.exportPDF()).qa;}')
 assert all(dxf_qa['checks'].values()),dxf_qa
 assert dxf_qa['dxf_import']['model_to_paper_scale']==.02,dxf_qa
 dxf_download.value.save_as(ROOT/'browser-smoke-dxf-export.pdf')
 (ROOT/'browser-smoke-dxf-qa.json').write_text(json.dumps(dxf_qa,indent=2))
 assert not errors,errors
 oversized=ROOT/'browser-smoke-oversized.dxf'
 doc=ezdxf.new();doc.units=4;doc.modelspace().add_lwpolyline([(0,0),(50000,0),(50000,3000),(0,3000)],close=True);doc.saveas(oversized)
 page.locator('#drawing').set_input_files(str(oversized))
 page.locator('#retry-scale').wait_for(state='visible',timeout=120000)
 assert 'Traceback' not in page.locator('#status').inner_text()
 assert page.locator('#export').is_disabled()
 assert page.locator('#retry-scale').inner_text()=='Retry at 1:200'
 page.locator('#retry-scale').click()
 page.wait_for_function('ParamountApp.getState().filename === "browser-smoke-oversized.dxf" && ParamountApp.getState().scale === 200',timeout=120000)
 page.wait_for_function('document.querySelector("#busy").hidden')
 assert not page.locator('#import-error').is_visible()
 assert page.evaluate('ParamountApp.getState().qa.source_bytes_unchanged')
 assert not page.locator('#export').is_disabled()
 page.screenshot(path=str(ROOT/'browser-smoke-scale-recovery.png'),full_page=True)
 # Source-defined objects stay out of wall lassos, and reviewed windows batch-render.
 import fitz
 fixture=ROOT/'browser-smoke-objects.pdf';document=fitz.open();sheet=document.new_page(width=1191,height=842)
 sheet.draw_rect(fitz.Rect(300,420,800,600),color=(0,0,0))
 for x,ref in [(400,'W01'),(550,'W02')]:
  sheet.draw_rect(fitz.Rect(x,440,x+60,500),color=(0,0,0));sheet.draw_rect(fitz.Rect(x+4,444,x+56,496),color=(0,0,0))
  for bar in (x+28,x+32):sheet.draw_line((bar,444),(bar,496),color=(0,0,0))
  sheet.insert_text((x+20,518),ref,fontsize=9)
 sheet.draw_rect(fitz.Rect(680,510,720,600),color=(0,0,0));sheet.draw_rect(fitz.Rect(684,514,716,596),color=(0,0,0));sheet.insert_text((690,618),'D01',fontsize=9)
 sheet.draw_rect(fitz.Rect(760,420,763,600),color=(0,0,0));sheet.insert_text((30,800),'Scale 1:100',fontsize=10);document.save(fixture);document.close()
 page.locator('#drawing').set_input_files(str(fixture));page.wait_for_function('ParamountApp.getState().filename === "browser-smoke-objects.pdf" && document.querySelector("#busy").hidden',timeout=120000)
 assert page.evaluate('ParamountApp.getState().objects.filter(o=>o.type==="window").length')==2
 page.select_option('#material-category','Stone');page.locator('#palette button[data-material="stone"]').click();page.locator('#lasso').click()
 for point in [(300,420),(800,420),(800,600),(300,600)]:corner(*point)
 page.locator('#close-lasso').focus();page.keyboard.press('Enter');page.keyboard.press('Enter')
 page.wait_for_function('ParamountApp.getState().manualFaces.length===1')
 assert page.evaluate('ParamountApp.getState().manualFaces[0].exclusions.length')>=4
 page.wait_for_timeout(300)
 assert pixel(430,470)[3]==0,pixel(430,470)
 assert pixel(700,550)[3]==0,pixel(700,550)
 assert pixel(761,450)[3]==0,pixel(761,450)
 assert pixel(350,450)[3]>200,pixel(350,450)
 page.locator('#objects-panel').evaluate('e=>e.open=true');page.locator('#find-objects').click()
 page.get_by_role('checkbox',name='Render W01 as window',exact=True).check();page.get_by_role('checkbox',name='Render W02 as window',exact=True).check()
 page.select_option('#window-colour','anthracite');page.locator('#render-windows').click()
 page.wait_for_function('ParamountApp.getState().objects.filter(o=>o.renderIds?.length).length===2')
 page.wait_for_timeout(300)
 assert pixel(402,442)[0]<100 and pixel(402,442)[3]>200,pixel(402,442)
 assert pixel(410,470)[0]>190,pixel(410,470)
 assert pixel(700,550)[3]==0
 initial_masks=page.evaluate('ParamountApp.getState().manualFaces.length');page.locator('#render-windows').click();page.wait_for_timeout(300)
 assert page.evaluate('ParamountApp.getState().manualFaces.length')==initial_masks
 with page.expect_download(timeout=180000) as objects_saved:page.locator('#save-project').click()
 objects_saved.value.save_as(ROOT/'browser-smoke-objects-project.json')
 project=json.loads((ROOT/'browser-smoke-objects-project.json').read_text());page.evaluate('async p=>{await ParamountApp.restoreProject(p);}',project)
 assert page.evaluate('ParamountApp.getState().objects.filter(o=>o.type==="window").length')==2
 page.select_option('#dpi','150')
 with page.expect_download(timeout=180000) as objects_export:objects_qa=page.evaluate('async()=>{return (await ParamountApp.exportPDF()).qa;}')
 assert all(objects_qa['checks'].values()),objects_qa
 assert len(objects_qa['protected_objects'])>=4
 objects_export.value.save_as(ROOT/'browser-smoke-objects-export.pdf');(ROOT/'browser-smoke-objects-qa.json').write_text(json.dumps(objects_qa,indent=2))
 pdf=fitz.open(ROOT/'browser-smoke-objects-export.pdf');raster=pdf[0].get_pixmap();assert raster.pixel(700,550)==(255,255,255),raster.pixel(700,550)
 assert objects_qa['pdf_export_mode']=='compact' and objects_qa['embedded_finish_images']==1,objects_qa
 compact_images=pdf[0].get_images();assert len(compact_images)==1,len(compact_images)
 # Compare layered and compact output on the same reviewed masks, windows and pipes.
 page.select_option('#pdf-mode','layered')
 with page.expect_download(timeout=180000) as layered_export:layered_qa=page.evaluate('async()=>{return (await ParamountApp.exportPDF()).qa;}')
 assert all(layered_qa['checks'].values()),layered_qa
 layered_export.value.save_as(ROOT/'browser-smoke-layered-export.pdf')
 layered=fitz.open(ROOT/'browser-smoke-layered-export.pdf');layered_raster=layered[0].get_pixmap()
 assert layered_qa['embedded_finish_images']>1,layered_qa
 assert len(layered[0].get_images())>len(compact_images)
 # Equal ordered appearance (allow minor alpha-compositing rounding differences).
 from PIL import ImageChops,ImageStat
 delta=ImageChops.difference(Image.frombytes('RGB',[raster.width,raster.height],raster.samples),Image.frombytes('RGB',[layered_raster.width,layered_raster.height],layered_raster.samples))
 assert max(ImageStat.Stat(delta).mean)<1,ImageStat.Stat(delta).mean
 assert (ROOT/'browser-smoke-objects-export.pdf').stat().st_size < (ROOT/'browser-smoke-layered-export.pdf').stat().st_size
 page.select_option('#pdf-mode','compact')
 page.screenshot(path=str(ROOT/'browser-smoke-objects-preview.png'),full_page=True)
 # Delete older/restored trees without touching material masks or original geometry.
 page.locator('#tree').click();corner(500,550)
 page.wait_for_function('ParamountApp.getState().context.length===1')
 page.locator('#plan-tree').click();corner(520,550)
 page.wait_for_function('ParamountApp.getState().context.length===2')
 planted=page.evaluate('JSON.parse(JSON.stringify(ParamountApp.getState().context))')
 before_delete=page.evaluate('JSON.stringify({a:ParamountApp.getState().assignments,m:ParamountApp.getState().manualFaces,order:ParamountApp.getState().paintOrder})')
 # Simulate reopening saved choices containing these existing trees.
 project['context']=planted;page.evaluate('async p=>{await ParamountApp.restoreProject(p);}',project)
 page.locator('#delete-tree').click();assert page.locator('.tree-delete-target').count()==2
 corner(50,50);assert page.evaluate('ParamountApp.getState().context.length')==2
 corner(510,500);page.wait_for_function('ParamountApp.getState().context.length===1')
 assert page.evaluate('ParamountApp.getState().context[0].type')=='tree' # Topmost overlapping plan tree removed first.
 assert page.evaluate('JSON.stringify({a:ParamountApp.getState().assignments,m:ParamountApp.getState().manualFaces,order:ParamountApp.getState().paintOrder})')==before_delete
 page.locator('#undo').click();page.wait_for_function('ParamountApp.getState().context.length===2')
 assert page.evaluate('ParamountApp.getState().context')==planted
 page.locator('#delete-tree').click();page.keyboard.press('Escape');assert page.locator('.tree-delete-target').count()==0
 page.locator('#delete-tree').click();corner(460,450) # Older elevation tree, outside the plan tree.
 assert page.evaluate('ParamountApp.getState().context.length')==1
 assert page.evaluate('ParamountApp.getState().context[0].type')=='plan'
 corner(510,500);page.wait_for_function('ParamountApp.getState().context.length===0')
 page.locator('#wand').click();assert page.locator('#delete-tree').get_attribute('aria-pressed')=='false'
 with page.expect_download(timeout=180000) as deleted_save:page.locator('#save-project').click()
 deleted_save.value.save_as(ROOT/'browser-smoke-deleted-tree-project.json')
 assert json.loads((ROOT/'browser-smoke-deleted-tree-project.json').read_text())['context']==[]
 assert not errors,errors
 # GPU opacity lightens surface colour while preserving masks, overlap order,
 # glass and solid frame colours. Low opacity must not reveal lower finishes.
 page.evaluate('''async()=>{
  const {MaterialRenderer}=await import('./renderer.js');const c=document.createElement('canvas'),r=new MaterialRenderer(c);
  const rect=(id,x,y,w,h)=>({id,ring:[[x,y],[x+w,y],[x+w,y+h],[x,y+h],[x,y]],holes:[]});const faces=[rect(0,10,10,70,70),rect(1,30,30,40,40)];
  const sample=()=>{const p=new Uint8Array(4);r.gl.readPixels(45,55,1,1,r.gl.RGBA,r.gl.UNSIGNED_BYTE,p);return [...p];};
  const options={paintOrder:[0,1],textureOpacity:100};
  await r.draw(faces,{0:'stone',1:'brick'},100,100,50,72,-45,.5,null,options);const full=sample();
  await r.draw(faces,{0:'stone',1:'brick'},100,100,50,72,-45,.5,null,{...options,textureOpacity:65});const faded=sample();
  if(faded[3]!==full[3]||faded.slice(0,3).some((v,i)=>Math.abs(v-(255*.35+full[i]*.65))>2))throw Error('Texture fade changed coverage or colour incorrectly '+[full,faded]);
  await r.draw(faces,{0:'stone',1:'brick'},100,100,50,72,-45,.5,null,{...options,textureOpacity:0});if(sample().some(v=>v!==255))throw Error('Faded upper texture revealed lower surface');
  for(const kind of ['glass','anthracite']){await r.draw([faces[0]],{0:kind},100,100,50,72,-45,.5,null,options);const a=sample();await r.draw([faces[0]],{0:kind},100,100,50,72,-45,.5,null,{...options,textureOpacity:0});if(JSON.stringify(a)!==JSON.stringify(sample()))throw Error(kind+' was faded');}
  r.gl.getExtension('WEBGL_lose_context')?.loseContext();
 }''')
 # Synthetic dense CAD hatchwork: opening and lasso export must retain every
 # source segment even when automatic detection switches to manual review.
 dense_path=ROOT/'browser-smoke-dense.pdf';dense=fitz.open();dense_page=dense.new_page(width=1191,height=842);shape=dense_page.new_shape()
 for i in range(94000):
  x=50+(i%470)*2;y=300+(i//470)*.5;shape.draw_line((x,y),(x+1,y+.2))
 shape.finish(color=(0,0,0),width=.1);shape.commit();dense_page.insert_text((50,50),'Synthetic detail 1:100',fontsize=10);dense.save(dense_path);dense.close()
 page.locator('#drawing').set_input_files(str(dense_path))
 page.wait_for_function('ParamountApp.getState().filename === "browser-smoke-dense.pdf" && document.querySelector("#busy").hidden',timeout=120000)
 assert page.evaluate('ParamountApp.getState().segments.length')>=94000
 assert page.locator('#boundary-warning').is_visible()
 assert 'Polygon lasso' in page.locator('#boundary-warning').inner_text()
 assert not page.locator('#export').is_disabled()
 page.locator('#lasso').click()
 for point in [(100,100),(200,100),(200,200),(100,200)]:corner(*point)
 page.locator('#close-lasso').focus();page.keyboard.press('Enter');page.keyboard.press('Enter')
 page.wait_for_function('ParamountApp.getState().manualFaces.length===1')
 page.locator('#drawing-mode').click();page.wait_for_timeout(300)
 assert page.locator('#texture-opacity').input_value()=='65'
 assert page.locator('#texture-opacity-value').inner_text()=='65%'
 with page.expect_download(timeout=180000) as readability_saved:page.locator('#save-project').click()
 readability_saved.value.save_as(ROOT/'browser-smoke-readability-project.json')
 readability=json.loads((ROOT/'browser-smoke-readability-project.json').read_text());assert readability['textureOpacity']==65
 page.locator('#presentation-mode').click();assert page.locator('#texture-opacity').input_value()=='100'
 page.evaluate('async p=>{await ParamountApp.restoreProject(p);}',readability)
 assert page.locator('#texture-opacity').input_value()=='65'
 assert page.locator('#drawing-mode').get_attribute('aria-pressed')=='true'
 assert page.evaluate("async p=>{try{await ParamountApp.restoreProject({...p,textureOpacity:101});return false;}catch{return true;}}",readability)
 page.select_option('#dpi','150')
 with page.expect_download(timeout=180000) as dense_export:dense_qa=page.evaluate('async()=>{return (await ParamountApp.exportPDF()).qa;}')
 assert all(dense_qa['checks'].values()),dense_qa
 assert dense_qa['texture_opacity_percent']==65,dense_qa
 assert dense_qa['original_vector_segments_checked']>=94000,dense_qa
 assert dense_qa['boundary_detection_warning'] and dense_qa['object_detection_notes']
 dense_export.value.save_as(ROOT/'browser-smoke-dense-export.pdf')
 (ROOT/'browser-smoke-dense-qa.json').write_text(json.dumps(dense_qa,indent=2))
 assert not errors,errors
 browser.close()
server.shutdown();print('Real browser import, WebGL material and native-vector PDF export passed.')
