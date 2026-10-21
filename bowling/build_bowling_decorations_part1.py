import bpy
import bmesh
import math
import sys
from mathutils import Vector, Euler, Matrix

sys.path.insert(0, "C:/argon/bowling")
sys.path.insert(0, "C:/argon/rapa_nui")
from bowling_utils import (
    PALETTE, init_scene, make_empty, add_box, add_weighted_box,
    add_weighted_tube, create_rig, make_pose_helpers,
    finalize_rigged_mesh, save_and_export_bowling
)


# ==============================================================================
# 11. cozy_bowling_trophy_case (Illuminated Glass League Trophy & Patch Showcase)
# ==============================================================================
def build_trophy_case():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",             ( 0.00,  0.00, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Door_Glass_L",     (-0.32, -0.22, 1.05), (-0.32, -0.22, 1.35), "Root"),
        ("Door_Glass_R",     ( 0.32, -0.22, 1.05), ( 0.32, -0.22, 1.35), "Root"),
        ("Top_Champion_Cup", ( 0.00,  0.00, 1.48), ( 0.00,  0.00, 1.76), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Walnut_Dark - cabinet frame & lower credenza
    # 1: Bowling_Gold_Brass - trophies, plaques & brass legs
    # 2: Bowling_Coral_Pink - velvet backing panel & ribbons
    # 3: Bowling_Teal_Seafoam - lower cabinet doors & league patches
    # 4: Bowling_Cream_Pearl - trophy marble bases & header sign
    # 5: Bowling_Glass_Tint - sliding glass doors
    mats = [
        "Bowling_Walnut_Dark", "Bowling_Gold_Brass", "Bowling_Coral_Pink",
        "Bowling_Teal_Seafoam", "Bowling_Cream_Pearl", "Bowling_Glass_Tint"
    ]

    # Tapered brass mid-century legs (Z = 0.00 to 0.16 m)
    for lx in (-0.62, 0.62):
        for ly in (-0.18, 0.18):
            add_weighted_tube(bm, deform, [
                ((lx, ly, 0.00), 0.018),
                ((lx * 0.96, ly, 0.16), 0.028),
            ], sides=6, mat_idx=1, vg_idx=b_idx["Root"])

    # Lower Credenza Base (Z = 0.16 to 0.64 m, width = 1.40 m, depth = 0.48 m)
    add_weighted_box(bm, deform, (0.0, 0.00, 0.40), 1.40, 0.48, 0.48, mat_idx=0, vg_idx=b_idx["Root"])
    for sx in (-0.33, 0.33):
        add_weighted_box(bm, deform, (sx, -0.245, 0.40), 0.62, 0.02, 0.40, mat_idx=3, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (sx * 0.25, -0.26, 0.40), 0.025, 0.03, 0.14, mat_idx=1, vg_idx=b_idx["Root"])

    # Upper Showcase Frame (Z = 0.64 to 1.96 m): Back wall, Left/Right walls, Top canopy & Shelves
    add_weighted_box(bm, deform, ( 0.00,  0.21, 1.30), 1.40, 0.06, 1.32, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.00,  0.17, 1.30), 1.28, 0.02, 1.22, mat_idx=2, vg_idx=b_idx["Root"])  # Coral velvet backing
    add_weighted_box(bm, deform, (-0.67,  0.00, 1.30), 0.06, 0.46, 1.32, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.67,  0.00, 1.30), 0.06, 0.46, 1.32, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.00,  0.00, 1.92), 1.42, 0.50, 0.10, mat_idx=0, vg_idx=b_idx["Root"])
    # Lit Header Plaque ("LEAGUE CHAMPIONS")
    add_weighted_box(bm, deform, ( 0.00, -0.255, 1.92), 1.10, 0.03, 0.07, mat_idx=4, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.00, -0.265, 1.92), 1.14, 0.02, 0.085, mat_idx=1, vg_idx=b_idx["Root"])

    # Interior Shelves at Z = 1.04 m and Z = 1.44 m
    for sz in (1.04, 1.44):
        add_weighted_box(bm, deform, (0.0, 0.01, sz), 1.28, 0.36, 0.03, mat_idx=4, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (0.0, -0.17, sz), 1.28, 0.02, 0.035, mat_idx=1, vg_idx=b_idx["Root"])

    # Bottom Shelf Trophies & "300 PERFECT GAME" Plaque (Z = 0.64 to 1.02 m)
    add_weighted_box(bm, deform, (0.0, 0.06, 0.82), 0.30, 0.04, 0.26, mat_idx=0, vg_idx=b_idx["Root"], rot_deg=(-12.0, 0.0, 0.0))
    add_weighted_box(bm, deform, (0.0, 0.04, 0.82), 0.24, 0.04, 0.20, mat_idx=1, vg_idx=b_idx["Root"], rot_deg=(-12.0, 0.0, 0.0))
    for tx in (-0.42, 0.42):
        add_weighted_box(bm, deform, (tx, 0.0, 0.67), 0.14, 0.14, 0.06, mat_idx=4, vg_idx=b_idx["Root"])
        add_weighted_tube(bm, deform, [
            ((tx, 0.0, 0.70), 0.035),
            ((tx, 0.0, 0.78), 0.018),
            ((tx, 0.0, 0.88), 0.055),
            ((tx, 0.0, 0.94), 0.045),
        ], sides=8, mat_idx=1, vg_idx=b_idx["Root"])

    # Middle Shelf Trophies & League Patches (Z = 1.06 to 1.42 m)
    for tx, tmat in [(-0.40, 1), (-0.14, 3), (0.14, 2), (0.40, 1)]:
        add_weighted_box(bm, deform, (tx, 0.0, 1.08), 0.12, 0.12, 0.05, mat_idx=4, vg_idx=b_idx["Root"])
        add_weighted_tube(bm, deform, [
            ((tx, 0.0, 1.105), 0.03),
            ((tx, 0.0, 1.22), 0.05),
            ((tx, 0.0, 1.32), 0.02),
            ((tx, 0.0, 1.36), 0.035),
        ], sides=8, mat_idx=tmat, vg_idx=b_idx["Root"])

    # Top Shelf Grand Champion Cup (`Top_Champion_Cup` bone at (0, 0, 1.48)) + Flanking Pin Trophies
    add_weighted_box(bm, deform, (0.0, 0.0, 1.49), 0.20, 0.20, 0.07, mat_idx=4, vg_idx=b_idx["Top_Champion_Cup"])
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 1.525), 0.055),
        ((0.0, 0.0, 1.59),  0.025),
        ((0.0, 0.0, 1.68),  0.095),
        ((0.0, 0.0, 1.78),  0.110),
        ((0.0, 0.0, 1.82),  0.040),
    ], sides=10, mat_idx=1, vg_idx=b_idx["Top_Champion_Cup"])
    for tx in (-0.42, 0.42):
        add_weighted_box(bm, deform, (tx, 0.0, 1.48), 0.13, 0.13, 0.05, mat_idx=4, vg_idx=b_idx["Root"])
        add_weighted_tube(bm, deform, [
            ((tx, 0.0, 1.505), 0.028),
            ((tx, 0.0, 1.60),  0.052),
            ((tx, 0.0, 1.68),  0.022),
            ((tx, 0.0, 1.75),  0.038),
        ], sides=8, mat_idx=1, vg_idx=b_idx["Root"])

    # Sliding Framed Showcase Doors (`Door_Glass_L` at Y = -0.21, `Door_Glass_R` at Y = -0.23)
    # Open-center glass frames so all 3 tiers of golden trophies are 100% visible in Eevee/Unity!
    for sx, dbone, dy in [(-0.32, "Door_Glass_L", -0.21), (0.32, "Door_Glass_R", -0.23)]:
        add_weighted_box(bm, deform, (sx, dy, 1.83), 0.64, 0.018, 0.06, mat_idx=5, vg_idx=b_idx[dbone])
        add_weighted_box(bm, deform, (sx, dy, 0.69), 0.64, 0.018, 0.06, mat_idx=5, vg_idx=b_idx[dbone])
        add_weighted_box(bm, deform, (sx - 0.29, dy, 1.26), 0.06, 0.018, 1.08, mat_idx=5, vg_idx=b_idx[dbone])
        add_weighted_box(bm, deform, (sx + 0.29, dy, 1.26), 0.06, 0.018, 1.08, mat_idx=5, vg_idx=b_idx[dbone])
        hx = sx - 0.26 if sx < 0 else sx + 0.26
        add_weighted_box(bm, deform, (hx, dy - 0.015, 1.26), 0.022, 0.025, 0.18, mat_idx=1, vg_idx=b_idx[dbone])

    rig_obj, rest_mat = create_rig("TrophyCase_Rig", bone_specs)
    finalize_rigged_mesh("TrophyCase_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Trophy_Focus", (0.0, 0.0, 1.66), parent=rig_obj, bone_parent="Top_Champion_Cup")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Case_Doors_Slide (36f: glass doors slide open and closed)
    act_slide = bpy.data.actions.new(name="Case_Doors_Slide")
    act_slide.use_fake_user = True
    rig_obj.animation_data.action = act_slide
    for f, dx in [(1, 0.0), (14, 0.28), (24, 0.28), (36, 0.0)]:
        key_frame(f, loc_map={"Door_Glass_L": (dx, 0.0, 0.0), "Door_Glass_R": (-dx, 0.0, 0.0)})

    # 2. Trophy_Sparkle_Spin (40f loop: grand champion cup rotates 360° with a gentle hover)
    act_spin = bpy.data.actions.new(name="Trophy_Sparkle_Spin")
    act_spin.use_fake_user = True
    rig_obj.animation_data.action = act_spin
    for f, yaw, dz in [(1, 0.0, 0.0), (10, 90.0, 0.02), (20, 180.0, 0.0), (30, 270.0, 0.02), (40, 360.0, 0.0)]:
        key_frame(f, rot_map={"Top_Champion_Cup": (0.0, 0.0, yaw)}, loc_map={"Top_Champion_Cup": (0.0, 0.0, dz)})

    save_and_export_bowling("cozy_bowling_trophy_case", animated=True)


