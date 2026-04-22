"""
Right side panel of the Ender 3 Pro electronics enclosure.

Mirror of left_side across the YZ plane at X = BOX_WIDTH / 2, so every
geometry change in left_side.py propagates here automatically. Do not
add independent geometry here - edit left_side.py instead. After
mirroring, the wall sits at X in [BOX_WIDTH, BOX_WIDTH + WALL_THK] and
the three flanges extend into the box in the -X direction.

Global axes (from config.py): +X printer width, +Y depth, +Z up.
"""

from pathlib import Path

from build123d import (
    Plane,
    export_step,
    export_stl,
    mirror,
)

import config as cfg
from left_side import left_side


right_side = mirror(left_side, Plane.YZ.offset(cfg.BOX_WIDTH / 2))


# ---------------------------------------------------------------------------
# Export + preview (only when run directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if cfg.EXPORT_STEP or cfg.EXPORT_STL:
        out_dir = Path(__file__).parent / "build"
        out_dir.mkdir(exist_ok=True)

        if cfg.EXPORT_STEP:
            step_path = out_dir / "right_side.step"
            export_step(right_side, str(step_path))
            print(f"right_side STEP -> {step_path}")

        if cfg.EXPORT_STL:
            stl_path = out_dir / "right_side.stl"
            export_stl(right_side, str(stl_path))
            print(f"right_side STL  -> {stl_path}")

    bb = right_side.bounding_box()
    print(f"bounding box min = {tuple(round(v, 2) for v in tuple(bb.min))}")
    print(f"bounding box max = {tuple(round(v, 2) for v in tuple(bb.max))}")
    print(f"volume           = {right_side.volume:.1f} mm^3")

    if cfg.SHOW_IN_VIEWER:
        try:
            from ocp_vscode import show
        except ImportError:
            print("ocp_vscode not available - skipping show()")
        else:
            show(right_side, names=["right_side"])
