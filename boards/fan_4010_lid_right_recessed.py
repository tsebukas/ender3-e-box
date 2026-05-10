"""
Right lid panel configured for a 40 x 40 x 11 mm (4010) axial fan,
RECESSED UP into a bump on top of the lid.

Same fan position, same mount-hole pattern, same grille pattern as
fan_4010_lid_right.py - but the fan body sits ABOVE the lid plate
(inside a hollow square bump), with its bottom face flush with the
lid's inner face. Nothing hangs below the lid, so the lid can be
slid horizontally into its grooves with the front panel already
installed.

Fan centre in the global frame:
    X = 197.5 mm from left wall
    Y = 80.0 mm from front face

Mount holes: two M3 through-holes at diagonally opposite corners of
the 40 x 40 fan square, 4 mm inset from each edge. Cylindrical
counterbores (6 mm dia, 1 mm deep) on the bump roof's TOP face let
the screw heads sit flush.

Bump dimensions (above lid top face):
    cavity 40.3 x 40.3, walls 2 mm, roof 2 mm,
    cavity height 11.3 mm (fan height + 0.3 mm vertical clearance).
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import panels
from panel_features import add_fan_grille_lid_recessed


# Fan centre (global frame)
FAN_CX = 197.5   # mm from left wall (X = 0)
FAN_CY = 80.0    # mm from front face (Y = 0)

# Fan body dimensions
FAN_SIZE   = 40.0
FAN_HEIGHT = 11.0

_FAN_HALF   = FAN_SIZE / 2
_HOLE_INSET = 4.0   # mount holes are 4 mm from each fan edge

# Left-front and right-back diagonal corners carry the two mount holes.
_HOLE_POSITIONS = [
    (FAN_CX - _FAN_HALF + _HOLE_INSET, FAN_CY - _FAN_HALF + _HOLE_INSET),
    (FAN_CX + _FAN_HALF - _HOLE_INSET, FAN_CY + _FAN_HALF - _HOLE_INSET),
]


def make_lid_right_fan_recessed() -> object:
    """Right lid blank with recessed 4010 fan bump and grille applied."""
    panel = panels.make_lid_blank("right")
    return add_fan_grille_lid_recessed(
        panel,
        fan_cx=FAN_CX,
        fan_cy=FAN_CY,
        hole_positions=_HOLE_POSITIONS,
        fan_size=FAN_SIZE,
        fan_height=FAN_HEIGHT,
    )


lid_right_fan_recessed = make_lid_right_fan_recessed()


if __name__ == "__main__":
    from preview import preview
    preview({"lid_right_fan_recessed": lid_right_fan_recessed})
