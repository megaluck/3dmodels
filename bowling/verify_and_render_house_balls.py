import bpy
import os
import sys
import math
from mathutils import Vector, Euler

SCRIPT_DIR = "C:/argon/bowling"
PREVIEW_DIR = "C:/argon/bowling/previews"
ARTIFACT_DIR = "C:/Users/gusta/.gemini/antigravity-cli/brain/a90575f0-cd53-4978-87f7-f305ca6a6fc6"
os.makedirs(PREVIEW_DIR, exist_ok=True)

BALL_NAMES = [
    "cozy_bowling_ball_06lb",
    "cozy_bowling_ball_08lb",
    "cozy_bowling_ball_10lb",
    "cozy_bowling_ball_12lb",
    "cozy_bowling_ball_14lb",
    "cozy_bowling_ball_16lb",
]

print("=" * 78)
print("1. NUMERIC AUDIT OF 6 HOUSE BALLS & EMPTY TIERED RACK (.glb & .fbx)")
print("=" * 78)

for bname in BALL_NAMES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f"{SCRIPT_DIR}/{bname}.glb")
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    empties = {o.name: o for o in bpy.data.objects if o.type == 'EMPTY'}
    assert len(meshes) == 1, f"{bname}: expected 1 mesh, got {len(meshes)}"
    m = meshes[0]
    tris = sum(len(p.vertices) - 2 for p in m.data.polygons)
    mats = [mat.name for mat in m.data.materials if mat]
    # Bounding box in world space
    coords = [m.matrix_world @ v.co for v in m.data.vertices]
    xs = [c.x for c in coords]
    ys = [c.y for c in coords]
    zs = [c.z for c in coords]
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    dz = max(zs) - min(zs)

    req_pts = ["Ball_Center", "Thumb_Hole", "Finger_Hole_Middle", "Finger_Hole_Ring"]
    for pt in req_pts:
        assert pt in empties, f"{bname}: missing empty {pt} (found {list(empties.keys())})"

    bc = empties["Ball_Center"].matrix_world.translation
    assert bc.length < 1e-4, f"{bname}: Ball_Center not at origin: {bc}"

    hole_info = []
    for hname in ["Thumb_Hole", "Finger_Hole_Middle", "Finger_Hole_Ring"]:
        e = empties[hname]
        pos = e.matrix_world.translation
        # In Blender, Verify local +Z points inward toward (0,0,0)
        # Note: GLTF import converts coords or preserves empty orientation; let's check both .blend and .glb
        hole_info.append(f"{hname}=({pos.x:+.4f},{pos.y:+.4f},{pos.z:+.4f})|r={pos.length:.4f}")

    # Also check .blend directly for exact Blender Empty local +Z axis
    bpy.ops.wm.open_mainfile(filepath=f"{SCRIPT_DIR}/{bname}.blend")
    for hname in ["Thumb_Hole", "Finger_Hole_Middle", "Finger_Hole_Ring"]:
        e = bpy.data.objects[hname]
        pos = e.matrix_world.translation
        z_axis = (e.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
        inward = (-pos).normalized()
        dot = z_axis.dot(inward)
        assert dot > 0.999, f"{bname} {hname}: local +Z does not point inward! dot={dot:.4f}"

    assert tris <= 600, f"{bname}: tris {tris} > 600"
    assert len(mats) <= 3, f"{bname}: mats {len(mats)} > 3"
    print(f"[PASS] {bname:24s} | {tris:3d} tris | dim=({dx:.4f}, {dy:.4f}, {dz:.4f})m | mats={mats}")
    print(f"       {' | '.join(hole_info)}")

# Audit Empty Tiered Rack
bpy.ops.wm.open_mainfile(filepath=f"{SCRIPT_DIR}/cozy_bowling_ball_rack_empty.blend")
rack_meshes = [o for o in bpy.data.objects if o.type == 'MESH']
rack_empties = {o.name: o for o in bpy.data.objects if o.type == 'EMPTY'}
assert "Grab_Top_Ball" not in rack_empties, "cozy_bowling_ball_rack_empty must NOT have Grab_Top_Ball"
assert len(bpy.data.actions) == 0, f"cozy_bowling_ball_rack_empty must have 0 actions, found {len(bpy.data.actions)}"

slot_positions = []
for i in range(1, 10):
    sname = f"Slot_Ball_{i}"
    assert sname in rack_empties, f"Missing {sname}"
    pos = rack_empties[sname].matrix_world.translation.copy()
    slot_positions.append((sname, pos))

print("\n[PASS] cozy_bowling_ball_rack_empty Slots (Top-to-Bottom, Left-to-Right):")
for sname, pos in slot_positions:
    print(f"       {sname}: X={pos.x:+.4f} m, Y={pos.y:+.4f} m, Z={pos.z:+.4f} m")

# Check ordering: 1..3 top tier, 4..6 mid tier, 7..9 bottom tier; X increasing left to right
for tier_start in (0, 3, 6):
    z0 = slot_positions[tier_start][1].z
    x0 = slot_positions[tier_start][1].x
    x1 = slot_positions[tier_start + 1][1].x
    x2 = slot_positions[tier_start + 2][1].x
    assert abs(slot_positions[tier_start + 1][1].z - z0) < 1e-4
    assert abs(slot_positions[tier_start + 2][1].z - z0) < 1e-4
    assert x0 < x1 < x2, f"Tier starting at {tier_start+1} not ordered left-to-right: {x0}, {x1}, {x2}"
assert slot_positions[0][1].z > slot_positions[3][1].z > slot_positions[6][1].z, "Tiers not ordered top-to-bottom!"

# Check pairwise clearance for 21.7cm balls
for i in range(len(slot_positions)):
    for j in range(i + 1, len(slot_positions)):
        dist = (slot_positions[i][1] - slot_positions[j][1]).length
        clearance = dist - 0.217
        assert clearance > 0.05, f"Overlap/tight between {slot_positions[i][0]} and {slot_positions[j][0]}: clearance={clearance:.4f}m"

# Audit Regulation 60-ft models
print("\n" + "=" * 78)
print("2. NUMERIC AUDIT OF REGULATION 60-FT LANE, PINSETTER & MALL SHELL")
print("=" * 78)
for rname in ["cozy_bowling_lane", "cozy_bowling_pinsetter", "cozy_bowling_mall_shell"]:
    bpy.ops.wm.open_mainfile(filepath=f"{SCRIPT_DIR}/{rname}.blend")
    m = [o for o in bpy.data.objects if o.type == 'MESH'][0]
    tris = sum(len(p.vertices) - 2 for p in m.data.polygons)
    coords = [m.matrix_world @ v.co for v in m.data.vertices]
    ymin, ymax = min(c.y for c in coords), max(c.y for c in coords)
    empties = {o.name: o.matrix_world.translation.copy() for o in bpy.data.objects if o.type == 'EMPTY'}
    print(f"[PASS] {rname:26s} | {tris:5d} tris | Y span=[{ymin:+.3f}, {ymax:+.3f}]m | empties={len(empties)}")
    if rname == "cozy_bowling_lane":
        p1 = empties["Pin_Spot_1"]
        p10 = empties["Pin_Spot_10"]
        print(f"       Pin_Spot_1 Y={p1.y:.4f}m (USBC 60ft = 18.2880m) | Pin_Spot_10 Y={p10.y:.4f}m")
        assert abs(p1.y - 18.288) < 1e-3
    elif rname == "cozy_bowling_pinsetter":
        cf = empties["Cushion_Face"]
        pbs = empties["Pit_Ball_Swallow"]
        print(f"       Cushion_Face Y={cf.y:.4f}m | Pit_Ball_Swallow Y={pbs.y:.4f}m")
        assert abs(cf.y - 1.503) < 5e-3
    elif rname == "cozy_bowling_mall_shell":
        l1 = empties["Lane_1_Origin"]
        oc = empties["Oiler_Cart_Origin"]
        sc = empties["Sputnik_Clock_Origin"]
        print(f"       Lane_1_Origin=({l1.x:+.2f},{l1.y:+.2f},{l1.z:+.2f}) | Oiler_Cart_Origin Y={oc.y:+.3f}m | Sputnik_Clock_Origin Y={sc.y:+.3f}m")
        assert abs(oc.y - 18.288) < 5e-3

print("\n" + "=" * 78)
print("3. RENDERING QA PREVIEWS OF 6 HOUSE BALLS & EMPTY/POPULATED RACK")
print("=" * 78)

def setup_render_scene(res_x=1400, res_y=900):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.film_transparent = False

    world = bpy.data.worlds.new("QA_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.045, 0.055, 0.075, 1.0)
        bg.inputs[1].default_value = 1.0

    # Studio backdrop floor
    bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0, 0, -0.002))
    floor = bpy.context.active_object
    fmat = bpy.data.materials.new("StudioFloor")
    fmat.use_nodes = True
    bsdf = fmat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.06, 0.075, 0.095, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.35
    floor.data.materials.append(fmat)

    # Lights
    key_data = bpy.data.lights.new("KeyLight", type='SUN')
    key_data.energy = 3.8
    key_data.color = (1.0, 0.97, 0.92)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    bpy.context.collection.objects.link(key_obj)
    key_obj.rotation_euler = Euler((math.radians(48), math.radians(-18), math.radians(28)), 'XYZ')

    fill_data = bpy.data.lights.new("FillLight", type='SUN')
    fill_data.energy = 1.8
    fill_data.color = (0.85, 0.93, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = Euler((math.radians(55), math.radians(20), math.radians(-135)), 'XYZ')

    rim_data = bpy.data.lights.new("RimLight", type='SUN')
    rim_data.energy = 2.2
    rim_data.color = (1.0, 0.92, 0.85)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = Euler((math.radians(35), math.radians(0), math.radians(165)), 'XYZ')

    return scene

def look_at(cam_obj, pos, target, lens=50.0):
    cam_obj.location = Vector(pos)
    cam_obj.data.lens = lens
    direction = Vector(target) - Vector(pos)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

# Render 1: Front 3/4 Lineup of the 6 House Balls (showing finger holes + weight numerals 6, 8, 10, 12, 14, 16)
scene = setup_render_scene(1600, 900)
spacing = 0.285
for idx, bname in enumerate(BALL_NAMES):
    bpy.ops.import_scene.gltf(filepath=f"{SCRIPT_DIR}/{bname}.glb")
    m = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
    x_pos = (idx - 2.5) * spacing
    # Place resting on Z=0 (ball center at Z = 0.1085)
    # Tilt slightly forward (-28 deg around X) so the top finger holes AND front weight numeral are both clearly visible
    m.location = Vector((x_pos, 0.0, 0.1085))
    m.rotation_euler = Euler((math.radians(-22), 0.0, math.radians(-10)), 'XYZ')

cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

look_at(cam_obj, (0.12, -2.05, 0.56), (0.0, 0.0, 0.11), lens=36.0)
out_front = f"{PREVIEW_DIR}/preview_house_balls_front34.png"
scene.render.filepath = out_front
bpy.ops.render.render(write_still=True)

# Render 2: Rear 3/4 Lineup of the 6 House Balls (showing back side + Coral Lanes starburst mark + swirl bands)
for o in [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name != "Plane"]:
    o.rotation_euler = Euler((math.radians(10), 0.0, math.radians(15)), 'XYZ')
look_at(cam_obj, (-0.15, 2.05, 0.58), (0.0, 0.0, 0.11), lens=36.0)
out_rear = f"{PREVIEW_DIR}/preview_house_balls_rear34.png"
scene.render.filepath = out_rear
bpy.ops.render.render(write_still=True)

# Render 3: Showcase with Empty Rack (left) and Populated Rack holding the 6 House Balls in Slots 1..6 (right), plus close-up lineup in front
scene = setup_render_scene(1600, 1000)
# Left: Empty rack at X = -0.62, Y = 0.25
bpy.ops.import_scene.gltf(filepath=f"{SCRIPT_DIR}/cozy_bowling_ball_rack_empty.glb")
rack_empty_objs = [o for o in bpy.context.selected_objects]
for o in rack_empty_objs:
    if o.parent is None:
        o.location.x -= 0.62
        o.location.y += 0.25

# Right: Second Empty rack at X = +0.62, Y = 0.25 populated with the 6 house balls at Slot_Ball_1..6 + 3 more at Slot_Ball_7..9
bpy.ops.import_scene.gltf(filepath=f"{SCRIPT_DIR}/cozy_bowling_ball_rack_empty.glb")
rack_pop_objs = [o for o in bpy.context.selected_objects]
slot_world_map = {}
for o in rack_pop_objs:
    if o.parent is None:
        o.location.x += 0.62
        o.location.y += 0.25
bpy.context.view_layer.update()
for o in rack_pop_objs:
    if o.type == 'EMPTY' and o.name.startswith("Slot_Ball_"):
        base_name = o.name.split(".")[0]
        slot_world_map[base_name] = o.matrix_world.translation.copy()

# Populate slots 1..9 on the right rack
slot_ball_order = [
    ("Slot_Ball_1", "cozy_bowling_ball_06lb"),
    ("Slot_Ball_2", "cozy_bowling_ball_08lb"),
    ("Slot_Ball_3", "cozy_bowling_ball_10lb"),
    ("Slot_Ball_4", "cozy_bowling_ball_12lb"),
    ("Slot_Ball_5", "cozy_bowling_ball_14lb"),
    ("Slot_Ball_6", "cozy_bowling_ball_16lb"),
    ("Slot_Ball_7", "cozy_bowling_ball_08lb"),
    ("Slot_Ball_8", "cozy_bowling_ball_12lb"),
    ("Slot_Ball_9", "cozy_bowling_ball_16lb"),
]
for sname, bfile in slot_ball_order:
    bpy.ops.import_scene.gltf(filepath=f"{SCRIPT_DIR}/{bfile}.glb")
    m = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
    m.location = slot_world_map[sname]
    m.rotation_euler = Euler((math.radians(-18), 0.0, math.radians(-8)), 'XYZ')

# Foreground lineup of the 6 house balls at Y = -0.38
for idx, bname in enumerate(BALL_NAMES):
    bpy.ops.import_scene.gltf(filepath=f"{SCRIPT_DIR}/{bname}.glb")
    m = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
    x_pos = (idx - 2.5) * 0.28
    m.location = Vector((x_pos, -0.42, 0.1085))
    m.rotation_euler = Euler((math.radians(-24), 0.0, math.radians(-12)), 'XYZ')

cam_data = bpy.data.cameras.new("CamShowcase")
cam_obj = bpy.data.objects.new("CamShowcase", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj
look_at(cam_obj, (0.15, -3.10, 1.15), (0.0, 0.05, 0.52), lens=34.0)
out_showcase = f"{PREVIEW_DIR}/preview_house_balls_and_rack_showcase.png"
scene.render.filepath = out_showcase
bpy.ops.render.render(write_still=True)

import shutil
os.makedirs("C:/3dassets/argon/bowling/previews", exist_ok=True)
for p in [out_front, out_rear, out_showcase]:
    shutil.copy2(p, f"{ARTIFACT_DIR}/{os.path.basename(p)}")
    shutil.copy2(p, f"C:/3dassets/argon/bowling/previews/{os.path.basename(p)}")

print("All QA renders saved and copied to artifact directory.")