# ==============================================================================
# 12. cozy_bowling_ball_rack_tiered (3-Tier A-Frame House Ball Tree)
# ==============================================================================
def build_ball_rack_tiered():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",          (0.0, 0.0, 0.00), (0.0, -0.15, 0.00), None),
        ("Top_Row_Balls", (0.0, 0.0, 0.92), (0.0,  0.00, 1.08), "Root"),
        ("Mid_Row_Balls", (0.0, 0.0, 0.56), (0.0,  0.00, 0.72), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Chrome_Steel - tubular A-frame & rails
    # 1: Bowling_Teal_Seafoam - base plinth & 10lb balls
    # 2: Bowling_Coral_Pink - 8lb balls & header sign
    # 3: Bowling_Bumper_Yellow - 12lb marigold balls
    # 4: Bowling_Obsidian_Ball - 15lb pro balls & rubber feet
    # 5: Bowling_Gold_Brass - weight tags
    mats = [
        "Bowling_Chrome_Steel", "Bowling_Teal_Seafoam", "Bowling_Coral_Pink",
        "Bowling_Bumper_Yellow", "Bowling_Obsidian_Ball", "Bowling_Gold_Brass"
    ]

    # Heavy Base Plinth (Z = 0.00 to 0.10 m, width = 1.16 m, depth = 0.44 m)
    add_weighted_box(bm, deform, (0.0, 0.0, 0.04), 1.16, 0.44, 0.08, mat_idx=1, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, 0.0, 0.09), 1.10, 0.38, 0.02, mat_idx=4, vg_idx=b_idx["Root"])

    # Left & Right A-Frame Chrome Uprights (`X = +-0.48 m`, Z = 0.08 to 1.14 m)
    for sx in (-0.48, 0.48):
        add_weighted_tube(bm, deform, [((sx, -0.16, 0.08), 0.022), ((sx, -0.05, 1.12), 0.020)], sides=8, mat_idx=0, vg_idx=b_idx["Root"])
        add_weighted_tube(bm, deform, [((sx,  0.16, 0.08), 0.022), ((sx,  0.05, 1.12), 0.020)], sides=8, mat_idx=0, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (sx, 0.0, 1.12), 0.045, 0.14, 0.04, mat_idx=5, vg_idx=b_idx["Root"])

    # Top Header Sign ("HOUSE BALLS — 8 TO 16 LB")
    add_weighted_box(bm, deform, (0.0, 0.0, 1.18), 0.68, 0.04, 0.11, mat_idx=2, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, 0.0, 1.18), 0.72, 0.03, 0.13, mat_idx=5, vg_idx=b_idx["Root"])

    # 3 Pairs of Horizontal Chrome Cradle Rails (Z = 0.18, 0.50, 0.82 m)
    for rz, ry_span in [(0.18, 0.09), (0.50, 0.08), (0.82, 0.07)]:
        for ry in (-ry_span, ry_span):
            add_weighted_tube(bm, deform, [((-0.48, ry, rz), 0.016), ((0.48, ry, rz), 0.016)], sides=8, mat_idx=0, vg_idx=b_idx["Root"])

    # 9 Bowling Balls across the 3 tiers (3 per row at X = -0.28, 0.00, +0.28 m)
    R = 0.104
    ball_lat = [(-0.98, 0.08), (-0.75, 0.65), (-0.40, 0.92), (0.00, 1.00), (0.40, 0.92), (0.75, 0.65), (0.98, 0.08)]
    tier_specs = [
        (0.26, "Root",          [( -0.28, 4), (0.00, 1), (0.28, 4)]),
        (0.58, "Mid_Row_Balls", [( -0.28, 1), (0.00, 3), (0.28, 2)]),
        (0.90, "Top_Row_Balls", [( -0.28, 2), (0.00, 5), (0.28, 3)]),
    ]
    for bz, bname, row_balls in tier_specs:
        for bx, bmat in row_balls:
            pts_rad = [((bx, 0.0, bz + kz * R), kr * R) for kz, kr in ball_lat]
            add_weighted_tube(bm, deform, pts_rad, sides=12, mat_idx=bmat, vg_idx=b_idx[bname])

    rig_obj, rest_mat = create_rig("BallRack_Rig", bone_specs)
    finalize_rigged_mesh("BallRack_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Grab_Top_Ball", (0.0, 0.0, 0.92), parent=rig_obj, bone_parent="Top_Row_Balls")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Balls_Rattle_Settle (28f: balls roll slightly along the rails when bumped)
    act_rattle = bpy.data.actions.new(name="Balls_Rattle_Settle")
    act_rattle.use_fake_user = True
    rig_obj.animation_data.action = act_rattle
    for f, dx, r_ang in [(1, 0.0, 0.0), (6, 0.035, 16.0), (13, -0.025, -12.0), (20, 0.012, 6.0), (28, 0.0, 0.0)]:
        key_frame(f, rot_map={"Top_Row_Balls": (0.0, r_ang, 0.0), "Mid_Row_Balls": (0.0, -r_ang * 0.8, 0.0)},
                  loc_map={"Top_Row_Balls": (dx, 0.0, 0.0), "Mid_Row_Balls": (-dx * 0.7, 0.0, 0.0)})

    # 2. Top_Ball_Lift_Inspect (32f: top row lifts up for inspection and settles back onto cradle)
    act_lift = bpy.data.actions.new(name="Top_Ball_Lift_Inspect")
    act_lift.use_fake_user = True
    rig_obj.animation_data.action = act_lift
    for f, dz, p_ang in [(1, 0.0, 0.0), (10, 0.12, -25.0), (20, 0.12, 25.0), (32, 0.0, 0.0)]:
        key_frame(f, rot_map={"Top_Row_Balls": (p_ang, 0.0, 0.0)}, loc_map={"Top_Row_Balls": (0.0, 0.0, dz)})

    save_and_export_bowling("cozy_bowling_ball_rack_tiered", animated=True)


