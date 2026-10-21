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
# 20. cozy_bowling_trash_ashtray_duo (Swinging-Dome Retro Trash Bin & Chrome Stand)
# ==============================================================================
def build_trash_ashtray_duo():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",            ( 0.00,  0.00, 0.00), ( 0.00, -0.12, 0.00), None),
        ("Can_Body",        (-0.18,  0.00, 0.00), (-0.18,  0.00, 0.65), "Root"),
        ("Trash_Flap_Dome", (-0.18, -0.02, 0.78), (-0.18, -0.14, 0.78), "Can_Body"),
        ("Sand_Stand",      ( 0.24,  0.00, 0.00), ( 0.24,  0.00, 0.58), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Coral_Pink - bullet trash bin body
    # 1: Bowling_Chrome_Steel - dome lid, push flap & pedestal stand
    # 2: Bowling_Teal_Seafoam - pedestal accent band
    # 3: Bowling_Maple_Light - sand tray fill
    # 4: Bowling_Obsidian_Ball - rubber floor rings
    mats = [
        "Bowling_Coral_Pink", "Bowling_Chrome_Steel", "Bowling_Teal_Seafoam",
        "Bowling_Maple_Light", "Bowling_Obsidian_Ball"
    ]

    # 1. Coral Fiberglass Bullet Trash Can (`Can_Body` at X = -0.18 m, Z = 0.00 to 0.90 m)
    add_weighted_tube(bm, deform, [
        ((-0.18, 0.0, 0.00), 0.195),
        ((-0.18, 0.0, 0.05), 0.190),
        ((-0.18, 0.0, 0.66), 0.200),
    ], sides=12, mat_idx=0, vg_idx=b_idx["Can_Body"])
    # Chrome Dome Hood (Z = 0.66 to 0.90 m) + Swinging Push Flap (`Trash_Flap_Dome`)
    add_weighted_tube(bm, deform, [
        ((-0.18, 0.0, 0.66), 0.205),
        ((-0.18, 0.0, 0.80), 0.185),
        ((-0.18, 0.0, 0.88), 0.110),
        ((-0.18, 0.0, 0.91), 0.030),
    ], sides=12, mat_idx=1, vg_idx=b_idx["Can_Body"])
    add_weighted_box(bm, deform, (-0.18, -0.175, 0.75), 0.16, 0.025, 0.13, mat_idx=4, vg_idx=b_idx["Trash_Flap_Dome"], rot_deg=(-12.0, 0.0, 0.0))

    # 2. Chrome & Seafoam Pedestal Sand Urn (`Sand_Stand` at X = +0.24 m, Z = 0.00 to 0.62 m)
    add_weighted_tube(bm, deform, [
        ((0.24, 0.0, 0.00), 0.13),
        ((0.24, 0.0, 0.04), 0.11),
        ((0.24, 0.0, 0.44), 0.045),
        ((0.24, 0.0, 0.56), 0.125),
        ((0.24, 0.0, 0.62), 0.130),
    ], sides=10, mat_idx=2, mat_end_idx=3, vg_idx=b_idx["Sand_Stand"])
    add_weighted_tube(bm, deform, [
        ((0.24, 0.0, 0.56), 0.132),
        ((0.24, 0.0, 0.625), 0.134),
    ], sides=10, mat_idx=1, cap_start=False, cap_end=False, vg_idx=b_idx["Sand_Stand"])

    rig_obj, rest_mat = create_rig("TrashDuo_Rig", bone_specs)
    finalize_rigged_mesh("TrashDuo_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Toss_Trash_Target", (-0.18, -0.18, 0.75), parent=rig_obj, bone_parent="Trash_Flap_Dome")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Trash_Flap_Swing (28f: push-flap swings inward when trash is tossed and rocks back)
    act_flap = bpy.data.actions.new(name="Trash_Flap_Swing")
    act_flap.use_fake_user = True
    rig_obj.animation_data.action = act_flap
    for f, p_ang in [(1, 0.0), (6, -55.0), (13, 18.0), (20, -10.0), (28, 0.0)]:
        key_frame(f, rot_map={"Trash_Flap_Dome": (p_ang, 0.0, 0.0)})

    # 2. Bin_Kick_Wobble (24f: bullet bin and sand stand wobble playfully)
    act_wobble = bpy.data.actions.new(name="Bin_Kick_Wobble")
    act_wobble.use_fake_user = True
    rig_obj.animation_data.action = act_wobble
    for f, r_ang in [(1, 0.0), (6, 10.0), (12, -8.0), (18, 4.0), (24, 0.0)]:
        key_frame(f, rot_map={"Can_Body": (0.0, r_ang, 0.0), "Sand_Stand": (0.0, -r_ang * 1.2, 0.0)})

    save_and_export_bowling("cozy_bowling_trash_ashtray_duo", animated=True)


# ==============================================================================
# 21. cozy_bowling_jukebox_bubbler (1970s Glowing Arch Wurlitzer Bubble Jukebox)
# ==============================================================================
def build_jukebox_bubbler():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",              ( 0.00,  0.00, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Jukebox_Body",      ( 0.00,  0.00, 0.08), ( 0.00,  0.00, 0.85), "Root"),
        ("Vinyl_Record",      ( 0.00, -0.12, 1.08), ( 0.00, -0.12, 1.18), "Jukebox_Body"),
        ("Tone_Arm",          ( 0.14, -0.12, 1.10), ( 0.04, -0.12, 1.10), "Jukebox_Body"),
        ("Selector_Carousel", ( 0.00, -0.22, 0.84), ( 0.00, -0.28, 0.84), "Jukebox_Body"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Walnut_Dark - wooden side & back cabinet
    # 1: Bowling_Neon_Pink - glowing outer neon bubble arch tubes
    # 2: Bowling_Bumper_Yellow - warm inner arch glow & record label
    # 3: Bowling_Chrome_Steel - lower speaker grille ribs & trim
    # 4: Bowling_Teal_Seafoam - song selector panel & lower accent
    # 5: Bowling_Obsidian_Ball - 45-RPM vinyl record & feet
    # 6: Bowling_Cream_Pearl - song title cards
    mats = [
        "Bowling_Walnut_Dark", "Bowling_Neon_Pink", "Bowling_Bumper_Yellow",
        "Bowling_Chrome_Steel", "Bowling_Teal_Seafoam", "Bowling_Obsidian_Ball",
        "Bowling_Cream_Pearl"
    ]

    # Lower Cabinet & Speaker Grille (`Jukebox_Body`, width = 0.84 m, depth = 0.52 m, Z = 0.00 to 0.96 m)
    add_weighted_box(bm, deform, (0.0, 0.02, 0.48), 0.78, 0.48, 0.92, mat_idx=0, vg_idx=b_idx["Jukebox_Body"])
    # Lower front speaker grille (Teal + Chrome horizontal louvers + Yellow glow backing)
    add_weighted_box(bm, deform, (0.0, -0.225, 0.38), 0.62, 0.02, 0.56, mat_idx=2, vg_idx=b_idx["Jukebox_Body"])
    for gz in (0.16, 0.26, 0.36, 0.46, 0.56, 0.64):
        add_weighted_box(bm, deform, (0.0, -0.24, gz), 0.64, 0.03, 0.035, mat_idx=3, vg_idx=b_idx["Jukebox_Body"])
    # Vertical chrome pilasters flanking the grille
    for sx in (-0.36, 0.36):
        add_weighted_box(bm, deform, (sx, -0.23, 0.48), 0.07, 0.05, 0.90, mat_idx=1, vg_idx=b_idx["Jukebox_Body"])

    # Song Selector Button Bank (`Selector_Carousel` at Y = -0.24 m, Z = 0.82 m)
    add_weighted_box(bm, deform, (0.0, -0.23, 0.82), 0.62, 0.06, 0.16, mat_idx=4, vg_idx=b_idx["Jukebox_Body"])
    add_weighted_box(bm, deform, (0.0, -0.265, 0.83), 0.48, 0.03, 0.10, mat_idx=6, vg_idx=b_idx["Selector_Carousel"])

    # Upper Rounded Arch Record Showcase (Z = 0.94 to 1.56 m)
    # Rear dark walnut arch housing (front at Y = -0.10 m) + stepped cream interior backdrop (front at Y = -0.13 m)
    add_weighted_box(bm, deform, (0.0,  0.08, 1.18), 0.76, 0.36, 0.48, mat_idx=0, vg_idx=b_idx["Jukebox_Body"])
    add_weighted_box(bm, deform, (0.0, -0.115, 1.16), 0.58, 0.03, 0.40, mat_idx=6, vg_idx=b_idx["Jukebox_Body"])
    # Continuous Glowing Pink Neon Bubble Arch Tube around the perimeter (X = -0.38 to +0.38, Z = 0.92 to 1.56 m)
    arch_pts = []
    for i in range(9):
        ang = math.pi * (i / 8.0)
        ax = -0.37 * math.cos(ang)
        az = 1.16 + 0.37 * math.sin(ang)
        arch_pts.append(((ax, -0.21, az), 0.048))
    add_weighted_tube(bm, deform, arch_pts, sides=8, mat_idx=1, vg_idx=b_idx["Jukebox_Body"])
    # Inner Golden Neon Arch Tube
    inner_pts = []
    for i in range(9):
        ang = math.pi * (i / 8.0)
        ax = -0.30 * math.cos(ang)
        az = 1.16 + 0.30 * math.sin(ang)
        inner_pts.append(((ax, -0.19, az), 0.028))
    add_weighted_tube(bm, deform, inner_pts, sides=8, mat_idx=2, vg_idx=b_idx["Jukebox_Body"])

    # Visible 45-RPM Vinyl Record on Turntable (`Vinyl_Record` at (0, -0.12, 1.10)) + Chrome Tone Arm (`Tone_Arm`)
    add_weighted_tube(bm, deform, [
        ((0.0, -0.12, 1.07), 0.13),
        ((0.0, -0.12, 1.09), 0.13),
        ((0.0, -0.12, 1.095), 0.045),
    ], sides=12, mat_idx=5, mat_end_idx=2, vg_idx=b_idx["Vinyl_Record"])
    add_weighted_box(bm, deform, (0.09, -0.12, 1.11), 0.14, 0.02, 0.02, mat_idx=3, vg_idx=b_idx["Tone_Arm"], rot_deg=(0.0, 0.0, 20.0))

    rig_obj, rest_mat = create_rig("Jukebox_Rig", bone_specs)
    finalize_rigged_mesh("Jukebox_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Select_Song_Spot", (0.0, -0.30, 0.84), parent=rig_obj, bone_parent="Jukebox_Body")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Jukebox_Play_Groove (40f loop: vinyl record spins 360° while jukebox body sways to the beat!)
    act_groove = bpy.data.actions.new(name="Jukebox_Play_Groove")
    act_groove.use_fake_user = True
    rig_obj.animation_data.action = act_groove
    for f, rec_yaw, sway_r, arm_y in [
        (1,    0.0,  0.0,   0.0),
        (10,  90.0,  2.5,  -8.0),
        (20, 180.0,  0.0, -12.0),
        (30, 270.0, -2.5,  -8.0),
        (40, 360.0,  0.0,   0.0),
    ]:
        key_frame(f, rot_map={
            "Vinyl_Record": (0.0, 0.0, rec_yaw),
            "Jukebox_Body": (0.0, sway_r, 0.0),
            "Tone_Arm":     (0.0, 0.0, arm_y),
        })

    # 2. Record_Change_Flip (30f: tone arm swings out, record lifts and flips, song selector clicks)
    act_flip = bpy.data.actions.new(name="Record_Change_Flip")
    act_flip.use_fake_user = True
    rig_obj.animation_data.action = act_flip
    for f, arm_yaw, rec_dz, sel_p in [
        (1,    0.0, 0.00,   0.0),
        (8,   35.0, 0.06,  25.0),
        (16,  35.0, 0.08, -25.0),
        (23,  12.0, 0.02,   0.0),
        (30,   0.0, 0.00,   0.0),
    ]:
        key_frame(f, rot_map={"Tone_Arm": (0.0, 0.0, arm_yaw), "Selector_Carousel": (sel_p, 0.0, 0.0)},
                  loc_map={"Vinyl_Record": (0.0, 0.0, rec_dz)})

    save_and_export_bowling("cozy_bowling_jukebox_bubbler", animated=True)


# ==============================================================================
# 22. cozy_bowling_bill_changer ("CHANGE — $1 TO QUARTERS" Arcade Coin Machine)
# ==============================================================================
def build_bill_changer():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",              (0.00,  0.00, 0.00), (0.00, -0.12, 0.00), None),
        ("Bill_Slider",       (0.06, -0.22, 1.12), (0.06, -0.30, 1.12), "Root"),
        ("Quarter_Pile",      (0.00, -0.22, 0.78), (0.00, -0.22, 0.86), "Root"),
        ("Out_Of_Order_Sign", (0.00, -0.23, 1.30), (0.00, -0.23, 1.40), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Walnut_Dark - wood-grain cabinet sides
    # 1: Bowling_Chrome_Steel - brushed steel front plate & coin cup
    # 2: Bowling_Coral_Pink - top header ("CHANGE — QUARTERS")
    # 3: Bowling_Gold_Brass - quarters pile & trim
    # 4: Bowling_Arcade_Green - $1 dollar bill in acceptor tray
    # 5: Bowling_Obsidian_Ball - recessed coin scoop & base
    mats = [
        "Bowling_Walnut_Dark", "Bowling_Chrome_Steel", "Bowling_Coral_Pink",
        "Bowling_Gold_Brass", "Bowling_Arcade_Green", "Bowling_Obsidian_Ball"
    ]

    # Upright Cabinet Body (width = 0.46 m, depth = 0.42 m, Z = 0.00 to 1.48 m)
    add_weighted_box(bm, deform, (0.0,  0.00, 0.74), 0.46, 0.42, 1.48, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.205, 1.04), 0.40, 0.02, 0.76, mat_idx=1, vg_idx=b_idx["Root"])
    # Header Sign ("CHANGE — 25c")
    add_weighted_box(bm, deform, (0.0, -0.215, 1.34), 0.36, 0.02, 0.12, mat_idx=2, vg_idx=b_idx["Out_Of_Order_Sign"])
    add_weighted_box(bm, deform, (0.0, -0.225, 1.34), 0.30, 0.015, 0.05, mat_idx=3, vg_idx=b_idx["Out_Of_Order_Sign"])

    # $1 Bill Acceptor Slot & Green Dollar Bill (`Bill_Slider` at (0.06, -0.22, 1.12))
    add_weighted_box(bm, deform, (0.06, -0.22, 1.12), 0.12, 0.03, 0.08, mat_idx=5, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.06, -0.25, 1.12), 0.08, 0.07, 0.012, mat_idx=4, vg_idx=b_idx["Bill_Slider"])

    # Coin Dispense Catch Cup (Z = 0.76 to 0.90 m) + Golden Quarter Pile (`Quarter_Pile`)
    add_weighted_box(bm, deform, (0.0, -0.22, 0.82), 0.22, 0.05, 0.14, mat_idx=5, vg_idx=b_idx["Root"])
    for qx in (-0.04, 0.0, 0.04):
        add_weighted_tube(bm, deform, [
            ((qx, -0.22, 0.77), 0.022),
            ((qx, -0.22, 0.80), 0.022),
        ], sides=8, mat_idx=3, vg_idx=b_idx["Quarter_Pile"])

    rig_obj, rest_mat = create_rig("Changer_Rig", bone_specs)
    finalize_rigged_mesh("Changer_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Insert_Bill_Spot", (0.06, -0.26, 1.12), parent=rig_obj, bone_parent="Bill_Slider")
    make_empty("Take_Quarters",    (0.00, -0.24, 0.80), parent=rig_obj, bone_parent="Quarter_Pile")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Dispense_Quarters_Clatter (30f: $1 bill slides in, then golden quarters pop up and clatter in the tray!)
    act_disp = bpy.data.actions.new(name="Dispense_Quarters_Clatter")
    act_disp.use_fake_user = True
    rig_obj.animation_data.action = act_disp
    for f, b_dy, q_dz, q_r in [
        (1,  0.000, 0.000,   0.0),
        (8,  0.055, 0.000,   0.0),
        (14, 0.055, 0.045,  18.0),
        (21, 0.055, 0.015, -14.0),
        (30, 0.000, 0.000,   0.0),
    ]:
        key_frame(f, rot_map={"Quarter_Pile": (0.0, q_r, 0.0)},
                  loc_map={"Bill_Slider": (0.0, b_dy, 0.0), "Quarter_Pile": (0.0, 0.0, q_dz)})

    # 2. Out_Of_Order_Flip (24f: top sign flips 180° when machine is empty)
    act_sign = bpy.data.actions.new(name="Out_Of_Order_Flip")
    act_sign.use_fake_user = True
    rig_obj.animation_data.action = act_sign
    for f, p_ang in [(1, 0.0), (8, 180.0), (16, 180.0), (24, 360.0)]:
        key_frame(f, rot_map={"Out_Of_Order_Sign": (p_ang, 0.0, 0.0)})

    save_and_export_bowling("cozy_bowling_bill_changer", animated=True)


