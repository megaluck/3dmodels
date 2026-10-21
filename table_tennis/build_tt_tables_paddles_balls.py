"""
Builds and exports the 8 Core Match Set Table Tennis models:
1. cozy_tt_table_indoor_pro
2. cozy_tt_table_outdoor_garden
3. cozy_tt_paddle_classic
4. cozy_tt_paddle_carbon_pro
5. cozy_tt_paddle_cast_iron_pan
6. cozy_tt_ball_white_3star
7. cozy_tt_ball_orange_3star
8. cozy_tt_ball_twotone_spin
"""

import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector, Euler

sys.path.insert(0, "C:/argon/table_tennis")
import tt_utils as U


def add_table_leaf_geometry(bm, y_sign, top_mat_idx, apron_mat_idx, vg_leaf, vg_leg):
    """
    Builds one half-leaf of a regulation 2.74 x 1.525 x 0.76 m table tennis table.
    y_sign = -1 for South (Player, Y in [-1.37, -0.004]), +1 for North (NPC, Y in [+0.004, +1.37]).
    """
    half_len = 1.366
    width = 1.525
    thick = 0.025
    z_top = 0.760
    z_mid = z_top - thick * 0.5
    y_center = y_sign * (half_len * 0.5 + 0.004)

    # Main playing slab
    U.add_weighted_box(
        bm,
        center=(0.0, y_center, z_mid),
        size=(width, half_len, thick),
        mat_idx=top_mat_idx,
        vg_idx=vg_leaf,
        chamfer=0.002,
    )

    # Crisp 2 cm White Perimeter Lines (flush +0.6 mm above slab)
    line_z = z_top + 0.0005
    line_h = 0.001
    line_w = 0.020

    # End baseline (at Y = y_sign * 1.370)
    y_end = y_sign * (0.004 + half_len - line_w * 0.5)
    U.add_weighted_box(bm, (0.0, y_end, line_z), (width, line_w, line_h), mat_idx=2, vg_idx=vg_leaf)

    # Left & Right sidelines (at X = ±0.7625)
    for x_side in (-1.0, 1.0):
        x_pos = x_side * (width * 0.5 - line_w * 0.5)
        U.add_weighted_box(bm, (x_pos, y_center, line_z), (line_w, half_len, line_h), mat_idx=2, vg_idx=vg_leaf)

    # Center doubles dividing line (3 mm wide down X = 0)
    U.add_weighted_box(bm, (0.0, y_center, line_z), (0.005, half_len, line_h), mat_idx=2, vg_idx=vg_leaf)

    # Metallic/Wood Under-Apron Frame
    apron_h = 0.038
    apron_z = z_top - thick - apron_h * 0.5
    for x_side in (-1.0, 1.0):
        U.add_weighted_box(
            bm,
            (x_side * (width * 0.5 - 0.03), y_center, apron_z),
            (0.018, half_len - 0.04, apron_h),
            mat_idx=apron_mat_idx,
            vg_idx=vg_leaf,
        )
    U.add_weighted_box(
        bm,
        (0.0, y_sign * (0.004 + half_len - 0.03), apron_z),
        (width - 0.06, 0.018, apron_h),
        mat_idx=apron_mat_idx,
        vg_idx=vg_leaf,
    )

    # Outer folding support legs (at Y = y_sign * 1.12)
    y_leg = y_sign * 1.12
    for x_side in (-0.62, 0.62):
        U.add_weighted_box(
            bm,
            (x_side, y_leg, 0.365),
            (0.038, 0.038, 0.71),
            mat_idx=3,
            vg_idx=vg_leg,
            chamfer=0.003,
        )
        # Red/Gold rubber leveling foot
        U.add_weighted_cylinder(
            bm,
            (x_side, y_leg, 0.012),
            0.028,
            0.024,
            0.024,
            segs=16,
            mat_idx=6,
            vg_idx=vg_leg,
        )
        # Diagonal folding linkage strut
        U.add_weighted_cylinder(
            bm,
            (x_side * 0.88, y_sign * 0.78, 0.52),
            0.010,
            0.010,
            0.62,
            segs=12,
            mat_idx=6,
            vg_idx=vg_leg,
            rot_euler=(y_sign * 0.78, 0.0, 0.0),
        )
    # Crossbar between outer legs
    U.add_weighted_box(
        bm,
        (0.0, y_leg, 0.22),
        (1.24, 0.028, 0.028),
        mat_idx=3,
        vg_idx=vg_leg,
    )


