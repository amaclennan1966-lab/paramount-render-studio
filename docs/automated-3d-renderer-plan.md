# Paramount Automated 3D Renderer — Initial Technical Plan

Status: feasibility/prototype; no rendering functionality implemented yet.

## Objective
Produce photorealistic architectural images from SketchUp 2025 source models without modifying original SKP files or altering architectural geometry.

## Architecture
1. Accept original SKP with SHA-256 fingerprint; store read-only.
2. Convert to neutral GLB via a tested OpenSKP importer or a SketchUp-side exporter. Compare bounds, transforms, instance counts and selected reference measurements against the source. Fail closed on discrepancies.
3. Maintain a separate rendering scene with material overrides, HDRI lighting, cameras and optional contextual landscaping.
4. Use Blender Cycles in headless mode for final GPU rendering; evaluate BlenderProc for orchestration. Optionally display a Three.js GLB preview in the existing browser app.
5. Return images plus QA manifest recording original file fingerprint, conversion method, scene transforms, material overrides and warnings.

## Architectural invariants
- Do not write to or overwrite original SKP.
- Do not apply shape-changing modifiers, displacement or AI image reconstruction to building elements.
- Preserve roof pitches, wall positions, openings, dimensions, components and glazing subdivisions.
- Use conservative defaults: unknown surfaces require review; missing material mappings must not invent geometry.
- Context objects are separate from the building model.
- A render is not dimensionally certified until import QA passes.

## Phase 1 acceptance test
- Select a real (non-sensitive) SketchUp 2025 test model.
- Validate import, dimensions, bounding boxes, component instances, and opening positions.
- Render fixed camera with automatic sun and a small PBR material catalogue.
- Produce a before/after comparison and QA JSON.
- Never change existing 2D PDF/DXF workflows.

## External libraries to evaluate
- https://github.com/DLR-RM/BlenderProc (GPL-3.0; assess distribution obligations)
- https://github.com/iamahsanmehmood/openskp (verify SKP 2025 and conversion fidelity)
- https://github.com/gkjohnson/three-gpu-pathtracer (browser preview)
- https://github.com/bardia-ardakanian/blender-headless-render (headless rendering scripts)

Do not vendor or merge external source before reviewing licences and tests.
