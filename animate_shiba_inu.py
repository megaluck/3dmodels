import bpy
import math
from mathutils import Vector, Euler

arm_obj = bpy.data.objects.get("Shiba_Rig")
scene = bpy.context.scene
scene.render.fps = 24

# Clear existing actions & NLA tracks on Shiba_Rig
if arm_obj.animation_data:
    arm_obj.animation_data_clear()
for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)

arm_obj.animation_data_create()
arm_obj.animation_data.use_nla = True

pbones = arm_obj.pose.bones
for pb in pbones:
    pb.rotation_mode = 'XYZ'

def reset_pose():
    for pb in pbones:
        pb.location = Vector((0.0, 0.0, 0.0))
        pb.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
        pb.scale = Vector((1.0, 1.0, 1.0))

def set_bone(name, loc=None, rot_deg=None, scale=None):
    pb = pbones.get(name)
    if not pb:
        return
    if loc is not None:
        pb.location = Vector(loc)
    if rot_deg is not None:
        pb.rotation_euler = Euler((
            math.radians(rot_deg[0]),
            math.radians(rot_deg[1]),
            math.radians(rot_deg[2]),
        ), 'XYZ')
    if scale is not None:
        pb.scale = Vector(scale)

def set_bone_world(name, world_rot_deg=(0.0, 0.0, 0.0), world_loc=(0.0, 0.0, 0.0)):
    """
    Converts a world-space Euler XYZ rotation delta (degrees) and world-space
    translation delta (meters) into the bone's exact local rest space (`bone.matrix_local`).
    World axes:
      +X = Dog's Left, -X = Dog's Right
      -Y = Dog's Front (Snout), +Y = Dog's Rear (Tail)
      +Z = Up, -Z = Down
    Consequences of `world_rot_deg = (rx, ry, rz)`:
      - Spine / Chest / Neck / Head / Jaw:
          rx > 0 pitches DOWN (-Z); rx < 0 pitches UP (+Z)
          ry > 0 rolls Left (+X) side UP / Right (-X) side DOWN
          rz > 0 yaws Snout (-Y) toward Left (+X)
      - Legs (Leg_Front_Upper/Lower, Leg_Back_Upper/Lower):
          rx < 0 swings leg FORWARD (-Y); rx > 0 swings leg BACKWARD (+Y)
          ry > 0 swings leg Toward Right (-X); ry < 0 swings leg Toward Left (+X)
    """
    pb = pbones.get(name)
    if not pb:
        return
    M_rest = pb.bone.matrix_local.to_3x3()
    R_world = Euler((
        math.radians(world_rot_deg[0]),
        math.radians(world_rot_deg[1]),
        math.radians(world_rot_deg[2]),
    ), 'XYZ').to_matrix()
    R_local = M_rest.transposed() @ R_world @ M_rest
    pb.rotation_euler = R_local.to_euler('XYZ')
    if world_loc != (0.0, 0.0, 0.0):
        pb.location = M_rest.transposed() @ Vector(world_loc)

def key_all_bones(frame):
    for pb in pbones:
        pb.keyframe_insert(data_path="location", frame=frame)
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)

def set_linear_or_bezier(action, cyclic=False):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fcu in bag.fcurves:
                    for kp in fcu.keyframe_points:
                        kp.interpolation = 'BEZIER'
                        kp.handle_left_type = 'AUTO_CLAMPED'
                        kp.handle_right_type = 'AUTO_CLAMPED'

def apply_sit_base_pose():
    """
    Sets the polite sitting Shiba Inu posture matching the user's reference screenshot:
    - Rear hips lowered (`Hips` loc z = -0.175, rot x = -38 deg)
    - Spine & Chest pitched proudly upright (`Spine` rot x = +20, `Chest` rot x = +18)
    - Back legs folded neatly on the ground with white paws forward
    - Front legs planted straight and proud in front
    """
    reset_pose()
    set_bone("Hips",  loc=(0.0, 0.02, -0.175), rot_deg=(-38.0, 0.0, 0.0))
    set_bone("Spine", rot_deg=(20.0, 0.0, 0.0))
    set_bone("Chest", rot_deg=(18.0, 0.0, 0.0))
    set_bone("Neck",  rot_deg=(4.0, 0.0, 0.0))
    set_bone("Head",  rot_deg=(-4.0, 0.0, 0.0))
    for side, sx in [("L", 1.0), ("R", -1.0)]:
        # Folded hind legs resting on the floor
        set_bone(f"Leg_Back_Upper.{side}", rot_deg=(76.0, 0.0, sx * -6.0))
        set_bone(f"Leg_Back_Lower.{side}", rot_deg=(-112.0, 0.0, 0.0))
        set_bone(f"Paw_Back.{side}",       rot_deg=(74.0, 0.0, 0.0))
        # Upright front legs compensating for chest pitch and lowered hips
        set_bone(f"Leg_Front_Upper.{side}", loc=(0.0, -0.02, -0.05), rot_deg=(6.0, 0.0, 0.0))
        set_bone(f"Leg_Front_Lower.{side}", rot_deg=(-6.0, 0.0, 0.0))
        set_bone(f"Paw_Front.{side}",       rot_deg=(0.0, 0.0, 0.0))

# Dictionary of (action_name, frame_end, builder_fn, is_loop)
anim_specs = []

