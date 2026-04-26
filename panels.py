"""
Slide-in panel blanks for the Ender 3 Pro electronics enclosure.

Three blank-panel factory functions return Part objects already placed
in the global coordinate frame, sized to slide into the matching
grooves on the LEFT or RIGHT half of the enclosure:

    make_bottom_blank(side)  -> bottom-panel half (floor grooves)
    make_front_blank(side)   -> front-panel half  (front grooves)
    make_lid_blank(side)     -> lid-panel half    (ceiling grooves)

The blanks carry no cutouts, mounting bosses or board-specific
features. Per-electronics-config files import these factory functions
and apply the cuts/adds for each board set.

Insertion order and resulting panel envelopes:

  1. BOTTOM slides in horizontally from the front, comes to rest with
     its front edge flush with the box's front face.
        Y in [-FLANGE_THK, BOX_DEPTH], Z in floor-groove slot.

  2. FRONT drops in vertically from the top and lands on top of the
     bottom panel's front edge. Its Z range stops short of both the
     floor and lid grooves so it does not reach inside either:
        Z in [_FRONT_PANEL_Z_LO, _FRONT_PANEL_Z_HI].
     Height = BOX_HEIGHT - FLANGE_THK - GROOVE_SLOT.

  3. LID slides in horizontally from the front, OVER the front panel,
     and ends flush with the box's front face like the bottom.
        Y in [-FLANGE_THK, BOX_DEPTH], Z in ceiling-groove slot.

Global axes (from config.py): +X printer width, +Y depth, +Z up.
"""

from pathlib import Path

from build123d import (
    Axis,
    BuildPart,
    Box,
    Locations,
    Part,
    export_step,
    export_stl,
    fillet,
)

import config as cfg


# ---------------------------------------------------------------------------
# Insertion X positions: where each panel's outer edge rests in its groove
# ---------------------------------------------------------------------------
# Side end caps: floor / ceiling / front grooves all reach the same X
# (each groove eats GROOVE_DEPTH inward from the flange's inner end).
_SIDE_LEFT_INSERT_X  = cfg.WALL_THK + cfg.FLANGE_WIDTH - cfg.GROOVE_DEPTH      # 3
_SIDE_RIGHT_INSERT_X = cfg.BOX_WIDTH - _SIDE_LEFT_INSERT_X                     # 247

# Centre divider has TWO sets of groove X positions:
#   - Narrow floor stem -> bottom-panel grooves (close to box centre).
#   - Wide top section  -> lid + front-panel grooves (further out, with
#     room for the carrier pocket between them).
_CX = cfg.BOX_WIDTH / 2

# Bottom (narrow) grooves.
_CENTER_FLOOR_LEFT_X         = _CX - cfg.WALL_THK / 2 - cfg.FLANGE_WIDTH                       # 118
_CENTER_BOTTOM_LEFT_INSERT_X  = _CENTER_FLOOR_LEFT_X + cfg.GROOVE_DEPTH                        # 123
_CENTER_BOTTOM_RIGHT_INSERT_X = cfg.BOX_WIDTH - _CENTER_BOTTOM_LEFT_INSERT_X                   # 127

# Lid + front (wide) grooves.
_CENTER_TOP_LEFT_X         = _CX - cfg.PROFILE_SIZE / 2 - cfg.WALL_THK - cfg.FLANGE_WIDTH      # 97
_CENTER_TOP_LEFT_INSERT_X  = _CENTER_TOP_LEFT_X + cfg.GROOVE_DEPTH                             # 102
_CENTER_TOP_RIGHT_INSERT_X = cfg.BOX_WIDTH - _CENTER_TOP_LEFT_INSERT_X                         # 148


# ---------------------------------------------------------------------------
# Common Y / Z extents
# ---------------------------------------------------------------------------
# Bottom and lid panels span the front face all the way to the back face
# (variant B): front edge flush with the box, rear free since neither
# the side nor centre grooves carry a back stopper.
_HORIZ_PANEL_Y_LO = -cfg.FLANGE_THK
_HORIZ_PANEL_Y_HI = cfg.BOX_DEPTH

