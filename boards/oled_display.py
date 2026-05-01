"""
Right front panel configured for a 0.91-inch OLED display (39 x 13 mm PCB,
short side along Z).

The display PCB lower-left corner is placed at (DISPLAY_X, DISPLAY_Z) in the
global frame.  A 2 mm-deep rectangular recess on the panel's inner face seats
the PCB body.  A 26 x 6 mm through-hole opens the view window to the front
face; the window sits WINDOW_FROM_RIGHT mm from the display's right edge and
WINDOW_FROM_TOP mm from its top edge.

Global coordinate frame: +X printer width, +Y depth, +Z up.
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from build123d import export_step, export_stl

import config as cfg
import panels
from panel_features import (
    add_rect_cutout_front_panel,
    add_rect_recess_front_panel,
)


# --- Display placement -------------------------------------------------------
DISPLAY_X = 200.0   # global X of PCB lower-left corner (from left wall)
DISPLAY_Z  =  20.0  # global Z of PCB lower-left corner (from box bottom)

DISPLAY_W = 39.0    # PCB X extent
DISPLAY_H = 13.0    # PCB Z extent
RECESS_DEPTH = 2.0  # depth of PCB seat pocket from inner face

# View window position measured from display edges.
WINDOW_W          = 23.0
WINDOW_H          =  6.0
WINDOW_FROM_RIGHT =  8.5   # distance from display right edge to window right edge
WINDOW_FROM_TOP   =  2.6   # distance from display top edge to window top edge


def make_front_right_oled() -> panels.Part:
    """Right front panel blank with OLED recess and view-window cutout."""
    panel = panels.make_front_blank("right")

    display_cx = DISPLAY_X + DISPLAY_W / 2
    display_cz = DISPLAY_Z + DISPLAY_H / 2
    panel = add_rect_recess_front_panel(
        panel,
        x_center=display_cx,
        z_center=display_cz,
        width=DISPLAY_W,
        height=DISPLAY_H,
        depth=RECESS_DEPTH,
    )

    window_cx = (DISPLAY_X + DISPLAY_W - WINDOW_FROM_RIGHT) - WINDOW_W / 2
    window_cz = (DISPLAY_Z + DISPLAY_H - WINDOW_FROM_TOP)   - WINDOW_H / 2
    panel = add_rect_cutout_front_panel(
        panel,
        x_center=window_cx,
        z_center=window_cz,
        width=WINDOW_W,
        height=WINDOW_H,
    )

    return panel


front_right_oled = make_front_right_oled()


# ---------------------------------------------------------------------------
# Direct-run preview
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parts = {"front_right_oled": front_right_oled}

    if cfg.EXPORT_STEP or cfg.EXPORT_STL:
        out_dir = Path(__file__).parent.parent / "build"
        out_dir.mkdir(exist_ok=True)
        for name, part in parts.items():
            if cfg.EXPORT_STEP:
                step_path = out_dir / f"{name}.step"
                export_step(part, str(step_path))
                print(f"{name} STEP -> {step_path}")
            if cfg.EXPORT_STL:
                stl_path = out_dir / f"{name}.stl"
                export_stl(part, str(stl_path))
                print(f"{name} STL  -> {stl_path}")

    for name, part in parts.items():
        bb = part.bounding_box()
        bb_min = tuple(round(v, 2) for v in tuple(bb.min))
        bb_max = tuple(round(v, 2) for v in tuple(bb.max))
        print(f"{name:25s}  bb={bb_min}->{bb_max}  vol={part.volume:.1f}")

    if cfg.SHOW_IN_VIEWER:
        try:
            from ocp_vscode import show
        except ImportError:
            print("ocp_vscode not available - skipping show()")
        else:
            show(*parts.values(), names=list(parts.keys()))
