import bpy
import bmesh
import math
import os
import sys
import shutil
from mathutils import Vector, Euler, Matrix

sys.path.insert(0, "C:/argon/rapa_nui")
from rapa_builder_utils import (
    PALETTE, hex_to_srgb, srgb_to_linear, get_mat, ensure_mat_slot,
    init_scene, make_mesh_obj, make_empty, make_frame_from_dir_and_normal,
    add_lofted_tube, add_faceted_rock
)

# "Coral Lanes" Mid-Century Aquarium Mall Bowling & Retro Arcade Palette
# (All colors automatically converted from sRGB hex to Scene-Linear RGB via get_mat)
PALETTE.update({
    "Bowling_Maple_Light":   ("#E8CFA8", 0.32, 0.00),  # Polished blonde hard-maple lane boards & pins
    "Bowling_Maple_Amber":   ("#C79252", 0.34, 0.00),  # Warm amber heartwood alternating lane strips
    "Bowling_Walnut_Dark":   ("#593A22", 0.45, 0.00),  # Inlaid aiming arrows, approach dots & cabinet trim
    "Bowling_Gutter_Slate":  ("#343B42", 0.55, 0.10),  # Deep semi-circular ABS gutter channels
    "Bowling_Coral_Pink":    ("#E26A52", 0.38, 0.00),  # Mid-century Coral Lanes primary accent & 8lb ball
    "Bowling_Teal_Seafoam":  ("#2D8A7E", 0.35, 0.05),  # Seafoam teal fiberglass hood, bumpers & 12lb ball
    "Bowling_Cream_Pearl":   ("#F4EFE6", 0.40, 0.00),  # Glossy pin lacquer, sofa vinyl & storefront trim
    "Bowling_Crimson_Stripe":("#C82822", 0.35, 0.00),  # Classic bowling pin neck stripes & arcade buttons
    "Bowling_Gold_Brass":    ("#D8A638", 0.28, 0.85),  # Brushed brass trim, Golden Pin, trophy & bell
    "Bowling_Chrome_Steel":  ("#C4CBD0", 0.22, 0.90),  # Chrome ball-return rails, sweep rake & coin door
    "Bowling_Obsidian_Ball": ("#1C2026", 0.20, 0.15),  # Heavy 15lb pro hook bowling ball & black rubber
    "Bowling_Foul_Red":      ("#F03228", 0.25, 0.00),  # Foul line sensor light & arcade LED beacon
    "Bowling_Bumper_Yellow": ("#F2C138", 0.42, 0.00),  # High-visibility pop-up gutter bumper rail
    "Bowling_Mall_Wall":     ("#EDE5DC", 0.78, 0.00),  # Warm Aquarium Mall plaster wall
    "Bowling_Mall_Floor":    ("#D6C7BC", 0.65, 0.00),  # Mall concourse tile & approach surround
    "Bowling_Glass_Tint":    ("#8AB8C2", 0.18, 0.10),  # Storefront display window glass
    "Bowling_Arcade_Blue":   ("#1F3B6E", 0.48, 0.00),  # Classic 1978 Space Invaders cabinet side art blue
    "Bowling_Arcade_Green":  ("#48C858", 0.35, 0.00),  # Retro pixel alien green & marquee accent
    "Bowling_Neon_Cyan":     ("#38E8E0", 0.15, 0.00),  # Glowing retro neon cyan tubing & slushie ice blue
    "Bowling_Neon_Pink":     ("#FF5876", 0.15, 0.00),  # Glowing retro neon coral-pink tubing & jukebox arch
    "Bowling_Plant_Green":   ("#2E7D47", 0.45, 0.00),  # Lush indoor Monstera & snake plant foliage
    "Bowling_Pretzel_Crust": ("#A86228", 0.48, 0.00),  # Golden-brown pretzel & pizza crust
    # House Ball Weight Series (6, 8, 10, 12, 14, 16 lb) new colors from artist brief:
    "Bowling_Ball_Lilac":    ("#B79AD6", 0.24, 0.00),  # 6 lb house ball primary lilac
    "Bowling_Ball_Sunflower":("#F2C138", 0.25, 0.00),  # 10 lb house ball primary sunflower yellow
    "Bowling_Ball_Seafoam":  ("#9FDCCF", 0.28, 0.00),  # 12 lb house ball seafoam swirl accent
    "Bowling_Ball_Ocean":    ("#2B5C9E", 0.24, 0.05),  # 14 lb house ball primary ocean blue
    "Bowling_Ball_Navy":     ("#1C2F55", 0.28, 0.05),  # 14 lb house ball deep navy swirl accent
    # Dedicated single-quad [0, 1] UV screen materials (1 quad per material so Unity C# can bind RenderTextures!)
    "Bowling_Screen_L":      ("#14242B", 0.25, 0.00),  # Overhead Scoreboard Left Lane 1 screen quad
    "Bowling_Screen_R":      ("#14242B", 0.25, 0.00),  # Overhead Scoreboard Right Lane 2 screen quad
    "Arcade_CRT_Screen":     ("#0E1821", 0.20, 0.00),  # Space Invaders Cabinet CRT screen quad
})


