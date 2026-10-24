# Paramount 3D — phase 1 prototype

Open `/3d/` on the existing GitHub Pages deployment (once this branch is merged) or serve repository locally with `python -m http.server 8080`.

This first prototype displays GLB files and downloads a preliminary geometry report including SHA-256, bounding box, mesh/triangle counts, and material names.

## Important limits
- Original SketchUp .skp is never touched, uploaded or overwritten; the user must export a **separate GLB copy**.
- This version does **not** automatically import .skp, apply materials or create final photorealistic renders.
- Do not interpret GLB's geometry dimensions as independently verified. Manually compare bounding dimensions and representative openings with SketchUp.
- Processing is client-only; Three.js is loaded from an external CDN.
- Never merge into main without browser tests and a real SketchUp 2025 reference model.

## Next stages
1. SKP 2025 export adapter, preserving component instances and units.
2. Source-to-GLB geometry checks (openings, sizes, origins and roofs).
3. Non-destructive material mapping and Blender Cycles automated image generation.
4. Optional user-controlled connection to ChatGPT.
