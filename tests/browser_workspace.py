"""Real workspace interactions and laptop/desktop screenshots; synthetic drawing only."""
from pathlib import Path
import http.server,threading,functools,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900},accept_downloads=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 try:
  page.goto(f'http://127.0.0.1:{server.server_port}',wait_until='networkidle',timeout=120000)
  page.wait_for_function('!!window.ParamountApp && !!window.ParamountWorkspace',timeout=120000)
  assert page.evaluate('ParamountWorkspace.sourceIds.every(id=>!!document.getElementById(id))')
  assert page.locator('[data-panel]:visible').count()==1
  for b in page.locator('#tool-rail button').all():assert b.get_attribute('title') and b.get_attribute('aria-label')
  page.locator('#demo').click();page.wait_for_function('!!window.renderStudioState && document.querySelector("#busy").hidden',timeout=120000)
  source=page.evaluate('JSON.stringify({scale:renderStudioState.scale,width:renderStudioState.width,height:renderStudioState.height,segments:renderStudioState.segments,hash:renderStudioState.sourceHash})')
  # Every original control is retained, focusable via its appropriate contextual panel.
  panels=page.evaluate('ParamountWorkspace.panels()')
  for name in panels:
   page.evaluate('name=>ParamountWorkspace.showPanel(name)',name)
   assert page.locator('[data-panel]:visible').count()==1
  page.locator('[data-ui-tool=brick]').click();assert page.locator('#material-category').input_value()=='Brick'
  page.locator('[data-ui-tool=roofs]').click();assert page.locator('#material-category').input_value()=='Roofing'
  page.locator('[data-ui-tool=materials]').click();assert page.locator('#palette button').count()==68
  page.select_option('#material-category','Solid colours');assert page.locator('#palette button').count()==30
  page.evaluate('async()=>{const s=ParamountApp.getState();await ParamountApp.assign(s.faces.reduce((a,b)=>a.area>b.area?a:b).id,"brick");}')
  original_pixels=page.locator('#finishes').evaluate('c=>c.toDataURL()')
  # Placeholder workspaces never clear or mutate the loaded drawing.
  for name in ['CAD','SITE PLAN']:
   page.get_by_role('button',name=name,exact=True).click();assert page.locator('#workspace-placeholder').is_visible()
   page.get_by_role('button',name='Return to RENDER',exact=True).click()
  assert page.locator('#workspace-placeholder').is_hidden()
  page.locator('#collapse-properties').click();assert page.locator('#properties').is_hidden()
  page.locator('#toggle-properties').click();assert page.locator('#properties').is_visible()
  page.locator('#properties-resize').focus();page.keyboard.press('ArrowLeft');assert page.locator('#properties-resize').get_attribute('aria-valuenow')=='316'
  page.locator('#canvas-focus').click();assert page.locator('#properties').is_hidden()
  page.keyboard.press('Escape');assert page.locator('#properties').is_visible()
  page.locator('#canvas-focus').click();page.keyboard.press('f');assert not page.evaluate('document.body.classList.contains("canvas-focus")')
  # Dedicated pan tool delegates to the existing Space-drag behaviour.
  page.locator('#zoom-in').click();page.locator('#zoom-in').click();page.locator('#zoom-in').click()
  v=page.locator('#viewport').bounding_box();page.locator('[data-ui-tool=pan]').click()
  before=page.locator('#viewport').evaluate('v=>[v.scrollLeft,v.scrollTop]')
  page.mouse.move(v['x']+v['width']/2,v['y']+v['height']/2);page.mouse.down();page.mouse.move(v['x']+v['width']/2-80,v['y']+v['height']/2-50,steps=5);page.mouse.up()
  after=page.locator('#viewport').evaluate('v=>[v.scrollLeft,v.scrollTop]');assert after[0]>before[0]+40 or after[1]>before[1]+30,(before,after)
  page.locator('[data-ui-tool=materials]').click();page.locator('#fit').click()
  assert page.locator('#finishes').evaluate('c=>c.toDataURL()')==original_pixels
  assert page.evaluate('JSON.stringify({scale:renderStudioState.scale,width:renderStudioState.width,height:renderStudioState.height,segments:renderStudioState.segments,hash:renderStudioState.sourceHash})')==source
  # Existing source notes remain accessible without an invented annotation engine.
  page.locator('[data-ui-tool=annotations]').click();assert page.locator('#notes').is_visible()
  page.locator('[data-ui-tool=materials]').click();page.select_option('#material-category','Brick')
  for width,height in [(1366,768),(1440,900),(1920,1080)]:
   page.set_viewport_size({'width':width,'height':height});page.locator('#fit').click()
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   canvas=page.locator('#viewport').bounding_box();assert canvas['width']>width*.68,(width,canvas)
   paper=page.locator('#sheet').bounding_box();assert paper['y']>=canvas['y'] and paper['y']+paper['height']<=canvas['y']+canvas['height']+.5,(canvas,paper)
   assert paper['x']>=canvas['x'] and paper['x']+paper['width']<=canvas['x']+canvas['width']+.5,(canvas,paper)
   assert page.locator('#properties').bounding_box()['width']<=440
   page.screenshot(path=str(ROOT/f'browser-smoke-workspace-{width}x{height}.png'),full_page=True)
  page.locator('#canvas-focus').click();page.screenshot(path=str(ROOT/'browser-smoke-workspace-focus.png'),full_page=True);page.keyboard.press('Escape')
  page.set_viewport_size({'width':390,'height':844});page.locator('#collapse-properties').click()
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.locator('[data-ui-tool=glazing]').click();assert page.locator('#objects-panel').is_visible()
  page.screenshot(path=str(ROOT/'browser-smoke-workspace-mobile.png'),full_page=True)
  assert not errors,errors
  (ROOT/'browser-smoke-workspace-qa.json').write_text(json.dumps({'screens':[1366,1440,1920,390],'source_geometry_unchanged':True,'render_pixels_unchanged':True,'all_original_ids_retained':True,'visible_panels':1,'errors':errors},indent=2))
 finally:
  page.screenshot(path=str(ROOT/'browser-smoke-workspace-final.png'),full_page=True)
  browser.close()
server.shutdown();print('Compact workspace, source geometry, identical rendered pixels and responsive screenshots passed.')
