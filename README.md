# Cozy Power-Wash Rooster — 3D Character Asset Package

A stylized, hand-painted-look **Rooster** 3D character asset designed, modeled, rigged, shaded, and animated in **Blender 5.2** for a **Cozy Power-Wash Game**.

---

## 1. Exported Files in `C:\3dassets\argon`

| File | Format | Size | Rigged | Animated | Materials | Best Used For |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `cozy_powerwash_rooster.blend` | **Blender 5.2 Native** | ~718 KB | Yes | Yes (7 Actions + NLA) | Yes (14 Procedural Node Shaders) | Master source file, editing geometry, tweaking animations, re-exporting |
| `cozy_powerwash_rooster.glb` | **glTF 2.0 Binary** | ~1.25 MB | Yes | Yes (All 7 Clips) | Yes | **Godot 4, Three.js, Babylon.js, Unreal Engine 5, Unity (glTFast), WebGL** |
| `cozy_powerwash_rooster.gltf` + `.bin` | **glTF 2.0 Separate** | ~1.31 MB | Yes | Yes (All 7 Clips) | Yes | Inspectable JSON glTF pipelines & custom engine importers |
| `cozy_powerwash_rooster.fbx` | **Autodesk FBX** | ~1.80 MB | Yes | Yes (Baked Actions + NLA) | Yes | **Unity, Unreal Engine 5, Maya, 3ds Max, Houdini** |
| `cozy_powerwash_rooster.usdc` | **Universal Scene Description (USD)** | ~1.09 MB | Yes | Yes | Yes | **NVIDIA Omniverse, Unreal Engine 5 Stage, Apple Reality Composer, Solaris** |
| `cozy_powerwash_rooster.abc` | **Alembic Cache** | ~25.7 MB | Vertex Cache | Yes (Frames 1–80) | Material Slots | VFX vertex-cache playback, Cinema 4D, Houdini, Katana |
| `cozy_powerwash_rooster.obj` + `.mtl` | **Wavefront OBJ + MTL** | ~1.70 MB | Static | Static | Yes | Static prop placement, ZBrush, Substance Painter, Marmoset Toolbag |
| `cozy_powerwash_rooster.ply` | **Stanford PLY** | ~2.58 MB | Static | Static | Normals + UVs | Point-cloud/mesh inspection, academic/procedural pipelines |
| `cozy_powerwash_rooster.stl` | **Stereolithography STL** | ~1.61 MB | Static | Static | Geometry Only | 3D printing, collision hull generation, static mesh slicing |

---

## 2. Geometry & Topology Specifications

- **Object Name:** `Rooster_Mesh`
- **Collection:** `Cozy_Rooster`
- **Vertex Count:** `16,774` vertices
- **Polygon / Face Count:** `18,828` faces (quad-dominant lofted feather cards, body tubes, and anatomical meshes)
- **Scale & Orientation:**
  - Real-world stylized game proportions (~`1.10 m` tall from toe to comb tips, ~`0.95 m` nose-to-tail).
  - Centered at world origin `(0, 0, 0)` with feet planted on `Z = 0.0`.
  - Forward Axis: `-Y` (Blender standard) | Up Axis: `+Z`.
