"""
Top-level assembly of the Ender 3 Pro electronics enclosure.

Imports the individual part modules and groups them into a single
Compound. Each part already places itself in the shared global
coordinate frame (see config.py), so no extra translation is needed
here - the left side's flanges extend into +X and the right side's
flanges extend into -X, meeting at the box interior X in [0, BOX_WIDTH].
"""

from pathlib import Path

from build123d import Compound, export_step, export_stl

import config as cfg
from left_side import left_side
from right_side import right_side


left_side.label = "left_side"
right_side.label = "right_side"

assembly = Compound(label="ender3_e_box", children=[left_side, right_side])


# ---------------------------------------------------------------------------
# Export + preview (only when run directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if cfg.EXPORT_STEP or cfg.EXPORT_STL:
        out_dir = Path(__file__).parent / "build"
        out_dir.mkdir(exist_ok=True)

        if cfg.EXPORT_STEP:
            step_path = out_dir / "assembly.step"
            export_step(assembly, str(step_path))
            print(f"assembly STEP -> {step_path}")

        if cfg.EXPORT_STL:
            stl_path = out_dir / "assembly.stl"
            export_stl(assembly, str(stl_path))
            print(f"assembly STL  -> {stl_path}")

    bb = assembly.bounding_box()
    print(f"bounding box min = {tuple(round(v, 2) for v in tuple(bb.min))}")
    print(f"bounding box max = {tuple(round(v, 2) for v in tuple(bb.max))}")

    if cfg.SHOW_IN_VIEWER:
        try:
            from ocp_vscode import show
        except ImportError:
            print("ocp_vscode not available - skipping show()")
        else:
            show(left_side, right_side, names=["left_side", "right_side"])
