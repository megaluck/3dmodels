import bpy
import math
from mathutils import Vector

OUT_DIR = "C:/argon/bowling"


def setup_render_scene(res_x=1500, res_y=900):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.film_transparent = False

    world = bpy.data.worlds.new("BowlingPreviewWorld")
    scene.world = world
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.055, 0.068, 0.090, 1.0)
        bg.inputs[1].default_value = 1.1

    # Key, Fill, Rim sun lights
    for name, rot_deg, energy, col in [
        ("Sun_Key",  (52, 0, -35), 3.6, (1.0, 0.96, 0.90)),
        ("Sun_Fill", (62, 0, 135), 1.8, (0.80, 0.92, 1.00)),
        ("Sun_Rim",  (35, 0, 180), 2.0, (1.0, 0.88, 0.82)),
    ]:
        ldata = bpy.data.lights.new(name=name, type='SUN')
        ldata.energy = energy
        ldata.color = col
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        scene.collection.objects.link(lobj)
        lobj.rotation_euler = tuple(math.radians(a) for a in rot_deg)

    return scene


def add_point_light(name, loc, energy=450.0, color=(1.0, 0.94, 0.84), radius=0.8):
    ldata = bpy.data.lights.new(name=name, type='POINT')
    ldata.energy = energy
    ldata.color = color
    ldata.shadow_soft_size = radius
    lobj = bpy.data.objects.new(name=name, object_data=ldata)
    bpy.context.scene.collection.objects.link(lobj)
    lobj.location = Vector(loc)
    return lobj


def import_blend_objects(blend_name, offset=(0.0, 0.0, 0.0), rot_z_deg=0.0):
    blend_path = f"{OUT_DIR}/{blend_name}.blend"
    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        data_to.objects = list(data_from.objects)
    root_objs = []
    for obj in data_to.objects:
        if obj is not None:
            bpy.context.scene.collection.objects.link(obj)
            if obj.parent is None:
                root_objs.append(obj)
    for obj in root_objs:
        obj.location = Vector(obj.location) + Vector(offset)
        obj.rotation_euler.z += math.radians(rot_z_deg)
    return root_objs


def aim_camera(cam_loc, target_loc, lens=35.0):
    scene = bpy.context.scene
    cdata = bpy.data.cameras.new("PreviewCam")
    cdata.lens = lens
    cdata.clip_start = 0.05
    cdata.clip_end = 200.0
    cobj = bpy.data.objects.new("PreviewCam", cdata)
    scene.collection.objects.link(cobj)
    cobj.location = Vector(cam_loc)
    direction = Vector(target_loc) - Vector(cam_loc)
    cobj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cobj
    return cobj


