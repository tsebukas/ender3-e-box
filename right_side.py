"""
Right side panel of the Ender 3 Pro electronics enclosure.

Mirror of left_side across the YZ plane at X = BOX_WIDTH / 2, so every
geometry change in left_side.py propagates here automatically. Do not
add independent geometry here - edit left_side.py instead. After
mirroring, the wall sits at X in [BOX_WIDTH, BOX_WIDTH + WALL_THK] and
the three flanges extend into the box in the -X direction.

Global axes (from config.py): +X printer width, +Y depth, +Z up.
"""

from build123d import (
    Plane,
    mirror,
)

import config as cfg
from left_side import left_side


right_side = mirror(left_side, Plane.YZ.offset(cfg.BOX_WIDTH / 2))


# ---------------------------------------------------------------------------
# Export + preview (only when run directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from preview import preview
    preview({"right_side": right_side})
