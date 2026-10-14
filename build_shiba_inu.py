import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

# ==============================================================================
# 1. CLEAN SCENE & SETUP COLLECTION (SHIBA INU ONLY - NO PROPS!)
# ==============================================================================
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)
for arm in list(bpy.data.armatures):
    bpy.data.armatures.remove(arm)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)
for mat in list(bpy.data.materials):
    bpy.data.materials.remove(mat)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)

scene = bpy.context.scene
scene.render.fps = 24

shiba_col = bpy.data.collections.new("Cozy_Shiba")
scene.collection.children.link(shiba_col)

# ==============================================================================
# 2. SCENE-LINEAR HAND-PAINTED / FACETED LOW-POLY SHIBA INU MATERIALS
#    (Following Workspace Rule #2: Always convert sRGB to Scene-Linear RGB!)
# ==============================================================================
def srgb_to_linear(c):
    def ch(x):
        return x / 12.92 if x <= 0.04045 else pow((x + 0.055) / 1.055, 2.4)
    return (ch(c[0]), ch(c[1]), ch(c[2]), c[3] if len(c) > 3 else 1.0)

def make_shiba_mat(name, col_dark_srgb, col_light_srgb, roughness=0.52, specular=0.25, noise_scale=8.0, bump_str=0.04):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    c_dark = srgb_to_linear(col_dark_srgb)
    c_light = srgb_to_linear(col_light_srgb)

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (280, 0)
    bsdf.inputs["Base Color"].default_value = c_light
    bsdf.inputs["Roughness"].default_value = roughness
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = specular

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-520, 0)

    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-300, 80)
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = 0.55

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (-40, 120)
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = c_dark
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = c_light

    links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    if bump_str > 0.0:
        bump = nodes.new("ShaderNodeBump")
        bump.location = (40, -140)
        bump.inputs["Strength"].default_value = bump_str
        bump.inputs["Distance"].default_value = 0.008
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    mat.diffuse_color = c_light
    return mat

# 11 Palette Slots matching the reference faceted Shiba Inu:
# 0: Ginger Orange (Main Coat: head crown, back, upper flanks, legs, outer tail)
# 1: Deep Amber-Rust (Shaded facets: neck sides, shoulder crease, outer hips, ear backs)
# 2: Golden Apricot (Bright sunlit facets: forehead, upper cheeks, shoulder tops, tail crest)
# 3: Cream White (Urajiro markings: cheeks, muzzle sides, eyebrows, chest shield, belly, paw tips, inner tail)
# 4: Warm Cream-Beige (Soft shaded urajiro under-chin, lower chest facets, inner hind legs)
# 5: Dark Espresso-Rose (Inner ear cavity triangles)
# 6: Glossy Charcoal-Black (Nose tip & smiling mouth line / lips)
# 7: Glossy Dark Ebony (Almond eyes)
# 8: Pure Bright White (Eye catchlight sparkles & teeth)
# 9: Rosy Coral Pink (Happy panting tongue)
# 10: Dark Slate-Brown (Paw pads)
palette_defs = [
    ("Mat_Shiba_Ginger",       (0.82, 0.39, 0.12), (0.94, 0.51, 0.18), 0.50, 0.25, 7.0, 0.03), # 0
    ("Mat_Shiba_AmberShadow",  (0.65, 0.27, 0.09), (0.78, 0.34, 0.12), 0.54, 0.22, 6.0, 0.03), # 1
    ("Mat_Shiba_GoldenLight",  (0.92, 0.53, 0.20), (0.99, 0.66, 0.28), 0.48, 0.28, 7.0, 0.02), # 2
    ("Mat_Shiba_CreamWhite",   (0.91, 0.86, 0.78), (0.99, 0.96, 0.91), 0.46, 0.25, 6.0, 0.02), # 3
    ("Mat_Shiba_CreamShadow",  (0.75, 0.67, 0.59), (0.86, 0.79, 0.71), 0.52, 0.22, 6.0, 0.02), # 4
    ("Mat_Shiba_EarInner",     (0.26, 0.12, 0.13), (0.38, 0.18, 0.18), 0.58, 0.18, 8.0, 0.02), # 5
    ("Mat_Shiba_NoseBlack",    (0.05, 0.05, 0.07), (0.11, 0.12, 0.15), 0.22, 0.55, 12.0, 0.01),# 6
    ("Mat_Shiba_EyeDark",      (0.03, 0.03, 0.05), (0.07, 0.07, 0.10), 0.10, 0.80, 10.0, 0.00),# 7
    ("Mat_Shiba_EyeSpec",      (0.96, 0.98, 1.00), (1.00, 1.00, 1.00), 0.05, 0.90, 5.0,  0.00),# 8
    ("Mat_Shiba_TonguePink",   (0.82, 0.32, 0.38), (0.94, 0.46, 0.50), 0.35, 0.45, 9.0,  0.02),# 9
    ("Mat_Shiba_PawPad",       (0.18, 0.14, 0.13), (0.25, 0.20, 0.18), 0.65, 0.15, 10.0, 0.03),# 10
]
materials = [make_shiba_mat(*p) for p in palette_defs]

