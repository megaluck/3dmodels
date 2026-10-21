"""
Audits all 16 Table Tennis .glb exports (verifying mesh, rig, sockets, and moving F-curves > 0)
and renders 4 multi-angle QA preview sheets.
"""

import os
import sys
import math
import shutil
import bpy
from mathutils import Vector, Euler

OUT_DIR = "C:/argon/table_tennis"
PREVIEW_DIR = "C:/argon/table_tennis/previews"
ARTIFACT_DIR = "C:/Users/gusta/.gemini/antigravity-cli/brain/a90575f0-cd53-4978-87f7-f305ca6a6fc6"

ASSETS = [
    "cozy_tt_table_indoor_pro",
    "cozy_tt_table_outdoor_garden",
    "cozy_tt_paddle_classic",
    "cozy_tt_paddle_carbon_pro",
    "cozy_tt_paddle_cast_iron_pan",
    "cozy_tt_ball_white_3star",
    "cozy_tt_ball_orange_3star",
    "cozy_tt_ball_twotone_spin",
    "cozy_tt_robot_launcher",
    "cozy_tt_target_flip_bullseye",
    "cozy_tt_target_cup_pyramid",
    "cozy_tt_scoreboard_flip",
    "cozy_tt_ball_hopper_caddy",
    "cozy_tt_paddle_rack_stand",
    "cozy_tt_barrier_surround",
    "cozy_tt_arena_showcase",
]


def get_action_fcurves(act):
    out = list(getattr(act, "fcurves", []) or [])
    if not out:
        for layer in getattr(act, "layers", []):
            for strip in layer.strips:
                for bag in strip.channelbags:
                    out += list(bag.fcurves)
    return out


def audit_all_exports():
    print("\n================ TABLE TENNIS 16-ASSET GLB AUDIT ================")
    all_passed = True
    for name in ASSETS:
        glb_path = f"{OUT_DIR}/{name}.glb"
        if not os.path.exists(glb_path):
            print(f"[FAIL] Missing {glb_path}")
            all_passed = False
            continue

        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=glb_path)

        meshes = [o for o in bpy.data.objects if o.type == 'MESH']
        arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
        empties = [o for o in bpy.data.objects if o.type == 'EMPTY']

        total_verts = sum(len(m.data.vertices) for m in meshes)
        total_faces = sum(len(m.data.polygons) for m in meshes)

        moving_actions = 0
        total_actions = len(bpy.data.actions)
        for a in bpy.data.actions:
            fcs = get_action_fcurves(a)
            moving = sum(
                1 for c in fcs
                if len(c.keyframe_points) > 1
                and (max(k.co[1] for k in c.keyframe_points) - min(k.co[1] for k in c.keyframe_points)) > 1e-4
            )
            if moving > 0:
                moving_actions += 1

        status = "PASS" if (len(meshes) >= 1 and len(arms) >= 1 and moving_actions > 0) else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(
            f"[{status}] {name:30s} | verts={total_verts:5d} faces={total_faces:5d} "
            f"| rigs={len(arms)} sockets={len(empties):2d} | moving_clips={moving_actions}/{total_actions}"
        )

    if not all_passed:
        raise RuntimeError("One or more Table Tennis assets failed the GLB audit!")
    print("================ ALL 16 ASSETS PASSED AUDIT ================\n")


def setup_studio_lighting_and_camera(cam_loc, look_at, lens=38.0, res=(1440, 960)):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]
    scene.render.film_transparent = False

    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.14, 0.16, 0.20, 1.0)
        bg.inputs[1].default_value = 1.1

    # Studio floor plane for grounded contact shadow
    bpy.ops.mesh.primitive_plane_add(size=18.0, location=(0.0, 0.0, -0.002))
    floor = bpy.context.active_object
    fmat = bpy.data.materials.new("StudioFloor")
    fmat.use_nodes = True
    fbsdf = fmat.node_tree.nodes.get("Principled BSDF")
    if fbsdf:
        fbsdf.inputs["Base Color"].default_value = (0.09, 0.10, 0.12, 1.0)
        fbsdf.inputs["Roughness"].default_value = 0.55
    floor.data.materials.append(fmat)

    # Key, Fill, and Rim Sun Lights
    for lname, energy, rot_deg, col in [
        ("KeySun", 3.8, (48.0, 12.0, -35.0), (1.0, 0.97, 0.92)),
        ("FillSun", 1.8, (55.0, -15.0, 135.0), (0.85, 0.92, 1.0)),
        ("RimSun", 2.2, (35.0, 0.0, -155.0), (1.0, 0.95, 0.88)),
    ]:
        ldata = bpy.data.lights.new(name=lname, type='SUN')
        ldata.energy = energy
        ldata.color = col
        lobj = bpy.data.objects.new(name=lname, object_data=ldata)
        lobj.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
        scene.collection.objects.link(lobj)

    cam_data = bpy.data.cameras.new("QACam")
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new("QACam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_obj.location = Vector(cam_loc)
    direction = Vector(look_at) - Vector(cam_loc)
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return scene


def import_asset_at(asset_name, loc=(0.0, 0.0, 0.0), rot_deg=(0.0, 0.0, 0.0), scale=1.0, rest_pose=False):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f"{OUT_DIR}/{asset_name}.glb")
    new_objs = [o for o in bpy.data.objects if o not in before]
    if rest_pose:
        for o in new_objs:
            if o.type == 'ARMATURE':
                o.data.pose_position = 'REST'
    roots = [o for o in new_objs if o.parent is None]
    for r in roots:
        r.location = Vector(loc)
        r.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
        r.scale = Vector((scale, scale, scale))
    return roots