# Front panel sits BETWEEN the floor groove top wall and the lid groove
# bottom wall, so it never reaches into either horizontal groove. The
# floor groove's top wall sits (FLANGE_THK + GROOVE_SLOT)/2 above Z=0;
# the lid groove's bottom wall sits the same offset below Z=BOX_HEIGHT.
_FRONT_PANEL_Z_LO = (cfg.FLANGE_THK + cfg.GROOVE_SLOT) / 2
_FRONT_PANEL_Z_HI = cfg.BOX_HEIGHT - _FRONT_PANEL_Z_LO


# ---------------------------------------------------------------------------
# Stepped panel cross-section (thick body + thin tongues)
# ---------------------------------------------------------------------------
# The part of the panel that slides into a groove slot must stay at the
# slot's PANEL_THK thickness. Everywhere else the panel's OUTSIDE face
# (lid top / front face / bottom of bottom panel) is raised toward the
# flange's outer face by _RAISE, so the box's outer surface looks like
# one continuous shell of flanges + panel bodies. _RAISE equals one
# groove lip thickness ((FLANGE_THK - GROOVE_SLOT)/2); a (GROOVE_SLOT -
# PANEL_THK)/2 visual recess remains, absorbing the slot's fit slack.
#
# Bonus side-effect (per design intent): the thick body sticks out of
# the X groove slots at the front, forming stoppers in the front
# corners of the bottom and lid panels.

_GROOVE_EDGE = (cfg.FLANGE_THK - cfg.GROOVE_SLOT) / 2
_STOPPER_DEPTH = cfg.FLANGE_THK - _GROOVE_EDGE

_RAISE = (cfg.FLANGE_THK - cfg.GROOVE_SLOT) / 2

# Bottom panel: thin part centred on the floor flange; thick body
# extends DOWN by _RAISE.
_BOTTOM_THIN_Z_LO = (cfg.FLANGE_THK - cfg.PANEL_THK) / 2
_BOTTOM_THIN_Z_HI = _BOTTOM_THIN_Z_LO + cfg.PANEL_THK
_BOTTOM_BODY_Z_LO = _BOTTOM_THIN_Z_LO - _RAISE
_BOTTOM_BODY_Z_HI = _BOTTOM_THIN_Z_HI

# Lid panel: thin part centred on the ceiling flange; thick body extends
# UP by _RAISE.
_LID_THIN_Z_HI = cfg.BOX_HEIGHT - (cfg.FLANGE_THK - cfg.PANEL_THK) / 2
_LID_THIN_Z_LO = _LID_THIN_Z_HI - cfg.PANEL_THK
_LID_BODY_Z_HI = _LID_THIN_Z_HI + _RAISE
_LID_BODY_Z_LO = _LID_THIN_Z_LO

# Front panel: thin part centred on the front flange; thick body
# extends FORWARD (toward -Y) by _RAISE.
_FRONT_THIN_Y_HI = -(cfg.FLANGE_THK - cfg.PANEL_THK) / 2
_FRONT_THIN_Y_LO = _FRONT_THIN_Y_HI - cfg.PANEL_THK
_FRONT_BODY_Y_LO = _FRONT_THIN_Y_LO - _RAISE
_FRONT_BODY_Y_HI = _FRONT_THIN_Y_HI


# ---------------------------------------------------------------------------
# Per-side X ranges
# ---------------------------------------------------------------------------

def _bottom_x_range(side: str) -> tuple[float, float]:
    """X range a bottom-panel half occupies, outer edge to outer edge."""
    if side == "left":
        return (_SIDE_LEFT_INSERT_X, _CENTER_BOTTOM_LEFT_INSERT_X)
    if side == "right":
        return (_CENTER_BOTTOM_RIGHT_INSERT_X, _SIDE_RIGHT_INSERT_X)
    raise ValueError(f"side must be 'left' or 'right', got {side!r}")


def _top_x_range(side: str) -> tuple[float, float]:
    """X range a lid- or front-panel half occupies."""
    if side == "left":
        return (_SIDE_LEFT_INSERT_X, _CENTER_TOP_LEFT_INSERT_X)
    if side == "right":
        return (_CENTER_TOP_RIGHT_INSERT_X, _SIDE_RIGHT_INSERT_X)
    raise ValueError(f"side must be 'left' or 'right', got {side!r}")