def add_box(bm, center, sx, sy, sz, mat_idx, rot_deg=(0.0, 0.0, 0.0), bevel_w=0.0):
    sub = bmesh.new()
    bmesh.ops.create_cube(sub, size=1.0)
    rot_m = Euler([math.radians(a) for a in rot_deg], 'XYZ').to_matrix()
    c_vec = Vector(center)
    for v in sub.verts:
        local = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
        v.co = c_vec + rot_m @ local
    if bevel_w > 0.0:
        try:
            bmesh.ops.bevel(sub, geom=list(sub.edges), offset=bevel_w, segments=1, affect='EDGES')
        except Exception:
            pass
    bmesh.ops.recalc_face_normals(sub, faces=sub.faces)
    faces_out = []
    for f in sub.faces:
        nv = [bm.verts.new(v.co) for v in f.verts]
        try:
            nf = bm.faces.new(nv)
            nf.material_index = mat_idx
            faces_out.append(nf)
        except ValueError:
            pass
    sub.free()
    return faces_out


def add_weighted_box(bm, deform, center, sx, sy, sz, mat_idx, vg_idx, rot_deg=(0.0, 0.0, 0.0), bevel_w=0.0):
    faces = add_box(bm, center, sx, sy, sz, mat_idx, rot_deg=rot_deg, bevel_w=bevel_w)
    for f in faces:
        for v in f.verts:
            v[deform][vg_idx] = 1.0
    return faces


def add_weighted_tube(bm, deform, pts_radii, sides, mat_idx, vg_idx, cap_start=True, cap_end=True, mat_end_idx=None, closed_ring=False):
    rings = add_lofted_tube(
        bm, pts_radii, sides=sides,
        cap_start=cap_start, cap_end=cap_end,
        mat_idx=mat_idx, mat_end_idx=mat_end_idx,
        closed_ring=closed_ring
    )
    for r in rings:
        for v in r:
            v[deform][vg_idx] = 1.0
    return rings


def add_uv_screen_quad(bm, deform, center, width_x, height_z, mat_idx, vg_idx, tilt_deg=0.0):
    """
    Creates a single-quad screen facing -Y (or tilted by tilt_deg around X)
    with guaranteed outward normal (normal.y < 0) and returns (face, uv_map_dict)
    so the caller can assign exact [0, 1] x [0, 1] bounds UVs!
    """
    cx, cy, cz = center
    hw = width_x * 0.5
    hh = height_z * 0.5
    rot_m = Euler((math.radians(tilt_deg), 0.0, 0.0), 'XYZ').to_matrix()
    c_vec = Vector((cx, cy, cz))

    corners_local = [
        (Vector((-hw, 0.0, -hh)), (0.0, 0.0)),  # Bottom-Left
        (Vector(( hw, 0.0, -hh)), (1.0, 0.0)),  # Bottom-Right
        (Vector(( hw, 0.0,  hh)), (1.0, 1.0)),  # Top-Right
        (Vector((-hw, 0.0,  hh)), (0.0, 1.0)),  # Top-Left
    ]
    verts = []
    uv_dict = {}
    for loc_v, uv_pt in corners_local:
        v = bm.verts.new(c_vec + rot_m @ loc_v)
        if deform is not None and vg_idx is not None:
            v[deform][vg_idx] = 1.0
        verts.append(v)
        uv_dict[v] = uv_pt

    f = bm.faces.new(verts)
    f.material_index = mat_idx
    f.normal_update()
    expected_n = rot_m @ Vector((0.0, -1.0, 0.0))
    if f.normal.dot(expected_n) < 0.0:
        f.normal_flip()
    return f, uv_dict