def add_net_assembly(bm, post_mat_idx, mesh_mat_idx, tape_mat_idx, vg_post, vg_net_flex):
    """
    Regulation 1.83m wide net (15.25cm overhanging posts on each side of the 1.525m table)
    and 15.25cm high above Z=0.760m (top cord at Z=0.9125m).
    """
    z_table = 0.760
    net_h = 0.1525
    half_span = 0.915  # 1.83m total width

    # Left & Right Post Clamps + Vertical Posts + Tension Chains
    for x_sign in (-1.0, 1.0):
        x_clamp = x_sign * 0.775
        x_post = x_sign * 0.900
        # C-clamp body gripping table edge
        U.add_weighted_box(bm, (x_clamp, 0.0, z_table - 0.015), (0.055, 0.065, 0.065), mat_idx=post_mat_idx, vg_idx=vg_post, chamfer=0.003)
        # Horizontal extension arm to 15.25cm overhang
        U.add_weighted_box(bm, (x_sign * 0.838, 0.0, z_table - 0.005), (0.14, 0.032, 0.024), mat_idx=post_mat_idx, vg_idx=vg_post)
        # Vertical net post
        U.add_weighted_cylinder(bm, (x_post, 0.0, z_table + net_h * 0.5), 0.012, 0.012, net_h + 0.02, segs=16, mat_idx=post_mat_idx, vg_idx=vg_post)
        # Brass finial cap & screw knob
        U.add_weighted_cylinder(bm, (x_post, 0.0, z_table + net_h + 0.014), 0.015, 0.012, 0.012, segs=16, mat_idx=5, vg_idx=vg_post)
        U.add_weighted_cylinder(bm, (x_clamp, 0.0, z_table - 0.058), 0.016, 0.016, 0.022, segs=14, mat_idx=5, vg_idx=vg_post)

    # Segmented Net Mesh & Top White Tape (weighted between vg_post at ends and vg_net_flex at center)
    segs_x = 16
    dx = (half_span * 2.0) / segs_x
    dlayer = bm.verts.layers.deform.verify()
    for i in range(segs_x):
        x0 = -half_span + (i + 0.5) * dx
        # Bell-curve flex weight: 1.0 at X=0, 0.0 at posts
        norm_x = abs(x0) / half_span
        w_flex = max(0.0, math.cos(norm_x * math.pi * 0.5) ** 1.5)
        w_post = 1.0 - w_flex

        # Net mesh panel
        v_mesh, _ = U.add_weighted_box(
            bm,
            (x0, 0.0, z_table + (net_h - 0.018) * 0.5 + 0.004),
            (dx * 0.98, 0.004, net_h - 0.022),
            mat_idx=mesh_mat_idx,
            vg_idx=vg_post,
        )
        # Top white canvas cord tape (15 mm tall)
        v_tape, _ = U.add_weighted_box(
            bm,
            (x0, 0.0, z_table + net_h - 0.008),
            (dx * 1.00, 0.007, 0.016),
            mat_idx=tape_mat_idx,
            vg_idx=vg_post,
        )
        # Bottom trim
        v_bot, _ = U.add_weighted_box(
            bm,
            (x0, 0.0, z_table + 0.006),
            (dx * 0.98, 0.005, 0.008),
            mat_idx=post_mat_idx,
            vg_idx=vg_post,
        )
        for v in v_mesh + v_tape + v_bot:
            v[dlayer][vg_post] = w_post
            v[dlayer][vg_net_flex] = w_flex