def _x_layout(outer: tuple[float, float]) -> tuple[tuple[float, float],
                                                   tuple[float, float],
                                                   tuple[float, float]]:
    """Split a panel's X span into (body, left_tongue, right_tongue).

    Each tongue is GROOVE_DEPTH wide at the panel's outer X edges - the
    part sliding into the side / centre flange slot. The body fills the
    middle and is raised to the box's outer face.
    """
    x_lo, x_hi = outer
    left_tongue = (x_lo, x_lo + cfg.GROOVE_DEPTH)
    right_tongue = (x_hi - cfg.GROOVE_DEPTH, x_hi)
    body = (left_tongue[1], right_tongue[0])
    return body, left_tongue, right_tongue


# ---------------------------------------------------------------------------
# Blank-panel factory functions
# ---------------------------------------------------------------------------

def make_bottom_blank(side: str) -> Part:
    """Blank bottom-panel half placed in the global frame."""
    body_x, left_tx, right_tx = _x_layout(_bottom_x_range(side))

    panel_cy    = (_HORIZ_PANEL_Y_LO + _HORIZ_PANEL_Y_HI) / 2
    panel_y_dim = _HORIZ_PANEL_Y_HI - _HORIZ_PANEL_Y_LO

    body_cz    = (_BOTTOM_BODY_Z_LO + _BOTTOM_BODY_Z_HI) / 2
    body_z_dim = _BOTTOM_BODY_Z_HI - _BOTTOM_BODY_Z_LO

    thin_cz    = (_BOTTOM_THIN_Z_LO + _BOTTOM_THIN_Z_HI) / 2

    with BuildPart() as builder:
        # Thick body in the middle.
        with Locations(((body_x[0] + body_x[1]) / 2, panel_cy, body_cz)):
            Box(body_x[1] - body_x[0], panel_y_dim, body_z_dim)
        # Thin tongues at each X side, sliding into the side / centre slot.
        for tx in (left_tx, right_tx):
            with Locations(((tx[0] + tx[1]) / 2, panel_cy, thin_cz)):
                Box(tx[1] - tx[0], panel_y_dim, cfg.PANEL_THK)
        # Stoppers 
        for tx in (left_tx, right_tx):
            with Locations(((tx[0] + tx[1]) / 2, 0 - cfg.FLANGE_THK + _STOPPER_DEPTH / 2, body_cz)):
                Box(tx[1] - tx[0],  _STOPPER_DEPTH, body_z_dim)
        # Round the front-bottom edge of the thick body.
        _tol = 0.01
        front_bottom = (
            builder.edges()
                   .filter_by(Axis.X)
                   .filter_by_position(Axis.Y, _HORIZ_PANEL_Y_LO - _tol,
                                                _HORIZ_PANEL_Y_LO + _tol)
                   .filter_by_position(Axis.Z, _BOTTOM_BODY_Z_LO - _tol,
                                                _BOTTOM_BODY_Z_LO + _tol)
        )
        fillet(front_bottom, cfg.OUTSIDE_FILLET_R)
    return builder.part


def make_front_blank(side: str) -> Part:
    """Blank front-panel half placed in the global frame."""
    body_x, left_tx, right_tx = _x_layout(_top_x_range(side))

    panel_cz    = (_FRONT_PANEL_Z_LO + _FRONT_PANEL_Z_HI) / 2
    panel_z_dim = _FRONT_PANEL_Z_HI - _FRONT_PANEL_Z_LO

    body_cy    = (_FRONT_BODY_Y_LO + _FRONT_BODY_Y_HI) / 2
    body_y_dim = _FRONT_BODY_Y_HI - _FRONT_BODY_Y_LO

    thin_cy    = (_FRONT_THIN_Y_LO + _FRONT_THIN_Y_HI) / 2

    with BuildPart() as builder:
        # Thick body in the middle.
        with Locations(((body_x[0] + body_x[1]) / 2, body_cy, panel_cz)):
            Box(body_x[1] - body_x[0], body_y_dim, panel_z_dim)
        # Thin tongues at each X side, sliding into the side / centre slot.
        for tx in (left_tx, right_tx):
            with Locations(((tx[0] + tx[1]) / 2, thin_cy, panel_cz)):
                Box(tx[1] - tx[0], cfg.PANEL_THK, panel_z_dim)
    return builder.part


