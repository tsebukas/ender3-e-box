"""
BTT SKR3 mainboard intrinsic data.

All dimensions in mm. Mount-hole positions are given in the BOARD-LOCAL
frame: origin at the board corner with smallest X / Y, +X along the
SHORTER side (84.3 mm), +Y along the LONGER side (109.67 mm). The
board-mount module under boards/ decides where to drop the local
origin in the global frame and whether to rotate.
"""

# --- PCB outline ---------------------------------------------------------
SIZE_X = 84.3     # shorter side
SIZE_Y = 109.67   # longer side


# --- Mount-hole pattern --------------------------------------------------
# Four corner holes. Hole centre insets (measured from the PCB edge to
# the hole centre):
#   X-inset (from each long Y-aligned edge)  = 4.00 mm
#   Y-inset (from each short X-aligned edge) = 3.91 mm
_X_INSET = 4.0
_Y_INSET = 3.91

MOUNT_HOLES = [
    (_X_INSET,           _Y_INSET),            # near-left
    (SIZE_X - _X_INSET,  _Y_INSET),            # near-right
    (_X_INSET,           SIZE_Y - _Y_INSET),   # far-left
    (SIZE_X - _X_INSET,  SIZE_Y - _Y_INSET),   # far-right
]
