import bpy
import bmesh
import math
from mathutils import Vector

OUT_DIR = "C:/argon/bowling"

MODELS = [
    ("cozy_bowling_mall_shell",           "Entrance_Doors_Swing",      20),
    ("cozy_bowling_lane",                 "Bumpers_Pop_Up",            30),
    ("cozy_bowling_pinsetter",            "Sweep_Rake_Drop_And_Clear", 12),
    ("cozy_bowling_ball_return",          "Ball_Stopper_Bounce",       10),
    ("cozy_bowling_overhead_scoreboard",  "Strike_Celebration_Spin",   22),
    ("cozy_bowling_pins_pack",            "Pin_Hit_Spin_Fly",          18),
    ("cozy_bowling_balls_pack",           "Ball_Return_Pop_Up",        18),
    ("cozy_bowling_lounge_booth",         "Table_Cup_Jiggle",          10),
    ("cozy_bowling_shoe_counter",         "Service_Bell_Ring",          8),
    ("cozy_bowling_arcade_space_invaders","Joystick_Move_L_R",         10),
    ("cozy_bowling_trophy_case",          "Case_Doors_Slide",          14),
    ("cozy_bowling_ball_rack_tiered",     "Top_Ball_Lift_Inspect",     10),
    ("cozy_bowling_chalk_cone_pedestal",  "Chalk_Pat_Poof",            14),
    ("cozy_bowling_leaderboard_chalkboard","New_High_Score_Flip",      10),
    ("cozy_bowling_lane_oiler_cart",      "Cart_Roll_Condition",       12),
    ("cozy_bowling_nachos_pizza_tray",    "Cheese_Dip_Dunk",           10),
    ("cozy_bowling_popcorn_cart",         "Kettle_Dump_Pop",           18),
    ("cozy_bowling_slushie_dispenser",    "Tap_Pull_Pour",             15),
    ("cozy_bowling_condiment_caddy",      "Squeeze_Bottles_Hop",        8),
    ("cozy_bowling_trash_ashtray_duo",    "Trash_Flap_Swing",           6),
    ("cozy_bowling_jukebox_bubbler",      "Record_Change_Flip",        16),
    ("cozy_bowling_bill_changer",         "Dispense_Quarters_Clatter", 14),
    ("cozy_bowling_gumball_tri_rack",     "Turn_Crank_Drop_Gumball",   10),
    ("cozy_bowling_arcade_stool_pair",    "Stool_Sit_Bounce",           7),
    ("cozy_bowling_neon_wall_signs",      "Neon_Sign_Pulse_Tilt",      10),
    ("cozy_bowling_sputnik_clock",        "Clock_Tick_Loop",           13),
    ("cozy_bowling_planter_divider",      "Leaves_Breeze_Sway",        12),
    ("cozy_bowling_window_display_podium","Display_Pin_Salute",         8),
]


def setup_qa_scene(res_x=1600, res_y=1000):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.film_transparent = False

    world = bpy.data.worlds.new("QAWorld")
    scene.world = world
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.08, 0.09, 0.11, 1.0)
        bg.inputs[1].default_value = 1.2

    for name, rot_deg, energy, col in [
        ("Sun_Key",  (48, 0, -35), 3.6, (1.0, 0.97, 0.92)),
        ("Sun_Fill", (55, 0, 140), 2.2, (0.85, 0.93, 1.00)),
        ("Sun_Back", (45, 0, -145), 2.2, (1.0, 0.92, 0.86)),
    ]:
        ldata = bpy.data.lights.new(name=name, type='SUN')
        ldata.energy = energy
        ldata.color = col
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        scene.collection.objects.link(lobj)
        lobj.rotation_euler = tuple(math.radians(a) for a in rot_deg)

    return scene


def aim_camera(cam_loc, target_loc, lens=35.0):
    scene = bpy.context.scene
    cam = bpy.data.objects.get("QACam")
    if cam is None:
        cdata = bpy.data.cameras.new("QACam")
        cdata.clip_start = 0.02
        cdata.clip_end = 250.0
        cam = bpy.data.objects.new("QACam", cdata)
        scene.collection.objects.link(cam)
    cam.data.lens = lens
    cam.location = Vector(cam_loc)
    direction = Vector(target_loc) - Vector(cam_loc)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam
    return cam


