# Paramount Render Studio

A standalone browser architectural renderer for free static hosting. No AI API,
AI tokens, paid rendering server or backend account is required. PDF/DXF bytes stay
on the user's device. The website downloads its pinned open-source libraries and
material assets; it does not send drawings to a rendering service.

## GitHub Pages

1. Create a **public** GitHub repository named `paramount-render-studio`, initialise
   it with a README, and upload this project's contents (not a ZIP file).
2. Open **Settings → Pages → Source → GitHub Actions** if Pages is not already
   enabled. The included workflow tests the app before publishing it.
3. Open the URL shown by the successful **Publish Paramount Render Studio** action.

Free GitHub Pages hosting applies to eligible public repositories within GitHub's
usage limits. It does not provide free server-side GPU rendering. This app uses
WebGL on the user's own device instead.

Repository: https://github.com/amaclennan1966-lab/paramount-render-studio

Pages must use GitHub Actions as its source in repository Settings.

## Use

Open the site in a modern browser with WebGL 2. Upload a vector PDF or a DXF whose
model-space units explicitly declare millimetres. Select a finish, then click a
closed source area. Adjust daylight and normal-map relief. Place illustrative
trees by clicking at ground level; undo removes the last edit. Save choices and
restore them after opening the matching drawing, page and scale.

Export gives a PDF containing photographic finish layers below original vector
linework. Download the QA report with its separate button. For a multi-page PDF,
only the selected sheet is rendered; other sheets are retained. Finish choices
are per sheet: save before switching sheets. Original drawings are never uploaded
to GitHub or included in the repository.

DXF imports use Python 3.12 / ezdxf 1.4.4 through Pyodide in a browser worker.
They export model-space geometry to a new A3 landscape sheet at the chosen scale
without fitting. Existing DXF paperspace title blocks, complex block boundaries
and curved material boundaries require the desktop renderer or a plotted PDF.
PDF inputs keep their original physical page size and scale; the scale control
sets the physical texture repeat only. No automatic rescaling is applied.

## Quality and limits

Real photographic diffuse and normal maps supply material relief, sun lighting
and generic reflections. This is an exact-projection photographic material
renderer, **not a ray-traced 3D building reconstruction**. It does not infer roof
pitch, building depth or new openings from photographs. Closed boundaries come
from finite source intersections; open gaps are not bridged. Materials and their
region assignments require explicit review. Screen colours, generic textures and
illustrative planting are not manufacturer-certified or surveyed specifications.

PDF export validates that original content streams, vector segment coordinates,
annotations and page size survive. DXF QA records unchanged source bytes,
original dimensions/extents and the fixed model-to-paper transform. A source PDF
cannot verify missing AutoCAD model-space coordinates. Output resolution depends
on device WebGL limits; the report states the achieved DPI.

A first DXF import downloads the Python runtime and its dependencies. Internet
access is required to load libraries. There is no tracking or AI inference in
this application. Use the browser's own PDF save/share controls on mobile.

## Local development

```sh
python -m http.server 8080
```

Open `http://localhost:8080`. No npm install or application build is needed.

```sh
node tests/geometry.test.js
pip install ezdxf==1.4.4 Pillow
python tests/test_cad_import.py
# Browser test (requires Chromium and network access for pinned CDN modules):
pip install playwright
playwright install chromium
python tests/browser_smoke.py
```

## Licences

Photographic materials and tree cutouts derive from Poly Haven CC0 assets listed
in `public/assets/LICENSES.json`. The bundled pure-Python ezdxf files are MIT
licensed. PDF.js is Apache 2.0; pdf-lib, jsPDF, svg2pdf.js and Pyodide have their
respective upstream licences. Include third-party notices when redistributing.
The sample drawing is synthetic; no customer drawing is included.