- **Anatomical & Stylized Features:**
  - **Plump Deep-Breasted Body:** Deep indigo-navy blue puffed chest, keel, and lower belly with 3 rows of overlapping breast shingle feathers.
  - **7-Tier Fiery Hackle Cape:** 102 individually oriented overlapping shingle feathers cascading from crimson-red at the nape through fiery orange to a jagged bright golden-orange pointed fringe overlapping the blue breast.
  - **7-Row Scalloped Saddle & Rump Plumage:** 73 overlapping red-orange scalloped feathers blanketing the upper back, saddle, and rear flanks down to the tail base.
  - **3-Tone Layered Scalloped Wings (Left & Right):**
    - *Row 1 (Shoulder Bow):* 6 deep indigo-navy covert feathers per wing.
    - *Rows 2 & 3 (Middle Coverts):* 12 ruby-crimson scalloped covert feathers per wing.
    - *Row 4 (Primaries):* 5 fiery orange-red flight feathers tipped with bright golden-yellow per wing.
  - **Faceted Sickle Ribbon Tail:** 12 indigo-navy tail-base tuft feathers supporting 6 wide, flat-bladed arched sickle tail ribbons transitioning from indigo base -> crimson arch -> glowing orange-gold tips.
  - **Expressive Head:**
    - 8-point serrated crimson crown comb.
    - Large white sclera eyes with centered dark pupils, framed by a pinkish-red eye ring.
    - Iconic curved white crescent cheek/ear lobe hugging below and behind each eye.
    - Hooked golden-yellow upper and lower beak (separately rigged for crowing/pecking).
    - Plump twin crimson-rose wattles beneath the chin.
  - **Chunky Legs & Double Spurs:** Indigo-navy feathered drumsticks leading into scaly tan-gold shins with **two rear spurs per leg** and 4-toed feet (3 front toes + 1 rear hallux).

---

## 3. Material & Shader Slots (14 Materials)

All materials use **Principled BSDF** shaders with procedural **Noise -> ColorRamp -> Bump** brush-stroke variation for a rich, hand-painted stylized finish (with scene-linear sRGB color conversion):

| Slot | Material Name | Visual Area | Color Palette (sRGB Hex) | Roughness |
| :---: | :--- | :--- | :--- | :---: |
| `0` | `Mat_Indigo_Body` | Breast, belly, drumsticks, wing shoulder bow, tail base tuft | `#18347B` → `#2E5CC5` | `0.58` |
| `1` | `Mat_Red_Plumage` | Upper head, upper neck hackles, upper back & saddle base | `#BA2418` → `#DF3B22` | `0.54` |
| `2` | `Mat_Orange_Plumage` | Mid-lower hackle cape, saddle tips, wing primary bases | `#DC4818` → `#F6741D` | `0.52` |
| `3` | `Mat_Gold_Tips` | Lower hackle jagged fringe, wing primary tips, sickle tail tips | `#EE6D19` → `#FFA424` | `0.50` |
| `4` | `Mat_Wing_Crimson` | Middle 2 rows of scalloped wing covert feathers | `#A61322` → `#DC2834` | `0.52` |
| `5` | `Mat_Tail_Crimson` | Arching sickle tail ribbon blades | `#9A141E` → `#D42A2A` | `0.52` |
| `6` | `Mat_Comb_Red` | 8-point serrated crown comb | `#C8222B` → `#EB3A3E` | `0.42` |
| `7` | `Mat_Wattle_Rose` | Twin hanging chin wattles | `#AE223B` → `#D83B52` | `0.44` |
| `8` | `Mat_Eye_Ring` | Fleshy pinkish-red ring around the eye | `#DA485A` → `#F06474` | `0.48` |
| `9` | `Mat_Cheek_White` | Curved white crescent cheek/ear lobe | `#D5DAE8` → `#F8FAFF` | `0.45` |
| `10` | `Mat_Eye_Sclera` | Large round white eyeball | `#E2E6F0` → `#FFFFFF` | `0.15` |
| `11` | `Mat_Eye_Pupil` | Glossy dark pupil | `#0D0F18` → `#1B1F2E` | `0.08` |
| `12` | `Mat_Beak_Gold` | Hooked upper and lower beak | `#D59222` → `#F7BA38` | `0.38` |
| `13` | `Mat_Leg_Tan` | Scaly shins, double rear spurs, and 4 toes | `#B48448` → `#D8A866` | `0.58` |

---

## 4. Rig / Armature Hierarchy (`Rooster_Rig` — 28 Bones)

The character is bound via smooth procedural weight groups to `Rooster_Rig` (`Rooster_Rig_Data`):

