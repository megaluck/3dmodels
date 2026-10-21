# Table Tennis (Ping Pong) Mini-Game — 16 Rigged 3D Assets (`C:/argon/table_tennis`)

Complete playable **Table Tennis (Ping Pong) Mini-Game Suite** for **Player vs. NPC**, **Solo Practice (Robot Ball Launcher & Folding Playback Wall)**, and **Trick-Shot Target Drills**, exported across all 9 formats (`.blend`, `.glb`, `.gltf`, `.fbx`, `.obj`, `.stl`, `.ply`, `.usdc`, `.abc`) in `C:/argon/table_tennis/` and `C:/3dassets/argon/table_tennis/`.

---

## 1. Complete 16-Asset Catalog

| # | Asset Name | Category | Dimensions (`W × D × H`) | Rig & Key Bones | Baked Gameplay Actions (`24 fps`) | Gameplay Sockets (`Empty`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `cozy_tt_table_indoor_pro` | Tournament Table | `1.525 × 2.740 × 0.760 m` (`1.83 m` w/ net posts) | `Root`, `Undercarriage`, `Leaf_South`, `Leg_Outer_South`, `Leaf_North`, `Leg_Outer_North`, `Net_Posts`, `Net_Center_Bend` | `Table_Match_Ready_Idle`, `Table_Net_Cord_Let_Jiggle`, `Table_Solo_Playback_Wall_Fold` (`90°` solo wall), `Table_Storage_Fold_Both` | `Serve_Spot_Player`, `Serve_Spot_NPC`, `Bounce_Zone_South_L/R`, `Bounce_Zone_North_L/R`, `Net_Top_Center`, `Robot_Mount_North`, `Paddle_Rest_South/North`, `NPC_Baseline_Center` |
| 2 | `cozy_tt_table_outdoor_garden` | Garden Park Table | `1.525 × 2.740 × 0.760 m` | Same bone hierarchy as `indoor_pro` | `Table_Match_Ready_Idle`, `Table_Net_Cord_Let_Jiggle`, `Table_Solo_Playback_Wall_Fold`, `Table_Storage_Fold_Both` | Same 11 sockets as `indoor_pro` |
| 3 | `cozy_tt_paddle_classic` | Club Paddle | `0.152 × 0.024 × 0.258 m` | `Root`, `Wrist_Pivot`, `Blade_Flex` | `Paddle_Idle_Twirl`, `Paddle_Forehand_Topspin_Drive`, `Paddle_Backhand_Flick`, `Paddle_Chop_Defense` | `Grab_Handle` (`0,0,0`), `SweetSpot_Forehand` (`0, -0.006, 0.125`), `SweetSpot_Backhand` (`0, +0.006, 0.125`) |
| 4 | `cozy_tt_paddle_carbon_pro` | Pro Spin Paddle | `0.152 × 0.024 × 0.258 m` | `Root`, `Wrist_Pivot`, `Blade_Flex` | `Paddle_Idle_Twirl`, `Paddle_Forehand_Topspin_Drive`, `Paddle_Backhand_Flick`, `Paddle_Chop_Defense` | `Grab_Handle`, `SweetSpot_Forehand`, `SweetSpot_Backhand` |
| 5 | `cozy_tt_paddle_cast_iron_pan` | Challenge Skillet Paddle | `0.172 × 0.028 × 0.268 m` | `Root`, `Wrist_Pivot`, `Blade_Flex` | `Paddle_Idle_Twirl`, `Paddle_Forehand_Topspin_Drive`, `Paddle_Backhand_Flick`, `Paddle_Chop_Defense` | `Grab_Handle`, `SweetSpot_Forehand`, `SweetSpot_Backhand` |
| 6 | `cozy_tt_ball_white_3star` | 3-Star White Ball | `Ø 0.040 m` (`40 mm`) | `Root`, `Ball_Squash`, `Ball_Spin` | `Ball_Topspin_Loop`, `Ball_Bounce_Squash`, `Ball_Serve_Toss` | `Ball_Center` (`0,0,0.020`), `Ball_Bottom_Contact` (`0,0,0`) |
| 7 | `cozy_tt_ball_orange_3star` | 3-Star Orange Ball | `Ø 0.040 m` (`40 mm`) | `Root`, `Ball_Squash`, `Ball_Spin` | `Ball_Topspin_Loop`, `Ball_Bounce_Squash`, `Ball_Serve_Toss` | `Ball_Center`, `Ball_Bottom_Contact` |
| 8 | `cozy_tt_ball_twotone_spin` | Spin-Tracker Ball | `Ø 0.040 m` (`40 mm`) | `Root`, `Ball_Squash`, `Ball_Spin` | `Ball_Topspin_Loop`, `Ball_Bounce_Squash`, `Ball_Serve_Toss` | `Ball_Center`, `Ball_Bottom_Contact` |
| 9 | `cozy_tt_robot_launcher` | Ball Launcher Robot | `0.32 × 0.34 × 0.44 m` | `Root`, `Base_Pedestal`, `Hopper_Agitator`, `Head_Yaw`, `Head_Pitch`, `Wheel_Top`, `Wheel_Bottom` | `Robot_Idle_Scan`, `Robot_Oscillate_Sweep_Fire`, `Robot_Topspin_High_Pitch`, `Robot_Backspin_Low_Cut` | `Muzzle_Launch_Socket` (`0, -0.165, 0.360`), `Hopper_Top_Refill`, `Table_Clamp_Origin` |
| 10 | `cozy_tt_target_flip_bullseye` | Trick-Shot Target | `0.22 × 0.12 × 0.27 m` | `Root`, `Outer_Ring_Flip`, `Bullseye_Center_Spin`, `Flag_Popup` | `Target_Idle`, `Target_Hit_Spin_Flip`, `Target_Reset` | `Bullseye_Hit_Center` (`0, -0.012, 0.130`), `Target_Base_Origin` |
| 11 | `cozy_tt_target_cup_pyramid` | Knockdown Pyramid | `0.29 × 0.10 × 0.35 m` | `Root`, `Cup_01..05`, `Cup_06_Gold` | `Pyramid_Idle`, `Pyramid_Strike_Scatter`, `Pyramid_Stack_Reset` | `Pyramid_Center_Hit`, `Pyramid_Base_Origin` |
| 12 | `cozy_tt_scoreboard_flip` | Flip-Card Scoreboard | `0.48 × 0.17 × 0.24 m` | `Root`, `Flip_Point_Home`, `Flip_Point_Away`, `Flip_Set_Home`, `Flip_Set_Away` | `Score_Flip_Point_Home`, `Score_Flip_Point_Away`, `Score_Set_Win_Flip` | `Scoreboard_Base` |
| 13 | `cozy_tt_ball_hopper_caddy` | Multi-Ball Caddy | `0.38 × 0.38 × 0.82 m` | `Root`, `Caddy_Frame`, `Bag_Basket` | `Caddy_Idle`, `Caddy_Roll_And_Bounce` | `Ball_Grab_Top` (`0,0,0.82`), `Caddy_Floor_Origin` |
| 14 | `cozy_tt_paddle_rack_stand` | Club Paddle Stand | `0.56 × 0.28 × 1.11 m` | `Root`, `Stand_Frame`, `Towel_Sway` | `Stand_Towel_Breeze` | `Slot_Paddle_01..04` |
| 15 | `cozy_tt_barrier_surround` | Court Surround | `2.00 × 0.36 × 0.75 m` | `Root`, `Panel_Hit_Flex` | `Barrier_Ball_Impact_Flex` | `Barrier_Origin` |
| 16 | `cozy_tt_arena_showcase` | Full Arena Set | `3.10 × 4.75 × 1.15 m` | `Root`, `Table_Base`, `Net_Center_Bend`, `Paddle_Player_South`, `Paddle_NPC_North`, `Rally_Ball`, `Score_Flip_Card` | `Arena_Live_Rally_Loop` (`48` frames) | `Serve_Spot_Player`, `Serve_Spot_NPC`, `NPC_Baseline_Center`, `Player_Baseline_Center` |

