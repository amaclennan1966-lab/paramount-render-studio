# PR #1 integration review — 17 October 2026

Base: b46721151d671553f54095092ed34049638ea87d.
PR head: c66d71774a8520bf261d0d68f61b5ca1a454b612.
Local branch: integrate-polyhaven.

## Comparison

Git confirms main has 16 distinct commits and PR #1 has eight.
GitHub reports PR #1 open, draft, unmerged and not mergeable.
Do not merge its older renderer wholesale.

| PR capability | Current main | Integration decision |
|---|---|---|
| Finish search and category filtering | Already implemented | Retain main |
| Architectural photographic finishes | 10 bundled source materials, with variants | Retain main and provenance checks |
| Plain colours and frame/render choices | Includes 30 standalone solid colours | Retain; do not import overlapping legacy presets |
| Three alternative reflective glass presets | Main deliberately consolidates legacy IDs into pale glass | Preserve main's migration and glass |
| Optional searchable Poly Haven catalogue | Missing | Port into separate polyhaven.js |
| Provider-reference persistence and QA | Missing | Add alongside existing photo and mask persistence |

Main's installed catalogue remains exactly 68 finishes. PR-only tint and solid presets
are presentation alternatives rather than new photographic surfaces; not imported.
The online catalogue supplies additional photographic surfaces on demand.

## Compatible implementation

No CAD import, PDF input, geometry, selection, outline-edit, paint-order or object
detection modules were replaced. Main's shader controls, mask exclusions, draw
order, texture multipliers, opacity and glass rendering remain in place.
Only image source selection and independent texture repeat height were extended.
Remote image loading uses anonymous CORS; failed loads can be retried.
Provider URLs and saved references are allowlisted; fetches have 15-second timeouts.
No drawing bytes are sent to the provider.

Provider catalogue dimensions are not assumed to be measured millimetres.
New entries use a documented 2000 × 2000 mm default and existing Texture size
adjustment. Saved validated repeat widths/heights remain independent of PDF
paper dimensions and drawing scale.

## Validation

- npm test: 23 passed, including new provider validation/error/roundtrip tests.
- python tests/test_cad_import.py: two passed.
- JavaScript syntax and git whitespace checks passed.
- Latest main publication workflow: completed successfully at the base SHA:
  https://github.com/amaclennan1966-lab/paramount-render-studio/actions/runs/39013577910
- PR-triggered workflow lookup returned no runs for PR #1's head.
- New tests/browser_polyhaven.py covers explicit loading, mocked CORS textures,
  actual GPU rendering, save/restore, unchanged source hash/segments/scale/page
  dimensions, and native-vector PDF QA.
- Existing browser smoke suite remains intact.
- Browser execution blocked locally: Chromium download produced truncated archives,
  leaving no executable. Neither browser suite is claimed to pass on this patch.
- Added non-deploying pull-request regression workflow to run both browser suites.

## Recommendation and remaining limits

Hold merge until both browser suites pass in GitHub CI and a live Poly Haven
catalogue download/export is checked. Mocked provider tests cannot prove current
provider CORS, API availability or URL conventions. Saved remote materials need
internet access and are not an offline embedded pack.

No merge or deployment performed. Branch publication was blocked by automatic
approval review because a GitHub push was outside the explicit local-change scope.
