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
    BuildSketch,
    Circle,
    Cone,
    Cylinder,
    Locations,
    Mode,
    Part,
    Plane,
    PolarLocations,
    add,
    extrude,
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


def add_fan_grille_lid(
    panel: Part,
    fan_cx: float,
    fan_cy: float,
    hole_positions: list[tuple[float, float]],
    hole_dia: float = 4.0,
    ring1_radius: float = 12.0,
    ring1_count: int = 15,
    ring2_radius: float = 17.0,
    ring2_count: int = 21,
    screw_dia: float = 3.2,
    cbore_dia: float = 6.0,
    cbore_depth: float = 1.0,
) -> Part:
    """Fan grille openings and M3 mount holes on a lid panel.

    Cuts two concentric rings of circular holes in the fan's annular target
    zone (OD=38mm, ID=20mm), centered at (fan_cx, fan_cy) in the global frame.

    Default geometry for a 4010 fan:
      ring 1: r=12mm, 15 holes, d=4mm -> arc wall ~1.0mm between holes
      ring 2: r=17mm, 21 holes, d=4mm -> arc wall ~1.1mm between holes
      combined open area: 36 * pi * 2^2 = 452mm^2 = 55% of the annular area.

    Small holes prevent objects from falling through while keeping airflow
    sufficient. Through-holes (screw_dia) with flat cylindrical counterbores
    (cbore_dia x cbore_depth) on the outer (top) face are cut at each (x, y)
    in hole_positions.

    Extrusion direction: sketch on outer (top) face, extrude -Z through lid.
    Plane.XY normal is +Z; negative amount gives downward (-Z) cut.
    """
    lid_top = panels.LID_OUTER_Z
    lid_bot = panels.LID_INNER_Z
    lid_thk = lid_top - lid_bot

    with BuildPart() as builder:
        add(panel)

        # Fan grille: two concentric rings of circular holes.
        # PolarLocations within Locations((fan_cx, fan_cy)) places hole centres
        # at (fan_cx + r*cos(theta), fan_cy + r*sin(theta)).
        with BuildSketch(Plane.XY.offset(lid_top + cfg.EPS)):
            with Locations((fan_cx, fan_cy)):
                with PolarLocations(ring1_radius, ring1_count):
                    Circle(hole_dia / 2)
                with PolarLocations(ring2_radius, ring2_count):
                    Circle(hole_dia / 2)
        extrude(amount=-(lid_thk + 2 * cfg.EPS), mode=Mode.SUBTRACT)

        # Mount holes: through-hole + flat counterbore on the outer (top) face.
        for hx, hy in hole_positions:
            hole_cz = (lid_top + lid_bot) / 2
            with Locations((hx, hy, hole_cz)):
                Cylinder(screw_dia / 2, lid_thk + 2 * cfg.EPS, mode=Mode.SUBTRACT)
            cbore_cz = lid_top - cbore_depth / 2 + cfg.EPS / 2
            with Locations((hx, hy, cbore_cz)):
                Cylinder(cbore_dia / 2, cbore_depth + cfg.EPS, mode=Mode.SUBTRACT)

    return builder.part
