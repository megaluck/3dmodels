import bpy
import os
import sys
import math
import shutil
from mathutils import Vector, Euler

CHESS_DIR = "C:/argon/chess_table"
MIRROR_DIR = "C:/3dassets/argon/chess_table"
PREVIEW_DIR = "C:/argon/chess_table/previews"
MIRROR_PREVIEW_DIR = "C:/3dassets/argon/chess_table/previews"
ARTIFACT_DIR = "C:/Users/gusta/.gemini/antigravity-cli/brain/a90575f0-cd53-4978-87f7-f305ca6a6fc6"

os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(MIRROR_PREVIEW_DIR, exist_ok=True)

ALL_MODELS = [
    "cozy_chess_marble_table",
    "cozy_chess_round_chair",
    "cozy_chess_clock_analog",
    "cozy_chess_station_set",
    "cozy_chess_white_king",
    "cozy_chess_white_queen",
    "cozy_chess_white_bishop",
    "cozy_chess_white_knight",
    "cozy_chess_white_rook",
    "cozy_chess_white_pawn",
    "cozy_chess_black_king",
    "cozy_chess_black_queen",
    "cozy_chess_black_bishop",
    "cozy_chess_black_knight",
    "cozy_chess_black_rook",
    "cozy_chess_black_pawn",
]


def get_action_fcurves(act):
    out = list(getattr(act, "fcurves", []) or [])
    if not out:
        for layer in getattr(act, "layers", []):
            for strip in layer.strips:
                for bag in strip.channelbags:
                    out += list(bag.fcurves)
    return out


print("=" * 82)
print("1. NUMERIC AUDIT OF ALL 16 CHESS MODELS (TRIS, DIMENSIONS, EMPTIES, MOVING CLIPS)")
print("=" * 82)

for mname in ALL_MODELS:
    bpy.ops.wm.open_mainfile(filepath=f"{CHESS_DIR}/{mname}.blend")
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    rigs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    empties = {o.name: o for o in bpy.data.objects if o.type == 'EMPTY'}

    assert len(meshes) == 1, f"{mname}: expected 1 mesh, got {len(meshes)}"
    assert len(rigs) == 1, f"{mname}: expected 1 rig, got {len(rigs)}"
    m = meshes[0]
    r = rigs[0]
    r.data.pose_position = 'REST'
    bpy.context.view_layer.update()

    tris = sum(len(p.vertices) - 2 for p in m.data.polygons)
    verts = len(m.data.vertices)
    mats = [mat.name for mat in m.data.materials if mat]
    coords = [m.matrix_world @ v.co for v in m.data.vertices]
    dx = max(c.x for c in coords) - min(c.x for c in coords)
    dy = max(c.y for c in coords) - min(c.y for c in coords)
    dz = max(c.z for c in coords) - min(c.z for c in coords)

    # Verify exported GLB actions actually move!
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f"{CHESS_DIR}/{mname}.glb")
    clip_summaries = []
    for act in bpy.data.actions:
        fcs = get_action_fcurves(act)
        moving = sum(
            1 for c in fcs
            if len(c.keyframe_points) > 1
            and (max(k.co[1] for k in c.keyframe_points) - min(k.co[1] for k in c.keyframe_points)) > 1e-4
        )
        assert moving > 0, f"{mname} action {act.name} has 0 moving FCurves in exported .glb!"
        clip_summaries.append(f"{act.name}({moving}fc)")

    print(f"[PASS] {mname:26s} | {tris:5d} tris ({verts:4d}v) | dim=({dx:.3f},{dy:.3f},{dz:.3f})m | empties={len(empties):3d} | clips={', '.join(clip_summaries)}")

# Specific Socket Audit on cozy_chess_marble_table
bpy.ops.wm.open_mainfile(filepath=f"{CHESS_DIR}/cozy_chess_marble_table.blend")
t_empties = {o.name: o.matrix_world.translation.copy() for o in bpy.data.objects if o.type == 'EMPTY'}
assert "Square_a1" in t_empties and "Square_h8" in t_empties
assert "Captured_W_01" in t_empties and "Captured_W_16" in t_empties
assert "Captured_B_01" in t_empties and "Captured_B_16" in t_empties
assert "Clock_Spot" in t_empties and "Chair_White_Spot" in t_empties and "Chair_Black_Spot" in t_empties and "NPC_IK_Hand_Target" in t_empties
print(f"       Table Square_a1={tuple(round(v, 4) for v in t_empties['Square_a1'])} | Square_h8={tuple(round(v, 4) for v in t_empties['Square_h8'])}")
print(f"       Chair_White_Spot={tuple(round(v, 3) for v in t_empties['Chair_White_Spot'])} | Chair_Black_Spot={tuple(round(v, 3) for v in t_empties['Chair_Black_Spot'])} | Clock_Spot={tuple(round(v, 3) for v in t_empties['Clock_Spot'])}")