def apply_screen_uvs(bm, screen_face_uv_list):
    """
    screen_face_uv_list: list of (face, uv_dict) pairs.
    Assigns exact [0, 1] UVs on UVMap for each screen quad and (0, 0) elsewhere.
    """
    uv_layer = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    face_lookup = {f: uvd for f, uvd in screen_face_uv_list}
    for f in bm.faces:
        uvd = face_lookup.get(f)
        for loop in f.loops:
            if uvd and loop.vert in uvd:
                loop[uv_layer].uv = uvd[loop.vert]
            else:
                loop[uv_layer].uv = (0.0, 0.0)


def create_rig(name, bone_specs):
    arm_data = bpy.data.armatures.new(name)
    rig_obj = bpy.data.objects.new(name, arm_data)
    bpy.context.collection.objects.link(rig_obj)
    bpy.context.view_layer.objects.active = rig_obj
    bpy.ops.object.mode_set(mode='EDIT')
    eb_map = {}
    for bname, h, t, p in bone_specs:
        eb = arm_data.edit_bones.new(bname)
        eb.head = Vector(h)
        eb.tail = Vector(t)
        eb.use_connect = False
        eb.inherit_scale = 'NONE'
        eb_map[bname] = eb
    for bname, _, _, p in bone_specs:
        if p and p in eb_map:
            eb_map[bname].parent = eb_map[p]
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in rig_obj.pose.bones:
        pb.rotation_mode = 'XYZ'
    rig_obj.animation_data_create()
    return rig_obj, {b.name: b.matrix_local.to_3x3() for b in arm_data.bones}


def make_pose_helpers(rig_obj, bone_rest_mat):
    def set_world_rot(bname, pitch_deg=0.0, roll_deg=0.0, yaw_deg=0.0):
        b_rest = bone_rest_mat[bname]
        r_world = Euler((math.radians(pitch_deg), math.radians(roll_deg), math.radians(yaw_deg)), 'XYZ').to_matrix()
        rig_obj.pose.bones[bname].rotation_euler = (b_rest.inverted() @ r_world @ b_rest).to_euler('XYZ')

    def set_world_loc(bname, dx=0.0, dy=0.0, dz=0.0):
        b_rest = bone_rest_mat[bname]
        rig_obj.pose.bones[bname].location = b_rest.inverted() @ Vector((dx, dy, dz))

    def key_frame(frame, rot_map=None, loc_map=None, scale_map=None):
        rot_map = rot_map or {}
        loc_map = loc_map or {}
        scale_map = scale_map or {}
        bpy.context.scene.frame_set(frame)
        for pb in rig_obj.pose.bones:
            bname = pb.name
            pr, rr, yr = rot_map.get(bname, (0.0, 0.0, 0.0))
            dx, dy, dz = loc_map.get(bname, (0.0, 0.0, 0.0))
            sx, sy, sz = scale_map.get(bname, (1.0, 1.0, 1.0))
            set_world_rot(bname, pr, rr, yr)
            set_world_loc(bname, dx, dy, dz)
            pb.scale = (sx, sy, sz)
            pb.keyframe_insert(data_path="location", frame=frame)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame)
            if scale_map:
                pb.keyframe_insert(data_path="scale", frame=frame)

    return set_world_rot, set_world_loc, key_frame


