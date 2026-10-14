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
 assert page.locator('#palette button').count()==40
 page.evaluate('''async()=>{const {FINISHES,MaterialRenderer}=await import('./renderer.js');const s=ParamountApp.getState(),id=s.faces.reduce((a,b)=>a.area>b.area?a:b).id,c=document.createElement('canvas'),r=new MaterialRenderer(c);for(const key of Object.keys(FINISHES).filter(k=>k.startsWith('library_'))){await r.draw(s.faces,{[id]:key},s.width,s.height,s.scale,36);const pixels=new Uint8Array(c.width*c.height*4);r.gl.readPixels(0,0,c.width,c.height,r.gl.RGBA,r.gl.UNSIGNED_BYTE,pixels);if(!pixels.some((v,i)=>i%4===3&&v>0)||r.gl.getError()!==r.gl.NO_ERROR)throw Error('Material render failed '+key);}}''')
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
 page.locator('#paint-layers').evaluate('e=>e.open=true')
 page.locator(f'#layer-list button[data-layer="{manual_id}"]').click();page.locator('#edit-outline').click()
 def drag_handle(ring,vertex,point):
  h=page.locator(f'#regions .outline-handle[data-ring="{ring}"][data-vertex="{vertex}"]').bounding_box();r=page.locator('#regions').bounding_box();s=page.evaluate('({w:ParamountApp.getState().width,h:ParamountApp.getState().height})')
  page.mouse.move(h['x']+h['width']/2,h['y']+h['height']/2);page.mouse.down();page.mouse.move(r['x']+point[0]*r['width']/s['w'],r['y']+point[1]*r['height']/s['h'],steps=4);page.mouse.up()
 drag_handle(0,0,(55,55))
 assert page.evaluate('ParamountApp.getState().manualFaces[0].ring[0]')==[60,60]
 page.locator('#outline-add').click();corner(112.5,57.5)
 assert page.locator('#regions .outline-handle[data-ring="0"]').count()==5
 page.locator('#outline-remove').click();page.locator('#regions .outline-handle[data-ring="0"][data-vertex="1"]').click()
 assert page.locator('#regions .outline-handle[data-ring="0"]').count()==4
 page.locator('#outline-move').click();drag_handle(1,0,(85,80))
 page.locator('#outline-move').focus();page.keyboard.press('Enter')
 page.wait_for_function('ParamountApp.getState().manualFaces[0].ring[0][0]===55')
 assert page.evaluate('ParamountApp.getState().manualFaces.length')==1
 assert page.evaluate('ParamountApp.getState().manualFaces[0].id')==manual_id
 assert page.evaluate('ParamountApp.getState().manualFaces[0].holes[0][0]')==[85,80]
 page.locator('#undo').click()
 assert page.evaluate('ParamountApp.getState().manualFaces[0].ring[0]')==[60,60]
 page.locator(f'#layer-list button[data-layer="{manual_id}"]').click();page.locator('#edit-outline').click();drag_handle(0,0,(55,55))
 page.keyboard.press('Escape')
 assert page.evaluate('ParamountApp.getState().manualFaces[0].ring[0]')==[60,60]
 assert page.locator('#regions .outline-handle').count()==0
 # Texture size is an area override, retained without changing paper scale.
 page.locator('#paint-layers').evaluate('e=>e.open=true')
 page.locator(f'#layer-list button[data-layer="{wall_id}"]').click()
 before_order=page.evaluate('JSON.stringify(ParamountApp.getState().paintOrder)')
 page.locator('#texture-size').fill('50')
 page.locator('#edit-texture').click()
 page.wait_for_function('(ParamountApp.getState().textureScales['+str(wall_id)+']||1)===.5')
 assert page.evaluate('JSON.stringify(ParamountApp.getState().paintOrder)')==before_order
 page.evaluate('''async()=>{const {MaterialRenderer,FINISHES}=await import('./renderer.js'),s=ParamountApp.getState(),c=document.createElement('canvas'),r=new MaterialRenderer(c),id=s.faces.reduce((a,b)=>a.area>b.area?a:b).id;await r.draw(s.faces,{[id]:'brick'},s.width,s.height,100,36,-45,.5,null,{textureScales:{[id]:1}});const a=r.gl.getUniform(r.program,r.gl.getUniformLocation(r.program,'repeats'))[0];await r.draw(s.faces,{[id]:'brick'},s.width,s.height,100,36,-45,.5,null,{textureScales:{[id]:.5}});const b=r.gl.getUniform(r.program,r.gl.getUniformLocation(r.program,'repeats'))[0];if(Math.abs(b/a-2)>.0001)throw Error('Half-size texture did not double repeats');if(FINISHES.glass.tint[1]<=FINISHES.glass.tint[2])throw Error('Default glass is not greener');}''')
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
 browser.close()
server.shutdown();print('Real browser import, WebGL material and native-vector PDF export passed.')
