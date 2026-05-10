"""
Top-level assembly of the Ender 3 Pro electronics enclosure.

Imports the individual part modules and groups them into a single
Compound. Each part already places itself in the shared global
coordinate frame (see config.py), so no extra translation is needed
here - the left side's flanges extend into +X and the right side's
flanges extend into -X, meeting at the box interior X in [0, BOX_WIDTH].
"""

from build123d import Compound

from left_side import left_side
from right_side import right_side
from center import center
from panels import (
    front_left,
    lid_left
)
from boards.fan_4010_lid_right_recessed import lid_right_fan_recessed
from boards.oled_display import front_right_oled
from boards.skr3 import bottom_left_skr3
from boards.orange_pi_lite import bottom_right_orange_pi_lite


left_side.label = "left_side"
right_side.label = "right_side"
center.label = "center"
bottom_left_skr3.label             = "bottom_left (SKR3)"
bottom_right_orange_pi_lite.label  = "bottom_right (Orange Pi Lite)"
front_left.label   = "front_left"
front_right_oled.label = "front_right (oled)"
lid_left.label     = "lid_left"
lid_right_fan_recessed.label    = "lid_right (fan)"

assembly = Compound(label="ender3_e_box",
                    children=[left_side, right_side, center,
                              bottom_left_skr3, bottom_right_orange_pi_lite,
                              front_left, front_right_oled,
                              lid_left, lid_right_fan_recessed])


# ---------------------------------------------------------------------------
# Export + preview (only when run directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from preview import preview
    preview({"assembly": assembly})
