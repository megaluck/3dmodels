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
    add_extruded_2d_outline_x,
    create_rig,
    finalize_rigged_mesh,
    make_empty,
    make_pose_helpers,
    save_and_export_chess,
)

# Tabletop scale factor: 1.0 unit in Staunton profile -> 0.105 m (King = 10.5 cm tall, Foot = 4.41 cm diameter on 6.5 cm squares)
PIECE_S = 0.105

BASE_H_UNITS = {
    "king":   1.00,
    "queen":  0.88,
    "bishop": 0.77,
    "knight": 0.73,
    "rook":   0.60,
    "pawn":   0.47,
}


def _arc(cz, rx, rz, deg_from, deg_to, n=7):
    pts = []
    for i in range(n + 1):
        a = math.radians(deg_from + (deg_to - deg_from) * i / n)
        pts.append((max(0.0005, rx * math.cos(a)), cz + rz * math.sin(a)))
    return pts


STAUNTON_BODY = {
    "pawn": [
        (0.165, 0.070), (0.165, 0.088), (0.150, 0.105), (0.120, 0.130),
        (0.095, 0.170), (0.078, 0.220), (0.070, 0.255), (0.114, 0.268),
        (0.114, 0.284), (0.062, 0.300),
        *_arc(0.385, 0.088, 0.088, -45, 90, 8),
    ],
    "rook": [
        (0.165, 0.070), (0.165, 0.090), (0.150, 0.112), (0.138, 0.150),
        (0.126, 0.240), (0.122, 0.370), (0.138, 0.390), (0.164, 0.410),
        (0.166, 0.430), (0.156, 0.440), (0.156, 0.530), (0.116, 0.530),
        (0.116, 0.500), (0.001, 0.500),
    ],
    "bishop": [
        (0.165, 0.070), (0.165, 0.090), (0.150, 0.112), (0.128, 0.150),
        (0.100, 0.240), (0.080, 0.350), (0.074, 0.420), (0.124, 0.440),
        (0.124, 0.456), (0.084, 0.470), (0.108, 0.486), (0.108, 0.500),
        (0.052, 0.512),
        *_arc(0.625, 0.096, 0.120, -62, 90, 9),
    ],
    "knight": [
        (0.165, 0.070), (0.165, 0.090), (0.152, 0.112), (0.140, 0.150),
        (0.136, 0.200), (0.152, 0.215), (0.152, 0.230), (0.001, 0.230),
    ],
    "queen": [
        (0.165, 0.070), (0.165, 0.090), (0.152, 0.112), (0.128, 0.150),
        (0.100, 0.260), (0.080, 0.400), (0.072, 0.500), (0.128, 0.520),
        (0.128, 0.536), (0.086, 0.550), (0.118, 0.570), (0.118, 0.582),
        (0.074, 0.600), (0.084, 0.660), (0.116, 0.725), (0.138, 0.758),
        (0.130, 0.772), (0.088, 0.768), (0.058, 0.786),
        *_arc(0.830, 0.050, 0.050, -55, 90, 6),
    ],
    "king": [
        (0.165, 0.070), (0.165, 0.090), (0.152, 0.112), (0.130, 0.150),
        (0.104, 0.270), (0.084, 0.420), (0.076, 0.550), (0.132, 0.572),
        (0.132, 0.588), (0.090, 0.600), (0.122, 0.620), (0.122, 0.632),
        (0.078, 0.650), (0.088, 0.710), (0.122, 0.780), (0.136, 0.810),
        (0.128, 0.822),
        *_arc(0.822, 0.128, 0.060, 0, 90, 6),
    ],
}

# Brass collar band height intervals in unscaled units (z_min, z_max)
COLLAR_BANDS_UNITS = {
    "pawn":   [(0.266, 0.286)],
    "rook":   [(0.388, 0.432)],
    "bishop": [(0.438, 0.458), (0.484, 0.502)],
    "knight": [(0.212, 0.232)],
    "queen":  [(0.518, 0.538), (0.568, 0.584)],
    "king":   [(0.570, 0.590), (0.618, 0.634)],
}

KNIGHT_HEAD_YZ = [
    (-0.115, 0.215), ( 0.095, 0.215), ( 0.105, 0.270), ( 0.082, 0.330),
    ( 0.092, 0.380), ( 0.150, 0.415), ( 0.188, 0.452), ( 0.196, 0.500),
    ( 0.182, 0.538), ( 0.142, 0.568), ( 0.070, 0.618), ( 0.045, 0.668),
    ( 0.022, 0.730), (-0.012, 0.690), (-0.040, 0.655), (-0.088, 0.600),
    (-0.128, 0.520), (-0.148, 0.420), (-0.152, 0.320), (-0.140, 0.255),
]