# ==============================================================================
# 3. BUILD 34-BONE EXPRESSIVE QUADRUPED + FACIAL ARMATURE (Shiba_Rig)
#    Rest pose is a natural standing posture so sitting, standing, trotting,
#    galloping, rolling over, and play-bowing all deform cleanly!
# ==============================================================================
arm_data = bpy.data.armatures.new("Shiba_Rig_Data")
arm_obj = bpy.data.objects.new("Shiba_Rig", arm_data)
shiba_col.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

eb = arm_data.edit_bones
def make_bone(name, head, tail, parent_name=None, connect=False):
    b = eb.new(name)
    b.head = Vector(head)
    b.tail = Vector(tail)
    if parent_name and parent_name in eb:
        b.parent = eb[parent_name]
        b.use_connect = connect
    return b

# Core Spine & Torso (Forward = -Y, Up = +Z)
make_bone("Root",       (0.0,  0.00, 0.00), (0.0,  0.00, 0.15))
make_bone("Hips",       (0.0,  0.16, 0.44), (0.0,  0.28, 0.46), "Root")
make_bone("Spine",      (0.0,  0.16, 0.44), (0.0, -0.02, 0.46), "Hips")
make_bone("Chest",      (0.0, -0.02, 0.46), (0.0, -0.20, 0.49), "Spine", connect=True)
make_bone("Neck",       (0.0, -0.18, 0.49), (0.0, -0.25, 0.62), "Chest")
make_bone("Head",       (0.0, -0.25, 0.62), (0.0, -0.32, 0.80), "Neck", connect=True)

# Expressive Facial Bones + VR Fetch Mouth Attachment Socket
make_bone("Snout",        (0.0, -0.33,  0.68),  (0.0, -0.49,  0.67),  "Head")
make_bone("Jaw",          (0.0, -0.31,  0.63),  (0.0, -0.45,  0.61),  "Head")
make_bone("Tongue",       (0.0, -0.34,  0.63),  (0.0, -0.46,  0.62),  "Jaw")
make_bone("Mouth_Socket", (0.0, -0.425, 0.648), (0.0, -0.425, 0.708), "Head")

for side, sx in [("L", 1.0), ("R", -1.0)]:
    make_bone(f"Ear.{side}",     (sx * 0.095, -0.22, 0.78), (sx * 0.135, -0.21, 0.94), "Head")
    make_bone(f"Brow.{side}",    (sx * 0.052, -0.37, 0.74), (sx * 0.082, -0.38, 0.76), "Head")
    make_bone(f"Eyelid.{side}",  (sx * 0.068, -0.36, 0.71), (sx * 0.068, -0.39, 0.71), "Head")

# Curled Fluffy Shiba Donut Tail (3 bones curling up and over the back)
make_bone("Tail_Base",  (0.0,  0.27, 0.47), (0.0,  0.37, 0.56), "Hips")
make_bone("Tail_Mid",   (0.0,  0.37, 0.56), (0.0,  0.36, 0.68), "Tail_Base", connect=True)
make_bone("Tail_Tip",   (0.0,  0.36, 0.68), (0.0,  0.25, 0.65), "Tail_Mid",  connect=True)