def build_table_variant(asset_name, is_outdoor=False):
    U.clear_scene()
    mats = U.create_tt_palette()

    bone_specs = [
        ("Root", None, (0.0, 0.0, 0.0), (0.0, 0.0, 0.20), False),
        ("Undercarriage", "Root", (0.0, 0.0, 0.20), (0.0, 0.0, 0.68), False),
        ("Leaf_South", "Undercarriage", (0.0, -0.045, 0.720), (0.0, -0.80, 0.720), False),
        ("Leg_Outer_South", "Leaf_South", (0.0, -1.12, 0.710), (0.0, -1.12, 0.05), False),
        ("Leaf_North", "Undercarriage", (0.0, +0.045, 0.720), (0.0, +0.80, 0.720), False),
        ("Leg_Outer_North", "Leaf_North", (0.0, +1.12, 0.710), (0.0, +1.12, 0.05), False),
        ("Net_Posts", "Undercarriage", (0.0, 0.0, 0.760), (0.0, 0.0, 0.9125), False),
        ("Net_Center_Bend", "Net_Posts", (0.0, 0.0, 0.850), (0.0, -0.08, 0.850), False),
    ]

    arm_obj, mesh_obj, vg = U.create_armature_and_mesh(asset_name, bone_specs, mats)
    bm = bmesh.new()

    if not is_outdoor:
        # INDOOR PRO TOURNAMENT TABLE (Matte Blue Top + Dark Steel + Red/Chrome Rolling Base)
        add_table_leaf_geometry(bm, -1.0, top_mat_idx=0, apron_mat_idx=6, vg_leaf=vg["Leaf_South"], vg_leg=vg["Leg_Outer_South"])
        add_table_leaf_geometry(bm, +1.0, top_mat_idx=0, apron_mat_idx=6, vg_leaf=vg["Leaf_North"], vg_leg=vg["Leg_Outer_North"])
        add_net_assembly(bm, post_mat_idx=8, mesh_mat_idx=7, tape_mat_idx=2, vg_post=vg["Net_Posts"], vg_net_flex=vg["Net_Center_Bend"])

        # Center rolling carriage & 4 caster wheels
        for x_side in (-0.52, 0.52):
            # Bottom horizontal beam
            U.add_weighted_box(bm, (x_side, 0.0, 0.14), (0.045, 0.46, 0.045), mat_idx=3, vg_idx=vg["Undercarriage"], chamfer=0.003)
            for y_side in (-0.20, 0.20):
                # Vertical H-frame post
                U.add_weighted_box(bm, (x_side, y_side, 0.42), (0.042, 0.042, 0.56), mat_idx=3, vg_idx=vg["Undercarriage"], chamfer=0.003)
                # Caster wheel fork (chrome) + wheel (dark rubber/red hub)
                U.add_weighted_box(bm, (x_side, y_side, 0.095), (0.036, 0.048, 0.05), mat_idx=4, vg_idx=vg["Undercarriage"])
                U.add_weighted_cylinder(
                    bm, (x_side, y_side, 0.055), 0.055, 0.055, 0.032, segs=20,
                    mat_idx=12, vg_idx=vg["Undercarriage"], rot_euler=(0.0, math.pi * 0.5, 0.0)
                )
                U.add_weighted_cylinder(
                    bm, (x_side, y_side, 0.055), 0.025, 0.025, 0.036, segs=16,
                    mat_idx=6, vg_idx=vg["Undercarriage"], rot_euler=(0.0, math.pi * 0.5, 0.0)
                )
        # Central tie-bar with ball/paddle storage tray
        U.add_weighted_box(bm, (0.0, 0.0, 0.34), (1.08, 0.16, 0.04), mat_idx=3, vg_idx=vg["Undercarriage"], chamfer=0.003)
    else:
        # OUTDOOR GARDEN PARK TABLE (Forest Green Top + Warm Teak Wood Trim + Brass Perforated Net)
        add_table_leaf_geometry(bm, -1.0, top_mat_idx=1, apron_mat_idx=9, vg_leaf=vg["Leaf_South"], vg_leg=vg["Leg_Outer_South"])
        add_table_leaf_geometry(bm, +1.0, top_mat_idx=1, apron_mat_idx=9, vg_leaf=vg["Leaf_North"], vg_leg=vg["Leg_Outer_North"])
        add_net_assembly(bm, post_mat_idx=5, mesh_mat_idx=5, tape_mat_idx=2, vg_post=vg["Net_Posts"], vg_net_flex=vg["Net_Center_Bend"])

        # Heavy Teak & Wrought-Iron Courtyard Pedestal Base
        for x_side in (-0.50, 0.50):
            U.add_weighted_box(bm, (x_side, 0.0, 0.06), (0.09, 0.56, 0.08), mat_idx=9, vg_idx=vg["Undercarriage"], chamfer=0.005)
            for y_side in (-0.18, 0.18):
                U.add_weighted_box(bm, (x_side, y_side, 0.40), (0.065, 0.065, 0.62), mat_idx=9, vg_idx=vg["Undercarriage"], chamfer=0.004)
                U.add_weighted_box(bm, (x_side, y_side, 0.015), (0.10, 0.10, 0.03), mat_idx=5, vg_idx=vg["Undercarriage"], chamfer=0.003)
        U.add_weighted_box(bm, (0.0, 0.0, 0.38), (1.04, 0.14, 0.07), mat_idx=9, vg_idx=vg["Undercarriage"], chamfer=0.004)

    U.finalize_bmesh(bm, mesh_obj)

    # Gameplay Sockets
    sockets = [
        U.add_socket_empty("Serve_Spot_Player", (0.0, -1.35, 0.761), arm_obj),
        U.add_socket_empty("Serve_Spot_NPC", (0.0, +1.35, 0.761), arm_obj),
        U.add_socket_empty("Bounce_Zone_South_L", (-0.38, -0.68, 0.761), arm_obj),
        U.add_socket_empty("Bounce_Zone_South_R", (+0.38, -0.68, 0.761), arm_obj),
        U.add_socket_empty("Bounce_Zone_North_L", (-0.38, +0.68, 0.761), arm_obj),
        U.add_socket_empty("Bounce_Zone_North_R", (+0.38, +0.68, 0.761), arm_obj),
        U.add_socket_empty("Net_Top_Center", (0.0, 0.0, 0.9125), arm_obj),
        U.add_socket_empty("Robot_Mount_North", (0.0, +1.370, 0.761), arm_obj),
        U.add_socket_empty("Paddle_Rest_South", (-0.48, -1.15, 0.762), arm_obj),
        U.add_socket_empty("Paddle_Rest_North", (+0.48, +1.15, 0.762), arm_obj),
        U.add_socket_empty("NPC_Baseline_Center", (0.0, +1.72, 0.000), arm_obj),
    ]

    # Animations
    reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all = U.make_pose_helpers(arm_obj)
    scene = bpy.context.scene
    actions = []

    # 1. Table_Match_Ready_Idle (subtle net breeze)
    act1 = U.start_action(arm_obj, "Table_Match_Ready_Idle")
    for f, dy in [(1, 0.0), (20, 0.003), (40, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_loc("Net_Center_Bend", 0.0, dy, 0.0)
        key_all(f)
    actions.append(act1)

    # 2. Table_Net_Cord_Let_Jiggle (when ball clips top of net)
    act2 = U.start_action(arm_obj, "Table_Net_Cord_Let_Jiggle")
    jiggle_frames = [
        (1, 0.0, 0.0),
        (4, -0.032, -0.012),
        (8, +0.024, +0.006),
        (12, -0.016, -0.005),
        (16, +0.010, +0.003),
        (21, -0.005, -0.002),
        (28, 0.0, 0.0),
    ]
    for f, dy, dz in jiggle_frames:
        scene.frame_set(f)
        reset_pose()
        set_world_loc("Net_Center_Bend", 0.0, dy, dz)
        key_all(f)
    actions.append(act2)

    # 3. Table_Solo_Playback_Wall_Fold (North leaf folds up 90° for solo practice!)
    act3 = U.start_action(arm_obj, "Table_Solo_Playback_Wall_Fold")
    for f, t in [(1, 0.0), (25, 1.0), (45, 1.0), (70, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Leaf_North", pitch_deg=-90.0 * t, roll_deg=0.0, yaw_deg=0.0)
        set_world_rot("Leg_Outer_North", pitch_deg=+88.0 * t, roll_deg=0.0, yaw_deg=0.0)
        key_all(f)
    actions.append(act3)

    # 4. Table_Storage_Fold_Both (Both halves fold upright for rolling storage)
    act4 = U.start_action(arm_obj, "Table_Storage_Fold_Both")
    for f, t in [(1, 0.0), (30, 1.0), (50, 1.0), (80, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Leaf_North", pitch_deg=-86.0 * t, roll_deg=0.0, yaw_deg=0.0)
        set_world_rot("Leg_Outer_North", pitch_deg=+85.0 * t, roll_deg=0.0, yaw_deg=0.0)
        set_world_rot("Leaf_South", pitch_deg=+86.0 * t, roll_deg=0.0, yaw_deg=0.0)
        set_world_rot("Leg_Outer_South", pitch_deg=-85.0 * t, roll_deg=0.0, yaw_deg=0.0)
        key_all(f)
    actions.append(act4)

    U.push_actions_to_muted_nla(arm_obj, actions)
    scene.frame_set(1)
    reset_pose()
    U.export_9_formats(asset_name, arm_obj, mesh_obj, sockets)


def build_paddle_variant(asset_name, style="classic"):
    """
    Builds a standalone Table Tennis Paddle (0.152 m wide x 0.258 m long).
    Origin (0,0,0) is at the center of the flared handle grip so it snaps directly to a player/NPC hand!
    Blade extends along +Z (0.045 to 0.205 m), Forehand face normal is -Y, Backhand face normal is +Y.
    """
    U.clear_scene()
    mats = U.create_tt_palette()

    bone_specs = [
        ("Root", None, (0.0, 0.0, -0.05), (0.0, 0.0, 0.05), False),
        ("Wrist_Pivot", "Root", (0.0, 0.0, 0.00), (0.0, 0.0, 0.055), False),
        ("Blade_Flex", "Wrist_Pivot", (0.0, 0.0, 0.055), (0.0, 0.0, 0.195), False),
    ]
    arm_obj, mesh_obj, vg = U.create_armature_and_mesh(asset_name, bone_specs, mats)
    bm = bmesh.new()

    if style in ("classic", "carbon"):
        handle_mat = 9 if style == "classic" else 13
        wood_mat = 10 if style == "classic" else 13
        fh_mat = 11 if style == "classic" else 15  # Red vs Magenta
        bh_mat = 12 if style == "classic" else 14  # Black vs Cyan
        edge_mat = 2 if style == "classic" else 5

        # Flared ergonomic handle (Z from -0.052 to +0.050)
        segs_h = 8
        for i in range(segs_h):
            t0 = i / segs_h
            z0 = -0.050 + t0 * 0.100
            flare = 1.0 + 0.32 * ((1.0 - t0) ** 2)
            U.add_weighted_box(
                bm,
                (0.0, 0.0, z0),
                (0.028 * flare, 0.022 * (0.9 + 0.15 * (1.0 - t0)), 0.0135),
                mat_idx=handle_mat,
                vg_idx=vg["Wrist_Pivot"],
                chamfer=0.003,
            )
        # Brass butt-cap badge at bottom of handle
        U.add_weighted_cylinder(
            bm, (0.0, 0.0, -0.054), 0.011, 0.013, 0.004, segs=16, mat_idx=5, vg_idx=vg["Wrist_Pivot"]
        )

        # Oval Tear-drop Paddle Blade (Center at Z = 0.125, Rx = 0.076, Rz = 0.082)
        # Core wooden/carbon blade
        U.add_weighted_cylinder(
            bm, (0.0, 0.0, 0.125), 0.076, 0.076, 0.006, segs=32,
            mat_idx=wood_mat, vg_idx=vg["Blade_Flex"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
        )
        # Protective edge tape ring
        U.add_weighted_cylinder(
            bm, (0.0, 0.0, 0.125), 0.0768, 0.0768, 0.0085, segs=32,
            mat_idx=edge_mat, vg_idx=vg["Blade_Flex"], rot_euler=(math.pi * 0.5, 0.0, 0.0), cap_ends=False
        )
        # Forehand Sponge Rubber (-Y face)
        U.add_weighted_cylinder(
            bm, (0.0, -0.0042, 0.125), 0.075, 0.075, 0.0025, segs=32,
            mat_idx=fh_mat, vg_idx=vg["Blade_Flex"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
        )
        # Backhand Sponge Rubber (+Y face)
        U.add_weighted_cylinder(
            bm, (0.0, +0.0042, 0.125), 0.075, 0.075, 0.0025, segs=32,
            mat_idx=bh_mat, vg_idx=vg["Blade_Flex"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
        )
        # Rectangular rubber base stop above handle
        U.add_weighted_box(bm, (0.0, 0.0, 0.056), (0.068, 0.0105, 0.016), mat_idx=wood_mat, vg_idx=vg["Blade_Flex"], chamfer=0.002)

    else:
        # CAST IRON SKILLET CHALLENGE PADDLE
        # Walnut grip + brass collar + cast-iron skillet pan with white target ring
        U.add_weighted_cylinder(bm, (0.0, 0.0, -0.005), 0.014, 0.012, 0.10, segs=18, mat_idx=9, vg_idx=vg["Wrist_Pivot"])
        U.add_weighted_cylinder(bm, (0.0, 0.0, +0.050), 0.015, 0.015, 0.016, segs=18, mat_idx=5, vg_idx=vg["Wrist_Pivot"])
        # Skillet pan disk
        U.add_weighted_cylinder(
            bm, (0.0, 0.0, 0.132), 0.084, 0.084, 0.008, segs=32,
            mat_idx=19, vg_idx=vg["Blade_Flex"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
        )
        # Raised pan rim on -Y face
        U.add_weighted_cylinder(
            bm, (0.0, -0.009, 0.132), 0.086, 0.082, 0.014, segs=32,
            mat_idx=19, vg_idx=vg["Blade_Flex"], rot_euler=(math.pi * 0.5, 0.0, 0.0), cap_ends=False
        )
        # Painted white bullseye ring & center dot on cooking face
        U.add_weighted_cylinder(
            bm, (0.0, -0.0046, 0.132), 0.052, 0.052, 0.0015, segs=28,
            mat_idx=2, vg_idx=vg["Blade_Flex"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
        )
        U.add_weighted_cylinder(
            bm, (0.0, -0.0052, 0.132), 0.044, 0.044, 0.0015, segs=28,
            mat_idx=19, vg_idx=vg["Blade_Flex"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
        )
        U.add_weighted_cylinder(
            bm, (0.0, -0.0056, 0.132), 0.016, 0.016, 0.0015, segs=20,
            mat_idx=6, vg_idx=vg["Blade_Flex"], rot_euler=(math.pi * 0.5, 0.0, 0.0)
        )

    U.finalize_bmesh(bm, mesh_obj)

    sockets = [
        U.add_socket_empty("Grab_Handle", (0.0, 0.0, 0.0), arm_obj),
        U.add_socket_empty("SweetSpot_Forehand", (0.0, -0.006, 0.125), arm_obj),
        U.add_socket_empty("SweetSpot_Backhand", (0.0, +0.006, 0.125), arm_obj),
    ]

    reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all = U.make_pose_helpers(arm_obj)
    scene = bpy.context.scene
    actions = []

    # 1. Paddle_Idle_Twirl
    act1 = U.start_action(arm_obj, "Paddle_Idle_Twirl")
    for f, yaw in [(1, 0.0), (15, 180.0), (30, 360.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Wrist_Pivot", 0.0, 0.0, yaw)
        key_all(f)
    actions.append(act1)

    # 2. Paddle_Forehand_Topspin_Drive
    act2 = U.start_action(arm_obj, "Paddle_Forehand_Topspin_Drive")
    for f, pitch, roll, yaw, dy in [
        (1, 0.0, 0.0, 0.0, 0.0),
        (8, -28.0, +18.0, -32.0, +0.08),
        (16, +34.0, -22.0, +38.0, -0.14),
        (26, 0.0, 0.0, 0.0, 0.0),
    ]:
        scene.frame_set(f)
        reset_pose()
        set_world_loc("Root", 0.0, dy, 0.0)
        set_world_rot("Wrist_Pivot", pitch, roll, yaw)
        set_world_rot("Blade_Flex", pitch * 0.15, 0.0, 0.0)
        key_all(f)
    actions.append(act2)

    # 3. Paddle_Backhand_Flick
    act3 = U.start_action(arm_obj, "Paddle_Backhand_Flick")
    for f, pitch, roll, yaw, dy in [
        (1, 0.0, 0.0, 0.0, 0.0),
        (7, +24.0, -20.0, +30.0, +0.05),
        (14, -36.0, +16.0, -28.0, -0.11),
        (24, 0.0, 0.0, 0.0, 0.0),
    ]:
        scene.frame_set(f)
        reset_pose()
        set_world_loc("Root", 0.0, dy, 0.0)
        set_world_rot("Wrist_Pivot", pitch, roll, yaw)
        key_all(f)
    actions.append(act3)

    # 4. Paddle_Chop_Defense
    act4 = U.start_action(arm_obj, "Paddle_Chop_Defense")
    for f, pitch, dz, dy in [
        (1, 0.0, 0.0, 0.0),
        (8, -42.0, +0.09, +0.06),
        (17, +22.0, -0.07, -0.12),
        (26, 0.0, 0.0, 0.0),
    ]:
        scene.frame_set(f)
        reset_pose()
        set_world_loc("Root", 0.0, dy, dz)
        set_world_rot("Wrist_Pivot", pitch, 0.0, 0.0)
        key_all(f)
    actions.append(act4)

    U.push_actions_to_muted_nla(arm_obj, actions)
    scene.frame_set(1)
    reset_pose()
    U.export_9_formats(asset_name, arm_obj, mesh_obj, sockets)


def build_ball_variant(asset_name, mode="white"):
    """
    Regulation 40mm (R = 0.020 m) 3-Star Table Tennis Ball.
    Center at Z = 0.020 m so bottom touches Z = 0.000 m at rest.
    """
    U.clear_scene()
    mats = U.create_tt_palette()

    bone_specs = [
        ("Root", None, (0.0, 0.0, 0.000), (0.0, 0.0, 0.010), False),
        ("Ball_Squash", "Root", (0.0, 0.0, 0.010), (0.0, 0.0, 0.020), False),
        ("Ball_Spin", "Ball_Squash", (0.0, 0.0, 0.020), (0.0, 0.0, 0.040), False),
    ]
    arm_obj, mesh_obj, vg = U.create_armature_and_mesh(asset_name, bone_specs, mats)
    bm = bmesh.new()

    R = 0.020
    rings_n = 20
    profile = []
    for i in range(rings_n + 1):
        theta = -math.pi * 0.5 + math.pi * (i / rings_n)
        r = max(0.0005, R * math.cos(theta))
        z = 0.020 + R * math.sin(theta)
        profile.append((r, z))

    def ball_mat_map(ring_idx):
        if mode == "white":
            return 5 if ring_idx == rings_n // 2 else 16
        elif mode == "orange":
            return 2 if ring_idx == rings_n // 2 else 17
        else:
            # Two-tone spin training ball: Bottom White, Equatorial Black/Gold seam, Top Orange!
            if ring_idx in (rings_n // 2 - 1, rings_n // 2):
                return 12
            return 16 if ring_idx < rings_n // 2 else 17

    U.add_lathe_profile(bm, profile, segs=32, mat_map=ball_mat_map, vg_idx=vg["Ball_Spin"])
    # Give polar cap vertices a 2% weight on Ball_Squash so glTF always exports a multi-joint Skin
    dlayer = bm.verts.layers.deform.verify()
    bm.verts.ensure_lookup_table()
    for i in range(min(32, len(bm.verts))):
        bm.verts[i][dlayer][vg["Ball_Squash"]] = 0.02
        bm.verts[i][dlayer][vg["Ball_Spin"]] = 0.98
    U.finalize_bmesh(bm, mesh_obj)

    sockets = [
        U.add_socket_empty("Ball_Center", (0.0, 0.0, 0.020), arm_obj),
        U.add_socket_empty("Ball_Bottom_Contact", (0.0, 0.0, 0.000), arm_obj),
    ]

    reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all = U.make_pose_helpers(arm_obj)
    scene = bpy.context.scene
    actions = []

    # 1. Ball_Topspin_Loop
    act1 = U.start_action(arm_obj, "Ball_Topspin_Loop")
    for f, deg in [(1, 0.0), (11, -180.0), (21, -360.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_rot("Ball_Spin", deg, 0.0, 0.0)
        key_all(f)
    actions.append(act1)

    # 2. Ball_Bounce_Squash
    act2 = U.start_action(arm_obj, "Ball_Bounce_Squash")
    for f, dz, sx, sz, pitch in [
        (1, 0.18, 1.0, 1.0, 0.0),
        (8, 0.00, 1.18, 0.76, -120.0),
        (11, 0.03, 0.94, 1.10, -180.0),
        (20, 0.18, 1.0, 1.0, -360.0),
    ]:
        scene.frame_set(f)
        reset_pose()
        set_world_loc("Root", 0.0, 0.0, dz)
        set_bone_scale("Ball_Squash", sx, sx, sz)
        set_world_rot("Ball_Spin", pitch, 0.0, 0.0)
        key_all(f)
    actions.append(act2)

    # 3. Ball_Serve_Toss (ITTF legal 16cm+ vertical palm toss)
    act3 = U.start_action(arm_obj, "Ball_Serve_Toss")
    for f, dz in [(1, 0.0), (14, 0.28), (28, 0.0)]:
        scene.frame_set(f)
        reset_pose()
        set_world_loc("Root", 0.0, 0.0, dz)
        set_world_rot("Ball_Spin", 0.0, 0.0, f * 10.0)
        key_all(f)
    actions.append(act3)

    U.push_actions_to_muted_nla(arm_obj, actions)
    scene.frame_set(1)
    reset_pose()
    U.export_9_formats(asset_name, arm_obj, mesh_obj, sockets)


if __name__ == "__main__":
    build_table_variant("cozy_tt_table_indoor_pro", is_outdoor=False)
    build_table_variant("cozy_tt_table_outdoor_garden", is_outdoor=True)
    build_paddle_variant("cozy_tt_paddle_classic", style="classic")
    build_paddle_variant("cozy_tt_paddle_carbon_pro", style="carbon")
    build_paddle_variant("cozy_tt_paddle_cast_iron_pan", style="skillet")
    build_ball_variant("cozy_tt_ball_white_3star", mode="white")
    build_ball_variant("cozy_tt_ball_orange_3star", mode="orange")
    build_ball_variant("cozy_tt_ball_twotone_spin", mode="twotone")
    print("[SUCCESS] All 8 Core Match Set Table Tennis models built and exported!")