# ==============================================================================
# 13. cozy_bowling_chalk_cone_pedestal (Bowler's Rosin/Chalk Cone Stand)
# ==============================================================================
def build_chalk_cone_pedestal():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",         (0.0,  0.00, 0.00), (0.0, -0.12, 0.00), None),
        ("Chalk_Cone",   (0.0,  0.00, 0.90), (0.0,  0.00, 1.04), "Root"),
        ("Puff_Ring",    (0.0,  0.00, 0.92), (0.0,  0.00, 1.06), "Root"),
        ("Dryer_Button", (0.0, -0.14, 0.82), (0.0, -0.19, 0.82), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Teal_Seafoam - fluted mid-century pedestal column
    # 1: Bowling_Coral_Pink - upper bowl housing
    # 2: Bowling_Gold_Brass - base ring, dish rim & hand-dryer louver
    # 3: Bowling_Cream_Pearl - chalk cone & puff cloud ring
    # 4: Bowling_Chrome_Steel - pedestal shaft
    # 5: Bowling_Crimson_Stripe - warm-air dryer push button
    mats = [
        "Bowling_Teal_Seafoam", "Bowling_Coral_Pink", "Bowling_Gold_Brass",
        "Bowling_Cream_Pearl", "Bowling_Chrome_Steel", "Bowling_Crimson_Stripe"
    ]

    # Pedestal Base & Column (Z = 0.00 to 0.88 m)
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 0.00), 0.24),
        ((0.0, 0.0, 0.04), 0.22),
        ((0.0, 0.0, 0.09), 0.11),
    ], sides=12, mat_idx=2, vg_idx=b_idx["Root"])
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 0.09), 0.085),
        ((0.0, 0.0, 0.48), 0.065),
        ((0.0, 0.0, 0.72), 0.095),
    ], sides=10, mat_idx=0, vg_idx=b_idx["Root"])
    # Upper Coral Dish Housing (Z = 0.72 to 0.90 m)
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 0.72), 0.11),
        ((0.0, 0.0, 0.85), 0.18),
        ((0.0, 0.0, 0.90), 0.19),
    ], sides=12, mat_idx=1, mat_end_idx=2, vg_idx=b_idx["Root"])

    # Warm-Air Hand Dryer Louver & Push Button on front (`Y = -0.14 m, Z = 0.82 m`)
    add_weighted_box(bm, deform, (0.0, -0.135, 0.79), 0.11, 0.04, 0.09, mat_idx=2, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.155, 0.81), 0.045, 0.03, 0.045, mat_idx=5, vg_idx=b_idx["Dryer_Button"])

    # Tapered White Bowler's Chalk Cone (`Chalk_Cone` at Z = 0.90..1.02 m)
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 0.90), 0.075),
        ((0.0, 0.0, 0.96), 0.052),
        ((0.0, 0.0, 1.01), 0.024),
        ((0.0, 0.0, 1.025), 0.008),
    ], sides=10, mat_idx=3, vg_idx=b_idx["Chalk_Cone"])

    # Stylized Chalk Poof Cloud Ring (`Puff_Ring` tucked inside cone at rest, expands on pat!)
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 0.91), 0.055),
        ((0.0, 0.0, 0.93), 0.065),
        ((0.0, 0.0, 0.95), 0.050),
    ], sides=10, mat_idx=3, vg_idx=b_idx["Puff_Ring"])

    rig_obj, rest_mat = create_rig("ChalkStand_Rig", bone_specs)
    finalize_rigged_mesh("ChalkStand_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Touch_Chalk_Cone", (0.0, 0.0, 0.98), parent=rig_obj, bone_parent="Chalk_Cone")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Chalk_Pat_Poof (28f: chalk cone depresses and puff ring rises and expands)
    act_poof = bpy.data.actions.new(name="Chalk_Pat_Poof")
    act_poof.use_fake_user = True
    rig_obj.animation_data.action = act_poof
    for f, c_dz, p_dz, p_sc in [
        (1,   0.000, 0.00, 0.6),
        (6,  -0.018, 0.04, 1.5),
        (14,  0.005, 0.12, 2.1),
        (22,  0.000, 0.16, 1.1),
        (28,  0.000, 0.00, 0.6),
    ]:
        key_frame(f, loc_map={"Chalk_Cone": (0.0, 0.0, c_dz), "Puff_Ring": (0.0, 0.0, p_dz)},
                  scale_map={"Puff_Ring": (p_sc, p_sc, p_sc)})

    # 2. Dryer_Button_Press (20f: pressing the hand-dryer button spins the chalk cone slightly)
    act_btn = bpy.data.actions.new(name="Dryer_Button_Press")
    act_btn.use_fake_user = True
    rig_obj.animation_data.action = act_btn
    for f, dy, yaw in [(1, 0.0, 0.0), (5, 0.018, 30.0), (12, 0.018, 120.0), (20, 0.0, 180.0)]:
        key_frame(f, rot_map={"Chalk_Cone": (0.0, 0.0, yaw)}, loc_map={"Dryer_Button": (0.0, dy, 0.0)})

    save_and_export_bowling("cozy_bowling_chalk_cone_pedestal", animated=True)