# ==============================================================================
# 1. Idle_Sit_Smile (Frames 1..72, 3.0s Loop) — MATCHES REFERENCE SCREENSHOT!
# ==============================================================================
def build_idle_sit_smile(act):
    frames = [1, 18, 36, 54, 72]
    head_tilts = [
        (-4.0,  6.0,  4.0),  # f1: Cute Shiba head tilt like reference!
        (-7.0, 12.0,  7.0),  # f18: Deeper curious head tilt + ear perk
        (-4.0,  4.0,  2.0),  # f36: Center proud smile
        (-6.0, -9.0, -5.0),  # f54: Tilt other way curiously
        (-4.0,  6.0,  4.0),  # f72: Loop back cleanly
    ]
    tail_sways = [0.0, 16.0, 0.0, -16.0, 0.0]
    breaths = [0.0, -2.5, 0.0, -2.5, 0.0]

    for idx, f in enumerate(frames):
        scene.frame_set(f)
        apply_sit_base_pose()
        br = breaths[idx]
        ht = head_tilts[idx]
        ts = tail_sways[idx]
        set_bone_world("Chest", (18.0 + br, 0.0, 0.0))
        set_bone_world("Head",  ht)
        set_bone_world("Ear.L", (-4.0, 5.0 if idx == 1 else 0.0, 0.0))
        set_bone_world("Ear.R", (-4.0, -5.0 if idx == 3 else 0.0, 0.0))
        set_bone("Brow.L", loc=(0.0, 0.0, 0.004 if idx in (1, 3) else 0.0))
        set_bone("Brow.R", loc=(0.0, 0.0, 0.004 if idx in (1, 3) else 0.0))
        set_bone_world("Tail_Base", (-8.0, ts, ts * 0.6))
        set_bone_world("Tail_Mid",  (0.0, ts * 0.8, 0.0))
        key_all_bones(f)

anim_specs.append(("Idle_Sit_Smile", 72, build_idle_sit_smile, True))

# ==============================================================================
# 2. Idle_Stand_Pant (Frames 1..60, 2.5s Loop)
# ==============================================================================
def build_idle_stand_pant(act):
    for f in range(1, 61, 5):
        scene.frame_set(f)
        reset_pose()
        t = (f - 1) / 59.0
        pant = math.sin(t * 6.0 * math.pi) # 3 happy pants per cycle
        wag  = math.sin(t * 4.0 * math.pi) # 2 tail wags per cycle
        breath = math.sin(t * 2.0 * math.pi)

        set_bone_world("Hips",  (0.0, 0.0, 0.0), world_loc=(0.0, 0.0, 0.008 * breath))
        set_bone_world("Chest", (-2.5 * breath, 0.0, 0.0))
        set_bone_world("Head",  (-4.0 - 2.0 * breath, 4.0 * wag, 3.0 * wag))
        set_bone_world("Jaw",   (14.0 + 7.0 * pant, 0.0, 0.0))
        set_bone("Tongue", loc=(0.0, -0.012 - 0.006 * max(0.0, pant), -0.004), rot_deg=(8.0, 0.0, 0.0))
        set_bone_world("Tail_Base", (-6.0, 18.0 * wag, 14.0 * wag))
        set_bone_world("Tail_Mid",  (0.0, 14.0 * wag, 10.0 * wag))
        key_all_bones(f)

anim_specs.append(("Idle_Stand_Pant", 60, build_idle_stand_pant, True))

# ==============================================================================
# 3. Pet_Head_Bliss (Frames 1..60, 2.5s Interaction Loop/Clip)
#    Leans head up into the player's hand, folds "airplane ears" back, squints
#    eyes shut in bliss (`Eyelid.L/R`), and wags tail double-speed!
# ==============================================================================
def build_pet_head_bliss(act):
    for f in range(1, 61, 4):
        scene.frame_set(f)
        apply_sit_base_pose()
        t = (f - 1) / 59.0
        envelope = math.sin(min(1.0, t * 4.0) * (math.pi / 2.0)) if t < 0.8 else math.cos((t - 0.8) / 0.2 * (math.pi / 2.0))
        wag = math.sin(t * 8.0 * math.pi) # Fast happy tail wag!
        nuzzle = math.sin(t * 4.0 * math.pi)

        set_bone_world("Neck",  (8.0 * envelope, 0.0, 0.0))
        set_bone_world("Head",  (-16.0 * envelope, 8.0 * nuzzle * envelope, 5.0 * nuzzle * envelope))
        # Airplane ears folded happily back & out!
        set_bone_world("Ear.L", (-24.0 * envelope, 34.0 * envelope, 12.0 * envelope))
        set_bone_world("Ear.R", (-24.0 * envelope, -34.0 * envelope, -12.0 * envelope))
        # Eyes squinted shut in pure bliss!
        set_bone("Eyelid.L", loc=(0.0, -0.003 * envelope, -0.014 * envelope), rot_deg=(22.0 * envelope, 0.0, 0.0))
        set_bone("Eyelid.R", loc=(0.0, -0.003 * envelope, -0.014 * envelope), rot_deg=(22.0 * envelope, 0.0, 0.0))
        set_bone("Brow.L",   loc=(0.0, 0.0, -0.005 * envelope))
        set_bone("Brow.R",   loc=(0.0, 0.0, -0.005 * envelope))
        # Slight happy smile pant
        set_bone_world("Jaw", (10.0 * envelope, 0.0, 0.0))
        set_bone("Tongue",    loc=(0.0, -0.010 * envelope, 0.0))
        # Rapid tail wag
        set_bone_world("Tail_Base", (-10.0, 24.0 * wag, 18.0 * wag))
        set_bone_world("Tail_Mid",  (0.0, 18.0 * wag, 12.0 * wag))
        key_all_bones(f)

anim_specs.append(("Pet_Head_Bliss", 60, build_pet_head_bliss, True))