# ==============================================================================
# 23. cozy_bowling_gumball_tri_rack (Chrome 3-Globe Vintage Gumball Stand)
# ==============================================================================
def build_gumball_tri_rack():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",          ( 0.00,  0.00, 0.00), ( 0.00, -0.12, 0.00), None),
        ("Globe_L",       (-0.24,  0.00, 0.88), (-0.24,  0.00, 1.12), "Root"),
        ("Globe_C",       ( 0.00,  0.00, 0.92), ( 0.00,  0.00, 1.16), "Root"),
        ("Globe_R",       ( 0.24,  0.00, 0.88), ( 0.24,  0.00, 1.12), "Root"),
        ("Crank_Wheel_C", ( 0.00, -0.11, 0.78), ( 0.00, -0.16, 0.78), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Crimson_Stripe - cast-iron gumball hoppers & caps
    # 1: Bowling_Chrome_Steel - tripod pedestal, crossbar & coin cranks
    # 2: Bowling_Coral_Pink - Left globe gumballs
    # 3: Bowling_Bumper_Yellow - Center globe gumballs
    # 4: Bowling_Teal_Seafoam - Right globe prize capsules
    # 5: Bowling_Obsidian_Ball - heavy cast-iron base
    mats = [
        "Bowling_Crimson_Stripe", "Bowling_Chrome_Steel", "Bowling_Coral_Pink",
        "Bowling_Bumper_Yellow", "Bowling_Teal_Seafoam", "Bowling_Obsidian_Ball"
    ]

    # Cast-Iron Base & Chrome Column + Crossbar (Z = 0.00 to 0.70 m)
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 0.00), 0.22),
        ((0.0, 0.0, 0.05), 0.18),
        ((0.0, 0.0, 0.10), 0.07),
    ], sides=10, mat_idx=5, vg_idx=b_idx["Root"])
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 0.10), 0.038),
        ((0.0, 0.0, 0.68), 0.038),
    ], sides=8, mat_idx=1, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, 0.0, 0.69), 0.62, 0.14, 0.04, mat_idx=1, vg_idx=b_idx["Root"])

    # 3 Vintage Gumball Machines on the Rack (`Globe_L`, `Globe_C`, `Globe_R`)
    for gx, gz, gbone, gmat in [
        (-0.24, 0.71, "Globe_L", 2),
        ( 0.00, 0.73, "Globe_C", 3),
        ( 0.24, 0.71, "Globe_R", 4),
    ]:
        # Red cast-iron hopper body
        add_weighted_tube(bm, deform, [
            ((gx, 0.0, gz),        0.075),
            ((gx, 0.0, gz + 0.14), 0.090),
        ], sides=8, mat_idx=0, vg_idx=b_idx[gbone])
        # Colorful gumball globe + red top cap
        add_weighted_tube(bm, deform, [
            ((gx, 0.0, gz + 0.14), 0.085),
            ((gx, 0.0, gz + 0.23), 0.115),
            ((gx, 0.0, gz + 0.32), 0.095),
            ((gx, 0.0, gz + 0.36), 0.035),
        ], sides=10, mat_idx=gmat, mat_end_idx=0, vg_idx=b_idx[gbone])

    # Center Coin Crank Wheel (`Crank_Wheel_C` at (0, -0.11, 0.80))
    add_weighted_box(bm, deform, (0.0, -0.105, 0.80), 0.07, 0.03, 0.09, mat_idx=1, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.125, 0.80), 0.06, 0.02, 0.02, mat_idx=1, vg_idx=b_idx["Crank_Wheel_C"])

    rig_obj, rest_mat = create_rig("Gumball_Rig", bone_specs)
    finalize_rigged_mesh("Gumball_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Turn_Gumball_Crank", (0.0, -0.13, 0.80), parent=rig_obj, bone_parent="Crank_Wheel_C")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Turn_Crank_Drop_Gumball (28f: crank wheel turns 360° around Y while center globe hops)
    act_crank = bpy.data.actions.new(name="Turn_Crank_Drop_Gumball")
    act_crank.use_fake_user = True
    rig_obj.animation_data.action = act_crank
    for f, r_crank, dz in [(1, 0.0, 0.0), (10, 180.0, 0.025), (20, 360.0, -0.008), (28, 360.0, 0.0)]:
        key_frame(f, rot_map={"Crank_Wheel_C": (0.0, r_crank, 0.0)}, loc_map={"Globe_C": (0.0, 0.0, dz)})

    # 2. Globes_Jiggle_Shake (24f: all 3 gumball globes jiggle and spin slightly)
    act_shake = bpy.data.actions.new(name="Globes_Jiggle_Shake")
    act_shake.use_fake_user = True
    rig_obj.animation_data.action = act_shake
    for f, r_ang in [(1, 0.0), (6, 12.0), (12, -12.0), (18, 6.0), (24, 0.0)]:
        key_frame(f, rot_map={
            "Globe_L": (0.0,  r_ang, 0.0),
            "Globe_C": (r_ang, 0.0, 0.0),
            "Globe_R": (0.0, -r_ang, 0.0),
        })

    save_and_export_bowling("cozy_bowling_gumball_tri_rack", animated=True)


