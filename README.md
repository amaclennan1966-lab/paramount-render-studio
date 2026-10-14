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

## Selection and sampled materials

Wand previews a closed source region; choose a finish and Apply selected finish.
Polygon lasso snaps within 10 screen pixels to source endpoints or finite edges.
Close outline creates a preview; Cut opening draws an exclusion inside it.
Edges that do not coincide with source linework require explicit confirmation of the preview by Enter or the Apply finish button.
These are separate presentation masks, recorded in QA with their unmatched edges;
original CAD geometry and PDF streams remain unchanged. Self-intersecting outlines
and overlapping/outside exclusions are rejected. Escape cancels; Enter closes an outline; Enter again confirms and applies it.

Sample a photo opens a local crop editor. Drag a material rectangle, or click a
pixel for sampled colour. Choose repeating texture or glass reflection, name it
and set its physical repeat width. Photo crops are saved in finish-choice JSON;
keep those project files private if the photos are private. Photo textures are
not automatically seamless, perspective-corrected or supplied with normal maps.
Glass reflection strength mixes a continuous image across panes using the same
finish with interior shading. Reflections are illustrative, not a 3D simulation.

Save finish choices includes reviewed masks, photo crops and reflection strength.
Restore rechecks mask validity against the matching source sheet and scale.

## Material library

The expanded built-in library has 40 finishes: ten additional checksum-verified
CC0 photographic surfaces, labelled colour variants, frame/metal colours, glass
tints and the original finishes. Search by material name or RAL code, or filter
by category. Finish IDs are stable so older saved projects remain compatible.
The app bundles textures locally; provider APIs are used only when preparing
new assets. Additional photo provenance is in public/assets/library/manifest.json.
All texture repeat sizes and RAL screen colours require product review.

## Draw order and texture size

Finishes paint from bottom to top in application order: the last applied finish
covers earlier overlapping finishes. Render draw order lists the topmost entry
first; select an entry to Bring to front, Send to back or Move up/down. Original
CAD linework stays above all material layers. PDF export follows the same order.
Opening exclusions stay transparent and reveal finishes beneath them.

Select a rendered area with the wand or layer list, change Texture size (%) and
press Update texture size. 50% gives half-size bricks; 200% doubles their size.
New outlines use the size set before Apply selected finish. This changes only
the physical material repeat, not CAD coordinates or paper scale. Glass uses
continuous reflections instead of tiled bricks and now has greener default tint
and interior shading. Saved projects and QA include order and texture sizes.

## Mouse wheel and Return

Wheel over the drawing to zoom around the pointer; the sidebar still scrolls
normally. View zoom never changes PDF page size, CAD dimensions or print scale.
Fit sheet resets the viewing zoom. Zoom is bounded between 8% and 800%.

Return/Enter closes a lasso outline. With a completed preview, Return/Enter
confirms the boundary and applies the selected finish. No review checkbox is
needed. The preview clearly identifies manually defined edges; confirming them
still records manual review in QA. Held-key repeats cannot accidentally confirm
a second action; typing in search fields does not apply finishes.

## Editable masks and panning

Preview a finished area using the wand or Render draw order, then choose Edit
outline. Drag handles on the outer perimeter or opening exclusions; nearby source
corners and edges snap. Add corner inserts a point on a clicked outline edge;
Remove corner deletes a clicked handle while retaining at least three points.
Self-crossings and invalid opening overlaps are rejected. Enter commits the edited
mask and rechecks its edges for QA; Escape cancels the preview. Undo restores the
previous mask after a committed edit. Source CAD/PDF lines are never dragged.

Hold Space and drag over the drawing to pan at any zoom. Panning does not paint
areas, place plants, move mask handles or alter PDF scale. Release Space to resume
the current tool. Text fields retain their normal Space-key behaviour.