---

## 2. Scene-Linear Material Palette (`22` Materials)

| Material Name | sRGB Hex | Role |
| :--- | :--- | :--- |
| `TT_Table_Blue` | `#1B4F9C` | Regulation matte anti-glare tournament blue playing surface |
| `TT_Table_Green` | `#1E563B` | Outdoor courtyard forest-green park playing surface |
| `TT_Line_White` | `#F7F9FC` | Crisp `20 mm` boundary lines, center doubles line, score digits |
| `TT_Steel_Dark` | `#22262E` | Powder-coated steel undercarriage, robot body, barrier frame |
| `TT_Chrome` | `#D8DEE6` | Caster wheel forks, rolling caddy frame, turret bearings |
| `TT_Brass` | `#D6A138` | Outdoor perforated net, butt-cap badges, bullseye target frame |
| `TT_Accent_Red` | `#C92A2A` | Folding safety struts, Away flip-cards, party cups, top flywheel |
| `TT_Net_Mesh` | `#EAECEF` | Tensioned `15.25 cm` tournament nylon net mesh |
| `TT_Navy_Fabric` | `#162A4A` | Net post clamps, court surround baffles, multi-ball canvas bag |
| `TT_Wood_Walnut` | `#6E4226` | Outdoor teak legs, paddle handles, scoreboard base, club stand |
| `TT_Wood_Beech` | `#D9A973` | 5-ply natural beechwood classic paddle blade |
| `TT_Rubber_Red` / `TT_Rubber_Black` | `#D1232A` / `#1C1E22` | Classic ITTF forehand/backhand sponge rubber |
| `TT_Carbon_Weave` | `#15171C` | Carbon-fiber pro blade & robot barrel housing |
| `TT_Rubber_Cyan` / `TT_Rubber_Magenta` | `#00A8E8` / `#E0218A` | High-tension pro spin sponge rubbers |
| `TT_Ball_White` / `TT_Ball_Orange` | `#FAF8F2` / `#FF7A18` | 3-Star `40 mm` tournament & spin-tracker balls |
| `TT_Acrylic_Clear` | `#DDF0FF` | Transparent robot ball hopper (`alpha = 0.38`) |
| `TT_Cast_Iron` | `#242528` | Seasoned cast-iron challenge skillet paddle |
| `TT_LED_Glow` | `#22FF88` | Robot muzzle pre-shot spin/fire indicator LED (`emission = 3.2`) |
| `TT_Towel_Cream` | `#F2EAD7` | Draped cotton sport towel on club paddle stand |

---

## 3. Rebuilding & Auditing From Source

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python "C:/argon/table_tennis/build_tt_tables_paddles_balls.py"
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python "C:/argon/table_tennis/build_tt_robot_targets_props_arena.py"
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python "C:/argon/table_tennis/verify_and_render_table_tennis.py"
```
