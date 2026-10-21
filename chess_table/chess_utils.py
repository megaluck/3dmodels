import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Matrix, Euler

OUTPUT_DIR = "C:/argon/chess_table"
MIRROR_DIR = "C:/3dassets/argon/chess_table"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MIRROR_DIR, exist_ok=True)


def srgb_to_linear(c):
    def ch(x):
        return x / 12.92 if x <= 0.04045 else pow((x + 0.055) / 1.055, 2.4)
    return (ch(c[0]), ch(c[1]), ch(c[2]), c[3] if len(c) > 3 else 1.0)


def hex_to_srgb(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0, 1.0)


def hex_to_linear(h, alpha=1.0):
    s = hex_to_srgb(h)
    lin = srgb_to_linear(s)
    return (lin[0], lin[1], lin[2], alpha)


# Palette: name -> (base_hex, vein_hex, roughness, metallic, emission_strength, is_veined_marble)
CHESS_PALETTE = {
    "Chess_Marble_White_Veined": ("#F3F0EA", "#B8BDC4", 0.16, 0.00, 0.0, True),
    "Chess_Marble_Black_Veined": ("#1B1E24", "#7C828D", 0.14, 0.02, 0.0, True),
    "Chess_Piece_White_Marble":  ("#F7F3EB", "#D5CFC3", 0.15, 0.00, 0.0, True),
    "Chess_Piece_Black_Marble":  ("#22252C", "#5E6470", 0.14, 0.04, 0.0, True),
    "Chess_Gold_Brass":          ("#D9A84E", "#B3822C", 0.22, 0.88, 0.0, False),
    "Chess_Felt_Green":          ("#1F5C3A", "#16442A", 0.85, 0.00, 0.0, False),
    "Chess_Felt_Crimson":        ("#7A2228", "#58161B", 0.85, 0.00, 0.0, False),
    "Chess_Cushion_Cream_Sage":  ("#DCE2D5", "#B8C4AE", 0.68, 0.00, 0.0, False),
    "Chess_Cushion_Piping":      ("#4A5D4E", "#364539", 0.55, 0.00, 0.0, False),
    "Chess_Walnut_Wood":         ("#5A3824", "#3E2415", 0.34, 0.00, 0.0, False),
    "Chess_Clock_Dial_Cream":    ("#FAF4E4", "#E5D9BF", 0.28, 0.00, 0.0, False),
    "Chess_Clock_Flag_Red":      ("#D93829", "#A82418", 0.32, 0.00, 0.0, False),
    "Chess_Groove_Slate":        ("#343840", "#23262C", 0.45, 0.00, 0.0, False),
    "Chess_Highlight_Glow":      ("#F5C445", "#F5C445", 0.18, 0.40, 1.4, False),
}


def get_or_create_material(name):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    spec = CHESS_PALETTE.get(name, ("#CCCCCC", "#999999", 0.4, 0.0, 0.0, False))
    base_hex, vein_hex, rough, metal, emit_str, is_marble = spec
    base_lin = hex_to_linear(base_hex)
    vein_lin = hex_to_linear(vein_hex)

    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_lin
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if emit_str > 0.0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = base_lin
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emit_str

        # Add procedural marble veining in Blender shader nodes AND keep Base Color socket clean for glTF/FBX
        if is_marble:
            tex_coord = nt.nodes.new("ShaderNodeTexCoord")
            wave = nt.nodes.new("ShaderNodeTexWave")
            wave.wave_type = 'BANDS'
            wave.bands_direction = 'DIAGONAL'
            wave.wave_profile = 'SAW'
            wave.inputs["Scale"].default_value = 3.6
            wave.inputs["Distortion"].default_value = 7.5
            wave.inputs["Detail"].default_value = 4.0
            wave.inputs["Detail Scale"].default_value = 2.2

            ramp = nt.nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position = 0.0
            ramp.color_ramp.elements[0].color = base_lin
            ramp.color_ramp.elements[1].position = 0.82
            ramp.color_ramp.elements[1].color = base_lin
            el_vein = ramp.color_ramp.elements.new(0.92)
            el_vein.color = vein_lin

            nt.links.new(tex_coord.outputs["Object"], wave.inputs["Vector"])
            nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    mat.diffuse_color = base_lin
    return mat


def init_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 60
    return scene