# ==============================================================================
# 4. Belly_Rub_RollOver (Frames 1..72, 3.0s Interaction)
#    Rolls onto its back on the floor with paws curled over chest and kicks hind leg!
# ==============================================================================
def build_belly_rub_rollover(act):
    for f in range(1, 73, 4):
        scene.frame_set(f)
        reset_pose()
        t = (f - 1) / 71.0
        if t < 0.22:
            roll = math.sin((t / 0.22) * (math.pi / 2.0))
        elif t > 0.78:
            roll = math.cos(((t - 0.78) / 0.22) * (math.pi / 2.0))
        else:
            roll = 1.0

        kick = math.sin(t * 10.0 * math.pi) * roll # Rhythmically kicking "the good spot"!
        wag  = math.sin(t * 6.0 * math.pi) * roll

        # Roll Root around World Y by 165 deg and lift Root Z by +0.62m so the inverted back rests on Z=0!
        set_bone_world("Root",  (0.0, 165.0 * roll, 0.0), world_loc=(0.0, 0.0, 0.62 * roll))
        # Since the dog is upside-down when rolled, positive rx curls the spine/neck/head UP toward the belly (+Z)!
        set_bone_world("Spine", (10.0 * roll, 0.0, 6.0 * wag))
        set_bone_world("Chest", (12.0 * roll, 0.0, 0.0))
        set_bone_world("Neck",  (24.0 * roll, 0.0, 0.0))
        set_bone_world("Head",  (22.0 * roll, 10.0 * roll, 6.0 * wag))
        set_bone_world("Jaw",   (18.0 * roll, 0.0, 0.0))
        set_bone("Tongue", loc=(0.010 * roll, -0.015 * roll, 0.0), rot_deg=(12.0 * roll, 0.0, 15.0 * roll))
        set_bone_world("Ear.L", (-18.0 * roll, 22.0 * roll, 0.0))
        set_bone_world("Ear.R", (-18.0 * roll, -22.0 * roll, 0.0))
        set_bone("Eyelid.L", loc=(0.0, -0.003 * roll, -0.014 * roll))
        set_bone("Eyelid.R", loc=(0.0, -0.003 * roll, -0.014 * roll))

        # Front paws tucked neatly over chest
        for side, sx in [("L", 1.0), ("R", -1.0)]:
            set_bone_world(f"Leg_Front_Upper.{side}", (-25.0 * roll, sx * 8.0 * roll, 0.0))
            set_bone_world(f"Leg_Front_Lower.{side}", (65.0 * roll, 0.0, 0.0))
            set_bone_world(f"Paw_Front.{side}",       (35.0 * roll, 0.0, 0.0))

        # Left back leg relaxed open, Right back leg kicking in bliss!
        set_bone_world("Leg_Back_Upper.L", (35.0 * roll, -14.0 * roll, 0.0))
        set_bone_world("Leg_Back_Lower.L", (-55.0 * roll, 0.0, 0.0))
        set_bone_world("Paw_Back.L",       (20.0 * roll, 0.0, 0.0))

        set_bone_world("Leg_Back_Upper.R", ((42.0 + 24.0 * kick) * roll, 16.0 * roll, 0.0))
        set_bone_world("Leg_Back_Lower.R", ((-58.0 - 28.0 * kick) * roll, 0.0, 0.0))
        set_bone_world("Paw_Back.R",       ((20.0 + 18.0 * kick) * roll, 0.0, 0.0))

        set_bone_world("Tail_Base", (15.0 * roll, 18.0 * wag, 14.0 * wag))
        key_all_bones(f)

anim_specs.append(("Belly_Rub_RollOver", 72, build_belly_rub_rollover, False))

# ==============================================================================
# 5. Speak_Double_Bark (Frames 1..40, 1.67s "Arf! Arf!")
# ==============================================================================
def build_speak_double_bark(act):
    # Keyframes for snappy double bark (Bark 1 at f12, Bark 2 at f24)
    kfs = [
        # (frame, chest_rx, head_rx, jaw_rx, ear_rx, hop_z, tail_wag)
        (1,   0.0,   0.0,   0.0,   0.0,  0.000,  0.0),
        (8,   6.0,   8.0,   0.0, -12.0, -0.018, -12.0), # Anticipation crouch (pitch slightly down)
        (12, -10.0, -16.0,  28.0,  12.0,  0.032,  22.0), # ARF 1! (Chest puff up, head toss up, jaw open!)
        (17, -2.0,  -2.0,   4.0,   0.0,  0.000, -15.0), # Recoil between barks
        (20,  4.0,   6.0,   2.0,  -8.0, -0.012,  10.0), # Second anticipation
        (24, -12.0, -20.0,  32.0,  14.0,  0.038, -24.0), # ARF 2!
        (31, -3.0,  -4.0,   6.0,   4.0,  0.000,  14.0), # Settle
        (40,  0.0,   0.0,   0.0,   0.0,  0.000,   0.0),
    ]
    for f, crx, hrx, jrx, erx, hz, tw in kfs:
        scene.frame_set(f)
        reset_pose()
        set_bone_world("Hips",  (-crx * 0.4, 0.0, 0.0), world_loc=(0.0, 0.0, hz))
        set_bone_world("Chest", (crx, 0.0, 0.0))
        set_bone_world("Neck",  (crx * 0.5, 0.0, 0.0))
        set_bone_world("Head",  (hrx, 0.0, 0.0))
        set_bone_world("Jaw",   (jrx, 0.0, 0.0))
        set_bone("Tongue", loc=(0.0, -0.012 if jrx > 15 else 0.0, 0.0))
        set_bone_world("Ear.L", (erx, 0.0, 0.0))
        set_bone_world("Ear.R", (erx, 0.0, 0.0))
        set_bone("Brow.L", loc=(0.0, 0.0, 0.006 if jrx > 15 else 0.0))
        set_bone("Brow.R", loc=(0.0, 0.0, 0.006 if jrx > 15 else 0.0))
        for side in ("L", "R"):
            set_bone_world(f"Leg_Front_Upper.{side}", (crx * 0.8, 0.0, 0.0))
            set_bone_world(f"Leg_Front_Lower.{side}", (-crx * 0.8, 0.0, 0.0))
        set_bone_world("Tail_Base", (-12.0 if jrx > 15 else 0.0, tw, tw * 0.6))
        key_all_bones(f)

anim_specs.append(("Speak_Double_Bark", 40, build_speak_double_bark, False))

# ==============================================================================
# 6. Give_Paw_Trick (Frames 1..48, 2.0s Interaction)
#    Sits and lifts right front white-tipped paw up high to shake hands!
# ==============================================================================
def build_give_paw_trick(act):
    for f in range(1, 49, 4):
        scene.frame_set(f)
        apply_sit_base_pose()
        t = (f - 1) / 47.0
        if t < 0.25:
            lift = math.sin((t / 0.25) * (math.pi / 2.0))
        elif t > 0.78:
            lift = math.cos(((t - 0.78) / 0.22) * (math.pi / 2.0))
        else:
            lift = 1.0
        wave = math.sin(t * 4.0 * math.pi) * lift

        set_bone_world("Head", (-6.0 * lift, 10.0 * lift, 6.0 * lift))
        set_bone_world("Jaw",  (12.0 * lift, 0.0, 0.0))
        # Raise Right Front Leg high forward + gentle paw wave
        set_bone("Leg_Front_Upper.R", loc=(0.0, -0.02, -0.04), rot_deg=(-72.0 * lift + 8.0 * wave, 0.0, -8.0 * lift))
        set_bone("Leg_Front_Lower.R", rot_deg=(28.0 * lift - 12.0 * wave, 0.0, 0.0))
        set_bone("Paw_Front.R",       rot_deg=(25.0 * lift + 15.0 * wave, 0.0, 0.0))
        set_bone_world("Tail_Base",   (-8.0, 20.0 * wave, 14.0 * wave))
        key_all_bones(f)

