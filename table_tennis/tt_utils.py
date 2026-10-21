"""
Shared utilities for the Table Tennis (Ping Pong) Mini-Game asset suite:
- Scene-Linear RGB procedural shaders (Tournament Matte Blue, Forest Green Park Top,
  Natural 5-Ply Beechwood, Carbon Fiber Weave, ITTF Red & Black Sponge Rubber,
  Electric Cyan/Magenta Pro Rubber, Cast-Iron Skillet, White/Orange/Two-Tone 3-Star ABS Balls,
  White Nylon Net Mesh, Brushed Chrome, Warm Teak, Polished Brass, Acrylic Hopper)
- BMesh procedural geometry builders with deterministic bone weights
- Blender 5.2 slotted action & world-space pose helpers
- Clean 9-format exporter (.blend, .fbx, .glb, .gltf, .obj, .stl, .ply, .usdc, .abc)
"""

import os
import math
import shutil
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler


OUT_DIR_PRIMARY = "C:/argon/table_tennis"
OUT_DIR_MIRROR = "C:/3dassets/argon/table_tennis"


def srgb_to_linear(c):
    def ch(x):
        return x / 12.92 if x <= 0.04045 else pow((x + 0.055) / 1.055, 2.4)
    return (ch(c[0]), ch(c[1]), ch(c[2]), c[3] if len(c) > 3 else 1.0)


def hex_to_linear(hex_str, alpha=1.0):
    h = hex_str.lstrip('#')
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return srgb_to_linear((r, g, b, alpha))


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.render.fps = 24
    return scene


