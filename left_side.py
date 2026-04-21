"""
Left side panel of the Ender 3 Pro electronics enclosure.

This is the left END CAP of the box. The wall itself sits at
X in [-WALL_THK, 0]. Three integrated 40 mm wide flanges extend into
the box in the +X direction:

    * a floor flange at the bottom (Z near 0)
    * a ceiling flange at the top  (Z near BOX_HEIGHT)
    * a front flange at the front  (Y near 0)

Each flange carries a rectangular groove on its inner edge into which
one of the separately printed panels (bottom, lid, front panel) slides.

The outer (-X) face of the wall carries a T-shaped rail that engages
the 4040 V-slot on the printer frame. The rail runs along the full Y
depth so the box slides into the profile from one end. The wall's
outer face is flush with the 4040 profile outer face.

Global axes (from config.py):
    +X along printer width, +Y depth, +Z up.
"""

from pathlib import Path

from build123d import Align, Box, Location, export_step, export_stl

import config as cfg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cutter(size, center):
    """Axis-aligned box centred at the given point, used as a boolean cutter."""
    return Location(center) * Box(*size)


def _corner_box(size, origin):
    """Axis-aligned box with its min-corner at the given origin."""
    return Location(origin) * Box(*size, align=(Align.MIN, Align.MIN, Align.MIN))


# ---------------------------------------------------------------------------
# Vertical side wall
# ---------------------------------------------------------------------------
# align=MAX on X places the +X face at X=0, so the wall occupies
# X in [-WALL_THK, 0].  Y and Z use MIN so the wall starts at the origin.
wall = Box(
    cfg.WALL_THK, cfg.BOX_DEPTH, cfg.BOX_HEIGHT,
    align=(Align.MAX, Align.MIN, Align.MIN),
)

# ---------------------------------------------------------------------------
# Floor flange (horizontal, at Z=0) + groove for the sliding bottom panel
# ---------------------------------------------------------------------------
floor_flange = _corner_box(
    (cfg.FLANGE_WIDTH, cfg.BOX_DEPTH, cfg.FLANGE_THK),
    (0.0, 0.0, 0.0),
)

# Groove opens in +X, runs the full Y depth (slides in from Y=0 end),
# centred in Z on the flange thickness.
floor_groove = _cutter(
    size=(cfg.GROOVE_DEPTH + cfg.EPS,
          cfg.BOX_DEPTH + 2 * cfg.EPS,
          cfg.GROOVE_SLOT),
    center=(cfg.FLANGE_WIDTH - cfg.GROOVE_DEPTH / 2 + cfg.EPS / 2,
            cfg.BOX_DEPTH / 2,
            cfg.FLANGE_THK / 2),
)

# ---------------------------------------------------------------------------
# Ceiling flange (horizontal, at Z=BOX_HEIGHT-FLANGE_THK) + lid groove
# ---------------------------------------------------------------------------
lid_flange = _corner_box(
    (cfg.FLANGE_WIDTH, cfg.BOX_DEPTH, cfg.FLANGE_THK),
    (0.0, 0.0, cfg.BOX_HEIGHT - cfg.FLANGE_THK),
)

lid_groove = _cutter(
    size=(cfg.GROOVE_DEPTH + cfg.EPS,
          cfg.BOX_DEPTH + 2 * cfg.EPS,
          cfg.GROOVE_SLOT),
    center=(cfg.FLANGE_WIDTH - cfg.GROOVE_DEPTH / 2 + cfg.EPS / 2,
            cfg.BOX_DEPTH / 2,
            cfg.BOX_HEIGHT - cfg.FLANGE_THK / 2),
)

# ---------------------------------------------------------------------------
# Front flange (vertical, at Y=0) + groove for the front panel
# ---------------------------------------------------------------------------
front_flange = _corner_box(
    (cfg.FLANGE_WIDTH, cfg.FLANGE_THK, cfg.BOX_HEIGHT),
    (0.0, 0.0, 0.0),
)

# The groove runs the full Z height; the front panel slides in from Z=0
# or Z=BOX_HEIGHT (whichever is free in final assembly).  It is centred
# in Y on the front-flange thickness and opens in +X.
front_groove = _cutter(
    size=(cfg.GROOVE_DEPTH + cfg.EPS,
          cfg.GROOVE_SLOT,
          cfg.BOX_HEIGHT + 2 * cfg.EPS),
    center=(cfg.FLANGE_WIDTH - cfg.GROOVE_DEPTH / 2 + cfg.EPS / 2,
            cfg.FLANGE_THK / 2,
            cfg.BOX_HEIGHT / 2),
)

# ---------------------------------------------------------------------------
# V-slot engaging rail on the outer (-X) face of the wall
# ---------------------------------------------------------------------------
# Cross-section in the X-Z plane is a T: a narrow tongue that passes
# through the 4040 neck, plus a wide foot that sits inside the chamber
# and keeps the box from being pulled away from the profile.  The rail
# runs the full Y depth of the box.

rail_z_center = cfg.BOX_HEIGHT / 2

# Narrow tongue (sits in the 6.77 mm neck of the V-slot, 1.80 mm deep)
rail_neck_width = cfg.VSLOT_NECK_WIDTH - cfg.RAIL_CLEARANCE
rail_neck = _corner_box(
    (cfg.VSLOT_NECK_DEPTH, cfg.BOX_DEPTH, rail_neck_width),
    (-cfg.WALL_THK - cfg.VSLOT_NECK_DEPTH,
     0.0,
     rail_z_center - rail_neck_width / 2),
)

# Wide foot (sits in the 11 mm inner chamber, 2.50 mm deeper)
rail_foot_width = cfg.VSLOT_INNER_WIDTH - cfg.RAIL_CLEARANCE
rail_foot_depth = cfg.VSLOT_INNER_DEPTH - cfg.VSLOT_NECK_DEPTH
rail_foot = _corner_box(
    (rail_foot_depth, cfg.BOX_DEPTH, rail_foot_width),
    (-cfg.WALL_THK - cfg.VSLOT_NECK_DEPTH - rail_foot_depth,
     0.0,
     rail_z_center - rail_foot_width / 2),
)

# ---------------------------------------------------------------------------
# Compose the part
# ---------------------------------------------------------------------------
left_side = (
    wall
    + floor_flange
    + lid_flange
    + front_flange
    + rail_neck
    + rail_foot
)
left_side = left_side - floor_groove - lid_groove - front_groove


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
