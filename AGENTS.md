# Workspace Rules — 3D Character Modeling, Rigging, Animation & Export in Blender

When creating, refining, rigging, shading, animating, or exporting 3D models in Blender via MCP (`mcp-for-blender` / TCP port `9876` or native Blender MCP tools), always follow these engineering rules learned from production workflows:

## 1. Scope & Scene Hygiene
- **Build Only What Was Requested:** Never add unrequested environment props (e.g., pedestals, puddles, ground planes) unless explicitly asked. Keep the collection strictly to `<Character>_Rig` and `<Character>_Mesh`.
- **Forward Slashes in Paths:** Inside Python scripts sent over JSON/TCP to Blender, always use forward slashes (`'C:/3dassets/argon/...'` or `'C:/argon/...'`) so sequences like `\a` or `\t` are never interpreted as control characters.

## 2. Scene-Linear Color Conversion for Blender Shaders
- Blender's `Principled BSDF` and `ColorRamp` sockets expect **Scene-Linear RGB**, whereas hex codes and reference image color pickers are **sRGB**.
- Passing raw sRGB floats directly makes colors look washed-out and pastel. Always convert sRGB to Scene-Linear RGB in shader generation scripts:
  ```python
  def srgb_to_linear(c):
      def ch(x):
          return x / 12.92 if x <= 0.04045 else pow((x + 0.055) / 1.055, 2.4)
      return (ch(c[0]), ch(c[1]), ch(c[2]), c[3] if len(c) > 3 else 1.0)
  ```

## 3. Procedural BMesh Geometry & Layering
- **Avoid Raw Blockout Primitives:** Do not rely on basic scaled spheres/cones (`create_uvsphere`, `create_cone`) for organic characters. Instead:
  - Use **multi-ring lofted spline paths** (`add_lofted_path`) with per-ring `(rx, ry)` radii and per-ring `material_index` assignments for organic trunks, necks, beaks, wattles, limbs, and ribbon tails.
  - Layer **individual 3D shingle feathers/scales** (`add_feather_oriented`) with arched midribs (`rachis`), cupped cross-sections, and two-tone base/tip material indices.
- **Vector-Frame Orientation (Never Guess Euler Angles on Curved Surfaces):**
  - Never use Euler `(rx, ry, rz)` guesses to orient feathers, scales, or plates around a curved body (which causes side elements to twist `90°` edge-on).
  - Always construct an orthonormal `3x3` rotation matrix from two explicit vectors: `tip_dir` (`+Z` length direction) and `face_normal` (`+Y` outward surface normal):
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
- **Strict Layering Offsets (No Inner Core Bleed-Through):**
  - Recess underlying core meshes (`torso`, `wing_core`) by `0.015–0.025 m` wherever multi-row shingle feathers sit on top.
  - Step each overlapping feather tier outward along the surface normal and fan feathers across a 2D area (`fy` and `fz`) rather than stacking along a single line.
  - When an upper cape/mane (e.g., neck hackle fringe) overlaps a lower zone (e.g., chest feathers), start the lower zone's shingle feathers *below* the upper fringe line so lower feathers never poke through on top.

## 4. Rig-First Modularity & Deterministic Skinning
- **Rest-Pose Rebuilds:** Always switch `arm_data.pose_position = 'REST'` before rebuilding or updating `<Character>_Mesh`, and restore `pose_position` afterward so existing rig animations are preserved seamlessly.
- **Procedural BMesh Deform Weights:** Assign exact vertex weights directly to `bm.verts.layers.deform.verify()` as each geometry component is generated rather than relying solely on automatic heat-map weights. This prevents cross-bleeding between wings and torso or upper and lower jaws/beaks.

## 5. Blender 5.0+ Slotted Actions, NLA & 1-Click Viewport UI
- **Keyframing in Blender 5.2:** Always assign `arm_obj.animation_data.action = action` and call `bpy.context.scene.frame_set(frame)` *before* setting pose bone transforms and calling `pb.keyframe_insert(...)`. When iterating FCurves in Blender 5.0+, traverse `action.layers -> layer.strips -> strip.channelbags -> bag.fcurves`.
- **1-Click Viewport Animation Buttons:** Register a lightweight operator and draw 1-click playback buttons in `VIEW3D_HT_header` that mute conflicting NLA tracks, set the active `Action` (and `action_slot`), set `scene.frame_start` / `scene.frame_end` to match that clip, and start playback (`bpy.ops.screen.animation_play()`).

## 6. Multi-Angle Visual QA & Multi-Format Export
- **Viewport Screenshot Protocol:** Before capturing a viewport screenshot via `get_viewport_screenshot`, always set `r3d.view_perspective = 'PERSP'` and call `r3d.update()` inside `execute_code`. Always verify at least two 3/4 angles (front-right 3/4 and rear-left 3/4) with `view_file`.
- **Clean Selection on Export:** Deselect all scene objects, select only `<Character>_Rig` and `<Character>_Mesh`, and export with `use_selection=True` across `.blend`, `.glb`, `.gltf`, `.fbx`, `.usdc`, `.abc`, `.obj`, `.ply`, and `.stl`, accompanied by a detailed `README.md`.