anim_specs.append(("Give_Paw_Trick", 48, build_give_paw_trick, False))

# ==============================================================================
# 7. Play_Bow_Excited (Frames 1..48, 2.0s Fetch Ready Pose)
#    Drops front elbows & forearms flat to the ground, rear hips high in the air, wagging!
# ==============================================================================
def build_play_bow_excited(act):
    for f in range(1, 49, 4):
        scene.frame_set(f)
        reset_pose()
        t = (f - 1) / 47.0
        bow = math.sin(min(1.0, t * 4.0) * (math.pi / 2.0)) if t < 0.8 else math.cos((t - 0.8) / 0.2 * (math.pi / 2.0))
        wag = math.sin(t * 8.0 * math.pi) * bow
        bounce = abs(math.sin(t * 4.0 * math.pi)) * bow

        # Rear hips stay high while spine/chest pitch downward (+rx) so shoulders drop low!
        set_bone_world("Hips",  (24.0 * bow, 0.0, 0.0), world_loc=(0.0, 0.04 * bow, -0.01 * bow + 0.015 * bounce))
        set_bone_world("Spine", (14.0 * bow, 0.0, 5.0 * wag))
        set_bone_world("Chest", (12.0 * bow, 0.0, 0.0))
        set_bone_world("Neck",  (-28.0 * bow, 0.0, 0.0))
        set_bone_world("Head",  (-24.0 * bow - 6.0 * bounce, 6.0 * wag, 4.0 * wag))
        set_bone_world("Jaw",   (18.0 * bow + 8.0 * bounce, 0.0, 0.0))
        set_bone("Tongue", loc=(0.0, -0.015 * bow, 0.0))

        for side, sx in [("L", 1.0), ("R", -1.0)]:
            # Front legs stretched forward with elbows & forearms resting flat on the floor (Z = 0.02)!
            set_bone_world(f"Leg_Front_Upper.{side}", (-82.0 * bow, sx * -6.0 * bow, 0.0))
            set_bone_world(f"Leg_Front_Lower.{side}", (-48.0 * bow, 0.0, 0.0))
            set_bone_world(f"Paw_Front.{side}",       (65.0 * bow, 0.0, 0.0))
            # Back legs standing tall
            set_bone_world(f"Leg_Back_Upper.{side}",  (-24.0 * bow, 0.0, 0.0))
            set_bone_world(f"Leg_Back_Lower.{side}",  (6.0 * bow, 0.0, 0.0))
            set_bone_world(f"Paw_Back.{side}",        (-6.0 * bow, 0.0, 0.0))

        set_bone_world("Tail_Base", (-18.0 * bow, 28.0 * wag, 22.0 * wag))
        set_bone_world("Tail_Mid",  (0.0, 22.0 * wag, 14.0 * wag))
        key_all_bones(f)

anim_specs.append(("Play_Bow_Excited", 48, build_play_bow_excited, True))

# ==============================================================================
# 8. Pickup_Drop_Ball (Frames 1..36, 1.5s Fetch Grab/Drop)
#    Bends front legs and pitches chest/neck forward to pick up ball at ground level!
# ==============================================================================
def build_pickup_drop_ball(act):
    kfs = [
        # (frame, reach_env, jaw_rx, lift_env)
        (1,  0.0,  0.0, 0.0),
        (10, 0.9, 30.0, 0.0), # Reach down & open jaw wide over ball
        (15, 1.0, 14.0, 0.0), # Clamp jaw onto ball near ground!
        (25, 0.0, 14.0, 1.0), # Proudly lift head up holding ball
        (36, 0.0,  0.0, 0.0),
    ]
    for f, r_env, jrx, l_env in kfs:
        scene.frame_set(f)
        reset_pose()
        set_bone_world("Hips",  (10.0 * r_env - 4.0 * l_env, 0.0, 0.0), world_loc=(0.0, 0.0, 0.02 * r_env + 0.015 * l_env))
        set_bone_world("Spine", (12.0 * r_env - 4.0 * l_env, 0.0, 0.0))
        set_bone_world("Chest", (10.0 * r_env - 4.0 * l_env, 0.0, 0.0))
        set_bone_world("Neck",  (24.0 * r_env - 10.0 * l_env, 0.0, 0.0))
        set_bone_world("Head",  (2.0 * r_env - 12.0 * l_env, 0.0, 0.0))
        set_bone_world("Jaw",   (jrx, 0.0, 0.0))
        for side in ("L", "R"):
            set_bone_world(f"Leg_Front_Upper.{side}", (18.0 * r_env + 4.0 * l_env, 0.0, 0.0))
            set_bone_world(f"Leg_Front_Lower.{side}", (-78.0 * r_env - 4.0 * l_env, 0.0, 0.0))
            set_bone_world(f"Paw_Front.{side}",       (28.0 * r_env, 0.0, 0.0))
            set_bone_world(f"Leg_Back_Upper.{side}",  (-10.0 * r_env, 0.0, 0.0))
            set_bone_world(f"Leg_Back_Lower.{side}",  (4.0 * r_env, 0.0, 0.0))
            set_bone_world(f"Paw_Back.{side}",        (-4.0 * r_env, 0.0, 0.0))
        set_bone_world("Tail_Base", (-12.0, 18.0 * l_env, 12.0 * l_env))
        key_all_bones(f)

anim_specs.append(("Pickup_Drop_Ball", 36, build_pickup_drop_ball, False))