# 4 Articulated Legs (Front L/R and Back L/R)
for side, sx in [("L", 1.0), ("R", -1.0)]:
    # Front Leg
    make_bone(f"Leg_Front_Upper.{side}", (sx * 0.095, -0.17, 0.43), (sx * 0.098, -0.15, 0.24), "Chest")
    make_bone(f"Leg_Front_Lower.{side}", (sx * 0.098, -0.15, 0.24), (sx * 0.098, -0.17, 0.06), f"Leg_Front_Upper.{side}", connect=True)
    make_bone(f"Paw_Front.{side}",       (sx * 0.098, -0.17, 0.06), (sx * 0.098, -0.25, 0.01), f"Leg_Front_Lower.{side}", connect=True)

    # Back Leg
    make_bone(f"Leg_Back_Upper.{side}",  (sx * 0.100,  0.18, 0.43), (sx * 0.105,  0.23, 0.24), "Hips")
    make_bone(f"Leg_Back_Lower.{side}",  (sx * 0.105,  0.23, 0.24), (sx * 0.105,  0.19, 0.06), f"Leg_Back_Upper.{side}", connect=True)
    make_bone(f"Paw_Back.{side}",        (sx * 0.105,  0.19, 0.06), (sx * 0.105,  0.11, 0.01), f"Leg_Back_Lower.{side}", connect=True)

bpy.ops.object.mode_set(mode='OBJECT')
for pb in arm_obj.pose.bones:
    pb.rotation_mode = 'XYZ'

# ==============================================================================
# 4. PROCEDURAL LOW-POLY FACETED ("ORIGAMI / PAPERCRAFT") SHIBA INU MESH
#    - Flat-shaded (`smooth=False`) with triangulated/faceted low-poly rings
#    - Per-face Urajiro color-blocking matching the reference screenshot!
# ==============================================================================
mesh_data = bpy.data.meshes.new("Shiba_Mesh_Data")
mesh_obj = bpy.data.objects.new("Shiba_Mesh", mesh_data)
shiba_col.objects.link(mesh_obj)

for mat in materials:
    mesh_data.materials.append(mat)

all_bone_names = [b.name for b in arm_data.bones]
vgroup_Index = {}
for bname in all_bone_names:
    vg = mesh_obj.vertex_groups.new(name=bname)
    vgroup_Index[bname] = vg.index

bm = bmesh.new()
deform_layer = bm.verts.layers.deform.verify()

def assign_weights(verts, weights_or_fn):
    if not weights_or_fn:
        return
    for v in verts:
        wmap = weights_or_fn(v.co, v) if callable(weights_or_fn) else weights_or_fn
        dvert = v[deform_layer]
        for bname, w in wmap.items():
            if bname in vgroup_Index and w > 0.001:
                dvert[vgroup_Index[bname]] = float(w)

