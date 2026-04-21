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
  - `BOX_DEPTH  = 125` mm along Y (horizontal depth)
  - `BOX_HEIGHT =  40` mm along Z (vertical; matches the 4040 profile
    cross-section so the enclosure sits flush with the frame).
- Every part module uses the same global coordinate frame
  (+X printer-width, +Y depth, +Z up). Do not invent part-local frames.
- Printer build volume limits a single part to ~220 mm, so the enclosure
  MUST be split. The chosen split:
  - Two mirrored side pieces (left and right END CAPS of the box),
    each with integrated 40 mm wide floor, ceiling and front flanges
    that carry grooves for the sliding panels.
  - A separate bottom panel that slides into the floor-flange grooves.
  - A separate lid that slides into the ceiling-flange grooves.
  - A separate front panel (holds connector cutouts for whatever board
    set is installed) that slides into the front-flange grooves.
- Sides attach to the printer frame via a T-shaped rail on the outer
  face of each side wall. The rail profile is derived from
  `lahteylesanne/4040_v-slot.jpg` (10 mm slot opening, 6.77 mm neck,
  1.80 mm lip, 4.30 mm total depth, 11 mm inner chamber). The rail runs
  along Y; the box slides into the profile from one Y-end. The wall's
  outer face is positioned flush with the 4040 profile outer face.
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
    1. write STEP and STL exports into a local `build/` directory, and
    2. call `ocp_vscode.show(part, names=[...])` so the part renders in
       the OCP CAD Viewer (wrap the import in try/except so the script
       still runs headless).

## Repository layout convention

- `lahteylesanne/` - original brief and reference drawings (read-only
  source of truth for requirements).
- Part files and the assembly script live at the project root (or a
  future `src/` folder) once created.

## Working with build123d

- Prefer build123d's modern builder API (`BuildPart`, `BuildSketch`,
  `BuildLine`) over the older cadquery-style fluent chain.
- Export STEP for assembly review and STL for slicing; keep exports out
  of version control unless explicitly requested.
- When you need up-to-date build123d API details, consult the context7
  MCP server rather than guessing - the library evolves quickly.
