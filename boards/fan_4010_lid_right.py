"""
Right lid panel configured for a 40 x 40 mm (4010) axial fan.

Fan centre in the global frame:
    X = 180 mm from left wall
    Y = 60 mm from front face

Mount holes: two M3 through-holes at diagonally opposite corners of the
40 x 40 fan square, 4 mm inset from each edge.  Cylindrical counterbores
(6 mm dia, 1 mm deep) on the outer (top) face let the screw head sit flush.

Fan opening: 38 mm OD / 20 mm ID donut with + spokes (spoke width 5 mm),
giving ~77 % open area of the annular region.
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import panels
from panel_features import add_fan_grille_lid


# Fan centre (global frame)
FAN_CX = 197.5   # mm from left wall (X = 0)
FAN_CY = 80.0    # mm from front face (Y = 0)

_FAN_HALF   = 40.0 / 2   # 20 mm half-side of the 40 x 40 fan square
_HOLE_INSET = 4.0        # mount holes are 4 mm from each fan edge

# Left-front and right-back diagonal corners carry the two mount holes.
_HOLE_POSITIONS = [
    (FAN_CX - _FAN_HALF + _HOLE_INSET, FAN_CY - _FAN_HALF + _HOLE_INSET),
    (FAN_CX + _FAN_HALF - _HOLE_INSET, FAN_CY + _FAN_HALF - _HOLE_INSET),
]


def make_lid_right_fan() -> object:
    """Right lid blank with 4010 fan grille and mount holes applied."""
    panel = panels.make_lid_blank("right")
    return add_fan_grille_lid(
        panel,
        fan_cx=FAN_CX,
        fan_cy=FAN_CY,
        hole_positions=_HOLE_POSITIONS,
    )


lid_right_fan = make_lid_right_fan()


if __name__ == "__main__":
    from preview import preview
    preview({"lid_right_fan": lid_right_fan})