def make_frame_from_dir_and_normal(direction, normal):
    z_ax = Vector(direction).normalized()
    n_hint = Vector(normal).normalized()
    x_ax = n_hint.cross(z_ax)
    if x_ax.length < 1e-4:
        fallback = Vector((1, 0, 0)) if abs(z_ax.x) < 0.9 else Vector((0, 1, 0))
        x_ax = fallback.cross(z_ax)
    x_ax.normalize()
    y_ax = z_ax.cross(x_ax).normalized()
    return Matrix((
        (x_ax.x, y_ax.x, z_ax.x),
        (x_ax.y, y_ax.y, z_ax.y),
        (x_ax.z, y_ax.z, z_ax.z),
    ))


def assign_vg(verts, deform_layer, vg_idx, weight=1.0):
    if vg_idx is not None:
        for v in verts:
            v[deform_layer][vg_idx] = weight


def add_weighted_box(bm, deform_layer, center, sx, sy, sz, mat_idx=0, vg_idx=0, rot_deg=(0.0, 0.0, 0.0), chamfer=0.0):
    existing_verts = set(bm.verts)
    existing_faces = set(bm.faces)
    res = bmesh.ops.create_cube(bm, size=1.0)
    verts = res["verts"]
    scale_mat = Matrix.Diagonal((sx, sy, sz, 1.0))
    bmesh.ops.transform(bm, matrix=scale_mat, verts=verts)

    if chamfer > 0.0:
        edges = [e for e in bm.edges if all(ev not in existing_verts for ev in e.verts)]
        bmesh.ops.bevel(bm, geom=edges, offset=chamfer, offset_type='OFFSET', segments=1, profile=0.5, affect='EDGES')

    new_verts = [v for v in bm.verts if v not in existing_verts]
    new_faces = [f for f in bm.faces if f not in existing_faces]

    rot_mat = Euler((math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2])), 'XYZ').to_matrix().to_4x4()
    trans_mat = Matrix.Translation(Vector(center))
    bmesh.ops.transform(bm, matrix=trans_mat @ rot_mat, verts=new_verts)
    assign_vg(new_verts, deform_layer, vg_idx, 1.0)
    for f in new_faces:
        f.material_index = mat_idx
    return new_verts


def add_lathe_profile(bm, deform_layer, profile_rz, sides=24, center=(0.0, 0.0, 0.0), rot_offset=0.0,
                      mat_idx=0, vg_idx=0, band_ranges=None, weight_fn=None):
    """
    Revolves a 2D (radius, z) profile around the Z axis.
    profile_rz: list of (r, z) from bottom to top. If r == 0 at start or end, caps cleanly.
    band_ranges: optional list of (z_min, z_max, mat_index) to assign specific rings to brass/felt materials.
    weight_fn: optional callable(z) -> dict of {vg_idx: weight} for multi-bone piece deformation.
    """
    cx, cy, cz = center
    rings = []
    ring_zs = []
    for r, z in profile_rz:
        ring = []
        eff_r = max(0.0004, r)
        for i in range(sides):
            ang = rot_offset + (2.0 * math.pi * i) / sides
            vx = cx + eff_r * math.cos(ang)
            vy = cy + eff_r * math.sin(ang)
            vz = cz + z
            v = bm.verts.new((vx, vy, vz))
            if weight_fn is not None:
                wmap = weight_fn(z)
                for b_i, w_val in wmap.items():
                    if w_val > 0.0:
                        v[deform_layer][b_i] = w_val
            elif vg_idx is not None:
                v[deform_layer][vg_idx] = 1.0
            ring.append(v)
        rings.append(ring)
        ring_zs.append(z)

    for k in range(len(rings) - 1):
        r0, r1 = rings[k], rings[k + 1]
        z_mid = 0.5 * (ring_zs[k] + ring_zs[k + 1])
        f_mat = mat_idx
        if band_ranges:
            for z0, z1, b_mat in band_ranges:
                if z0 <= z_mid <= z1:
                    f_mat = b_mat
                    break
        for i in range(sides):
            inext = (i + 1) % sides
            try:
                f = bm.faces.new((r0[i], r0[inext], r1[inext], r1[i]))
                f.material_index = f_mat
            except ValueError:
                pass

    # Bottom and top caps
    if len(rings) >= 2:
        try:
            f_bot = bm.faces.new(list(reversed(rings[0])))
            f_bot.material_index = band_ranges[0][2] if (band_ranges and band_ranges[0][0] <= ring_zs[0] + 1e-4) else mat_idx
        except ValueError:
            pass
        try:
            f_top = bm.faces.new(rings[-1])
            f_top.material_index = mat_idx
        except ValueError:
            pass

    return rings