# ==============================================================================
# 24. cozy_bowling_arcade_stool_pair (2 Chrome Swivel Barstools — Coral & Teal)
# ==============================================================================
def build_arcade_stool_pair():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",          ( 0.00, 0.00, 0.00), ( 0.00, -0.12, 0.00), None),
        ("Seat_Swivel_1", (-0.28, 0.00, 0.62), (-0.28,  0.00, 0.76), "Root"),
        ("Seat_Swivel_2", ( 0.28, 0.00, 0.62), ( 0.28,  0.00, 0.76), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Chrome_Steel - pedestal bases, columns & foot-rings
    # 1: Bowling_Coral_Pink - Stool 1 tufted vinyl cushion
    # 2: Bowling_Teal_Seafoam - Stool 2 tufted vinyl cushion
    # 3: Bowling_Cream_Pearl - white piping & two-tone side band
    # 4: Bowling_Obsidian_Ball - non-slip floor ring
    mats = [
        "Bowling_Chrome_Steel", "Bowling_Coral_Pink", "Bowling_Teal_Seafoam",
        "Bowling_Cream_Pearl", "Bowling_Obsidian_Ball"
    ]

    for sx, sbone, smat in [(-0.28, "Seat_Swivel_1", 1), (0.28, "Seat_Swivel_2", 2)]:
        # Chrome Trumpet Base & Column (Z = 0.00 to 0.62 m)
        add_weighted_tube(bm, deform, [
            ((sx, 0.0, 0.00), 0.21),
            ((sx, 0.0, 0.03), 0.19),
            ((sx, 0.0, 0.08), 0.06),
            ((sx, 0.0, 0.62), 0.032),
        ], sides=10, mat_idx=0, vg_idx=b_idx["Root"])
        # Footrest Ring at Z = 0.26 m
        add_weighted_tube(bm, deform, [
            ((sx, 0.0, 0.25), 0.15),
            ((sx, 0.0, 0.27), 0.15),
        ], sides=10, mat_idx=0, cap_start=False, cap_end=False, vg_idx=b_idx["Root"])
        # Padded Swivel Cushion (`Seat_Swivel_1` / `Seat_Swivel_2`, Z = 0.62 to 0.74 m)
        c_rings = add_weighted_tube(bm, deform, [
            ((sx, 0.0, 0.62), 0.175),
            ((sx, 0.0, 0.66), 0.185),
            ((sx, 0.0, 0.71), 0.185),
            ((sx, 0.0, 0.74), 0.155),
        ], sides=12, mat_idx=smat, vg_idx=b_idx[sbone])
        # Cream side piping stripe so 360° swivel is readable
        add_weighted_box(bm, deform, (sx, 0.0, 0.685), 0.375, 0.06, 0.04, mat_idx=3, vg_idx=b_idx[sbone])

    rig_obj, rest_mat = create_rig("Stools_Rig", bone_specs)
    finalize_rigged_mesh("Stools_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Sit_Stool_1", (-0.28, 0.0, 0.75), parent=rig_obj, bone_parent="Seat_Swivel_1")
    make_empty("Sit_Stool_2", ( 0.28, 0.0, 0.75), parent=rig_obj, bone_parent="Seat_Swivel_2")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Stool_Spin_360 (36f loop: both stools swivel 360° in opposite directions)
    act_spin = bpy.data.actions.new(name="Stool_Spin_360")
    act_spin.use_fake_user = True
    rig_obj.animation_data.action = act_spin
    for f, yaw in [(1, 0.0), (10, 90.0), (19, 180.0), (28, 270.0), (36, 360.0)]:
        key_frame(f, rot_map={"Seat_Swivel_1": (0.0, 0.0, yaw), "Seat_Swivel_2": (0.0, 0.0, -yaw)})

    # 2. Stool_Sit_Bounce (24f: cushions compress down and spring back with a swivel twist)
    act_sit = bpy.data.actions.new(name="Stool_Sit_Bounce")
    act_sit.use_fake_user = True
    rig_obj.animation_data.action = act_sit
    for f, dz, yaw in [(1, 0.0, 0.0), (7, -0.038, 25.0), (15, 0.010, -12.0), (24, 0.0, 0.0)]:
        key_frame(f, rot_map={"Seat_Swivel_1": (0.0, 0.0, yaw), "Seat_Swivel_2": (0.0, 0.0, -yaw)},
                  loc_map={"Seat_Swivel_1": (0.0, 0.0, dz), "Seat_Swivel_2": (0.0, 0.0, dz)})

    save_and_export_bowling("cozy_bowling_arcade_stool_pair", animated=True)


# ==============================================================================
# 25. cozy_bowling_neon_wall_signs (3-Piece Retro 3D Neon Sign Set)
# ==============================================================================
def build_neon_wall_signs():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",       ( 0.00,  0.00, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Neon_Arrow", (-0.65, -0.05, 0.00), (-0.45, -0.05, 0.00), "Root"),
        ("Neon_Pin",   ( 0.00, -0.05, 0.00), ( 0.00, -0.05, 0.35), "Root"),
        ("Star_Spark", ( 0.65, -0.05, 0.08), ( 0.65, -0.05, 0.28), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Obsidian_Ball - dark mid-century backing shields
    # 1: Bowling_Neon_Pink - glowing coral-pink neon tubing & arrow
    # 2: Bowling_Neon_Cyan - glowing electric cyan neon border & waves
    # 3: Bowling_Bumper_Yellow - golden starburst sparks & chaser bulbs
    # 4: Bowling_Cream_Pearl - neon pin silhouette
    # 5: Bowling_Teal_Seafoam - sign trim
    mats = [
        "Bowling_Obsidian_Ball", "Bowling_Neon_Pink", "Bowling_Neon_Cyan",
        "Bowling_Bumper_Yellow", "Bowling_Cream_Pearl", "Bowling_Teal_Seafoam"
    ]

    # 1. Left Sign: "ARCADE ->" Neon Arrow (`Neon_Arrow` at X = -0.65 m)
    add_weighted_box(bm, deform, (-0.65,  0.00, 0.00), 0.54, 0.04, 0.28, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (-0.65, -0.025, 0.00), 0.50, 0.02, 0.22, mat_idx=5, vg_idx=b_idx["Root"])
    # Raised 3D Glowing Pink Neon Arrow (`Neon_Arrow` bone)
    add_weighted_box(bm, deform, (-0.70, -0.05, 0.00), 0.32, 0.03, 0.07, mat_idx=1, vg_idx=b_idx["Neon_Arrow"])
    add_weighted_box(bm, deform, (-0.52, -0.05, 0.05), 0.14, 0.03, 0.04, mat_idx=1, vg_idx=b_idx["Neon_Arrow"], rot_deg=(0.0, 38.0, 0.0))
    add_weighted_box(bm, deform, (-0.52, -0.05,-0.05), 0.14, 0.03, 0.04, mat_idx=1, vg_idx=b_idx["Neon_Arrow"], rot_deg=(0.0,-38.0, 0.0))

    # 2. Center Sign: "BOWL!" Crashing Neon Pin & Cyan Ring (`Neon_Pin` at X = 0.0 m)
    add_weighted_box(bm, deform, (0.0,  0.00, 0.00), 0.52, 0.04, 0.52, mat_idx=0, vg_idx=b_idx["Root"], rot_deg=(0.0, 45.0, 0.0))
    add_weighted_box(bm, deform, (0.0, -0.025, 0.00), 0.44, 0.02, 0.44, mat_idx=2, vg_idx=b_idx["Root"], rot_deg=(0.0, 45.0, 0.0))
    add_weighted_tube(bm, deform, [
        ((0.0, -0.05, -0.22), 0.045),
        ((0.0, -0.05, -0.08), 0.085),
        ((0.0, -0.05,  0.06), 0.042),
        ((0.0, -0.05,  0.18), 0.062),
        ((0.0, -0.05,  0.24), 0.025),
    ], sides=8, mat_idx=4, mat_end_idx=1, vg_idx=b_idx["Neon_Pin"])

    # 3. Right Sign: "STRIKE!" Atomic Starburst (`Star_Spark` at X = +0.65 m)
    add_weighted_box(bm, deform, (0.65, 0.00, 0.00), 0.50, 0.04, 0.36, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.65, -0.025, -0.06), 0.42, 0.02, 0.10, mat_idx=1, vg_idx=b_idx["Root"])
    for ray_i in range(4):
        ang = ray_i * 45.0
        add_weighted_box(bm, deform, (0.65, -0.05, 0.08), 0.28, 0.03, 0.04, mat_idx=3, vg_idx=b_idx["Star_Spark"], rot_deg=(0.0, ang, 0.0))

    rig_obj, rest_mat = create_rig("NeonSigns_Rig", bone_specs)
    finalize_rigged_mesh("NeonSigns_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Neon_Center", (0.0, -0.06, 0.0), parent=rig_obj, bone_parent="Root")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Neon_Sign_Pulse_Tilt (40f loop: neon pin tilts, starburst spins, arrow pulses)
    act_pulse = bpy.data.actions.new(name="Neon_Sign_Pulse_Tilt")
    act_pulse.use_fake_user = True
    rig_obj.animation_data.action = act_pulse
    for f, p_roll, s_roll, a_dx in [
        (1,   0.0,   0.0,  0.00),
        (10, 16.0,  45.0,  0.04),
        (20,  0.0,  90.0,  0.00),
        (30,-16.0, 135.0, -0.02),
        (40,  0.0, 180.0,  0.00),
    ]:
        key_frame(f, rot_map={"Neon_Pin": (0.0, p_roll, 0.0), "Star_Spark": (0.0, s_roll, 0.0)},
                  loc_map={"Neon_Arrow": (a_dx, 0.0, 0.0)})

    # 2. Arrow_Chaser_Bounce (24f: neon arrow darts right 3 times while starburst pops)
    act_arrow = bpy.data.actions.new(name="Arrow_Chaser_Bounce")
    act_arrow.use_fake_user = True
    rig_obj.animation_data.action = act_arrow
    for f, dx, sc in [(1, 0.0, 1.0), (6, 0.06, 1.2), (12, 0.0, 1.0), (18, 0.06, 1.2), (24, 0.0, 1.0)]:
        key_frame(f, loc_map={"Neon_Arrow": (dx, 0.0, 0.0)}, scale_map={"Star_Spark": (sc, sc, sc)})

    save_and_export_bowling("cozy_bowling_neon_wall_signs", animated=True)


