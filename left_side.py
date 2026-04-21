"""
Left side panel of the Ender 3 Pro electronics enclosure.

This is the left END CAP of the box. The wall sits at X in [-WALL_THK, 0]
and spans Y in [0, BOX_DEPTH], Z in [0, BOX_HEIGHT]. Three integrated
flanges (floor, ceiling, front) extend into the box in the +X direction,
each carrying a 5 mm deep slide-in groove for its own separately printed
panel (bottom, lid, front panel).

The outer (-X) face of the wall carries TWO T-shape rails that engage
the two V-slots of the printer's 40-series frame profile. The rails run
the full Y depth, so the box slides into the profile from one Y-end.

Global axes (from config.py): +X printer width, +Y depth, +Z up.
"""

from pathlib import Path

from build123d import (
    BuildPart,
    BuildSketch,
    Box,
    Locations,
    Mode,
    Plane,
    Rectangle,
    export_step,
    export_stl,
    extrude,
)

import config as cfg


# ---------------------------------------------------------------------------
# Derived geometry for the V-slot engaging rails
# ---------------------------------------------------------------------------
# T cross-section, drawn on Plane.XZ (local x = global X, local y = global Z):
#
#     |<--- foot ----->|<-- tongue -->|
#     +----------------+              |
#     |                |              |  wider foot sits inside the
#     |                +--------------+  11 mm chamber, narrower tongue
#     |                |              |  slides through the 6.77 mm neck
#     |                +--------------+
#     +----------------+              |
#                             wall outer face (X = -WALL_THK)

_RAIL_NECK_W = cfg.VSLOT_NECK_WIDTH - cfg.RAIL_CLEARANCE     # Z extent
_RAIL_NECK_D = cfg.VSLOT_NECK_DEPTH                          # X extent
_RAIL_FOOT_W = cfg.VSLOT_INNER_WIDTH - cfg.RAIL_CLEARANCE    # Z extent
_RAIL_FOOT_D = cfg.VSLOT_INNER_DEPTH - cfg.VSLOT_NECK_DEPTH  # X extent

_WALL_OUTER_X = -cfg.WALL_THK

_TONGUE_CX = _WALL_OUTER_X - _RAIL_NECK_D / 2
_FOOT_CX   = _WALL_OUTER_X - _RAIL_NECK_D - _RAIL_FOOT_D / 2

_RAIL_Z_LO = cfg.BOX_HEIGHT / 2 - cfg.RAIL_SPACING / 2
_RAIL_Z_HI = cfg.BOX_HEIGHT / 2 + cfg.RAIL_SPACING / 2


# ---------------------------------------------------------------------------
# Build the part
# ---------------------------------------------------------------------------

with BuildPart() as left_side_builder:

    # --- Side wall -----------------------------------------------------
    # X in [-WALL_THK, 0], Y in [0, BOX_DEPTH], Z in [0, BOX_HEIGHT]
    with Locations((-cfg.WALL_THK / 2,
                    cfg.BOX_DEPTH / 2,
                    cfg.BOX_HEIGHT / 2)):
        Box(cfg.WALL_THK, cfg.BOX_DEPTH, cfg.BOX_HEIGHT)

    # --- Floor flange + bottom-panel groove ----------------------------
    with Locations((cfg.FLANGE_WIDTH / 2,
                    cfg.BOX_DEPTH / 2,
                    cfg.FLANGE_THK / 2)):
        Box(cfg.FLANGE_WIDTH, cfg.BOX_DEPTH, cfg.FLANGE_THK)

    _groove_cx = cfg.FLANGE_WIDTH - cfg.GROOVE_DEPTH / 2 + cfg.EPS / 2
    with Locations((_groove_cx,
                    cfg.BOX_DEPTH / 2,
                    cfg.FLANGE_THK / 2)):
        Box(cfg.GROOVE_DEPTH + cfg.EPS,
            cfg.BOX_DEPTH + 2 * cfg.EPS,
            cfg.GROOVE_SLOT,
            mode=Mode.SUBTRACT)

    # --- Ceiling flange + lid groove -----------------------------------
    with Locations((cfg.FLANGE_WIDTH / 2,
                    cfg.BOX_DEPTH / 2,
                    cfg.BOX_HEIGHT - cfg.FLANGE_THK / 2)):
        Box(cfg.FLANGE_WIDTH, cfg.BOX_DEPTH, cfg.FLANGE_THK)

    with Locations((_groove_cx,
                    cfg.BOX_DEPTH / 2,
                    cfg.BOX_HEIGHT - cfg.FLANGE_THK / 2)):
        Box(cfg.GROOVE_DEPTH + cfg.EPS,
            cfg.BOX_DEPTH + 2 * cfg.EPS,
            cfg.GROOVE_SLOT,
            mode=Mode.SUBTRACT)

    # --- Front flange + front-panel groove -----------------------------
    with Locations((cfg.FLANGE_WIDTH / 2,
                    cfg.FLANGE_THK / 2,
                    cfg.BOX_HEIGHT / 2)):
        Box(cfg.FLANGE_WIDTH, cfg.FLANGE_THK, cfg.BOX_HEIGHT)

    with Locations((_groove_cx,
                    cfg.FLANGE_THK / 2,
                    cfg.BOX_HEIGHT / 2)):
        Box(cfg.GROOVE_DEPTH + cfg.EPS,
            cfg.GROOVE_SLOT,
            cfg.BOX_HEIGHT + 2 * cfg.EPS,
            mode=Mode.SUBTRACT)

    # --- Two V-slot engaging rails (extruded T cross-sections) ---------
    # Sketch both T-profiles on Plane.XZ at Y=0 and extrude along +Y
    # so the rails span the whole side wall.  Plane.XZ's normal points
    # in -Y, so a negative amount gives a +Y extrusion.
    with BuildSketch(Plane.XZ) as _rail_sketch:
        for _z in (_RAIL_Z_LO, _RAIL_Z_HI):
            with Locations((_TONGUE_CX, _z)):
                Rectangle(_RAIL_NECK_D, _RAIL_NECK_W)
            with Locations((_FOOT_CX, _z)):
                Rectangle(_RAIL_FOOT_D, _RAIL_FOOT_W)
    extrude(amount=-cfg.BOX_DEPTH)


left_side = left_side_builder.part


# ---------------------------------------------------------------------------
# Export + preview (only when run directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    out_dir = Path(__file__).parent / "build"
    out_dir.mkdir(exist_ok=True)

    step_path = out_dir / "left_side.step"
    stl_path  = out_dir / "left_side.stl"

    export_step(left_side, str(step_path))
    export_stl(left_side, str(stl_path))

    bb = left_side.bounding_box()
    print(f"left_side STEP -> {step_path}")
    print(f"left_side STL  -> {stl_path}")
    print(f"bounding box min = {tuple(round(v, 2) for v in tuple(bb.min))}")
    print(f"bounding box max = {tuple(round(v, 2) for v in tuple(bb.max))}")
    print(f"volume           = {left_side.volume:.1f} mm^3")

    try:
        from ocp_vscode import show
    except ImportError:
        print("ocp_vscode not available - skipping show()")
    else:
        show(left_side, names=["left_side"])
