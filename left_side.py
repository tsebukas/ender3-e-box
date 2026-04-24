"""
Left side panel of the Ender 3 Pro electronics enclosure.

This is the left END CAP of the box. The wall sits inside the BOX_WIDTH
envelope at X in [0, WALL_THK] and spans Y in [0, BOX_DEPTH],
Z in [0, BOX_HEIGHT]. Three integrated flanges (floor, ceiling, front)
extend into the box in the +X direction, each carrying a 5 mm deep
slide-in groove for its own separately printed panel (bottom, lid,
front panel).

The outer (X = 0) face of the wall carries TWO T-shape rails that
engage the two V-slots of the printer's 40-series frame profile. The
rails protrude into -X and run the full Y depth, so the box slides
into the profile from one Y-end.

Global axes (from config.py): +X printer width, +Y depth, +Z up.
"""

from pathlib import Path

from build123d import (
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Box,
    Circle,
    Locations,
    Mode,
    Plane,
    Polyline,
    export_step,
    export_stl,
    extrude,
    fillet,
    make_face,
)

import config as cfg


# ---------------------------------------------------------------------------
# Derived geometry for the V-slot engaging rails
# ---------------------------------------------------------------------------
# Arrow cross-section, drawn on Plane.XZ (local x = global X, local y =
# global Z). The tongue is a straight rectangle that fits through the
# V-slot neck; the foot widens to the full chamber width right past the
# neck, stays parallel for VSLOT_CHAMBER_FLAT_DEPTH, then tapers to a
# short flat tip matching the chamber's back wall:
#
#     |<--- foot ----->|<-- tongue -->|
#        +-------------+              |
#       /              |              |
#      /               +--------------+
#     +                |              |
#      \               +--------------+
#       \              |              |
#        +-------------+              |
#                             wall outer face (X = 0)

_RAIL_NECK_W = cfg.VSLOT_NECK_WIDTH         - cfg.VSLOT_CLEARANCE    # tongue Z
_RAIL_FOOT_W = cfg.VSLOT_CHAMBER_WIDTH      - cfg.VSLOT_CLEARANCE    # foot flat Z
_RAIL_TIP_W  = cfg.VSLOT_CHAMBER_BACK_WIDTH - cfg.VSLOT_CLEARANCE    # tip flat Z

_WALL_OUTER_X     = 0.0
_TONGUE_END_X     = _WALL_OUTER_X - cfg.VSLOT_NECK_DEPTH
_FOOT_FLAT_END_X  = _TONGUE_END_X - cfg.VSLOT_CHAMBER_FLAT_DEPTH
_FOOT_TIP_X       = _WALL_OUTER_X - cfg.VSLOT_POCKET_DEPTH

_RAIL_Z_LO = cfg.BOX_HEIGHT / 2 - cfg.VSLOT_SPACING / 2
_RAIL_Z_HI = cfg.BOX_HEIGHT / 2 + cfg.VSLOT_SPACING / 2


def _rail_polygon_pts(z_center: float) -> list[tuple[float, float]]:
    """Ten (X, Z) vertices of one rail's cross-section, clockwise."""
    return [
        (_WALL_OUTER_X,    z_center + _RAIL_NECK_W / 2),
        (_TONGUE_END_X,    z_center + _RAIL_NECK_W / 2),
        (_TONGUE_END_X,    z_center + _RAIL_FOOT_W / 2),
        (_FOOT_FLAT_END_X, z_center + _RAIL_FOOT_W / 2),
        (_FOOT_TIP_X,      z_center + _RAIL_TIP_W  / 2),
        (_FOOT_TIP_X,      z_center - _RAIL_TIP_W  / 2),
        (_FOOT_FLAT_END_X, z_center - _RAIL_FOOT_W / 2),
        (_TONGUE_END_X,    z_center - _RAIL_FOOT_W / 2),
        (_TONGUE_END_X,    z_center - _RAIL_NECK_W / 2),
        (_WALL_OUTER_X,    z_center - _RAIL_NECK_W / 2),
    ]


