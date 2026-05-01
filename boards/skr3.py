"""
Bottom panel (left half) configured for the BTT SKR3 mainboard.

Imports a blank from `panels`, board geometry from `config_skr3`, and
applies heat-insert bosses for the four PCB mount holes via
`panel_features`. Future additions (front-panel connector cutouts,
mounts for a second board, ...) extend this file or sit alongside it
as `boards/<board_set>.py`.

Board placement (BTT SKR3 on the LEFT bottom panel):

    Local-origin global position : (BOARD_X, BOARD_Y)
    Local +X axis                : along global +X  (shorter side)
    Local +Y axis                : along global +Y  (longer side)

I.e. the PCB's short side runs along the printer width and its long
side runs along the printer depth, with the bottom-left PCB corner
sitting BOARD_X mm from the box's left wall and BOARD_Y mm from the
front wall.
"""

import sys
from pathlib import Path

# Allow direct script run (`py boards/skr3.py`) from any cwd by adding
# the project root to sys.path so the root-level modules import.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import config_skr3 as skr3
import panels
from panel_features import add_heat_insert_boss


# --- Board placement -----------------------------------------------------
BOARD_X = 9.0   # global X of the board's local origin (its near-left corner)
BOARD_Y = 9.0   # global Y of the board's local origin


def make_bottom_left_skr3():
    """Bottom-left panel blank with SKR3 mount-hole bosses applied."""
    panel = panels.make_bottom_blank("left")
    for hx, hy in skr3.MOUNT_HOLES:
        panel = add_heat_insert_boss(
            panel,
            x=BOARD_X + hx,
            y=BOARD_Y + hy,
            surface_z=panels.BOTTOM_INNER_Z,
            direction=+1,
        )
    return panel


bottom_left_skr3 = make_bottom_left_skr3()


# ---------------------------------------------------------------------------
# Direct-run preview
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from preview import preview
    preview({"bottom_left_skr3": bottom_left_skr3})