def make_solid_mat(name, hex_color, roughness=0.4, metallic=0.0, coat=0.0, alpha=1.0, emission_strength=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    lin = hex_to_linear(hex_color, alpha)
    bsdf.inputs["Base Color"].default_value = lin
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        if hasattr(mat, "blend_method"):
            mat.blend_method = 'BLEND'
    if emission_strength > 0.0 and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = lin
        bsdf.inputs["Emission Strength"].default_value = emission_strength

    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_wood_mat(name, base_hex, grain_hex, roughness=0.38, coat=0.15):
    """
    Sets Base Color directly in Scene-Linear RGB so glTF 2.0 (.glb/.gltf) and FBX
    export the exact rich wood tone instead of falling back to white.
    """
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = hex_to_linear(base_hex)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat

    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def create_tt_palette():
    """Creates and returns the standard 22-material palette for all Table Tennis assets."""
    mats = [
        # 0: Tournament Matte Blue Table Surface
        make_solid_mat("TT_Table_Blue", "#1B4F9C", roughness=0.36, metallic=0.0, coat=0.08),
        # 1: Outdoor Garden Forest Green Table Surface
        make_solid_mat("TT_Table_Green", "#1E563B", roughness=0.38, metallic=0.0, coat=0.08),
        # 2: Crisp White Boundary Lines & Score Numbers
        make_solid_mat("TT_Line_White", "#F7F9FC", roughness=0.32, metallic=0.0),
        # 3: Dark Powder-Coat Steel Undercarriage
        make_solid_mat("TT_Steel_Dark", "#22262E", roughness=0.42, metallic=0.75),
        # 4: Brushed Chrome / Stainless Metal
        make_solid_mat("TT_Chrome", "#D8DEE6", roughness=0.18, metallic=0.92),
        # 5: Polished Club Brass / Gold Accents
        make_solid_mat("TT_Brass", "#D6A138", roughness=0.22, metallic=0.88),
        # 6: Crimson Powder-Coat Strut / Flip Card Red
        make_solid_mat("TT_Accent_Red", "#C92A2A", roughness=0.34, metallic=0.15),
        # 7: White Nylon Net Mesh
        make_solid_mat("TT_Net_Mesh", "#EAECEF", roughness=0.65, metallic=0.0),
        # 8: Navy Net Post Clamp & Barrier Fabric
        make_solid_mat("TT_Navy_Fabric", "#162A4A", roughness=0.68, metallic=0.0),
        # 9: Warm Teak / Walnut Hardwood
        make_wood_mat("TT_Wood_Walnut", "#6E4226", "#422411", roughness=0.34, coat=0.2),
        # 10: Natural 5-Ply Beechwood Paddle Blade
        make_wood_mat("TT_Wood_Beech", "#D9A973", "#B58149", roughness=0.42, coat=0.05),
        # 11: ITTF Forehand Pimpled Red Sponge Rubber
        make_solid_mat("TT_Rubber_Red", "#D1232A", roughness=0.48, metallic=0.0, coat=0.05),
        # 12: ITTF Backhand Pimpled Black Sponge Rubber
        make_solid_mat("TT_Rubber_Black", "#1C1E22", roughness=0.48, metallic=0.0, coat=0.05),
        # 13: Carbon Fiber Weave
        make_solid_mat("TT_Carbon_Weave", "#15171C", roughness=0.26, metallic=0.45, coat=0.3),
        # 14: Pro Spin Electric Cyan Rubber
        make_solid_mat("TT_Rubber_Cyan", "#00A8E8", roughness=0.44, metallic=0.0, coat=0.1),
        # 15: Pro Spin Electric Magenta Rubber
        make_solid_mat("TT_Rubber_Magenta", "#E0218A", roughness=0.44, metallic=0.0, coat=0.1),
        # 16: 3-Star Matte White Celluloid/ABS Ball
        make_solid_mat("TT_Ball_White", "#FAF8F2", roughness=0.28, metallic=0.0, coat=0.12),
        # 17: 3-Star Tournament Orange Ball
        make_solid_mat("TT_Ball_Orange", "#FF7A18", roughness=0.28, metallic=0.0, coat=0.12),
        # 18: Clear Acrylic Hopper Plastic
        make_solid_mat("TT_Acrylic_Clear", "#DDF0FF", roughness=0.12, metallic=0.0, coat=0.4, alpha=0.38),
        # 19: Cast Iron Seasoned Skillet
        make_solid_mat("TT_Cast_Iron", "#242528", roughness=0.55, metallic=0.65),
        # 20: Glowing Neon Cyan / Green Ready LED
        make_solid_mat("TT_LED_Glow", "#22FF88", roughness=0.15, metallic=0.0, emission_strength=3.2),
        # 21: Soft Cotton Sport Towel Cream
        make_solid_mat("TT_Towel_Cream", "#F2EAD7", roughness=0.82, metallic=0.0),
    ]
    return mats


def attach_palette(mesh_obj, mats):
    mesh_obj.data.materials.clear()
    for m in mats:
        mesh_obj.data.materials.append(m)


def assign_vg(bm, verts, vg_index, weight=1.0):
    if vg_index is None or vg_index < 0:
        return
    dlayer = bm.verts.layers.deform.verify()
    for v in verts:
        if v.is_valid:
            v[dlayer][vg_index] = weight


def add_weighted_box(bm, center, size, mat_idx=0, vg_idx=0, rot_euler=None, chamfer=0.0):
    bm.verts.layers.deform.verify()
    existing_verts = set(bm.verts)
    existing_faces = set(bm.faces)
    res = bmesh.ops.create_cube(bm, size=1.0)
    cube_verts = res["verts"]

    sx, sy, sz = size
    scale_mat = Matrix.Diagonal((sx, sy, sz, 1.0))
    bmesh.ops.transform(bm, matrix=scale_mat, verts=cube_verts)

    eff_chamfer = min(chamfer, 0.32 * min(sx, sy, sz)) if chamfer > 0.0 else 0.0
    if eff_chamfer > 1e-4:
        new_edges = [e for e in bm.edges if all(ev not in existing_verts for ev in e.verts)]
        bmesh.ops.bevel(
            bm,
            geom=new_edges,
            offset=eff_chamfer,
            offset_type='OFFSET',
            segments=1,
            profile=0.5,
            affect='EDGES'
        )

    new_verts = [v for v in bm.verts if v.is_valid and v not in existing_verts]
    new_faces = [f for f in bm.faces if f.is_valid and f not in existing_faces]

    if rot_euler is not None:
        rmat = Euler(rot_euler, 'XYZ').to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=rmat, verts=new_verts)

    bmesh.ops.translate(bm, vec=Vector(center), verts=new_verts)
    for f in new_faces:
        f.material_index = mat_idx
        f.smooth = eff_chamfer > 1e-4
    assign_vg(bm, new_verts, vg_idx, 1.0)
    return new_verts, new_faces