def add_faceted_loft(rings_spec, up_hint=(0, 0, 1), segs=12, mat_fn=None, default_mat=0, weights=None, cap_start=True, cap_end=True, twist_half_step=True):
    """
    Builds a crisp, origami-style faceted low-poly tube by alternating a half-segment
    angular offset between adjacent rings and triangulating quads into diamond facets!
    `rings_spec`: list of (center_xyz, rx, ry) or (center_xyz, rx, ry, z_squash_bottom)
    """
    pts = [Vector(r[0]) for r in rings_spec]
    n = len(pts)
    hint = Vector(up_hint).normalized()
    all_verts = []
    rings = []

    for i, r in enumerate(rings_spec):
        p = pts[i]
        rx, ry = r[1], r[2]
        if i == 0:
            tang = pts[1] - pts[0]
        elif i == n - 1:
            tang = pts[-1] - pts[-2]
        else:
            tang = pts[i + 1] - pts[i - 1]
        z_ax = tang.normalized()
        x_ax = hint.cross(z_ax)
        if x_ax.length < 1e-4:
            x_ax = Vector((1, 0, 0)).cross(z_ax)
        x_ax.normalize()
        y_ax = z_ax.cross(x_ax).normalized()
        rot = Matrix((
            (x_ax.x, y_ax.x, z_ax.x),
            (x_ax.y, y_ax.y, z_ax.y),
            (x_ax.z, y_ax.z, z_ax.z),
        ))

        ring_v = []
        ang_offset = (0.5 / segs) * 2.0 * math.pi if (twist_half_step and (i % 2 == 1)) else 0.0
        for s in range(segs):
            ang = (s / segs) * 2.0 * math.pi + ang_offset
            ca, sa = math.cos(ang), math.sin(ang)
            local_p = Vector((ca * rx, sa * ry, 0.0))
            world_p = p + (rot @ local_p)
            v = bm.verts.new(world_p)
            ring_v.append(v)
            all_verts.append(v)
        rings.append(ring_v)

    for r_idx in range(n - 1):
        r0 = rings[r_idx]
        r1 = rings[r_idx + 1]
        for s in range(segs):
            ns = (s + 1) % segs
            if twist_half_step:
                # 2 crisp origami triangles per segment
                if r_idx % 2 == 0:
                    f1 = bm.faces.new((r0[s], r0[ns], r1[s]))
                    f2 = bm.faces.new((r0[ns], r1[ns], r1[s]))
                else:
                    f1 = bm.faces.new((r0[s], r0[ns], r1[ns]))
                    f2 = bm.faces.new((r0[s], r1[ns], r1[s]))
                for f in (f1, f2):
                    f.smooth = False
                    fc = f.calc_center_median()
                    fn = f.normal
                    f.material_index = mat_fn(fc, fn, r_idx) if mat_fn else default_mat
            else:
                f = bm.faces.new((r0[s], r0[ns], r1[ns], r1[s]))
                f.smooth = False
                fc = f.calc_center_median()
                fn = f.normal
                f.material_index = mat_fn(fc, fn, r_idx) if mat_fn else default_mat

    if cap_start and rings:
        c0 = sum((v.co for v in rings[0]), Vector((0, 0, 0))) / segs
        vc0 = bm.verts.new(c0)
        all_verts.append(vc0)
        for s in range(segs):
            ns = (s + 1) % segs
            f = bm.faces.new((rings[0][ns], rings[0][s], vc0))
            f.smooth = False
            fc = f.calc_center_median()
            f.material_index = mat_fn(fc, f.normal, 0) if mat_fn else default_mat

    if cap_end and rings:
        c1 = sum((v.co for v in rings[-1]), Vector((0, 0, 0))) / segs
        vc1 = bm.verts.new(c1)
        all_verts.append(vc1)
        for s in range(segs):
            ns = (s + 1) % segs
            f = bm.faces.new((rings[-1][s], rings[-1][ns], vc1))
            f.smooth = False
            fc = f.calc_center_median()
            f.material_index = mat_fn(fc, f.normal, n - 1) if mat_fn else default_mat

    assign_weights(all_verts, weights)
    return all_verts

# ------------------------------------------------------------------------------
# A. TORSO, CHEST & NECK (WITH URAJIRO CREAM-WHITE CHEST SHIELD & BELLY!)
# ------------------------------------------------------------------------------
def torso_weights(co, _v):
    if co.z > 0.56 and co.y < -0.14:
        t = min(1.0, (co.z - 0.56) / 0.10)
        return {"Neck": 0.65 + 0.25 * t, "Chest": 0.35 - 0.25 * t}
    elif co.y < -0.06:
        return {"Chest": 0.80, "Spine": 0.20}
    elif co.y < 0.10:
        return {"Spine": 0.75, "Chest": 0.15, "Hips": 0.10}
    else:
        return {"Hips": 0.80, "Spine": 0.20}

def torso_mat_fn(fc, fn, r_idx):
    # Urajiro white/cream throat, front chest shield, and underbelly
    if fc.y < -0.18 and fc.z < 0.63 and abs(fc.x) < 0.115:
        return 3 if fc.z > 0.44 else 4
    if fc.z < 0.37 and abs(fc.x) < 0.105:
        return 4
    # Bright sunlit golden top back / collar facets
    if fn.z > 0.55 and fc.z > 0.48:
        return 2
    # Deep amber shaded lower flank facets
    if abs(fc.x) > 0.125 and fc.z < 0.45:
        return 1
    return 0

torso_rings = [
    ((0.0,  0.29, 0.46), 0.115, 0.110), # Rear rump
    ((0.0,  0.19, 0.45), 0.148, 0.145), # Hips
    ((0.0,  0.07, 0.44), 0.158, 0.155), # Mid-back / waist
    ((0.0, -0.06, 0.45), 0.168, 0.168), # Ribcage
    ((0.0, -0.17, 0.48), 0.165, 0.165), # Broad proud Shiba chest
    ((0.0, -0.22, 0.55), 0.145, 0.142), # Lower neck ruff
    ((0.0, -0.24, 0.62), 0.128, 0.125), # Mid neck
    ((0.0, -0.25, 0.67), 0.110, 0.110), # Upper neck base
]
add_faceted_loft(torso_rings, up_hint=(0, 0, 1), segs=12, mat_fn=torso_mat_fn, weights=torso_weights)