# ==============================================================================
# 14. cozy_bowling_leaderboard_chalkboard (League High-Score Pegboard & Rules)
# ==============================================================================
def build_leaderboard_chalkboard():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",          ( 0.00,  0.00, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Crown_Badge",   ( 0.00, -0.06, 0.52), ( 0.00, -0.06, 0.72), "Root"),
        ("Name_Plaque_1", ( 0.00, -0.05, 0.18), ( 0.00, -0.15, 0.18), "Root"),
        ("Name_Plaque_2", ( 0.00, -0.05, 0.02), ( 0.00, -0.15, 0.02), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Walnut_Dark - outer frame
    # 1: Bowling_Obsidian_Ball - dark felt letterboard surface
    # 2: Bowling_Gold_Brass - crown topper, frame trim & #1 plaque
    # 3: Bowling_Coral_Pink - header banner & #2 plaque
    # 4: Bowling_Teal_Seafoam - #3/#4 plaques & side etiquette poster
    # 5: Bowling_Cream_Pearl - score strips & pin icons
    mats = [
        "Bowling_Walnut_Dark", "Bowling_Obsidian_Ball", "Bowling_Gold_Brass",
        "Bowling_Coral_Pink", "Bowling_Teal_Seafoam", "Bowling_Cream_Pearl"
    ]

    # Main Wall Board Frame (centered at (0, 0, 0), width = 1.65 m, height = 1.05 m)
    add_weighted_box(bm, deform, (0.0,  0.00, 0.00), 1.65, 0.05, 1.05, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.02, 0.00), 1.53, 0.03, 0.93, mat_idx=1, vg_idx=b_idx["Root"])
    # Header Banner ("CORAL LANES — 300 CLUB")
    add_weighted_box(bm, deform, (0.0, -0.04, 0.36), 1.38, 0.03, 0.14, mat_idx=3, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.05, 0.36), 1.15, 0.02, 0.06, mat_idx=5, vg_idx=b_idx["Root"])

    # Flip-able #1 & #2 High-Score Name Plaques (`Name_Plaque_1`, `Name_Plaque_2`) + Static #3 & #4 rows
    add_weighted_box(bm, deform, (0.0, -0.045,  0.18), 1.30, 0.03, 0.11, mat_idx=2, vg_idx=b_idx["Name_Plaque_1"])
    add_weighted_box(bm, deform, (0.0, -0.058,  0.18), 1.12, 0.02, 0.05, mat_idx=5, vg_idx=b_idx["Name_Plaque_1"])
    add_weighted_box(bm, deform, (0.0, -0.045,  0.02), 1.30, 0.03, 0.11, mat_idx=3, vg_idx=b_idx["Name_Plaque_2"])
    add_weighted_box(bm, deform, (0.0, -0.058,  0.02), 1.12, 0.02, 0.05, mat_idx=5, vg_idx=b_idx["Name_Plaque_2"])

    for rz in (-0.14, -0.30):
        add_weighted_box(bm, deform, (0.0, -0.04, rz), 1.30, 0.025, 0.10, mat_idx=4, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (0.0, -0.05, rz), 1.10, 0.015, 0.045, mat_idx=5, vg_idx=b_idx["Root"])

    # Golden Starburst & Crossed-Pins Topper (`Crown_Badge` at (0, -0.06, 0.56))
    add_weighted_box(bm, deform, (0.0, -0.05, 0.56), 0.24, 0.04, 0.24, mat_idx=2, vg_idx=b_idx["Crown_Badge"], rot_deg=(0.0, 45.0, 0.0))
    add_weighted_box(bm, deform, (0.0, -0.07, 0.56), 0.06, 0.04, 0.30, mat_idx=5, vg_idx=b_idx["Crown_Badge"], rot_deg=(0.0,  28.0, 0.0))
    add_weighted_box(bm, deform, (0.0, -0.08, 0.56), 0.06, 0.04, 0.30, mat_idx=5, vg_idx=b_idx["Crown_Badge"], rot_deg=(0.0, -28.0, 0.0))

    rig_obj, rest_mat = create_rig("Leaderboard_Rig", bone_specs)
    finalize_rigged_mesh("Leaderboard_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Board_Center", (0.0, -0.06, 0.0), parent=rig_obj, bone_parent="Root")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. New_High_Score_Flip (36f: #1 and #2 name plaques flip 360° around X as crown badge rocks)
    act_flip = bpy.data.actions.new(name="New_High_Score_Flip")
    act_flip.use_fake_user = True
    rig_obj.animation_data.action = act_flip
    for f, p1, p2, r_cr in [
        (1,    0.0,   0.0,   0.0),
        (10, 180.0,  90.0,  15.0),
        (20, 360.0, 270.0, -15.0),
        (28, 360.0, 360.0,   8.0),
        (36, 360.0, 360.0,   0.0),
    ]:
        key_frame(f, rot_map={
            "Name_Plaque_1": (p1, 0.0, 0.0),
            "Name_Plaque_2": (p2, 0.0, 0.0),
            "Crown_Badge":   (0.0, r_cr, 0.0),
        })

    # 2. Crown_Badge_Pulse (30f loop: golden badge rocks and pulses)
    act_pulse = bpy.data.actions.new(name="Crown_Badge_Pulse")
    act_pulse.use_fake_user = True
    rig_obj.animation_data.action = act_pulse
    for f, r_ang, sc in [(1, 0.0, 1.0), (8, 12.0, 1.12), (16, 0.0, 1.0), (23, -12.0, 1.12), (30, 0.0, 1.0)]:
        key_frame(f, rot_map={"Crown_Badge": (0.0, r_ang, 0.0)}, scale_map={"Crown_Badge": (sc, sc, sc)})

    save_and_export_bowling("cozy_bowling_leaderboard_chalkboard", animated=True)


# ==============================================================================
# 15. cozy_bowling_lane_oiler_cart (Vintage Roll-Away Lane Conditioner & Mop Cart)
# ==============================================================================
def build_lane_oiler_cart():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",         ( 0.00,  0.00, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Cart_Body",    ( 0.00,  0.00, 0.12), ( 0.00,  0.00, 0.55), "Root"),
        ("Roller_Brush", ( 0.00, -0.26, 0.08), ( 0.25, -0.26, 0.08), "Cart_Body"),
        ("Warning_Cone", ( 0.48, -0.10, 0.00), ( 0.48, -0.10, 0.48), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Teal_Seafoam - conditioner tank housing
    # 1: Bowling_Coral_Pink - top hood & warning cone stripes
    # 2: Bowling_Chrome_Steel - push handle & squeegee bar
    # 3: Bowling_Bumper_Yellow - caution cone & oil sight gauge
    # 4: Bowling_Obsidian_Ball - wheels & rubber squeegee
    # 5: Bowling_Cream_Pearl - microfiber conditioning roller
    mats = [
        "Bowling_Teal_Seafoam", "Bowling_Coral_Pink", "Bowling_Chrome_Steel",
        "Bowling_Bumper_Yellow", "Bowling_Obsidian_Ball", "Bowling_Cream_Pearl"
    ]

    # Cart Chassis & Tank (`Cart_Body` bone, width = 0.64 m, depth = 0.48 m, Z = 0.08 to 0.56 m)
    add_weighted_box(bm, deform, (0.0, 0.00, 0.28), 0.62, 0.46, 0.36, mat_idx=0, vg_idx=b_idx["Cart_Body"])
    add_weighted_box(bm, deform, (0.0, 0.00, 0.50), 0.56, 0.40, 0.10, mat_idx=1, vg_idx=b_idx["Cart_Body"])
    add_weighted_box(bm, deform, (0.0, -0.235, 0.32), 0.32, 0.03, 0.12, mat_idx=3, vg_idx=b_idx["Cart_Body"])
    # 4 Caster Wheels (Z = 0.00 to 0.12 m)
    for wx in (-0.26, 0.26):
        for wy in (-0.16, 0.16):
            add_weighted_box(bm, deform, (wx, wy, 0.06), 0.05, 0.11, 0.12, mat_idx=4, vg_idx=b_idx["Cart_Body"])

    # Angled Chrome Push Handle (`Z = 0.45 to 0.96 m, Y = +0.20 to +0.38 m`)
    for hx in (-0.24, 0.24):
        add_weighted_tube(bm, deform, [((hx, 0.20, 0.44), 0.016), ((hx, 0.38, 0.94), 0.016)], sides=8, mat_idx=2, vg_idx=b_idx["Cart_Body"])
    add_weighted_tube(bm, deform, [((-0.26, 0.38, 0.94), 0.018), ((0.26, 0.38, 0.94), 0.018)], sides=8, mat_idx=2, vg_idx=b_idx["Cart_Body"])

    # Front Spinning Lane-Conditioner Microfiber Roller (`Roller_Brush` at Y = -0.26 m, Z = 0.08 m)
    add_weighted_tube(bm, deform, [((-0.28, -0.26, 0.08), 0.055), ((0.28, -0.26, 0.08), 0.055)], sides=10, mat_idx=5, vg_idx=b_idx["Roller_Brush"])

    # Companion Wet-Oil Caution Cone (`Warning_Cone` at X = +0.48 m, Z = 0.00 to 0.52 m)
    add_weighted_box(bm, deform, (0.48, -0.10, 0.02), 0.28, 0.28, 0.04, mat_idx=4, vg_idx=b_idx["Warning_Cone"])
    cone_rings = add_weighted_tube(bm, deform, [
        ((0.48, -0.10, 0.04), 0.11),
        ((0.48, -0.10, 0.20), 0.08),
        ((0.48, -0.10, 0.36), 0.05),
        ((0.48, -0.10, 0.50), 0.02),
    ], sides=8, mat_idx=3, vg_idx=b_idx["Warning_Cone"])
    r_mid_a, r_mid_b = set(cone_rings[1]), set(cone_rings[2])
    for f in bm.faces:
        if all(v in r_mid_a or v in r_mid_b for v in f.verts):
            f.material_index = 1

    rig_obj, rest_mat = create_rig("OilerCart_Rig", bone_specs)
    finalize_rigged_mesh("OilerCart_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Push_Grip", (0.0, 0.38, 0.94), parent=rig_obj, bone_parent="Cart_Body")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Cart_Roll_Condition (36f: cart rolls forward and back while roller brush spins 360°)
    act_roll = bpy.data.actions.new(name="Cart_Roll_Condition")
    act_roll.use_fake_user = True
    rig_obj.animation_data.action = act_roll
    for f, dy, p_ang in [(1, 0.0, 0.0), (12, -0.18, -180.0), (24, 0.08, -360.0), (36, 0.0, 0.0)]:
        key_frame(f, rot_map={"Roller_Brush": (p_ang, 0.0, 0.0)}, loc_map={"Cart_Body": (0.0, dy, 0.0)})

    # 2. Cone_Tip_Wobble (28f: caution cone rocks back and forth when bumped)
    act_cone = bpy.data.actions.new(name="Cone_Tip_Wobble")
    act_cone.use_fake_user = True
    rig_obj.animation_data.action = act_cone
    for f, r_ang, p_ang in [(1, 0.0, 0.0), (6, 22.0, -14.0), (13, -16.0, 10.0), (20, 8.0, -5.0), (28, 0.0, 0.0)]:
        key_frame(f, rot_map={"Warning_Cone": (p_ang, r_ang, 0.0)})

    save_and_export_bowling("cozy_bowling_lane_oiler_cart", animated=True)


# ==============================================================================
# 16. cozy_bowling_nachos_pizza_tray (Diner Table Snack Platter)
# ==============================================================================
def build_nachos_pizza_tray():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",        ( 0.00,  0.00, 0.00), ( 0.00, -0.10, 0.00), None),
        ("Pizza_Slice", (-0.12, -0.02, 0.04), (-0.12, -0.02, 0.12), "Root"),
        ("Pretzel",     ( 0.14,  0.04, 0.04), ( 0.14,  0.04, 0.12), "Root"),
        ("Cheese_Cup",  ( 0.04, -0.08, 0.03), ( 0.04, -0.08, 0.10), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Coral_Pink - retro diner serving tray
    # 1: Bowling_Cream_Pearl - checkered paper liner & dip cup
    # 2: Bowling_Pretzel_Crust - golden baked pretzel & pizza crust
    # 3: Bowling_Bumper_Yellow - melted nacho cheese & pizza mozzarella
    # 4: Bowling_Crimson_Stripe - pepperoni slices & salsa
    # 5: Bowling_Arcade_Green - jalapeno slices
    mats = [
        "Bowling_Coral_Pink", "Bowling_Cream_Pearl", "Bowling_Pretzel_Crust",
        "Bowling_Bumper_Yellow", "Bowling_Crimson_Stripe", "Bowling_Arcade_Green"
    ]

    # Diner Serving Tray (width = 0.48 m, depth = 0.34 m, Z = 0.00 to 0.035 m)
    add_weighted_box(bm, deform, (0.0, 0.0, 0.012), 0.48, 0.34, 0.024, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, 0.0, 0.025), 0.42, 0.28, 0.006, mat_idx=1, vg_idx=b_idx["Root"])

    # 1. Pepperoni Pizza Slice (`Pizza_Slice` bone at X = -0.12 m)
    add_weighted_box(bm, deform, (-0.12, -0.01, 0.040), 0.15, 0.18, 0.018, mat_idx=3, vg_idx=b_idx["Pizza_Slice"], rot_deg=(0.0, 0.0, 15.0))
    add_weighted_box(bm, deform, (-0.14,  0.07, 0.048), 0.16, 0.035, 0.028, mat_idx=2, vg_idx=b_idx["Pizza_Slice"], rot_deg=(0.0, 0.0, 15.0))
    for px, py in [(-0.12, -0.04), (-0.09, 0.02), (-0.15, 0.01)]:
        add_weighted_tube(bm, deform, [((px, py, 0.048), 0.020), ((px, py, 0.054), 0.020)], sides=8, mat_idx=4, vg_idx=b_idx["Pizza_Slice"])

    # 2. Twisted Golden Soft Pretzel (`Pretzel` bone at X = +0.14, Y = +0.04 m)
    add_weighted_tube(bm, deform, [
        ((0.08, 0.00, 0.042), 0.014),
        ((0.09, 0.09, 0.045), 0.016),
        ((0.14, 0.11, 0.046), 0.017),
        ((0.19, 0.09, 0.045), 0.016),
        ((0.20, 0.00, 0.042), 0.014),
        ((0.14, 0.04, 0.048), 0.015),
    ], sides=6, mat_idx=2, closed_ring=True, vg_idx=b_idx["Pretzel"])

    # 3. Nacho Cheese Dip Cup & Tortilla Chips (`Cheese_Cup` bone at X = +0.04, Y = -0.08 m)
    add_weighted_tube(bm, deform, [
        ((0.04, -0.08, 0.028), 0.036),
        ((0.04, -0.08, 0.068), 0.044),
    ], sides=8, mat_idx=1, mat_end_idx=3, vg_idx=b_idx["Cheese_Cup"])
    # Tortilla chips around the cup
    for cx, cy, rz in [(0.13, -0.08, 25.0), (0.17, -0.05, -20.0), (0.09, -0.11, 45.0)]:
        add_weighted_box(bm, deform, (cx, cy, 0.042), 0.055, 0.045, 0.008, mat_idx=3, vg_idx=b_idx["Root"], rot_deg=(18.0, 0.0, rz))

    rig_obj, rest_mat = create_rig("SnackTray_Rig", bone_specs)
    finalize_rigged_mesh("SnackTray_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Grab_Pizza",   (-0.12, -0.02, 0.06), parent=rig_obj, bone_parent="Pizza_Slice")
    make_empty("Grab_Pretzel", ( 0.14,  0.04, 0.06), parent=rig_obj, bone_parent="Pretzel")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Snack_Grab_Bounce (28f: pizza slice and pretzel lift up playfully and settle)
    act_bounce = bpy.data.actions.new(name="Snack_Grab_Bounce")
    act_bounce.use_fake_user = True
    rig_obj.animation_data.action = act_bounce
    for f, dz1, dz2, r_ang in [(1, 0.0, 0.0, 0.0), (8, 0.08, 0.03, 14.0), (16, 0.02, 0.09, -14.0), (28, 0.0, 0.0, 0.0)]:
        key_frame(f, rot_map={"Pizza_Slice": (r_ang, 0.0, 0.0), "Pretzel": (-r_ang, 0.0, 0.0)},
                  loc_map={"Pizza_Slice": (0.0, 0.0, dz1), "Pretzel": (0.0, 0.0, dz2)})

    # 2. Cheese_Dip_Dunk (24f: pretzel dips over into the warm nacho cheese cup and returns)
    act_dunk = bpy.data.actions.new(name="Cheese_Dip_Dunk")
    act_dunk.use_fake_user = True
    rig_obj.animation_data.action = act_dunk
    for f, dx, dy, dz, p_ang in [
        (1,   0.00,  0.00, 0.00,   0.0),
        (8,  -0.08, -0.10, 0.07, -30.0),
        (13, -0.10, -0.12, 0.02, -45.0),
        (19, -0.05, -0.06, 0.08, -15.0),
        (24,  0.00,  0.00, 0.00,   0.0),
    ]:
        key_frame(f, rot_map={"Pretzel": (p_ang, 0.0, 0.0)}, loc_map={"Pretzel": (dx, dy, dz)})

    save_and_export_bowling("cozy_bowling_nachos_pizza_tray", animated=True)


# ==============================================================================
# 17. cozy_bowling_popcorn_cart (1970s Illuminated Glass Popcorn Popper Machine)
# ==============================================================================
def build_popcorn_cart():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",         ( 0.00,  0.00, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Kettle_Hinge", ( 0.00,  0.00, 1.32), ( 0.00,  0.00, 1.16), "Root"),
        ("Popcorn_Heap", ( 0.00,  0.00, 0.90), ( 0.00,  0.00, 1.04), "Root"),
        ("Wheel_Spoke",  (-0.36,  0.00, 0.24), (-0.44,  0.00, 0.24), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Coral_Pink - lower cart cabinet & canopy roof
    # 1: Bowling_Gold_Brass - corner posts, spoke wheels & trim
    # 2: Bowling_Bumper_Yellow - warm buttered popcorn heap
    # 3: Bowling_Chrome_Steel - hanging kettle & push handle
    # 4: Bowling_Cream_Pearl - striped popcorn boxes & canopy stripe
    # 5: Bowling_Glass_Tint - glass enclosure panels
    mats = [
        "Bowling_Coral_Pink", "Bowling_Gold_Brass", "Bowling_Bumper_Yellow",
        "Bowling_Chrome_Steel", "Bowling_Cream_Pearl", "Bowling_Glass_Tint"
    ]

    # Lower Cart Cabinet (Z = 0.16 to 0.86 m, width = 0.68 m, depth = 0.52 m)
    add_weighted_box(bm, deform, (0.0, 0.0, 0.51), 0.68, 0.52, 0.70, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.265, 0.51), 0.54, 0.02, 0.54, mat_idx=4, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.275, 0.51), 0.42, 0.02, 0.42, mat_idx=1, vg_idx=b_idx["Root"])

    # Vintage Spoked Cart Wheels on Left (`Wheel_Spoke`) and Right + Front Caster Legs
    for sx, bname in [(-0.36, "Wheel_Spoke"), (0.36, "Wheel_Spoke")]:
        add_weighted_tube(bm, deform, [((sx - 0.02, 0.0, 0.24), 0.24), ((sx + 0.02, 0.0, 0.24), 0.24)], sides=12, mat_idx=1, vg_idx=b_idx[bname])
    for fx in (-0.26, 0.26):
        add_weighted_box(bm, deform, (fx, -0.20, 0.08), 0.04, 0.04, 0.16, mat_idx=1, vg_idx=b_idx["Root"])

    # Upper Glass Popper Enclosure (Z = 0.86 to 1.54 m): 4 Brass Corner Posts + Roof Canopy
    for cx in (-0.31, 0.31):
        for cy in (-0.23, 0.23):
            add_weighted_box(bm, deform, (cx, cy, 1.20), 0.04, 0.04, 0.68, mat_idx=1, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, 0.0, 1.58), 0.74, 0.58, 0.10, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.295, 1.58), 0.62, 0.02, 0.07, mat_idx=4, vg_idx=b_idx["Root"])

    # Hanging Stainless Steel Popper Kettle (`Kettle_Hinge` bone at Z = 1.32 m)
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 1.52), 0.016),
        ((0.0, 0.0, 1.34), 0.016),
    ], sides=6, mat_idx=3, vg_idx=b_idx["Root"])
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 1.18), 0.085),
        ((0.0, 0.0, 1.29), 0.115),
        ((0.0, 0.0, 1.32), 0.120),
    ], sides=10, mat_idx=3, mat_end_idx=1, vg_idx=b_idx["Kettle_Hinge"])

    # Golden Buttered Popcorn Heap & Striped Scoop Boxes (`Popcorn_Heap` bone at Z = 0.88..1.04 m)
    add_weighted_box(bm, deform, ( 0.00, 0.02, 0.92), 0.56, 0.40, 0.10, mat_idx=2, vg_idx=b_idx["Popcorn_Heap"])
    add_weighted_box(bm, deform, (-0.12, -0.04, 0.98), 0.26, 0.22, 0.08, mat_idx=2, vg_idx=b_idx["Popcorn_Heap"])
    # Striped Popcorn Scoop Box inside
    add_weighted_box(bm, deform, ( 0.18, -0.10, 0.96), 0.10, 0.10, 0.14, mat_idx=0, vg_idx=b_idx["Popcorn_Heap"])
    add_weighted_box(bm, deform, ( 0.18, -0.10, 1.04), 0.11, 0.11, 0.04, mat_idx=2, vg_idx=b_idx["Popcorn_Heap"])

    rig_obj, rest_mat = create_rig("Popcorn_Rig", bone_specs)
    finalize_rigged_mesh("Popcorn_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Serve_Popcorn", (0.0, -0.28, 1.05), parent=rig_obj, bone_parent="Root")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Kettle_Dump_Pop (36f: kettle tips forward to dump fresh popcorn while heap bounces up)
    act_pop = bpy.data.actions.new(name="Kettle_Dump_Pop")
    act_pop.use_fake_user = True
    rig_obj.animation_data.action = act_pop
    for f, k_pitch, h_dz in [
        (1,    0.0, 0.000),
        (10, -55.0, 0.010),
        (18, -65.0, 0.045),
        (26,  12.0, 0.020),
        (36,   0.0, 0.000),
    ]:
        key_frame(f, rot_map={"Kettle_Hinge": (k_pitch, 0.0, 0.0)}, loc_map={"Popcorn_Heap": (0.0, 0.0, h_dz)})

    # 2. Crank_Spin_Loop (30f: cart wheels rock gently while kettle stirs)
    act_spin = bpy.data.actions.new(name="Crank_Spin_Loop")
    act_spin.use_fake_user = True
    rig_obj.animation_data.action = act_spin
    for f, w_pitch, k_yaw in [(1, 0.0, 0.0), (10, 20.0, 15.0), (20, -20.0, -15.0), (30, 0.0, 0.0)]:
        key_frame(f, rot_map={"Wheel_Spoke": (w_pitch, 0.0, 0.0), "Kettle_Hinge": (0.0, 0.0, k_yaw)})

    save_and_export_bowling("cozy_bowling_popcorn_cart", animated=True)