def add_extruded_2d_outline_x(bm, deform_layer, poly_yz, thickness_x, center=(0.0, 0.0, 0.0),
                              mat_idx=0, vg_idx=0, weight_fn=None):
    """
    Extrudes a 2D polygon in (y_forward, z_up) along X by [-thickness_x/2, +thickness_x/2].
    Used for the Staunton Knight's sculpted horse head profile.
    """
    cx, cy, cz = center
    hx = 0.5 * thickness_x
    # Ensure counter-clockwise in (y, z)
    area = 0.0
    n = len(poly_yz)
    for i in range(n):
        y0, z0 = poly_yz[i]
        y1, z1 = poly_yz[(i + 1) % n]
        area += y0 * z1 - y1 * z0
    pts = list(reversed(poly_yz)) if area < 0 else list(poly_yz)

    left_verts = []
    right_verts = []
    for y, z in pts:
        vl = bm.verts.new((cx - hx, cy + y, cz + z))
        vr = bm.verts.new((cx + hx, cy + y, cz + z))
        for v in (vl, vr):
            if weight_fn is not None:
                for b_i, w_val in weight_fn(z).items():
                    if w_val > 0.0:
                        v[deform_layer][b_i] = w_val
            elif vg_idx is not None:
                v[deform_layer][vg_idx] = 1.0
        left_verts.append(vl)
        right_verts.append(vr)

    # Side rim quads
    for i in range(n):
        inext = (i + 1) % n
        try:
            f = bm.faces.new((left_verts[i], right_verts[i], right_verts[inext], left_verts[inext]))
            f.material_index = mat_idx
        except ValueError:
            pass

    # Cap faces and triangulate concave outline cleanly
    try:
        fl = bm.faces.new(list(reversed(left_verts)))
        fl.material_index = mat_idx
        fr = bm.faces.new(right_verts)
        fr.material_index = mat_idx
        bmesh.ops.triangulate(bm, faces=[fl, fr])
    except ValueError:
        pass

    return left_verts + right_verts


def create_rig(rig_name, bone_specs):
    arm_data = bpy.data.armatures.new(rig_name)
    arm_obj = bpy.data.objects.new(rig_name, arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    for bname, head, tail, parent_name in bone_specs:
        eb = arm_data.edit_bones.new(bname)
        eb.head = Vector(head)
        eb.tail = Vector(tail)
        eb.use_connect = False
        eb.inherit_scale = 'NONE'
        if parent_name and parent_name in arm_data.edit_bones:
            eb.parent = arm_data.edit_bones[parent_name]
    bpy.ops.object.mode_set(mode='OBJECT')
    arm_obj.animation_data_create()
    rest_mat = {b.name: b.matrix_local.to_3x3().copy() for b in arm_data.bones}
    return arm_obj, rest_mat


def finalize_rigged_mesh(mesh_name, bm, rig_obj, bone_specs, mat_names):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh_data = bpy.data.meshes.new(mesh_name)
    bm.to_mesh(mesh_data)
    bm.free()

    for p in mesh_data.polygons:
        p.use_smooth = False

    mesh_obj = bpy.data.objects.new(mesh_name, mesh_data)
    bpy.context.collection.objects.link(mesh_obj)

    for mname in mat_names:
        mesh_obj.data.materials.append(get_or_create_material(mname))

    for bname, _, _, _ in bone_specs:
        if bname not in mesh_obj.vertex_groups:
            mesh_obj.vertex_groups.new(name=bname)

    mesh_obj.parent = rig_obj
    mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = rig_obj
    return mesh_obj


def make_empty(name, loc, rot_deg=(0.0, 0.0, 0.0), parent=None, bone_parent=None, size=0.04):
    emp = bpy.data.objects.new(name, None)
    emp.empty_display_type = 'PLAIN_AXES'
    emp.empty_display_size = size
    bpy.context.collection.objects.link(emp)
    if parent is not None and bone_parent is not None:
        emp.parent = parent
        emp.parent_type = 'BONE'
        emp.parent_bone = bone_parent
        bone = parent.data.bones[bone_parent]
        tail_world = parent.matrix_world @ bone.tail_local
        b_mat = bone.matrix_local.to_3x3()
        emp.location = b_mat.inverted() @ (Vector(loc) - tail_world)
        r_world = Euler((math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2])), 'XYZ').to_matrix()
        emp.rotation_euler = (b_mat.inverted() @ r_world).to_euler('XYZ')
    elif parent is not None:
        emp.parent = parent
        emp.location = Vector(loc)
        emp.rotation_euler = Euler((math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2])), 'XYZ')
    else:
        emp.location = Vector(loc)
        emp.rotation_euler = Euler((math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2])), 'XYZ')
    return emp