def finalize_rigged_mesh(mesh_name, bm, rig_obj, bone_specs, mat_names, origin=(0.0, 0.0, 0.0), merge_doubles=True):
    ox, oy, oz = origin
    if abs(ox) > 1e-6 or abs(oy) > 1e-6 or abs(oz) > 1e-6:
        bmesh.ops.translate(bm, verts=bm.verts, vec=(-ox, -oy, -oz))
    if merge_doubles:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0004)
    mesh = bpy.data.meshes.new(mesh_name)
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = False
    obj = bpy.data.objects.new(mesh_name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = Vector(origin)
    for m in mat_names:
        ensure_mat_slot(obj, m)
    obj.parent = rig_obj
    mod = obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = rig_obj
    for bname, _, _, _ in bone_specs:
        obj.vertex_groups.new(name=bname)
    return obj


def save_and_export_bowling(model_name, animated=True):
    out_dirs = ["C:/argon/bowling", "C:/3dassets/argon/bowling"]
    for d in out_dirs:
        os.makedirs(d, exist_ok=True)

    for m in list(bpy.data.materials):
        if "." in m.name:
            base = m.name.split(".")[0]
            if base in PALETTE:
                m.name = base

    bpy.context.scene.frame_set(1)
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            obj.data.pose_position = 'POSE'
            for pb in obj.pose.bones:
                pb.location = (0.0, 0.0, 0.0)
                pb.rotation_mode = 'XYZ'
                pb.rotation_euler = (0.0, 0.0, 0.0)
                pb.scale = (1.0, 1.0, 1.0)

    blend_primary = f"C:/argon/bowling/{model_name}.blend"
    fbx_primary = f"C:/argon/bowling/{model_name}.fbx"
    glb_primary = f"C:/argon/bowling/{model_name}.glb"

    bpy.ops.wm.save_as_mainfile(filepath=blend_primary)

    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type in {'MESH', 'ARMATURE', 'EMPTY'}:
            obj.select_set(True)

    bpy.ops.export_scene.fbx(
        filepath=fbx_primary,
        use_selection=True,
        object_types={'EMPTY', 'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        bake_anim=animated,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=animated,
        bake_anim_force_startend_keying=True,
        bake_anim_simplify_factor=0.0,
    )

    try:
        bpy.ops.export_scene.gltf(
            filepath=glb_primary,
            use_selection=True,
            export_format='GLB',
            export_animations=animated,
        )
        bpy.ops.export_scene.gltf(
            filepath=f"C:/argon/bowling/{model_name}.gltf",
            use_selection=True,
            export_format='GLTF_SEPARATE',
            export_animations=animated,
        )
    except Exception:
        pass

    try:
        bpy.ops.wm.alembic_export(filepath=f"C:/argon/bowling/{model_name}.abc", selected=True, start=1, end=30)
    except Exception:
        pass

    # Static formats exported in REST pose
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            obj.data.pose_position = 'REST'
    try:
        bpy.ops.wm.obj_export(filepath=f"C:/argon/bowling/{model_name}.obj", export_selected_objects=True)
        bpy.ops.wm.stl_export(filepath=f"C:/argon/bowling/{model_name}.stl", export_selected_objects=True)
        bpy.ops.wm.ply_export(filepath=f"C:/argon/bowling/{model_name}.ply", export_selected_objects=True)
        bpy.ops.wm.usd_export(filepath=f"C:/argon/bowling/{model_name}.usdc", selected_objects_only=True)
    except Exception:
        pass
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            obj.data.pose_position = 'POSE'

    for ext in (".blend", ".fbx", ".glb", ".gltf", ".bin", ".abc", ".obj", ".mtl", ".stl", ".ply", ".usdc"):
        src = f"C:/argon/bowling/{model_name}{ext}"
        if os.path.exists(src):
            shutil.copy2(src, f"C:/3dassets/argon/bowling/{model_name}{ext}")

    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    total_tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
    total_verts = sum(len(o.data.vertices) for o in meshes)
    n_actions = len(bpy.data.actions)
    print(f"[BOWLING EXPORTED] {model_name}: {len(meshes)} meshes, {total_tris} tris, {total_verts} verts, {n_actions} actions")