# ------------------------------------------------------------------------------
# B. EXPRESSIVE FACETED SHIBA HEAD, CHEEKS, SNOUT, JAW & SMILING MOUTH
#    In the reference, the Shiba has wide, fluffy hexagonal cheeks (cream white on
#    the lower half, ginger-gold on the upper half), white pip eyebrows, and a cute smile!
# ------------------------------------------------------------------------------
def head_mat_fn(fc, fn, r_idx):
    # White "urajiro" cheeks & under-jaw
    if fc.z < 0.705 and (fc.y < -0.26 or abs(fc.x) > 0.08):
        return 3 if fc.z > 0.655 else 4
    # Forehead & crown golden-apricot highlight facets
    if fc.z > 0.775 and abs(fc.x) < 0.095 and fc.y < -0.22:
        return 2
    # Back of skull shaded amber
    if fc.y > -0.20:
        return 1
    return 0

head_rings = [
    ((0.0, -0.17, 0.69), 0.115, 0.105), # Back of head / nape
    ((0.0, -0.22, 0.71), 0.152, 0.132), # Wide fluffy rear cheek ruff
    ((0.0, -0.28, 0.71), 0.165, 0.138), # Widest iconic Shiba cheek diamond!
    ((0.0, -0.33, 0.70), 0.135, 0.116), # Front face / eye plane
    ((0.0, -0.375,0.68), 0.085, 0.075), # Upper snout bridge
]
add_faceted_loft(head_rings, up_hint=(0, 0, 1), segs=12, mat_fn=head_mat_fn, weights={"Head": 0.9, "Neck": 0.1})

# Upper Muzzle / Snout (Compact cute Shiba muzzle: Ginger top bridge + Cream-White sides)
def snout_mat_fn(fc, fn, r_idx):
    if fn.z > 0.45 and abs(fc.x) < 0.042 and fc.y > -0.435:
        return 2 if fc.y > -0.39 else 0
    return 3 if fc.z > 0.655 else 4

snout_rings = [
    ((0.0, -0.335, 0.676), 0.082, 0.056),
    ((0.0, -0.388, 0.674), 0.064, 0.046),
    ((0.0, -0.432, 0.670), 0.046, 0.036),
    ((0.0, -0.456, 0.667), 0.025, 0.022),
]
add_faceted_loft(snout_rings, up_hint=(0, 0, 1), segs=10, mat_fn=snout_mat_fn, weights={"Snout": 0.85, "Head": 0.15})

# Glossy Faceted Black Nose Tip (Mat 6) + Philtrum Line down to Upper Lip
nose_rings = [
    ((0.0, -0.440, 0.678), 0.028, 0.022),
    ((0.0, -0.464, 0.680), 0.032, 0.025),
    ((0.0, -0.476, 0.675), 0.018, 0.015),
]
add_faceted_loft(nose_rings, up_hint=(0, 0, 1), segs=8, default_mat=6, weights={"Snout": 1.0})

philtrum_rings = [
    ((0.0, -0.462, 0.668), 0.005, 0.005),
    ((0.0, -0.458, 0.650), 0.004, 0.004),
]
add_faceted_loft(philtrum_rings, up_hint=(0, 1, 0), segs=4, default_mat=6, weights={"Snout": 1.0}, twist_half_step=False)

# Articulated Lower Jaw / Chin (Cream-White outside, dark lip rim)
def jaw_mat_fn(fc, fn, r_idx):
    if fn.z > 0.45 and fc.y < -0.35:
        return 6 # Dark inner mouth / lip line
    return 4 if fc.z < 0.635 else 3

jaw_rings = [
    ((0.0, -0.305, 0.636), 0.075, 0.032),
    ((0.0, -0.355, 0.634), 0.062, 0.028),
    ((0.0, -0.405, 0.634), 0.046, 0.024),
    ((0.0, -0.438, 0.638), 0.026, 0.016),
]
add_faceted_loft(jaw_rings, up_hint=(0, 0, 1), segs=8, mat_fn=jaw_mat_fn, weights={"Jaw": 0.9, "Head": 0.1})

