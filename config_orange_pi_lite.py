"""
Orange Pi Lite SBC intrinsic data.

All dimensions in mm. Mount-hole positions are given in the BOARD-LOCAL
frame whose axes match how the board sits in the global frame for its
intended placement (right bottom panel of the e-box):

    +X along the LONGER side  (69 mm, runs along global +X)
    +Y along the SHORTER side (48 mm, runs along global +Y)

Origin is the board corner with the smallest X / Y. The board-mount
module under boards/ decides where to drop the local origin in the
global frame.
"""

# --- PCB outline ---------------------------------------------------------
SIZE_X = 69.0   # longer side  (along global +X for this board's placement)
SIZE_Y = 48.0   # shorter side (along global +Y)


# --- Mount-hole pattern --------------------------------------------------
# Four corner holes, inset 3 mm from every PCB edge.
_INSET = 3.0

MOUNT_HOLES = [
    (_INSET,           _INSET),            # near-left
    (SIZE_X - _INSET,  _INSET),            # near-right
    (_INSET,           SIZE_Y - _INSET),   # far-left
    (SIZE_X - _INSET,  SIZE_Y - _INSET),   # far-right
]
