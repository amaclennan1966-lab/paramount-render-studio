"""Deterministic provider integration: CORS textures, persistence, rendering and PDF QA."""
from pathlib import Path
import http.server,threading,functools,json
from playwright.sync_api import sync_playwright
from workspace_navigation import WorkspacePage
ROOT=Path(__file__).resolve().parents[1]
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=WorkspacePage(browser.new_page(accept_downloads=True)); errors=[]; requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 def provider(route):
  requests.append(route.request.url)
  headers={'Access-Control-Allow-Origin':'*'}
  if '/assets?' in route.request.url:
   route.fulfill(json={'test_brick':{'name':'Test brick','categories':['brick'],'dimensions':[1,2]}},headers=headers)
  elif '/files/' in route.request.url:
   route.fulfill(json={'Diffuse':{'1k':{'jpg':{'url':'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/test_brick/test_brick_diff_1k.jpg'}}}},headers=headers)
  else: route.fulfill(body=(ROOT/'public/assets/brick.jpg').read_bytes(),content_type='image/jpeg',headers=headers)
 page.route('https://api.polyhaven.com/**',provider)
 page.route('https://dl.polyhaven.org/**',provider)
 page.route('https://cdn.polyhaven.com/**',provider)
 page.goto(f'http://127.0.0.1:{server.server_port}',wait_until='networkidle',timeout=120000)
 page.wait_for_function('!!window.ParamountApp',timeout=120000)
 page.locator('#demo').click();page.wait_for_function('!!window.renderStudioState',timeout=120000)
 assert not requests,requests
 original=page.evaluate('({width:renderStudioState.width,height:renderStudioState.height,scale:renderStudioState.scale,hash:renderStudioState.sourceHash,segments:JSON.stringify(renderStudioState.segments)})')
 page.locator('#online-library summary').click();page.locator('#load-library').click()
 page.locator('.online-finish').click()
 page.wait_for_function("!!renderStudioState.libraryFinishes.ph_test_brick")
 face=page.evaluate('renderStudioState.faces.reduce((a,b)=>a.area>b.area?a:b).id')
 page.locator(f'#regions [data-face="{face}"]').dispatch_event('click')
 page.locator('#apply-selection').click()
 page.wait_for_function("Object.values(renderStudioState.assignments).includes('ph_test_brick')")
 with page.expect_download() as saved:page.locator('#save-project').click()
 project=json.loads(saved.value.path().read_text())
 assert project['libraryFinishes']['ph_test_brick']['tile']==2000
 page.evaluate('async p=>await ParamountApp.restoreProject(p)',project)
 page.select_option('#dpi','150')
 with page.expect_download(timeout=180000): qa=page.evaluate('async()=> (await ParamountApp.exportPDF()).qa')
 assert all(qa['checks'].values()),qa
 assert qa['catalogue_materials']['ph_test_brick']['provider']=='Poly Haven CC0'
 assert page.evaluate('({width:renderStudioState.width,height:renderStudioState.height,scale:renderStudioState.scale,hash:renderStudioState.sourceHash,segments:JSON.stringify(renderStudioState.segments)})')==original
 assert not errors,errors
 browser.close()
server.shutdown()
print('Optional catalogue, GPU render, save/restore and original-vector PDF QA passed.')