def add_weighted_cylinder(bm, center, radius_bottom, radius_top, depth, segs=24, mat_idx=0, vg_idx=0, rot_euler=None, cap_ends=True):
    bm.verts.layers.deform.verify()
    existing_verts = set(bm.verts)
    existing_faces = set(bm.faces)
    bmesh.ops.create_cone(
        bm,
        cap_ends=cap_ends,
        cap_tris=False,
        segments=segs,
        radius1=radius_bottom,
        radius2=radius_top,
        depth=depth
    )
    new_verts = [v for v in bm.verts if v not in existing_verts]
    new_faces = [f for f in bm.faces if f not in existing_faces]

    if rot_euler is not None:
        rmat = Euler(rot_euler, 'XYZ').to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=rmat, verts=new_verts)

    bmesh.ops.translate(bm, vec=Vector(center), verts=new_verts)
    for f in new_faces:
        f.material_index = mat_idx
        f.smooth = True
    assign_vg(bm, new_verts, vg_idx, 1.0)
    return new_verts, new_faces


def add_weighted_sphere(bm, center, radius=0.020, subdivisions=2, mat_idx=16, vg_idx=0):
    """
    Builds a clean lathed UV sphere using bm.verts.new / bm.faces.new
    (avoiding bmesh.ops.create_icosphere which corrupts non-empty BMesh instances).
    """
    rings_n = 10
    profile = []
    for i in range(rings_n + 1):
        theta = -math.pi * 0.5 + math.pi * (i / rings_n)
        r = max(0.0005, radius * math.cos(theta))
        z = radius * math.sin(theta)
        profile.append((r, z))
    return add_lathe_profile(
        bm,
        profile,
        segs=16,
        mat_map=lambda _idx: mat_idx,
        vg_idx=vg_idx,
        center_offset=center,
    )


def add_lathe_profile(bm, profile_rz, segs=32, mat_map=None, vg_idx=0, center_offset=(0, 0, 0), rot_euler=None):
    """
    Revolves a 2D profile [(r, z), ...] around Z axis.
    mat_map: optional dict or callable mapping ring_idx -> material_index
    """
    bm.verts.layers.deform.verify()
    rings = []
    all_verts = []
    for r, z in profile_rz:
        ring = []
        r_safe = max(r, 0.0004)
        for s in range(segs):
            ang = 2.0 * math.pi * s / segs
            v = bm.verts.new((r_safe * math.cos(ang), r_safe * math.sin(ang), z))
            ring.append(v)
            all_verts.append(v)
        rings.append(ring)

    new_faces = []
    for i in range(len(rings) - 1):
        r0 = rings[i]
        r1 = rings[i + 1]
        m_idx = mat_map(i) if callable(mat_map) else (mat_map.get(i, 0) if isinstance(mat_map, dict) else (mat_map or 0))
        for s in range(segs):
            s_next = (s + 1) % segs
            f = bm.faces.new((r0[s], r0[s_next], r1[s_next], r1[s]))
            f.material_index = m_idx
            f.smooth = True
            new_faces.append(f)

    # Bottom and top caps
    f_bot = bm.faces.new(list(reversed(rings[0])))
    f_bot.material_index = mat_map(0) if callable(mat_map) else 0
    f_top = bm.faces.new(rings[-1])
    f_top.material_index = mat_map(len(rings) - 2) if callable(mat_map) else 0
    new_faces.extend([f_bot, f_top])

    if rot_euler is not None:
        rmat = Euler(rot_euler, 'XYZ').to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=rmat, verts=all_verts)

    if center_offset != (0, 0, 0):
        bmesh.ops.translate(bm, vec=Vector(center_offset), verts=all_verts)

    assign_vg(bm, all_verts, vg_idx, 1.0)
    return all_verts, new_faces


