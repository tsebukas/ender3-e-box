"""
Centre divider of the Ender 3 Pro electronics enclosure.

The Y-axis carrier (a 4040 profile sitting on top of the H middle bar at
X = BOX_WIDTH / 2, running along Y) is sunk Y_CARRIER_RECESS into the
middle bar. The divider mirrors that geometry: it sinks the carrier the
same depth into its own top, so the divider's overall working height
matches BOX_HEIGHT (40 mm) and its lid groove lines up with the side
end caps' lid grooves.

Cross-section (X-Z, viewed from +Y), with FLANGE_WIDTH = 6, WALL_THK = 2:

      X=97 X=103 X=105        X=145 X=147 X=153
Z=40   +----+----+ carrier pocket +----+----+   <- lid level
       |LEFT|side| (open up,      |side|RGHT|
       |ceil|wall| open back,     |wall|ceil|
Z=36   +----+    | open front)    |    +----+
            |    | X=105..145     |    |
            |    | Z=33.25..40    |    |
Z=33.25     +----+----------------+----+   <- pocket floor (rails up)
       +-------- pocket floor plate -----+    (X=103..147)
Z=31.25 +-+              +-+              +-+
          | wall X=124..126 |                |
Z=4    +--+                 +--+
       |LEFT floor   RIGHT floor|
Z=0    +-----+-----------+------+
       X=118 X=124    X=126 X=132

The wide front flange at Y in [-FLANGE_THK, 0] connects everything in
the X-Z plane. The carrier pocket cuts through the front flange so the
carrier can slide in/out the front, turning it into a U. The bottom
edge of each U-half then gets an extra horizontal cutout from the U's
outer X end inward to the bottom-panel groove, so the bottom panel
half can slide in from the front through the front-flange opening.

The two top V-slot rails extend FLANGE_THK forward of the box envelope
(Y in [-FLANGE_THK, BOX_DEPTH]) so they sit on the lower-U front flange
material at the front, which makes the part easier to print.

Global axes (from config.py): +X printer width, +Y depth, +Z up.
"""

from pathlib import Path

from build123d import (
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Box,
    Locations,
    Mode,
    Plane,
    Polyline,
    Cylinder,
    export_step,
    export_stl,
    extrude,
    fillet,
    make_face,
)

import config as cfg


# ---------------------------------------------------------------------------
# Top V-slot rail cross-section
# ---------------------------------------------------------------------------
# Same arrow profile as the side walls, rotated 90 degrees so the
# tongue points in +Z (into the carrier's bottom V-slot) and the foot
# widens in +/-X. Sketched on Plane.XZ, extruded along Y.

_RAIL_NECK_W = cfg.VSLOT_NECK_WIDTH         - cfg.VSLOT_CLEARANCE
_RAIL_FOOT_W = cfg.VSLOT_CHAMBER_WIDTH      - cfg.VSLOT_CLEARANCE
_RAIL_TIP_W  = cfg.VSLOT_CHAMBER_BACK_WIDTH - cfg.VSLOT_CLEARANCE

_WALL_TOP_Z      = cfg.CENTER_HEIGHT
_TONGUE_END_Z    = _WALL_TOP_Z   + cfg.VSLOT_NECK_DEPTH
_FOOT_FLAT_END_Z = _TONGUE_END_Z + cfg.VSLOT_CHAMBER_FLAT_DEPTH
_FOOT_TIP_Z      = _WALL_TOP_Z   + cfg.VSLOT_POCKET_DEPTH

_RAIL_X_LO = cfg.BOX_WIDTH / 2 - cfg.VSLOT_SPACING / 2
_RAIL_X_HI = cfg.BOX_WIDTH / 2 + cfg.VSLOT_SPACING / 2


