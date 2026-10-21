import bpy
import bmesh
import math
import sys
from mathutils import Vector, Euler, Matrix

sys.path.insert(0, "C:/argon/bowling")
sys.path.insert(0, "C:/argon/rapa_nui")
from bowling_utils import (
    PALETTE, init_scene, make_empty, add_box, add_weighted_box,
    add_weighted_tube, add_uv_screen_quad, apply_screen_uvs,
    create_rig, make_pose_helpers, finalize_rigged_mesh, save_and_export_bowling
)

# Standard 10-pin equilateral triangle offsets relative to Head-Pin (Pin 1 at (0, 0)):
# Regulation 12-inch (0.3048 m) center-to-center spacing; row depth = 0.3048 * sin(60°) = 0.2640 m
HEAD = 18.288            # foul line to the head pin's spot: 60 ft (USBC regulation)
DECK = 0.8684            # head pin's spot to the pit: 34 3/16 in
KICK = 1.5272 / 2        # the kickbacks' wood faces: 60 1/8 in apart
CUSHION = 0.635          # a free-fall machine's cushion: at least 25 in past the end of the lane
PIT_DROP = 0.1207        # the pit floor at least 4 3/4 in below the deck
BOARD = 1.067 / 39       # a board's width
BACK = HEAD + 1.70       # the alley's back wall: 1.70 m past the head pin

ROW_DY = 0.2640
COL_DX = 0.1524
PIN_TRIANGLE_OFFSETS = [
    (1,  0.0 * COL_DX, 0.0 * ROW_DY),  # Row 1: Pin 1 (Head-pin)
    (2, -1.0 * COL_DX, 1.0 * ROW_DY),  # Row 2: Pin 2, 3
    (3,  1.0 * COL_DX, 1.0 * ROW_DY),
    (4, -2.0 * COL_DX, 2.0 * ROW_DY),  # Row 3: Pin 4, 5, 6
    (5,  0.0 * COL_DX, 2.0 * ROW_DY),
    (6,  2.0 * COL_DX, 2.0 * ROW_DY),
    (7, -3.0 * COL_DX, 3.0 * ROW_DY),  # Row 4: Pin 7, 8, 9, 10
    (8, -1.0 * COL_DX, 3.0 * ROW_DY),
    (9,  1.0 * COL_DX, 3.0 * ROW_DY),
    (10, 3.0 * COL_DX, 3.0 * ROW_DY),
]


