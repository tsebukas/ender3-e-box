# Ender 3 Pro Electronics Enclosure

A 3D-printable electronics box for the Ender 3 Pro. It mounts to the
front-facing side of the 4040 V-slot H-frame legs, houses the control
electronics (BTT SKR3 mainboard + Orange Pi Lite SBC), and slides onto
the frame without tools.

Outer envelope: 250 mm wide x 120 mm deep x 40 mm tall (matches the
4040 profile cross-section so the box sits flush with the frame).

## Parts

The enclosure splits into pieces that each fit on an Ender 3 build plate
(220 mm limit):

| File | Part | Count |
|---|---|---|
| `left_side.py` | Left end cap - side wall, floor/ceiling/front flanges, two T-rails | 1 |
| `right_side.py` | Right end cap - pure mirror of left | 1 |
| `center.py` | Centre divider - hooks onto the Y-axis carrier profile | 1 |
| `panels.py` | Blank bottom / front / lid panel halves | 6 |
| `boards/skr3.py` | Left bottom panel with SKR3 mount-hole bosses | 1 |
| `boards/orange_pi_lite.py` | Right bottom panel with Orange Pi Lite bosses | 1 |

The six sliding panels insert in order: bottom first (slides in from the
front), front next (drops in from the top), lid last (slides in over the
front panel).

## Prerequisites

- Python 3.11 or newer (on Windows, use `py` to invoke the launcher)
- [build123d](https://github.com/gumyr/build123d)
- [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) VS Code extension (optional, for live preview)

Install build123d:

```
pip install build123d
```

## Previewing a part

Run any part module directly. By default `SHOW_IN_VIEWER = True` in
`config.py`, so the part opens in the OCP CAD Viewer panel inside VS Code:

```
py left_side.py
py center.py
py panels.py
py boards/skr3.py
py boards/orange_pi_lite.py
py assembly.py
```

`assembly.py` builds and previews the complete enclosure with all parts
in place.

## Exporting STL / STEP

Open `config.py` and flip the relevant flags before running:

```python
EXPORT_STEP = True   # writes build/<part>.step
EXPORT_STL  = True   # writes build/<part>.stl
```

Output files land in the `build/` directory (created automatically).

## Adding a new electronics board

1. Create `config_<board>.py` at the project root with the PCB outline,
   mount-hole XY positions, and connector positions measured from the
   board's own origin.

2. Create `boards/<board>.py`. Import the relevant blank from `panels`,
   the board data from step 1, and `add_heat_insert_boss` from
   `panel_features`. Walk the mount-hole list and call the helper for
   each hole. Expose the finished panel at module level.

3. Import the new panel in `assembly.py` and add it to the `Compound`
   children list in place of (or alongside) the existing board panels.

Keep connector cutouts and boss features inside the thick body region of
the panel only - the thin tongue edges that slide into the grooves must
remain unmodified.

## Repository layout

```
config.py              - all shared dimensions and output flags
config_skr3.py         - BTT SKR3 board geometry
config_orange_pi_lite.py - Orange Pi Lite board geometry
left_side.py           - left end cap
right_side.py          - right end cap (mirrors left_side)
center.py              - centre divider
panels.py              - blank panel factory functions and instances
panel_features.py      - build123d helpers (heat-insert bosses, cutouts)
boards/
    skr3.py            - left bottom panel for SKR3
    orange_pi_lite.py  - right bottom panel for Orange Pi Lite
assembly.py            - full enclosure preview / export
build/                 - generated STEP and STL files (not committed)
lahteylesanne/         - original design brief and reference drawings
```

## Design notes

- All dimensions come from `config.py`. Do not hard-code numbers in part
  files.
- The global coordinate frame is +X along printer width, +Y along depth,
  +Z up. Every part uses this frame directly.
- The right end cap is a pure mirror of the left - editing `left_side.py`
  is sufficient for geometry changes to both sides.
- The centre divider hooks onto the Y-axis carrier (a 4040 profile on top
  of the H-frame middle bar) using two upward-pointing V-slot rails, the
  same profile geometry the side end caps use for their outward-pointing
  side rails.