# 1. Full 16.5m 3-Shop Mall Storefront & Fully Populated 28-Asset Interior Bowling Alley Showcase
def render_storefront_and_lanes():
    scene = setup_render_scene(1500, 900)
    import_blend_objects("cozy_bowling_mall_shell", (0.0, 0.0, 0.0))
    import_blend_objects("cozy_bowling_lane", (-1.15, 0.0, 0.0))
    import_blend_objects("cozy_bowling_lane", ( 1.15, 0.0, 0.0))
    import_blend_objects("cozy_bowling_pinsetter", (-1.15, 13.50, 0.0))
    import_blend_objects("cozy_bowling_pinsetter", ( 1.15, 13.50, 0.0))
    import_blend_objects("cozy_bowling_ball_return", (0.0, -0.85, 0.0))
    import_blend_objects("cozy_bowling_overhead_scoreboard", (0.0, 1.80, 2.85))
    import_blend_objects("cozy_bowling_lounge_booth", (-5.40, -1.60, 0.0))
    import_blend_objects("cozy_bowling_shoe_counter", ( 5.40, -1.60, 0.0))
    import_blend_objects("cozy_bowling_arcade_space_invaders", ( 6.60, 1.60, 0.0), rot_z_deg=-90.0)

    # All 18 Decorative & Interactive Props placed at their exact interior anchors:
    import_blend_objects("cozy_bowling_trophy_case",          ( 7.65, -0.20, 0.00), rot_z_deg=-90.0)
    import_blend_objects("cozy_bowling_ball_rack_tiered",     (-2.85, -1.20, 0.00), rot_z_deg=25.0)
    import_blend_objects("cozy_bowling_chalk_cone_pedestal",  ( 0.00, -2.55, 0.00))
    import_blend_objects("cozy_bowling_leaderboard_chalkboard",(-7.95, 3.20, 1.85), rot_z_deg=90.0)
    import_blend_objects("cozy_bowling_lane_oiler_cart",      ( 3.10, 12.20, 0.00), rot_z_deg=-20.0)
    import_blend_objects("cozy_bowling_nachos_pizza_tray",    (-5.25, -2.05, 0.57))
    import_blend_objects("cozy_bowling_condiment_caddy",      (-5.75, -2.05, 0.57))
    import_blend_objects("cozy_bowling_popcorn_cart",         (-7.15, -0.20, 0.00), rot_z_deg=65.0)
    import_blend_objects("cozy_bowling_slushie_dispenser",    ( 4.65, -1.92, 0.96))
    import_blend_objects("cozy_bowling_trash_ashtray_duo",    (-3.55, -3.40, 0.00))
    import_blend_objects("cozy_bowling_jukebox_bubbler",      (-7.15,  1.80, 0.00), rot_z_deg=75.0)
    import_blend_objects("cozy_bowling_bill_changer",         ( 7.45,  2.55, 0.00), rot_z_deg=-90.0)
    import_blend_objects("cozy_bowling_gumball_tri_rack",     ( 2.15, -3.65, 0.00))
    import_blend_objects("cozy_bowling_arcade_stool_pair",    ( 5.65,  1.60, 0.00), rot_z_deg=-90.0)
    import_blend_objects("cozy_bowling_neon_wall_signs",      ( 7.95,  4.80, 2.25), rot_z_deg=-90.0)
    import_blend_objects("cozy_bowling_sputnik_clock",        ( 0.00, 14.95, 2.95))
    import_blend_objects("cozy_bowling_planter_divider",      (-5.40, -3.35, 0.00))
    import_blend_objects("cozy_bowling_window_display_podium",(-5.75, -3.95, 0.00))
    import_blend_objects("cozy_bowling_window_display_podium",( 5.75, -3.95, 0.00))

    # Warm interior ceiling lights so the enclosed bowling alley glows richly
    for ly in (-2.0, 2.5, 7.5, 12.8):
        for lx in (-4.8, 0.0, 4.8):
            add_point_light(f"IntLight_{lx}_{ly}", (lx, ly, 3.35), energy=380.0, color=(1.0, 0.95, 0.86))

    # Exterior 3/4 view showing the exact 16.50m x 4.20m 3-Shop Storefront + Window Displays
    aim_camera((7.5, -16.5, 3.6), (0.0, -3.5, 2.0), lens=24.0)
    scene.render.filepath = f"{OUT_DIR}/preview_bowling_mall_storefront.png"
    bpy.ops.render.render(write_still=True)

    # Interior wide view looking across the populated Concourse, Twin Lanes, Lounge, Counter & Arcade
    aim_camera((3.20, -4.10, 2.10), (-0.40, 3.80, 1.15), lens=19.0)
    scene.render.filepath = f"{OUT_DIR}/preview_bowling_interior_lanes.png"
    bpy.ops.render.render(write_still=True)