def _top_rail_polygon_pts(x_center: float) -> list[tuple[float, float]]:
    """Ten (X, Z) vertices of one top rail's cross-section."""
    return [
        (x_center + _RAIL_NECK_W / 2, _WALL_TOP_Z),
        (x_center + _RAIL_NECK_W / 2, _TONGUE_END_Z),
        (x_center + _RAIL_FOOT_W / 2, _TONGUE_END_Z),
        (x_center + _RAIL_FOOT_W / 2, _FOOT_FLAT_END_Z),
        (x_center + _RAIL_TIP_W  / 2, _FOOT_TIP_Z),
        (x_center - _RAIL_TIP_W  / 2, _FOOT_TIP_Z),
        (x_center - _RAIL_FOOT_W / 2, _FOOT_FLAT_END_Z),
        (x_center - _RAIL_FOOT_W / 2, _TONGUE_END_Z),
        (x_center - _RAIL_NECK_W / 2, _TONGUE_END_Z),
        (x_center - _RAIL_NECK_W / 2, _WALL_TOP_Z),
    ]


# ---------------------------------------------------------------------------
# Convenience X positions
# ---------------------------------------------------------------------------
_CX = cfg.BOX_WIDTH / 2

# Narrow floor stem (matches the original 2*FLANGE_WIDTH + WALL_THK
# wide bottom).
_WALL_LEFT_X       = _CX - cfg.WALL_THK / 2          # 124
_WALL_RIGHT_X      = _CX + cfg.WALL_THK / 2          # 126
_FLOOR_LEFT_CX     = _WALL_LEFT_X  - cfg.FLANGE_WIDTH / 2
_FLOOR_RIGHT_CX    = _WALL_RIGHT_X + cfg.FLANGE_WIDTH / 2
_FLOOR_LEFT_FAR_X  = _WALL_LEFT_X  - cfg.FLANGE_WIDTH
_FLOOR_RIGHT_FAR_X = _WALL_RIGHT_X + cfg.FLANGE_WIDTH

# Wide top section (PROFILE_SIZE + 2*FLANGE_WIDTH + 2*WALL_THK).
_POCKET_LEFT_X     = _CX - cfg.PROFILE_SIZE / 2                    # 105
_POCKET_RIGHT_X    = _CX + cfg.PROFILE_SIZE / 2                    # 145
_SIDE_LEFT_X       = _POCKET_LEFT_X  - cfg.WALL_THK                # 103
_SIDE_RIGHT_X      = _POCKET_RIGHT_X + cfg.WALL_THK                # 147
_TOP_LEFT_X        = _SIDE_LEFT_X  - cfg.FLANGE_WIDTH              # 97
_TOP_RIGHT_X       = _SIDE_RIGHT_X + cfg.FLANGE_WIDTH              # 153
_TOP_LEFT_CX       = (_TOP_LEFT_X  + _SIDE_LEFT_X)  / 2            # 100
_TOP_RIGHT_CX      = (_SIDE_RIGHT_X + _TOP_RIGHT_X) / 2            # 150
_SIDE_LEFT_CX      = (_SIDE_LEFT_X  + _POCKET_LEFT_X)  / 2         # 104
_SIDE_RIGHT_CX     = (_POCKET_RIGHT_X + _SIDE_RIGHT_X) / 2         # 146

# Y extent of pieces that share a face with the wide front flange:
# extend FLANGE_THK forward so the union is manifold (a 2D face share
# instead of a 1D line touch).
_WALL_LEN_Y = cfg.BOX_DEPTH + cfg.FLANGE_THK
_WALL_CY    = (cfg.BOX_DEPTH - cfg.FLANGE_THK) / 2

# Pocket floor plate spans the carrier pocket plus a side-wall on each
# side, so the side walls share a 2D face with it.
_PLATE_WIDTH = cfg.PROFILE_SIZE + 2 * cfg.WALL_THK   # 44
_PLATE_THK   = cfg.WALL_THK

_FLANGE_CORNER = (cfg.FLANGE_THK - cfg.GROOVE_SLOT) / 2 + cfg.GROOVE_SLOT


# ---------------------------------------------------------------------------
# Build the part
# ---------------------------------------------------------------------------