# Happy Pink Tongue (nested inside Jaw so when Jaw opens for panting/barking/belly-rubs, it's visible!)
tongue_rings = [
    ((0.0, -0.335, 0.642), 0.024, 0.008),
    ((0.0, -0.378, 0.642), 0.026, 0.009),
    ((0.0, -0.415, 0.640), 0.022, 0.007),
    ((0.0, -0.434, 0.637), 0.012, 0.004),
]
add_faceted_loft(tongue_rings, up_hint=(0, 0, 1), segs=8, default_mat=9, weights={"Tongue": 1.0}, twist_half_step=False)

# Iconic Smiling Shiba Mouth Corners (Clean, sleek dark smile curve hugging the upper muzzle & cheek!)
for side, sx in [("L", 1.0), ("R", -1.0)]:
    smile_path = [
        ((0.0,        -0.456, 0.650), 0.0045, 0.0045),
        ((sx * 0.032, -0.438, 0.647), 0.0055, 0.0055),
        ((sx * 0.056, -0.406, 0.648), 0.0060, 0.0055),
        ((sx * 0.074, -0.378, 0.658), 0.0050, 0.0045),
        ((sx * 0.084, -0.358, 0.670), 0.0030, 0.0030),
    ]
    add_faceted_loft(smile_path, up_hint=(0, 0, 1), segs=6, default_mat=6, weights={"Snout": 0.70, "Head": 0.30}, twist_half_step=False)

# ------------------------------------------------------------------------------
# C. EXPRESSIVE EYES, EYELIDS, WHITE SHIBA "PIP" EYEBROWS & POINTED TRIANGULAR EARS
#    Positioned cleanly in front of the face facets (`y = -0.375..-0.402`) so
#    they sit completely unobstructed on the surface of the face!
# ------------------------------------------------------------------------------
for side, sx in [("L", 1.0), ("R", -1.0)]:
    # Dark Ebony Almond Eye (protruding cleanly in front of the head surface)
    eye_rings = [
        ((sx * 0.040, -0.390, 0.716), 0.006, 0.008), # Inner tear duct corner
        ((sx * 0.052, -0.391, 0.721), 0.017, 0.020), # Inner-mid eye
        ((sx * 0.065, -0.385, 0.722), 0.019, 0.021), # Outer-mid eye
        ((sx * 0.077, -0.373, 0.719), 0.007, 0.008), # Outer almond eye corner
    ]
    add_faceted_loft(eye_rings, up_hint=(0, 0, 1), segs=8, default_mat=7, weights={"Head": 1.0}, twist_half_step=False)

    # Bright White Eye Catchlight Sparkle (Sits right on the front corneal surface!)
    spec_rings = [
        ((sx * 0.052, -0.405, 0.727), 0.0055, 0.0055),
        ((sx * 0.058, -0.404, 0.728), 0.0065, 0.0065),
        ((sx * 0.062, -0.401, 0.726), 0.0035, 0.0035),
    ]
    add_faceted_loft(spec_rings, up_hint=(0, 0, 1), segs=6, default_mat=8, weights={"Head": 1.0}, twist_half_step=False)

    # Expressive Upper Eyelid / Lash Line (Rigged to `Eyelid.L/R` so it closes/squints when petted!)
    lid_rings = [
        ((sx * 0.038, -0.390, 0.722), 0.006, 0.005),
        ((sx * 0.058, -0.394, 0.735), 0.014, 0.007),
        ((sx * 0.078, -0.375, 0.724), 0.006, 0.005),
    ]
    add_faceted_loft(lid_rings, up_hint=(0, 0, 1), segs=6, default_mat=6, weights={f"Eyelid.{side}": 0.85, "Head": 0.15}, twist_half_step=False)

    # Iconic Shiba Cream-White "Pip" Eyebrow Spot (Rigged to `Brow.L/R`, bold diamond/oval on the brow!)
    brow_rings = [
        ((sx * 0.032, -0.376, 0.748), 0.008, 0.010),
        ((sx * 0.044, -0.382, 0.758), 0.018, 0.018),
        ((sx * 0.058, -0.375, 0.756), 0.016, 0.016),
        ((sx * 0.068, -0.364, 0.748), 0.006, 0.007),
    ]
    add_faceted_loft(brow_rings, up_hint=(0, 0, 1), segs=6, default_mat=3, weights={f"Brow.{side}": 0.85, "Head": 0.15}, twist_half_step=False)

    # Pointed Faceted Triangular Shiba Ear (Ginger outer shell + Recessed Dark Espresso-Rose inner ear hollow)
    def make_ear_mat(s_sign=sx):
        def _emat(fc, fn, r_idx):
            if fn.y < -0.15 and fc.z < 0.90:
                return 0 # Outer ginger rim
            if fn.y > 0.2:
                return 1 # Shaded amber ear back
            return 2 if fc.z > 0.88 else 0
        return _emat

    ear_rings = [
        ((sx * 0.088, -0.220, 0.765), 0.048, 0.034),
        ((sx * 0.106, -0.215, 0.822), 0.043, 0.028),
        ((sx * 0.120, -0.212, 0.878), 0.029, 0.020),
        ((sx * 0.130, -0.210, 0.925), 0.015, 0.011),
        ((sx * 0.135, -0.208, 0.950), 0.004, 0.004),
    ]
    add_faceted_loft(
        ear_rings,
        up_hint=(0, -1, 0),
        segs=6,
        mat_fn=make_ear_mat(sx),
        weights={f"Ear.{side}": 0.90, "Head": 0.10},
        twist_half_step=True,
    )

    # Distinct Dark Inner Ear Cavity Triangle on the Front of the Ear (Mat 5)
    ear_inner_rings = [
        ((sx * 0.092, -0.244, 0.780), 0.026, 0.012),
        ((sx * 0.106, -0.236, 0.828), 0.024, 0.011),
        ((sx * 0.118, -0.228, 0.875), 0.015, 0.008),
        ((sx * 0.126, -0.220, 0.910), 0.004, 0.004),
    ]
    add_faceted_loft(
        ear_inner_rings,
        up_hint=(0, -1, 0),
        segs=5,
        default_mat=5,
        weights={f"Ear.{side}": 0.90, "Head": 0.10},
        twist_half_step=False,
    )

