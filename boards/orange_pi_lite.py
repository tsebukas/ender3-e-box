"""
Bottom panel (right half) configured for the Orange Pi Lite SBC.

Imports a blank from `panels`, board geometry from
`config_orange_pi_lite`, and applies heat-insert bosses for the four
PCB mount holes via `panel_features`.

Board placement (Orange Pi Lite on the RIGHT bottom panel):

    Local-origin global position : (BOARD_X, BOARD_Y)
    Local +X axis                : along global +X  (longer side, 69 mm)
    Local +Y axis                : along global +Y  (shorter side, 48 mm)

I.e. the PCB's long side runs along the printer width and its short
side runs along the printer depth, with the bottom-left PCB corner
sitting BOARD_X mm from the box's left wall and BOARD_Y mm from the
front wall.
"""

import sys
from pathlib import Path

# Allow direct script run (`py boards/orange_pi_lite.py`) from any cwd
# by adding the project root to sys.path.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import config_orange_pi_lite as opl
import panels
from panel_features import add_heat_insert_boss


# --- Board placement -----------------------------------------------------
BOARD_X = 165.0   # global X of the board's local origin (160 mm from left wall)
BOARD_Y =  20.0   # global Y of the board's local origin ( 20 mm from front wall)


def make_bottom_right_orange_pi_lite():
    """Bottom-right panel blank with Orange Pi Lite mount-hole bosses applied."""
    panel = panels.make_bottom_blank("right")
    for hx, hy in opl.MOUNT_HOLES:
        panel = add_heat_insert_boss(
            panel,
            x=BOARD_X + hx,
            y=BOARD_Y + hy,
            surface_z=panels.BOTTOM_INNER_Z,
            direction=+1,
        )
    return panel


bottom_right_orange_pi_lite = make_bottom_right_orange_pi_lite()


# ---------------------------------------------------------------------------
# Direct-run preview
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from preview import preview
    preview({"bottom_right_orange_pi_lite": bottom_right_orange_pi_lite})
