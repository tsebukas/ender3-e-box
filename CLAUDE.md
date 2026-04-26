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
    by `FLANGE_WIDTH` in `config.py`) that carry grooves for the
    sliding panels.
  - A CENTRE divider (`center.py`) that hangs from the Y-axis carrier
    in the middle of the box (see "Centre divider" below). Splits each
    panel into a left and a right half.
  - Two bottom-panel halves, each sliding into one side's floor-flange
    groove and one of the divider's two floor-flange grooves.
  - Two lid halves, sliding into the matching ceiling-flange grooves.
  - Two front-panel halves (host connector cutouts for whatever board
    set is installed), sliding into the front-flange grooves.
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
- Default wall thickness is `WALL_THK = 2 mm`. Integrated flanges are
  `FLANGE_THK = 4 mm` thick and `FLANGE_WIDTH = 6 mm` wide; sliding
  panels are `PANEL_THK = 2 mm` and the slot eats `GROOVE_DEPTH = 5 mm`
  into the flange end. These are tuned values - changing them ripples
  through every part. Confirm in `config.py` rather than memorising.
- The front panel and bottom panel are deliberately isolated so swapping
  an electronics board only requires reprinting those pieces, not the
  whole enclosure. Preserve this modularity when adding new boards.

## Centre divider

The Ender 3 Pro's H-frame carries a third 4040 profile on top of its
middle bar - the Y-axis carrier - sunk `Y_CARRIER_RECESS = 6.75 mm`
into the bar (see `lahteylesanne/altvaade.png` and `eestvaade.png` for
the printer-side reference). The centre divider hooks onto the carrier
the same way the side end caps hook onto the H-leg profiles, with two
arrow-shaped V-slot rails - but pointing UP from the divider's pocket
floor (`+Z`) instead of outward like the side rails (`-X`).

Geometry:
- The divider mirrors the carrier's recess into its OWN top: the top
  of the central body (the rail anchor surface) sits at
  `CENTER_HEIGHT = BOX_HEIGHT - Y_CARRIER_RECESS = 33.25 mm`. Above
  that, a `PROFILE_SIZE` x `Y_CARRIER_RECESS` carrier pocket cuts
  through the divider so the carrier sinks in flush. The divider's
  effective height stays `BOX_HEIGHT` so its lid groove lines up with
  the side end caps' lid grooves.
- Two-tier X footprint: the BOTTOM (floor flanges + central wall) keeps
  the original narrow `2 * FLANGE_WIDTH + WALL_THK` width. The TOP
  (lid + front flange halves with the pocket between them) widens to
  `CENTER_TOP_WIDTH = PROFILE_SIZE + 2 * FLANGE_WIDTH + 2 * WALL_THK`.
  The extra `WALL_THK` on each side is a vertical "side wall" that
  drops from the lid flange down to the pocket floor plate, anchoring
  the lid + front flanges so they don't cantilever in mid-air.
- The top V-slot rails extend `FLANGE_THK` forward of the box envelope
  (Y in `[-FLANGE_THK, BOX_DEPTH]`) so they sit on the lower-U front
  flange material at the front - this gives the rails a continuous
  print bed and avoids a fragile starting tip.
- The wide front flange would otherwise block the bottom-panel halves
  from sliding in. A horizontal passage cutout at the panel's Z range
  opens each U-half from its outer X end inward to the bottom groove.
- The narrow stem (floor flanges + central wall) is `CENTER_DEPTH`
  long in Y (currently 5 mm longer than `BOX_DEPTH`), so it pokes out
  the back of the box. The wide top section (pocket plate, side walls,
  lid + front flange halves) still spans only `BOX_DEPTH`. The Y tail
  at `Y in [BOX_DEPTH, CENTER_DEPTH]` sticks past the rear of the
  enclosure to anchor the divider against the Y-axis carrier's back
  end. Keep this asymmetry in mind when adding geometry: pieces tied
  to the box envelope use `BOX_DEPTH`, pieces tied to the narrow
  stem use `CENTER_DEPTH`.
- The central wall has a horizontal pass-through opening for cabling
  between the two box halves. The opening leaves `CENTER_TAIL` mm of
  solid wall at the back (Y end). Its Z extent is bounded by
  `FLANGE_THK` below (above the floor flanges) and `WALL_THK` above
  (below the pocket plate); the front end is rounded with a half-circle
  whose radius equals half the opening height, for printability.

Manifold gotcha: the central wall and the wide front flange touch only
along a single line (X = wall edge, Y = 0) unless the wall is extended
forward into the front flange's Y range. Without this extension OCCT
treats the union as non-manifold and `fillet` later fails on the inside
front-wall corners. Every Y-extending divider piece (central wall,
side walls) therefore extends to `Y = -FLANGE_THK`, sharing a 2D face
with the wide front flange. Future modifications must preserve this.

Fillet edge gotcha: only X- and Z-axis inside corners are filleted on
the divider; Y-axis edges along the central / side wall roots fail
under OCCT and are deliberately skipped. Where a horizontal inside
corner crosses the central wall (the floor's front-top corner at
Z=FLANGE_THK and the pocket plate's front-bottom corner at
Z=CENTER_HEIGHT-WALL_THK), OCCT merges the LEFT and RIGHT halves into
one continuous X-axis edge spanning across the wall - one selector
per row, NOT per half. Selectors that filter by half ranges
(_FLOOR_LEFT_FAR_X..._WALL_LEFT_X etc.) silently match nothing.
The wide ceiling row stays split into two halves because the carrier
pocket cut sits between them; that selector still uses per-half
ranges.

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

