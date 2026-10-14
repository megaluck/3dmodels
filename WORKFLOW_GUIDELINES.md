# Blender 3D Character Pipeline Guidelines: Idea → Model → Rig → Animation → Export

This guide documents the end-to-end workflow for building, rigging, shading, animating, and exporting stylized 3D game characters in **Blender 5.2 via MCP (`mcp-for-blender`)**, distilled from creating the **Cozy Power-Wash Rooster** asset. It specifically highlights **what went wrong in early iterations** and the **exact engineering rules** that solved every issue so future tasks get it right on the first pass.

---

## 1. End-to-End Workflow Architecture

```mermaid
flowchart LR
    A["1. Gameplay & Reference Analysis"] --> B["2. Armature & Joint Blueprint"]
    B --> C["3. Procedural BMesh + Explicit Orientation"]
    C --> D["4. Scene-Linear Stylized Shaders"]
    D --> E["5. Action + NLA + Viewport UI Controls"]
    E --> F["6. Multi-Angle Visual QA & Multi-Format Export"]
```

### Phase 1: Gameplay & Reference Analysis (Before Writing Code)
1. **Only Build What the User Asked For:**
   - *Early Mistake:* Adding unrequested environment props (`Cozy_Pedestal`, `Cozy_Puddle`) cluttered the scene and exported files.
   - *Rule:* Never add pedestals, ground planes, or extra props unless explicitly requested. Keep the scene collection strictly to `<Character>_Rig` and `<Character>_Mesh`.
2. **Deconstruct Reference Proportions & Color Zones First:**
   - Break the reference image into explicit coordinate zones (`Z` height ranges, `Y` front-to-back depth, `X` width) and list every distinct color/material zone before writing geometry code.

---

## 2. Early Mistakes vs. Proven Solutions (Lessons Learned)

### Mistake 1: Washed-Out / Pastel Colors in Blender Shaders
- **What Happened:** Passing standard sRGB values (e.g., `(0.86, 0.28, 0.09)` for fiery orange) directly into Blender's `Principled BSDF` or `ColorRamp` sockets produced pale, washed-out pastel colors in the viewport.
- **Why:** Blender's shader node color sockets operate in **Scene-Linear RGB**, whereas hex codes and color pickers from reference screenshots are in **sRGB**.
- **The Fix (Mandatory Helper):** Always convert sRGB tuples to Scene-Linear RGB before assigning them to any Blender node socket:
  ```python
  def srgb_to_linear(c):
      def ch(x):
          return x / 12.92 if x <= 0.04045 else pow((x + 0.055) / 1.055, 2.4)
      return (ch(c[0]), ch(c[1]), ch(c[2]), c[3] if len(c) > 3 else 1.0)
  ```

### Mistake 2: Too-Raw Blockout Primitives ("Balloon Animal" Look)
- **What Happened:** Our first iteration used basic scaled spheres and cones (`create_uvsphere`, `create_cone`), which looked like raw blockout primitives even for a stylized low-poly game.
- **The Fix:**
  - Use **multi-ring lofted spline tubes** (`add_lofted_path`) with varying `rx, ry` cross-sections and per-ring material indices for organic trunks, necks, beaks, wattles, legs, and ribbon tails.
  - Layer **hundreds of individual 3D shingle feathers/scales** (`add_feather_oriented`) with arched midribs (`rachis`), cupped cross-sections, and two-tone base/tip material assignments.

### Mistake 3: Euler Angle Twisting on Feathers, Scales, and Appendages
- **What Happened:** Orienting feathers around a curved body using Euler `(rx, ry, rz)` rotations caused side feathers to twist edge-on (`90°` off), leaving gaps and spiky silhouettes.
- **The Fix:** Never use Euler guesses to place surface details around a body. Always construct an **orthonormal basis matrix** directly from two explicit vectors:
  1. `tip_dir` (`+Z` local axis: direction the feather/scale points).
  2. `face_normal` (`+Y` local axis: outward surface normal of the body at that point).
  ```python
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
  ```

### Mistake 4: Inner Core Geometry Poking Through Layered Outer Feathers
- **What Happened:** When layering 3-tone wing covert feathers (`Indigo -> Crimson -> Orange-Gold`) or overlapping neck hackles over the chest, the underlying torso or `wing_core` mesh had a wider `X` radius than the feather bases, swallowing the feathers or poking through between rows.
- **The Fix (Strict Layering Offsets):**
  - Keep the underlying core mesh slightly recessed (`rx` smaller by `0.015–0.025 m`) where multi-row feathers sit on top.
  - Step each overlapping layer outward along the surface normal (e.g., `Row 1: x=0.180`, `Row 2: x=0.186`, `Row 3: x=0.188`) and stagger their vertical (`fz`) and longitudinal (`fy`) positions so they fan across a 2D area instead of stacking along a single line.
  - When a upper cape/mane (like the orange-gold hackle fringe) overlaps a lower zone (like the blue breast), start the lower zone's shingle feathers *below* the fringe line (`z <= 0.49`) so thelower feathers never poke out above the upper cape.