def make_lid_blank(side: str) -> Part:
    """Blank lid-panel half placed in the global frame."""
    body_x, left_tx, right_tx = _x_layout(_top_x_range(side))

    panel_cy    = (_HORIZ_PANEL_Y_LO + _HORIZ_PANEL_Y_HI) / 2
    panel_y_dim = _HORIZ_PANEL_Y_HI - _HORIZ_PANEL_Y_LO

    body_cz    = (_LID_BODY_Z_LO + _LID_BODY_Z_HI) / 2
    body_z_dim = _LID_BODY_Z_HI - _LID_BODY_Z_LO

    thin_cz    = (_LID_THIN_Z_LO + _LID_THIN_Z_HI) / 2

    with BuildPart() as builder:
        # Thick body in the middle.
        with Locations(((body_x[0] + body_x[1]) / 2, panel_cy, body_cz)):
            Box(body_x[1] - body_x[0], panel_y_dim, body_z_dim)
        # Thin tongues at each X side, sliding into the side / centre slot.
        for tx in (left_tx, right_tx):
            with Locations(((tx[0] + tx[1]) / 2, panel_cy, thin_cz)):
                Box(tx[1] - tx[0], panel_y_dim, cfg.PANEL_THK)
        # Stoppers 
        for tx in (left_tx, right_tx):
            with Locations(((tx[0] + tx[1]) / 2, 0 - cfg.FLANGE_THK + _STOPPER_DEPTH / 2, body_cz)):
                Box(tx[1] - tx[0], _STOPPER_DEPTH, body_z_dim)
        # Round the front-top edge of the thick body.
        _tol = 0.01
        front_top = (
            builder.edges()
                   .filter_by(Axis.X)
                   .filter_by_position(Axis.Y, _HORIZ_PANEL_Y_LO - _tol,
                                                _HORIZ_PANEL_Y_LO + _tol)
                   .filter_by_position(Axis.Z, _LID_BODY_Z_HI - _tol,
                                                _LID_BODY_Z_HI + _tol)
        )
        fillet(front_top, cfg.OUTSIDE_FILLET_R)
    return builder.part


# ---------------------------------------------------------------------------
# Module-level blank instances
# ---------------------------------------------------------------------------

bottom_left  = make_bottom_blank("left")
bottom_right = make_bottom_blank("right")
front_left   = make_front_blank("left")
front_right  = make_front_blank("right")
lid_left     = make_lid_blank("left")
lid_right    = make_lid_blank("right")


# ---------------------------------------------------------------------------
# Direct-run preview: show all six blank panels
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    blanks = {
        "bottom_left":  bottom_left,
        "bottom_right": bottom_right,
        "front_left":   front_left,
        "front_right":  front_right,
        "lid_left":     lid_left,
        "lid_right":    lid_right,
    }

    if cfg.EXPORT_STEP or cfg.EXPORT_STL:
        out_dir = Path(__file__).parent / "build"
        out_dir.mkdir(exist_ok=True)
        for name, part in blanks.items():
            if cfg.EXPORT_STEP:
                step_path = out_dir / f"{name}_blank.step"
                export_step(part, str(step_path))
                print(f"{name} STEP -> {step_path}")
            if cfg.EXPORT_STL:
                stl_path = out_dir / f"{name}_blank.stl"
                export_stl(part, str(stl_path))
                print(f"{name} STL  -> {stl_path}")

    for name, part in blanks.items():
        bb = part.bounding_box()
        bb_min = tuple(round(v, 2) for v in tuple(bb.min))
        bb_max = tuple(round(v, 2) for v in tuple(bb.max))
        print(f"{name:13s}  bb={bb_min}->{bb_max}  vol={part.volume:.1f}")

    if cfg.SHOW_IN_VIEWER:
        try:
            from ocp_vscode import show
        except ImportError:
            print("ocp_vscode not available - skipping show()")
        else:
            show(*blanks.values(), names=list(blanks.keys()))
