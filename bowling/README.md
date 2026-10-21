# Coral Lanes — 2-Lane Regulation 60-ft Mall Bowling Alley, 6 House Balls, Empty Tiered Rack, 1978 Space Invaders Arcade & 18 Decorations Pack (35 Models)

Complete **35-model 3D asset pack** (28 rigged & animated models with 65 verified animation clips + 6 USBC-sized individual House Balls `6–16 lb` + 1 Empty Tiered Ball Rack across `.blend`, `.fbx`, `.glb`, `.gltf`, `.obj`, `.stl`, `.ply`, `.usdc`, and `.abc`) built in Blender 5.2 (`C:/argon/bowling` and mirrored to `C:/3dassets/argon/bowling`) for the **Aquarium Mall (`atrium-tank`)** map in `C:/claude/vrcozy`.

---

## 1. Exact Aquarium Mall 3-Shop Dimensions & Regulation 60-ft (`18.288 m`) Lane Layout

From [`src/pw/world/atrium-tank.ts`](file:///C:/claude/vrcozy/src/pw/world/atrium-tank.ts) and [`src/pw/world/atrium-shops.ts`](file:///C:/claude/vrcozy/src/pw/world/atrium-shops.ts), the three adjacent ground-floor shops sit on the **North wall (`side = 0`, `level = 0`, `y = 0`, storefront plane at `z = -13.50 m`)**:

| Mall Slot | Original Shop | Kind | Center Along Wall (`x`) | Width (`SHOP.w`) | Mall `x` Span | Local Shell `X` Span (centered at `x = +2.75 m`) |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Bay 1 (Left)** | **The Golden Crust** | `bakery` | `-3.00 m` | `5.00 m` | `[-5.50, -0.50]` | `[-8.25, -3.25]` (center `-5.75 m`) |
| **Pier 1–2** | *Center Wall Pier* | `plaster` | `0.00 m` | `1.00 m` | `[-0.50, +0.50]` | `[-3.25, -2.25]` (center `-2.75 m`) |
| **Bay 2 (Center)** | **Sugarplum** | `sweets` | `+3.00 m` | `5.00 m` | `[+0.50, +5.50]` | `[-2.25, +2.75]` (center `+0.25 m`) |
| **Pier 2–3** | *East-Mid Wall Pier* | `plaster` | `+5.75 m` | `0.50 m` | `[+5.50, +6.00]` | `[+2.75, +3.25]` (center `+3.00 m`) |
| **Bay 3 (Right)** | **Tea for Two** | `tea` | `+8.50 m` | `5.00 m` | `[+6.00, +11.00]` | `[+3.25, +8.25]` (center `+5.75 m`) |

### USBC Regulation 60-ft (`18.288 m`) Specifications Kept in `cozy_bowling_lane`, `cozy_bowling_pinsetter`, and `cozy_bowling_mall_shell`
- **Foul Line to Head Pin (`Pin_Spot_1`):** **`60 ft 0 in = 18.288 m`** (`Y = 0.000 m` foul line to `Y = 18.288 m` head pin)
- **Foul Line to Back of Pin Deck (`Pin_Deck_End`):** **`62 ft 10 3/16 in = 19.156 m`** (`Pin_Spot_7..10` at `Y = 19.080 m`)
- **Lane Width:** **`41 1/2 in = 1.0541 m`** (39 maple boards × `27.028 mm`)
- **Gutters:** **`9 1/4 in = 0.235 m`** wide on each side (`1 7/8 in` deep)
- **Seven Aiming Chevrons:** Boards `5, 10, 15, 20, 25, 30, 35` at `12–16 ft` (`3.658–4.877 m`, center arrow at `Y = 4.267 m`)
- **10-Pin Equilateral Triangle:** **`12 in = 0.3048 m`** center-to-center spacing (`dY = 0.2640 m` row step, `dX = 0.1524 m` half-column step)
- **Pinsetter Kickbacks & Pit:** **`60 1/8 in = 1.527 m`** between kickback faces (`±0.7636 m`), `4 3/4 in` (`0.121 m`) pit drop, rear cushion face at `Y = +1.505 m` past head pin (`Y = 19.793 m` in lane space)
- **Shell Depth:** Storefront along `Y = -4.55 m` (marquee to `Y = -5.09 m`), interior back wall at `Y = +19.888 m` (exterior `Y = +20.088 m`, total depth `25.18 m`)

---

## 2. Six Individual House Balls (`6–16 lb`) & Empty Tiered Ball Rack (Assets 29–35)

Built by [`build_bowling_house_balls_and_rack.py`](file:///C:/argon/bowling/build_bowling_house_balls_and_rack.py) to the Coral Lanes House Balls specification. Every house ball shares the regulation **USBC diameter of `21.7 cm` (`0.217 m`, radius `R = 0.1085 m`)** centered at `(0, 0, 0)`, with **three real recessed cylindrical finger/thumb holes** (`6.0 cm` deep for fingers, `7.0 cm` deep for thumb, dark interior walls + bevel rim), an **inlaid front weight numeral (`6`, `8`, `10`, `12`, `14`, `16`)** beside the grip, and a **Coral Lanes starburst mark** on the back (`+Y`).

### 2.1 Six House Balls (`cozy_bowling_ball_06lb` .. `cozy_bowling_ball_16lb`)

| # | Asset Name | Weight & Grip Class | Triangles | Materials (Max 3) & Hex Colors | Socket Points (`Empty` Nodes) |
| :-: | :--- | :--- | :---: | :--- | :--- |
| **29** | `cozy_bowling_ball_06lb` | **6 lb** (Compact grip: `5.1 cm` span, `2.10 cm` fingers, `2.50 cm` thumb) | `468` | `Bowling_Ball_Lilac` (`#B79AD6`), `Bowling_Cream_Pearl` (`#FAF3E6`), `Bowling_Gold_Brass` (`#E5B53A`) | `Ball_Center` `(0, 0, 0)`, `Thumb_Hole` `(0.0000, -0.1082, -0.0082)`, `Finger_Hole_Middle` `(-0.0175, -0.0987, +0.0416)`, `Finger_Hole_Ring` `(+0.0175, -0.0987, +0.0416)` |
| **30** | `cozy_bowling_ball_08lb` | **8 lb** (Compact grip: `5.1 cm` span, `2.10 cm` fingers, `2.50 cm` thumb) | `478` | `Bowling_Coral_Pink` (`#F46C5B`), `Bowling_Cream_Pearl` (`#FAF3E6`), `Bowling_Gold_Brass` (`#E5B53A`) | `Ball_Center` `(0, 0, 0)`, `Thumb_Hole` `(0.0000, -0.1082, -0.0082)`, `Finger_Hole_Middle` `(-0.0175, -0.0987, +0.0416)`, `Finger_Hole_Ring` `(+0.0175, -0.0987, +0.0416)` |
| **31** | `cozy_bowling_ball_10lb` | **10 lb** (Compact grip: `5.1 cm` span, `2.10 cm` fingers, `2.50 cm` thumb) | `468` | `Bowling_Ball_Sunflower` (`#F2C138`), `Bowling_Cream_Pearl` (`#FAF3E6`), `Bowling_Gold_Brass` (`#E5B53A`) | `Ball_Center` `(0, 0, 0)`, `Thumb_Hole` `(0.0000, -0.1082, -0.0082)`, `Finger_Hole_Middle` `(-0.0175, -0.0987, +0.0416)`, `Finger_Hole_Ring` `(+0.0175, -0.0987, +0.0416)` |
| **32** | `cozy_bowling_ball_12lb` | **12 lb** (Adult grip: `5.8 cm` span, `2.36 cm` fingers, `2.76 cm` thumb) | `464` | `Bowling_Teal_Seafoam` (`#2AA89B`), `Bowling_Ball_Seafoam` (`#9FDCCF`), `Bowling_Gold_Brass` (`#E5B53A`) | `Ball_Center` `(0, 0, 0)`, `Thumb_Hole` `(0.0000, -0.1082, -0.0082)`, `Finger_Hole_Middle` `(-0.0195, -0.0956, +0.0474)`, `Finger_Hole_Ring` `(+0.0195, -0.0956, +0.0474)` |
| **33** | `cozy_bowling_ball_14lb` | **14 lb** (Adult grip: `5.8 cm` span, `2.36 cm` fingers, `2.76 cm` thumb) | `458` | `Bowling_Ball_Ocean` (`#2B5C9E`), `Bowling_Ball_Navy` (`#1C2F55`), `Bowling_Gold_Brass` (`#E5B53A`) | `Ball_Center` `(0, 0, 0)`, `Thumb_Hole` `(0.0000, -0.1082, -0.0082)`, `Finger_Hole_Middle` `(-0.0195, -0.0956, +0.0474)`, `Finger_Hole_Ring` `(+0.0195, -0.0956, +0.0474)` |
| **34** | `cozy_bowling_ball_16lb` | **16 lb** (Adult grip: `5.8 cm` span, `2.36 cm` fingers, `2.76 cm` thumb) | `474` | `Bowling_Obsidian_Ball` (`#1E222A`), `Bowling_Gold_Brass` (`#E5B53A`), `Bowling_Cream_Pearl` (`#FAF3E6`) | `Ball_Center` `(0, 0, 0)`, `Thumb_Hole` `(0.0000, -0.1082, -0.0082)`, `Finger_Hole_Middle` `(-0.0195, -0.0956, +0.0474)`, `Finger_Hole_Ring` `(+0.0195, -0.0956, +0.0474)` |

- **Hole Socket Orientation:** On all 6 balls, `Thumb_Hole`, `Finger_Hole_Middle`, and `Finger_Hole_Ring` sit on the outer sphere surface (`|p| = 0.1085 m`) at the mouth of each hole, and their **local `+Z` axis points radially inward** toward `Ball_Center (0, 0, 0)` (`dot(local_Z, -pos.normalized()) = 1.0000`).

### 2.2 Empty Tiered Ball Rack (`cozy_bowling_ball_rack_empty`)

| # | Asset Name | Type | Triangles | Materials (5) & Hex Colors | Socket Points (`Slot_Ball_1` .. `Slot_Ball_9`) |
| :-: | :--- | :--- | :---: | :--- | :--- |
| **35** | `cozy_bowling_ball_rack_empty` | Static Mesh + 9 Slot Empties (no baked balls, no clips, no `Grab_Top_Ball`) | `1,480` | `Bowling_Chrome_Steel` (`#D8E0E8`), `Bowling_Teal_Seafoam` (`#2AA89B`), `Bowling_Coral_Pink` (`#F46C5B`), `Bowling_Obsidian_Ball` (`#1E222A`), `Bowling_Gold_Brass` (`#E5B53A`) | **Top Tier (`Z = +0.9381 m`):** `Slot_Ball_1` `(-0.29, 0, +0.9381)`, `Slot_Ball_2` `(0.00, 0, +0.9381)`, `Slot_Ball_3` `(+0.29, 0, +0.9381)`<br>**Middle Tier (`Z = +0.5981 m`):** `Slot_Ball_4` `(-0.29, 0, +0.5981)`, `Slot_Ball_5` `(0.00, 0, +0.5981)`, `Slot_Ball_6` `(+0.29, 0, +0.5981)`<br>**Bottom Tier (`Z = +0.2581 m`):** `Slot_Ball_7` `(-0.29, 0, +0.2581)`, `Slot_Ball_8` `(0.00, 0, +0.2581)`, `Slot_Ball_9` `(+0.29, 0, +0.2581)` |

- **Clearance & Fit:** Each `Slot_Ball_1..9` point sits at the exact center of a `21.7 cm` house ball resting on the twin parallel chrome rails (`rail Z = 0.85, 0.51, 0.17 m`, `rail Y = ±0.064 m`, `ball center Z = rail_z + sqrt(0.1085² - 0.064²) = rail_z + 0.0881 m`), giving **`7.3 cm` horizontal gap** between adjacent balls and **`11.8 cm` vertical reach-in clearance** above every lower-tier ball.
- *(Note: The original animated `cozy_bowling_ball_rack_tiered` and `cozy_bowling_balls_pack` remain untouched in the pack.)*

---

## 3. Core Architecture, Lanes, Machines & Arcade (Assets 1–10)

| # | Asset Name | Rig | Baked Animations (`moving > 0` verified) | Key Socket Empties & `[0,1]` UV Screens |
| :-: | :--- | :--- | :--- | :--- |
| **1** | `cozy_bowling_mall_shell` | `Shell_Rig` | `Marquee_Idle_Bob`, `Entrance_Doors_Swing` | 25 placement `Empty` anchors for every interior zone & decoration |
| **2** | `cozy_bowling_lane` | `Lane_Rig` | `Bumpers_Pop_Up`, `Bumpers_Retract`, `Foul_Light_Flash` | `Foul_Line_Center`, `Arrow_Aim_Center`, `Pin_Deck_End`, `Pin_Spot_1`..`Pin_Spot_10` (`Pin_Spot_1` at `Y = 18.288 m`) |
| **3** | `cozy_bowling_pinsetter` | `Pinsetter_Rig` | `Pinsetter_Idle`, `Sweep_Rake_Drop_And_Clear`, `Spotter_Set_New_Pins`, `Pit_Curtain_Impact` | `Spotter_Center`, `Rake_Edge`, `Pit_Ball_Swallow`, `Cushion_Face` |
| **4** | `cozy_bowling_ball_return` | `BallReturn_Rig` | `Blower_Fan_Spin`, `Ball_Stopper_Bounce`, `Button_Reset_Press`, `Button_Bumper_Press` | `Ball_Eject_Point`, `Ball_Rack_Slot_1`..`Ball_Rack_Slot_6` |
| **5** | `cozy_bowling_overhead_scoreboard` | `Scoreboard_Rig` | `Scoreboard_Idle`, `Strike_Celebration_Spin`, `Gutter_Womp_Droop` | **Single-Quad `[0,1]` UVs:** `Bowling_Screen_L`, `Bowling_Screen_R` |
| **6** | `cozy_bowling_pins_pack` | `Pins_Rig` | `Pin_Idle_Wobble`, `Pin_Hit_Spin_Fly` | `Grab_Pin_Standard`, `Grab_Pin_Golden` |
| **7** | `cozy_bowling_balls_pack` | `Balls_Rig` | `Ball_Roll_Spin`, `Ball_Return_Pop_Up` | `Grip_Ball_Coral`, `Grip_Ball_Teal`, `Grip_Ball_Obsidian`, `Grip_Ball_Gold` |
| **8** | `cozy_bowling_lounge_booth` | `Lounge_Rig` | `Cushion_Sit_Squish`, `Table_Cup_Jiggle` | `Seat_1`..`Seat_4`, `Table_Center` |
| **9** | `cozy_bowling_shoe_counter` | `Counter_Rig` | `Service_Bell_Ring`, `Polisher_Spin_Buff`, `Shoes_Cubby_Rattle` | `Grab_Rental_Shoes`, `Bell_Hit`, `Polisher_Slot` |
| **10** | `cozy_bowling_arcade_space_invaders` | `Arcade_Rig` | `Arcade_Idle_Attract`, `Joystick_Move_L_R`, `Fire_Buttons_Mash`, `Coin_Insert_Clunk` | **Single-Quad `[0,1]` UV:** `Arcade_CRT_Screen`, `Player_Stand_Spot`, `Grab_Joystick`, `Hit_Fire_Btn`, `Coin_Slot` |

---

## 4. Decorative & Interactive Props (Assets 11–28)

| # | Asset Name | Rig | Zone Anchor in `Shell_Rig` | Baked Animations (`moving > 0` verified) | Key Socket Empties |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **11** | `cozy_bowling_trophy_case` | `TrophyCase_Rig` | `Trophy_Case_Origin` | `Case_Doors_Slide`, `Trophy_Sparkle_Spin` | `Trophy_Focus` |
| **12** | `cozy_bowling_ball_rack_tiered` | `BallRack_Rig` | `Ball_Rack_Origin` | `Balls_Rattle_Settle`, `Top_Ball_Lift_Inspect` | `Grab_Top_Ball` |
| **13** | `cozy_bowling_chalk_cone_pedestal` | `ChalkStand_Rig` | `Chalk_Pedestal_Origin` | `Chalk_Pat_Poof`, `Dryer_Button_Press` | `Touch_Chalk_Cone` |
| **14** | `cozy_bowling_leaderboard_chalkboard` | `Leaderboard_Rig` | `Leaderboard_Origin` | `New_High_Score_Flip`, `Crown_Badge_Pulse` | `Board_Center` |
| **15** | `cozy_bowling_lane_oiler_cart` | `OilerCart_Rig` | `Oiler_Cart_Origin` | `Cart_Roll_Condition`, `Cone_Tip_Wobble` | `Push_Grip` |
| **16** | `cozy_bowling_nachos_pizza_tray` | `SnackTray_Rig` | `Snack_Tray_Origin` | `Snack_Grab_Bounce`, `Cheese_Dip_Dunk` | `Grab_Pizza`, `Grab_Pretzel` |
| **17** | `cozy_bowling_popcorn_cart` | `Popcorn_Rig` | `Popcorn_Cart_Origin` | `Kettle_Dump_Pop`, `Crank_Spin_Loop` | `Serve_Popcorn` |
| **18** | `cozy_bowling_slushie_dispenser` | `Slushie_Rig` | `Slushie_Machine_Origin` | `Slushie_Augers_Spin`, `Tap_Pull_Pour` | `Cup_Fill_Spot_L`, `Cup_Fill_Spot_R` |
| **19** | `cozy_bowling_condiment_caddy` | `Caddy_Rig` | `Condiment_Caddy_Origin` | `Caddy_Shake_Jiggle`, `Squeeze_Bottles_Hop` | `Grab_Caddy` |
| **20** | `cozy_bowling_trash_ashtray_duo` | `TrashDuo_Rig` | `Trash_Duo_Origin` | `Trash_Flap_Swing`, `Bin_Kick_Wobble` | `Toss_Trash_Target` |
| **21** | `cozy_bowling_jukebox_bubbler` | `Jukebox_Rig` | `Jukebox_Origin` | `Jukebox_Play_Groove`, `Record_Change_Flip` | `Select_Song_Spot` |
| **22** | `cozy_bowling_bill_changer` | `Changer_Rig` | `Bill_Changer_Origin` | `Dispense_Quarters_Clatter`, `Out_Of_Order_Flip` | `Insert_Bill_Spot`, `Take_Quarters` |
| **23** | `cozy_bowling_gumball_tri_rack` | `Gumball_Rig` | `Gumball_Rack_Origin` | `Turn_Crank_Drop_Gumball`, `Globes_Jiggle_Shake` | `Turn_Gumball_Crank` |
| **24** | `cozy_bowling_arcade_stool_pair` | `Stools_Rig` | `Arcade_Stools_Origin` | `Stool_Spin_360`, `Stool_Sit_Bounce` | `Sit_Stool_1`, `Sit_Stool_2` |
| **25** | `cozy_bowling_neon_wall_signs` | `NeonSigns_Rig` | `Neon_Signs_Origin` | `Neon_Sign_Pulse_Tilt`, `Arrow_Chaser_Bounce` | `Neon_Center` |
| **26** | `cozy_bowling_sputnik_clock` | `Clock_Rig` | `Sputnik_Clock_Origin` | `Clock_Tick_Loop`, `Strike_Hour_Chime` | `Clock_Center` |
| **27** | `cozy_bowling_planter_divider` | `Planter_Rig` | `Planter_Divider_Origin` | `Leaves_Breeze_Sway`, `Plant_Touch_Rustle` | `Foliage_Center` |
| **28** | `cozy_bowling_window_display_podium` | `Podium_Rig` | `Window_Podium_Origin` | `Window_Turntable_Spin`, `Display_Pin_Salute` | `Grab_Retro_Bag` |