# ==============================================================================
# 18. cozy_bowling_slushie_dispenser (Twin-Bowl Spinning Frozen Slushie Machine)
# ==============================================================================
def build_slushie_dispenser():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",         ( 0.00,  0.00, 0.00), ( 0.00, -0.12, 0.00), None),
        ("Auger_L",      (-0.14,  0.00, 0.32), (-0.14,  0.00, 0.56), "Root"),
        ("Auger_R",      ( 0.14,  0.00, 0.32), ( 0.14,  0.00, 0.56), "Root"),
        ("Tap_Handle_L", (-0.14, -0.22, 0.28), (-0.14, -0.22, 0.38), "Root"),
        ("Tap_Handle_R", ( 0.14, -0.22, 0.28), ( 0.14, -0.22, 0.38), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Chrome_Steel - brushed stainless base & drip tray
    # 1: Bowling_Neon_Pink - Left bowl Coral-Cherry slushie & lid
    # 2: Bowling_Neon_Cyan - Right bowl Blue-Raspberry slushie & lid
    # 3: Bowling_Obsidian_Ball - tap handles & vents
    # 4: Bowling_Cream_Pearl - mixing auger blades
    mats = [
        "Bowling_Chrome_Steel", "Bowling_Neon_Pink", "Bowling_Neon_Cyan",
        "Bowling_Obsidian_Ball", "Bowling_Cream_Pearl"
    ]

    # Countertop Base Unit & Front Drip Tray (Z = 0.00 to 0.28 m, width = 0.56 m, depth = 0.42 m)
    add_weighted_box(bm, deform, (0.0,  0.02, 0.14), 0.56, 0.38, 0.28, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.22, 0.025), 0.52, 0.12, 0.05, mat_idx=3, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.22, 0.052), 0.48, 0.09, 0.008, mat_idx=0, vg_idx=b_idx["Root"])

    # Left & Right Frozen Slushie Cylinders & Spinning Mixing Augers (`Auger_L`, `Auger_R`, Z = 0.28 to 0.64 m)
    for sx, abone, smat in [(-0.14, "Auger_L", 1), (0.14, "Auger_R", 2)]:
        # Slushie cylinder + domed lid
        add_weighted_tube(bm, deform, [
            ((sx, 0.0, 0.28), 0.115),
            ((sx, 0.0, 0.56), 0.115),
            ((sx, 0.0, 0.62), 0.095),
            ((sx, 0.0, 0.65), 0.035),
        ], sides=12, mat_idx=smat, mat_end_idx=4, vg_idx=b_idx[abone])
        # External mixing fin rings so the 360° spin is super readable
        add_weighted_box(bm, deform, (sx, 0.0, 0.42), 0.24, 0.03, 0.22, mat_idx=4, vg_idx=b_idx[abone])
        add_weighted_box(bm, deform, (sx, 0.0, 0.42), 0.03, 0.24, 0.22, mat_idx=4, vg_idx=b_idx[abone])

    # Pull-Down Dispenser Spigots (`Tap_Handle_L`, `Tap_Handle_R` at Y = -0.22 m, Z = 0.28 m)
    for sx, tbone, smat in [(-0.14, "Tap_Handle_L", 1), (0.14, "Tap_Handle_R", 2)]:
        add_weighted_box(bm, deform, (sx, -0.20, 0.26), 0.04, 0.07, 0.05, mat_idx=0, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (sx, -0.23, 0.32), 0.03, 0.03, 0.11, mat_idx=smat, vg_idx=b_idx[tbone])

    rig_obj, rest_mat = create_rig("Slushie_Rig", bone_specs)
    finalize_rigged_mesh("Slushie_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Cup_Fill_Spot_L", (-0.14, -0.22, 0.06), parent=rig_obj, bone_parent="Root")
    make_empty("Cup_Fill_Spot_R", ( 0.14, -0.22, 0.06), parent=rig_obj, bone_parent="Root")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Slushie_Augers_Spin (36f loop: both slushie cylinders/augers counter-rotate 360°)
    act_spin = bpy.data.actions.new(name="Slushie_Augers_Spin")
    act_spin.use_fake_user = True
    rig_obj.animation_data.action = act_spin
    for f, yaw in [(1, 0.0), (10, 90.0), (19, 180.0), (28, 270.0), (36, 360.0)]:
        key_frame(f, rot_map={"Auger_L": (0.0, 0.0, yaw), "Auger_R": (0.0, 0.0, -yaw)})

    # 2. Tap_Pull_Pour (28f: left and right tap handles pull forward to dispense slushie)
    act_pour = bpy.data.actions.new(name="Tap_Pull_Pour")
    act_pour.use_fake_user = True
    rig_obj.animation_data.action = act_pour
    for f, p_l, p_r in [(1, 0.0, 0.0), (7, 45.0, 0.0), (15, 45.0, 45.0), (22, 0.0, 45.0), (28, 0.0, 0.0)]:
        key_frame(f, rot_map={"Tap_Handle_L": (p_l, 0.0, 0.0), "Tap_Handle_R": (p_r, 0.0, 0.0)})

    save_and_export_bowling("cozy_bowling_slushie_dispenser", animated=True)


