import bpy
import os

MODELS = [
    "cozy_bowling_mall_shell",
    "cozy_bowling_lane",
    "cozy_bowling_pinsetter",
    "cozy_bowling_ball_return",
    "cozy_bowling_overhead_scoreboard",
    "cozy_bowling_pins_pack",
    "cozy_bowling_balls_pack",
    "cozy_bowling_lounge_booth",
    "cozy_bowling_shoe_counter",
    "cozy_bowling_arcade_space_invaders",
    "cozy_bowling_trophy_case",
    "cozy_bowling_ball_rack_tiered",
    "cozy_bowling_chalk_cone_pedestal",
    "cozy_bowling_leaderboard_chalkboard",
    "cozy_bowling_lane_oiler_cart",
    "cozy_bowling_nachos_pizza_tray",
    "cozy_bowling_popcorn_cart",
    "cozy_bowling_slushie_dispenser",
    "cozy_bowling_condiment_caddy",
    "cozy_bowling_trash_ashtray_duo",
    "cozy_bowling_jukebox_bubbler",
    "cozy_bowling_bill_changer",
    "cozy_bowling_gumball_tri_rack",
    "cozy_bowling_arcade_stool_pair",
    "cozy_bowling_neon_wall_signs",
    "cozy_bowling_sputnik_clock",
    "cozy_bowling_planter_divider",
    "cozy_bowling_window_display_podium",
]

def get_curves(a):
    out = list(getattr(a, "fcurves", []) or [])
    if not out:
        for layer in getattr(a, "layers", []):
            for strip in layer.strips:
                for bag in strip.channelbags:
                    out += list(bag.fcurves)
    return out

total_clips = 0
still_clips = 0

for name in MODELS:
    fbx_path = f"C:/argon/bowling/{name}.fbx"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    print(f"=== {name} ===")
    for a in bpy.data.actions:
        fc = get_curves(a)
        moving = sum(
            1 for c in fc
            if len(c.keyframe_points) > 1
            and max(k.co[1] for k in c.keyframe_points) - min(k.co[1] for k in c.keyframe_points) > 1e-4
        )
        total_clips += 1
        if moving == 0:
            still_clips += 1
        flag = "<-- STILL!" if moving == 0 else "OK"
        print(f"  {a.name:48s} curves={len(fc):4d} moving={moving:4d} {flag}")

print(f"\nSUMMARY: {total_clips} total clips checked across {len(MODELS)} FBX models, {still_clips} still clips.")
assert still_clips == 0, f"Found {still_clips} still clips!"