def add_staunton_piece_geometry(
    bm,
    deform_layer,
    kind,
    scale_k=PIECE_S,
    center=(0.0, 0.0, 0.0),
    yaw_deg=0.0,
    mat_body=0,
    mat_brass=1,
    mat_felt=2,
    vg_body=0,
    vg_crown=None,
):
    """
    Appends a complete tabletop Staunton piece to `bm` at `center`, rotated by `yaw_deg` around Z.
    Materials:
      mat_body  = main veined marble (white or black)
      mat_brass = polished gold brass collar & accents
      mat_felt  = green or crimson felt base pad
    Vertex groups:
      vg_body   = main piece body bone
      vg_crown  = optional upper head/crown bone (falls back to vg_body if None)
    """
    if vg_crown is None:
        vg_crown = vg_body

    s = scale_k
    h_split = 0.52 * BASE_H_UNITS[kind] * s

    def w_fn(z_local):
        return {vg_crown if z_local >= h_split else vg_body: 1.0}

    # Build at origin first, then rotate by yaw_deg and translate to center if needed
    temp_bm = bmesh.new()
    temp_def = temp_bm.verts.layers.deform.verify()

    # 1. Octagonal Felt Pad + Stepped Plinth (8-sided, flat face front/back via pi/8 offset)
    plinth_prof = [
        (0.208 * s, 0.000 * s),
        (0.210 * s, 0.018 * s),
        (0.210 * s, 0.058 * s),
        (0.180 * s, 0.070 * s),
    ]
    plinth_bands = [(0.000, 0.019 * s, mat_felt)]
    add_lathe_profile(
        temp_bm, temp_def, plinth_prof, sides=8, center=(0, 0, 0),
        rot_offset=math.pi / 8.0, mat_idx=mat_body, vg_idx=vg_body,
        band_ranges=plinth_bands, weight_fn=w_fn
    )

    # 2. Turned Staunton Body Profile (18-sided for crisp silhouette & compact triangle budget)
    body_prof = [(r * s, z * s) for (r, z) in STAUNTON_BODY[kind]]
    body_bands = [(z0 * s, z1 * s, mat_brass) for (z0, z1) in COLLAR_BANDS_UNITS[kind]]
    add_lathe_profile(
        temp_bm, temp_def, body_prof, sides=18, center=(0, 0, 0),
        rot_offset=0.0, mat_idx=mat_body, vg_idx=vg_body,
        band_ranges=body_bands, weight_fn=w_fn
    )

    # 3. Crown / Head Sculpted Details per Piece Kind
    h_u = BASE_H_UNITS[kind]
    if kind == "rook":
        # 6 fortress battlements (merlons) around the turret rim
        for i in range(6):
            ang_deg = i * 60.0
            rad = math.radians(ang_deg)
            mx = 0.137 * s * math.sin(rad)
            my = 0.137 * s * math.cos(rad)
            mz = 0.565 * s
            add_weighted_box(
                temp_bm, temp_def, (mx, my, mz),
                0.068 * s, 0.042 * s, 0.065 * s,
                mat_idx=mat_body, vg_idx=vg_crown, rot_deg=(0.0, 0.0, -ang_deg)
            )

    elif kind == "bishop":
        # Slanted mitre collar accent and top finial orb
        add_weighted_box(
            temp_bm, temp_def, (0.0, 0.032 * s, 0.655 * s),
            0.115 * s, 0.016 * s, 0.085 * s,
            mat_idx=mat_brass, vg_idx=vg_crown, rot_deg=(35.0, 0.0, 0.0)
        )
        orb_prof = _arc((h_u - 0.012) * s, 0.032 * s, 0.032 * s, -85, 85, 5)
        add_lathe_profile(
            temp_bm, temp_def, orb_prof, sides=10, center=(0, 0, 0),
            mat_idx=mat_brass, vg_idx=vg_crown
        )

    elif kind == "knight":
        # Sculpted horse head profile extruded along X, facing +Y in local space
        scaled_head = [(y * s, z * s) for (y, z) in KNIGHT_HEAD_YZ]
        add_extruded_2d_outline_x(
            temp_bm, temp_def, scaled_head, thickness_x=0.146 * s,
            center=(0.0, 0.0, 0.0), mat_idx=mat_body, vg_idx=vg_crown, weight_fn=w_fn
        )
        # 7 scalloped mane crests down the back of the neck
        for i in range(7):
            t = i / 6.0
            my = (-0.035 - t * 0.115) * s
            mz = (0.655 - t * 0.310) * s
            add_weighted_box(
                temp_bm, temp_def, (0.0, my, mz),
                0.072 * s, 0.056 * s, 0.048 * s,
                mat_idx=mat_body, vg_idx=vg_crown, rot_deg=(18.0, 0.0, 0.0)
            )
        # Twin sculpted ears on top of the head
        for sx in (-1.0, 1.0):
            add_weighted_box(
                temp_bm, temp_def, (sx * 0.045 * s, 0.018 * s, 0.725 * s),
                0.024 * s, 0.034 * s, 0.058 * s,
                mat_idx=mat_body, vg_idx=vg_crown, rot_deg=(-12.0, sx * 8.0, 0.0)
            )
            # Brass eyes
            add_weighted_box(
                temp_bm, temp_def, (sx * 0.076 * s, 0.062 * s, 0.600 * s),
                0.016 * s, 0.026 * s, 0.022 * s,
                mat_idx=mat_brass, vg_idx=vg_crown
            )

    elif kind == "queen":
        # 9 coronet pearls around the crown rim + brass finial sphere at apex
        for i in range(9):
            a = (2.0 * math.pi * i) / 9.0
            px = 0.130 * s * math.sin(a)
            py = 0.130 * s * math.cos(a)
            pz = 0.786 * s
            add_weighted_box(
                temp_bm, temp_def, (px, py, pz),
                0.032 * s, 0.032 * s, 0.034 * s,
                mat_idx=mat_brass, vg_idx=vg_crown, rot_deg=(0.0, 0.0, math.degrees(-a))
            )
        orb_prof = _arc((h_u - 0.005) * s, 0.026 * s, 0.026 * s, -85, 85, 4)
        add_lathe_profile(
            temp_bm, temp_def, orb_prof, sides=10, center=(0, 0, 0),
            mat_idx=mat_brass, vg_idx=vg_crown
        )

    elif kind == "king":
        # Royal Finial Cross at apex (vertical shaft + horizontal crossbar)
        add_weighted_box(
            temp_bm, temp_def, (0.0, 0.0, (h_u - 0.062) * s),
            0.046 * s, 0.042 * s, 0.132 * s,
            mat_idx=mat_brass, vg_idx=vg_crown
        )
        add_weighted_box(
            temp_bm, temp_def, (0.0, 0.0, (h_u - 0.055) * s),
            0.122 * s, 0.042 * s, 0.044 * s,
            mat_idx=mat_brass, vg_idx=vg_crown
        )

    # Transform temp_bm into bm at (center, yaw_deg)
    rot_m = Euler((0.0, 0.0, math.radians(yaw_deg)), 'XYZ').to_matrix().to_4x4()
    trans_m = Matrix.Translation(Vector(center))
    xform = trans_m @ rot_m

    vert_map = {}
    for v in temp_bm.verts:
        nv = bm.verts.new(xform @ v.co)
        for k_vg, w_vg in v[temp_def].items():
            nv[deform_layer][k_vg] = w_vg
        vert_map[v] = nv

    for f in temp_bm.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.material_index = f.material_index
        except ValueError:
            pass

    temp_bm.free()