# ==============================================================================
# 9. Walk_Jaunty_Trot (Frames 1..24, 1.0s Diagonal 4-Legged Trot Loop)
#    Anatomically accurate canine diagonal trot:
#    - Pair 1 (Front.L + Back.R) vs Pair 2 (Front.R + Back.L)
#    - rx < 0 swings upper leg FORWARD (-Y); rx > 0 swings upper leg BACKWARD (+Y)
#    - During lift phase (c > 0), lower leg flexes backward (+rx) to clear the ground cleanly!
# ==============================================================================
def build_walk_jaunty_trot(act):
    for f in range(1, 25, 2):
        scene.frame_set(f)
        reset_pose()
        phase = ((f - 1) / 24.0) * 2.0 * math.pi
        s1 = math.sin(phase)
        c1 = math.cos(phase)
        s2 = math.sin(phase + math.pi)
        c2 = math.cos(phase + math.pi)
        bob = abs(math.sin(phase))

        set_bone_world("Hips",  (2.5 * s1, 3.5 * s1, 0.0), world_loc=(0.0, 0.0, 0.020 * bob))
        set_bone_world("Spine", (-1.5 * bob, 0.0, 2.5 * s1))
        set_bone_world("Chest", (-2.5 * s1, -3.5 * s1, 0.0))
        set_bone_world("Neck",  (-3.0 * bob, 0.0, 0.0))
        set_bone_world("Head",  (-4.0 * bob, 3.0 * s1, 3.0 * s1))
        set_bone_world("Jaw",   (10.0 + 3.0 * bob, 0.0, 0.0))
        set_bone("Tongue", loc=(0.0, -0.010, 0.0))
        set_bone_world("Ear.L", (-6.0 * bob, 0.0, 0.0))
        set_bone_world("Ear.R", (-6.0 * bob, 0.0, 0.0))
        set_bone_world("Tail_Base", (-8.0 - 6.0 * bob, 16.0 * s1, 12.0 * s1))
        set_bone_world("Tail_Mid",  (0.0, 14.0 * s1, 8.0 * s1))

        # Diagonal Pair 1: Front Left & Back Right
        # When s1 > 0, leg swings FORWARD (rx = -22 * s1); when c1 > 0 (mid-swing lift), lower leg flexes (+26 * c1)
        set_bone_world("Leg_Front_Upper.L", (-22.0 * s1, 0.0, 0.0))
        set_bone_world("Leg_Front_Lower.L", (26.0 * max(0.0, c1) + 6.0 * max(0.0, -s1), 0.0, 0.0))
        set_bone_world("Paw_Front.L",       (12.0 * s1 - 16.0 * max(0.0, c1), 0.0, 0.0))

        set_bone_world("Leg_Back_Upper.R",  (-22.0 * s1, 0.0, 0.0))
        set_bone_world("Leg_Back_Lower.R",  (24.0 * max(0.0, c1) + 8.0 * max(0.0, s1), 0.0, 0.0))
        set_bone_world("Paw_Back.R",        (10.0 * s1 - 14.0 * max(0.0, c1), 0.0, 0.0))

        # Diagonal Pair 2: Front Right & Back Left
        set_bone_world("Leg_Front_Upper.R", (-22.0 * s2, 0.0, 0.0))
        set_bone_world("Leg_Front_Lower.R", (26.0 * max(0.0, c2) + 6.0 * max(0.0, -s2), 0.0, 0.0))
        set_bone_world("Paw_Front.R",       (12.0 * s2 - 16.0 * max(0.0, c2), 0.0, 0.0))

        set_bone_world("Leg_Back_Upper.L",  (-22.0 * s2, 0.0, 0.0))
        set_bone_world("Leg_Back_Lower.L",  (24.0 * max(0.0, c2) + 8.0 * max(0.0, s2), 0.0, 0.0))
        set_bone_world("Paw_Back.L",        (10.0 * s2 - 14.0 * max(0.0, c2), 0.0, 0.0))

        key_all_bones(f)

anim_specs.append(("Walk_Jaunty_Trot", 24, build_walk_jaunty_trot, True))

# ==============================================================================
# 10. Run_Fetch_Gallop (Frames 1..18, 0.75s Fast Bouncy Gallop Loop)
#      Bounding canine gallop with clean clearance between front and back legs!
# ==============================================================================
def build_run_fetch_gallop(act):
    for f in range(1, 19, 2):
        scene.frame_set(f)
        reset_pose()
        phase = ((f - 1) / 18.0) * 2.0 * math.pi
        s = math.sin(phase)
        c = math.cos(phase)

        # Spine flexes and extends dynamically during gallop:
        # When s > 0 (extended reach): Front legs reach forward (-rx), Back legs push backward (+rx)
        # When s < 0 (gathered suspension): Front legs swing back (+20 deg max), Back legs swing forward (-20 deg max)
        set_bone_world("Hips",  (10.0 * s, 0.0, 0.0), world_loc=(0.0, 0.0, 0.045 * c + 0.015))
        set_bone_world("Spine", (-10.0 * c, 0.0, 0.0))
        set_bone_world("Chest", (-8.0 * s, 0.0, 0.0))
        set_bone_world("Neck",  (6.0 * s, 0.0, 0.0))
        set_bone_world("Head",  (-8.0 * s, 0.0, 0.0))
        set_bone_world("Jaw",   (16.0 + 6.0 * s, 0.0, 0.0))
        set_bone("Tongue", loc=(0.0, -0.016, 0.0))
        set_bone_world("Ear.L", (-20.0 - 8.0 * s, 0.0, 0.0))
        set_bone_world("Ear.R", (-20.0 - 8.0 * s, 0.0, 0.0))
        set_bone_world("Tail_Base", (14.0 - 12.0 * c, 0.0, 0.0))

        for side, offset in [("L", 0.0), ("R", 0.35)]:
            sf = math.sin(phase + offset)
            cf = math.cos(phase + offset)
            sb = math.sin(phase + offset)
            cb = math.cos(phase + offset)

            # Front leg: reaches far forward (-34 deg) when sf > 0, swings moderately back (+20 deg) when sf < 0
            f_upper_rx = -34.0 * sf if sf > 0 else -20.0 * sf
            f_lower_rx = 36.0 * max(0.0, cf) + 12.0 * max(0.0, -sf)
            set_bone_world(f"Leg_Front_Upper.{side}", (f_upper_rx, 0.0, 0.0))
            set_bone_world(f"Leg_Front_Lower.{side}", (f_lower_rx, 0.0, 0.0))
            set_bone_world(f"Paw_Front.{side}",       (14.0 * sf - 18.0 * max(0.0, cf), 0.0, 0.0))

            # Back leg: pushes far backward (+34 deg) when sb > 0, gathers moderately forward (-20 deg) when sb < 0
            b_upper_rx = 34.0 * sb if sb > 0 else 20.0 * sb
            b_lower_rx = 32.0 * max(0.0, -cb) + 10.0 * max(0.0, -sb)
            set_bone_world(f"Leg_Back_Upper.{side}",  (b_upper_rx, 0.0, 0.0))
            set_bone_world(f"Leg_Back_Lower.{side}",  (b_lower_rx, 0.0, 0.0))
            set_bone_world(f"Paw_Back.{side}",        (-16.0 * sb, 0.0, 0.0))

        key_all_bones(f)

