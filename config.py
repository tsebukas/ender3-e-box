"""
Shared configuration for every part of the Ender 3 Pro e-box project.

Every part module imports from here so the whole enclosure stays
dimensionally consistent. Do not hard-code geometry numbers inside the
part modules - extend this file instead.

Global coordinate frame (used by every part and by the assembly):

    +X : horizontal along the printer width  (BOX_WIDTH  = 250 mm)
    +Y : horizontal depth into the printer   (BOX_DEPTH  = 120 mm)
    +Z : vertical, up                        (BOX_HEIGHT =  40 mm)

The enclosure is mounted flush with a 4040 V-slot profile, so the
vertical size BOX_HEIGHT is fixed at 40 mm to match the profile.
"""

# --- Enclosure outer envelope --------------------------------------------
BOX_WIDTH  = 250.0   # X, along printer width
BOX_DEPTH  = 120.0   # Y, horizontal depth into the printer
BOX_HEIGHT =  40.0   # Z, matches 4040 profile cross-section

# The Y-axis carrier (a 4040 profile sitting on top of the H middle bar
# at X = BOX_WIDTH / 2, running along Y) is sunk Y_CARRIER_RECESS into
# the middle bar. The centre divider mirrors that: it sinks the carrier
# the same depth into its own top, so the divider's working height
# matches BOX_HEIGHT (40 mm) and its lid groove lines up with the side
# pieces' lid grooves. CENTER_HEIGHT is the Z of the carrier-pocket
# floor (the surface the top rails sprout from).
Y_CARRIER_RECESS = 6.75
CENTER_HEIGHT    = BOX_HEIGHT - Y_CARRIER_RECESS   # 33.25 mm
# CENTER_TOP_WIDTH is computed below, after PROFILE_SIZE and
# FLANGE_WIDTH are introduced.

# --- Wall and integrated flange stock ------------------------------------
WALL_THK     = 2.0    # nominal side wall thickness
FLANGE_WIDTH = 6.0   # how far each integrated flange extends into the box (X)
FLANGE_THK   = 4.0    # flange thickness, deep enough to host the slide-in groove

# --- Sliding panels and grooves ------------------------------------------
PANEL_THK    = 2.0                # nominal thickness of bottom/lid/front panels
GROOVE_SLOT  = PANEL_THK + 0.3    # slot opening perpendicular to the panel face
GROOVE_DEPTH = 5.0                # how far the groove bites into the flange (X)

# --- Cosmetic / stress-relief fillets ------------------------------------
INSIDE_FILLET_R  = 1.0   # radius on the interior edges where wall meets flanges
OUTSIDE_FILLET_R = 2.0   # radius on the exterior edges of the front plate / cap

# --- Threaded heat insert mounting bosses --------------------------------
# Bosses extrude from a panel's INNER face to receive a metric threaded
# heat insert. The boss is a TRUNCATED CONE (frustum): wider at the
# panel root (BOSS_BASE_OD) and narrower at the outer face
# (BOSS_TOP_OD), giving the boss a stiffening flare without bulking up
# the seat surface. A coaxial blind hole (HOLE_DIA / HOLE_DEPTH) is
# drilled from the boss outer face inward; HOLE_DEPTH is 1 mm greater
# than BOSS_HEIGHT so the insert sinks 1 mm into the panel body for a
# flush seat. Shared across every panel that hosts inserts.
HEAT_INSERT_BOSS_TOP_OD  = 7.0    # foot outer diameter at the boss outer face
HEAT_INSERT_BOSS_BASE_OD = 10.0   # foot outer diameter at the panel inner face
HEAT_INSERT_BOSS_HEIGHT  = 3.0    # foot height above the panel inner face
HEAT_INSERT_HOLE_DIA     = 4.0    # blind hole diameter (insert outer dia)
HEAT_INSERT_HOLE_DEPTH   = 4.0    # blind hole depth (1 mm past boss base into panel)

# --- Printer frame profile -----------------------------------------------
PROFILE_SIZE = 40.0   # 4040 aluminium profile cross-section (square)

# Width of the divider's wide top section (ceiling + side wall + front
# flange halves spanning across the carrier pocket). Each side carries
# a FLANGE_WIDTH lid/front flange plus a WALL_THK side wall that drops
# from the ceiling down to the pocket floor, anchoring the flange so
# it doesn't cantilever in mid-air. Bottom of the divider stays at the
# original narrow stem width (2 * FLANGE_WIDTH + WALL_THK).
CENTER_TOP_WIDTH = PROFILE_SIZE + 2 * FLANGE_WIDTH + 2 * WALL_THK   # 56 mm
CENTER_DEPTH = 125.0
CENTER_TAIL = 10.0

# --- V-slot profile reference (from lahteylesanne/4040_v-slot.jpg) -------
# The 4040 profile's face carries TWO V-slots (not the single V-slot of
# a standard 4040). Each V-slot opens through a narrow NECK into a
# wider inner chamber. The chamber stays at full width for a short
# depth past the neck (VSLOT_CHAMBER_FLAT_DEPTH), then tapers to a
# narrower flat back wall.
#
# VSLOT_SPACING is the Z-centre-to-Z-centre distance between the two
# V-slots on the profile face; each side piece's two T-rails must match
# it. VSLOT_CLEARANCE is slack applied to the mating rail cross-section
# so it slides into the V-slot smoothly.
VSLOT_SPACING            = 20.0   # Z centre-to-centre of the two V-slots (placeholder - measure on printer)
VSLOT_NECK_WIDTH         =  6.1   # neck opening width (between outer face and chamber)
VSLOT_NECK_DEPTH         =  2.0   # neck depth (outer face -> chamber front = outer lip thickness)
VSLOT_CHAMBER_WIDTH      = 10.3   # chamber width at its widest, right past the neck
VSLOT_CHAMBER_BACK_WIDTH =  6.1   # chamber back wall width (estimated, not on drawing)
VSLOT_CHAMBER_FLAT_DEPTH =  1.7   # how far past the neck the chamber stays at full width before tapering
VSLOT_POCKET_DEPTH       =  6.1   # outer face -> chamber back wall (total pocket depth, neck + chamber)
VSLOT_CLEARANCE          =  0.3   # slack on the mating rail so it slides in smoothly

# --- Output controls (for each part module's __main__ block) ------------
# Toggle what a direct `py <part>.py` run produces. Part modules check
# these flags before exporting or previewing. Keep all three ON during
# interactive design; flip to OFF (e.g. in CI or batch builds) to skip
# file writes or the viewer call.
EXPORT_STEP    = False   # write STEP to build/<part>.step (for assembly review)
EXPORT_STL     = True   # write STL to build/<part>.stl (for slicing)
SHOW_IN_VIEWER = True   # call ocp_vscode.show() to preview in OCP CAD Viewer

# --- Misc ----------------------------------------------------------------
EPS = 0.1   # small overshoot for boolean cuts to avoid coincident faces
