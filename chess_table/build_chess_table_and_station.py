import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector, Matrix, Euler

sys.path.append("C:/argon/chess_table")
from chess_utils import (
    init_scene,
    add_weighted_box,
    add_lathe_profile,
    create_rig,
    finalize_rigged_mesh,
    make_empty,
    make_pose_helpers,
    save_and_export_chess,
)
from build_chess_pieces import (
    PIECE_S,
    BASE_H_UNITS,
    add_staunton_piece_geometry,
)

# Board constants
SQUARE_M = 0.065            # 6.5 cm per square -> 8x8 board = 0.520 m x 0.520 m
BOARD_HALF = 4.0 * SQUARE_M # 0.260 m
BORDER_M = 0.130            # 13.0 cm wide white marble border all around -> total top = 0.780 m x 0.780 m
TABLE_HALF = BOARD_HALF + BORDER_M  # 0.390 m
TABLE_TOP_Z = 0.740         # 74.0 cm table surface height
FILES = "abcdefgh"


def square_xy(file_idx, rank_idx):
    """
    file_idx: 0..7 ('a'..'h', running -X to +X from White's perspective)
    rank_idx: 0..7 ('1'..'8', running -Y (White side) to +Y (Black/NPC side))
    """
    return ((file_idx - 3.5) * SQUARE_M, (rank_idx - 3.5) * SQUARE_M)


def add_marble_table_geometry(
    bm,
    deform,
    vg_root=0,
    vg_drawer=None,
    vg_hl_from=None,
    vg_hl_to=None,
):
    """
    Appends the luxury Italian Marble Pedestal Chess Table (matching il_1588xN.6916912488_oq7k.webp) to `bm`.
    Material slot order expected on mesh:
      0: Chess_Marble_White_Veined (tabletop border, light squares, 4 corner pillars, stepped base plinth)
      1: Chess_Marble_Black_Veined (dark squares, 4 recessed pedestal side panels)
      2: Chess_Gold_Brass          (inlaid board pinstripe frame, drawer pull, pedestal trim, move highlight rings)
      3: Chess_Groove_Slate        (recessed tile joint bed)
      4: Chess_Felt_Green          (felt-lined interior of slide-out storage drawer)
      5: Chess_Highlight_Glow      (glowing square move-guide frame)
    """
    if vg_drawer is None:
        vg_drawer = vg_root

    # 1. Stepped White Veined Marble Floor Plinth (0.540 m x 0.540 m, Z = 0.000 to 0.056 m)
    add_weighted_box(bm, deform, (0.0, 0.0, 0.022), 0.540, 0.540, 0.044, mat_idx=0, vg_idx=vg_root, chamfer=0.005)
    add_weighted_box(bm, deform, (0.0, 0.0, 0.050), 0.496, 0.496, 0.016, mat_idx=0, vg_idx=vg_root, chamfer=0.003)

    # 2. Four Square White Veined Marble Corner Pillars (at X = +-0.180, Y = +-0.180, size 0.110 x 0.110 m, Z = 0.054 to 0.686 m)
    pillar_h = 0.632
    pillar_cz = 0.054 + 0.5 * pillar_h
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            add_weighted_box(
                bm, deform, (sx * 0.180, sy * 0.180, pillar_cz),
                0.110, 0.110, pillar_h, mat_idx=0, vg_idx=vg_root, chamfer=0.003
            )

    # 3. Four Recessed Polished Black Veined Marble Side Panels between the corner pillars
    #    Recessed 2.8 cm inward from outer pillar face (outer pillar face = 0.235 m, black panel face = 0.207 m)
    panel_h = 0.616
    panel_cz = 0.058 + 0.5 * panel_h
    # Front (-Y) and Back (+Y) black marble panels
    for sy in (-1.0, 1.0):
        add_weighted_box(
            bm, deform, (0.0, sy * 0.198, panel_cz),
            0.252, 0.018, panel_h, mat_idx=1, vg_idx=vg_root
        )
        # Subtle brass accent frame top & bottom of each recessed black panel
        add_weighted_box(bm, deform, (0.0, sy * 0.208, 0.064), 0.250, 0.004, 0.008, mat_idx=2, vg_idx=vg_root)
        add_weighted_box(bm, deform, (0.0, sy * 0.208, 0.668), 0.250, 0.004, 0.008, mat_idx=2, vg_idx=vg_root)

    # Left (-X) and Right (+X) black marble panels
    for sx in (-1.0, 1.0):
        add_weighted_box(
            bm, deform, (sx * 0.198, 0.0, panel_cz),
            0.018, 0.252, panel_h, mat_idx=1, vg_idx=vg_root
        )
        add_weighted_box(bm, deform, (sx * 0.208, 0.0, 0.064), 0.004, 0.250, 0.008, mat_idx=2, vg_idx=vg_root)
        add_weighted_box(bm, deform, (sx * 0.208, 0.0, 0.668), 0.004, 0.250, 0.008, mat_idx=2, vg_idx=vg_root)

    # Inner structural core box so no gaps exist behind panels
    add_weighted_box(bm, deform, (0.0, 0.0, pillar_cz), 0.360, 0.360, pillar_h, mat_idx=1, vg_idx=vg_root)

    # 4. Under-Table Marble Crown Collar & Slide-Out Storage Drawer (`Piece_Drawer` on +X right side)
    add_weighted_box(bm, deform, (0.0, 0.0, 0.680), 0.520, 0.520, 0.016, mat_idx=0, vg_idx=vg_root, chamfer=0.003)

    # Slide-out drawer tucked cleanly into the +X upper pedestal apron
    add_weighted_box(bm, deform, (0.140, 0.0, 0.652), 0.220, 0.230, 0.036, mat_idx=0, vg_idx=vg_drawer, chamfer=0.002)
    add_weighted_box(bm, deform, (0.135, 0.0, 0.660), 0.195, 0.205, 0.024, mat_idx=4, vg_idx=vg_drawer)
    # Brass drawer knob on +X face
    add_weighted_box(bm, deform, (0.256, 0.0, 0.652), 0.014, 0.042, 0.012, mat_idx=2, vg_idx=vg_drawer, chamfer=0.002)

    # 5. Thick Chamfered White Veined Marble Tabletop Border & Sub-Slab (0.780 m x 0.780 m, Z = 0.686 to 0.740 m)
    # Solid lower tabletop slab from Z = 0.686 to 0.737 m
    add_weighted_box(bm, deform, (0.0, 0.0, 0.7115), 0.780, 0.780, 0.051, mat_idx=0, vg_idx=vg_root, chamfer=0.005)
    # Dark slate tile bed under the 64 squares (Z = 0.737 to 0.7388 m)
    add_weighted_box(bm, deform, (0.0, 0.0, 0.7379), 0.528, 0.528, 0.0018, mat_idx=3, vg_idx=vg_root)

    # Four flush White Veined Marble top border strips around the 8x8 playfield (Z = 0.735 to 0.740 m)
    b_mid = BOARD_HALF + 0.5 * BORDER_M  # 0.260 + 0.065 = 0.325 m
    # Front (-Y) and Back (+Y) border strips (full width 0.780 m x 0.126 m)
    for sy in (-1.0, 1.0):
        add_weighted_box(
            bm, deform, (0.0, sy * (b_mid + 0.002), 0.7375),
            0.780, BORDER_M - 0.004, 0.005, mat_idx=0, vg_idx=vg_root, chamfer=0.0015
        )
    # Left (-X) and Right (+X) border strips between front/back strips
    for sx in (-1.0, 1.0):
        add_weighted_box(
            bm, deform, (sx * (b_mid + 0.002), 0.0, 0.7375),
            BORDER_M - 0.004, 2.0 * BOARD_HALF + 0.008, 0.005, mat_idx=0, vg_idx=vg_root, chamfer=0.0015
        )

    # Inlaid Gold Brass Pinstripe Frame around the 8x8 playfield (at +-0.262 m)
    for sy in (-1.0, 1.0):
        add_weighted_box(bm, deform, (0.0, sy * 0.262, 0.7392), 0.528, 0.0035, 0.0018, mat_idx=2, vg_idx=vg_root)
    for sx in (-1.0, 1.0):
        add_weighted_box(bm, deform, (sx * 0.262, 0.0, 0.7392), 0.0035, 0.528, 0.0018, mat_idx=2, vg_idx=vg_root)

    # 6. 64 Individual Inlaid Veined Marble Squares (Square_a1..Square_h8)
    #    Each square is 6.36 cm x 6.36 cm (leaving a crisp 1.4 mm joint groove) with top at Z = 0.7400 m
    tile_w = SQUARE_M - 0.0014
    for f_i in range(8):
        for r_i in range(8):
            sx, sy = square_xy(f_i, r_i)
            # (f_i + r_i) % 2 == 0 -> Dark square (a1 is dark!), == 1 -> Light square (h1 is light!)
            sq_mat = 1 if ((f_i + r_i) % 2 == 0) else 0
            add_weighted_box(
                bm, deform, (sx, sy, 0.7390),
                tile_w, tile_w, 0.0020, mat_idx=sq_mat, vg_idx=vg_root, chamfer=0.0005
            )

    # 7. Optional Animated Move Highlight Frames (parked inside tabletop slab at Z = 0.725 m at rest; pop up to Z = 0.741 m)
    if vg_hl_from is not None and vg_hl_to is not None:
        for vg_hl, sq_coords in [(vg_hl_from, square_xy(4, 1)), (vg_hl_to, square_xy(4, 3))]:  # e2 and e4 at rest
            hx, hy = sq_coords
            hz = 0.725
            for d_side in (-1.0, 1.0):
                add_weighted_box(bm, deform, (hx, hy + d_side * 0.029, hz), 0.062, 0.004, 0.002, mat_idx=5, vg_idx=vg_hl)
                add_weighted_box(bm, deform, (hx + d_side * 0.029, hy, hz), 0.004, 0.054, 0.002, mat_idx=5, vg_idx=vg_hl)