# ------------------------------------------------------------------------------
# D. FLUFFY CURLED SHIBA DONUT TAIL (GINGER OUTER + CREAM-WHITE INNER/TIP)
# ------------------------------------------------------------------------------
def tail_weights(co, _v):
    if co.z < 0.54 and co.y < 0.36:
        return {"Tail_Base": 0.80, "Hips": 0.20}
    elif co.z < 0.64 and co.y >= 0.33:
        return {"Tail_Mid": 0.80, "Tail_Base": 0.20}
    else:
        return {"Tail_Tip": 0.85, "Tail_Mid": 0.15}

def tail_mat_fn(fc, fn, r_idx):
    if r_idx >= 5 or (fn.z > 0.5 and fc.z > 0.64):
        return 3 # Cream-white tail tip / inner curl
    if fn.z > 0.25:
        return 2 # Golden sunlit top of tail curl
    return 0

tail_rings = [
    ((0.0, 0.26, 0.46), 0.046, 0.046),
    ((0.0, 0.34, 0.51), 0.062, 0.058),
    ((0.0, 0.39, 0.58), 0.070, 0.065),
    ((0.0, 0.38, 0.66), 0.068, 0.064),
    ((0.0, 0.32, 0.70), 0.060, 0.056),
    ((0.0, 0.25, 0.67), 0.045, 0.042),
    ((0.0, 0.22, 0.61), 0.020, 0.020),
]
add_faceted_loft(tail_rings, up_hint=(1, 0, 0), segs=10, mat_fn=tail_mat_fn, weights=tail_weights)