def audit_model(name, peak_action_name, peak_frame):
    bpy.ops.wm.open_mainfile(filepath=f"{OUT_DIR}/{name}.blend")
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 800

    # Add strong back/fill lighting so rear 3/4 views are clearly visible
    for lname, rot_deg, energy in [("QA_BackLight", (50, 0, 145), 2.5), ("QA_FrontFill", (55, 0, -25), 2.5)]:
        ldata = bpy.data.lights.new(name=lname, type='SUN')
        ldata.energy = energy
        lobj = bpy.data.objects.new(name=lname, object_data=ldata)
        scene.collection.objects.link(lobj)
        lobj.rotation_euler = tuple(math.radians(a) for a in rot_deg)

    meshes = [o for o in scene.objects if o.type == 'MESH']
    rigs = [o for o in scene.objects if o.type == 'ARMATURE']
    assert len(meshes) == 1 and len(rigs) == 1, f"{name}: Expected 1 mesh and 1 rig!"
    mesh_obj = meshes[0]
    rig_obj = rigs[0]

    # 1. Check unweighted vertices & face normals
    me = mesh_obj.data
    unweighted = sum(1 for v in me.vertices if len(v.groups) == 0)
    zero_area = sum(1 for p in me.polygons if p.area < 1e-7)

    # Check UV screen normal direction if present
    screen_report = []
    for p in me.polygons:
        mat_name = me.materials[p.material_index].name if p.material_index < len(me.materials) else ""
        if "Screen" in mat_name or "CRT" in mat_name:
            screen_report.append((mat_name, tuple(round(x, 3) for x in p.normal), round(p.area, 4)))

    # Compute world-space bounding box in rest pose
    rig_obj.data.pose_position = 'REST'
    bpy.context.view_layer.update()
    verts_world = [mesh_obj.matrix_world @ v.co for v in me.vertices]
    min_v = Vector((min(v.x for v in verts_world), min(v.y for v in verts_world), min(v.z for v in verts_world)))
    max_v = Vector((max(v.x for v in verts_world), max(v.y for v in verts_world), max(v.z for v in verts_world)))
    center = (min_v + max_v) * 0.5
    size = max_v - min_v
    radius = max(size.x, size.y, size.z) * 0.5

    print(f"[AUDIT] {name:34s} | bbox_min={tuple(round(x,3) for x in min_v)} bbox_max={tuple(round(x,3) for x in max_v)} size={tuple(round(x,3) for x in size)} unweighted={unweighted} zero_area={zero_area} screens={screen_report}")

    # Check Z-fighting coplanar overlapping faces with different materials
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    # Check if any faces have inverted normals on flat horizontal top surfaces (e.g. lane arrows/dots)
    downward_top_decals = 0
    for f in bm.faces:
        mat_name = me.materials[f.material_index].name if f.material_index < len(me.materials) else ""
        if name == "cozy_bowling_lane" and mat_name == "Bowling_Walnut_Dark":
            # Arrows, foul line, pin spots on Z ~ 0.001
            avg_z = sum(v.co.z for v in f.verts) / len(f.verts)
            if abs(avg_z) < 0.005 and abs(f.normal.z) > 0.9 and f.normal.z < 0:
                downward_top_decals += 1
    if downward_top_decals:
        print(f"  [WARN] {name} has {downward_top_decals} downward-facing top decal faces!")
    bm.free()

    # Render Front-Right 3/4, Rear-Left 3/4, and Peak Pose 3/4
    rig_obj.data.pose_position = 'POSE'
    dist = max(radius * 2.35, 1.4)
    if name == "cozy_bowling_mall_shell":
        # Interior + Exterior special angles
        aim_camera((9.5, -16.0, 4.2), (0.0, -3.5, 2.1), lens=26.0)
        scene.render.filepath = f"{OUT_DIR}/qa_{name}_front34.png"
        bpy.ops.render.render(write_still=True)

        aim_camera((-9.5, 22.5, 5.5), (0.0, 5.0, 2.0), lens=26.0)
        scene.render.filepath = f"{OUT_DIR}/qa_{name}_rear34.png"
        bpy.ops.render.render(write_still=True)
    elif name == "cozy_bowling_lane":
        # Foulline/approach 3/4 and Pin-deck 3/4
        aim_camera((2.6, -4.8, 1.8), (0.0, 2.5, 0.0), lens=28.0)
        scene.render.filepath = f"{OUT_DIR}/qa_{name}_front34.png"
        bpy.ops.render.render(write_still=True)

        aim_camera((-2.4, 16.2, 1.8), (0.0, 11.5, 0.0), lens=28.0)
        scene.render.filepath = f"{OUT_DIR}/qa_{name}_rear34.png"
        bpy.ops.render.render(write_still=True)
    else:
        # Front-Right 3/4 (looking from -Y, +X)
        aim_camera((center.x + dist * 0.72, center.y - dist * 0.95, center.z + dist * 0.52), center, lens=34.0)
        scene.render.filepath = f"{OUT_DIR}/qa_{name}_front34.png"
        bpy.ops.render.render(write_still=True)

        # Rear-Left 3/4 (looking from +Y, -X)
        aim_camera((center.x - dist * 0.72, center.y + dist * 0.95, center.z + dist * 0.52), center, lens=34.0)
        scene.render.filepath = f"{OUT_DIR}/qa_{name}_rear34.png"
        bpy.ops.render.render(write_still=True)

    # Peak animation frame render from Front-Left 3/4
    act = bpy.data.actions.get(peak_action_name)
    if act and rig_obj.animation_data:
        rig_obj.animation_data.action = act
        if hasattr(act, "slots") and len(act.slots) > 0:
            try:
                rig_obj.animation_data.action_slot = act.slots[0]
            except Exception:
                pass
        scene.frame_set(peak_frame)
        bpy.context.view_layer.update()
        if name == "cozy_bowling_mall_shell":
            aim_camera((-5.5, -12.5, 3.2), (0.25, -4.5, 1.8), lens=28.0)
        elif name == "cozy_bowling_lane":
            aim_camera((-1.8, -2.5, 1.1), (0.0, 3.5, 0.0), lens=30.0)
        else:
            aim_camera((center.x - dist * 0.68, center.y - dist * 0.95, center.z + dist * 0.48), center, lens=34.0)
        scene.render.filepath = f"{OUT_DIR}/qa_{name}_peak.png"
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    for m_name, act_name, f_peak in MODELS:
        audit_model(m_name, act_name, f_peak)
    print("ALL QA AUDITS & RENDERS COMPLETE!")