def add_round_chair_geometry(bm, deform, center=(0.0, 0.0, 0.0), vg_base=0, vg_swivel=0, vg_cushion=0, vg_tuft=0):
    """
    Appends a Matching White & Black Veined Marble Drum Stool with a brass collar ring and soft tufted garden cushion.
    Seat top at Z = 0.460 m, diameter = 0.420 m (radius 0.210 m).
    Material indices:
      0: Chess_Marble_White_Veined (fluted marble drum body & stepped base plinth)
      1: Chess_Marble_Black_Veined (8 vertical recessed black marble flutes around drum)
      2: Chess_Gold_Brass          (collar ring & central tuft button)
      3: Chess_Cushion_Cream_Sage  (plump round upholstered seat cushion)
      4: Chess_Cushion_Piping      (contrasting welt cord piping ring)
    """
    cx, cy, cz = center

    # 1. Stepped White Veined Marble Drum Base & Barrel (Z = 0.000 to 0.395 m)
    drum_prof = [
        (0.212, 0.000),
        (0.212, 0.032),
        (0.194, 0.044),
        (0.176, 0.056),
        (0.168, 0.190),
        (0.176, 0.345),
        (0.192, 0.368),
        (0.198, 0.382),
        (0.198, 0.398),
        (0.001, 0.398),
    ]
    drum_bands = [
        (0.032, 0.044, 1),  # black marble lower accent step
        (0.380, 0.399, 2),  # polished gold brass collar ring under cushion
    ]
    add_lathe_profile(
        bm, deform, drum_prof, sides=20, center=center,
        mat_idx=0, vg_idx=vg_base, band_ranges=drum_bands
    )

    # 2. Eight Vertical Recessed Black Veined Marble Fluted Panels around the Drum Column
    for i in range(8):
        ang_deg = i * 45.0
        rad = math.radians(ang_deg)
        px = cx + 0.168 * math.sin(rad)
        py = cy + 0.168 * math.cos(rad)
        pz = cz + 0.202
        add_weighted_box(
            bm, deform, (px, py, pz),
            0.052, 0.014, 0.255,
            mat_idx=1, vg_idx=vg_swivel, rot_deg=(0.0, 0.0, -ang_deg), chamfer=0.002
        )
        # Subtle brass vertical flute Divider Pin
        ang_mid = ang_deg + 22.5
        rad_m = math.radians(ang_mid)
        bx = cx + 0.172 * math.sin(rad_m)
        by = cy + 0.172 * math.cos(rad_m)
        add_weighted_box(
            bm, deform, (bx, by, pz),
            0.008, 0.008, 0.255,
            mat_idx=2, vg_idx=vg_swivel, rot_deg=(0.0, 0.0, -ang_mid)
        )

    # 3. Plump Tufted Garden Cushion on Top (Z = 0.398 to 0.462 m, dipping to 0.452 m at center tuft)
    cush_prof = [
        (0.194, 0.398),
        (0.208, 0.412),
        (0.212, 0.432),
        (0.204, 0.450),
        (0.182, 0.460),
        (0.120, 0.463),
        (0.045, 0.458),
        (0.015, 0.450),
        (0.001, 0.450),
    ]
    cush_bands = [
        (0.398, 0.410, 4),  # lower welt cord piping
        (0.449, 0.458, 4),  # upper seam piping
    ]
    add_lathe_profile(
        bm, deform, cush_prof, sides=20, center=center,
        mat_idx=3, vg_idx=vg_cushion, band_ranges=cush_bands
    )

    # 4. Central Brass Tuft Button at (0, 0, 0.453 m)
    tuft_prof = [
        (0.022, 0.448),
        (0.025, 0.454),
        (0.018, 0.459),
        (0.001, 0.460),
    ]
    add_lathe_profile(
        bm, deform, tuft_prof, sides=12, center=center,
        mat_idx=2, vg_idx=vg_tuft
    )