anim_specs.append(("Run_Fetch_Gallop", 18, build_run_fetch_gallop, True))

# ==============================================================================
# 11. Play_Chomp_Spray (Frames 1..48, 2.0s Power-Wash Spray Chomp!)
#     Rears up playfully and snaps/chomps jaw left & right at water mist!
# ==============================================================================
def build_play_chomp_spray(act):
    for f in range(1, 49, 3):
        scene.frame_set(f)
        reset_pose()
        t = (f - 1) / 47.0
        hop = math.sin(t * math.pi)
        chomp = abs(math.sin(t * 6.0 * math.pi)) * hop # 3 big water chomps in mid-air!
        look_lr = math.sin(t * 4.0 * math.pi) * hop

        set_bone_world("Hips",  (-28.0 * hop, 0.0, 0.0), world_loc=(0.0, 0.02 * hop, 0.06 * hop))
        set_bone_world("Spine", (-8.0 * hop, 0.0, 0.0))
        set_bone_world("Chest", (-8.0 * hop, 0.0, 0.0))
        set_bone_world("Neck",  (10.0 * hop, 0.0, 0.0))
        set_bone_world("Head",  (8.0 * hop, 14.0 * look_lr, 14.0 * look_lr))
        set_bone_world("Jaw",   (32.0 * chomp, 0.0, 0.0))
        set_bone("Tongue", loc=(0.0, -0.015 * chomp, 0.0))
        set_bone_world("Ear.L", (-14.0 * hop, 12.0 * chomp, 0.0))
        set_bone_world("Ear.R", (-14.0 * hop, -12.0 * chomp, 0.0))

        for side, sx in [("L", 1.0), ("R", -1.0)]:
            set_bone_world(f"Leg_Front_Upper.{side}", (-35.0 * hop + sx * 14.0 * look_lr, sx * -10.0 * hop, 0.0))
            set_bone_world(f"Leg_Front_Lower.{side}", (48.0 * hop, 0.0, 0.0))
            set_bone_world(f"Paw_Front.{side}",       (20.0 * hop, 0.0, 0.0))
            set_bone_world(f"Leg_Back_Upper.{side}",  (24.0 * hop, 0.0, 0.0))
            set_bone_world(f"Leg_Back_Lower.{side}",  (12.0 * hop, 0.0, 0.0))
            set_bone_world(f"Paw_Back.{side}",        (-12.0 * hop, 0.0, 0.0))

        set_bone_world("Tail_Base", (-10.0, 24.0 * look_lr, 16.0 * look_lr))
        key_all_bones(f)

anim_specs.append(("Play_Chomp_Spray", 48, build_play_chomp_spray, False))

# ==============================================================================
# 12. Shake_Off_Water (Frames 1..48, 2.0s Full-Body Ripple Shake!)
#     Phase-delayed high-frequency axial roll around World Y from Head -> Tail!
# ==============================================================================
def build_shake_off_water(act):
    for f in range(1, 49, 2):
        scene.frame_set(f)
        reset_pose()
        t = (f - 1) / 47.0
        env = math.sin(t * math.pi)
        freq = t * 14.0 * math.pi # 7 rapid full-body shakes

        w_head  = math.sin(freq) * env
        w_neck  = math.sin(freq - 0.5) * env
        w_chest = math.sin(freq - 1.0) * env
        w_hips  = math.sin(freq - 1.6) * env
        w_tail  = math.sin(freq - 2.2) * env

        # Wide stance crouch while twisting axially around World Y (`ry`)
        set_bone_world("Hips",  (0.0, 18.0 * w_hips, 5.0 * w_hips), world_loc=(0.0, 0.0, -0.025 * env))
        set_bone_world("Spine", (4.0 * env, 20.0 * w_chest, 0.0))
        set_bone_world("Chest", (6.0 * env, 22.0 * w_chest, 6.0 * w_chest))
        set_bone_world("Neck",  (10.0 * env, 20.0 * w_neck, 8.0 * w_neck))
        set_bone_world("Head",  (8.0 * env, 26.0 * w_head, 12.0 * w_head))
        set_bone_world("Ear.L", (-10.0 * env, 32.0 * w_head, 18.0 * w_head))
        set_bone_world("Ear.R", (-10.0 * env, 32.0 * w_head, 18.0 * w_head))
        set_bone("Eyelid.L", loc=(0.0, -0.003 * env, -0.013 * env))
        set_bone("Eyelid.R", loc=(0.0, -0.003 * env, -0.013 * env))
        set_bone_world("Jaw",   (10.0 * env, 8.0 * w_head, 0.0))

        for side, sx in [("L", 1.0), ("R", -1.0)]:
            set_bone_world(f"Leg_Front_Upper.{side}", (-8.0 * env, sx * -8.0 * env, 0.0))
            set_bone_world(f"Leg_Front_Lower.{side}", (14.0 * env, 0.0, 0.0))
            set_bone_world(f"Leg_Back_Upper.{side}",  (-8.0 * env, sx * -8.0 * env, 0.0))
            set_bone_world(f"Leg_Back_Lower.{side}",  (14.0 * env, 0.0, 0.0))

        set_bone_world("Tail_Base", (0.0, 32.0 * w_tail, 22.0 * w_tail))
        set_bone_world("Tail_Mid",  (0.0, 26.0 * w_tail, 16.0 * w_tail))
        key_all_bones(f)

