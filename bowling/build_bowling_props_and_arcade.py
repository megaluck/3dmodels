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


# ==============================================================================
# 4. cozy_bowling_pins_pack (Regulation 38.1 cm Maple Pin + Golden Jackpot Pin)
# ==============================================================================
def build_pins_pack():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    # Regulation bowling pin: 38.1 cm tall (15 inches), max belly diameter 12.1 cm (radius = 0.0605 m).
    # Placed at X = -0.18 m (Standard White Maple Pin with dual crimson neck stripes)
    # and X = +0.18 m (Golden Jackpot Head-Pin).
    bone_specs = [
        ("Root",         ( 0.00, 0.00, 0.00), ( 0.00, -0.08, 0.00), None),
        ("Pin_Standard", (-0.18, 0.00, 0.00), (-0.18,  0.00, 0.381), "Root"),
        ("Pin_Gold",     ( 0.18, 0.00, 0.00), ( 0.18,  0.00, 0.381), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Cream_Pearl (#F4EFE6) - glossy white pin body
    # 1: Bowling_Crimson_Stripe (#C82822) - dual red neck stripes
    # 2: Bowling_Gold_Brass (#D8A638) - Golden Jackpot Pin body
    # 3: Bowling_Obsidian_Ball (#1C2026) - protective nylon base ring
    mats = [
        "Bowling_Cream_Pearl", "Bowling_Crimson_Stripe",
        "Bowling_Gold_Brass", "Bowling_Obsidian_Ball"
    ]

    # Authentic USBC 15-inch (0.381 m) bowling pin lathe profile:
    pin_profile = [
        (0.000, 0.0260),  # 0: Base foot (5.2 cm diameter)
        (0.012, 0.0320),  # 1: Base bevel ring
        (0.055, 0.0480),  # 2: Lower taper
        (0.114, 0.0605),  # 3: Max belly (4.5 inches up, 12.1 cm diameter!)
        (0.175, 0.0540),  # 4: Upper belly
        (0.215, 0.0350),  # 5: Lower neck stripe start
        (0.232, 0.0290),  # 6: Lower neck stripe end
        (0.246, 0.0255),  # 7: Narrowest neck waist (10 inches up)
        (0.260, 0.0275),  # 8: Upper neck stripe start
        (0.277, 0.0325),  # 9: Upper neck stripe end
        (0.318, 0.0425),  # 10: Head cheek
        (0.352, 0.0410),  # 11: Head crown
        (0.372, 0.0280),  # 12: Top dome
        (0.381, 0.0100),  # 13: Top apex
    ]

    for px, bname, body_mat in [(-0.18, "Pin_Standard", 0), (0.18, "Pin_Gold", 2)]:
        pts_rad = [((px, 0.0, z), r) for z, r in pin_profile]
        rings = add_weighted_tube(bm, deform, pts_rad, sides=12, mat_idx=body_mat, vg_idx=b_idx[bname])
        # Color base ring (seg 0) dark nylon (3), and dual neck stripes (seg 5 and seg 8) crimson red (1)!
        for seg_i, m_override in [(0, 3), (5, 1), (8, 1)]:
            r_a = set(rings[seg_i])
            r_b = set(rings[seg_i + 1])
            for f in bm.faces:
                if all(v in r_a or v in r_b for v in f.verts):
                    f.material_index = m_override

    rig_obj, rest_mat = create_rig("Pins_Rig", bone_specs)
    finalize_rigged_mesh("Pins_Mesh", bm, rig_obj, bone_specs, mats)

    make_empty("Pin_Standard_Base", (-0.18, 0.0, 0.000), parent=rig_obj, bone_parent="Pin_Standard")
    make_empty("Pin_Standard_Top",  (-0.18, 0.0, 0.381), parent=rig_obj, bone_parent="Pin_Standard")
    make_empty("Pin_Gold_Base",     ( 0.18, 0.0, 0.000), parent=rig_obj, bone_parent="Pin_Gold")
    make_empty("Pin_Gold_Top",      ( 0.18, 0.0, 0.381), parent=rig_obj, bone_parent="Pin_Gold")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Pin_Idle_Wobble (48f loop: comical "teetering on the edge of falling over!" wobble)
    act_wobble = bpy.data.actions.new(name="Pin_Idle_Wobble")
    act_wobble.use_fake_user = True
    rig_obj.animation_data.action = act_wobble
    for f, p_ang, r_ang in [
        (1,   0.0,   0.0),
        (12, 14.0, -10.0),
        (24, -8.0,  14.0),
        (36, 10.0,  -8.0),
        (48,  0.0,   0.0),
    ]:
        key_frame(f, rot_map={
            "Pin_Standard": (p_ang, r_ang, 0.0),
            "Pin_Gold":     (-p_ang, -r_ang, 0.0),
        })

    # 2. Pin_Hit_Spin_Fly (40f: explosive pin-action spin, airborne tumble & reset)
    act_fly = bpy.data.actions.new(name="Pin_Hit_Spin_Fly")
    act_fly.use_fake_user = True
    rig_obj.animation_data.action = act_fly
    for f, dy, dz, pitch, roll in [
        (1,  0.00, 0.00,    0.0,   0.0),
        (6,  0.18, 0.22, -110.0,  45.0),
        (14, 0.42, 0.30, -260.0, 110.0),
        (24, 0.58, 0.06, -450.0, 180.0),
        (32, 0.58, 0.06, -450.0, 180.0),
        (40, 0.00, 0.00,    0.0,   0.0),
    ]:
        key_frame(f, rot_map={
            "Pin_Standard": (pitch, roll, 0.0),
            "Pin_Gold":     (pitch, -roll, 0.0),
        }, loc_map={
            "Pin_Standard": (-0.12 * (dy / 0.58 if dy > 0 else 0), dy, dz),
            "Pin_Gold":     ( 0.12 * (dy / 0.58 if dy > 0 else 0), dy, dz),
        })

    save_and_export_bowling("cozy_bowling_pins_pack", animated=True)


# ==============================================================================
# 5. cozy_bowling_balls_pack (4 Regulation 21.6 cm 3-Hole Bowling Balls)
# ==============================================================================
def build_balls_pack():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    # Regulation bowling ball diameter = 21.6 cm (radius = 0.108 m, center at Z = 0.108 m).
    # 4 distinct weight/style balls placed at X = -0.45, -0.15, +0.15, +0.45 m:
    # 1. Ball_Coral_8lb (-0.45)
    # 2. Ball_Teal_12lb (-0.15)
    # 3. Ball_Obsidian_15lb (+0.15)
    # 4. Ball_Gold_Trophy (+0.45)
    bone_specs = [
        ("Root",               ( 0.00, 0.0, 0.000), ( 0.00, -0.08, 0.000), None),
        ("Ball_Coral_8lb",     (-0.45, 0.0, 0.108), (-0.45,  0.00, 0.216), "Root"),
        ("Ball_Teal_12lb",     (-0.15, 0.0, 0.108), (-0.15,  0.00, 0.216), "Root"),
        ("Ball_Obsidian_15lb", ( 0.15, 0.0, 0.108), ( 0.15,  0.00, 0.216), "Root"),
        ("Ball_Gold_Trophy",   ( 0.45, 0.0, 0.108), ( 0.45,  0.00, 0.216), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Coral_Pink (#E26A52)
    # 1: Bowling_Teal_Seafoam (#2D8A7E)
    # 2: Bowling_Obsidian_Ball (#1C2026) - 15lb ball & finger holes
    # 3: Bowling_Gold_Brass (#D8A638)
    # 4: Bowling_Cream_Pearl (#F4EFE6) - swirl equatorial band
    # 5: Bowling_Crimson_Stripe (#C82822) - obsidian pro-hook band
    mats = [
        "Bowling_Coral_Pink", "Bowling_Teal_Seafoam", "Bowling_Obsidian_Ball",
        "Bowling_Gold_Brass", "Bowling_Cream_Pearl", "Bowling_Crimson_Stripe"
    ]

    R = 0.108
    ball_lat = [
        (-0.96, 0.28),
        (-0.78, 0.62),
        (-0.50, 0.866),
        (-0.18, 0.984),
        ( 0.18, 0.984),
        ( 0.50, 0.866),
        ( 0.78, 0.62),
        ( 0.96, 0.28),
    ]

    ball_configs = [
        (-0.45, "Ball_Coral_8lb",     0, 4),
        (-0.15, "Ball_Teal_12lb",     1, 3),
        ( 0.15, "Ball_Obsidian_15lb", 2, 5),
        ( 0.45, "Ball_Gold_Trophy",   3, 4),
    ]

    for bx, bname, main_mat, stripe_mat in ball_configs:
        pts_rad = [((bx, 0.0, 0.108 + kz * R), kr * R) for kz, kr in ball_lat]
        rings = add_weighted_tube(bm, deform, pts_rad, sides=14, mat_idx=main_mat, vg_idx=b_idx[bname])
        # Equatorial swirl band so rolling spin is super readable in VR!
        r_eq_a, r_eq_b = set(rings[3]), set(rings[4])
        for f in bm.faces:
            if all(v in r_eq_a or v in r_eq_b for v in f.verts):
                f.material_index = stripe_mat

        # 3 Flush Dark Finger Grip Holes on the top-front hemisphere (`Bowling_Obsidian_Ball`, mat 2)
        for dx, dy in [
            (-0.018, -0.022),  # Middle finger
            ( 0.018, -0.022),  # Ring finger
            ( 0.000, -0.052),  # Thumb hole
        ]:
            surf_z = 0.108 + math.sqrt(max(0.0, (R * 0.96) ** 2 - dx * dx - dy * dy))
            add_weighted_tube(bm, deform, [
                ((bx + dx, dy, surf_z - 0.010), 0.010),
                ((bx + dx, dy, surf_z + 0.001), 0.010),
            ], sides=8, mat_idx=2, vg_idx=b_idx[bname])

    rig_obj, rest_mat = create_rig("Balls_Rig", bone_specs)
    finalize_rigged_mesh("Balls_Mesh", bm, rig_obj, bone_specs, mats)

    make_empty("Grip_Ball_Coral",    (-0.45, -0.03, 0.21), parent=rig_obj, bone_parent="Ball_Coral_8lb")
    make_empty("Grip_Ball_Teal",     (-0.15, -0.03, 0.21), parent=rig_obj, bone_parent="Ball_Teal_12lb")
    make_empty("Grip_Ball_Obsidian", ( 0.15, -0.03, 0.21), parent=rig_obj, bone_parent="Ball_Obsidian_15lb")
    make_empty("Grip_Ball_Gold",     ( 0.45, -0.03, 0.21), parent=rig_obj, bone_parent="Ball_Gold_Trophy")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)
    ball_bones = ["Ball_Coral_8lb", "Ball_Teal_12lb", "Ball_Obsidian_15lb", "Ball_Gold_Trophy"]

    # 1. Ball_Roll_Spin (24f loop: smooth 360° forward roll around X)
    act_roll = bpy.data.actions.new(name="Ball_Roll_Spin")
    act_roll.use_fake_user = True
    rig_obj.animation_data.action = act_roll
    for f, p_ang in [(1, 0.0), (7, -90.0), (13, -180.0), (19, -270.0), (24, -360.0)]:
        key_frame(f, rot_map={b: (p_ang, 0.0, 0.0) for b in ball_bones})

    # 2. Ball_Return_Pop_Up (36f: ball rises out of underground return chute, rolls forward & settles)
    act_pop = bpy.data.actions.new(name="Ball_Return_Pop_Up")
    act_pop.use_fake_user = True
    rig_obj.animation_data.action = act_pop
    for f, dy, dz, p_ang in [
        (1,   0.18, -0.22,    0.0),
        (10,  0.08,  0.04, -120.0),
        (20, -0.04,  0.00, -260.0),
        (28,  0.01,  0.00, -240.0),
        (36,  0.00,  0.00,    0.0),
    ]:
        key_frame(f, rot_map={b: (p_ang, 0.0, 0.0) for b in ball_bones}, loc_map={b: (0.0, dy, dz) for b in ball_bones})

    save_and_export_bowling("cozy_bowling_balls_pack", animated=True)


# ==============================================================================
# 8. cozy_bowling_lounge_booth (Curved Tufted Diner Sofa, Pin Table & Soda Cups)
# ==============================================================================
def build_lounge_booth():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    # Sits in the Left Bay (Bowler's Lounge), facing -Y (or toward the lanes).
    # Includes a 2.30 m wide curved two-tone Coral & Cream diner sofa, a bowling-lane-inlaid table, and 2 soda cups!
    bone_specs = [
        ("Root",         ( 0.00,  0.00, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Seat_Cushion", ( 0.00,  0.18, 0.42), ( 0.00,  0.18, 0.56), "Root"),
        ("Cup_1",        (-0.28, -0.45, 0.58), (-0.28, -0.45, 0.78), "Root"),
        ("Cup_2",        ( 0.25, -0.42, 0.58), ( 0.25, -0.42, 0.78), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Coral_Pink (#E26A52) - outer sofa backrest & cup stripes
    # 1: Bowling_Cream_Pearl (#F4EFE6) - tufted seat cushions & cups
    # 2: Bowling_Maple_Light (#E8CFA8) - sofa plinth & bowling-lane table top
    # 3: Bowling_Maple_Amber (#C79252) - table stripe
    # 4: Bowling_Gold_Brass (#D8A638) - tapered mid-century legs
    # 5: Bowling_Teal_Seafoam (#2D8A7E) - cup 2 accent & table trim
    mats = [
        "Bowling_Coral_Pink", "Bowling_Cream_Pearl", "Bowling_Maple_Light",
        "Bowling_Maple_Amber", "Bowling_Gold_Brass", "Bowling_Teal_Seafoam"
    ]

    # 1. Continuous U-shaped Diner Booth Base & Backrest (`Root`) with ZERO overlapping corners or rear gaps!
    # Back bench base (X = -1.15 to +1.15, Y = 0.00 to +0.58, Z = 0.00 to 0.34 m)
    # + Left/Right side wing bases abutting in front (X = +-0.98, Y = -0.52 to 0.00, Z = 0.00 to 0.34 m)
    add_weighted_box(bm, deform, ( 0.00,  0.29, 0.17), 2.30, 0.58, 0.34, mat_idx=2, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (-0.98, -0.26, 0.17), 0.34, 0.52, 0.34, mat_idx=2, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, ( 0.98, -0.26, 0.17), 0.34, 0.52, 0.34, mat_idx=2, vg_idx=b_idx["Root"])

    # Continuous U-shaped Coral & Cream Backrest (`Z = 0.34 to 0.96 m`, flush from top of base to top of booth)
    add_weighted_box(bm, deform, ( 0.00,  0.49, 0.65), 2.30, 0.18, 0.62, mat_idx=0, vg_idx=b_idx["Root"])
    for ch_i in range(5):
        cx = -0.64 + ch_i * 0.32
        add_weighted_box(bm, deform, (cx, 0.38, 0.70), 0.27, 0.05, 0.44, mat_idx=1, vg_idx=b_idx["Root"])
    for sx in (-1.06, 1.06):
        add_weighted_box(bm, deform, (sx, -0.06, 0.65), 0.18, 0.92, 0.62, mat_idx=0, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (sx - (0.10 if sx > 0 else -0.10), -0.06, 0.70), 0.04, 0.74, 0.44, mat_idx=1, vg_idx=b_idx["Root"])

    # 2. Continuous U-shaped Plush Seat Cushions (`Seat_Cushion` bone, Z = 0.34 to 0.46 m)
    add_weighted_box(bm, deform, ( 0.00,  0.20, 0.40), 1.94, 0.40, 0.12, mat_idx=1, vg_idx=b_idx["Seat_Cushion"])
    add_weighted_box(bm, deform, (-0.885,-0.05, 0.40), 0.17, 0.90, 0.12, mat_idx=1, vg_idx=b_idx["Seat_Cushion"])
    add_weighted_box(bm, deform, ( 0.885,-0.05, 0.40), 0.17, 0.90, 0.12, mat_idx=1, vg_idx=b_idx["Seat_Cushion"])

    # 3. Mid-Century Bowling-Lane Coffee Table at Y = -0.45 m (`Z = 0.0 to 0.56 m`)
    add_weighted_box(bm, deform, (0.0, -0.45, 0.54), 1.35, 0.62, 0.05, mat_idx=2, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.45, 0.566), 1.25, 0.16, 0.006, mat_idx=3, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.45, 0.535), 1.38, 0.65, 0.03, mat_idx=5, vg_idx=b_idx["Root"])
    for lx in (-0.52, 0.52):
        for ly in (-0.66, -0.24):
            add_weighted_tube(bm, deform, [
                ((lx, ly, 0.00), 0.016),
                ((lx * 0.9, ly, 0.52), 0.026),
            ], sides=6, mat_idx=4, vg_idx=b_idx["Root"])

    # 4. Two Fountain Soda Cups with Straws (`Cup_1` and `Cup_2`)
    for cx, cy, c_bone, c_mat in [(-0.28, -0.45, "Cup_1", 0), (0.25, -0.42, "Cup_2", 5)]:
        add_weighted_tube(bm, deform, [
            ((cx, cy, 0.565), 0.034),
            ((cx, cy, 0.700), 0.046),
            ((cx, cy, 0.715), 0.048),
        ], sides=8, mat_idx=c_mat, mat_end_idx=1, vg_idx=b_idx[c_bone])
        # Angled drinking straw
        add_weighted_tube(bm, deform, [
            ((cx, cy, 0.71), 0.005),
            ((cx + 0.02, cy - 0.02, 0.78), 0.005),
        ], sides=5, mat_idx=1, vg_idx=b_idx[c_bone])

    rig_obj, rest_mat = create_rig("Lounge_Rig", bone_specs)
    finalize_rigged_mesh("Lounge_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Seat_1",       (-0.72,  0.22, 0.48), parent=rig_obj, bone_parent="Seat_Cushion")
    make_empty("Seat_2",       (-0.24,  0.22, 0.48), parent=rig_obj, bone_parent="Seat_Cushion")
    make_empty("Seat_3",       ( 0.24,  0.22, 0.48), parent=rig_obj, bone_parent="Seat_Cushion")
    make_empty("Seat_4",       ( 0.72,  0.22, 0.48), parent=rig_obj, bone_parent="Seat_Cushion")
    make_empty("Table_Center", ( 0.00, -0.45, 0.57), parent=rig_obj, bone_parent="Root")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Cushion_Sit_Squish (30f: seat cushion compresses down and springs back)
    act_sit = bpy.data.actions.new(name="Cushion_Sit_Squish")
    act_sit.use_fake_user = True
    rig_obj.animation_data.action = act_sit
    for f, dz in [(1, 0.0), (8, -0.045), (16, 0.012), (23, -0.006), (30, 0.0)]:
        key_frame(f, loc_map={"Seat_Cushion": (0.0, 0.0, dz)})

    # 2. Table_Cup_Jiggle (28f: soda cups hop and wobble on the table)
    act_cup = bpy.data.actions.new(name="Table_Cup_Jiggle")
    act_cup.use_fake_user = True
    rig_obj.animation_data.action = act_cup
    for f, r_ang, dz in [(1, 0.0, 0.0), (5, 12.0, 0.025), (11, -10.0, 0.0), (17, 6.0, 0.01), (28, 0.0, 0.0)]:
        key_frame(f, rot_map={
            "Cup_1": (r_ang, r_ang * 0.7, 0.0),
            "Cup_2": (-r_ang, r_ang * 0.8, 0.0),
        }, loc_map={
            "Cup_1": (0.0, 0.0, dz),
            "Cup_2": (0.0, 0.0, dz * 0.8),
        })

    save_and_export_bowling("cozy_bowling_lounge_booth", animated=True)


# ==============================================================================
# 9. cozy_bowling_shoe_counter (Shoe Rental Counter, Cubby Wall & Ball Polisher)
# ==============================================================================
def build_shoe_counter():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    # Sits in the Right Bay (Shoe Rental & Pro Shop), facing -Y.
    # Includes front counter desk, brass service bell, motorized ball polisher spinner,
    # and rear cubbyhole cabinet stocked with two-tone Coral & Teal bowling shoes!
    bone_specs = [
        ("Root",              ( 0.00,  0.00, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Service_Bell",      (-0.55, -0.32, 0.96), (-0.55, -0.32, 1.08), "Root"),
        ("Polisher_Wheel",    ( 0.52, -0.30, 1.08), ( 0.52, -0.30, 1.28), "Root"),
        ("Rental_Shoes_Pair", ( 0.00, -0.28, 0.96), ( 0.00, -0.45, 0.96), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Maple_Light (#E8CFA8) - counter top & shoe cubby shelves
    # 1: Bowling_Teal_Seafoam (#2D8A7E) - front counter paneling & shoe heels
    # 2: Bowling_Coral_Pink (#E26A52) - shoe toes & polisher hood
    # 3: Bowling_Gold_Brass (#D8A638) - service bell & trim
    # 4: Bowling_Walnut_Dark (#593A22) - shoe soles & cubby backing
    # 5: Bowling_Cream_Pearl (#F4EFE6) - shoe laces & buffing pad
    mats = [
        "Bowling_Maple_Light", "Bowling_Teal_Seafoam", "Bowling_Coral_Pink",
        "Bowling_Gold_Brass", "Bowling_Walnut_Dark", "Bowling_Cream_Pearl"
    ]

    # 1. Front Check-In Counter Desk (`Y = -0.32 m`, width = 2.10 m, height = 0.96 m)
    add_weighted_box(bm, deform, (0.0, -0.32, 0.46), 2.04, 0.52, 0.92, mat_idx=1, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.32, 0.94), 2.14, 0.60, 0.05, mat_idx=0, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.0, -0.59, 0.06), 2.06, 0.04, 0.12, mat_idx=3, vg_idx=b_idx["Root"])

    # 2. Rear Shoe Cubbyhole Cabinet (`Y = +0.48 m`, width = 2.10 m, height = 2.05 m)
    add_weighted_box(bm, deform, (0.0, 0.56, 1.025), 2.10, 0.06, 2.05, mat_idx=4, vg_idx=b_idx["Root"])
    # 4 horizontal shelves & 5 vertical dividers creating 12 shoe cubbies
    for sz in (0.45, 0.92, 1.38, 1.84, 2.04):
        add_weighted_box(bm, deform, (0.0, 0.42, sz), 2.10, 0.32, 0.04, mat_idx=0, vg_idx=b_idx["Root"])
    for dx in (-1.03, -0.52, 0.0, 0.52, 1.03):
        add_weighted_box(bm, deform, (dx, 0.42, 1.025), 0.04, 0.32, 2.05, mat_idx=0, vg_idx=b_idx["Root"])

    # Helper to build an iconic two-tone Coral & Teal Rental Bowling Shoe
    def add_bowling_shoe(sx, sy, sz, vg_name):
        # Dark sole + Teal rear upper + Coral toe cap + Cream tongue
        add_weighted_box(bm, deform, (sx, sy, sz + 0.012), 0.09, 0.24, 0.024, mat_idx=4, vg_idx=b_idx[vg_name])
        add_weighted_box(bm, deform, (sx, sy + 0.04, sz + 0.055), 0.085, 0.13, 0.065, mat_idx=1, vg_idx=b_idx[vg_name])
        add_weighted_box(bm, deform, (sx, sy - 0.05, sz + 0.040), 0.082, 0.10, 0.042, mat_idx=2, vg_idx=b_idx[vg_name])
        add_weighted_box(bm, deform, (sx, sy - 0.01, sz + 0.072), 0.055, 0.06, 0.025, mat_idx=5, vg_idx=b_idx[vg_name])

    # Pair of featured Rental Shoes sitting right on the counter (`Rental_Shoes_Pair` bone)
    add_bowling_shoe(-0.07, -0.30, 0.965, "Rental_Shoes_Pair")
    add_bowling_shoe( 0.07, -0.30, 0.965, "Rental_Shoes_Pair")

    # Stock the rear cubbies with extra pairs of bowling shoes (`Root`)
    for cub_x in (-0.78, -0.26, 0.26, 0.78):
        for cub_z in (0.47, 0.94, 1.40):
            add_bowling_shoe(cub_x - 0.06, 0.38, cub_z, "Root")
            add_bowling_shoe(cub_x + 0.06, 0.38, cub_z, "Root")

    # 3. Brass Service Bell on Left Side of Counter (`Service_Bell` at (-0.55, -0.32, 0.965))
    add_weighted_tube(bm, deform, [
        ((-0.55, -0.32, 0.965), 0.065),
        ((-0.55, -0.32, 0.985), 0.058),
        ((-0.55, -0.32, 1.035), 0.042),
        ((-0.55, -0.32, 1.055), 0.018),
    ], sides=8, mat_idx=3, vg_idx=b_idx["Service_Bell"])

    # 4. Motorized Ball Buffing / Polisher Machine on Right Side of Counter (`Polisher_Wheel` at (0.52, -0.30, 1.08))
    add_weighted_box(bm, deform, (0.52, -0.30, 1.01), 0.34, 0.32, 0.09, mat_idx=2, vg_idx=b_idx["Root"])
    add_weighted_tube(bm, deform, [
        ((0.52, -0.30, 1.05), 0.11),
        ((0.52, -0.30, 1.16), 0.12),
        ((0.52, -0.30, 1.24), 0.09),
    ], sides=10, mat_idx=3, mat_end_idx=5, vg_idx=b_idx["Polisher_Wheel"])

    rig_obj, rest_mat = create_rig("Counter_Rig", bone_specs)
    finalize_rigged_mesh("Counter_Mesh", bm, rig_obj, bone_specs, mats)

    make_empty("Grab_Rental_Shoes", ( 0.00, -0.30, 1.02), parent=rig_obj, bone_parent="Rental_Shoes_Pair")
    make_empty("Bell_Hit",          (-0.55, -0.32, 1.06), parent=rig_obj, bone_parent="Service_Bell")
    make_empty("Polisher_Slot",     ( 0.52, -0.30, 1.15), parent=rig_obj, bone_parent="Polisher_Wheel")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Service_Bell_Ring (24f: bell dome dings and vibrates)
    act_bell = bpy.data.actions.new(name="Service_Bell_Ring")
    act_bell.use_fake_user = True
    rig_obj.animation_data.action = act_bell
    for f, dz, r_ang in [(1, 0.0, 0.0), (4, -0.018, 12.0), (8, 0.008, -10.0), (13, 0.0, 6.0), (18, 0.0, -3.0), (24, 0.0, 0.0)]:
        key_frame(f, rot_map={"Service_Bell": (0.0, r_ang, 0.0)}, loc_map={"Service_Bell": (0.0, 0.0, dz)})

    # 2. Polisher_Spin_Buff (30f loop: motorized ball polisher spins 360°)
    act_pol = bpy.data.actions.new(name="Polisher_Spin_Buff")
    act_pol.use_fake_user = True
    rig_obj.animation_data.action = act_pol
    for f, yaw in [(1, 0.0), (8, 90.0), (16, 180.0), (23, 270.0), (30, 360.0)]:
        key_frame(f, rot_map={"Polisher_Wheel": (0.0, 0.0, yaw)})

    # 3. Shoes_Cubby_Rattle (28f: counter rental shoes hop forward when dispensed)
    act_shoes = bpy.data.actions.new(name="Shoes_Cubby_Rattle")
    act_shoes.use_fake_user = True
    rig_obj.animation_data.action = act_shoes
    for f, dy, dz, p_ang in [(1, 0.0, 0.0, 0.0), (7, -0.06, 0.05, 14.0), (14, -0.02, 0.0, -8.0), (21, 0.0, 0.015, 4.0), (28, 0.0, 0.0, 0.0)]:
        key_frame(f, rot_map={"Rental_Shoes_Pair": (p_ang, 0.0, 0.0)}, loc_map={"Rental_Shoes_Pair": (0.0, dy, dz)})

    save_and_export_bowling("cozy_bowling_shoe_counter", animated=True)


# ==============================================================================
# 10. cozy_bowling_arcade_space_invaders (1978 Stand-Up Space Invaders Cabinet)
# ==============================================================================
def build_arcade_space_invaders():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    # Classic 1978 Upright Space Invaders Arcade Cabinet:
    # Origin (0, 0, 0) on the floor at center of cabinet base, facing -Y towards the player.
    # Features a single-quad [0, 1] UV-mapped CRT screen (`Arcade_CRT_Screen`) tilted back 18° for comfortable VR play,
    # plus rigged Joystick, Left/Right/Fire buttons, and 25c Coin Button!
    bone_specs = [
        ("Root",        ( 0.00,  0.00, 0.00), ( 0.00, -0.15, 0.00), None),
        ("Joystick",    (-0.14, -0.34, 0.94), (-0.14, -0.34, 1.06), "Root"),
        ("Btn_Left",    ( 0.04, -0.35, 0.94), ( 0.04, -0.35, 0.98), "Root"),
        ("Btn_Right",   ( 0.11, -0.35, 0.94), ( 0.11, -0.35, 0.98), "Root"),
        ("Btn_Fire",    ( 0.20, -0.33, 0.94), ( 0.20, -0.33, 0.98), "Root"),
        ("Coin_Button", ( 0.06, -0.37, 0.52), ( 0.06, -0.42, 0.52), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Materials:
    # 0: Bowling_Arcade_Blue (#1F3B6E) - upright side panels
    # 1: Bowling_Obsidian_Ball (#1C2026) - recessed monitor bezel, control deck & base
    # 2: Bowling_Arcade_Green (#48C858) - pixel alien side emblem & marquee header
    # 3: Bowling_Coral_Pink (#E26A52) - UFO side emblem & marquee trim
    # 4: Bowling_Bumper_Yellow (#F2C138) - T-molding & Left/Right buttons
    # 5: Bowling_Crimson_Stripe (#C82822) - joystick ball top, Fire button & 25c coin button
    # 6: Bowling_Chrome_Steel (#C4CBD0) - joystick shaft & coin door frame
    # 7: Bowling_Walnut_Dark (#593A22) - vintage wood-grain lower cabinet front
    # 8: Arcade_CRT_Screen (#0E1821) - ONLY on the single-quad [0, 1] UV CRT Screen!
    mats = [
        "Bowling_Arcade_Blue", "Bowling_Obsidian_Ball", "Bowling_Arcade_Green",
        "Bowling_Coral_Pink", "Bowling_Bumper_Yellow", "Bowling_Crimson_Stripe",
        "Bowling_Chrome_Steel", "Bowling_Walnut_Dark", "Arcade_CRT_Screen"
    ]

    # 1. Upright Cabinet Body (`Root`, width = 0.70 m, depth = 0.78 m, height = 1.78 m)
    # Lower pedestal box (Z = 0.0 to 0.92 m)
    add_weighted_box(bm, deform, (0.0,  0.00, 0.46), 0.68, 0.74, 0.92, mat_idx=7, vg_idx=b_idx["Root"])
    # Upper monitor house recessed behind the tilted CRT bezel (Y = -0.11 to +0.37 m, Z = 0.92 to 1.56 m)
    add_weighted_box(bm, deform, (0.0,  0.13, 1.24), 0.68, 0.48, 0.64, mat_idx=1, vg_idx=b_idx["Root"])
    # Overhanging Top Marquee Header Box (Z = 1.56 to 1.78 m, projecting forward to Y = -0.38 m)
    add_weighted_box(bm, deform, (0.0, -0.02, 1.67), 0.70, 0.76, 0.22, mat_idx=0, vg_idx=b_idx["Root"])
    # Lit Green & Coral Marquee Sign Plate on front of header (`Y = -0.40 m, Z = 1.67 m`)
    add_weighted_box(bm, deform, (0.0, -0.40, 1.67), 0.64, 0.03, 0.17, mat_idx=2, vg_idx=b_idx["Root"], rot_deg=(-12.0, 0.0, 0.0))
    add_weighted_box(bm, deform, (0.0, -0.41, 1.67), 0.52, 0.02, 0.07, mat_idx=3, vg_idx=b_idx["Root"], rot_deg=(-12.0, 0.0, 0.0))

    # Left & Right Sculpted Side Panels (`X = +-0.35 m`) with Yellow T-Molding & Pixel Space Invader Side Art!
    for sx in (-1.0, 1.0):
        px = sx * 0.35
        add_weighted_box(bm, deform, (px, 0.01, 0.89), 0.03, 0.76, 1.78, mat_idx=0, vg_idx=b_idx["Root"])
        # Bright yellow T-molding front edge
        add_weighted_box(bm, deform, (px, -0.37, 0.89), 0.036, 0.025, 1.78, mat_idx=4, vg_idx=b_idx["Root"])
        # Iconic 3D Pixel Space Invader Alien emblem on the exterior side panel (`px + sx * 0.018`)
        ax = px + sx * 0.018
        add_weighted_box(bm, deform, (ax, 0.02, 1.22), 0.012, 0.28, 0.12, mat_idx=2, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (ax, 0.02, 1.30), 0.012, 0.18, 0.06, mat_idx=2, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (ax, -0.09, 1.12), 0.012, 0.05, 0.08, mat_idx=2, vg_idx=b_idx["Root"])
        add_weighted_box(bm, deform, (ax,  0.13, 1.12), 0.012, 0.05, 0.08, mat_idx=2, vg_idx=b_idx["Root"])
        # Coral pixel UFO above the alien
        add_weighted_box(bm, deform, (ax, -0.05, 1.44), 0.012, 0.22, 0.06, mat_idx=3, vg_idx=b_idx["Root"])

    # 2. Angled Control Panel Deck (`Y = -0.33 m, Z = 0.92 m`)
    add_weighted_box(bm, deform, (0.0, -0.31, 0.91), 0.66, 0.22, 0.06, mat_idx=1, vg_idx=b_idx["Root"], rot_deg=(10.0, 0.0, 0.0))

    # Joystick (`Joystick` bone at (-0.14, -0.34, 0.94)): chrome shaft + crimson ball top
    add_weighted_tube(bm, deform, [
        ((-0.14, -0.34, 0.93), 0.026),
        ((-0.14, -0.34, 0.95), 0.008),
        ((-0.14, -0.34, 1.02), 0.008),
    ], sides=6, mat_idx=6, vg_idx=b_idx["Joystick"])
    add_weighted_tube(bm, deform, [
        ((-0.14, -0.34, 1.01), 0.016),
        ((-0.14, -0.34, 1.035), 0.024),
        ((-0.14, -0.34, 1.06), 0.014),
    ], sides=8, mat_idx=5, vg_idx=b_idx["Joystick"])

    # Arcade Push-Buttons: Left (`Btn_Left`, yellow), Right (`Btn_Right`, yellow), Fire (`Btn_Fire`, crimson)
    for bx, by, bname, bmat in [
        (0.04, -0.35, "Btn_Left",  4),
        (0.11, -0.35, "Btn_Right", 4),
        (0.20, -0.33, "Btn_Fire",  5),
    ]:
        add_weighted_tube(bm, deform, [
            ((bx, by, 0.935), 0.020),
            ((bx, by, 0.962), 0.018),
        ], sides=8, mat_idx=bmat, vg_idx=b_idx[bname])

    # 3. Brushed Chrome Coin Door & 25c Reject Plunger (`Coin_Button` at (0.06, -0.37, 0.52))
    add_weighted_box(bm, deform, (0.0, -0.37, 0.46), 0.36, 0.02, 0.42, mat_idx=6, vg_idx=b_idx["Root"])
    add_weighted_box(bm, deform, (0.06, -0.385, 0.52), 0.045, 0.03, 0.055, mat_idx=5, vg_idx=b_idx["Coin_Button"])

    # 4. SINGLE-QUAD [0, 1] UV CRT SCREEN (`Arcade_CRT_Screen`, mat 8):
    # Centered at (0.0, -0.220, 1.24), 0.50 m wide x 0.40 m tall, reclined back (`tilt_deg = -20.0`)
    # so its bottom is forward near the control deck (`y = -0.288`) and top reclines back (`y = -0.152`),
    # giving an upward-facing normal `(0.0, -0.940, +0.342)` aimed directly at the player's eyes!
    # Backed by a dark tilted CRT bezel plate (`center Y = -0.195, sy = 0.03`):
    add_weighted_box(bm, deform, ( 0.00, -0.195, 1.24), 0.64, 0.03, 0.50, mat_idx=1, vg_idx=b_idx["Root"], rot_deg=(-20.0, 0.0, 0.0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    f_crt, uv_crt = add_uv_screen_quad(
        bm, deform,
        center=(0.0, -0.220, 1.24),
        width_x=0.50, height_z=0.40,
        mat_idx=8, vg_idx=b_idx["Root"],
        tilt_deg=-20.0
    )
    apply_screen_uvs(bm, [(f_crt, uv_crt)])

    rig_obj, rest_mat = create_rig("Arcade_Rig", bone_specs)
    finalize_rigged_mesh("Arcade_Mesh", bm, rig_obj, bone_specs, mats, merge_doubles=False)

    make_empty("Player_Stand_Spot", ( 0.00, -0.85, 0.00), parent=rig_obj, bone_parent="Root")
    make_empty("Grab_Joystick",     (-0.14, -0.34, 1.04), parent=rig_obj, bone_parent="Joystick")
    make_empty("Hit_Fire_Btn",      ( 0.20, -0.33, 0.96), parent=rig_obj, bone_parent="Btn_Fire")
    make_empty("Coin_Slot",         ( 0.06, -0.39, 0.52), parent=rig_obj, bone_parent="Coin_Button")
    make_empty("Screen_Center",     ( 0.00, -0.26, 1.25), parent=rig_obj, bone_parent="Root")

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # 1. Arcade_Idle_Attract (48f loop: subtle joystick wiggle in attract mode)
    act_idle = bpy.data.actions.new(name="Arcade_Idle_Attract")
    act_idle.use_fake_user = True
    rig_obj.animation_data.action = act_idle
    for f, r_ang in [(1, 0.0), (16, 6.0), (32, -6.0), (48, 0.0)]:
        key_frame(f, rot_map={"Joystick": (0.0, r_ang, 0.0)})

    # 2. Joystick_Move_L_R (36f: player dodges laser fire left and right!)
    act_joy = bpy.data.actions.new(name="Joystick_Move_L_R")
    act_joy.use_fake_user = True
    rig_obj.animation_data.action = act_joy
    for f, r_ang, b_l, b_r in [
        (1,    0.0,  0.000,  0.000),
        (9,  -26.0, -0.015,  0.000),
        (18,  26.0,  0.000, -0.015),
        (27, -22.0, -0.015,  0.000),
        (36,   0.0,  0.000,  0.000),
    ]:
        key_frame(f, rot_map={"Joystick": (0.0, r_ang, 0.0)}, loc_map={
            "Btn_Left":  (0.0, 0.0, b_l),
            "Btn_Right": (0.0, 0.0, b_r),
        })

    # 3. Fire_Buttons_Mash (24f: rapid-fire laser button mashing!)
    act_fire = bpy.data.actions.new(name="Fire_Buttons_Mash")
    act_fire.use_fake_user = True
    rig_obj.animation_data.action = act_fire
    for f, dz in [(1, 0.0), (4, -0.018), (8, 0.0), (12, -0.018), (16, 0.0), (20, -0.018), (24, 0.0)]:
        key_frame(f, loc_map={"Btn_Fire": (0.0, 0.0, dz)})

    # 4. Coin_Insert_Clunk (20f: pressing the 25c coin plunger)
    act_coin = bpy.data.actions.new(name="Coin_Insert_Clunk")
    act_coin.use_fake_user = True
    rig_obj.animation_data.action = act_coin
    for f, dy in [(1, 0.0), (5, 0.022), (12, 0.022), (20, 0.0)]:
        key_frame(f, loc_map={"Coin_Button": (0.0, dy, 0.0)})

    save_and_export_bowling("cozy_bowling_arcade_space_invaders", animated=True)


if __name__ == "__main__":
    build_pins_pack()
    build_balls_pack()
    build_lounge_booth()
    build_shoe_counter()
    build_arcade_space_invaders()
