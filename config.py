"""
Shared configuration for every part of the Ender 3 Pro e-box project.

Every part module imports from here so the whole enclosure stays
dimensionally consistent. Do not hard-code geometry numbers inside the
part modules - extend this file instead.

Global coordinate frame (used by every part and by the assembly):

    +X : horizontal along the printer width  (BOX_WIDTH  = 250 mm)
    +Y : horizontal depth into the printer   (BOX_DEPTH  = 125 mm)
    +Z : vertical, up                        (BOX_HEIGHT =  40 mm)

The enclosure is mounted flush with a 4040 V-slot profile, so the
vertical size BOX_HEIGHT is fixed at 40 mm to match the profile.
"""

# --- Enclosure outer envelope --------------------------------------------
BOX_WIDTH  = 250.0   # X
BOX_DEPTH  = 125.0   # Y
BOX_HEIGHT =  40.0   # Z, matches 4040 profile cross-section

# --- Wall and integrated flange stock ------------------------------------
WALL_THK     = 3.0
FLANGE_WIDTH = 40.0   # how far each integrated flange extends into the box
FLANGE_THK   = 5.0    # thickness of the integrated flanges

# --- Sliding panels and grooves ------------------------------------------
PANEL_THK    = 3.0                # nominal thickness of bottom/lid/front
GROOVE_SLOT  = PANEL_THK + 0.3    # slot opening perpendicular to the panel
GROOVE_DEPTH = 5.0                # how far the groove bites into the flange

# --- 4040 V-slot profile (reference values from the profile drawing) -----
VSLOT_NECK_WIDTH  =  6.77   # width of the neck between outer lip and chamber
VSLOT_NECK_DEPTH  =  1.80   # outer lip thickness (distance from outer face
                            # to the front of the neck)
VSLOT_INNER_DEPTH =  4.30   # distance from outer face to the inner chamber
VSLOT_INNER_WIDTH = 11.00   # width of the inner chamber
PROFILE_SIZE      = 40.0    # 4040 profile cross-section

# --- Clearances ----------------------------------------------------------
RAIL_CLEARANCE = 0.3   # slack on the V-slot engaging rail so it slides in

# --- Misc ----------------------------------------------------------------
EPS = 0.1   # small overshoot for boolean cuts to avoid coincident faces
