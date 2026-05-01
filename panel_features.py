"""
Shared build123d helpers that add board-specific features (cutouts,
mounting bosses, ...) to a panel blank produced by `panels.py`.

Helpers consume coordinates in the project's GLOBAL frame; per-config
files translate board-local positions into global X/Y/Z before calling.
Each helper takes a Part, returns a Part - chain helpers freely:

    panel = make_bottom_blank("left")
    for x, y in board_holes_global:
        panel = add_heat_insert_boss(panel, x, y,
                                     surface_z=panels.BOTTOM_INNER_Z)
"""

from build123d import (
    Box,
    BuildPart,
    Cone,
    Cylinder,
    Locations,
    Mode,
    Part,
    add,
)

import config as cfg
import panels


def add_heat_insert_boss(panel: Part, x: float, y: float,
                         surface_z: float, direction: int = 1) -> Part:
    """Add a single heat-insert boss on a HORIZONTAL panel surface.

    Boss geometry from cfg.HEAT_INSERT_*: a TRUNCATED CONE wider at the
    panel root (BOSS_BASE_OD) and narrower at the outer face
    (BOSS_TOP_OD), BOSS_HEIGHT tall, rooted at z = surface_z and
    extruded along +Z (direction = +1, bottom-panel case) or -Z
    (direction = -1, lid case). A coaxial HOLE_DIA x HOLE_DEPTH blind
    hole is drilled from the boss outer face inward; HOLE_DEPTH >
    BOSS_HEIGHT by 1 mm so the insert sinks 1 mm into the panel body.

    Coordinates (x, y, surface_z) are in the GLOBAL frame.
    """
    if direction not in (1, -1):
        raise ValueError(f"direction must be +1 or -1, got {direction!r}")

    boss_h  = cfg.HEAT_INSERT_BOSS_HEIGHT
    base_r  = cfg.HEAT_INSERT_BOSS_BASE_OD / 2
    top_r   = cfg.HEAT_INSERT_BOSS_TOP_OD / 2
    hole_d  = cfg.HEAT_INSERT_HOLE_DEPTH
    hole_r  = cfg.HEAT_INSERT_HOLE_DIA / 2

    # Boss centre Z: half the boss height past the panel inner face
    # along the chosen normal direction.
    boss_cz = surface_z + direction * (boss_h / 2)

    # Cone() places its bottom_radius face at -h/2 and top_radius face
    # at +h/2 (axis along Z). For direction=+1 the wide base must sit
    # at -h/2 (= surface_z), so bottom_radius = base_r. For direction=-1
    # the wide base must sit at +h/2 (= surface_z), so swap.
    if direction == 1:
        cone_bottom_r, cone_top_r = base_r, top_r
    else:
        cone_bottom_r, cone_top_r = top_r, base_r

    # Hole spans from the boss outer face inward by HOLE_DEPTH.
    hole_cz = surface_z + direction * (boss_h - hole_d / 2)

    with BuildPart() as builder:
        add(panel)
        with Locations((x, y, boss_cz)):
            Cone(cone_bottom_r, cone_top_r, boss_h)
        with Locations((x, y, hole_cz)):
            Cylinder(hole_r, hole_d, mode=Mode.SUBTRACT)
    return builder.part


def add_rect_recess_front_panel(panel: Part, x_center: float, z_center: float,
                                width: float, height: float,
                                depth: float) -> Part:
    """Rectangular pocket on the inner (rear) face of a front panel.

    x_center, z_center : global XZ centre of the pocket.
    width              : X extent.
    height             : Z extent.
    depth              : pocket depth cutting from the inner face toward -Y.
    """
    y_center = panels.FRONT_INNER_Y - depth / 2
    with BuildPart() as builder:
        add(panel)
        with Locations((x_center, y_center, z_center)):
            Box(width, depth, height, mode=Mode.SUBTRACT)
    return builder.part


def add_rect_cutout_front_panel(panel: Part, x_center: float, z_center: float,
                                width: float, height: float) -> Part:
    """Through rectangular hole in a front panel, spanning its full Y thickness.

    x_center, z_center : global XZ centre of the opening.
    width              : X extent.
    height             : Z extent.
    """
    y_span   = abs(panels.FRONT_INNER_Y - panels.FRONT_OUTER_Y) + 2 * cfg.EPS
    y_center = (panels.FRONT_INNER_Y + panels.FRONT_OUTER_Y) / 2
    with BuildPart() as builder:
        add(panel)
        with Locations((x_center, y_center, z_center)):
            Box(width, y_span, height, mode=Mode.SUBTRACT)
    return builder.part
