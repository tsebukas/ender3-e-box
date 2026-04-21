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
WALL_THK     = 2.0
FLANGE_WIDTH = 40.0   # how far each integrated flange extends into the box
FLANGE_THK   = 5.0    # thickness of the integrated flanges

# --- Sliding panels and grooves ------------------------------------------
PANEL_THK    = 3.0                # nominal thickness of bottom/lid/front
GROOVE_SLOT  = PANEL_THK + 0.3    # slot opening perpendicular to the panel
GROOVE_DEPTH = 5.0                # how far the groove bites into the flange

# --- V-slot profile reference (from lahteylesanne/4040_v-slot.jpg) -------
# The printer frame profile is a 4040 (40 x 40 mm) whose face carries
# TWO V-slots (not the single V-slot of a standard 4040). The two
# V-slots give the side piece two T-rails to engage instead of one.
VSLOT_NECK_WIDTH  =  6.77   # width of the neck between outer lip and chamber
VSLOT_NECK_DEPTH  =  1.80   # outer lip thickness (outer face -> neck front)
VSLOT_INNER_DEPTH =  4.30   # outer face -> back of the inner chamber
VSLOT_INNER_WIDTH = 11.00   # inner chamber width (widest, right after the neck)
VSLOT_BACK_WIDTH  =  3.00   # flat back wall of the chamber (estimated, no drawing dim)
PROFILE_SIZE      = 40.0    # 4040 profile cross-section (square)

# --- V-slot engaging rails on the side piece -----------------------------
# Two arrow-shaped rails on the outer face of each side wall, running
# the full Y depth. Each rail has a rectangular tongue that passes
# through the V-slot neck, followed by a pentagonal foot: a short flat
# back at chamber width (11 mm) immediately past the neck, then
# tapering walls that narrow to a point at the chamber back.
# RAIL_SPACING is the Z-centre-to-Z-centre distance between the two
# rails and must match the V-slot spacing on the mating profile face.
RAIL_SPACING       = 20.0   # placeholder - measure against the actual frame
RAIL_CLEARANCE     =  0.3   # slack on rail width so it slides in smoothly
RAIL_FOOT_FLAT_DEP =  1.25  # depth of the foot's flat-back portion (past neck)

# --- Misc ----------------------------------------------------------------
EPS = 0.1   # small overshoot for boolean cuts to avoid coincident faces