anim_specs.append(("Shake_Off_Water", 48, build_shake_off_water, False))

# ==============================================================================
# 13. Scratch_Ear_Itch (Frames 1..54, 2.25s Sitting Hind-Leg Ear Scratch)
#     Leans head down & right while Right Hind Leg reaches FORWARD (-rx) and
#     OUTWARD (-X via rz = -22) so Paw_Back.R scratches right outside the cheek/ear!
# ==============================================================================
def build_scratch_ear_itch(act):
    for f in range(1, 55, 3):
        scene.frame_set(f)
        apply_sit_base_pose()
        t = (f - 1) / 53.0
        env = math.sin(min(1.0, t * 4.0) * (math.pi / 2.0)) if t < 0.8 else math.cos((t - 0.8) / 0.2 * (math.pi / 2.0))
        scratch = math.sin(t * 14.0 * math.pi) * env # Rapid hind-paw thumping behind right ear!

        set_bone_world("Spine", (20.0 - 4.0 * env, -4.0 * env, -3.0 * env))
        set_bone_world("Chest", (18.0 - 6.0 * env, -5.0 * env, -4.0 * env))
        set_bone_world("Neck",  (4.0 - 12.0 * env, -10.0 * env, -6.0 * env))
        set_bone_world("Head",  (-4.0 - 2.0 * env + 4.0 * scratch, -16.0 * env, -8.0 * env))
        set_bone_world("Ear.R", (12.0 * env + 10.0 * scratch, -26.0 * env, 0.0))
        set_bone("Eyelid.R", loc=(0.0, -0.003 * env, -0.014 * env))
        set_bone_world("Jaw",   (12.0 * env + 6.0 * abs(scratch), 0.0, 0.0))

        # Interpolate Right Hind Leg from sitting pose (+76, -112, +74) to forward outward ear-scratch pose
        u_rx = (1.0 - env) * 76.0  + env * (-82.0 + 12.0 * scratch)
        l_rx = (1.0 - env) * (-112.0) + env * (-12.0 - 18.0 * scratch)
        p_rx = (1.0 - env) * 74.0  + env * (-15.0 + 16.0 * scratch)
        set_bone_world("Leg_Back_Upper.R", (u_rx, 18.0 * env, -22.0 * env))
        set_bone_world("Leg_Back_Lower.R", (l_rx, 0.0, 0.0))
        set_bone_world("Paw_Back.R",       (p_rx, 0.0, 0.0))
        key_all_bones(f)

anim_specs.append(("Scratch_Ear_Itch", 54, build_scratch_ear_itch, False))

# ==============================================================================
# 14. Sniff_Find_Dirt (Frames 1..60, 2.5s Sniffing Ground & Pointing at Dirt!)
# ==============================================================================
def build_sniff_find_dirt(act):
    for f in range(1, 61, 4):
        scene.frame_set(f)
        reset_pose()
        t = (f - 1) / 59.0
        # First 65%: nose low to ground sweeping left-right sniffing; Last 35%: alert point with front paw!
        if t < 0.65:
            st = t / 0.65
            env = math.sin(min(1.0, st * 3.0) * (math.pi / 2.0)) if st < 0.8 else math.cos((st - 0.8) / 0.2 * (math.pi / 2.0))
            sweep = math.sin(st * 4.0 * math.pi) * env
            sniff_bob = abs(math.sin(st * 10.0 * math.pi)) * env

            set_bone_world("Hips",  (10.0 * env, 0.0, 0.0), world_loc=(0.0, 0.0, 0.02 * env))
            set_bone_world("Spine", (10.0 * env, 0.0, 4.0 * sweep))
            set_bone_world("Chest", (10.0 * env, 0.0, 4.0 * sweep))
            set_bone_world("Neck",  (22.0 * env, 8.0 * sweep, 10.0 * sweep))
            set_bone_world("Head",  (4.0 * env + 4.0 * sniff_bob, 10.0 * sweep, 14.0 * sweep))
            set_bone_world("Ear.L", (10.0 * env, 0.0, 0.0))
            set_bone_world("Ear.R", (10.0 * env, 0.0, 0.0))
            for side in ("L", "R"):
                set_bone_world(f"Leg_Front_Upper.{side}", (16.0 * env, 0.0, 0.0))
                set_bone_world(f"Leg_Front_Lower.{side}", (-72.0 * env, 0.0, 0.0))
                set_bone_world(f"Paw_Front.{side}",       (26.0 * env, 0.0, 0.0))
                set_bone_world(f"Leg_Back_Upper.{side}",  (-10.0 * env, 0.0, 0.0))
                set_bone_world(f"Leg_Back_Lower.{side}",  (4.0 * env, 0.0, 0.0))
                set_bone_world(f"Paw_Back.{side}",        (-4.0 * env, 0.0, 0.0))
            set_bone_world("Tail_Base", (-10.0, 18.0 * sweep, 12.0 * sweep))
        else:
            pt = (t - 0.65) / 0.35
            alert = math.sin(pt * math.pi)
            # Alert pointer stance: head proud, ears perked, front left paw raised pointing at dirt!
            set_bone_world("Head",  (-8.0 * alert, 0.0, 0.0))
            set_bone_world("Ear.L", (10.0 * alert, 0.0, 0.0))
            set_bone_world("Ear.R", (10.0 * alert, 0.0, 0.0))
            set_bone_world("Leg_Front_Upper.L", (-42.0 * alert, 0.0, 0.0))
            set_bone_world("Leg_Front_Lower.L", (64.0 * alert, 0.0, 0.0))
            set_bone_world("Paw_Front.L",       (28.0 * alert, 0.0, 0.0))
            set_bone_world("Tail_Base",         (-16.0 * alert, 0.0, 0.0))
        key_all_bones(f)

anim_specs.append(("Sniff_Find_Dirt", 60, build_sniff_find_dirt, False))

