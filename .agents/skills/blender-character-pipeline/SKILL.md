---
name: blender-character-pipeline
description: >-
  End-to-end workflow for modeling, shading, rigging, animating, previewing, and
  exporting stylized 3D game characters in Blender 5.x via MCP (mcp-for-blender).
  Use whenever asked to create, refine, rig, animate, match a reference image, or
  export a 3D character or creature in Blender.
---

# Blender Stylized Character Pipeline (Model → Rig → Animate → Export)

## Overview
Provides a production-tested workflow and reusable geometry/shader/animation helpers for building stylized 3D characters in Blender 5.x via `mcp-for-blender` (TCP port `9876` or MCP tools), preventing common pitfalls in shader color space, surface feather/scale orientation, layering bleed-through, Blender 5.0+ Slotted Actions, and multi-format exports.

## Workflow

### 1. Scope & Reference Decomposition
- **Strict Scene Hygiene:** Create only `<Character>_Rig` and `<Character>_Mesh` inside a dedicated collection. Never add unrequested pedestals, puddles, or ground planes.
- **Coordinate Blueprint:** Map reference proportions (`Z` heights, `Y` front-to-back depth, `X` widths) and distinct color/material zones before generating geometry.

### 2. Rig-First Modularity
- Create `<Character>_Rig` in rest pose first (`Root`, `Hips`, `Spine`, `Chest`, `Neck`, `Head`, facial bones, limbs, tail).
- When rebuilding or refining `<Character>_Mesh`, always switch `arm_data.pose_position = 'REST'` before generating BMesh geometry and restore `pose_position` afterward so existing animations remain intact.

### 3. Scene-Linear Stylized Shaders
- **Mandatory sRGB-to-Linear Conversion:** Blender shader node color sockets expect **Scene-Linear RGB**. Convert all sRGB colors picked from reference images using:
  ```python
  def srgb_to_linear(c):
      def ch(x):
          return x / 12.92 if x <= 0.04045 else pow((x + 0.055) / 1.055, 2.4)
      return (ch(c[0]), ch(c[1]), ch(c[2]), c[3] if len(c) > 3 else 1.0)
  ```
- Combine `ShaderNodeTexCoord (Object)` -> `ShaderNodeTexNoise` -> `ShaderNodeValToRGB` -> `Principled BSDF Base Color` + `ShaderNodeBump` for a subtle hand-painted brush finish.

### 4. Procedural BMesh Lofting & Vector-Oriented Shingles
- **Lofted Spline Tubes (`add_lofted_path`):** Build organic trunks, necks, beaks, wattles, limbs, and flat-bladed tail ribbons using multi-ring lofted spline paths with per-ring `(rx, ry)` radii and per-ring `material_index`.
- **Orthonormal Vector Frames (`make_frame_from_dir_and_normal`):** Never orient feathers, scales, or plates around curved surfaces using Euler angles. Always construct a `3x3` rotation matrix from `tip_dir` (`+Z` length axis) and `face_normal` (`+Y` outward normal):
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
- **Layering Offsets:**
  - Recess inner core meshes (`torso`, `wing_core`) by `0.015–0.025 m` under multi-row shingle feathers so the core never pokes through.
  - Step outer rows progressively outward along the surface normal and fan feathers across a 2D area (`fy`, `fz`).
  - Place lower-zone shingle feathers *below* the fringe line of overlapping upper capes/manes.
- **Deterministic Skinning:** Assign exact vertex weights directly to `bm.verts.layers.deform.verify()` as each BMesh element is created.

### 5. Blender 5.0+ Slotted Actions, NLA & 1-Click Viewport Playback UI
- **Keyframing:** Set `arm_obj.animation_data.action = action` and `bpy.context.scene.frame_set(frame)` *before* setting pose bone transforms and calling `pb.keyframe_insert(...)`.
- **Blender 5.0+ FCurves:** Access FCurves via `action.layers -> layer.strips -> strip.channelbags -> bag.fcurves`.
- **1-Click Viewport UI:** Register a custom playback operator and draw 1-click animation buttons in `VIEW3D_HT_header` that mute conflicting NLA tracks, set `arm_obj.animation_data.action` (and `action_slot`), set `scene.frame_start` / `scene.frame_end`, and call `bpy.ops.screen.animation_play()`.

### 6. Visual QA & Multi-Format Export
- **Viewport Screenshot Protocol:** Always set `r3d.view_perspective = 'PERSP'` and call `r3d.update()` inside `execute_code` before calling `get_viewport_screenshot`. Verify at least 2 angles (front-right 3/4 and rear-left 3/4) with `view_file`.
- **Multi-Format Export:** Select only `<Character>_Rig` and `<Character>_Mesh` (`use_selection=True`) and export to `.blend`, `.glb`, `.gltf`, `.fbx`, `.usdc`, `.abc`, `.obj`, `.ply`, and `.stl`, plus a complete `README.md`.

## Common Mistakes
1. **Passing sRGB directly to Principled BSDF:** Results in washed-out pastel colors. Always use `srgb_to_linear()`.
2. **Using Euler angles for feathers on curved bodies:** Causes side feathers to twist `90°` edge-on. Always use `make_frame_from_dir_and_normal(tip_dir, face_normal)`.
3. **Backslashes in Windows file paths sent over JSON:** `'C:\argon'` turns `\a` into ASCII `0x07`. Always use forward slashes `'C:/argon/...'`.