### Mistake 5: Blender 5.0+ Slotted Action API Breaking Classic FCurve Scripts
- **What Happened:** In Blender 5.0+, `action.fcurves.new()` was removed from `bpy.types.Action` in favor of the new **Slotted Actions / Channelbag** architecture (`action.layers` -> `action.strips` -> `strip.channelbag(slot)`), causing classic scripts to fail or only keyframe the last frame when using `keyframe_insert` improperly.
- **The Fix:**
  - Always set `arm_obj.animation_data.action = action` and `bpy.context.scene.frame_set(frame)` **before** setting pose bone transforms (`pb.location`, `pb.rotation_euler`) and calling `pb.keyframe_insert(data_path=..., frame=frame)`.
  - To inspect or set cyclic loop modifiers on FCurves in Blender 5.2, iterate through the channelbag:
    ```python
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fcu in bag.fcurves:
                    # modify fcu.keyframe_points or fcu.modifiers
    ```

### Mistake 6: NLA Track Stack Overriding Active Action Playback in the Viewport
- **What Happened:** Pushing all 7 animations onto NLA tracks (`arm_obj.animation_data.nla_tracks`) caused top tracks to override or blend with the active Action, making it hard for the user to preview individual animations in the viewport.
- **The Fix:**
  - Mute NLA tracks (`track.mute = True`) during interactive Action preview, or provide **1-click UI buttons right inside Blender's 3D Viewport Header (`VIEW3D_HT_header`)** that:
    1. Mute conflicting NLA tracks,
    2. Assign the chosen `bpy.data.actions[name]` to `arm_obj.animation_data.action` (and assign the action slot `arm_obj.animation_data.action_slot = action.slots[0]`),
    3. Set `scene.frame_start` and `scene.frame_end` to the exact frame range of that animation, and
    4. Trigger `bpy.ops.screen.animation_play()`.

### Mistake 7: Viewport Screenshots Not Updating Camera Angle or Corrupting Windows Paths
- **What Happened:**
  1. Changing `space.region_3d.view_rotation` without setting `r3d.view_perspective = 'PERSP'` and calling `r3d.update()` captured stale camera angles.
  2. Passing Windows paths with backslashes (`'C:\argon\...'`) inside Python strings sent over JSON interpreted `\a` as ASCII `0x07` (bell character).
- **The Fix:**
  - Always use forward slashes (`'C:/argon/...'` or `'C:/3dassets/argon/...'`) inside scripts sent to Blender.
  - Always call `r3d.view_perspective = 'PERSP'` and `r3d.update()` before calling `get_viewport_screenshot`, and inspect **at least 2 angles** (front-right 3/4 and rear-left 3/4) after every mesh update.

---

## 3. Reusable Checklist for Future Character Tasks

1. **Rig-First Modular Design:**
   - Build the `Armature` in rest pose first (`Root`, `Hips`, `Spine`, `Chest`, `Neck`, `Head`, facial bones, limbs, tail).
   - Store bone names and rest coordinates so the mesh generator can rebuild `Rooster_Mesh` in rest pose (`arm_data.pose_position = 'REST'`) at any time without breaking existing animations.
2. **Procedural Weight Assignment During BMesh Creation:**
   - Assign vertex weights via a custom `BMesh` deform layer (`bm.verts.layers.deform.verify()`) right as each body part or feather is created. This guarantees 100% clean, deterministic skinning (zero cross-bleeding between wings and torso, or between upper and lower beak) compared to automatic heat-map weights.
3. **Interactive Blender Viewport UI:**
   - Register a lightweight operator (`ROOSTER_OT_play_anim`) and draw 1-click animation buttons in `VIEW3D_HT_header` so the user can test every animation immediately without hunting through Blender's NLA or Dope Sheet editors.
4. **Multi-Format Export Verification:**
   - Select only the character rig and mesh (`use_selection=True`) and export to `.blend`, `.glb`, `.gltf`, `.fbx`, `.usdc`, `.abc`, `.obj`, `.ply`, and `.stl`, accompanied by a complete `README.md` documenting vertex counts, material slots, bone hierarchy, and animation frame tables.