def add_analog_clock_geometry(
    bm,
    deform,
    center=(0.0, 0.0, 0.0),
    yaw_deg=0.0,
    vg_root=0,
    vg_btn_w=0,
    vg_btn_b=0,
    vg_hand_w=0,
    vg_hand_b=0,
    vg_flag_w=0,
    vg_flag_b=0,
):
    """
    Appends a classic mechanical twin-dial analog chess clock (width 0.176 m, depth 0.062 m, height 0.102 m).
    Material indices:
      0: Chess_Walnut_Wood      (warm vintage wood case)
      1: Chess_Gold_Brass       (bezel rings, rocker buttons, base feet, top handle)
      2: Chess_Clock_Dial_Cream (twin circular clock faces)
      3: Chess_Marble_Black_Veined (clock hands & tick marks)
      4: Chess_Clock_Flag_Red   (hanging timeout flags)
    """
    temp_bm = bmesh.new()
    temp_def = temp_bm.verts.layers.deform.verify()

    # 1. Brass Base Feet & Walnut Body Casing (X in [-0.088, +0.088], Y in [-0.031, +0.031], Z = 0.000 to 0.088 m)
    for sx in (-0.072, 0.072):
        for sy in (-0.020, 0.020):
            add_weighted_box(temp_bm, temp_def, (sx, sy, 0.003), 0.020, 0.014, 0.006, mat_idx=1, vg_idx=vg_root)

    add_weighted_box(temp_bm, temp_def, (0.0, 0.0, 0.047), 0.176, 0.058, 0.082, mat_idx=0, vg_idx=vg_root, chamfer=0.004)
    # Brass top plate & decorative front/back trim
    add_weighted_box(temp_bm, temp_def, (0.0, 0.0, 0.089), 0.146, 0.036, 0.004, mat_idx=1, vg_idx=vg_root, chamfer=0.001)

    # 2. Twin Circular Clock Dials on the -Y Front Face (White dial at X = -0.044, Black dial at X = +0.044, Z = 0.046)
    for side_idx, (dx, vg_h, vg_fl) in enumerate([(-0.044, vg_hand_w, vg_flag_w), (0.044, vg_hand_b, vg_flag_b)]):
        # Brass bezel ring + Cream dial face (oriented facing -Y)
        add_weighted_box(temp_bm, temp_def, (dx, -0.030, 0.046), 0.064, 0.004, 0.064, mat_idx=1, vg_idx=vg_root, chamfer=0.008)
        add_weighted_box(temp_bm, temp_def, (dx, -0.0315, 0.046), 0.054, 0.003, 0.054, mat_idx=2, vg_idx=vg_root, chamfer=0.006)
        # 4 cardinal tick marks on dial
        for tx, tz in [(0.0, 0.021), (0.0, -0.021), (-0.021, 0.0), (0.021, 0.0)]:
            add_weighted_box(temp_bm, temp_def, (dx + tx, -0.0332, 0.046 + tz), 0.003, 0.002, 0.005, mat_idx=3, vg_idx=vg_root)
        # Minute hand (`vg_h`)
        add_weighted_box(temp_bm, temp_def, (dx, -0.034, 0.054), 0.004, 0.002, 0.018, mat_idx=3, vg_idx=vg_h)
        add_weighted_box(temp_bm, temp_def, (dx, -0.0345, 0.046), 0.006, 0.003, 0.006, mat_idx=1, vg_idx=vg_h)
        # Red timeout flag (`vg_fl`) near 11:55
        add_weighted_box(temp_bm, temp_def, (dx - 0.008, -0.0338, 0.061), 0.005, 0.002, 0.011, mat_idx=4, vg_idx=vg_fl, rot_deg=(0.0, 18.0, 0.0))

    # 3. Twin Rocking Brass Turn Buttons on Top (`vg_btn_w` at X = -0.044, `vg_btn_b` at X = +0.044, Z = 0.096)
    for dx, vg_b in [(-0.044, vg_btn_w), (0.044, vg_btn_b)]:
        add_weighted_box(temp_bm, temp_def, (dx, 0.0, 0.094), 0.022, 0.022, 0.010, mat_idx=1, vg_idx=vg_b, chamfer=0.002)
        add_weighted_box(temp_bm, temp_def, (dx, 0.0, 0.100), 0.028, 0.026, 0.004, mat_idx=1, vg_idx=vg_b, chamfer=0.001)

    rot_m = Euler((0.0, 0.0, math.radians(yaw_deg)), 'XYZ').to_matrix().to_4x4()
    trans_m = Matrix.Translation(Vector(center))
    xform = trans_m @ rot_m

    vert_map = {}
    for v in temp_bm.verts:
        nv = bm.verts.new(xform @ v.co)
        for k_vg, w_vg in v[temp_def].items():
            nv[deform][k_vg] = w_vg
        vert_map[v] = nv

    for f in temp_bm.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.material_index = f.material_index
        except ValueError:
            pass
    temp_bm.free()