def make_pose_helpers(rig_obj, rest_mat):
    pb = rig_obj.pose.bones
    for b in pb:
        b.rotation_mode = 'XYZ'

    def set_world_rot(bname, pitch_deg=0.0, roll_deg=0.0, yaw_deg=0.0):
        b_rest = rest_mat[bname]
        r_world = Euler((math.radians(pitch_deg), math.radians(roll_deg), math.radians(yaw_deg)), 'XYZ').to_matrix()
        pb[bname].rotation_euler = (b_rest.inverted() @ r_world @ b_rest).to_euler('XYZ')

    def set_world_loc(bname, dx=0.0, dy=0.0, dz=0.0):
        b_rest = rest_mat[bname]
        pb[bname].location = b_rest.inverted() @ Vector((dx, dy, dz))

    def key_frame(frame, rot_map=None, loc_map=None, scale_map=None):
        bpy.context.scene.frame_set(frame)
        for b in pb:
            b.rotation_euler = (0.0, 0.0, 0.0)
            b.location = (0.0, 0.0, 0.0)
            b.scale = (1.0, 1.0, 1.0)
        if rot_map:
            for bname, (rx, ry, rz) in rot_map.items():
                set_world_rot(bname, rx, ry, rz)
        if loc_map:
            for bname, (dx, dy, dz) in loc_map.items():
                set_world_loc(bname, dx, dy, dz)
        if scale_map:
            for bname, (sx, sy, sz) in scale_map.items():
                pb[bname].scale = (sx, sy, sz)
        for b in pb:
            b.keyframe_insert(data_path="location", frame=frame)
            b.keyframe_insert(data_path="rotation_euler", frame=frame)
            b.keyframe_insert(data_path="scale", frame=frame)

    return set_world_rot, set_world_loc, key_frame


def save_and_export_chess(base_name, animated=True):
    bpy.ops.object.select_all(action='SELECT')
    rigs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    for r in rigs:
        r.data.pose_position = 'POSE' if animated else 'REST'

    base_path = f"{OUTPUT_DIR}/{base_name}"
    bpy.ops.wm.save_as_mainfile(filepath=f"{base_path}.blend")

    bpy.ops.export_scene.fbx(
        filepath=f"{base_path}.fbx",
        use_selection=True,
        add_leaf_bones=False,
        bake_anim=animated,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=animated,
        bake_anim_force_startend_keying=True,
        bake_anim_simplify_factor=0.0,
    )
    bpy.ops.export_scene.gltf(
        filepath=f"{base_path}.glb",
        export_format='GLB',
        use_selection=True,
        export_animations=animated,
        export_animation_mode='ACTIONS',
    )
    bpy.ops.export_scene.gltf(
        filepath=f"{base_path}.gltf",
        export_format='GLTF_SEPARATE',
        use_selection=True,
        export_animations=animated,
        export_animation_mode='ACTIONS',
    )
    bpy.ops.wm.alembic_export(
        filepath=f"{base_path}.abc",
        selected=True,
        start=1,
        end=60 if animated else 1,
    )

    for r in rigs:
        r.data.pose_position = 'REST'
    bpy.context.view_layer.update()

    bpy.ops.wm.obj_export(filepath=f"{base_path}.obj", export_selected_objects=True)
    bpy.ops.wm.stl_export(filepath=f"{base_path}.stl", export_selected_objects=True)
    bpy.ops.wm.ply_export(filepath=f"{base_path}.ply", export_selected_objects=True)
    bpy.ops.wm.usd_export(filepath=f"{base_path}.usdc", selected_objects_only=True)

    for r in rigs:
        r.data.pose_position = 'POSE'

    for ext in [".blend", ".fbx", ".glb", ".gltf", ".bin", ".abc", ".obj", ".mtl", ".stl", ".ply", ".usdc"]:
        src = f"{base_path}{ext}"
        if os.path.exists(src):
            shutil.copy2(src, f"{MIRROR_DIR}/{base_name}{ext}")
    print(f"[EXPORTED] {base_name} across all 9 formats -> {OUTPUT_DIR} & {MIRROR_DIR}")