# ==============================================================================
# 26. cozy_bowling_sputnik_clock (Mid-Century Brass Starburst Wall Clock & Sconces)
# ==============================================================================
def build_sputnik_clock():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",        (0.0,  0.00, 0.0), (0.0, -0.12, 0.00), None),
        ("Hand_Hour",   (0.0, -0.06, 0.0), (0.0, -0.06, 0.14), "Root"),
        ("Hand_Minute", (0.0, -0.07, 0.0), (0.0, -0.07, 0.20), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Gold_Brass - 12 starburst spokes & bezel
    # 1: Bowling_Coral_Pink - alternating atomic ball tips & sconces
    # 2: Bowling_Teal_Seafoam - alternating atomic ball tips
    # 3: Bowling_Cream_Pearl - clock dial face
    # 4: Bowling_Obsidian_Ball - clock hands
    mats = [
        "Bowling_Gold_Brass", "Bowling_Coral_Pink", "Bowling_Teal_Seafoam",
        "Bowling_Cream_Pearl", "Bowling_Obsidian_Ball"
    ]

    # 12 Brass Starburst Spokes & Colored Atomic Ball Tips (Radius = 0.42 m)
    for i in range(12):
        ang_deg = i * 30.0
        ang_rad = math.radians(ang_deg)
        tx = 0.38 * math.sin(ang_rad)
        tz = 0.38 * math.cos(ang_rad)
        add_weighted_box(bm, deform, (0.0, -0.01, 0.0), 0.022, 0.02, 0.74, mat_idx=0, vg_idx=b_idx["Root"], rot_deg=(0.0, ang_deg, 0.0))
        tip_mat = 1 if (i % 2 == 0) else 2
        add_weighted_box(bm, deform, (tx, -0.02, tz), 0.055, 0.055, 0.055, mat_idx=tip_mat, vg_idx=b_idx["Root"], rot_deg=(0.0, ang_deg, 0.0))

    # Center Brass Bezel & Cream Dial Face (Radius = 0.18 m)
    add_weighted_box(bm, deform, (0.0, -0.025, 0.0), 0.28, 0.04, 0.28, mat_idx=0, vg_idx=b_idx["Root"], rot_deg=(0.0, 45.0, 0.0))
    add_weighted_box(bm, deform, (0.0, -0.045, 0.0), 0.22, 0.02, 0.22, mat_idx=3, vg_idx=b_idx["Root"], rot_deg=(0.0, 45.0, 0.0))

    # Clock Hands (`Hand_Hour`, `Hand_Minute`)
    add_weighted_box(bm, deform, (0.0, -0.06, 0.045), 0.024, 0.015, 0.10, mat_idx=4, vg_idx=b_idx["Hand_Hour"])
    add_weighted_box(bm, deform, (0.0, -0.07, 0.065), 0.016, 0.015, 0.14, mat_idx=4, vg_idx=b_idx["Hand_Minute"])

    # Flanking Left & Right Mid-Century Cone Wall Sconces (`X = +-0.62 m`)
    for sx in (-0.62, 0.62):
        add_weighted_box(bm, deform, (sx, -0.02, 0.0), 0.08, 0.06, 0.08, mat_idx=0, vg_idx=b_idx["Root"])
        add_weighted_tube(bm, deform, [
            ((sx, -0.06, -0.08), 0.025),
            ((sx, -0.06,  0.08), 0.075),
            ((sx, -0.06,  0.14), 0.095),
        ], sides=8, mat_idx=1, mat_end_idx=3, vg_idx=b_idx["Root"])

    rig_obj, rest_mat = create_rig("Clock_Rig", bone_specs)
    finalize_rigged_mesh("Clock_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Clock_Center", (0.0, -0.08, 0.0), parent=rig_obj, bone_parent="Root")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Clock_Tick_Loop (48f loop: minute hand sweeps 360° while hour hand advances 30°)
    act_tick = bpy.data.actions.new(name="Clock_Tick_Loop")
    act_tick.use_fake_user = True
    rig_obj.animation_data.action = act_tick
    for f, m_ang, h_ang in [(1, 0.0, 0.0), (13, 90.0, 7.5), (25, 180.0, 15.0), (37, 270.0, 22.5), (48, 360.0, 30.0)]:
        key_frame(f, rot_map={"Hand_Minute": (0.0, m_ang, 0.0), "Hand_Hour": (0.0, h_ang, 0.0)})

    # 2. Strike_Hour_Chime (24f: clock hands spin rapidly and whole clock shivers on the hour)
    act_chime = bpy.data.actions.new(name="Strike_Hour_Chime")
    act_chime.use_fake_user = True
    rig_obj.animation_data.action = act_chime
    for f, m_ang, r_root in [(1, 0.0, 0.0), (6, 120.0, 6.0), (12, 240.0, -6.0), (18, 360.0, 4.0), (24, 360.0, 0.0)]:
        key_frame(f, rot_map={"Hand_Minute": (0.0, m_ang, 0.0), "Root": (0.0, r_root, 0.0)})

    save_and_export_bowling("cozy_bowling_sputnik_clock", animated=True)


# ==============================================================================
# 27. cozy_bowling_planter_divider (Slatted Wood Room Divider with Tropical Plants)
# ==============================================================================
def build_planter_divider():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",            ( 0.00, 0.0, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Plant_Cluster_L", (-0.52, 0.0, 0.42), (-0.52,  0.00, 0.92), "Root"),
        ("Plant_Cluster_C", ( 0.00, 0.0, 0.42), ( 0.00,  0.00, 0.98), "Root"),
        ("Plant_Cluster_R", ( 0.52, 0.0, 0.42), ( 0.52,  0.00, 0.92), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Cream_Pearl - terrazzo planter trough
    # 1: Bowling_Maple_Light - vertical mid-century wood privacy slats
    # 2: Bowling_Walnut_Dark - planter soil bed & top/bottom slat rails
    # 3: Bowling_Plant_Green - lush tropical Monstera & snake plant leaves
    # 4: Bowling_Gold_Brass - brass plinth feet & trim
    # 5: Bowling_Coral_Pink - decorative planter stripe
    mats = [
        "Bowling_Cream_Pearl", "Bowling_Maple_Light", "Bowling_Walnut_Dark",
        "Bowling_Plant_Green", "Bowling_Gold_Brass", "Bowling_Coral_Pink"
    ]

    # Terrazzo Planter Box on Brass Feet (width = 1.68 m, depth = 0.38 m, Z = 0.00 to 0.44 m)
    add_weighted_box(bm, deform, (0.0, 0.0, 0.04), 1.62, 0.34, 0.08, mat_idx=4, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, 0.0, 0.25), 1.68, 0.38, 0.34, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.195, 0.25), 1.56, 0.02, 0.08, mat_idx=5, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, 0.0, 0.425), 1.58, 0.28, 0.02, mat_idx=2, vg_idx=b_idx["Root"])

    # Rear Slatted Mid-Century Wood Privacy Screen (`Y = +0.14 m`, Z = 0.42 to 1.64 m)
    add_weighted_box(bm, deform, (0.0, 0.14, 1.62), 1.68, 0.06, 0.05, mat_idx=2, vg_idx=b_idx["Root"])
    for i in range(11):
        sx = -0.75 + i * 0.15
        add_weighted_box(bm, deform, (sx, 0.14, 1.02), 0.045, 0.05, 1.18, mat_idx=1, vg_idx=b_idx["Root"])

    # 3 Lush Tropical Snake-Plant & Monstera Leaf Clusters (`Plant_Cluster_L`, `Plant_Cluster_C`, `Plant_Cluster_R`)
    for cx, cbone in [(-0.52, "Plant_Cluster_L"), (0.0, "Plant_Cluster_C"), (0.52, "Plant_Cluster_R")]:
        for dx, dy, h_top, tilt_x, tilt_y in [
            ( 0.00,  0.00, 0.98,   4.0,   0.0),
            (-0.12, -0.04, 0.88,  12.0, -16.0),
            ( 0.12, -0.04, 0.90,  10.0,  16.0),
            (-0.08,  0.05, 0.84,  -8.0, -10.0),
            ( 0.08,  0.05, 0.86,  -8.0,  10.0),
        ]:
            add_weighted_box(
                bm, deform,
                (cx + dx, dy, 0.42 + (h_top - 0.42) * 0.5),
                0.08, 0.025, h_top - 0.42,
                mat_idx=3, vg_idx=b_idx[cbone],
                rot_deg=(tilt_x, tilt_y, 0.0)
            )

    rig_obj, rest_mat = create_rig("Planter_Rig", bone_specs)
    finalize_rigged_mesh("Planter_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Foliage_Center", (0.0, 0.0, 0.78), parent=rig_obj, bone_parent="Plant_Cluster_C")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Leaves_Breeze_Sway (48f loop: tropical foliage sways gently in staggered phase)
    act_sway = bpy.data.actions.new(name="Leaves_Breeze_Sway")
    act_sway.use_fake_user = True
    rig_obj.animation_data.action = act_sway
    for f, r_l, r_c, r_r in [
        (1,   0.0,  0.0,  0.0),
        (12,  7.0,  4.0, -5.0),
        (24,  0.0,  8.0,  0.0),
        (36, -7.0, -4.0,  6.0),
        (48,  0.0,  0.0,  0.0),
    ]:
        key_frame(f, rot_map={
            "Plant_Cluster_L": (0.0, r_l, 0.0),
            "Plant_Cluster_C": (r_c * 0.5, r_c, 0.0),
            "Plant_Cluster_R": (0.0, r_r, 0.0),
        })

    # 2. Plant_Touch_Rustle (24f: quick rustle when a player brushes past the leaves)
    act_rustle = bpy.data.actions.new(name="Plant_Touch_Rustle")
    act_rustle.use_fake_user = True
    rig_obj.animation_data.action = act_rustle
    for f, r_ang in [(1, 0.0), (5, 16.0), (10, -14.0), (16, 8.0), (24, 0.0)]:
        key_frame(f, rot_map={
            "Plant_Cluster_L": (r_ang, -r_ang, 0.0),
            "Plant_Cluster_C": (-r_ang, r_ang, 0.0),
            "Plant_Cluster_R": (r_ang, r_ang, 0.0),
        })

    save_and_export_bowling("cozy_bowling_planter_divider", animated=True)