# ------------------------------------------------------------------------------
# E. 4 FACETED LEGS & WHITE-SOCK PAWS WITH TOE CLAW GROOVES (MATCHING REFERENCE!)
# ------------------------------------------------------------------------------
for side, sx in [("L", 1.0), ("R", -1.0)]:
    # Front Leg
    def make_fleg_weights(s=side):
        def _w(co, _v):
            if co.z > 0.36:
                return {f"Leg_Front_Upper.{s}": 0.75, "Chest": 0.25}
            elif co.z > 0.23:
                return {f"Leg_Front_Upper.{s}": 0.80, f"Leg_Front_Lower.{s}": 0.20}
            elif co.z > 0.07:
                return {f"Leg_Front_Lower.{s}": 0.85, f"Leg_Front_Upper.{s}": 0.15}
            else:
                return {f"Paw_Front.{s}": 0.90, f"Leg_Front_Lower.{s}": 0.10}
        return _w

    def fleg_mat_fn(fc, fn, r_idx):
        if fc.z < 0.085:
            return 3 # Iconic white Shiba socks / paws!
        if abs(fc.x) < 0.085 and fc.z > 0.22:
            return 4 # Shaded cream inner leg
        return 0 if fc.y < -0.15 else 1

    fleg_rings = [
        ((sx * 0.095, -0.16, 0.43), 0.062, 0.065),
        ((sx * 0.097, -0.15, 0.33), 0.048, 0.050),
        ((sx * 0.098, -0.15, 0.23), 0.038, 0.040),
        ((sx * 0.098, -0.16, 0.13), 0.033, 0.034),
        ((sx * 0.098, -0.17, 0.05), 0.035, 0.036),
        ((sx * 0.098, -0.20, 0.025),0.042, 0.048),
        ((sx * 0.098, -0.22, 0.004),0.038, 0.044),
    ]
    add_faceted_loft(fleg_rings, up_hint=(0, 1, 0), segs=8, mat_fn=fleg_mat_fn, weights=make_fleg_weights(side))

    # 2 Dark Toe Divider Grooves on each Front Paw (Matches reference paw detail!)
    for tx_off in (-0.014, 0.014):
        groove = [
            ((sx * 0.098 + tx_off, -0.215, 0.034), 0.003, 0.004),
            ((sx * 0.098 + tx_off, -0.242, 0.020), 0.003, 0.004),
            ((sx * 0.098 + tx_off, -0.248, 0.005), 0.003, 0.003),
        ]
        add_faceted_loft(groove, up_hint=(0, 0, 1), segs=4, default_mat=10, weights={f"Paw_Front.{side}": 1.0}, twist_half_step=False)

    # Back Leg (Thicker muscular haunch/thigh + hock joint + white-tipped paw)
    def make_bleg_weights(s=side):
        def _w(co, _v):
            if co.z > 0.36:
                return {f"Leg_Back_Upper.{s}": 0.75, "Hips": 0.25}
            elif co.z > 0.23:
                return {f"Leg_Back_Upper.{s}": 0.80, f"Leg_Back_Lower.{s}": 0.20}
            elif co.z > 0.07:
                return {f"Leg_Back_Lower.{s}": 0.85, f"Leg_Back_Upper.{s}": 0.15}
            else:
                return {f"Paw_Back.{s}": 0.90, f"Leg_Back_Lower.{s}": 0.10}
        return _w

    def bleg_mat_fn(fc, fn, r_idx):
        if fc.z < 0.085:
            return 3 # White Shiba socks / paws
        if fc.y < 0.16 and fc.z < 0.34:
            return 4 # Cream front of hind thigh/hock (visible in sitting reference!)
        return 0 if abs(fc.x) > 0.11 else 1

    bleg_rings = [
        ((sx * 0.100,  0.17, 0.43), 0.076, 0.085),
        ((sx * 0.104,  0.20, 0.33), 0.062, 0.070),
        ((sx * 0.105,  0.23, 0.23), 0.044, 0.050),
        ((sx * 0.105,  0.20, 0.13), 0.034, 0.036),
        ((sx * 0.105,  0.19, 0.05), 0.035, 0.038),
        ((sx * 0.105,  0.15, 0.025),0.042, 0.048),
        ((sx * 0.105,  0.13, 0.004),0.038, 0.044),
    ]
    add_faceted_loft(bleg_rings, up_hint=(0, 1, 0), segs=8, mat_fn=bleg_mat_fn, weights=make_bleg_weights(side))

    for tx_off in (-0.014, 0.014):
        groove = [
            ((sx * 0.105 + tx_off, 0.135, 0.034), 0.003, 0.004),
            ((sx * 0.105 + tx_off, 0.108, 0.020), 0.003, 0.004),
            ((sx * 0.105 + tx_off, 0.102, 0.005), 0.003, 0.003),
        ]
        add_faceted_loft(groove, up_hint=(0, 0, 1), segs=4, default_mat=10, weights={f"Paw_Back.{side}": 1.0}, twist_half_step=False)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh_data)
bm.free()
mesh_data.update()

mesh_obj.parent = arm_obj
arm_mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
arm_mod.object = arm_obj
arm_mod.use_vertex_groups = True

bpy.context.view_layer.update()
print("Shiba_Mesh & Shiba_Rig built! Verts:", len(mesh_data.vertices), "Faces:", len(mesh_data.polygons))