# 2. Close-up Showcase of Core Props, Lounge, Shoe Counter, Pinsetter, Balls, Pins & Space Invaders Arcade
def render_props_and_arcade():
    scene = setup_render_scene(1500, 900)
    import_blend_objects("cozy_bowling_lounge_booth", (-3.7, 0.2, 0.0), rot_z_deg=22.0)
    import_blend_objects("cozy_bowling_ball_return", (-1.3, -0.4, 0.0), rot_z_deg=16.0)
    import_blend_objects("cozy_bowling_pinsetter", ( 0.4, 0.4, 0.0), rot_z_deg=-8.0)
    import_blend_objects("cozy_bowling_balls_pack", (-1.1, -1.65, 0.0))
    import_blend_objects("cozy_bowling_pins_pack", ( 0.4, -1.65, 0.0))
    import_blend_objects("cozy_bowling_shoe_counter", ( 2.5, 0.2, 0.0), rot_z_deg=-18.0)
    import_blend_objects("cozy_bowling_arcade_space_invaders", ( 4.4, -0.4, 0.0), rot_z_deg=-26.0)

    aim_camera((0.4, -7.8, 2.55), (0.35, -0.2, 0.85), lens=25.0)
    scene.render.filepath = f"{OUT_DIR}/preview_bowling_props_and_arcade.png"
    bpy.ops.render.render(write_still=True)


# 3. Showcase Lineup of Decorations Part 1 (Assets 11-19: Pro Shop, Approach & Diner Snacks)
def render_decorations_part1():
    scene = setup_render_scene(1500, 900)
    import_blend_objects("cozy_bowling_trophy_case",            (-3.40,  0.30, 0.00), rot_z_deg=18.0)
    import_blend_objects("cozy_bowling_ball_rack_tiered",       (-1.75,  0.10, 0.00), rot_z_deg=12.0)
    import_blend_objects("cozy_bowling_chalk_cone_pedestal",    (-0.65, -0.40, 0.00))
    import_blend_objects("cozy_bowling_leaderboard_chalkboard", ( 0.45,  0.55, 1.55))
    import_blend_objects("cozy_bowling_lane_oiler_cart",        ( 0.55, -0.65, 0.00), rot_z_deg=-15.0)
    import_blend_objects("cozy_bowling_popcorn_cart",           ( 2.05,  0.10, 0.00), rot_z_deg=-14.0)
    import_blend_objects("cozy_bowling_slushie_dispenser",      ( 3.25,  0.00, 0.45), rot_z_deg=-20.0)
    import_blend_objects("cozy_bowling_nachos_pizza_tray",      (-1.55, -1.25, 0.25))
    import_blend_objects("cozy_bowling_condiment_caddy",        (-0.85, -1.25, 0.25))

    aim_camera((0.0, -6.2, 2.20), (0.0, -0.1, 0.90), lens=26.0)
    scene.render.filepath = f"{OUT_DIR}/preview_bowling_decorations_part1.png"
    bpy.ops.render.render(write_still=True)


# 4. Showcase Lineup of Decorations Part 2 (Assets 20-28: Jukebox, Arcade Coin-Op, Neon, Clock & Window Podium)
def render_decorations_part2():
    scene = setup_render_scene(1500, 900)
    import_blend_objects("cozy_bowling_trash_ashtray_duo",     (-3.65, -0.20, 0.00), rot_z_deg=20.0)
    import_blend_objects("cozy_bowling_jukebox_bubbler",       (-2.45,  0.20, 0.00), rot_z_deg=16.0)
    import_blend_objects("cozy_bowling_bill_changer",          (-1.35,  0.20, 0.00), rot_z_deg=10.0)
    import_blend_objects("cozy_bowling_gumball_tri_rack",      (-0.45, -0.20, 0.00))
    import_blend_objects("cozy_bowling_arcade_stool_pair",     ( 0.50, -0.45, 0.00))
    import_blend_objects("cozy_bowling_neon_wall_signs",       (-0.15,  0.65, 1.65))
    import_blend_objects("cozy_bowling_sputnik_clock",         ( 1.95,  0.65, 2.15))
    import_blend_objects("cozy_bowling_planter_divider",       ( 1.95, -0.25, 0.00), rot_z_deg=-12.0)
    import_blend_objects("cozy_bowling_window_display_podium", ( 3.55, -0.15, 0.00), rot_z_deg=-22.0)

    aim_camera((0.0, -6.5, 2.30), (0.0, 0.0, 0.95), lens=26.0)
    scene.render.filepath = f"{OUT_DIR}/preview_bowling_decorations_part2.png"
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    render_storefront_and_lanes()
    render_props_and_arcade()
    render_decorations_part1()
    render_decorations_part2()
    print("Renders complete!")