## How the part scripts relate

- `left_side.py` is the single source of truth for the side-wall
  geometry. Edit it directly.
- `right_side.py` is a PURE MIRROR of `left_side` across the YZ plane
  at `X = BOX_WIDTH / 2` (`right_side = mirror(left_side, ...)`).
  Every geometry change in `left_side.py` propagates automatically.
  Do NOT add independent geometry to `right_side.py`, and do NOT
  run it to "verify" a left-side edit - running `left_side.py` alone
  is enough. Only run `right_side.py` when the user asks about the
  right piece specifically, or when the mirroring itself was changed.
- `center.py` is the centre divider. Independent geometry (NOT a mirror
  of anything) - its body is symmetric in X around `BOX_WIDTH / 2`, so
  the LEFT and RIGHT halves are built in the same module via paired
  positions, not by mirroring a separate file.
- `panels.py` is the shared module for the six sliding panel halves
  (bottom / front / lid x left / right). It exposes three blank-panel
  factory functions (`make_bottom_blank`, `make_front_blank`,
  `make_lid_blank`) plus six module-level instances (`bottom_left`,
  `bottom_right`, ...). The blanks carry no electronics-specific
  cutouts or mounting bosses - those will be added later by per-board
  config files that import the factories and apply features. See the
  "Sliding panels" section below for the cross-section + insertion
  order constraints.
- `assembly.py` imports `left_side`, `right_side`, `center` and the
  six panel halves from `panels`, wrapping them all in a single
  `Compound`. It adds no independent geometry; each part module
  already places itself in the shared global frame.

## Sliding panels

All six panels are produced by `panels.py`. The module is the single
source of truth for panel cross-sections, insertion-order constraints
and X-extent maths.

Insertion order (mandatory - the panel sizes are tuned for it):

  1. BOTTOM slides in horizontally from the front, ends flush with the
     box's front face. Y in `[-FLANGE_THK, BOX_DEPTH]`.
  2. FRONT drops in vertically from the top and lands on top of the
     bottom panel's front edge. Z in `[(FLANGE_THK + GROOVE_SLOT)/2,
     BOX_HEIGHT - (FLANGE_THK + GROOVE_SLOT)/2]`. Stops short of both
     the floor and lid grooves so it never collides with horizontal
     panels during their insertion.
  3. LID slides in horizontally from the front, OVER the front panel,
     also flush with the box's front face. Same Y as the bottom panel.

Stepped cross-section: each panel is THICK (PANEL_THK + `_RAISE`,
where `_RAISE = (FLANGE_THK - GROOVE_SLOT)/2`) in the middle and THIN
(`PANEL_THK`) at the X edges that slide into a groove slot. The thick
body's outside face is raised toward the box's outer shell so the box
looks like one continuous surface of flanges + panel bodies, with a
`(GROOVE_SLOT - PANEL_THK)/2` recess that absorbs the slot's fit
slack. The thick body also acts as a stopper at the bottom + lid
panel's front corners (it's wider in Z than the side / centre groove
slot, so the panel can't be pushed past the front face). Bottom and
lid panels' OUTER front edge of the thick body carries an
`OUTSIDE_FILLET_R` fillet; the front panel does not.

Electronics-config files (future) import the blank factories from
`panels` and add cutouts / mounting bosses for the chosen board set.
The thin tongue X regions are reserved for the groove slot fit and
should NOT carry any cutouts or bosses - keep features in the thick
body region only.

Per-config layering (in place for SKR3, extend for further boards
as they land):

- `config_<board>.py` - one Python data module per electronics board
  (e.g. `config_skr3.py`, future `config_orange_pi_lite.py`). Holds
  the board's intrinsic facts: PCB outline, mounting-hole pattern
  (XY positions + diameter), connector positions/sizes measured from
  a board-local origin, recommended standoff height. No build123d
  code here - just dimensions and lists. Sits at the project root
  alongside the shared `config.py`. Heat-insert geometry constants
  (boss OD/height, hole dia/depth) are NOT here - they live in the
  shared `config.py` because every board mount uses the same insert.
- `panel_features.py` - shared helper module with small build123d
  helpers that operate on a panel `Part` plus parameters:
  `add_heat_insert_boss(panel, x, y, surface_z, direction)`, future
  `add_rect_cutout(panel, x, y, w, h, ...)`,
  `add_circle_cutout(panel, x, y, r, ...)`, etc. Each helper consumes
  GLOBAL-frame coordinates so the board-mount module's local-origin
  positions get translated by the caller, not by the helper.
- `boards/<board_or_board_set>.py` - one file per panel configuration
  (e.g. `boards/skr3.py`, future `boards/skr3_orangepi.py` for a
  combo). Imports the relevant blank from `panels`, the board data
  from `config_<board>.py`, and helpers from `panel_features`, then
  wires them together (place board at intended XY, walk its
  mount-hole list, walk its connector list). Exposes the resulting
  configured panels at module level so `assembly.py` can swap from
  blank to configured by changing one import line.

Why not JSON-driven config: panel features are too varied to model
cleanly as data (rectangular USB, circular fan, D-shaped power
switch, oval card slot, threaded vs pass-through bosses). Python
helper calls read close to the same as the equivalent JSON but stay
flexible. Reconsider only if a GUI-based feature editor becomes
relevant.

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
