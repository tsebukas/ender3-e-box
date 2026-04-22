# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

3D-printable electronics enclosure for an Ender 3 Pro 3D printer. The box
houses control electronics (initial target: Orange Pi Lite SBC + BTT SKR 3
mainboard) and mounts to the front of the printer's 4040 V-slot H-frame.
Full brief (in Estonian) is in `lahteylesanne/lahteylesanne.md`.

## Key design constraints

- Enclosure outer envelope (fixed, shared via `config.py`):
  - `BOX_WIDTH  = 250` mm along X (horizontal, along printer width)
  - `BOX_DEPTH  = 120` mm along Y (horizontal depth)
  - `BOX_HEIGHT =  40` mm along Z (vertical; matches the 4040 profile
    cross-section so the enclosure sits flush with the frame).
- Every part module uses the same global coordinate frame
  (+X printer-width, +Y depth, +Z up). Do not invent part-local frames.
- Printer build volume limits a single part to ~220 mm, so the enclosure
  MUST be split. The chosen split:
  - Two mirrored side pieces (left and right END CAPS of the box),
    each with integrated floor, ceiling and front flanges (width set
    by `FLANGE_WIDTH` in `config.py`, currently 20 mm) that carry
    grooves for the sliding panels.
  - A separate bottom panel that slides into the floor-flange grooves.
  - A separate lid that slides into the ceiling-flange grooves.
  - A separate front panel (holds connector cutouts for whatever board
    set is installed) that slides into the front-flange grooves.
- Sides attach to the printer frame via TWO T-shape rails on the outer
  face of each side wall. The rail profile is derived from
  `lahteylesanne/4040_v-slot.jpg`, which shows a 4040 profile (40 x 40
  mm) whose face carries TWO V-slots: a narrow neck opens into a wider
  inner chamber that tapers to a flat back wall. Exact dimensions live
  in `config.py` under the `VSLOT_*` constants (neck width/depth,
  chamber width/back width/flat depth, pocket depth, slot spacing and
  fit clearance). Both rails run along Y for the full box depth; the
  box slides into the profile from one Y-end. The wall's outer face
  sits flush with the profile face.
- Default wall thickness is 2 mm. Integrated flanges are 5 mm thick
  (thicker than the wall so they can host a 5 mm deep groove).
- The front panel and bottom panel are deliberately isolated so swapping
  an electronics board only requires reprinting those pieces, not the
  whole enclosure. Preserve this modularity when adding new boards.

## Toolchain

- CAD is authored in Python using
  [build123d](https://github.com/gumyr/build123d). Add supporting
  packages only when build123d itself does not cover the need.
- One Python file per physical part (left side, right side, bottom,
  front panel, lid, etc.). Whether to factor shared geometry into helper
  modules is a judgement call per case.
- A top-level assembly script imports the individual part modules and
  composes the full enclosure for preview / export.
- All shared dimensions, tolerances and material parameters live in
  `config.py` at the project root. Every part module imports from there
  (`import config as cfg`) instead of hard-coding numbers locally.
- Each part module's `if __name__ == "__main__":` block must:
    1. write STEP and STL exports into a local `build/` directory,
       each gated on `cfg.EXPORT_STEP` and `cfg.EXPORT_STL`, and
    2. call `ocp_vscode.show(part, names=[...])` so the part renders in
       the OCP CAD Viewer, gated on `cfg.SHOW_IN_VIEWER` (wrap the
       `from ocp_vscode import show` import in try/except so the script
       still runs headless when the viewer package is missing).
  Do not hard-code "always export" / "always show" - respect the flags
  so batch/CI runs can turn any of them off without editing every part.

## Repository layout convention

- `lahteylesanne/` - original brief and reference drawings (read-only
  source of truth for requirements).
- Part files and the assembly script live at the project root (or a
  future `src/` folder) once created.

## Working with build123d

- Build parts with the context-manager builder API: wrap the whole part
  in `with BuildPart() as name:` and add primitives or subtract cutters
  inside. Non-rectangular features (V-slot rails, any contoured
  profile) are built as a `BuildSketch` + `extrude`, not assembled from
  primitive booleans. Avoid the algebraic `(a + b) - c` style for
  anything but quick throwaway experiments.
- Note the plane-normal direction when extruding: `Plane.XZ` has its
  normal pointing in `-Y`, so extruding to +Y needs a negative amount
  (or a custom plane). Comment the sign when it matters.
- Export STEP for assembly review and STL for slicing; keep exports out
  of version control unless explicitly requested.
- When you need up-to-date build123d API details, consult the context7
  MCP server rather than guessing - the library evolves quickly.