print("\n" + "=" * 82)
print("2. RENDERING 4 MULTI-ANGLE QA SHOWCASE PREVIEWS")
print("=" * 82)


def setup_garden_studio(res_x=1600, res_y=1050, lawn_floor=True):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.film_transparent = False

    world = bpy.data.worlds.new("Chess_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        # Warm late-afternoon garden sky tone
        bg.inputs[0].default_value = (0.12, 0.16, 0.14, 1.0)
        bg.inputs[1].default_value = 1.0

    # Ground plane (warm garden lawn green or dark studio slate)
    bpy.ops.mesh.primitive_plane_add(size=14.0, location=(0, 0, -0.002))
    floor = bpy.context.active_object
    fmat = bpy.data.materials.new("LawnFloor")
    fmat.use_nodes = True
    bsdf = fmat.node_tree.nodes.get("Principled BSDF")
    if lawn_floor:
        bsdf.inputs["Base Color"].default_value = (0.065, 0.115, 0.045, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.78
    else:
        bsdf.inputs["Base Color"].default_value = (0.055, 0.065, 0.080, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.35
    floor.data.materials.append(fmat)

    # Sunlight (warm golden afternoon key light matching the reference garden photo)
    sun_data = bpy.data.lights.new("SunKey", type='SUN')
    sun_data.energy = 4.2
    sun_data.color = (1.0, 0.96, 0.88)
    sun_obj = bpy.data.objects.new("SunKey", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = Euler((math.radians(46), math.radians(-22), math.radians(32)), 'XYZ')

    # Soft sky fill light
    fill_data = bpy.data.lights.new("SkyFill", type='SUN')
    fill_data.energy = 1.8
    fill_data.color = (0.82, 0.91, 1.0)
    fill_obj = bpy.data.objects.new("SkyFill", fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = Euler((math.radians(58), math.radians(18), math.radians(-135)), 'XYZ')

    # Rim light to highlight marble edges & brass collars
    rim_data = bpy.data.lights.new("RimLight", type='SUN')
    rim_data.energy = 2.0
    rim_data.color = (1.0, 0.94, 0.86)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = Euler((math.radians(38), math.radians(0), math.radians(160)), 'XYZ')

    cam_data = bpy.data.cameras.new("QACam")
    cam_obj = bpy.data.objects.new("QACam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    return scene, cam_obj


def look_at(cam_obj, pos, target, lens=42.0):
    cam_obj.location = Vector(pos)
    cam_obj.data.lens = lens
    direction = Vector(target) - Vector(pos)
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


# Render 1 & 2: Complete Assembled Station Set (Front 3/4 matching reference angle + Rear 3/4 from NPC side)
scene, cam_obj = setup_garden_studio(1600, 1050, lawn_floor=True)
bpy.ops.wm.append(
    filepath=f"{CHESS_DIR}/cozy_chess_station_set.blend/Object/Chess_Station_Mesh",
    directory=f"{CHESS_DIR}/cozy_chess_station_set.blend/Object",
    filename="Chess_Station_Mesh",
)

# Front-Right 3/4 View (showing pedestal corner pillars, recessed black panels, 64 veined squares, 32 pieces, clock & both round chairs)
look_at(cam_obj, (1.28, -1.35, 1.26), (0.0, 0.0, 0.44), lens=38.0)
out_r1 = f"{PREVIEW_DIR}/preview_chess_station_front34.png"
scene.render.filepath = out_r1
bpy.ops.render.render(write_still=True)

# Rear-Left 3/4 View (from Black/NPC chair side looking across the board toward White's chair)
look_at(cam_obj, (-1.25, 1.38, 1.28), (0.0, 0.0, 0.44), lens=38.0)
out_r2 = f"{PREVIEW_DIR}/preview_chess_station_rear34.png"
scene.render.filepath = out_r2
bpy.ops.render.render(write_still=True)

# Render 3: Close-up Lineup of all 12 Standalone Rigged Pieces (6 White + 6 Black) + Analog Chess Clock
scene, cam_obj = setup_garden_studio(1600, 950, lawn_floor=False)
kinds_order = ["king", "queen", "bishop", "knight", "rook", "pawn"]
for idx, kind in enumerate(kinds_order):
    x_pos = (idx - 2.5) * 0.072
    # White row in front (Y = -0.048)
    w_name = f"cozy_chess_white_{kind}"
    m_name = f"Chess_White_{kind.capitalize()}_Mesh"
    bpy.ops.wm.append(
        filepath=f"{CHESS_DIR}/{w_name}.blend/Object/{m_name}",
        directory=f"{CHESS_DIR}/{w_name}.blend/Object",
        filename=m_name,
    )
    w_obj = bpy.data.objects[m_name]
    w_obj.location = Vector((x_pos, -0.052, 0.0))
    if kind == "knight":
        w_obj.rotation_euler = Euler((0.0, 0.0, math.radians(-35.0)), 'XYZ')

    # Black row behind (Y = +0.048)
    b_name = f"cozy_chess_black_{kind}"
    bm_name = f"Chess_Black_{kind.capitalize()}_Mesh"
    bpy.ops.wm.append(
        filepath=f"{CHESS_DIR}/{b_name}.blend/Object/{bm_name}",
        directory=f"{CHESS_DIR}/{b_name}.blend/Object",
        filename=bm_name,
    )
    b_obj = bpy.data.objects[bm_name]
    b_obj.location = Vector((x_pos, 0.042, 0.0))
    if kind == "knight":
        b_obj.rotation_euler = Euler((0.0, 0.0, math.radians(-145.0)), 'XYZ')

# Analog Chess Clock centered behind the two rows at Y = +0.145
bpy.ops.wm.append(
    filepath=f"{CHESS_DIR}/cozy_chess_clock_analog.blend/Object/Chess_Clock_Mesh",
    directory=f"{CHESS_DIR}/cozy_chess_clock_analog.blend/Object",
    filename="Chess_Clock_Mesh",
)
clk_obj = bpy.data.objects["Chess_Clock_Mesh"]
clk_obj.location = Vector((0.0, 0.145, 0.0))

look_at(cam_obj, (0.08, -0.58, 0.28), (0.0, 0.02, 0.055), lens=35.0)
out_r3 = f"{PREVIEW_DIR}/preview_chess_pieces_lineup.png"
scene.render.filepath = out_r3
bpy.ops.render.render(write_still=True)

# Render 4: Standalone Marble Pedestal Table (with Drawer Slightly Open) + Round Drum Chair Showcase
scene, cam_obj = setup_garden_studio(1600, 1000, lawn_floor=True)
bpy.ops.wm.append(
    filepath=f"{CHESS_DIR}/cozy_chess_marble_table.blend/Object/Chess_Table_Mesh",
    directory=f"{CHESS_DIR}/cozy_chess_marble_table.blend/Object",
    filename="Chess_Table_Mesh",
)
tbl_obj = bpy.data.objects["Chess_Table_Mesh"]
tbl_obj.location = Vector((-0.24, 0.0, 0.0))

bpy.ops.wm.append(
    filepath=f"{CHESS_DIR}/cozy_chess_round_chair.blend/Object/Chess_Round_Chair_Mesh",
    directory=f"{CHESS_DIR}/cozy_chess_round_chair.blend/Object",
    filename="Chess_Round_Chair_Mesh",
)
chr_obj = bpy.data.objects["Chess_Round_Chair_Mesh"]
chr_obj.location = Vector((0.46, -0.18, 0.0))

look_at(cam_obj, (0.78, -1.35, 0.98), (0.05, -0.05, 0.38), lens=40.0)
out_r4 = f"{PREVIEW_DIR}/preview_chess_table_and_chair_closeup.png"
scene.render.filepath = out_r4
bpy.ops.render.render(write_still=True)

for p in [out_r1, out_r2, out_r3, out_r4]:
    shutil.copy2(p, f"{ARTIFACT_DIR}/{os.path.basename(p)}")
    shutil.copy2(p, f"{MIRROR_PREVIEW_DIR}/{os.path.basename(p)}")

print("All 4 QA renders saved and copied to artifact directory.")