# ---------------------------------------------------------------------------
# Build the part
# ---------------------------------------------------------------------------

with BuildPart() as left_side_builder:

    # --- Side wall -----------------------------------------------------
    # X in [0, WALL_THK], Y in [0, BOX_DEPTH], Z in [0, BOX_HEIGHT]
    with Locations((cfg.WALL_THK / 2,
                    cfg.BOX_DEPTH / 2,
                    cfg.BOX_HEIGHT / 2)):
        Box(cfg.WALL_THK, cfg.BOX_DEPTH, cfg.BOX_HEIGHT)

    # --- Floor flange --------------------------------------------------
    # Flange X in [WALL_THK, WALL_THK + FLANGE_WIDTH].
    with Locations((cfg.WALL_THK + cfg.FLANGE_WIDTH / 2,
                    cfg.BOX_DEPTH / 2,
                    cfg.FLANGE_THK / 2)):
        Box(cfg.FLANGE_WIDTH, cfg.BOX_DEPTH, cfg.FLANGE_THK)

    # --- Ceiling flange ------------------------------------------------
    with Locations((cfg.WALL_THK + cfg.FLANGE_WIDTH / 2,
                    cfg.BOX_DEPTH / 2,
                    cfg.BOX_HEIGHT - cfg.FLANGE_THK / 2)):
        Box(cfg.FLANGE_WIDTH, cfg.BOX_DEPTH, cfg.FLANGE_THK)

    # --- Front flange --------------------------------------------------
    # Moved OUTSIDE the box envelope in Y (Y in [-FLANGE_THK, 0]) so its
    # front face is flush with the profile end cap instead of eating
    # into the box interior.
    with Locations((cfg.WALL_THK + cfg.FLANGE_WIDTH / 2,
                    -cfg.FLANGE_THK / 2,
                    cfg.BOX_HEIGHT / 2)):
        Box(cfg.FLANGE_WIDTH, cfg.FLANGE_THK, cfg.BOX_HEIGHT)

    # --- Profile end cap ----------------------------------------------
    # 42 x 40 mm plate (PROFILE_SIZE + WALL_THK wide, PROFILE_SIZE tall)
    # covering the 4040 V-slot profile end AND the wall's outer face -
    # extending the cap by WALL_THK in +X closes the gap to the front
    # flange at X=WALL_THK so the whole front becomes one manifold plate.
    with Locations(((-cfg.PROFILE_SIZE + cfg.WALL_THK) / 2,
                    -cfg.FLANGE_THK / 2,
                    cfg.PROFILE_SIZE / 2)):
        Box(cfg.PROFILE_SIZE + cfg.WALL_THK,
            cfg.FLANGE_THK,
            cfg.PROFILE_SIZE)

    # --- Inside fillets ------------------------------------------------
    # Five inside corners where the side wall meets a flange, or where
    # two flanges meet each other. Each edge is picked by its axis
    # direction and by the center coordinates that uniquely identify
    # the inside corner it belongs to. Apply BEFORE cutting grooves so
    # the fillet selectors only see the five pristine corner edges.
    # The front plate now sits at Y in [-FLANGE_THK, 0], so the three
    # front-related inside corners are at Y=0 (not Y=FLANGE_THK).
    _tol = 0.01
    _wt = cfg.WALL_THK
    _ft = cfg.FLANGE_THK
    _cz = cfg.BOX_HEIGHT - cfg.FLANGE_THK
    _all = left_side_builder.edges()
    _inside_edges = (
        # floor <-> wall (along Y)
        _all.filter_by(Axis.Y)
            .filter_by_position(Axis.X, _wt - _tol, _wt + _tol)
            .filter_by_position(Axis.Z, _ft - _tol, _ft + _tol)
        # ceiling <-> wall (along Y)
        + _all.filter_by(Axis.Y)
              .filter_by_position(Axis.X, _wt - _tol, _wt + _tol)
              .filter_by_position(Axis.Z, _cz - _tol, _cz + _tol)
        # front plate <-> wall (along Z)
        + _all.filter_by(Axis.Z)
              .filter_by_position(Axis.X, _wt - _tol, _wt + _tol)
              .filter_by_position(Axis.Y, -_tol, _tol)
        # floor <-> front plate (along X)
        + _all.filter_by(Axis.X)
              .filter_by_position(Axis.Y, -_tol, _tol)
              .filter_by_position(Axis.Z, _ft - _tol, _ft + _tol)
        # ceiling <-> front plate (along X)
        + _all.filter_by(Axis.X)
              .filter_by_position(Axis.Y, -_tol, _tol)
              .filter_by_position(Axis.Z, _cz - _tol, _cz + _tol)
    )
    fillet(_inside_edges, cfg.INSIDE_FILLET_R)

    # --- Slide-in grooves in the three flanges -------------------------
    _groove_cx = cfg.WALL_THK + cfg.FLANGE_WIDTH - cfg.GROOVE_DEPTH / 2 + cfg.EPS / 2

    # bottom-panel groove in the floor flange
    # Shifted forward by FLANGE_THK so the groove opens at the front
    # face (Y = -FLANGE_THK) - the bottom panel slides in from the
    # front - while leaving a FLANGE_THK-thick stopper of uncut floor
    # flange at the back (Y near BOX_DEPTH).
    with Locations((_groove_cx,
                    cfg.BOX_DEPTH / 2 - cfg.FLANGE_THK,
                    cfg.FLANGE_THK / 2)):
        Box(cfg.GROOVE_DEPTH + cfg.EPS,
            cfg.BOX_DEPTH + 2 * cfg.EPS,
            cfg.GROOVE_SLOT,
            mode=Mode.SUBTRACT)

    # lid groove in the ceiling flange
    # Same forward shift as the floor groove so the lid also slides in
    # from the front and lands against a back stopper.
    with Locations((_groove_cx,
                    cfg.BOX_DEPTH / 2 - cfg.FLANGE_THK,
                    cfg.BOX_HEIGHT - cfg.FLANGE_THK / 2)):
        Box(cfg.GROOVE_DEPTH + cfg.EPS,
            cfg.BOX_DEPTH + 2 * cfg.EPS,
            cfg.GROOVE_SLOT,
            mode=Mode.SUBTRACT)

    # front-panel groove in the front flange
    with Locations((_groove_cx,
                    -cfg.FLANGE_THK / 2,
                    cfg.BOX_HEIGHT / 2)):
        Box(cfg.GROOVE_DEPTH + cfg.EPS,
            cfg.GROOVE_SLOT,
            cfg.BOX_HEIGHT + 2 * cfg.EPS,
            mode=Mode.SUBTRACT)

    # --- Remove front-lip corner nubs ----------------------------------
    # The ~0.85 mm-thick front lip that closes the front-panel groove
    # at Y = -FLANGE_THK would leave tiny nubs where the floor and lid
    # grooves cross it - one in the lower-left corner, one in the
    # upper-left corner of the Front flange. Cut them out so both
    # horizontal slots open cleanly at the front face.
    _nub_y_dim    = (cfg.FLANGE_THK - cfg.GROOVE_SLOT) / 2 + 2 * cfg.EPS
    _nub_y_center = -cfg.FLANGE_THK + _nub_y_dim / 2 - cfg.EPS
    _nub_z_dim    = (cfg.FLANGE_THK - cfg.GROOVE_SLOT) / 2 + 2 * cfg.EPS

    with Locations((_groove_cx, _nub_y_center, _nub_z_dim / 2 - cfg.EPS)):
        Box(cfg.GROOVE_DEPTH + cfg.EPS, _nub_y_dim, _nub_z_dim,
            mode=Mode.SUBTRACT)

    with Locations((_groove_cx, _nub_y_center,
                    cfg.BOX_HEIGHT - _nub_z_dim / 2 + cfg.EPS)):
        Box(cfg.GROOVE_DEPTH + cfg.EPS, _nub_y_dim, _nub_z_dim,
            mode=Mode.SUBTRACT)

    # --- Screw holes through the profile end cap -----------------------
    # Two 5 mm through-holes on the diagonal from (X=-PROFILE_SIZE, Z=0)
    # to (X=0, Z=PROFILE_SIZE), each 10 mm from both edges. The diagonal
    # uses the 40 x 40 profile footprint - the +WALL_THK extension that
    # reaches the front flange is ignored when placing the holes.
    with BuildSketch(Plane.XZ) as _hole_sketch:
        with Locations((-cfg.PROFILE_SIZE + 10.0, 10.0),
                       (-10.0, cfg.PROFILE_SIZE - 10.0)):
            Circle(radius=2.5)
    extrude(amount=cfg.FLANGE_THK + cfg.EPS, mode=Mode.SUBTRACT)

    # --- Two V-slot engaging arrow-shaped rails ------------------------
    # Sketch both rail cross-sections on Plane.XZ at Y=0 and extrude
    # along +Y so the rails span the whole side wall.  Plane.XZ's
    # normal points in -Y, so a negative amount gives a +Y extrusion.
    with BuildSketch(Plane.XZ) as _rail_sketch:
        for _z in (_RAIL_Z_LO, _RAIL_Z_HI):
            with BuildLine() as _rail_line:
                Polyline(*_rail_polygon_pts(_z), close=True)
            make_face()
    extrude(amount=-cfg.BOX_DEPTH)

    # --- Front-plate outside fillets -----------------------------------
    # 2 mm fillet on three outer edges of the combined profile-cap +
    # front-flange plate at the front face (Y = -FLANGE_THK): top
    # (Z=BOX_HEIGHT), bottom (Z=0), and cap-end (X=-PROFILE_SIZE). The
    # front-panel groove side (X=WALL_THK+FLANGE_WIDTH) stays sharp.
    _fp_all = left_side_builder.edges()
    _fp_edges = (
        _fp_all.filter_by(Axis.X)
               .filter_by_position(Axis.Y, -cfg.FLANGE_THK - _tol, -cfg.FLANGE_THK + _tol)
               .filter_by_position(Axis.Z, cfg.BOX_HEIGHT - _tol, cfg.BOX_HEIGHT + _tol)
        + _fp_all.filter_by(Axis.X)
                 .filter_by_position(Axis.Y, -cfg.FLANGE_THK - _tol, -cfg.FLANGE_THK + _tol)
                 .filter_by_position(Axis.Z, -_tol, _tol)
        + _fp_all.filter_by(Axis.Z)
                 .filter_by_position(Axis.X, -cfg.PROFILE_SIZE - _tol, -cfg.PROFILE_SIZE + _tol)
                 .filter_by_position(Axis.Y, -cfg.FLANGE_THK - _tol, -cfg.FLANGE_THK + _tol)
    )
    fillet(_fp_edges, cfg.OUTSIDE_FILLET_R)


left_side = left_side_builder.part


# ---------------------------------------------------------------------------
# Export + preview (only when run directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if cfg.EXPORT_STEP or cfg.EXPORT_STL:
        out_dir = Path(__file__).parent / "build"
        out_dir.mkdir(exist_ok=True)

        if cfg.EXPORT_STEP:
            step_path = out_dir / "left_side.step"
            export_step(left_side, str(step_path))
            print(f"left_side STEP -> {step_path}")

        if cfg.EXPORT_STL:
            stl_path = out_dir / "left_side.stl"
            export_stl(left_side, str(stl_path))
            print(f"left_side STL  -> {stl_path}")

    bb = left_side.bounding_box()
    print(f"bounding box min = {tuple(round(v, 2) for v in tuple(bb.min))}")
    print(f"bounding box max = {tuple(round(v, 2) for v in tuple(bb.max))}")
    print(f"volume           = {left_side.volume:.1f} mm^3")

    if cfg.SHOW_IN_VIEWER:
        try:
            from ocp_vscode import show
        except ImportError:
            print("ocp_vscode not available - skipping show()")
        else:
            show(left_side, names=["left_side"])
