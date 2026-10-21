"""
Builds and exports the 8 Solo Practice, Trick-Shot, Scoring, Court Props & Arena models:
9.  cozy_tt_robot_launcher
10. cozy_tt_target_flip_bullseye
11. cozy_tt_target_cup_pyramid
12. cozy_tt_scoreboard_flip
13. cozy_tt_ball_hopper_caddy
14. cozy_tt_paddle_rack_stand
15. cozy_tt_barrier_surround
16. cozy_tt_arena_showcase
"""

import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector, Euler

sys.path.insert(0, "C:/argon/table_tennis")
import tt_utils as U
from build_tt_tables_paddles_balls import add_table_leaf_geometry, add_net_assembly


def build_robot_launcher():
    """
    9. Automated Ping-Pong Ball Robot Launcher (cozy_tt_robot_launcher)
    Base sits at Z=0.0 (can clamp onto table end at Z=0.761m or stand on its tripod/pedestal).
    Total height: 0.56 m, width: 0.34 m, depth: 0.32 m.
    """
    asset_name = "cozy_tt_robot_launcher"
    U.clear_scene()
    mats = U.create_tt_palette()

    bone_specs = [
        ("Root", None, (0.0, 0.0, 0.0), (0.0, 0.0, 0.15), False),
        ("Base_Pedestal", "Root", (0.0, 0.0, 0.0), (0.0, 0.0, 0.22), False),
        ("Hopper_Agitator", "Base_Pedestal", (0.0, 0.02, 0.14), (0.0, 0.02, 0.28), False),
        ("Head_Yaw", "Base_Pedestal", (0.0, -0.02, 0.26), (0.0, -0.02, 0.38), False),
        ("Head_Pitch", "Head_Yaw", (0.0, -0.04, 0.36), (0.0, -0.16, 0.36), False),
        ("Wheel_Top", "Head_Pitch", (0.0, -0.13, 0.405), (0.05, -0.13, 0.405), False),
        ("Wheel_Bottom", "Head_Pitch", (0.0, -0.13, 0.315), (0.05, -0.13, 0.315), False),
    ]
    arm_obj, mesh_obj, vg = U.create_armature_and_mesh(asset_name, bone_specs, mats)
    bm = bmesh.new()

    # Heavy weighted mounting base & control box
    U.add_weighted_box(bm, (0.0, 0.02, 0.025), (0.26, 0.24, 0.05), mat_idx=3, vg_idx=vg["Base_Pedestal"], chamfer=0.005)
    U.add_weighted_box(bm, (0.0, 0.10, 0.08), (0.18, 0.08, 0.07), mat_idx=13, vg_idx=vg["Base_Pedestal"], chamfer=0.004)
    # Brass speed & spin dials on control box
    for x_d in (-0.05, 0.0, 0.05):
        U.add_weighted_cylinder(bm, (x_d, 0.10, 0.12), 0.014, 0.012, 0.015, segs=16, mat_idx=5, vg_idx=vg["Base_Pedestal"])

    # Central feed column
    U.add_weighted_cylinder(bm, (0.0, 0.0, 0.15), 0.045, 0.042, 0.22, segs=24, mat_idx=3, vg_idx=vg["Base_Pedestal"])

    # Clear Acrylic Hopper Bowl (Z = 0.12 to 0.28)
    U.add_weighted_cylinder(bm, (0.0, 0.02, 0.19), 0.09, 0.155, 0.14, segs=28, mat_idx=18, vg_idx=vg["Base_Pedestal"], cap_ends=False)
    # Brass rim around hopper top
    U.add_weighted_cylinder(bm, (0.0, 0.02, 0.26), 0.157, 0.157, 0.010, segs=28, mat_idx=5, vg_idx=vg["Base_Pedestal"], cap_ends=False)

    # 18 Visible Practice Balls inside the hopper (bound to Hopper_Agitator so they swirl!)
    for idx in range(18):
        layer = idx // 6
        ang = (idx % 6) * (math.pi / 3.0) + layer * 0.5
        r_ring = 0.052 + layer * 0.032
        bx = r_ring * math.cos(ang)
        by = 0.02 + r_ring * math.sin(ang)
        bz = 0.155 + layer * 0.034
        b_mat = 17 if (idx % 2 == 0) else 16
        U.add_weighted_sphere(bm, (bx, by, bz), radius=0.020, subdivisions=2, mat_idx=b_mat, vg_idx=vg["Hopper_Agitator"])

    # Yaw Turret Fork (Head_Yaw)
    U.add_weighted_cylinder(bm, (0.0, -0.01, 0.28), 0.052, 0.048, 0.04, segs=24, mat_idx=4, vg_idx=vg["Head_Yaw"])
    for x_side in (-0.068, 0.068):
        U.add_weighted_box(bm, (x_side, -0.03, 0.335), (0.018, 0.055, 0.095), mat_idx=3, vg_idx=vg["Head_Yaw"], chamfer=0.003)

    # Pitch Barrel Housing (Head_Pitch, shooting toward -Y)
    U.add_weighted_cylinder(
        bm, (0.0, -0.08, 0.36), 0.054, 0.050, 0.15, segs=24,
        mat_idx=13, vg_idx=vg["Head_Pitch"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
    )
    # Glowing Pre-Shot LED Indicator Ring at muzzle
    U.add_weighted_cylinder(
        bm, (0.0, -0.152, 0.36), 0.051, 0.051, 0.008, segs=24,
        mat_idx=20, vg_idx=vg["Head_Pitch"], rot_euler=(math.pi * 0.5, 0.0, 0.0), cap_ends=False
    )

    # Top & Bottom Foam Flywheel Rollers (Wheel_Top, Wheel_Bottom)
    U.add_weighted_cylinder(
        bm, (0.0, -0.13, 0.405), 0.034, 0.034, 0.036, segs=20,
        mat_idx=6, vg_idx=vg["Wheel_Top"], rot_euler=(0.0, math.pi * 0.5, 0.0)
    )
    U.add_weighted_cylinder(
        bm, (0.0, -0.13, 0.315), 0.034, 0.034, 0.036, segs=20,
        mat_idx=14, vg_idx=vg["Wheel_Bottom"], rot_euler=(0.0, math.pi * 0.5, 0.0)
    )

    U.finalize_bmesh(bm, mesh_obj)

    sockets = [
        U.add_socket_empty("Muzzle_Launch_Socket", (0.0, -0.165, 0.360), arm_obj),
        U.add_socket_empty("Hopper_Top_Refill", (0.0, 0.02, 0.270), arm_obj),
        U.add_socket_empty("Table_Clamp_Origin", (0.0, 0.0, 0.000), arm_obj),
    ]

    reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all = U.make_pose_helpers(arm_obj)
    scene = bpy.context.scene
    actions = []

    # 1. Robot_Idle_Scan
    act1 = U.start_action(arm_obj, "Robot_Idle_Scan")
    for f, yaw in [(1, 0.0), (15, -18.0), (30, +18.0), (45, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Head_Yaw", 0.0, 0.0, yaw)
        set_world_rot("Hopper_Agitator", 0.0, 0.0, f * 8.0)
        key_all(f)
    actions.append(act1)

    # 2. Robot_Oscillate_Sweep_Fire
    act2 = U.start_action(arm_obj, "Robot_Oscillate_Sweep_Fire")
    for f, yaw, pitch in [(1, -26.0, +6.0), (20, +26.0, +12.0), (40, -26.0, +6.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Head_Yaw", 0.0, 0.0, yaw)
        set_world_rot("Head_Pitch", pitch, 0.0, 0.0)
        set_world_rot("Wheel_Top", f * -36.0, 0.0, 0.0)
        set_world_rot("Wheel_Bottom", f * +18.0, 0.0, 0.0)
        set_world_rot("Hopper_Agitator", 0.0, 0.0, f * 18.0)
        key_all(f)
    actions.append(act2)

    # 3. Robot_Topspin_High_Pitch
    act3 = U.start_action(arm_obj, "Robot_Topspin_High_Pitch")
    for f in (1, 15, 30):
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Head_Pitch", +16.0, 0.0, 0.0)
        set_world_rot("Wheel_Top", f * -48.0, 0.0, 0.0)
        set_world_rot("Wheel_Bottom", f * +12.0, 0.0, 0.0)
        set_world_rot("Hopper_Agitator", 0.0, 0.0, f * 12.0)
        key_all(f)
    actions.append(act3)

    # 4. Robot_Backspin_Low_Cut
    act4 = U.start_action(arm_obj, "Robot_Backspin_Low_Cut")
    for f in (1, 15, 30):
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Head_Pitch", -8.0, 0.0, 0.0)
        set_world_rot("Wheel_Top", f * +12.0, 0.0, 0.0)
        set_world_rot("Wheel_Bottom", f * -48.0, 0.0, 0.0)
        set_world_rot("Hopper_Agitator", 0.0, 0.0, f * 12.0)
        key_all(f)
    actions.append(act4)

    U.push_actions_to_muted_nla(arm_obj, actions)
    scene.frame_set(1)
    reset_pose()
    U.export_9_formats(asset_name, arm_obj, mesh_obj, sockets)


def build_target_flip_bullseye():
    """
    10. Magnetic Arcade Flip-Paddle Bullseye Target (cozy_tt_target_flip_bullseye)
    Sits on table corners for trick-shot accuracy drills (0.24 x 0.14 x 0.26 m).
    """
    asset_name = "cozy_tt_target_flip_bullseye"
    U.clear_scene()
    mats = U.create_tt_palette()

    bone_specs = [
        ("Root", None, (0.0, 0.0, 0.0), (0.0, 0.0, 0.08), False),
        ("Outer_Ring_Flip", "Root", (0.0, 0.0, 0.13), (0.0, 0.0, 0.22), False),
        ("Bullseye_Center_Spin", "Root", (0.0, 0.0, 0.13), (0.0, -0.05, 0.13), False),
        ("Flag_Popup", "Root", (0.0, 0.02, 0.21), (0.0, 0.02, 0.27), False),
    ]
    arm_obj, mesh_obj, vg = U.create_armature_and_mesh(asset_name, bone_specs, mats)
    bm = bmesh.new()

    # Weighted rubber & brass base
    U.add_weighted_box(bm, (0.0, 0.0, 0.012), (0.22, 0.12, 0.024), mat_idx=3, vg_idx=vg["Root"], chamfer=0.004)
    # Twin brass uprights + top crossbar
    for x_s in (-0.095, 0.095):
        U.add_weighted_cylinder(bm, (x_s, 0.0, 0.12), 0.009, 0.009, 0.20, segs=16, mat_idx=5, vg_idx=vg["Root"])
    U.add_weighted_cylinder(
        bm, (0.0, 0.0, 0.215), 0.008, 0.008, 0.20, segs=16,
        mat_idx=5, vg_idx=vg["Root"], rot_euler=(0.0, math.pi * 0.5, 0.0)
    )

    # Outer Blue/White Target Ring (Outer_Ring_Flip)
    U.add_weighted_cylinder(
        bm, (0.0, 0.0, 0.13), 0.072, 0.072, 0.010, segs=28,
        mat_idx=0, vg_idx=vg["Outer_Ring_Flip"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
    )
    U.add_weighted_cylinder(
        bm, (0.0, -0.0055, 0.13), 0.056, 0.056, 0.002, segs=28,
        mat_idx=2, vg_idx=vg["Outer_Ring_Flip"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
    )

    # Center Red/Gold Bullseye Spinner (Bullseye_Center_Spin)
    U.add_weighted_cylinder(
        bm, (0.0, -0.007, 0.13), 0.034, 0.034, 0.006, segs=24,
        mat_idx=6, vg_idx=vg["Bullseye_Center_Spin"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
    )
    U.add_weighted_cylinder(
        bm, (0.0, -0.0105, 0.13), 0.014, 0.014, 0.002, segs=20,
        mat_idx=5, vg_idx=vg["Bullseye_Center_Spin"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
    )

    # Popup "100 PT" Gold/Red Flag on top (Flag_Popup)
    U.add_weighted_cylinder(bm, (0.0, 0.015, 0.24), 0.004, 0.004, 0.06, segs=12, mat_idx=5, vg_idx=vg["Flag_Popup"])
    U.add_weighted_box(bm, (0.025, 0.015, 0.258), (0.05, 0.006, 0.028), mat_idx=6, vg_idx=vg["Flag_Popup"], chamfer=0.001)

    U.finalize_bmesh(bm, mesh_obj)

    sockets = [
        U.add_socket_empty("Bullseye_Hit_Center", (0.0, -0.012, 0.130), arm_obj),
        U.add_socket_empty("Target_Base_Origin", (0.0, 0.0, 0.000), arm_obj),
    ]

    reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all = U.make_pose_helpers(arm_obj)
    scene = bpy.context.scene
    actions = []

    # 1. Target_Idle
    act1 = U.start_action(arm_obj, "Target_Idle")
    for f, deg in [(1, 0.0), (15, 4.0), (30, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Flag_Popup", -85.0, 0.0, 0.0)
        set_world_rot("Outer_Ring_Flip", deg, 0.0, 0.0)
        key_all(f)
    actions.append(act1)

    # 2. Target_Hit_Spin_Flip (Ring flips backward 85°, center spins 720°, flag pops up!)
    act2 = U.start_action(arm_obj, "Target_Hit_Spin_Flip")
    for f, ring_p, bull_r, flag_p in [
        (1, 0.0, 0.0, -85.0),
        (5, -82.0, 240.0, +10.0),
        (14, -88.0, 580.0, -5.0),
        (24, -85.0, 720.0, 0.0),
    ]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Outer_Ring_Flip", ring_p, 0.0, 0.0)
        set_world_rot("Bullseye_Center_Spin", bull_r, 0.0, 0.0)
        set_world_rot("Flag_Popup", flag_p, 0.0, 0.0)
        key_all(f)
    actions.append(act2)

    # 3. Target_Reset
    act3 = U.start_action(arm_obj, "Target_Reset")
    for f, ring_p, flag_p in [(1, -85.0, 0.0), (12, +10.0, -90.0), (20, 0.0, -85.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Outer_Ring_Flip", ring_p, 0.0, 0.0)
        set_world_rot("Flag_Popup", flag_p, 0.0, 0.0)
        key_all(f)
    actions.append(act3)

    U.push_actions_to_muted_nla(arm_obj, actions)
    scene.frame_set(1)
    reset_pose()
    U.export_9_formats(asset_name, arm_obj, mesh_obj, sockets)


def build_target_cup_pyramid():
    """
    11. 6-Cup Trick-Shot Pyramid (cozy_tt_target_cup_pyramid)
    3 base cups, 2 middle cups, 1 golden crown cup on top. Each cup has its own bone for physics/animation scatter!
    """
    asset_name = "cozy_tt_target_cup_pyramid"
    U.clear_scene()
    mats = U.create_tt_palette()

    cup_h = 0.115
    cup_r_bot = 0.031
    cup_r_top = 0.046
    dx = 0.096

    cup_positions = [
        ("Cup_01", (-dx, 0.0, 0.0), 6),
        ("Cup_02", (0.0, 0.0, 0.0), 6),
        ("Cup_03", (+dx, 0.0, 0.0), 6),
        ("Cup_04", (-dx * 0.5, 0.0, cup_h), 6),
        ("Cup_05", (+dx * 0.5, 0.0, cup_h), 6),
        ("Cup_06_Gold", (0.0, 0.0, cup_h * 2.0), 5),
    ]

    bone_specs = [("Root", None, (0.0, 0.0, 0.0), (0.0, 0.0, 0.10), False)]
    for cname, (cx, cy, cz), _ in cup_positions:
        bone_specs.append((cname, "Root", (cx, cy, cz), (cx, cy, cz + cup_h), False))

    arm_obj, mesh_obj, vg = U.create_armature_and_mesh(asset_name, bone_specs, mats)
    bm = bmesh.new()

    for cname, (cx, cy, cz), cmat in cup_positions:
        # Cup body (inverted or upright party cup with white Rolled Lip)
        U.add_weighted_cylinder(
            bm, (cx, cy, cz + cup_h * 0.5), cup_r_bot, cup_r_top, cup_h - 0.006,
            segs=24, mat_idx=cmat, vg_idx=vg[cname]
        )
        # Crisp white rolled top lip
        U.add_weighted_cylinder(
            bm, (cx, cy, cz + cup_h - 0.003), cup_r_top + 0.002, cup_r_top + 0.002, 0.006,
            segs=24, mat_idx=2, vg_idx=vg[cname]
        )

    U.finalize_bmesh(bm, mesh_obj)

    sockets = [
        U.add_socket_empty("Pyramid_Center_Hit", (0.0, -0.04, cup_h * 1.4), arm_obj),
        U.add_socket_empty("Pyramid_Base_Origin", (0.0, 0.0, 0.0), arm_obj),
    ]

    reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all = U.make_pose_helpers(arm_obj)
    scene = bpy.context.scene
    actions = []

    # 1. Pyramid_Idle
    act1 = U.start_action(arm_obj, "Pyramid_Idle")
    for f, rot in [(1, 0.0), (15, 1.5), (30, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Cup_06_Gold", 0.0, 0.0, rot)
        key_all(f)
    actions.append(act1)

    # 2. Pyramid_Strike_Scatter (explosive smash hit!)
    act2 = U.start_action(arm_obj, "Pyramid_Strike_Scatter")
    scatter_Vectors = {
        "Cup_01": ((-0.14, +0.18, 0.0), (75.0, -45.0, 30.0)),
        "Cup_02": ((+0.02, +0.28, 0.0), (88.0, 12.0, -25.0)),
        "Cup_03": ((+0.16, +0.16, 0.0), (72.0, +50.0, -40.0)),
        "Cup_04": ((-0.22, +0.24, -cup_h + 0.03), (-85.0, -60.0, 55.0)),
        "Cup_05": ((+0.20, +0.26, -cup_h + 0.03), (86.0, +42.0, -65.0)),
        "Cup_06_Gold": ((0.00, +0.36, -cup_h * 2.0 + 0.03), (92.0, -20.0, 110.0)),
    }
    for f, t in [(1, 0.0), (6, 0.45), (14, 1.0), (26, 1.0)]:
        scene.frame_set(f)
        reset_pose()
        arc = math.sin(min(1.0, t * 1.2) * math.pi) * 0.14 if f < 14 else 0.0
        for cname, ((dx_v, dy_v, dz_v), (rx, ry, rz)) in scatter_Vectors.items():
            set_world_loc(cname, dx_v * t, dy_v * t, dz_v * t + arc)
            set_world_rot(cname, rx * t, ry * t, rz * t)
        key_all(f)
    actions.append(act2)

    # 3. Pyramid_Stack_Reset
    act3 = U.start_action(arm_obj, "Pyramid_Stack_Reset")
    for f, t in [(1, 1.0), (15, 0.0), (24, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        for cname, ((dx_v, dy_v, dz_v), (rx, ry, rz)) in scatter_Vectors.items():
            set_world_loc(cname, dx_v * t, dy_v * t, dz_v * t)
            set_world_rot(cname, rx * t, ry * t, rz * t)
        key_all(f)
    actions.append(act3)

    U.push_actions_to_muted_nla(arm_obj, actions)
    scene.frame_set(1)
    reset_pose()
    U.export_9_formats(asset_name, arm_obj, mesh_obj, sockets)


def build_scoreboard_flip():
    """
    12. Tabletop Umpire Mechanical Flip-Card Scoreboard (cozy_tt_scoreboard_flip)
    Dimensions: 0.48 x 0.18 x 0.26 m.
    """
    asset_name = "cozy_tt_scoreboard_flip"
    U.clear_scene()
    mats = U.create_tt_palette()

    bone_specs = [
        ("Root", None, (0.0, 0.0, 0.0), (0.0, 0.0, 0.15), False),
        ("Flip_Point_Home", "Root", (-0.14, 0.0, 0.225), (-0.14, 0.0, 0.125), False),
        ("Flip_Point_Away", "Root", (+0.14, 0.0, 0.225), (+0.14, 0.0, 0.125), False),
        ("Flip_Set_Home", "Root", (-0.045, 0.0, 0.225), (-0.045, 0.0, 0.155), False),
        ("Flip_Set_Away", "Root", (+0.045, 0.0, 0.225), (+0.045, 0.0, 0.155), False),
    ]
    arm_obj, mesh_obj, vg = U.create_armature_and_mesh(asset_name, bone_specs, mats)
    bm = bmesh.new()

    # Walnut & dark steel A-frame easel body
    U.add_weighted_box(bm, (0.0, 0.0, 0.015), (0.48, 0.17, 0.03), mat_idx=9, vg_idx=vg["Root"], chamfer=0.004)
    U.add_weighted_box(bm, (0.0, 0.0, 0.125), (0.45, 0.08, 0.20), mat_idx=3, vg_idx=vg["Root"], chamfer=0.004)
    # Top brass binder rod & rings
    U.add_weighted_cylinder(
        bm, (0.0, 0.0, 0.232), 0.008, 0.008, 0.47, segs=18,
        mat_idx=5, vg_idx=vg["Root"], rot_euler=(0.0, math.pi * 0.5, 0.0)
    )

    # Large Point Flip Cards (Home Blue at X=-0.14, Away Red at X=+0.14)
    for x_c, mat_card, bname in [
        (-0.14, 0, "Flip_Point_Home"),
        (+0.14, 6, "Flip_Point_Away"),
    ]:
        # Static back stack
        U.add_weighted_box(bm, (x_c, -0.043, 0.14), (0.11, 0.006, 0.14), mat_idx=mat_card, vg_idx=vg["Root"], chamfer=0.001)
        # Active flipping card + white score digit bar
        U.add_weighted_box(bm, (x_c, -0.050, 0.145), (0.108, 0.004, 0.135), mat_idx=mat_card, vg_idx=vg[bname], chamfer=0.001)
        U.add_weighted_box(bm, (x_c, -0.053, 0.145), (0.055, 0.002, 0.085), mat_idx=2, vg_idx=vg[bname])

    # Smaller Set Flip Cards (Home at X=-0.045, Away at X=+0.045)
    for x_s, bname in [(-0.045, "Flip_Set_Home"), (+0.045, "Flip_Set_Away")]:
        U.add_weighted_box(bm, (x_s, -0.048, 0.165), (0.058, 0.004, 0.095), mat_idx=12, vg_idx=vg[bname], chamfer=0.001)
        U.add_weighted_box(bm, (x_s, -0.051, 0.165), (0.028, 0.002, 0.055), mat_idx=5, vg_idx=vg[bname])

    U.finalize_bmesh(bm, mesh_obj)

    sockets = [
        U.add_socket_empty("Scoreboard_Base", (0.0, 0.0, 0.0), arm_obj),
    ]

    reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all = U.make_pose_helpers(arm_obj)
    scene = bpy.context.scene
    actions = []

    # 1. Score_Flip_Point_Home (flips 360° over the top ring)
    act1 = U.start_action(arm_obj, "Score_Flip_Point_Home")
    for f, deg in [(1, 0.0), (12, -180.0), (24, -360.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Flip_Point_Home", deg, 0.0, 0.0)
        key_all(f)
    actions.append(act1)

    # 2. Score_Flip_Point_Away
    act2 = U.start_action(arm_obj, "Score_Flip_Point_Away")
    for f, deg in [(1, 0.0), (12, -180.0), (24, -360.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Flip_Point_Away", deg, 0.0, 0.0)
        key_all(f)
    actions.append(act2)

    # 3. Score_Set_Win_Flip
    act3 = U.start_action(arm_obj, "Score_Set_Win_Flip")
    for f, deg in [(1, 0.0), (12, -180.0), (24, -360.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Flip_Set_Home", deg, 0.0, 0.0)
        set_world_rot("Flip_Set_Away", deg, 0.0, 0.0)
        key_all(f)
    actions.append(act3)

    U.push_actions_to_muted_nla(arm_obj, actions)
    scene.frame_set(1)
    reset_pose()
    U.export_9_formats(asset_name, arm_obj, mesh_obj, sockets)


def build_ball_hopper_caddy():
    """
    13. Rolling Multi-Ball Practice Hopper Caddy (cozy_tt_ball_hopper_caddy)
    Dimensions: 0.44 x 0.44 x 0.86 m. Holds 36 visible white & orange balls at waist height!
    """
    asset_name = "cozy_tt_ball_hopper_caddy"
    U.clear_scene()
    mats = U.create_tt_palette()

    bone_specs = [
        ("Root", None, (0.0, 0.0, 0.0), (0.0, 0.0, 0.25), False),
        ("Caddy_Frame", "Root", (0.0, 0.0, 0.08), (0.0, 0.0, 0.82), False),
        ("Bag_Basket", "Caddy_Frame", (0.0, 0.0, 0.52), (0.0, 0.0, 0.84), False),
    ]
    arm_obj, mesh_obj, vg = U.create_armature_and_mesh(asset_name, bone_specs, mats)
    bm = bmesh.new()

    # 4 Chrome Tubular Corner Legs + Caster Wheels
    for x_s in (-0.17, 0.17):
        for y_s in (-0.17, 0.17):
            U.add_weighted_cylinder(bm, (x_s, y_s, 0.45), 0.011, 0.011, 0.74, segs=14, mat_idx=4, vg_idx=vg["Caddy_Frame"])
            # Caster wheel
            U.add_weighted_cylinder(
                bm, (x_s, y_s, 0.035), 0.035, 0.035, 0.022, segs=16,
                mat_idx=12, vg_idx=vg["Caddy_Frame"], rot_euler=(0.0, math.pi * 0.5, 0.0)
            )
    # Lower storage shelf at Z = 0.18
    U.add_weighted_box(bm, (0.0, 0.0, 0.18), (0.34, 0.34, 0.02), mat_idx=3, vg_idx=vg["Caddy_Frame"], chamfer=0.003)

    # Upper Navy Canvas Ball Bag (Z = 0.50 to 0.82)
    U.add_weighted_box(bm, (0.0, 0.0, 0.65), (0.36, 0.36, 0.28), mat_idx=8, vg_idx=vg["Bag_Basket"], chamfer=0.01)
    # Gold trim rim around bag top
    for x_s in (-0.18, 0.18):
        U.add_weighted_box(bm, (x_s, 0.0, 0.795), (0.018, 0.37, 0.022), mat_idx=5, vg_idx=vg["Bag_Basket"])
    for y_s in (-0.18, 0.18):
        U.add_weighted_box(bm, (0.0, y_s, 0.795), (0.37, 0.018, 0.022), mat_idx=5, vg_idx=vg["Bag_Basket"])

    # 25 Visible White & Orange Practice Balls heaped at the top of the basket
    for gx in range(-2, 3):
        for gy in range(-2, 3):
            bx = gx * 0.058
            by = gy * 0.058
            bz = 0.785 + 0.018 * math.cos(gx * 0.7) * math.cos(gy * 0.7)
            b_mat = 17 if ((gx + gy) % 2 == 0) else 16
            U.add_weighted_sphere(bm, (bx, by, bz), radius=0.020, subdivisions=2, mat_idx=b_mat, vg_idx=vg["Bag_Basket"])

    U.finalize_bmesh(bm, mesh_obj)

    sockets = [
        U.add_socket_empty("Ball_Grab_Top", (0.0, 0.0, 0.82), arm_obj),
        U.add_socket_empty("Caddy_Floor_Origin", (0.0, 0.0, 0.0), arm_obj),
    ]

    reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all = U.make_pose_helpers(arm_obj)
    scene = bpy.context.scene
    actions = []

    # 1. Caddy_Idle
    act1 = U.start_action(arm_obj, "Caddy_Idle")
    for f, dz in [(1, 0.0), (15, -0.004), (30, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_loc("Bag_Basket", 0.0, 0.0, dz)
        key_all(f)
    actions.append(act1)

    # 2. Caddy_Roll_And_Bounce
    act2 = U.start_action(arm_obj, "Caddy_Roll_And_Bounce")
    for f, dx, dz, tilt in [(1, 0.0, 0.0, 0.0), (12, 0.18, -0.015, 4.0), (24, 0.0, 0.0, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_loc("Caddy_Frame", dx, 0.0, 0.0)
        set_world_loc("Bag_Basket", 0.0, 0.0, dz)
        set_world_rot("Bag_Basket", tilt, 0.0, 0.0)
        key_all(f)
    actions.append(act2)

    U.push_actions_to_muted_nla(arm_obj, actions)
    scene.frame_set(1)
    reset_pose()
    U.export_9_formats(asset_name, arm_obj, mesh_obj, sockets)


def build_paddle_rack_stand():
    """
    14. Clubhouse Walnut & Brass Paddle & Ball Display Stand (cozy_tt_paddle_rack_stand)
    Dimensions: 0.56 x 0.30 x 1.12 m. Includes 4 displayed paddles, 6 balls, and draped cotton towel.
    """
    asset_name = "cozy_tt_paddle_rack_stand"
    U.clear_scene()
    mats = U.create_tt_palette()

    bone_specs = [
        ("Root", None, (0.0, 0.0, 0.0), (0.0, 0.0, 0.25), False),
        ("Stand_Frame", "Root", (0.0, 0.0, 0.0), (0.0, 0.0, 1.10), False),
        ("Towel_Sway", "Stand_Frame", (+0.26, 0.0, 0.88), (+0.26, 0.0, 0.52), False),
    ]
    arm_obj, mesh_obj, vg = U.create_armature_and_mesh(asset_name, bone_specs, mats)
    bm = bmesh.new()

    # Walnut base & twin upright pillars
    U.add_weighted_box(bm, (0.0, 0.0, 0.025), (0.54, 0.28, 0.05), mat_idx=9, vg_idx=vg["Stand_Frame"], chamfer=0.005)
    for x_s in (-0.22, 0.22):
        U.add_weighted_box(bm, (x_s, 0.04, 0.56), (0.045, 0.06, 1.04), mat_idx=9, vg_idx=vg["Stand_Frame"], chamfer=0.004)
        U.add_weighted_cylinder(bm, (x_s, 0.04, 1.095), 0.026, 0.020, 0.03, segs=16, mat_idx=5, vg_idx=vg["Stand_Frame"])

    # Upper Paddle Rack Shelf (Z = 0.88) & Lower Ball Tray Shelf (Z = 0.46)
    U.add_weighted_box(bm, (0.0, 0.0, 0.88), (0.48, 0.16, 0.03), mat_idx=9, vg_idx=vg["Stand_Frame"], chamfer=0.003)
    U.add_weighted_box(bm, (0.0, 0.0, 0.46), (0.48, 0.14, 0.035), mat_idx=9, vg_idx=vg["Stand_Frame"], chamfer=0.003)
    # Brass ball rail on lower shelf
    U.add_weighted_cylinder(
        bm, (0.0, -0.055, 0.495), 0.006, 0.006, 0.44, segs=14,
        mat_idx=5, vg_idx=vg["Stand_Frame"], rot_euler=(0.0, math.pi * 0.5, 0.0)
    )

    # 4 Displayed Paddles hanging in slots at Z = 0.88
    for idx, x_p in enumerate((-0.15, -0.05, +0.05, +0.15)):
        fh_m = 11 if idx % 2 == 0 else 15
        U.add_weighted_cylinder(bm, (x_p, -0.02, 0.93), 0.012, 0.010, 0.09, segs=12, mat_idx=10, vg_idx=vg["Stand_Frame"])
        U.add_weighted_cylinder(
            bm, (x_p, -0.02, 0.78), 0.068, 0.068, 0.010, segs=24,
            mat_idx=fh_m, vg_idx=vg["Stand_Frame"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
        )

    # 6 Displayed 3-Star Balls on lower tray
    for idx in range(6):
        bx = -0.175 + idx * 0.070
        b_mat = 16 if idx < 3 else 17
        U.add_weighted_sphere(bm, (bx, -0.02, 0.498), radius=0.020, subdivisions=2, mat_idx=b_mat, vg_idx=vg["Stand_Frame"])

    # Side Brass Towel Hook + Draped Cream Sport Towel (Towel_Sway)
    U.add_weighted_cylinder(
        bm, (+0.26, 0.02, 0.88), 0.008, 0.008, 0.06, segs=12,
        mat_idx=5, vg_idx=vg["Stand_Frame"], rot_euler=(0.0, math.pi * 0.5, 0.0)
    )
    U.add_weighted_box(bm, (+0.275, 0.02, 0.70), (0.035, 0.14, 0.36), mat_idx=21, vg_idx=vg["Towel_Sway"], chamfer=0.006)
    # Red club stripe near bottom of towel
    U.add_weighted_box(bm, (+0.276, 0.02, 0.56), (0.037, 0.142, 0.024), mat_idx=6, vg_idx=vg["Towel_Sway"])

    U.finalize_bmesh(bm, mesh_obj)

    sockets = [
        U.add_socket_empty("Slot_Paddle_01", (-0.15, -0.02, 0.88), arm_obj),
        U.add_socket_empty("Slot_Paddle_02", (-0.05, -0.02, 0.88), arm_obj),
        U.add_socket_empty("Slot_Paddle_03", (+0.05, -0.02, 0.88), arm_obj),
        U.add_socket_empty("Slot_Paddle_04", (+0.15, -0.02, 0.88), arm_obj),
    ]

    reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all = U.make_pose_helpers(arm_obj)
    scene = bpy.context.scene
    actions = []

    # 1. Stand_Towel_Breeze
    act1 = U.start_action(arm_obj, "Stand_Towel_Breeze")
    for f, roll in [(1, 0.0), (18, 6.0), (36, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Towel_Sway", 0.0, roll, 0.0)
        key_all(f)
    actions.append(act1)

    U.push_actions_to_muted_nla(arm_obj, actions)
    scene.frame_set(1)
    reset_pose()
    U.export_9_formats(asset_name, arm_obj, mesh_obj, sockets)


def build_barrier_surround():
    """
    15. Tournament Padded Court Barrier Surround (cozy_tt_barrier_surround)
    Dimensions: 2.00 m wide x 0.75 m tall x 0.36 m foot depth.
    """
    asset_name = "cozy_tt_barrier_surround"
    U.clear_scene()
    mats = U.create_tt_palette()

    bone_specs = [
        ("Root", None, (0.0, 0.0, 0.0), (0.0, 0.0, 0.25), False),
        ("Panel_Hit_Flex", "Root", (0.0, 0.0, 0.38), (0.0, -0.10, 0.38), False),
    ]
    arm_obj, mesh_obj, vg = U.create_armature_and_mesh(asset_name, bone_specs, mats)
    bm = bmesh.new()

    # Tubular steel side posts & pivoted floor feet
    for x_s in (-0.96, +0.96):
        U.add_weighted_cylinder(bm, (x_s, 0.0, 0.38), 0.016, 0.016, 0.72, segs=16, mat_idx=3, vg_idx=vg["Root"])
        U.add_weighted_box(bm, (x_s, 0.0, 0.015), (0.04, 0.36, 0.03), mat_idx=3, vg_idx=vg["Root"], chamfer=0.004)
    # Top & Bottom horizontal frame bars
    for z_b in (0.08, 0.73):
        U.add_weighted_cylinder(
            bm, (0.0, 0.0, z_b), 0.015, 0.015, 1.92, segs=16,
            mat_idx=3, vg_idx=vg["Root"], rot_euler=(0.0, math.pi * 0.5, 0.0)
        )

    # Tensioned Navy Vinyl Baffle Banner with Gold/White Club Stripe (Panel_Hit_Flex)
    U.add_weighted_box(bm, (0.0, 0.0, 0.405), (1.88, 0.014, 0.60), mat_idx=8, vg_idx=vg["Panel_Hit_Flex"], chamfer=0.002)
    U.add_weighted_box(bm, (0.0, 0.0, 0.405), (1.60, 0.018, 0.09), mat_idx=5, vg_idx=vg["Panel_Hit_Flex"])
    U.add_weighted_box(bm, (0.0, 0.0, 0.405), (1.40, 0.020, 0.035), mat_idx=2, vg_idx=vg["Panel_Hit_Flex"])

    U.finalize_bmesh(bm, mesh_obj)

    sockets = [
        U.add_socket_empty("Barrier_Origin", (0.0, 0.0, 0.0), arm_obj),
    ]

    reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all = U.make_pose_helpers(arm_obj)
    scene = bpy.context.scene
    actions = []

    # 1. Barrier_Ball_Impact_Flex
    act1 = U.start_action(arm_obj, "Barrier_Ball_Impact_Flex")
    for f, dy in [(1, 0.0), (5, +0.045), (10, -0.022), (16, +0.010), (24, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_loc("Panel_Hit_Flex", 0.0, dy, 0.0)
        key_all(f)
    actions.append(act1)

    U.push_actions_to_muted_nla(arm_obj, actions)
    scene.frame_set(1)
    reset_pose()
    U.export_9_formats(asset_name, arm_obj, mesh_obj, sockets)


def build_arena_showcase():
    """
    16. Complete Assembled Table Tennis Arena & Live Rally Station (cozy_tt_arena_showcase)
    Includes:
    - Indoor Pro Table at center (0, 0, 0)
    - South Player Paddle & North NPC Paddle animated in a continuous live rally!
    - Live Two-Tone Rally Ball bouncing & arcing over the net
    - Umpire Table + Flip Scoreboard at (+1.45, 0.0, 0.0)
    - Rolling Ball Hopper Caddy at (-1.35, -1.15, 0.0)
    - Paddle Display Stand at (-1.45, +0.60, 0.0)
    - 2 Court Barrier Surrounds behind North & South baselines
    """
    asset_name = "cozy_tt_arena_showcase"
    U.clear_scene()
    mats = U.create_tt_palette()

    bone_specs = [
        ("Root", None, (0.0, 0.0, 0.0), (0.0, 0.0, 0.25), False),
        ("Table_Base", "Root", (0.0, 0.0, 0.0), (0.0, 0.0, 0.76), False),
        ("Net_Center_Bend", "Table_Base", (0.0, 0.0, 0.85), (0.0, -0.08, 0.85), False),
        ("Paddle_Player_South", "Root", (-0.28, -1.42, 0.92), (-0.28, -1.42, 1.08), False),
        ("Paddle_NPC_North", "Root", (+0.28, +1.42, 0.92), (+0.28, +1.42, 1.08), False),
        ("Rally_Ball", "Root", (0.0, 0.0, 1.05), (0.0, 0.0, 1.09), False),
        ("Score_Flip_Card", "Root", (+1.35, -0.14, 0.88), (+1.35, -0.14, 0.78), False),
    ]
    arm_obj, mesh_obj, vg = U.create_armature_and_mesh(asset_name, bone_specs, mats)
    bm = bmesh.new()

    # 1. Center Tournament Table
    add_table_leaf_geometry(bm, -1.0, top_mat_idx=0, apron_mat_idx=6, vg_leaf=vg["Table_Base"], vg_leg=vg["Table_Base"])
    add_table_leaf_geometry(bm, +1.0, top_mat_idx=0, apron_mat_idx=6, vg_leaf=vg["Table_Base"], vg_leg=vg["Table_Base"])
    add_net_assembly(bm, post_mat_idx=8, mesh_mat_idx=7, tape_mat_idx=2, vg_post=vg["Table_Base"], vg_net_flex=vg["Net_Center_Bend"])
    for x_side in (-0.52, 0.52):
        U.add_weighted_box(bm, (x_side, 0.0, 0.40), (0.045, 0.40, 0.62), mat_idx=3, vg_idx=vg["Table_Base"], chamfer=0.003)

    # 2. South Player Paddle & North NPC Paddle
    for bname, px, py, fh_m, bh_m in [
        ("Paddle_Player_South", -0.28, -1.42, 11, 12),
        ("Paddle_NPC_North", +0.28, +1.42, 15, 14),
    ]:
        U.add_weighted_cylinder(bm, (px, py, 0.90), 0.013, 0.011, 0.09, segs=14, mat_idx=9, vg_idx=vg[bname])
        U.add_weighted_cylinder(
            bm, (px, py, 1.01), 0.075, 0.075, 0.010, segs=24,
            mat_idx=fh_m, vg_idx=vg[bname], rot_euler=(math.pi * 0.5, 0.0, 0.0)
        )

    # 3. Live Rally Ball (Rally_Ball)
    U.add_weighted_sphere(bm, (0.0, 0.0, 1.05), radius=0.022, subdivisions=2, mat_idx=17, vg_idx=vg["Rally_Ball"])

    # 4. Umpire Side Pedestal + Flip Scoreboard at (+1.35, 0.0, 0.0)
    U.add_weighted_box(bm, (+1.35, 0.0, 0.36), (0.36, 0.54, 0.72), mat_idx=9, vg_idx=vg["Table_Base"], chamfer=0.005)
    U.add_weighted_box(bm, (+1.35, 0.0, 0.82), (0.14, 0.44, 0.18), mat_idx=3, vg_idx=vg["Table_Base"], chamfer=0.003)
    U.add_weighted_box(bm, (+1.30, -0.14, 0.83), (0.01, 0.11, 0.13), mat_idx=0, vg_idx=vg["Score_Flip_Card"])
    U.add_weighted_box(bm, (+1.30, +0.14, 0.83), (0.01, 0.11, 0.13), mat_idx=6, vg_idx=vg["Table_Base"])

    # 5. Rolling Ball Hopper Caddy at (-1.35, -0.95, 0.0)
    U.add_weighted_box(bm, (-1.35, -0.95, 0.62), (0.36, 0.36, 0.28), mat_idx=8, vg_idx=vg["Table_Base"], chamfer=0.008)
    for x_s in (-1.51, -1.19):
        for y_s in (-1.11, -0.79):
            U.add_weighted_cylinder(bm, (x_s, y_s, 0.38), 0.012, 0.012, 0.74, segs=12, mat_idx=4, vg_idx=vg["Table_Base"])

    # 6. Rear North & South Court Barrier Surrounds at Y = ±2.35 m
    for y_bar in (-2.35, +2.35):
        U.add_weighted_box(bm, (0.0, y_bar, 0.40), (1.88, 0.02, 0.60), mat_idx=8, vg_idx=vg["Table_Base"], chamfer=0.002)
        U.add_weighted_box(bm, (0.0, y_bar, 0.40), (1.50, 0.025, 0.08), mat_idx=5, vg_idx=vg["Table_Base"])

    U.finalize_bmesh(bm, mesh_obj)

    sockets = [
        U.add_socket_empty("Serve_Spot_Player", (0.0, -1.35, 0.761), arm_obj),
        U.add_socket_empty("Serve_Spot_NPC", (0.0, +1.35, 0.761), arm_obj),
        U.add_socket_empty("NPC_Baseline_Center", (0.0, +1.72, 0.000), arm_obj),
        U.add_socket_empty("Player_Baseline_Center", (0.0, -1.72, 0.000), arm_obj),
    ]

    reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all = U.make_pose_helpers(arm_obj)
    scene = bpy.context.scene
    actions = []

    # 1. Arena_Live_Rally_Loop (48-frame full rally cycle with table bounces & paddle swings!)
    act1 = U.start_action(arm_obj, "Arena_Live_Rally_Loop")
    rally_keyframes = [
        # (frame, ball_dx, ball_dy, ball_dz, south_dy, south_pitch, north_dy, north_pitch)
        (1,  -0.26, -1.35, -0.10, +0.12, +28.0,  0.00,   0.0),  # South player strikes ball
        (10,  0.00,  0.00, +0.08,  0.00,   0.0,  0.00, -12.0),  # Ball clears net going North
        (17, +0.18, +0.75, -0.27,  0.00,   0.0, -0.06, -24.0),  # Bounce on North table surface (Z=0.78m)
        (24, +0.26, +1.35, -0.10,  0.00,   0.0, -0.14, +30.0),  # North NPC strikes ball back
        (34,  0.00,  0.00, +0.09, -0.05, -18.0,  0.00,   0.0),  # Ball clears net going South
        (41, -0.18, -0.75, -0.27, -0.10, -26.0,  0.00,   0.0),  # Bounce on South table surface
        (48, -0.26, -1.35, -0.10, +0.12, +28.0,  0.00,   0.0),  # Loop complete
    ]
    for f, b_dx, b_dy, b_dz, s_dy, s_p, n_dy, n_p in rally_keyframes:
        scene.frame_set(f)
        reset_pose()
        set_world_loc("Rally_Ball", b_dx, b_dy, b_dz)
        set_world_loc("Paddle_Player_South", 0.0, s_dy, 0.0)
        set_world_rot("Paddle_Player_South", s_p, 0.0, 0.0)
        set_world_loc("Paddle_NPC_North", 0.0, n_dy, 0.0)
        set_world_rot("Paddle_NPC_North", n_p, 0.0, 0.0)
        if f == 24:
            set_world_rot("Score_Flip_Card", 0.0, -180.0, 0.0)
        key_all(f)
    actions.append(act1)

    U.push_actions_to_muted_nla(arm_obj, actions)
    scene.frame_set(1)
    reset_pose()
    U.export_9_formats(asset_name, arm_obj, mesh_obj, sockets)


if __name__ == "__main__":
    build_robot_launcher()
    build_target_flip_bullseye()
    build_target_cup_pyramid()
    build_scoreboard_flip()
    build_ball_hopper_caddy()
    build_paddle_rack_stand()
    build_barrier_surround()
    build_arena_showcase()
    print("[SUCCESS] All 8 Robot, Target, Prop & Arena Table Tennis models built and exported!")