```text
Root
 ├── Hips
 │    ├── Spine
 │    │    └── Chest
 │    │         ├── Neck_Base
 │    │         │    └── Neck_Top
 │    │         │         └── Head
 │    │         │              ├── Beak_Upper
 │    │         │              ├── Beak_Lower
 │    │         │              ├── Comb
 │    │         │              └── Wattle
 │    │         ├── Wing_Shoulder.L  ──> Wing_Mid.L  ──> Wing_Tip.L
 │    │         └── Wing_Shoulder.R  ──> Wing_Mid.R  ──> Wing_Tip.R
 │    ├── Tail_Base
 │    │    └── Tail_Mid
 │    │         ├── Tail_Tip
 │    │         ├── Tail_Fan.L
 │    │         └── Tail_Fan.R
 │    ├── Thigh.L  ──> Shin.L  ──> Foot.L  ──> Toes.L
 │    └── Thigh.R  ──> Shin.R  ──> Foot.R  ──> Toes.R
```

---

## 5. Included Animations (7 Game-Ready Actions @ 24 FPS)

All 7 animations are stored both as individual **Actions** (`bpy.data.actions`) and as non-overlapping **NLA Tracks** on `Rooster_Rig`:

| # | Action Name | Frame Range | Duration (@ 24 FPS) | Loopable | Cozy Power-Wash Gameplay Behavior |
| :-: | :--- | :---: | :---: | :---: | :--- |
| **1** | `Idle_LookAround` | `1 – 80` | **3.33 sec** | Yes | Breathing chest puff, curious quick chicken head tilts, beak nibble, and gentle tail sway while standing around the yard. |
| **2** | `Peck_Scratch` | `1 – 70` | **2.92 sec** | Yes | Dips forward for rapid ground pecks (`Beak_Upper`/`Beak_Lower` open/close), then scratches the dirt twice with its left foot (`Thigh.L`/`Shin.L`/`Foot.L`). |
| **3** | `Walk_Strut` | `1 – 32` | **1.33 sec** | Yes | Classic proud rooster strut with rhythmic front-to-back head-bobbing, high-stepping legs, toe curl, and side-to-side tail swagger. |
| **4** | `Startled_Hop` | `1 – 36` | **1.50 sec** | One-Shot | **Triggered when hit by the power-washer spray!** Jumps straight up in surprise, flares both wings wide open, splays toes in mid-air, and lands with a squash-and-stretch bounce. |
| **5** | `Shake_Off_Water` | `1 – 50` | **2.08 sec** | One-Shot | **Played after getting soaked!** Crouches slightly and rapidly vibrates/shakes head, wattles, comb, wings, and tail out of phase to fling water droplets off its feathers. |
| **6** | `Run_Flee` | `1 – 16` | **0.67 sec** | Yes | Fast comedic panic sprint away from the player's water stream — neck stretched forward, wings held up and fluttering, rapid leg cycle. |
| **7** | `Happy_Crow` | `1 – 75` | **3.13 sec** | One-Shot | **Played when the yard/coop is 100% sparkling clean!** Deep chest inhale, arches back proudly, opens beak wide (`Rooster-doodle-doo!`), and flaps wings in celebration. |

---

## 6. How to Preview Animations in Blender

When you open `cozy_powerwash_rooster.blend` in Blender:
1. **Top 3D Viewport Header Bar:** Look at the top bar of the 3D Viewport (or the Sidebar `N` -> `Rooster` tab) to find the **7 one-click animation buttons** (`Idle_LookAround`, `Peck_Scratch`, `Walk_Strut`, `Startled_Hop`, `Shake_Off_Water`, `Run_Flee`, `Happy_Crow`).
2. Clicking any button automatically:
   - Unmutes/activates that animation Action on `Rooster_Rig`,
   - Sets the scene's `frame_start` and `frame_end` to match that exact clip's length, and
   - Starts real-time playback in the 3D Viewport (`Spacebar` to pause/resume).