# ==============================================================================
# 28. cozy_bowling_window_display_podium (Storefront Window Turntable & Retro Bag)
# ==============================================================================
def build_window_display_podium():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",              ( 0.00, 0.00, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Turntable_Top",     ( 0.00, 0.00, 0.16), ( 0.00,  0.00, 0.36), "Root"),
        ("Giant_Display_Pin", (-0.20, 0.04, 0.24), (-0.20,  0.04, 1.05), "Turntable_Top"),
        ("Bowling_Bag_Retro", ( 0.20,-0.04, 0.24), ( 0.20, -0.04, 0.58), "Turntable_Top"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Teal_Seafoam - lower stepped podium base & bag body
    # 1: Bowling_Coral_Pink - upper turntable platter & bag side panels
    # 2: Bowling_Gold_Brass - podium rim trim & bag hardware
    # 3: Bowling_Cream_Pearl - giant display pin lacquer & bag piping
    # 4: Bowling_Crimson_Stripe - giant display pin neck stripes
    mats = [
        "Bowling_Teal_Seafoam", "Bowling_Coral_Pink", "Bowling_Gold_Brass",
        "Bowling_Cream_Pearl", "Bowling_Crimson_Stripe"
    ]

    # Stepped Circular Window Podium (`Root` base + `Turntable_Top` platter, Z = 0.00 to 0.24 m)
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 0.00), 0.62),
        ((0.0, 0.0, 0.12), 0.60),
        ((0.0, 0.0, 0.14), 0.56),
    ], sides=16, mat_idx=0, mat_end_idx=2, vg_idx=b_idx["Root"])
    add_weighted_tube(bm, deform, [
        ((0.0, 0.0, 0.14), 0.48),
        ((0.0, 0.0, 0.23), 0.46),
        ((0.0, 0.0, 0.24), 0.45),
    ], sides=16, mat_idx=1, mat_end_idx=3, vg_idx=b_idx["Turntable_Top"])

    # 1. Giant 0.90 m Storefront Display Bowling Pin (`Giant_Display_Pin` on left side of turntable)
    pin_profile = [
        (0.00, 0.075), (0.14, 0.135), (0.34, 0.165), (0.52, 0.095),
        (0.62, 0.062), (0.72, 0.092), (0.84, 0.085), (0.90, 0.030),
    ]
    p_rings = add_weighted_tube(
        bm, deform,
        [((-0.20, 0.04, 0.24 + pz), pr) for pz, pr in pin_profile],
        sides=12, mat_idx=3, vg_idx=b_idx["Giant_Display_Pin"]
    )
    for r_i in (3, 5):
        ra, rb = set(p_rings[r_i]), set(p_rings[r_i + 1])
        for f in bm.faces:
            if all(v in ra or v in rb for v in f.verts):
                f.material_index = 4

    # 2. Retro Two-Tone Curved Leather Bowling Ball Bag (`Bowling_Bag_Retro` on right side of turntable)
    add_weighted_box(bm, deform, (0.20, -0.04, 0.34), 0.32, 0.22, 0.20, mat_idx=0, vg_idx=b_idx["Bowling_Bag_Retro"])
    add_weighted_box(bm, deform, (0.20, -0.04, 0.46), 0.26, 0.18, 0.10, mat_idx=1, vg_idx=b_idx["Bowling_Bag_Retro"])
    add_weighted_box(bm, deform, (0.20, -0.155, 0.38), 0.24, 0.02, 0.16, mat_idx=3, vg_idx=b_idx["Bowling_Bag_Retro"])
    # Twin curved leather carry handles on top
    for hy in (-0.08, 0.00):
        add_weighted_tube(bm, deform, [
            ((0.12, hy, 0.50), 0.012),
            ((0.15, hy, 0.58), 0.012),
            ((0.25, hy, 0.58), 0.012),
            ((0.28, hy, 0.50), 0.012),
        ], sides=6, mat_idx=2, vg_idx=b_idx["Bowling_Bag_Retro"])

    rig_obj, rest_mat = create_rig("Podium_Rig", bone_specs)
    finalize_rigged_mesh("Podium_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Grab_Retro_Bag", (0.20, -0.04, 0.56), parent=rig_obj, bone_parent="Bowling_Bag_Retro")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Window_Turntable_Spin (60f loop: motorized window display turntable rotates 360°)
    act_spin = bpy.data.actions.new(name="Window_Turntable_Spin")
    act_spin.use_fake_user = True
    rig_obj.animation_data.action = act_spin
    for f, yaw in [(1, 0.0), (16, 90.0), (31, 180.0), (46, 270.0), (60, 360.0)]:
        key_frame(f, rot_map={"Turntable_Top": (0.0, 0.0, yaw)})

    # 2. Display_Pin_Salute (32f: giant display pin and retro bowling bag hop and bow to mall shoppers)
    act_salute = bpy.data.actions.new(name="Display_Pin_Salute")
    act_salute.use_fake_user = True
    rig_obj.animation_data.action = act_salute
    for f, p_ang, dz in [(1, 0.0, 0.0), (8, 16.0, 0.06), (16, -12.0, 0.0), (24, 6.0, 0.03), (32, 0.0, 0.0)]:
        key_frame(f, rot_map={"Giant_Display_Pin": (p_ang, 0.0, 0.0), "Bowling_Bag_Retro": (-p_ang, 0.0, 0.0)},
                  loc_map={"Giant_Display_Pin": (0.0, 0.0, dz), "Bowling_Bag_Retro": (0.0, 0.0, dz * 0.8)})

    save_and_export_bowling("cozy_bowling_window_display_podium", animated=True)


if __name__ == "__main__":
    build_trash_ashtray_duo()
    build_jukebox_bubbler()
    build_bill_changer()
    build_gumball_tri_rack()
    build_arcade_stool_pair()
    build_neon_wall_signs()
    build_sputnik_clock()
    build_planter_divider()
    build_window_display_podium()