# ==============================================================================
# 19. cozy_bowling_condiment_caddy (Diner Napkin Holder, Ketchup/Mustard & Pin Shakers)
# ==============================================================================
def build_condiment_caddy():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",          ( 0.00,  0.00, 0.00), ( 0.00, -0.10, 0.00), None),
        ("Bottle_Red",    (-0.08, -0.03, 0.03), (-0.08, -0.03, 0.18), "Root"),
        ("Bottle_Yellow", ( 0.08, -0.03, 0.03), ( 0.08, -0.03, 0.18), "Root"),
        ("Pin_Shakers",   ( 0.00, -0.08, 0.03), ( 0.00, -0.08, 0.12), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Chrome_Steel - caddy wire rack & napkin dispenser
    # 1: Bowling_Crimson_Stripe - ketchup squeeze bottle & pin shaker stripe
    # 2: Bowling_Bumper_Yellow - mustard squeeze bottle
    # 3: Bowling_Cream_Pearl - napkins & miniature bowling-pin shakers
    # 4: Bowling_Teal_Seafoam - caddy base tray
    mats = [
        "Bowling_Chrome_Steel", "Bowling_Crimson_Stripe", "Bowling_Bumper_Yellow",
        "Bowling_Cream_Pearl", "Bowling_Teal_Seafoam"
    ]

    # Caddy Base Tray & Center Handle Loop (width = 0.28 m, depth = 0.22 m)
    add_weighted_box(bm, deform, (0.0, 0.0, 0.015), 0.28, 0.22, 0.03, mat_idx=4, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, 0.0, 0.035), 0.29, 0.23, 0.012, mat_idx=0, vg_idx=b_idx["Root"])
    # Rear Chrome Napkin Dispenser (Y = +0.05 m, Z = 0.03 to 0.17 m)
    add_weighted_box(bm, deform, (0.0, 0.05, 0.10), 0.15, 0.07, 0.14, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, 0.05, 0.10), 0.16, 0.04, 0.11, mat_idx=3, vg_idx=b_idx["Root"])

    # Red Ketchup & Yellow Mustard Squeeze Bottles (`Bottle_Red`, `Bottle_Yellow`)
    for bx, bname, bmat in [(-0.08, "Bottle_Red", 1), (0.08, "Bottle_Yellow", 2)]:
        add_weighted_tube(bm, deform, [
            ((bx, -0.03, 0.03), 0.032),
            ((bx, -0.03, 0.14), 0.032),
            ((bx, -0.03, 0.16), 0.016),
            ((bx, -0.03, 0.20), 0.005),
        ], sides=8, mat_idx=bmat, vg_idx=b_idx[bname])

    # Pair of Miniature Bowling-Pin Salt & Pepper Shakers (`Pin_Shakers` bone at Y = -0.08 m)
    for sx in (-0.025, 0.025):
        add_weighted_tube(bm, deform, [
            ((sx, -0.08, 0.03), 0.012),
            ((sx, -0.08, 0.06), 0.018),
            ((sx, -0.08, 0.09), 0.009),
            ((sx, -0.08, 0.115), 0.014),
            ((sx, -0.08, 0.13), 0.006),
        ], sides=8, mat_idx=3, mat_end_idx=0, vg_idx=b_idx["Pin_Shakers"])

    rig_obj, rest_mat = create_rig("Caddy_Rig", bone_specs)
    finalize_rigged_mesh("Caddy_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Grab_Caddy", (0.0, 0.0, 0.18), parent=rig_obj, bone_parent="Root")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Caddy_Shake_Jiggle (24f: pin shakers and squeeze bottles wobble playfully)
    act_shake = bpy.data.actions.new(name="Caddy_Shake_Jiggle")
    act_shake.use_fake_user = True
    rig_obj.animation_data.action = act_shake
    for f, r_ang, dz in [(1, 0.0, 0.0), (6, 16.0, 0.02), (12, -16.0, 0.0), (18, 10.0, 0.01), (24, 0.0, 0.0)]:
        key_frame(f, rot_map={
            "Bottle_Red":    (0.0,  r_ang, 0.0),
            "Bottle_Yellow": (0.0, -r_ang, 0.0),
            "Pin_Shakers":   (r_ang, 0.0, 0.0),
        }, loc_map={"Pin_Shakers": (0.0, 0.0, dz)})

    # 2. Squeeze_Bottles_Hop (28f: ketchup and mustard bottles hop up and tip forward)
    act_hop = bpy.data.actions.new(name="Squeeze_Bottles_Hop")
    act_hop.use_fake_user = True
    rig_obj.animation_data.action = act_hop
    for f, dz_r, dz_y, p_ang in [(1, 0.0, 0.0, 0.0), (8, 0.07, 0.0, 28.0), (16, 0.0, 0.07, -28.0), (28, 0.0, 0.0, 0.0)]:
        key_frame(f, rot_map={"Bottle_Red": (p_ang, 0.0, 0.0), "Bottle_Yellow": (-p_ang, 0.0, 0.0)},
                  loc_map={"Bottle_Red": (0.0, 0.0, dz_r), "Bottle_Yellow": (0.0, 0.0, dz_y)})

    save_and_export_bowling("cozy_bowling_condiment_caddy", animated=True)


if __name__ == "__main__":
    build_trophy_case()
    build_ball_rack_tiered()
    build_chalk_cone_pedestal()
    build_leaderboard_chalkboard()
    build_lane_oiler_cart()
    build_nachos_pizza_tray()
    build_popcorn_cart()
    build_slushie_dispenser()
    build_condiment_caddy()