# ==============================================================================
# 1. cozy_bowling_mall_shell (3-Bay Aquarium Mall Storefront & Regulation 60ft Interior Alley)
# ==============================================================================
def build_mall_shell():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    DEPTH = BACK + 4.50
    CY = (BACK - 4.50) / 2
    DOOR_CX = 0.25  # Center of Bay 2 ("Sugarplum", mall x = +3.00 m, clear of the x=0 atrium column!)
    bone_specs = [
        ("Root",        ( 0.00,  0.00, 0.00), ( 0.00, -0.20, 0.00), None),
        ("Door_L",      (DOOR_CX - 1.30, -4.50, 0.00), (DOOR_CX - 1.30, -4.50, 2.55), "Root"),
        ("Door_R",      (DOOR_CX + 1.30, -4.50, 0.00), (DOOR_CX + 1.30, -4.50, 2.55), "Root"),
        ("Marquee_Pin", (DOOR_CX - 0.35, -4.72, 3.35), (DOOR_CX - 0.15, -4.72, 4.15), "Root"),
        ("Marquee_Ball",(DOOR_CX + 0.42, -4.74, 3.45), (DOOR_CX + 0.42, -4.74, 3.85), "Root"),
        ("Starburst_L", (DOOR_CX - 1.95, -4.68, 3.75), (DOOR_CX - 1.95, -4.82, 3.75), "Root"),
        ("Starburst_R", (DOOR_CX + 1.95, -4.68, 3.75), (DOOR_CX + 1.95, -4.82, 3.75), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    mats = [
        "Bowling_Mall_Wall", "Bowling_Mall_Floor", "Bowling_Coral_Pink",
        "Bowling_Teal_Seafoam", "Bowling_Maple_Light", "Bowling_Gold_Brass",
        "Bowling_Glass_Tint", "Bowling_Cream_Pearl", "Bowling_Crimson_Stripe",
        "Bowling_Walnut_Dark"
    ]

    # Floor slab across the 16.50 m x 24.49 m interior (open over the two pits, which sink below it):
    add_weighted_box(bm, deform, (-5.175, CY, -0.04), 6.15, DEPTH, 0.08, mat_idx=1, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 5.175, CY, -0.04), 6.15, DEPTH, 0.08, mat_idx=1, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.00, -3.975, -0.04), 4.20,  1.05, 0.08, mat_idx=1, vg_idx=b_idx["Root"])
    PIT_FROM, PIT_TO = HEAD + DECK, HEAD + DECK + CUSHION
    add_weighted_box(bm, deform, ( 0.00, (PIT_FROM - 3.45) / 2, -0.065), 4.20, PIT_FROM + 3.45, 0.06, mat_idx=9, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.00, (PIT_FROM + PIT_TO) / 2, -0.065), 0.60, PIT_TO - PIT_FROM, 0.06, mat_idx=9, vg_idx=b_idx["Root"])
    for sx in (-1.0, 1.0):
        add_weighted_box(bm, deform, (sx * 2.04, (PIT_FROM + PIT_TO) / 2, -0.065), 0.12, PIT_TO - PIT_FROM, 0.06, mat_idx=9, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.00, (PIT_TO + BACK) / 2, -0.065), 4.20, BACK - PIT_TO, 0.06, mat_idx=9, vg_idx=b_idx["Root"])

    # Back wall (Y = BACK, width = 16.50 m, height = 4.20 m) and Left/Right perimeter walls (X = -8.25 m, X = +8.25 m)
    add_weighted_box(bm, deform, ( 0.00, BACK, 2.10), 16.50, 0.20, 4.20, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.00, BACK - 0.12, 2.95), 15.90, 0.04, 0.60, mat_idx=3, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.00, BACK - 0.14, 2.50), 15.90, 0.04, 0.28, mat_idx=2, vg_idx=b_idx["Root"])

    # Side walls with warm maple Wainscoting (lower 1.25 m in Maple Light, upper in Mall Wall)
    for sx in (-1.0, 1.0):
        wx = sx * 8.25
        add_weighted_box(bm, deform, (wx, CY, 2.10), 0.20, DEPTH, 4.20, mat_idx=0, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (wx - sx * 0.11, CY, 0.625), 0.04, DEPTH - 0.30, 1.25, mat_idx=4, vg_idx=b_idx["Root"])

    # Ceiling slab at Z = 4.20 m (matching SHOP.h = 4.20 m) + 8 rows of acoustic wood-slat baffles & lamps every 3 m
    add_weighted_box(bm, deform, (0.00, CY, 4.16), 16.50, DEPTH, 0.08, mat_idx=0, vg_idx=b_idx["Root"])
    slat_y = -2.5
    while slat_y < BACK - 1.0:
        add_weighted_box(bm, deform, (0.00, slat_y, 4.02), 15.90, 0.22, 0.14, mat_idx=4, vg_idx=b_idx["Root"])
        for lx in (-5.0, 0.0, 5.0):
            add_weighted_tube(bm, deform, [
                ((lx, slat_y, 4.02), 0.015),
                ((lx, slat_y, 3.55), 0.015),
                ((lx, slat_y, 3.46), 0.150),
                ((lx, slat_y, 3.32), 0.150),
                ((lx, slat_y, 3.24), 0.045),
            ], sides=8, mat_idx=5, mat_end_idx=7, vg_idx=b_idx["Root"])
        slat_y += 3.0

    # 3-Bay Mall Storefront at Y = -4.50 m matching atrium-shops.ts & atrium-tank.ts:
    # Outer edge pilasters (0.30 m wide) and exact interior piers:
    #   - Left outer pilaster: X = -8.10 (width 0.30)
    #   - Pier 1-2 (between Bay 1 & Bay 2): X = -2.75 (width 1.00, matching mall x in [-0.5, +0.5])
    #   - Pier 2-3 (between Bay 2 & Bay 3): X = +3.00 (width 0.50, matching mall x in [+5.5, +6.0])
    #   - Right outer pilaster: X = +8.10 (width 0.30)
    for px, pw in [(-8.10, 0.30), (-2.75, 1.00), (3.00, 0.50), (8.10, 0.30)]:
        add_weighted_box(bm, deform, (px, -4.50, 2.10), pw, 0.36, 4.20, mat_idx=0, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (px, -4.69, 2.10), pw * 0.65, 0.04, 3.96, mat_idx=5, vg_idx=b_idx["Root"])

    # Continuous upper storefront fascia header (Z = 3.30 to 4.20 m = SHOP.ceiling to SHOP.h) across all 3 bays (16.50 m)
    add_weighted_box(bm, deform, ( 0.00, -4.50, 3.75), 16.50, 0.30, 0.90, mat_idx=0, vg_idx=b_idx["Root"])
    # Cornice molding at top of fascia (Z = 4.12 to 4.20 m, matching atrium-shops.ts line 102)
    add_weighted_box(bm, deform, ( 0.00, -4.54, 4.16), 16.60, 0.38, 0.08, mat_idx=7, vg_idx=b_idx["Root"])
    # Bay 1 Fascia Panel (X = -5.75, 5.0 m wide, Coral Pink), Bay 2 Center Sign Panel (X = +0.25, 5.0 m wide, Teal Seafoam),
    # Bay 3 Fascia Panel (X = +5.75, 5.0 m wide, Coral Pink)
    add_weighted_box(bm, deform, (-5.75, -4.66, 3.72), 4.70, 0.08, 0.68, mat_idx=2, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.25, -4.68, 3.72), 4.80, 0.10, 0.74, mat_idx=3, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 5.75, -4.66, 3.72), 4.70, 0.08, 0.68, mat_idx=2, vg_idx=b_idx["Root"])
    # Gold brass fascia border frames & under-fascia lit strip at Z = 3.28 m
    add_weighted_box(bm, deform, ( 0.00, -4.70, 3.34), 16.10, 0.06, 0.05, mat_idx=5, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.00, -4.70, 4.10), 16.10, 0.06, 0.05, mat_idx=5, vg_idx=b_idx["Root"])

    # Bay 1 (X = -5.75) & Bay 3 (X = +5.75) Mullioned Display Windows (4.70 m clear width, stallriser Z = 0..0.42 m, glass Z = 0.42..3.30 m)
    for bay_cx in (-5.75, 5.75):
        # Stone stallriser bulkhead (Z = 0.0 to 0.42 m, matching SHOP stallriser = 0.42 m)
        add_weighted_box(bm, deform, (bay_cx, -4.50, 0.21), 4.70, 0.24, 0.42, mat_idx=0, vg_idx=b_idx["Root"])
        # Tinted window glass pane (Z = 0.42 to 3.28 m)
        add_weighted_box(bm, deform, (bay_cx, -4.50, 1.85), 4.64, 0.04, 2.86, mat_idx=6, vg_idx=b_idx["Root"])
        # Horizontal transom bar at Z = 2.55 m (matching atrium-shops.ts line 114)
        add_weighted_box(bm, deform, (bay_cx, -4.50, 2.55), 4.68, 0.08, 0.06, mat_idx=9, vg_idx=b_idx["Root"])
        # Vertical mullions dividing each 5.0 m bay window into 3 panes
        for mx in (-1.55, 0.0, 1.55):
            add_weighted_box(bm, deform, (bay_cx + mx, -4.50, 1.85), 0.06, 0.09, 2.86, mat_idx=9, vg_idx=b_idx["Root"])

    # Bay 2 (Center Bay, X = +0.25, clear span X = -2.25 to +2.75) Side Sidelight Windows + Swinging Double Glass Doors:
    for side_s, side_cx in [(-1.0, DOOR_CX - 1.90), (1.0, DOOR_CX + 1.90)]:
        add_weighted_box(bm, deform, (side_cx, -4.50, 0.21), 1.15, 0.24, 0.42, mat_idx=0, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (side_cx, -4.50, 1.85), 1.10, 0.04, 2.86, mat_idx=6, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (side_cx, -4.50, 2.55), 1.15, 0.08, 0.06, mat_idx=9, vg_idx=b_idx["Root"])
    # Full-height vertical walnut/bronze jamb posts flanking the double doors (Z = 0.00 to 3.30 m)
    for jx in (DOOR_CX - 1.32, DOOR_CX + 1.32):
        add_weighted_box(bm, deform, (jx, -4.50, 1.65), 0.07, 0.12, 3.30, mat_idx=9, vg_idx=b_idx["Root"])
    # Transom glass above Center Double Doors (Z = 2.55 to 3.28 m)
    add_weighted_box(bm, deform, (DOOR_CX, -4.50, 2.55), 2.64, 0.08, 0.06, mat_idx=9, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (DOOR_CX, -4.50, 2.92), 2.58, 0.04, 0.72, mat_idx=6, vg_idx=b_idx["Root"])

    # Center Bay Swinging Double Glass Doors (`Door_L` and `Door_R` centered at DOOR_CX = +0.25 m, Z = 0.0 to 2.55 m)
    for d_side, d_bone, hinge_x in [(-1.0, "Door_L", DOOR_CX - 1.30), (1.0, "Door_R", DOOR_CX + 1.30)]:
        cx = hinge_x - d_side * 0.64
        # Door frame & glass
        add_weighted_box(bm, deform, (cx, -4.50, 1.27), 1.26, 0.05, 2.52, mat_idx=6, vg_idx=b_idx[d_bone])
        add_weighted_box(bm, deform, (cx, -4.50, 0.12), 1.28, 0.07, 0.24, mat_idx=5, vg_idx=b_idx[d_bone])
        add_weighted_box(bm, deform, (cx, -4.50, 2.46), 1.28, 0.07, 0.12, mat_idx=5, vg_idx=b_idx[d_bone])
        # Brass vertical push/pull handle bar (matching atrium-shops.ts long bronze pulls)
        hx = hinge_x - d_side * 1.12
        add_weighted_box(bm, deform, (hx, -4.56, 1.10), 0.03, 0.08, 0.85, mat_idx=5, vg_idx=b_idx[d_bone])

    # 3D Rooftop Marquee Sign above Center Bay Entrance (DOOR_CX = +0.25 m):
    # 1. Giant 1.1 m 3D Tilted Bowling Pin (`Marquee_Pin`)
    pin_pts = [
        ((DOOR_CX - 0.38, -4.82, 3.35), 0.09),
        ((DOOR_CX - 0.34, -4.82, 3.58), 0.18),
        ((DOOR_CX - 0.29, -4.82, 3.82), 0.14),
        ((DOOR_CX - 0.25, -4.82, 4.00), 0.08),
        ((DOOR_CX - 0.22, -4.82, 4.14), 0.11),
        ((DOOR_CX - 0.19, -4.82, 4.26), 0.09),
        ((DOOR_CX - 0.17, -4.82, 4.32), 0.03),
    ]
    pin_rings = add_weighted_tube(bm, deform, pin_pts, sides=10, mat_idx=7, vg_idx=b_idx["Marquee_Pin"])
    # Red neck stripe on Marquee Pin
    r_neck_a, r_neck_b = set(pin_rings[2]), set(pin_rings[3])
    for f in bm.faces:
        if all(v in r_neck_a or v in r_neck_b for v in f.verts):
            f.material_index = 8

    # 2. Giant 3D Coral Bowling Ball (`Marquee_Ball`) crashing toward the Marquee Pin
    ball_c = Vector((DOOR_CX + 0.42, -4.84, 3.72))
    add_weighted_tube(bm, deform, [
        (ball_c + Vector((0, 0, -0.24)), 0.06),
        (ball_c + Vector((0, 0, -0.18)), 0.19),
        (ball_c + Vector((0, 0,  0.00)), 0.25),
        (ball_c + Vector((0, 0,  0.18)), 0.19),
        (ball_c + Vector((0, 0,  0.24)), 0.06),
    ], sides=12, mat_idx=2, vg_idx=b_idx["Marquee_Ball"])

    # 3. Left & Right Mid-Century Golden Starbursts (`Starburst_L`, `Starburst_R`)
    for sb_x, sb_bone in [(DOOR_CX - 1.95, "Starburst_L"), (DOOR_CX + 1.95, "Starburst_R")]:
        for ray_i in range(4):
            ang = ray_i * 45.0
            add_weighted_box(bm, deform, (sb_x, -4.74, 3.75), 0.46, 0.04, 0.07, mat_idx=5, vg_idx=b_idx[sb_bone], rot_deg=(0.0, ang, 0.0))

    rig_obj, rest_mat = create_rig("Shell_Rig", bone_specs)
    finalize_rigged_mesh("Shell_Mesh", bm, rig_obj, bone_specs, mats)

    # Placement empties for all interior zones & 18 decorative props (with regulation 60ft offsets)
    make_empty("Lane_1_Origin",          (-1.15,  0.00, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Lane_2_Origin",          ( 1.15,  0.00, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Ball_Return_Origin",     ( 0.00, -0.85, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Scoreboard_Origin",      ( 0.00,  1.80, 2.85), parent=rig_obj, bone_parent="Root")
    make_empty("Lounge_Origin",          (-5.40, -1.45, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Counter_Origin",         ( 5.40, -1.60, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Arcade_Origin",          ( 6.60,  1.60, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Trophy_Case_Origin",     ( 7.65, -0.20, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Ball_Rack_Origin",       (-2.85, -1.20, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Chalk_Pedestal_Origin",  ( 0.00, -2.55, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Leaderboard_Origin",     (-8.05,  3.20, 1.45), parent=rig_obj, bone_parent="Root")
    make_empty("Oiler_Cart_Origin",      ( 3.10,  HEAD, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Snack_Tray_Origin",      (-4.95, -1.45, 0.57), parent=rig_obj, bone_parent="Root")
    make_empty("Popcorn_Cart_Origin",    (-7.35, -0.40, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Slushie_Machine_Origin", ( 4.65, -1.92, 0.96), parent=rig_obj, bone_parent="Root")
    make_empty("Condiment_Caddy_Origin", (-4.95, -1.90, 0.57), parent=rig_obj, bone_parent="Root")
    make_empty("Trash_Duo_Origin",       (-3.55, -3.60, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Jukebox_Origin",         (-7.35,  1.80, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Bill_Changer_Origin",    ( 7.55,  2.55, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Gumball_Rack_Origin",    ( 2.15, -3.85, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Arcade_Stools_Origin",   ( 5.75,  1.60, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Neon_Signs_Origin",      ( 8.05,  4.80, 2.25), parent=rig_obj, bone_parent="Root")
    make_empty("Sputnik_Clock_Origin",   ( 0.00, BACK - 0.18, 3.55), parent=rig_obj, bone_parent="Root")
    make_empty("Planter_Divider_Origin", (-5.40, -2.88, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Window_Podium_Origin",   (-5.75, -3.75, 0.00), parent=rig_obj, bone_parent="Root")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Marquee_Idle_Bob (60f loop: starbursts spin 180 deg, marquee pin & ball bob playfully)
    act_idle = bpy.data.actions.new(name="Marquee_Idle_Bob")
    act_idle.use_fake_user = True
    rig_obj.animation_data.action = act_idle
    for f, r_star, p_bob, dz in [
        (1,    0.0,  0.0, 0.00),
        (15,  45.0,  6.0, 0.05),
        (30,  90.0,  0.0, 0.00),
        (45, 135.0, -6.0, 0.05),
        (60, 180.0,  0.0, 0.00),
    ]:
        key_frame(f, rot_map={
            "Marquee_Pin":  (0.0, p_bob, 0.0),
            "Marquee_Ball": (0.0, -p_bob * 1.5, 0.0),
            "Starburst_L":  (0.0, r_star, 0.0),
            "Starburst_R":  (0.0, -r_star, 0.0),
        }, loc_map={
            "Marquee_Ball": (0.0, 0.0, dz),
        })

    # 2. Entrance_Doors_Swing (45f: double doors swing open 85° into the alley and close)
    act_doors = bpy.data.actions.new(name="Entrance_Doors_Swing")
    act_doors.use_fake_user = True
    rig_obj.animation_data.action = act_doors
    for f, yaw_d in [(1, 0.0), (15, 85.0), (30, 85.0), (45, 0.0)]:
        key_frame(f, rot_map={
            "Door_L": (0.0, 0.0, -yaw_d),
            "Door_R": (0.0, 0.0,  yaw_d),
        })

    save_and_export_bowling("cozy_bowling_mall_shell", animated=True)


# ==============================================================================
# 2. cozy_bowling_lane (Regulation 60ft / 18.288m Roll Lane + Deck + Bumpers)
# ==============================================================================
def build_bowling_lane():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    END = HEAD + DECK
    KICK_FROM = HEAD - 0.30
    BUMP_TO = HEAD - 0.40
    bone_specs = [
        ("Root",       ( 0.000, 0.00,  0.00), ( 0.000, -0.20, 0.00), None),
        ("Bumper_L",   (-0.640, 0.20, -0.02), (-0.640, BUMP_TO - 0.10, -0.02), "Root"),
        ("Bumper_R",   ( 0.640, 0.20, -0.02), ( 0.640, BUMP_TO - 0.10, -0.02), "Root"),
        ("Foul_Light", (-0.780, 0.00,  0.10), (-0.780,  0.00,  0.22), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    mats = [
        "Bowling_Maple_Light", "Bowling_Maple_Amber", "Bowling_Walnut_Dark",
        "Bowling_Gutter_Slate", "Bowling_Bumper_Yellow", "Bowling_Chrome_Steel",
        "Bowling_Foul_Red"
    ]

    # 1. Lane Bed made of 9 alternating blonde maple & warm amber plank strips
    strip_w = 1.067 / 9.0
    for s_i in range(9):
        sx_center = -0.5335 + (s_i + 0.5) * strip_w
        m_plank = 0 if (s_i % 2 == 0) else 1
        add_weighted_box(bm, deform, (sx_center, -1.76, -0.02), strip_w, 3.48, 0.04, mat_idx=0, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (sx_center, (0.02 + END) / 2, -0.02), strip_w, END - 0.02, 0.04, mat_idx=m_plank, vg_idx=b_idx["Root"])

    # 2. Dark Walnut Foul Line Strip at Y = 0.00 m
    add_weighted_box(bm, deform, (0.0, 0.00, -0.019), 1.067, 0.04, 0.042, mat_idx=2, vg_idx=b_idx["Root"])

    # 3. Approach Alignment Dots
    for dy in (-0.15, -3.00, -3.40):
        for dx in (-0.36, -0.24, -0.12, 0.0, 0.12, 0.24, 0.36):
            add_weighted_box(bm, deform, (dx, dy, 0.001), 0.022, 0.022, 0.002, mat_idx=2, vg_idx=b_idx["Root"])

    # 4. Seven Inlaid Chevron Aiming Arrows on boards 5, 10, 15, 20, 25, 30, 35 (12 ft to 16 ft past foul line)
    FT = 0.3048
    arrow_specs = [(k * 5 * BOARD, (12 + (3 - abs(k)) * 4.0 / 3) * FT) for k in (-3, -2, -1, 0, 1, 2, 3)]
    for ax, ay in arrow_specs:
        add_weighted_tube(bm, deform, [
            ((ax, ay - 0.12, 0.001), 0.016, 0.002),
            ((ax, ay + 0.06, 0.001), 0.024, 0.002),
            ((ax, ay + 0.18, 0.001), 0.002, 0.002),
        ], sides=4, mat_idx=2, vg_idx=b_idx["Root"])

    # 5. Ten Inlaid Pin-Spot Discs on the Pin Deck (Pin 1 at Y = HEAD = 18.288 m)
    for p_num, pdx, pdy in PIN_TRIANGLE_OFFSETS:
        py = HEAD + pdy
        add_weighted_tube(bm, deform, [
            ((pdx, py, 0.000), 0.028),
            ((pdx, py, 0.002), 0.028),
        ], sides=8, mat_idx=2, vg_idx=b_idx["Root"])

    # 6. Full-Width Approach Side Wings + Solid U-Channel Gutters (Y = 0.00 to END) + Capping Rail to Kickbacks
    for g_side in (-1.0, 1.0):
        gx = g_side * 0.650
        add_weighted_box(bm, deform, (gx, -1.75, -0.02), 0.233, 3.50, 0.04, mat_idx=0, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (gx, END / 2, -0.055), 0.233, END, 0.02, mat_idx=3, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (g_side * 0.543, END / 2, -0.025), 0.020, END, 0.05, mat_idx=3, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (g_side * 0.756, END / 2, -0.025), 0.020, END, 0.05, mat_idx=3, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (g_side * 0.785, (KICK_FROM - 3.50) / 2, -0.01), 0.04, KICK_FROM + 3.50, 0.06, mat_idx=1, vg_idx=b_idx["Root"])

    # 7. Foul-Line Infrared Sensor Unit & Strobe Light
    add_weighted_box(bm, deform, (-0.785, 0.00, 0.05), 0.07, 0.14, 0.08, mat_idx=5, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.785, 0.00, 0.05), 0.07, 0.14, 0.08, mat_idx=5, vg_idx=b_idx["Root"])
    add_weighted_tube(bm, deform, [
        ((-0.785, 0.00, 0.09), 0.024),
        ((-0.785, 0.00, 0.14), 0.020),
    ], sides=8, mat_idx=6, vg_idx=b_idx["Foul_Light"])

    # 8. Pop-Up Gutter Bumpers (Y = +0.25 to BUMP_TO, with 6 struts evenly along)
    for b_side, b_name in [(-1.0, "Bumper_L"), (1.0, "Bumper_R")]:
        bx = b_side * 0.575
        add_weighted_box(bm, deform, (bx, (0.25 + BUMP_TO) / 2, -0.018), 0.032, BUMP_TO - 0.25, 0.062, mat_idx=4, vg_idx=b_idx[b_name])
        for i in range(6):
            strut_y = 1.0 + i * (BUMP_TO - 1.2) / 5
            add_weighted_box(bm, deform, (bx, strut_y, -0.042), 0.022, 0.06, 0.045, mat_idx=5, vg_idx=b_idx[b_name])

    rig_obj, rest_mat = create_rig("Lane_Rig", bone_specs)
    for f in bm.faces:
        if f.material_index == 2:
            avg_z = sum(v.co.z for v in f.verts) / len(f.verts)
            if avg_z > -0.005 and f.normal.z < -0.5:
                f.normal_flip()
    finalize_rigged_mesh("Lane_Mesh", bm, rig_obj, bone_specs, mats)

    make_empty("Foul_Line_Center", (0.0, 0.00, 0.0), parent=rig_obj, bone_parent="Root")
    make_empty("Arrow_Aim_Center", (0.0, 14 * FT, 0.0), parent=rig_obj, bone_parent="Root")
    make_empty("Pin_Deck_End",     (0.0, END, 0.0), parent=rig_obj, bone_parent="Root")
    for p_num, pdx, pdy in PIN_TRIANGLE_OFFSETS:
        make_empty(f"Pin_Spot_{p_num}", (pdx, HEAD + pdy, 0.0), parent=rig_obj, bone_parent="Root")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    act_up = bpy.data.actions.new(name="Bumpers_Pop_Up")
    act_up.use_fake_user = True
    rig_obj.animation_data.action = act_up
    for f, dz in [(1, 0.000), (18, 0.095), (24, 0.084), (30, 0.088)]:
        key_frame(f, loc_map={"Bumper_L": (0.0, 0.0, dz), "Bumper_R": (0.0, 0.0, dz)})

    act_down = bpy.data.actions.new(name="Bumpers_Retract")
    act_down.use_fake_user = True
    rig_obj.animation_data.action = act_down
    for f, dz in [(1, 0.088), (10, 0.094), (30, 0.000)]:
        key_frame(f, loc_map={"Bumper_L": (0.0, 0.0, dz), "Bumper_R": (0.0, 0.0, dz)})

    act_foul = bpy.data.actions.new(name="Foul_Light_Flash")
    act_foul.use_fake_user = True
    rig_obj.animation_data.action = act_foul
    for f, dz, yaw in [(1, 0.0, 0.0), (6, 0.08, 90.0), (12, 0.02, 180.0), (18, 0.08, 270.0), (24, 0.0, 360.0)]:
        key_frame(f, rot_map={"Foul_Light": (0.0, 0.0, yaw)}, loc_map={"Foul_Light": (0.0, 0.0, dz)})

    save_and_export_bowling("cozy_bowling_lane", animated=True)


# ==============================================================================
# 3. cozy_bowling_pinsetter (Regulation Kickbacks 60 1/8 in apart, Free-Fall Pit & Cushion)
# ==============================================================================
def build_pinsetter():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    FACE = DECK + CUSHION + 0.002
    REAR = FACE + 0.08
    FRONT = -0.30
    bone_specs = [
        ("Root",         (0.0,  0.50, 0.00), (0.0,  0.30, 0.00), None),
        ("Sweep_Rake",   (0.0, -0.22, 0.56), (0.0, -0.22, 0.18), "Root"),
        ("Spotter_Rack", (0.0,  0.42, 0.72), (0.0,  0.42, 1.05), "Root"),
        ("Pit_Curtain",  (0.0,  1.15, 0.68), (0.0,  1.15, 0.08), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    mats = [
        "Bowling_Teal_Seafoam", "Bowling_Coral_Pink", "Bowling_Cream_Pearl",
        "Bowling_Chrome_Steel", "Bowling_Obsidian_Ball", "Bowling_Gold_Brass"
    ]

    # 1. Machine Housing Frame (`Root`): side cowls and dark kickback faces 60 1/8 in apart
    for sx in (-1.0, 1.0):
        add_weighted_box(bm, deform, (sx * (KICK + 0.03 + 0.05), (FRONT + REAR) / 2, 0.725), 0.10, REAR - FRONT, 1.45, mat_idx=0, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (sx * (KICK + 0.015), (FRONT + 0.03 + FACE) / 2, (1.40 - PIT_DROP) / 2), 0.03, FACE - FRONT - 0.03, 1.40 + PIT_DROP, mat_idx=4, vg_idx=b_idx["Root"])
    WIDE = 2 * (KICK + 0.13)

    # Top canopy hood & retro Coral/Teal front masking unit
    add_weighted_box(bm, deform, (0.0, (FRONT + REAR) / 2, 1.40), WIDE, REAR - FRONT, 0.10, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.28, 1.15), WIDE, 0.12, 0.55, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.34, 1.15), 1.46, 0.04, 0.36, mat_idx=2, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.35, 1.15), 1.38, 0.04, 0.14, mat_idx=1, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.36, 1.15), 0.42, 0.04, 0.08, mat_idx=5, vg_idx=b_idx["Root"])

    # Rear Pit Floor (4 3/4 in below deck) & Cushion Back Wall (`Root`)
    add_weighted_box(bm, deform, (0.0, (DECK + FACE) / 2, -PIT_DROP - 0.04), 2 * KICK, FACE - DECK, 0.08, mat_idx=4, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, (FACE + REAR) / 2, (1.425 - PIT_DROP) / 2), 2 * KICK, REAR - FACE, 1.425 + PIT_DROP, mat_idx=4, vg_idx=b_idx["Root"])

    # 2. Heavy Padded Rear Impact Curtain (`Pit_Curtain` bone at Y = +1.15 m)
    add_weighted_box(bm, deform, (0.0, 1.15, 0.38), 2 * KICK - 0.03, 0.06, 0.68, mat_idx=4, vg_idx=b_idx["Pit_Curtain"])
    add_weighted_box(bm, deform, (0.0, 1.12, 0.18), 2 * KICK - 0.07, 0.08, 0.22, mat_idx=3, vg_idx=b_idx["Pit_Curtain"])

    # 3. Chrome & Cream Sweep Rake Bar (`Sweep_Rake` bone)
    add_weighted_box(bm, deform, (0.0, -0.22, 0.78), 1.38, 0.06, 0.14, mat_idx=2, vg_idx=b_idx["Sweep_Rake"])
    add_weighted_box(bm, deform, (0.0, -0.25, 0.78), 1.34, 0.02, 0.06, mat_idx=1, vg_idx=b_idx["Sweep_Rake"])
    for rx in (-0.64, 0.64):
        add_weighted_tube(bm, deform, [
            ((rx, -0.22, 0.78), 0.022),
            ((rx, -0.22, 1.18), 0.022),
        ], sides=6, mat_idx=3, vg_idx=b_idx["Sweep_Rake"])

    # 4. Overhead 10-Pin Scissor Spotter Deck (`Spotter_Rack` bone)
    add_weighted_box(bm, deform, (0.0, 0.42, 0.78), 1.12, 0.92, 0.05, mat_idx=3, vg_idx=b_idx["Spotter_Rack"])
    for sx in (-0.38, 0.38):
        add_weighted_box(bm, deform, (sx, 0.42, 0.98), 0.04, 0.48, 0.36, mat_idx=3, vg_idx=b_idx["Spotter_Rack"])

    for p_num, pdx, pdy in PIN_TRIANGLE_OFFSETS:
        add_weighted_tube(bm, deform, [
            ((pdx, pdy, 0.76), 0.048),
            ((pdx, pdy, 0.66), 0.052),
        ], sides=8, mat_idx=5, vg_idx=b_idx["Spotter_Rack"])
        add_weighted_tube(bm, deform, [
            ((pdx, pdy, 0.66), 0.038),
            ((pdx, pdy, 0.54), 0.056),
        ], sides=8, mat_idx=2, vg_idx=b_idx["Spotter_Rack"])

    rig_obj, rest_mat = create_rig("Pinsetter_Rig", bone_specs)
    finalize_rigged_mesh("Pinsetter_Mesh", bm, rig_obj, bone_specs, mats)

    make_empty("Spotter_Center",   (0.0,  0.42, 0.72), parent=rig_obj, bone_parent="Spotter_Rack")
    make_empty("Rake_Edge",        (0.0, -0.22, 0.72), parent=rig_obj, bone_parent="Sweep_Rake")
    make_empty("Pit_Ball_Swallow", (0.0,  1.05, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Cushion_Face",     (0.0,  FACE, 0.00), parent=rig_obj, bone_parent="Root")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Pinsetter_Idle (60f loop: subtle mechanical hum & ready state)
    act_idle = bpy.data.actions.new(name="Pinsetter_Idle")
    act_idle.use_fake_user = True
    rig_obj.animation_data.action = act_idle
    key_frame(1,  loc_map={"Sweep_Rake": (0.0, 0.0, 0.000)})
    key_frame(30, loc_map={"Sweep_Rake": (0.0, 0.0, 0.012)})
    key_frame(60, loc_map={"Sweep_Rake": (0.0, 0.0, 0.000)})

    # 2. Sweep_Rake_Drop_And_Clear (60f: rake drops down -0.64m to lane, sweeps deadwood into pit, lifts, and returns forward)
    act_sweep = bpy.data.actions.new(name="Sweep_Rake_Drop_And_Clear")
    act_sweep.use_fake_user = True
    rig_obj.animation_data.action = act_sweep
    for f, r_dy, r_dz in [
        (1,  0.00,  0.00),  # Parked high at Z = 0.78m under front hood
        (10, 0.00, -0.64),  # Drops down to Z = 0.14m to guard lane
        (18, 0.00, -0.64),  # Pause while ball clears
        (38, 1.18, -0.64),  # Sweeps backward across entire pin deck into pit!
        (46, 1.18,  0.00),  # Lifts up at rear of deck
        (60, 0.00,  0.00),  # Returns forward to home position
    ]:
        key_frame(f, loc_map={"Sweep_Rake": (0.0, r_dy, r_dz)})

    # 3. Spotter_Set_New_Pins (55f: rake guards while Spotter_Rack lowers 10 fresh pins onto the deck and rises)
    act_spot = bpy.data.actions.new(name="Spotter_Set_New_Pins")
    act_spot.use_fake_user = True
    rig_obj.animation_data.action = act_spot
    for f, rake_dz, spot_dz in [
        (1,   0.00,  0.00),
        (8,  -0.64,  0.00),  # Rake drops to guard
        (24, -0.64, -0.52),  # Spotter rack lowers all the way down to pin deck!
        (34, -0.64, -0.52),  # Releases pins on spots
        (48,  0.00,  0.00),  # Both rake and spotter rack rise back up
        (55,  0.00,  0.00),
    ]:
        key_frame(f, loc_map={
            "Sweep_Rake":   (0.0, 0.0, rake_dz),
            "Spotter_Rack": (0.0, 0.0, spot_dz),
        })

    # 4. Pit_Curtain_Impact (30f: heavy rear curtain swings backward when hit by a fast ball & dampens)
    act_curtain = bpy.data.actions.new(name="Pit_Curtain_Impact")
    act_curtain.use_fake_user = True
    rig_obj.animation_data.action = act_curtain
    for f, pitch in [(1, 0.0), (4, -28.0), (10, 12.0), (16, -6.0), (22, 2.5), (30, 0.0)]:
        key_frame(f, rot_map={"Pit_Curtain": (pitch, 0.0, 0.0)})

    save_and_export_bowling("cozy_bowling_pinsetter", animated=True)


# ==============================================================================
# 6. cozy_bowling_ball_return (Shared Center Twin-Lane Ball Return Hood & Keypad)
# ==============================================================================
def build_ball_return():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    # Sits on the approach between Lane 1 and Lane 2.
    # Front hood faces -Y (towards the bowler on the approach), with the 8-ball rack extending from Y = -0.20 to -1.55 m,
    # and the control pedestal at the front (Y = -1.72 m).
    bone_specs = [
        ("Root",         ( 0.00,  0.00, 0.00), ( 0.00, -0.20, 0.00), None),
        ("Blower_Fan",   ( 0.00,  0.18, 0.52), ( 0.00,  0.18, 0.68), "Root"),
        ("Ball_Stopper", ( 0.00, -1.52, 0.44), ( 0.00, -1.62, 0.44), "Root"),
        ("Btn_Bumpers",  (-0.08, -1.72, 0.88), (-0.08, -1.72, 0.94), "Root"),
        ("Btn_Reset",    ( 0.08, -1.72, 0.88), ( 0.08, -1.72, 0.94), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Teal_Seafoam (#2D8A7E) - streamlined fiberglass hood
    # 1: Bowling_Coral_Pink (#E26A52) - side fins & reset button
    # 2: Bowling_Chrome_Steel (#C4CBD0) - tubular ball rails & trim
    # 3: Bowling_Obsidian_Ball (#1C2026) - underground tunnel mouth & rubber stopper
    # 4: Bowling_Gold_Brass (#D8A638) - blower grille & badge
    # 5: Bowling_Bumper_Yellow (#F2C138) - bumper toggle button
    mats = [
        "Bowling_Teal_Seafoam", "Bowling_Coral_Pink", "Bowling_Chrome_Steel",
        "Bowling_Obsidian_Ball", "Bowling_Gold_Brass", "Bowling_Bumper_Yellow"
    ]

    # 1. Full-Length Mid-Century Base Plinth (`Z = 0.00 to 0.14 m, Y = -1.62 to +0.50 m`) + Streamlined Googie Hood
    add_weighted_box(bm, deform, (0.0, -0.56, 0.07), 0.44, 2.12, 0.14, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.56, 0.02), 0.46, 2.14, 0.04, mat_idx=2, vg_idx=b_idx["Root"])
    # Sculpted flat-bottomed Brunswick-style teardrop cowl rising from Z = 0.14 to 0.66 m (`Y = -0.26 to +0.48 m`)
    add_weighted_box(bm, deform, (0.0,  0.11, 0.28), 0.46, 0.72, 0.28, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0,  0.08, 0.48), 0.40, 0.64, 0.16, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0,  0.04, 0.59), 0.30, 0.52, 0.08, mat_idx=0, vg_idx=b_idx["Root"])
    # Swept rear tail ramp at Y = +0.38 m
    add_weighted_box(bm, deform, (0.0,  0.38, 0.44), 0.36, 0.24, 0.14, mat_idx=0, vg_idx=b_idx["Root"], rot_deg=(-28.0, 0.0, 0.0))
    # Coral side fins & central chrome dorsal fin on the hood
    for sx in (-0.24, 0.24):
        add_weighted_box(bm, deform, (sx, 0.08, 0.32), 0.04, 0.58, 0.28, mat_idx=1, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, 0.06, 0.65), 0.05, 0.48, 0.05, mat_idx=2, vg_idx=b_idx["Root"])
    # Dark underground ball exit mouth on the -Y front of the hood
    add_weighted_box(bm, deform, (0.0, -0.25, 0.40), 0.28, 0.06, 0.28, mat_idx=3, vg_idx=b_idx["Root"])

    # 2. Hand-Dryer Air Vent & Spinning Turbine (`Blower_Fan` at (0.0, 0.18, 0.64))
    add_weighted_tube(bm, deform, [
        ((0.0, 0.18, 0.60), 0.095),
        ((0.0, 0.18, 0.67), 0.095),
    ], sides=8, mat_idx=4, vg_idx=b_idx["Blower_Fan"])
    for blade_i in range(3):
        add_weighted_box(bm, deform, (0.0, 0.18, 0.68), 0.16, 0.03, 0.015, mat_idx=2, vg_idx=b_idx["Blower_Fan"], rot_deg=(0.0, 0.0, blade_i * 60.0))

    # 3. Twin-Tier Tubular Chrome Ball Rack (`Y = -0.25 to -1.55 m`) holding up to 8 bowling balls
    for tier_z in (0.42, 0.22):
        for rail_x in (-0.17, -0.06, 0.06, 0.17):
            add_weighted_tube(bm, deform, [
                ((rail_x, -0.22, tier_z), 0.016),
                ((rail_x, -1.52, tier_z), 0.016),
            ], sides=6, mat_idx=2, vg_idx=b_idx["Root"])

    # Support stanchions rising from the base plinth under the ball rack
    for py in (-0.35, -0.92, -1.48):
        add_weighted_box(bm, deform, (0.0, py, 0.28), 0.38, 0.06, 0.28, mat_idx=0, vg_idx=b_idx["Root"])

    # 4. Front Rubber Ball Stopper Bumper (`Ball_Stopper` at Y = -1.52 m, Z = 0.44 m)
    add_weighted_box(bm, deform, (0.0, -1.52, 0.44), 0.38, 0.07, 0.12, mat_idx=3, vg_idx=b_idx["Ball_Stopper"])

    # 5. Bowler's Control Pedestal at Y = -1.72 m with Bumper & Reset Push-Buttons (`Btn_Bumpers`, `Btn_Reset`)
    add_weighted_tube(bm, deform, [
        ((0.0, -1.72, 0.00), 0.12),
        ((0.0, -1.72, 0.04), 0.05),
        ((0.0, -1.72, 0.84), 0.045),
    ], sides=8, mat_idx=2, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -1.72, 0.87), 0.34, 0.22, 0.06, mat_idx=0, vg_idx=b_idx["Root"], rot_deg=(18.0, 0.0, 0.0))

    # Left button: Yellow Bumpers toggle (`Btn_Bumpers`), Right button: Coral Reset (`Btn_Reset`)
    add_weighted_tube(bm, deform, [
        ((-0.08, -1.72, 0.89), 0.036),
        ((-0.08, -1.72, 0.93), 0.032),
    ], sides=8, mat_idx=5, vg_idx=b_idx["Btn_Bumpers"])
    add_weighted_tube(bm, deform, [
        (( 0.08, -1.72, 0.89), 0.036),
        (( 0.08, -1.72, 0.93), 0.032),
    ], sides=8, mat_idx=1, vg_idx=b_idx["Btn_Reset"])

    rig_obj, rest_mat = create_rig("BallReturn_Rig", bone_specs)
    finalize_rigged_mesh("BallReturn_Mesh", bm, rig_obj, bone_specs, mats)

    # Empties for ball spawn, 8 rack slots, hand dryer, and buttons
    make_empty("Ball_Spawn_Exit", (0.0, -0.26, 0.46), parent=rig_obj, bone_parent="Root")
    make_empty("Hand_Dryer_Vent", (0.0,  0.18, 0.68), parent=rig_obj, bone_parent="Root")
    make_empty("Btn_Bumpers_Hit", (-0.08, -1.72, 0.93), parent=rig_obj, bone_parent="Btn_Bumpers")
    make_empty("Btn_Reset_Hit",   ( 0.08, -1.72, 0.93), parent=rig_obj, bone_parent="Btn_Reset")

    slot_idx = 1
    for sx in (-0.115, 0.115):
        for sy in (-0.48, -0.76, -1.04, -1.32):
            make_empty(f"Slot_Ball_{slot_idx}", (sx, sy, 0.52), parent=rig_obj, bone_parent="Root")
            slot_idx += 1

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Blower_Fan_Spin (30f loop: hand-dryer turbine spins 360°)
    act_fan = bpy.data.actions.new(name="Blower_Fan_Spin")
    act_fan.use_fake_user = True
    rig_obj.animation_data.action = act_fan
    for f, yaw in [(1, 0.0), (8, 90.0), (16, 180.0), (23, 270.0), (30, 360.0)]:
        key_frame(f, rot_map={"Blower_Fan": (0.0, 0.0, yaw)})

    # 2. Ball_Stopper_Bounce (25f: rubber stopper compresses when a returning ball hits the end of the rack)
    act_stop = bpy.data.actions.new(name="Ball_Stopper_Bounce")
    act_stop.use_fake_user = True
    rig_obj.animation_data.action = act_stop
    for f, dy in [(1, 0.0), (4, -0.045), (9, 0.018), (15, -0.008), (25, 0.0)]:
        key_frame(f, loc_map={"Ball_Stopper": (0.0, dy, 0.0)})

    # 3. Button_Bumper_Press (20f)
    act_bb = bpy.data.actions.new(name="Button_Bumper_Press")
    act_bb.use_fake_user = True
    rig_obj.animation_data.action = act_bb
    for f, dz in [(1, 0.0), (6, -0.025), (12, -0.025), (20, 0.0)]:
        key_frame(f, loc_map={"Btn_Bumpers": (0.0, 0.0, dz)})

    # 4. Button_Reset_Press (20f)
    act_br = bpy.data.actions.new(name="Button_Reset_Press")
    act_br.use_fake_user = True
    rig_obj.animation_data.action = act_br
    for f, dz in [(1, 0.0), (6, -0.025), (12, -0.025), (20, 0.0)]:
        key_frame(f, loc_map={"Btn_Reset": (0.0, 0.0, dz)})

    save_and_export_bowling("cozy_bowling_ball_return", animated=True)


# ==============================================================================
# 7. cozy_bowling_overhead_scoreboard (Dual-Lane Hanging Scoreboard + [0,1] UV Screens)
# ==============================================================================
def build_overhead_scoreboard():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    # Suspended overhead console (2.60 m wide along X, centered at (0, 0, 0) where Z = 0 is bottom of console).
    # Faces -Y towards the bowler, with two single-quad [0, 1] UV screens:
    # Left screen (`Bowling_Screen_L` at X = -0.68 m) and Right screen (`Bowling_Screen_R` at X = +0.68 m).
    bone_specs = [
        ("Root",         ( 0.00, 0.0, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Strike_Crown", ( 0.00, 0.0, 0.78), ( 0.00,  0.00, 1.18), "Root"),
        ("Flag_Arm_L",   (-1.32, 0.0, 0.42), (-1.72,  0.00, 0.56), "Root"),
        ("Flag_Arm_R",   ( 1.32, 0.0, 0.42), ( 1.72,  0.00, 0.56), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Teal_Seafoam (#2D8A7E) - main dual-monitor housing
    # 1: Bowling_Coral_Pink (#E26A52) - mid-century wing trim & celebration flags
    # 2: Bowling_Gold_Brass (#D8A638) - bezel frames & spinning Strike Crown
    # 3: Bowling_Chrome_Steel (#C4CBD0) - ceiling suspension rods
    # 4: Bowling_Cream_Pearl (#F4EFE6) - center divider badge
    # 5: Bowling_Screen_L (#14242B) - ONLY on Lane 1 Left Screen Quad!
    # 6: Bowling_Screen_R (#14242B) - ONLY on Lane 2 Right Screen Quad!
    mats = [
        "Bowling_Teal_Seafoam", "Bowling_Coral_Pink", "Bowling_Gold_Brass",
        "Bowling_Chrome_Steel", "Bowling_Cream_Pearl",
        "Bowling_Screen_L", "Bowling_Screen_R"
    ]

    # 1. Dual-Monitor Googie Housing (`Root`, X = -1.32 to +1.32 m, Z = 0.0 to 0.76 m)
    add_weighted_box(bm, deform, (0.0, 0.06, 0.38), 2.64, 0.22, 0.76, mat_idx=0, vg_idx=b_idx["Root"])
    # Brass top & bottom trim bars
    add_weighted_box(bm, deform, (0.0, -0.02, 0.75), 2.70, 0.10, 0.04, mat_idx=2, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.02, 0.01), 2.70, 0.10, 0.04, mat_idx=2, vg_idx=b_idx["Root"])
    # Center decorative diamond fin between Lane 1 and Lane 2 monitors
    add_weighted_box(bm, deform, (0.0, -0.05, 0.38), 0.12, 0.08, 0.68, mat_idx=1, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.08, 0.38), 0.06, 0.04, 0.52, mat_idx=4, vg_idx=b_idx["Root"])

    # Brass monitor bezel frames around Left Screen (-0.68) and Right Screen (+0.68)
    for sx in (-0.68, 0.68):
        add_weighted_box(bm, deform, (sx, -0.05, 0.69), 1.12, 0.06, 0.04, mat_idx=2, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (sx, -0.05, 0.07), 1.12, 0.06, 0.04, mat_idx=2, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (sx - 0.54, -0.05, 0.38), 0.04, 0.06, 0.60, mat_idx=2, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (sx + 0.54, -0.05, 0.38), 0.04, 0.06, 0.60, mat_idx=2, vg_idx=b_idx["Root"])

    # Twin Chrome Ceiling Suspension Rods (`Z = 0.76 to 1.45 m`)
    for rx in (-0.85, 0.85):
        add_weighted_tube(bm, deform, [
            ((rx, 0.06, 0.76), 0.025),
            ((rx, 0.06, 1.45), 0.025),
        ], sides=6, mat_idx=3, vg_idx=b_idx["Root"])

    # 2. Mechanical Strike Crown Topper (`Strike_Crown` at X = 0.0, Z = 0.76 to 1.18 m)
    add_weighted_tube(bm, deform, [
        ((0.0, 0.04, 0.76), 0.09),
        ((0.0, 0.04, 0.84), 0.09),
    ], sides=8, mat_idx=3, vg_idx=b_idx["Strike_Crown"])
    add_weighted_box(bm, deform, (0.0, 0.04, 0.98), 0.24, 0.10, 0.24, mat_idx=2, vg_idx=b_idx["Strike_Crown"], rot_deg=(0.0, 45.0, 0.0))
    for ray_i in range(4):
        add_weighted_box(bm, deform, (0.0, 0.04, 0.98), 0.50, 0.05, 0.06, mat_idx=1, vg_idx=b_idx["Strike_Crown"], rot_deg=(0.0, ray_i * 45.0, 0.0))
    # Rear inspection panel & ventilation trim on back of scoreboard (+Y = +0.18 m)
    for rx in (-0.68, 0.68):
        add_weighted_box(bm, deform, (rx, 0.175, 0.38), 0.88, 0.02, 0.46, mat_idx=2, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (rx, 0.185, 0.38), 0.80, 0.02, 0.38, mat_idx=4, vg_idx=b_idx["Root"])

    # 3. Left & Right Celebration Semaphore Flags (`Flag_Arm_L`, `Flag_Arm_R`)
    for f_side, f_bone in [(-1.0, "Flag_Arm_L"), (1.0, "Flag_Arm_R")]:
        fx = f_side * 1.32
        add_weighted_tube(bm, deform, [
            ((fx, 0.02, 0.42), 0.022),
            ((fx + f_side * 0.38, 0.02, 0.56), 0.016),
        ], sides=6, mat_idx=3, vg_idx=b_idx[f_bone])
        add_weighted_box(bm, deform, (fx + f_side * 0.32, 0.02, 0.62), 0.24, 0.03, 0.14, mat_idx=1, vg_idx=b_idx[f_bone], rot_deg=(0.0, f_side * -18.0, 0.0))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    # 4. TWO SINGLE-QUAD [0, 1] UV SCREENS (`Bowling_Screen_L` = mat 5, `Bowling_Screen_R` = mat 6)
    # Each screen is 1.04 m wide x 0.58 m tall, sitting at Y = -0.056 m facing -Y!
    f_scr_l, uv_l = add_uv_screen_quad(bm, deform, center=(-0.68, -0.056, 0.38), width_x=1.04, height_z=0.58, mat_idx=5, vg_idx=b_idx["Root"])
    f_scr_r, uv_r = add_uv_screen_quad(bm, deform, center=( 0.68, -0.056, 0.38), width_x=1.04, height_z=0.58, mat_idx=6, vg_idx=b_idx["Root"])
    apply_screen_uvs(bm, [(f_scr_l, uv_l), (f_scr_r, uv_r)])

    rig_obj, rest_mat = create_rig("Scoreboard_Rig", bone_specs)
    finalize_rigged_mesh("Scoreboard_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Screen_Center_L", (-0.68, -0.06, 0.38), parent=rig_obj, bone_parent="Root")
    make_empty("Screen_Center_R", ( 0.68, -0.06, 0.38), parent=rig_obj, bone_parent="Root")
    make_empty("Topper_Crown",    ( 0.00,  0.02, 0.98), parent=rig_obj, bone_parent="Strike_Crown")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Scoreboard_Idle (60f loop: gentle topper crown rotation)
    act_idle = bpy.data.actions.new(name="Scoreboard_Idle")
    act_idle.use_fake_user = True
    rig_obj.animation_data.action = act_idle
    for f, r_arm in [(1, 0.0), (30, 5.0), (60, 0.0)]:
        key_frame(f, rot_map={
            "Flag_Arm_L": (0.0, -r_arm, 0.0),
            "Flag_Arm_R": (0.0,  r_arm, 0.0),
        })

    # 2. Strike_Celebration_Spin (60f: crown pops up & spins 720° while semaphore arms pump!)
    act_strike = bpy.data.actions.new(name="Strike_Celebration_Spin")
    act_strike.use_fake_user = True
    rig_obj.animation_data.action = act_strike
    for f, yaw_c, dz_c, arm_r in [
        (1,    0.0, 0.00,   0.0),
        (12, 180.0, 0.14,  28.0),
        (24, 360.0, 0.04, -18.0),
        (36, 540.0, 0.14,  28.0),
        (48, 680.0, 0.02, -10.0),
        (60, 720.0, 0.00,   0.0),
    ]:
        key_frame(f, rot_map={
            "Strike_Crown": (0.0, 0.0, yaw_c),
            "Flag_Arm_L":   (0.0, -arm_r, 0.0),
            "Flag_Arm_R":   (0.0,  arm_r, 0.0),
        }, loc_map={
            "Strike_Crown": (0.0, 0.0, dz_c),
        })

    # 3. Gutter_Womp_Droop (45f: semaphore flags droop down 55° in comical "womp-womp" disappointment)
    act_gutter = bpy.data.actions.new(name="Gutter_Womp_Droop")
    act_gutter.use_fake_user = True
    rig_obj.animation_data.action = act_gutter
    for f, droop, dz_c in [
        (1,   0.0,  0.00),
        (8,  55.0, -0.06),
        (16, 48.0, -0.05),
        (28, 52.0, -0.06),
        (45,  0.0,  0.00),
    ]:
        key_frame(f, rot_map={
            "Flag_Arm_L": (0.0,  droop, 0.0),
            "Flag_Arm_R": (0.0, -droop, 0.0),
        }, loc_map={
            "Strike_Crown": (0.0, 0.0, dz_c),
        })

    save_and_export_bowling("cozy_bowling_overhead_scoreboard", animated=True)


if __name__ == "__main__":
    build_mall_shell()
    build_bowling_lane()
    build_pinsetter()
    build_ball_return()
    build_overhead_scoreboard()