with BuildPart() as center_builder:

    # --- Narrow floor flanges ------------------------------------------
    for _cx in (_FLOOR_LEFT_CX, _FLOOR_RIGHT_CX):
        with Locations((_cx, cfg.CENTER_DEPTH / 2, cfg.FLANGE_THK / 2)):
            Box(cfg.FLANGE_WIDTH, cfg.CENTER_DEPTH, cfg.FLANGE_THK)

    # --- Central wall, extended forward to share a face with the front -
    with Locations((_CX, (cfg.CENTER_DEPTH - cfg.FLANGE_THK) / 2, cfg.CENTER_HEIGHT / 2)):
        Box(cfg.WALL_THK, cfg.CENTER_DEPTH + cfg.FLANGE_THK, cfg.CENTER_HEIGHT)

    # --- Opening in Central wall, rounded ening for simplier printing -
    _center_opening_height = cfg.CENTER_HEIGHT - cfg.FLANGE_THK - cfg.WALL_THK
    _center_opening_radius = _center_opening_height / 2
    with Locations((_CX, (cfg.CENTER_DEPTH  - cfg.CENTER_TAIL - _center_opening_radius) / 2, (cfg.CENTER_HEIGHT + cfg.FLANGE_THK - cfg.WALL_THK) / 2)):
        Box(cfg.WALL_THK + 2 * cfg.EPS,
            cfg.CENTER_DEPTH  - cfg.CENTER_TAIL - _center_opening_radius,
            _center_opening_height,
            mode=Mode.SUBTRACT)
        
    with Locations((_CX, cfg.CENTER_DEPTH  - cfg.CENTER_TAIL - _center_opening_radius, (cfg.CENTER_HEIGHT + cfg.FLANGE_THK - cfg.WALL_THK) / 2)):
        Cylinder(_center_opening_radius,
            cfg.WALL_THK + 2 * cfg.EPS,
            rotation=(0,90,0),
            mode=Mode.SUBTRACT)

    # --- Pocket floor plate (where the top rails sprout from) ----------
    # Spans PROFILE_SIZE + 2 * WALL_THK so the side walls drop onto its
    # outer edges with a 2D-face share.
    with Locations((_CX,
                    cfg.BOX_DEPTH / 2,
                    cfg.CENTER_HEIGHT - _PLATE_THK / 2)):
        Box(_PLATE_WIDTH, cfg.BOX_DEPTH, _PLATE_THK)

    # --- Side walls (anchor the wide ceiling/front flanges) ------------
    # WALL_THK wide vertical strips between each lid flange and the
    # pocket. Drop from the lid level (BOX_HEIGHT) down to the pocket
    # floor (CENTER_HEIGHT). Extended forward to merge into the wide
    # front flange instead of touching it along a single line.
    _side_z_dim = cfg.BOX_HEIGHT - cfg.CENTER_HEIGHT
    _side_z_cy  = (cfg.BOX_HEIGHT + cfg.CENTER_HEIGHT) / 2
    for _cx in (_SIDE_LEFT_CX, _SIDE_RIGHT_CX):
        with Locations((_cx, _WALL_CY, _side_z_cy)):
            Box(cfg.WALL_THK, _WALL_LEN_Y, _side_z_dim)

    # --- Wide ceiling slab (cut into LEFT/RIGHT halves by the pocket) --
    with Locations((_CX,
                    cfg.BOX_DEPTH / 2,
                    cfg.BOX_HEIGHT - cfg.FLANGE_THK / 2)):
        Box(cfg.CENTER_TOP_WIDTH, cfg.BOX_DEPTH, cfg.FLANGE_THK)

    # --- Wide front flange (becomes U-shaped after the pocket cut) -----
    with Locations((_CX,
                    -cfg.FLANGE_THK / 2,
                    cfg.BOX_HEIGHT / 2 + _FLANGE_CORNER / 2)):
        Box(cfg.CENTER_TOP_WIDTH, cfg.FLANGE_THK, cfg.BOX_HEIGHT - _FLANGE_CORNER)

    # --- Carrier pocket cut --------------------------------------------
    # Removes X in [pocket left, pocket right], Z in [CENTER_HEIGHT,
    # BOX_HEIGHT], Y across the full depth AND through the front flange
    # (so the carrier can slide in/out the front). Splits the wide
    # ceiling slab into two flange halves and turns the wide front
    # flange into a U.
    _pocket_y_lo = -cfg.FLANGE_THK - cfg.EPS
    _pocket_y_hi = cfg.BOX_DEPTH + cfg.EPS
    _pocket_z_lo = cfg.CENTER_HEIGHT
    _pocket_z_hi = cfg.BOX_HEIGHT + cfg.EPS
    with Locations((_CX,
                    (_pocket_y_lo + _pocket_y_hi) / 2,
                    (_pocket_z_lo + _pocket_z_hi) / 2)):
        Box(cfg.PROFILE_SIZE + cfg.VSLOT_CLEARANCE,
            _pocket_y_hi - _pocket_y_lo,
            _pocket_z_hi - _pocket_z_lo,
            mode=Mode.SUBTRACT)

    # --- Inside fillets ------------------------------------------------
    # Apply BEFORE cutting grooves and bottom-passage so the selectors
    # only see pristine corner edges.
    _tol = 0.01
    _ft  = cfg.FLANGE_THK
    _cz_low  = cfg.CENTER_HEIGHT - _PLATE_THK   # plate bottom Z
    _cz_high = cfg.BOX_HEIGHT - cfg.FLANGE_THK  # ceiling-flange bottom Z
    _all = center_builder.edges()
    _inside_edges = (
        # narrow-floor <-> wide front flange (along X), each half
        _all.filter_by(Axis.X)
              .filter_by_position(Axis.X, _FLOOR_LEFT_FAR_X  - _tol, _WALL_LEFT_X  + _tol)
              .filter_by_position(Axis.Y, -_tol, _tol)
              .filter_by_position(Axis.Z, _ft - _tol, _ft + _tol)
        + _all.filter_by(Axis.X)
              .filter_by_position(Axis.X, _WALL_RIGHT_X - _tol, _FLOOR_RIGHT_FAR_X + _tol)
              .filter_by_position(Axis.Y, -_tol, _tol)
              .filter_by_position(Axis.Z, _ft - _tol, _ft + _tol)
        # wide ceiling <-> wide front flange (along X), each half
        + _all.filter_by(Axis.X)
              .filter_by_position(Axis.X, _TOP_LEFT_X  - _tol, _SIDE_LEFT_X  + _tol)
              .filter_by_position(Axis.Y, -_tol, _tol)
              .filter_by_position(Axis.Z, _cz_high - _tol, _cz_high + _tol)
        + _all.filter_by(Axis.X)
              .filter_by_position(Axis.X, _SIDE_RIGHT_X - _tol, _TOP_RIGHT_X + _tol)
              .filter_by_position(Axis.Y, -_tol, _tol)
              .filter_by_position(Axis.Z, _cz_high - _tol, _cz_high + _tol)
        # pocket plate side + side wall <-> wide front flange (along Z),
        # where the merged plate-edge and side-wall outer face meets the
        # front flange's interior Y=0 face on each upper U-arm
        + _all.filter_by(Axis.Z)
              .filter_by_position(Axis.X, _SIDE_LEFT_X  - _tol, _SIDE_LEFT_X  + _tol)
              .filter_by_position(Axis.Y, -_tol, _tol)
              .filter_by_position(Axis.Z, _cz_low - _tol, _cz_high + _tol)
        + _all.filter_by(Axis.Z)
              .filter_by_position(Axis.X, _SIDE_RIGHT_X - _tol, _SIDE_RIGHT_X + _tol)
              .filter_by_position(Axis.Y, -_tol, _tol)
              .filter_by_position(Axis.Z, _cz_low - _tol, _cz_high + _tol)
        # pocket plate bottom <-> wide front flange (along X), each half
        # of the plate bottom edge that meets the front flange interior
        + _all.filter_by(Axis.X)
              .filter_by_position(Axis.X, _SIDE_LEFT_X  - _tol, _WALL_LEFT_X  + _tol)
              .filter_by_position(Axis.Y, -_tol, _tol)
              .filter_by_position(Axis.Z, _cz_low - _tol, _cz_low + _tol)
        + _all.filter_by(Axis.X)
              .filter_by_position(Axis.X, _WALL_RIGHT_X - _tol, _SIDE_RIGHT_X + _tol)
              .filter_by_position(Axis.Y, -_tol, _tol)
              .filter_by_position(Axis.Z, _cz_low - _tol, _cz_low + _tol)
    )
    fillet(_inside_edges, cfg.INSIDE_FILLET_R)

    # --- Slide-in grooves ----------------------------------------------
    # Bottom-panel grooves (in the narrow floor flanges).
    _bottom_gx_left  = _FLOOR_LEFT_FAR_X  + cfg.GROOVE_DEPTH / 2 - cfg.EPS / 2
    _bottom_gx_right = _FLOOR_RIGHT_FAR_X - cfg.GROOVE_DEPTH / 2 + cfg.EPS / 2
    for _gx in (_bottom_gx_left, _bottom_gx_right):
        with Locations((_gx,
                        cfg.CENTER_DEPTH / 2 - cfg.FLANGE_THK,
                        cfg.FLANGE_THK / 2)):
            Box(cfg.GROOVE_DEPTH + cfg.EPS,
                cfg.CENTER_DEPTH + 2 * cfg.EPS + 2 * cfg.FLANGE_THK,
                cfg.GROOVE_SLOT,
                mode=Mode.SUBTRACT)

    # Lid-panel grooves (in the WIDE ceiling flange halves).
    _lid_gx_left  = _TOP_LEFT_X  + cfg.GROOVE_DEPTH / 2 - cfg.EPS / 2
    _lid_gx_right = _TOP_RIGHT_X - cfg.GROOVE_DEPTH / 2 + cfg.EPS / 2
    for _gx in (_lid_gx_left, _lid_gx_right):
        with Locations((_gx,
                        cfg.BOX_DEPTH / 2 - cfg.FLANGE_THK,
                        cfg.BOX_HEIGHT - cfg.FLANGE_THK / 2)):
            Box(cfg.GROOVE_DEPTH + cfg.EPS,
                cfg.BOX_DEPTH + 2 * cfg.EPS + 2 * cfg.FLANGE_THK,
                cfg.GROOVE_SLOT,
                mode=Mode.SUBTRACT)

    # Front-panel grooves (in the WIDE front flange's U-arms).
    _front_gx_left  = _lid_gx_left
    _front_gx_right = _lid_gx_right
    for _gx in (_front_gx_left, _front_gx_right):
        with Locations((_gx,
                        -cfg.FLANGE_THK / 2,
                        cfg.BOX_HEIGHT / 2)):
            Box(cfg.GROOVE_DEPTH + cfg.EPS,
                cfg.GROOVE_SLOT,
                cfg.BOX_HEIGHT + 2 * cfg.EPS,
                mode=Mode.SUBTRACT)
            
    # --- Front-lip nub trim --------------------------------------------
    # Each LEFT/RIGHT pair of lid + front grooves leaves a tiny corner
    # nub at the top-front face. The bottom-front nubs are already gone
    # because the bottom-passage cutout punches through the front flange
    # at the panel's Z range.
    _nub_y_dim    = (cfg.FLANGE_THK - cfg.GROOVE_SLOT) / 2 + 2 * cfg.EPS
    _nub_y_center = -cfg.FLANGE_THK + _nub_y_dim / 2 - cfg.EPS
    _nub_z_dim    = (cfg.FLANGE_THK - cfg.GROOVE_SLOT) / 2 + 2 * cfg.EPS

    for _gx in (_lid_gx_left, _lid_gx_right):
        with Locations((_gx, _nub_y_center,
                        cfg.BOX_HEIGHT - _nub_z_dim / 2 + cfg.EPS)):
            Box(cfg.GROOVE_DEPTH + cfg.EPS, _nub_y_dim, _nub_z_dim,
                mode=Mode.SUBTRACT)

    # --- Needs a little adjustment at the bottom grooves ---
    with Locations((_CX,
                    -cfg.FLANGE_THK / 2,
                    _FLANGE_CORNER / 2)):
        Box(cfg.WALL_THK + (cfg.FLANGE_WIDTH - cfg.GROOVE_DEPTH) * 2 , cfg.FLANGE_THK, _FLANGE_CORNER)

    # --- Two V-slot engaging arrow rails on the pocket floor -----------
    # Sketch on Plane.XZ offset to Y = -FLANGE_THK and extrude in +Y so
    # the rails span (BOX_DEPTH + FLANGE_THK), reaching FLANGE_THK
    # forward of the box envelope. This gives the rails a continuous
    # bed of solid material at the front (the lower-U front flange) so
    # the part is easier to print.  Plane.XZ's normal is -Y, so a
    # positive offset moves the sketch plane to -Y; a negative extrude
    # amount on that plane goes back in +Y.
    with BuildSketch(Plane.XZ.offset(cfg.FLANGE_THK)) as _rail_sketch:
        for _x in (_RAIL_X_LO, _RAIL_X_HI):
            with BuildLine() as _rail_line:
                Polyline(*_top_rail_polygon_pts(_x), close=True)
            make_face()
    extrude(amount=-(cfg.BOX_DEPTH + cfg.FLANGE_THK))

    # --- Front-plate outside fillets -----------------------------------
    # 2 mm fillet on three outer edges of the combined profile-cap +
    # front-flange plate at the front face (Y = -FLANGE_THK): top
    # (Z=BOX_HEIGHT), bottom (Z=0)
    _fp_all = center_builder.edges()
    _fp_edges = (
        _fp_all.filter_by(Axis.X)
               .filter_by_position(Axis.Y, -cfg.FLANGE_THK - _tol, -cfg.FLANGE_THK + _tol)
               .filter_by_position(Axis.Z, cfg.BOX_HEIGHT - _tol, cfg.BOX_HEIGHT + _tol)
        + _fp_all.filter_by(Axis.X)
                 .filter_by_position(Axis.Y, -cfg.FLANGE_THK - _tol, -cfg.FLANGE_THK + _tol)
                 .filter_by_position(Axis.Z, -_tol, _tol)
    )
    fillet(_fp_edges, cfg.OUTSIDE_FILLET_R)


center = center_builder.part


# ---------------------------------------------------------------------------
# Export + preview (only when run directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if cfg.EXPORT_STEP or cfg.EXPORT_STL:
        out_dir = Path(__file__).parent / "build"
        out_dir.mkdir(exist_ok=True)

        if cfg.EXPORT_STEP:
            step_path = out_dir / "center.step"
            export_step(center, str(step_path))
            print(f"center STEP -> {step_path}")

        if cfg.EXPORT_STL:
            stl_path = out_dir / "center.stl"
            export_stl(center, str(stl_path))
            print(f"center STL  -> {stl_path}")

    bb = center.bounding_box()
    print(f"bounding box min = {tuple(round(v, 2) for v in tuple(bb.min))}")
    print(f"bounding box max = {tuple(round(v, 2) for v in tuple(bb.max))}")
    print(f"volume           = {center.volume:.1f} mm^3")

    if cfg.SHOW_IN_VIEWER:
        try:
            from ocp_vscode import show
        except ImportError:
            print("ocp_vscode not available - skipping show()")
        else:
            show(center, names=["center"])
