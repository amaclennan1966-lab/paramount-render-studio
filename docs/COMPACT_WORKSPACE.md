# Compact icon workspace

Review branch: `feature/compact-icon-workspace`. Do not merge or publish without review.

## Architecture and scope

The existing application is plain ES modules, not React. `workspace.js` moves the original live controls into contextual panels and delegates toolbar commands to their original handlers. `workspace.css` adds the dark shell over the existing styles. `app.js` only gains the UI module import; the renderer, masks, material library, PDF/DXF logic and saved-choice schema are unchanged. The icons are bundled inline vector paths, with accessible names and native tooltips; no framework, icon CDN or build dependency is added.

## Existing function inventory and access

| Tool group | Features retained | Access |
| --- | --- | --- |
| Document | Original PDF/DXF upload, sample, paper/material scale, PDF sheets, oversize retry | Folder and ruler icons; Document & scale |
| Selection | Wand, lasso, inspection, close/back/cancel, manual-boundary review, hole cut, internal-object exclusion, outline move/add/remove, Enter confirmation | Selection icons; Selection & mask |
| Finishes | All 68 built-ins, 30 solid colours, search/categories, photo crops, sampled colour/reflection, optional Poly Haven catalogue/search/import | Palette, brick and roof icons; Materials & finishes |
| Windows | Source object previews, review checkboxes, frame colours, batch glass/frames, manual window/door/pipe protection | Glazing icon; Windows & glazing |
| Layer management | Current finish, texture size, bring/send/front/back/up/down, layer list, clear finish, Undo | Layers and selection panels; erase/undo icons |
| Readability | Drawing/presentation presets and texture opacity | Materials panel → Texture opacity & drawing readability |
| Lighting | Sun direction, relief and glass reflection strength | Lighting or glazing panel |
| Context | Elevation tree, plan tree and undoable tree deletion | Tree icon; Landscaping |
| Notes | Full source notes, review caveats and original annotation information | Notes icon; Source annotations |
| Projects | Save choices and restore including imported catalogue/photo finishes | Save icon; Save & restore |
| Export | Compact/layered PDF, DPI, export, separate QA report | Export icon; Export & QA |
| View | Mouse-wheel zoom, pointer anchoring, Space pan, dedicated pan button, zoom buttons, fit, canvas focus | Hand icon, canvas bar, F / Escape |

Original dimensions and notes are retained. No measurement, annotation editing, layer-visibility engine or new CAD/site engine is invented. CAD and SITE PLAN are labelled interface placeholders; switching them does not clear the open render.

## Interface behaviour

One contextual panel appears at a time. The right panel has a collapse button, a draggable divider (240–440 px), and keyboard divider resizing using Left/Right arrows. Panel width is a UI preference, separate from saved drawing choices. Existing per-panel sections remain collapsible. Selecting a mask reveals its original selection controls. Canvas focus hides the rail, header and properties, retaining drawing navigation and status; F toggles it and Escape exits. Input fields and photo dialogs retain their normal keyboard behaviour.

At widths of 750 px or less the properties panel becomes an overlay, with the drawing accessible after collapse. Desktop screenshots use 1366×768, 1440×900 and 1920×1080; an additional phone view checks overflow at 390×844. Screenshots contain only the bundled synthetic sample, not customer drawings.

## Verification

Run `npm test`, syntax checks for `app.js`, `workspace.js`, `renderer.js`, `pdf-input.js` and `polyhaven.js`, plus `python tests/test_cad_import.py`. With Playwright Chromium installed, run `python tests/browser_workspace.py`, `python tests/browser_polyhaven.py` and `python tests/browser_smoke.py`.

The original browser regressions retain their rendering, import/export and project checks. `workspace_navigation.py` opens the appropriate real contextual panel before acting on an existing control, rather than bypassing the interface or showing all panels. The new dedicated workspace test uses actual toolbar interactions, verifies every original control ID, panel isolation, pan, resize, placeholder round-trip, source coordinate/hash equality, and byte-identical finish canvas pixels after UI-only changes.

The existing Pages workflow still publishes only main. The review workflow has read-only permissions and no Pages deployment. Review artifacts include screenshots and geometry QA. The final test results and PR checks are the source of truth; no production deployment is part of this change.

## Known boundaries

CAD and SITE PLAN are intentional placeholders. Existing material, scale, source-detail and manually reviewed mask limitations remain. Full native OS/browser fullscreen is not requested; canvas focus provides the uncluttered in-app view and keeps an accessible exit. No new lint/build pipeline is introduced because this static application has no configured bundler or linter.