def create_armature_and_mesh(asset_name, bone_specs, mats):
    """
    Creates <asset_name>_Rig and <asset_name>_Mesh with vertex groups matching bone_specs.
    bone_specs: list of (bname, parent_name, head_xyz, tail_xyz, use_connect)
    """
    arm_data = bpy.data.armatures.new(f"{asset_name}_RigData")
    arm_obj = bpy.data.objects.new(f"{asset_name}_Rig", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')
    for bname, parent_name, head_xyz, tail_xyz, use_connect in bone_specs:
        eb = arm_data.edit_bones.new(bname)
        eb.head = Vector(head_xyz)
        eb.tail = Vector(tail_xyz)
        eb.inherit_scale = 'NONE'
        if parent_name and parent_name in arm_data.edit_bones:
            eb.parent = arm_data.edit_bones[parent_name]
            eb.use_connect = use_connect
    bpy.ops.object.mode_set(mode='OBJECT')

    mesh_data = bpy.data.meshes.new(f"{asset_name}_MeshData")
    mesh_obj = bpy.data.objects.new(f"{asset_name}_Mesh", mesh_data)
    bpy.context.collection.objects.link(mesh_obj)
    attach_palette(mesh_obj, mats)

    vg_map = {}
    for idx, (bname, _, _, _, _) in enumerate(bone_specs):
        mesh_obj.vertex_groups.new(name=bname)
        vg_map[bname] = idx

    mesh_obj.parent = arm_obj
    mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj

    for pb in arm_obj.pose.bones:
        pb.rotation_mode = 'XYZ'

    return arm_obj, mesh_obj, vg_map


def finalize_bmesh(bm, mesh_obj):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh_obj.data)
    bm.free()
    mesh_obj.data.update()


def add_socket_empty(name, loc_xyz, parent_obj, rot_deg=(0.0, 0.0, 0.0)):
    emp = bpy.data.objects.new(name, None)
    emp.empty_display_type = 'PLAIN_AXES'
    emp.empty_display_size = 0.04
    emp.location = Vector(loc_xyz)
    emp.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    emp.parent = parent_obj
    bpy.context.collection.objects.link(emp)
    return emp


def make_pose_helpers(arm_obj):
    arm_data = arm_obj.data
    bone_rest_mat = {b.name: b.matrix_local.to_3x3() for b in arm_data.bones}
    pb_map = arm_obj.pose.bones

    def reset_pose():
        for pb in pb_map:
            pb.rotation_mode = 'XYZ'
            pb.location = Vector((0.0, 0.0, 0.0))
            pb.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
            pb.scale = Vector((1.0, 1.0, 1.0))

    def set_world_rot(bname, pitch_deg=0.0, roll_deg=0.0, yaw_deg=0.0):
        b_rest = bone_rest_mat[bname]
        r_world = Euler(
            (math.radians(pitch_deg), math.radians(roll_deg), math.radians(yaw_deg)),
            'XYZ'
        ).to_matrix()
        pb_map[bname].rotation_euler = (b_rest.inverted() @ r_world @ b_rest).to_euler('XYZ')

    def set_world_loc(bname, dx=0.0, dy=0.0, dz=0.0):
        b_rest = bone_rest_mat[bname]
        pb_map[bname].location = b_rest.inverted() @ Vector((dx, dy, dz))

    def set_bone_scale(bname, sx=1.0, sy=1.0, sz=1.0):
        pb_map[bname].scale = Vector((sx, sy, sz))

    def key_all(frame, bone_names=None):
        names = bone_names if bone_names is not None else [b.name for b in arm_data.bones]
        for bname in names:
            pb = pb_map[bname]
            pb.keyframe_insert(data_path="location", frame=frame)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame)
            pb.keyframe_insert(data_path="scale", frame=frame)

    return reset_pose, set_world_rot, set_world_loc, set_bone_scale, key_all