def render_to_both(filename):
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    out_path = f"{PREVIEW_DIR}/{filename}"
    bpy.context.scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    shutil.copy2(out_path, f"{OUT_DIR}/{filename}")
    shutil.copy2(out_path, f"{ARTIFACT_DIR}/{filename}")
    print(f"[RENDERED] {out_path}")


def render_all_previews():
    # 1. Arena Front-Right 3/4 View
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import_asset_at("cozy_tt_arena_showcase", (0.0, 0.0, 0.0))
    setup_studio_lighting_and_camera(cam_loc=(3.4, -3.6, 2.35), look_at=(0.0, 0.0, 0.65), lens=35.0)
    bpy.context.scene.frame_set(10)
    render_to_both("preview_tt_arena_front34.png")

    # 2. Arena Rear-Left 3/4 View
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import_asset_at("cozy_tt_arena_showcase", (0.0, 0.0, 0.0))
    setup_studio_lighting_and_camera(cam_loc=(-3.4, 3.6, 2.35), look_at=(0.0, 0.0, 0.65), lens=35.0)
    bpy.context.scene.frame_set(24)
    render_to_both("preview_tt_arena_rear34.png")

    # 3. Both Table Variants (Indoor Pro Blue + Outdoor Garden Green/Teak + Hopper Caddy + Stand)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import_asset_at("cozy_tt_table_indoor_pro", (-1.05, 0.0, 0.0), rest_pose=True)
    import_asset_at("cozy_tt_table_outdoor_garden", (+1.05, 0.0, 0.0), rest_pose=True)
    import_asset_at("cozy_tt_ball_hopper_caddy", (-2.10, -0.6, 0.0), rest_pose=True)
    import_asset_at("cozy_tt_paddle_rack_stand", (+2.10, -0.6, 0.0), rot_deg=(0.0, 0.0, -25.0), rest_pose=True)
    setup_studio_lighting_and_camera(cam_loc=(0.0, -4.85, 2.55), look_at=(0.0, -0.1, 0.55), lens=28.0)
    render_to_both("preview_tt_tables_indoor_outdoor.png")

    # 4. Close-up Lineup: 3 Paddles, 3 Balls, Robot Launcher, Flip Bullseye Target, Cup Pyramid, Scoreboard
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Display pedestal slab
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.02))
    ped = bpy.context.active_object
    ped.scale = (2.2, 0.9, 0.04)
    pmat = bpy.data.materials.new("PedMat")
    pmat.use_nodes = True
    pmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.03, 0.09, 0.22, 1.0)
    ped.data.materials.append(pmat)

    import_asset_at("cozy_tt_paddle_classic", (-0.68, -0.16, 0.10), rot_deg=(15.0, 0.0, -12.0), rest_pose=True)
    import_asset_at("cozy_tt_paddle_carbon_pro", (-0.48, -0.16, 0.10), rot_deg=(15.0, 0.0, 12.0), rest_pose=True)
    import_asset_at("cozy_tt_paddle_cast_iron_pan", (-0.28, -0.16, 0.10), rot_deg=(15.0, 0.0, -8.0), rest_pose=True)

    import_asset_at("cozy_tt_ball_white_3star", (-0.66, -0.34, 0.04), scale=1.5, rest_pose=True)
    import_asset_at("cozy_tt_ball_orange_3star", (-0.48, -0.34, 0.04), scale=1.5, rest_pose=True)
    import_asset_at("cozy_tt_ball_twotone_spin", (-0.30, -0.34, 0.04), scale=1.5, rest_pose=True)

    import_asset_at("cozy_tt_robot_launcher", (-0.02, 0.04, 0.04), rest_pose=True)
    import_asset_at("cozy_tt_target_flip_bullseye", (+0.30, -0.14, 0.04), rest_pose=True)
    import_asset_at("cozy_tt_target_cup_pyramid", (+0.62, -0.14, 0.04), rest_pose=True)
    import_asset_at("cozy_tt_scoreboard_flip", (+0.52, +0.20, 0.04), rot_deg=(0.0, 0.0, -15.0), rest_pose=True)

    setup_studio_lighting_and_camera(cam_loc=(0.0, -1.85, 0.78), look_at=(0.0, -0.02, 0.22), lens=32.0)
    render_to_both("preview_tt_paddles_balls_robot_targets.png")


if __name__ == "__main__":
    audit_all_exports()
    render_all_previews()