def build_single_chess_piece(side, kind):
    """
    Builds and exports `cozy_chess_<side>_<kind>` (e.g. `cozy_chess_white_king`).
    """
    init_scene()
    asset_name = f"cozy_chess_{side}_{kind}"
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    h_m = BASE_H_UNITS[kind] * PIECE_S
    h_mid = 0.52 * h_m

    bone_specs = [
        ("Root",         (0.0, 0.0, 0.0),   (0.0, 0.0, 0.015), None),
        ("Body_Tilt",    (0.0, 0.0, 0.004), (0.0, 0.0, h_mid), "Root"),
        ("Crown_Accent", (0.0, 0.0, h_mid), (0.0, 0.0, h_m),   "Body_Tilt"),
    ]
    b_idx = {b[0]: i for i, b in enumerate(bone_specs)}

    if side == "white":
        mats = ["Chess_Piece_White_Marble", "Chess_Gold_Brass", "Chess_Felt_Green"]
    else:
        mats = ["Chess_Piece_Black_Marble", "Chess_Gold_Brass", "Chess_Felt_Crimson"]

    # White pieces face +Y (toward Black); Black pieces face -Y in world when placed, or +Y in local space
    add_staunton_piece_geometry(
        bm, deform, kind, scale_k=PIECE_S, center=(0.0, 0.0, 0.0), yaw_deg=0.0,
        mat_body=0, mat_brass=1, mat_felt=2,
        vg_body=b_idx["Body_Tilt"], vg_crown=b_idx["Crown_Accent"]
    )

    rig_obj, rest_mat = create_rig("Piece_Rig", bone_specs)
    finalize_rigged_mesh(f"Chess_{side.capitalize()}_{kind.capitalize()}_Mesh", bm, rig_obj, bone_specs, mats)

    # Gameplay Sockets:
    # 1. Piece_Base at (0, 0, 0) — snaps onto Square_a1..h8 or Captured_W/B_01..16
    make_empty("Piece_Base", (0.0, 0.0, 0.0), parent=rig_obj, bone_parent="Root", size=0.025)
    # 2. Grab_Top near the top neck/finial — local +Z points straight down into the stem (rot X = 180 deg) for VR/NPC pinch
    make_empty("Grab_Top", (0.0, 0.0, h_m - 0.010), rot_deg=(180.0, 0.0, 0.0), parent=rig_obj, bone_parent="Crown_Accent", size=0.025)
    # 3. Crown_Tip at exact apex
    make_empty("Crown_Tip", (0.0, 0.0, h_m), parent=rig_obj, bone_parent="Crown_Accent", size=0.020)

    _, _, key_frame = make_pose_helpers(rig_obj, rest_mat)

    # Clip 1: Piece_Lift_Hop (36f: lifted up +4.5cm with slight pitch as picked up by player/NPC, arcs, and settles cleanly)
    act_lift = bpy.data.actions.new(name="Piece_Lift_Hop")
    act_lift.use_fake_user = True
    rig_obj.animation_data.action = act_lift
    for f, dz, pitch, cr_pitch in [
        (1,  0.000,   0.0,  0.0),
        (8,  0.032, -12.0, -4.0),
        (18, 0.048,  -6.0,  3.0),
        (27, 0.014,   8.0,  4.0),
        (31, 0.000,  -3.5, -2.0),
        (36, 0.000,   0.0,  0.0),
    ]:
        key_frame(
            f,
            rot_map={"Body_Tilt": (pitch, 0.0, 0.0), "Crown_Accent": (cr_pitch, 0.0, 0.0)},
            loc_map={"Body_Tilt": (0.0, 0.0, dz)}
        )

    # Clip 2: Piece_Slide_Place (30f: smooth forward tabletop slide-in and tactile rim rock when placed on a square)
    act_slide = bpy.data.actions.new(name="Piece_Slide_Place")
    act_slide.use_fake_user = True
    rig_obj.animation_data.action = act_slide
    for f, dy, pitch, roll in [
        (1,  -0.045,  5.0,  0.0),
        (14,  0.000, -7.5,  2.5),
        (20,  0.000,  4.0, -2.0),
        (25,  0.000, -1.8,  0.8),
        (30,  0.000,  0.0,  0.0),
    ]:
        key_frame(
            f,
            rot_map={"Body_Tilt": (pitch, roll, 0.0)},
            loc_map={"Body_Tilt": (0.0, dy, 0.0)}
        )

    # Clip 3: Piece_Capture_Tip_Fall (40f: struck by capturing piece, tips back onto base edge, and topples 90 deg onto its side)
    act_cap = bpy.data.actions.new(name="Piece_Capture_Tip_Fall")
    act_cap.use_fake_user = True
    rig_obj.animation_data.action = act_cap
    for f, dy, dz, pitch, roll in [
        (1,  0.000, 0.000,   0.0,  0.0),
        (6,  0.006, 0.004, -18.0,  6.0),
        (14, 0.014, 0.008, -48.0, 14.0),
        (24, 0.026, 0.016, -88.0, 22.0),
        (30, 0.028, 0.018, -82.0, 18.0),
        (40, 0.028, 0.016, -88.0, 20.0),
    ]:
        key_frame(
            f,
            rot_map={"Body_Tilt": (pitch, roll, 0.0)},
            loc_map={"Body_Tilt": (0.0, dy, dz)}
        )

    # Clip 4: King_Check_Shiver (36f: nervous rapid tremor when in check or threatened)
    act_check = bpy.data.actions.new(name="King_Check_Shiver")
    act_check.use_fake_user = True
    rig_obj.animation_data.action = act_check
    for f, roll, yaw in [
        (1,   0.0,   0.0),
        (5,   5.5,   6.0),
        (10, -5.5,  -6.0),
        (15,  6.0,   7.0),
        (20, -6.0,  -7.0),
        (25,  4.5,   5.0),
        (30, -3.5,  -4.0),
        (36,  0.0,   0.0),
    ]:
        key_frame(
            f,
            rot_map={"Body_Tilt": (0.0, roll, yaw), "Crown_Accent": (0.0, roll * 0.6, -yaw * 0.5)}
        )

    save_and_export_chess(asset_name, animated=True)


if __name__ == "__main__":
    for side in ("white", "black"):
        for kind in ("king", "queen", "rook", "bishop", "knight", "pawn"):
            build_single_chess_piece(side, kind)
    print("All 12 standalone rigged chess pieces exported successfully.")