def start_action(arm_obj, action_name):
    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()
    act = bpy.data.actions.new(name=action_name)
    act.use_fake_user = True
    arm_obj.animation_data.action = act
    if hasattr(arm_obj.animation_data, "action_slot") and len(act.slots) > 0:
        arm_obj.animation_data.action_slot = act.slots[0]
    return act


def push_actions_to_muted_nla(arm_obj, actions):
    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()
    for act in actions:
        track = arm_obj.animation_data.nla_tracks.new()
        track.name = act.name
        strip = track.strips.new(act.name, int(act.frame_range[0]), act)
        strip.name = act.name
        track.mute = True
    if actions:
        arm_obj.animation_data.action = actions[0]
        if hasattr(arm_obj.animation_data, "action_slot") and len(actions[0].slots) > 0:
            arm_obj.animation_data.action_slot = actions[0].slots[0]


def export_9_formats(asset_name, arm_obj, mesh_obj, sockets=None):
    os.makedirs(OUT_DIR_PRIMARY, exist_ok=True)
    os.makedirs(OUT_DIR_MIRROR, exist_ok=True)
    base_primary = f"{OUT_DIR_PRIMARY}/{asset_name}"

    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    mesh_obj.select_set(True)
    if sockets:
        for s in sockets:
            s.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    # 1. Animated exports in POSE mode
    arm_obj.data.pose_position = 'POSE'
    bpy.context.view_layer.update()

    bpy.ops.wm.save_as_mainfile(filepath=f"{base_primary}.blend")

    bpy.ops.export_scene.fbx(
        filepath=f"{base_primary}.fbx",
        use_selection=True,
        add_leaf_bones=False,
        bake_anim=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=True,
        bake_anim_force_startend_keying=True,
        bake_anim_simplify_factor=0.0,
    )

    bpy.ops.export_scene.gltf(
        filepath=f"{base_primary}.glb",
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_animation_mode='ACTIONS',
    )

    bpy.ops.export_scene.gltf(
        filepath=f"{base_primary}.gltf",
        export_format='GLTF_SEPARATE',
        use_selection=True,
        export_animations=True,
        export_animation_mode='ACTIONS',
    )

    bpy.ops.wm.alembic_export(
        filepath=f"{base_primary}.abc",
        selected=True,
        start=1,
        end=40,
    )

    # 2. Static geometry exports in REST mode
    arm_obj.data.pose_position = 'REST'
    bpy.context.view_layer.update()

    bpy.ops.wm.usd_export(
        filepath=f"{base_primary}.usdc",
        selected_objects_only=True,
    )
    bpy.ops.wm.obj_export(
        filepath=f"{base_primary}.obj",
        export_selected_objects=True,
    )
    bpy.ops.wm.ply_export(
        filepath=f"{base_primary}.ply",
        export_selected_objects=True,
    )
    bpy.ops.wm.stl_export(
        filepath=f"{base_primary}.stl",
        export_selected_objects=True,
    )

    # Restore POSE mode in saved .blend
    arm_obj.data.pose_position = 'POSE'
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=f"{base_primary}.blend")

    # Mirror all exported files to C:/3dassets/argon/table_tennis
    exts = [".blend", ".fbx", ".glb", ".gltf", ".bin", ".abc", ".usdc", ".obj", ".mtl", ".ply", ".stl"]
    for ext in exts:
        src = f"{base_primary}{ext}"
        if os.path.exists(src):
            shutil.copy2(src, f"{OUT_DIR_MIRROR}/{asset_name}{ext}")
    print(f"[EXPORTED 9 FORMATS] {asset_name}")