# ==============================================================================
# 15. Sleep_Curl_Nap (Frames 1..84, 3.5s Cozy Sleeping Loop)
#     Lies flat on belly with all 4 legs folded naturally on the floor, head curled!
# ==============================================================================
def build_sleep_curl_nap(act):
    for f in range(1, 85, 6):
        scene.frame_set(f)
        reset_pose()
        t = (f - 1) / 83.0
        breath = math.sin(t * 2.0 * math.pi)
        ear_twitch = 1.0 if f in (31, 37) else 0.0

        set_bone_world("Hips",  (0.0, 0.0, 6.0), world_loc=(0.0, 0.0, -0.27))
        set_bone_world("Spine", (2.0 + 2.0 * breath, 0.0, 8.0))
        set_bone_world("Chest", (4.0 + 2.5 * breath, 0.0, 8.0))
        set_bone_world("Neck",  (24.0, 6.0, 14.0))
        set_bone_world("Head",  (14.0 + 2.0 * breath, 8.0, 16.0))
        set_bone("Eyelid.L", loc=(0.0, -0.003, -0.014), rot_deg=(24.0, 0.0, 0.0))
        set_bone("Eyelid.R", loc=(0.0, -0.003, -0.014), rot_deg=(24.0, 0.0, 0.0))
        set_bone_world("Ear.L", (-12.0 + 14.0 * ear_twitch, 12.0, 0.0))
        set_bone_world("Ear.R", (-12.0, -12.0, 0.0))

        for side, sx in [("L", 1.0), ("R", -1.0)]:
            set_bone_world(f"Leg_Front_Upper.{side}", (-72.0, 0.0, 0.0))
            set_bone_world(f"Leg_Front_Lower.{side}", (-12.0, 0.0, 0.0))
            set_bone_world(f"Paw_Front.{side}",       (55.0, 0.0, 0.0))

            set_bone_world(f"Leg_Back_Upper.{side}",  (-72.0, sx * -10.0, 0.0))
            set_bone_world(f"Leg_Back_Lower.{side}",  (-14.0, 0.0, 0.0))
            set_bone_world(f"Paw_Back.{side}",        (55.0, 0.0, 0.0))

        set_bone_world("Tail_Base", (10.0, 22.0, 26.0))
        set_bone_world("Tail_Mid",  (0.0, 18.0, 16.0))
        key_all_bones(f)

anim_specs.append(("Sleep_Curl_Nap", 84, build_sleep_curl_nap, True))

# ==============================================================================
# BUILD ALL 15 ACTIONS & PUSH TO NLA TRACKS
# ==============================================================================
nla_cursor = 1
for act_name, f_end, builder_fn, is_loop in anim_specs:
    act = bpy.data.actions.new(name=act_name)
    act.use_fake_user = True
    arm_obj.animation_data.action = act
    builder_fn(act)
    set_linear_or_bezier(act, cyclic=is_loop)

    # Create non-overlapping NLA track for game engine exporters (FBX / glTF / USD)
    track = arm_obj.animation_data.nla_tracks.new()
    track.name = act_name
    strip = track.strips.new(name=act_name, start=nla_cursor, action=act)
    strip.action_frame_start = 1
    strip.action_frame_end = f_end
    track.mute = True # Muted during interactive viewport preview so active action plays cleanly
    nla_cursor += f_end + 10

# Set default active Action to `Idle_Sit_Smile` (Matching the reference image!)
sit_act = bpy.data.actions.get("Idle_Sit_Smile")
arm_obj.animation_data.action = sit_act
if sit_act and len(sit_act.slots) > 0:
    arm_obj.animation_data.action_slot = sit_act.slots[0]
scene.frame_start = 1
scene.frame_end = 72
scene.frame_set(18) # Frame 18 has the exact cute reference head-tilt & smile!

# ==============================================================================
# REGISTER 1-CLICK BLENDER VIEWPORT HEADER & SIDEBAR UI BUTTONS FOR ALL 15 ANIMS
# ==============================================================================
ANIM_FRAME_RANGES = {name: f_end for name, f_end, _, _ in anim_specs}

class SHIBA_OT_play_anim(bpy.types.Operator):
    bl_idname = "shiba.play_anim"
    bl_label = "Play Shiba Animation"
    anim_name: bpy.props.StringProperty()

    def execute(self, context):
        rig = bpy.data.objects.get("Shiba_Rig")
        act = bpy.data.actions.get(self.anim_name)
        if rig and act:
            if not rig.animation_data:
                rig.animation_data_create()
            for tr in rig.animation_data.nla_tracks:
                tr.mute = True
            rig.animation_data.action = act
            if len(act.slots) > 0:
                rig.animation_data.action_slot = act.slots[0]
            f_end = ANIM_FRAME_RANGES.get(self.anim_name, 60)
            context.scene.frame_start = 1
            context.scene.frame_end = f_end
            context.scene.frame_set(1)
            if not context.screen.is_animation_playing:
                bpy.ops.screen.animation_play()
        return {'FINISHED'}

class SHIBA_PT_anim_panel(bpy.types.Panel):
    bl_label = "Shiba Inu Animations (15)"
    bl_idname = "SHIBA_PT_anim_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Shiba Inu'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Click to Play Animation:", icon='PLAY')
        for name, f_end, _, _ in anim_specs:
            op = layout.operator("shiba.play_anim", text=f"{name} ({f_end}f)", icon='ACTION')
            op.anim_name = name

def draw_shiba_header(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.label(text="Shiba:", icon='OUTLINER_OB_ARMATURE')
    for name, _, _, _ in anim_specs[:8]:
        op = row.operator("shiba.play_anim", text=name.replace("_", " "))
        op.anim_name = name

try:
    bpy.utils.register_class(SHIBA_OT_play_anim)
    bpy.utils.register_class(SHIBA_PT_anim_panel)
    bpy.types.VIEW3D_HT_header.append(draw_shiba_header)
except Exception as e:
    print("UI registration note:", e)

bpy.context.view_layer.update()
print("All 15 Shiba Inu animations rebuilt with world-to-local kinematics & set to Idle_Sit_Smile!")