# ==============================================================================
# 1. cozy_chess_marble_table
# ==============================================================================
def build_marble_table():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    e2_xy = square_xy(4, 1)
    e4_xy = square_xy(4, 3)

    bone_specs = [
        ("Root",                (0.0, 0.0, 0.0),                     (0.0, 0.0, 0.25),                    None),
        ("Piece_Drawer",        (0.140, 0.0, 0.652),                 (0.260, 0.0, 0.652),                 "Root"),
        ("Move_Highlight_From", (e2_xy[0], e2_xy[1], 0.725),         (e2_xy[0], e2_xy[1], 0.740),         "Root"),
        ("Move_Highlight_To",   (e4_xy[0], e4_xy[1], 0.725),         (e4_xy[0], e4_xy[1], 0.740),         "Root"),
        ("NPC_Hand_Target",     (0.180, 0.460, 0.760),               (0.180, 0.460, 0.810),               "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    mats = [
        "Chess_Marble_White_Veined",
        "Chess_Marble_Black_Veined",
        "Chess_Gold_Brass",
        "Chess_Groove_Slate",
        "Chess_Felt_Green",
        "Chess_Highlight_Glow",
    ]

    add_marble_table_geometry(
        bm, deform,
        vg_root=b_idx["Root"],
        vg_drawer=b_idx["Piece_Drawer"],
        vg_hl_from=b_idx["Move_Highlight_From"],
        vg_hl_to=b_idx["Move_Highlight_To"],
    )

    rig_obj, rest_mat = create_rig("Table_Rig", bone_specs)
    finalize_rigged_mesh("Chess_Table_Mesh", bm, rig_obj, bone_specs, mats)

    # 1. All 64 Board Square Sockets: Square_a1 .. Square_h8 at Z = 0.740 m
    for f_i, f_ch in enumerate(FILES):
        for r_i in range(8):
            sx, sy = square_xy(f_i, r_i)
            make_empty(f"Square_{f_ch}{r_i + 1}", (sx, sy, TABLE_TOP_Z), parent=rig_obj, bone_parent="Root", size=0.018)

    # 2. 16 Captured White Piece Slots along the Left (-X) White Marble Border
    for idx in range(16):
        col = idx // 8       # 0 or 1
        row = idx % 8        # 0..7
        cx = -0.305 - col * 0.048
        cy = (row - 3.5) * 0.062
        make_empty(f"Captured_W_{idx + 1:02d}", (cx, cy, TABLE_TOP_Z), parent=rig_obj, bone_parent="Root", size=0.015)

    # 3. 16 Captured Black Piece Slots along the Right (+X) White Marble Border
    for idx in range(16):
        col = idx // 8       # 0 or 1
        row = idx % 8        # 0..7
        cx = 0.305 + col * 0.048
        cy = (row - 3.5) * 0.062
        make_empty(f"Captured_B_{idx + 1:02d}", (cx, cy, TABLE_TOP_Z), parent=rig_obj, bone_parent="Root", size=0.015)

    # 4. Clock, Chair & NPC IK Hand Sockets
    make_empty("Clock_Spot",         (-0.330,  0.000, TABLE_TOP_Z), rot_deg=(0.0, 0.0, 90.0), parent=rig_obj, bone_parent="Root", size=0.03)
    make_empty("Chair_White_Spot",   ( 0.000, -0.680, 0.000),       rot_deg=(0.0, 0.0,   0.0), parent=rig_obj, bone_parent="Root", size=0.05)
    make_empty("Chair_Black_Spot",   ( 0.000,  0.680, 0.000),       rot_deg=(0.0, 0.0, 180.0), parent=rig_obj, bone_parent="Root", size=0.05)
    make_empty("NPC_IK_Hand_Target", ( 0.180,  0.460, 0.760),       rot_deg=(180.0, 0.0, 180.0), parent=rig_obj, bone_parent="NPC_Hand_Target", size=0.035)

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # Clip 1: Move_Guide_Pulse (60f: highlights e2 -> e4 squares and sweeps NPC_Hand_Target from Black rest to e7 -> e5 -> Clock_Spot)
    act_guide = bpy.data.actions.new(name="Move_Guide_Pulse")
    act_guide.use_fake_user = True
    rig_obj.animation_data.action = act_guide
    e7_xy = square_xy(4, 6)
    e5_xy = square_xy(4, 4)
    # Relative offsets from NPC_Hand_Target rest (0.180, 0.460, 0.760)
    for f, hl_dz, ik_dx, ik_dy, ik_dz in [
        (1,  0.000,  0.000,                  0.000,                  0.000),
        (12, 0.016,  e7_xy[0] - 0.180,       e7_xy[1] - 0.460,       0.035),
        (24, 0.018,  e7_xy[0] - 0.180,       e7_xy[1] - 0.460,      -0.005),
        (36, 0.016,  e5_xy[0] - 0.180,       e5_xy[1] - 0.460,       0.048),
        (46, 0.016,  e5_xy[0] - 0.180,       e5_xy[1] - 0.460,      -0.005),
        (54, 0.008, -0.330 - 0.180,          0.044 - 0.460,          0.082),
        (60, 0.000,  0.000,                  0.000,                  0.000),
    ]:
        key_frame(
            f,
            loc_map={
                "Move_Highlight_From": (0.0, 0.0, hl_dz),
                "Move_Highlight_To":   (0.0, 0.0, hl_dz),
                "NPC_Hand_Target":     (ik_dx, ik_dy, ik_dz),
            }
        )

    # Clip 2: Drawer_Slide_Open (50f: felt-lined storage drawer slides out +16 cm on +X side and closes)
    act_drawer = bpy.data.actions.new(name="Drawer_Slide_Open")
    act_drawer.use_fake_user = True
    rig_obj.animation_data.action = act_drawer
    for f, dx in [(1, 0.000), (20, 0.165), (32, 0.165), (50, 0.000)]:
        key_frame(f, loc_map={"Piece_Drawer": (dx, 0.0, 0.0)})

    # Clip 3: Board_Reset_Sweep (40f: highlight frames sweep across the ranks to signal new game start)
    act_reset = bpy.data.actions.new(name="Board_Reset_Sweep")
    act_reset.use_fake_user = True
    rig_obj.animation_data.action = act_reset
    for f, dy, dz in [
        (1,   0.000, 0.000),
        (8,  -0.065, 0.016),
        (28,  0.325, 0.016),
        (40,  0.000, 0.000),
    ]:
        key_frame(
            f,
            loc_map={
                "Move_Highlight_From": (0.0, dy, dz),
                "Move_Highlight_To":   (0.0, -dy, dz),
            }
        )

    save_and_export_chess("cozy_chess_marble_table", animated=True)


# ==============================================================================
# 2. cozy_chess_round_chair
# ==============================================================================
def build_round_chair():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",           (0.0, 0.0, 0.000), (0.0, 0.0, 0.060), None),
        ("Swivel_Column",  (0.0, 0.0, 0.060), (0.0, 0.0, 0.395), "Root"),
        ("Cushion_Squish", (0.0, 0.0, 0.395), (0.0, 0.0, 0.455), "Swivel_Column"),
        ("Tuft_Button",    (0.0, 0.0, 0.445), (0.0, 0.0, 0.462), "Cushion_Squish"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    mats = [
        "Chess_Marble_White_Veined",
        "Chess_Marble_Black_Veined",
        "Chess_Gold_Brass",
        "Chess_Cushion_Cream_Sage",
        "Chess_Cushion_Piping",
    ]

    add_round_chair_geometry(
        bm, deform, center=(0.0, 0.0, 0.0),
        vg_base=b_idx["Root"],
        vg_swivel=b_idx["Swivel_Column"],
        vg_cushion=b_idx["Cushion_Squish"],
        vg_tuft=b_idx["Tuft_Button"],
    )

    rig_obj, rest_mat = create_rig("Chair_Rig", bone_specs)
    finalize_rigged_mesh("Chess_Round_Chair_Mesh", bm, rig_obj, bone_specs, mats)

    # Seat & NPC Alignment Sockets (in Chair local space, +Y faces the table!)
    make_empty("Seat_Origin",      ( 0.000, 0.000, 0.460), parent=rig_obj, bone_parent="Cushion_Squish", size=0.04)
    make_empty("NPC_Spine_Anchor", ( 0.000, 0.000, 0.460), parent=rig_obj, bone_parent="Cushion_Squish", size=0.04)
    make_empty("Foot_Rest_L",      (-0.140, 0.240, 0.000), parent=rig_obj, bone_parent="Root",           size=0.03)
    make_empty("Foot_Rest_R",      ( 0.140, 0.240, 0.000), parent=rig_obj, bone_parent="Root",           size=0.03)
    make_empty("NPC_Hand_Rest_L",  (-0.180, 0.240, 0.740), parent=rig_obj, bone_parent="Swivel_Column",  size=0.03)
    make_empty("NPC_Hand_Rest_R",  ( 0.180, 0.240, 0.740), parent=rig_obj, bone_parent="Swivel_Column",  size=0.03)

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # Clip 1: Chair_Sit_Cushion_Squish (40f: cushion compresses when player/NPC sits down and settles)
    act_sit = bpy.data.actions.new(name="Chair_Sit_Cushion_Squish")
    act_sit.use_fake_user = True
    rig_obj.animation_data.action = act_sit
    for f, c_dz, t_dz in [
        (1,   0.000,  0.000),
        (10, -0.022, -0.008),
        (18, -0.012, -0.003),
        (28, -0.016, -0.005),
        (40,  0.000,  0.000),
    ]:
        key_frame(f, loc_map={"Cushion_Squish": (0.0, 0.0, c_dz), "Tuft_Button": (0.0, 0.0, t_dz)})

    # Clip 2: Chair_Swivel_Idle (60f: contemplative left/right swivel while studying the chess position)
    act_swivel = bpy.data.actions.new(name="Chair_Swivel_Idle")
    act_swivel.use_fake_user = True
    rig_obj.animation_data.action = act_swivel
    for f, yaw in [(1, 0.0), (15, 14.0), (30, 0.0), (45, -14.0), (60, 0.0)]:
        key_frame(f, rot_map={"Swivel_Column": (0.0, 0.0, yaw), "Cushion_Squish": (0.0, 0.0, yaw * 0.3)})

    # Clip 3: Chair_Slide_In_Out (50f: slides backward -18 cm along Y to let NPC stand/sit, then slides in)
    act_slide = bpy.data.actions.new(name="Chair_Slide_In_Out")
    act_slide.use_fake_user = True
    rig_obj.animation_data.action = act_slide
    for f, dy, yaw in [
        (1,   0.000,  0.0),
        (18, -0.180,  8.0),
        (32, -0.180, -4.0),
        (50,  0.000,  0.0),
    ]:
        key_frame(f, loc_map={"Root": (0.0, dy, 0.0)}, rot_map={"Swivel_Column": (0.0, 0.0, yaw)})

    save_and_export_chess("cozy_chess_round_chair", animated=True)


# ==============================================================================
# 3. cozy_chess_clock_analog
# ==============================================================================
def build_analog_clock():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    bone_specs = [
        ("Root",         ( 0.000,  0.000, 0.000), ( 0.000,  0.000, 0.040), None),
        ("Button_White", (-0.044,  0.000, 0.088), (-0.044,  0.000, 0.104), "Root"),
        ("Button_Black", ( 0.044,  0.000, 0.088), ( 0.044,  0.000, 0.104), "Root"),
        ("Hand_White",   (-0.044, -0.033, 0.046), (-0.044, -0.033, 0.064), "Root"),
        ("Hand_Black",   ( 0.044, -0.033, 0.046), ( 0.044, -0.033, 0.064), "Root"),
        ("Flag_White",   (-0.052, -0.033, 0.065), (-0.052, -0.033, 0.054), "Root"),
        ("Flag_Black",   ( 0.036, -0.033, 0.065), ( 0.036, -0.033, 0.054), "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    mats = [
        "Chess_Walnut_Wood",
        "Chess_Gold_Brass",
        "Chess_Clock_Dial_Cream",
        "Chess_Marble_Black_Veined",
        "Chess_Clock_Flag_Red",
    ]

    add_analog_clock_geometry(
        bm, deform, center=(0.0, 0.0, 0.0), yaw_deg=0.0,
        vg_root=b_idx["Root"],
        vg_btn_w=b_idx["Button_White"],
        vg_btn_b=b_idx["Button_Black"],
        vg_hand_w=b_idx["Hand_White"],
        vg_hand_b=b_idx["Hand_Black"],
        vg_flag_w=b_idx["Flag_White"],
        vg_flag_b=b_idx["Flag_Black"],
    )

    rig_obj, rest_mat = create_rig("Clock_Rig", bone_specs)
    finalize_rigged_mesh("Chess_Clock_Mesh", bm, rig_obj, bone_specs, mats)

    make_empty("Clock_Base",       ( 0.000, 0.000, 0.000), parent=rig_obj, bone_parent="Root",         size=0.025)
    make_empty("Hit_Button_White", (-0.044, 0.000, 0.102), parent=rig_obj, bone_parent="Button_White", size=0.020)
    make_empty("Hit_Button_Black", ( 0.044, 0.000, 0.102), parent=rig_obj, bone_parent="Button_Black", size=0.020)

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # Clip 1: Clock_Tick_Loop (60f: White hand ticks forward while White button is up)
    act_tick = bpy.data.actions.new(name="Clock_Tick_Loop")
    act_tick.use_fake_user = True
    rig_obj.animation_data.action = act_tick
    for f, deg_w in [(1, 0.0), (15, 15.0), (30, 30.0), (45, 45.0), (60, 60.0)]:
        key_frame(
            f,
            rot_map={"Hand_White": (0.0, deg_w, 0.0)},
            loc_map={"Button_White": (0.0, 0.0, 0.003), "Button_Black": (0.0, 0.0, -0.004)}
        )

    # Clip 2: Press_White_Turn (30f: White player taps left button down, popping Black button up!)
    act_pw = bpy.data.actions.new(name="Press_White_Turn")
    act_pw.use_fake_user = True
    rig_obj.animation_data.action = act_pw
    for f, zw, zb, r_roll in [
        (1,   0.004, -0.004,  0.0),
        (8,  -0.006,  0.005, -2.5),
        (14, -0.004,  0.004,  1.0),
        (30, -0.004,  0.004,  0.0),
    ]:
        key_frame(
            f,
            rot_map={"Root": (0.0, r_roll, 0.0)},
            loc_map={"Button_White": (0.0, 0.0, zw), "Button_Black": (0.0, 0.0, zb)}
        )

    # Clip 3: Press_Black_Turn (30f: NPC/Black player taps right button down, popping White button up!)
    act_pb = bpy.data.actions.new(name="Press_Black_Turn")
    act_pb.use_fake_user = True
    rig_obj.animation_data.action = act_pb
    for f, zw, zb, r_roll in [
        (1,  -0.004,  0.004,  0.0),
        (8,   0.005, -0.006,  2.5),
        (14,  0.004, -0.004, -1.0),
        (30,  0.004, -0.004,  0.0),
    ]:
        key_frame(
            f,
            rot_map={"Root": (0.0, r_roll, 0.0)},
            loc_map={"Button_White": (0.0, 0.0, zw), "Button_Black": (0.0, 0.0, zb)}
        )

    # Clip 4: Flag_Fall_Time_Out (40f: minute hand reaches 12:00 and red timeout flag drops!)
    act_flag = bpy.data.actions.new(name="Flag_Fall_Time_Out")
    act_flag.use_fake_user = True
    rig_obj.animation_data.action = act_flag
    for f, h_deg, f_deg in [
        (1,  -25.0,  35.0),
        (16,  -5.0,  58.0),
        (22,   2.0,   0.0),
        (28,   5.0, -12.0),
        (40,  10.0,   0.0),
    ]:
        key_frame(
            f,
            rot_map={"Hand_White": (0.0, h_deg, 0.0), "Flag_White": (0.0, f_deg, 0.0)}
        )

    save_and_export_chess("cozy_chess_clock_analog", animated=True)


# ==============================================================================
# 4. cozy_chess_station_set (Complete Assembled Table + 2 Round Chairs + Clock + 32 Starting Pieces)
# ==============================================================================
def build_station_set():
    init_scene()
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    e2_xy = square_xy(4, 1)
    e7_xy = square_xy(4, 6)
    g1_xy = square_xy(6, 0)
    b8_xy = square_xy(1, 7)

    bone_specs = [
        ("Root",              ( 0.000,  0.000, 0.000),              ( 0.000,  0.000, 0.250),              None),
        ("Chair_White",       ( 0.000, -0.680, 0.000),              ( 0.000, -0.680, 0.460),              "Root"),
        ("Chair_Black",       ( 0.000,  0.680, 0.000),              ( 0.000,  0.680, 0.460),              "Root"),
        ("Clock_Rocker",      (-0.330,  0.000, TABLE_TOP_Z),        (-0.330,  0.000, TABLE_TOP_Z + 0.10), "Root"),
        ("White_Pawn_e2",     (e2_xy[0], e2_xy[1], TABLE_TOP_Z),    (e2_xy[0], e2_xy[1], TABLE_TOP_Z + 0.05), "Root"),
        ("Black_Pawn_e7",     (e7_xy[0], e7_xy[1], TABLE_TOP_Z),    (e7_xy[0], e7_xy[1], TABLE_TOP_Z + 0.05), "Root"),
        ("White_Knight_g1",   (g1_xy[0], g1_xy[1], TABLE_TOP_Z),    (g1_xy[0], g1_xy[1], TABLE_TOP_Z + 0.08), "Root"),
        ("Black_Knight_b8",   (b8_xy[0], b8_xy[1], TABLE_TOP_Z),    (b8_xy[0], b8_xy[1], TABLE_TOP_Z + 0.08), "Root"),
        ("NPC_Hand_IK_Guide", ( 0.180,  0.460, 0.760),              ( 0.180,  0.460, 0.810),              "Root"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    # Unified Material Table for the Full Station:
    #  0: Chess_Marble_White_Veined
    #  1: Chess_Marble_Black_Veined
    #  2: Chess_Gold_Brass
    #  3: Chess_Groove_Slate
    #  4: Chess_Felt_Green
    #  5: Chess_Highlight_Glow
    #  6: Chess_Cushion_Cream_Sage
    #  7: Chess_Cushion_Piping
    #  8: Chess_Piece_White_Marble
    #  9: Chess_Piece_Black_Marble
    # 10: Chess_Felt_Crimson
    # 11: Chess_Walnut_Wood
    # 12: Chess_Clock_Dial_Cream
    # 13: Chess_Clock_Flag_Red
    mats = [
        "Chess_Marble_White_Veined",
        "Chess_Marble_Black_Veined",
        "Chess_Gold_Brass",
        "Chess_Groove_Slate",
        "Chess_Felt_Green",
        "Chess_Highlight_Glow",
        "Chess_Cushion_Cream_Sage",
        "Chess_Cushion_Piping",
        "Chess_Piece_White_Marble",
        "Chess_Piece_Black_Marble",
        "Chess_Felt_Crimson",
        "Chess_Walnut_Wood",
        "Chess_Clock_Dial_Cream",
        "Chess_Clock_Flag_Red",
    ]

    # 1. Marble Pedestal Chess Table at (0, 0, 0)
    add_marble_table_geometry(bm, deform, vg_root=b_idx["Root"])

    # 2. Two Round Marble & Cushion Drum Chairs at (0, -0.68, 0) and (0, +0.68, 0)
    #    Note: remap material indices 3->6 (Cushion) and 4->7 (Piping) on the chairs
    for chair_y, chair_bone in [(-0.680, "Chair_White"), (0.680, "Chair_Black")]:
        c_bm = bmesh.new()
        c_def = c_bm.verts.layers.deform.verify()
        vg_c = b_idx[chair_bone]
        add_round_chair_geometry(c_bm, c_def, center=(0.0, chair_y, 0.0), vg_base=vg_c, vg_swivel=vg_c, vg_cushion=vg_c, vg_tuft=vg_c)
        mat_remap_chair = {0: 0, 1: 1, 2: 2, 3: 6, 4: 7}
        vmap = {}
        for v in c_bm.verts:
            nv = bm.verts.new(v.co)
            for k, w in v[c_def].items():
                nv[deform][k] = w
            vmap[v] = nv
        for f in c_bm.faces:
            try:
                nf = bm.faces.new([vmap[v] for v in f.verts])
                nf.material_index = mat_remap_chair.get(f.material_index, 0)
            except ValueError:
                pass
        c_bm.free()

    # 3. Analog Chess Clock at Clock_Spot (-0.330, 0.0, 0.740), facing +X toward the board (yaw = -90 deg)
    clk_bm = bmesh.new()
    clk_def = clk_bm.verts.layers.deform.verify()
    vg_clk = b_idx["Clock_Rocker"]
    add_analog_clock_geometry(
        clk_bm, clk_def, center=(-0.330, 0.0, TABLE_TOP_Z), yaw_deg=-90.0,
        vg_root=vg_clk, vg_btn_w=vg_clk, vg_btn_b=vg_clk,
        vg_hand_w=vg_clk, vg_hand_b=vg_clk, vg_flag_w=vg_clk, vg_flag_b=vg_clk,
    )
    mat_remap_clk = {0: 11, 1: 2, 2: 12, 3: 1, 4: 13}
    vmap = {}
    for v in clk_bm.verts:
        nv = bm.verts.new(v.co)
        for k, w in v[clk_def].items():
            nv[deform][k] = w
        vmap[v] = nv
    for f in clk_bm.faces:
        try:
            nf = bm.faces.new([vmap[v] for v in f.verts])
            nf.material_index = mat_remap_clk.get(f.material_index, 11)
        except ValueError:
            pass
    clk_bm.free()

    # 4. All 32 Starting Pieces on Ranks 1, 2 (White) and Ranks 7, 8 (Black)
    back_rank_kinds = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    for f_i in range(8):
        # White Rank 1 (r_i = 0) & Rank 2 Pawns (r_i = 1)
        k_r1 = back_rank_kinds[f_i]
        vg_w1 = b_idx["White_Knight_g1"] if (f_i == 6) else b_idx["Root"]
        sx, sy = square_xy(f_i, 0)
        add_staunton_piece_geometry(
            bm, deform, k_r1, scale_k=PIECE_S, center=(sx, sy, TABLE_TOP_Z), yaw_deg=0.0,
            mat_body=8, mat_brass=2, mat_felt=4, vg_body=vg_w1, vg_crown=vg_w1
        )

        vg_w2 = b_idx["White_Pawn_e2"] if (f_i == 4) else b_idx["Root"]
        sx, sy = square_xy(f_i, 1)
        add_staunton_piece_geometry(
            bm, deform, "pawn", scale_k=PIECE_S, center=(sx, sy, TABLE_TOP_Z), yaw_deg=0.0,
            mat_body=8, mat_brass=2, mat_felt=4, vg_body=vg_w2, vg_crown=vg_w2
        )

        # Black Rank 7 Pawns (r_i = 6) & Rank 8 Officers (r_i = 7) — facing -Y (yaw_deg = 180.0)
        vg_b7 = b_idx["Black_Pawn_e7"] if (f_i == 4) else b_idx["Root"]
        sx, sy = square_xy(f_i, 6)
        add_staunton_piece_geometry(
            bm, deform, "pawn", scale_k=PIECE_S, center=(sx, sy, TABLE_TOP_Z), yaw_deg=180.0,
            mat_body=9, mat_brass=2, mat_felt=10, vg_body=vg_b7, vg_crown=vg_b7
        )

        k_r8 = back_rank_kinds[f_i]
        vg_b8 = b_idx["Black_Knight_b8"] if (f_i == 1) else b_idx["Root"]
        sx, sy = square_xy(f_i, 7)
        add_staunton_piece_geometry(
            bm, deform, k_r8, scale_k=PIECE_S, center=(sx, sy, TABLE_TOP_Z), yaw_deg=180.0,
            mat_body=9, mat_brass=2, mat_felt=10, vg_body=vg_b8, vg_crown=vg_b8
        )

    rig_obj, rest_mat = create_rig("Station_Rig", bone_specs)
    finalize_rigged_mesh("Chess_Station_Mesh", bm, rig_obj, bone_specs, mats)

    # Key Station Sockets
    make_empty("Player_White_Seat",  ( 0.000, -0.680, 0.460), rot_deg=(0.0, 0.0,   0.0), parent=rig_obj, bone_parent="Chair_White", size=0.05)
    make_empty("NPC_Black_Seat",     ( 0.000,  0.680, 0.460), rot_deg=(0.0, 0.0, 180.0), parent=rig_obj, bone_parent="Chair_Black", size=0.05)
    make_empty("Board_Center",       ( 0.000,  0.000, TABLE_TOP_Z),                      parent=rig_obj, bone_parent="Root",        size=0.04)
    make_empty("NPC_IK_Hand_Socket", ( 0.180,  0.460, 0.760), rot_deg=(180.0, 0.0, 180.0), parent=rig_obj, bone_parent="NPC_Hand_IK_Guide", size=0.04)

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # Clip 1: Station_Attract_Idle (60f: chairs swivel gently, knights nod)
    act_idle = bpy.data.actions.new(name="Station_Attract_Idle")
    act_idle.use_fake_user = True
    rig_obj.animation_data.action = act_idle
    for f, c_yaw, k_dz in [
        (1,   0.0, 0.000),
        (15,  8.0, 0.006),
        (30,  0.0, 0.000),
        (45, -8.0, 0.006),
        (60,  0.0, 0.000),
    ]:
        key_frame(
            f,
            rot_map={"Chair_White": (0.0, 0.0, c_yaw), "Chair_Black": (0.0, 0.0, -c_yaw)},
            loc_map={"White_Knight_g1": (0.0, 0.0, k_dz), "Black_Knight_b8": (0.0, 0.0, k_dz)},
        )

    # Clip 2: Opening_Move_e2e4_e7e5_Demo (60f: 1. e4 e5 opening + NPC hand IK guide + clock tap)
    act_open = bpy.data.actions.new(name="Opening_Move_e2e4_e7e5_Demo")
    act_open.use_fake_user = True
    rig_obj.animation_data.action = act_open
    dy_2sq = 2.0 * SQUARE_M  # 0.130 m
    for f, w_dy, w_dz, b_dy, b_dz, ik_dx, ik_dy, ik_dz, clk_pitch in [
        (1,  0.000,  0.000,   0.000,  0.000,  0.000,  0.000, 0.000,  0.0),
        (10, 0.065,  0.042,   0.000,  0.000,  0.000,  0.000, 0.000,  0.0),
        (20, dy_2sq, 0.000,   0.000,  0.000,  e7_xy[0] - 0.180, e7_xy[1] - 0.460, 0.040,  3.0),
        (28, dy_2sq, 0.000,   0.000,  0.000,  e7_xy[0] - 0.180, e7_xy[1] - 0.460, 0.000,  3.0),
        (38, dy_2sq, 0.000,  -0.065,  0.042,  e7_xy[0] - 0.180, e7_xy[1] - 0.065 - 0.460, 0.042,  3.0),
        (46, dy_2sq, 0.000, -dy_2sq,  0.000,  e7_xy[0] - 0.180, e7_xy[1] - dy_2sq - 0.460, 0.000,  3.0),
        (53, dy_2sq, 0.000, -dy_2sq,  0.000, -0.330 - 0.180,    0.044 - 0.460,            0.082, -3.5),
        (60, 0.000,  0.000,   0.000,  0.000,  0.000,  0.000, 0.000,  0.0),
    ]:
        key_frame(
            f,
            rot_map={"Clock_Rocker": (clk_pitch, 0.0, 0.0)},
            loc_map={
                "White_Pawn_e2":     (0.0, w_dy, w_dz),
                "Black_Pawn_e7":     (0.0, b_dy, b_dz),
                "NPC_Hand_IK_Guide": (ik_dx, ik_dy, ik_dz),
            }
        )

    # Clip 3: NPC_Knight_Develop_Demo (60f: White Nf3 & Black Nc6 L-shaped knight leaps over pawns)
    act_kn = bpy.data.actions.new(name="NPC_Knight_Develop_Demo")
    act_kn.use_fake_user = True
    rig_obj.animation_data.action = act_kn
    for f, wx, wy, wz, bx, by, bz in [
        (1,   0.000,     0.000,       0.000,  0.000,    0.000,       0.000),
        (12, -0.032,     SQUARE_M,    0.065,  0.000,    0.000,       0.000),
        (24, -SQUARE_M,  2*SQUARE_M,  0.000,  0.000,    0.000,       0.000),
        (38, -SQUARE_M,  2*SQUARE_M,  0.000,  0.032,   -SQUARE_M,    0.065),
        (50, -SQUARE_M,  2*SQUARE_M,  0.000,  SQUARE_M, -2*SQUARE_M, 0.000),
        (60,  0.000,     0.000,       0.000,  0.000,    0.000,       0.000),
    ]:
        key_frame(
            f,
            loc_map={
                "White_Knight_g1": (wx, wy, wz),
                "Black_Knight_b8": (bx, by, bz),
            }
        )

    save_and_export_chess("cozy_chess_station_set", animated=True)


if __name__ == "__main__":
    build_marble_table()
    build_round_chair()
    build_analog_clock()
    build_station_set()
    print("All 4 table/chair/clock/station models built and exported successfully.")
