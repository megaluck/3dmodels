# Tabletop Marble Chess Set — Pedestal Table, 2 Round Drum Chairs, Analog Chess Clock & 12 Standalone Rigged Staunton Pieces (16 Models)

Complete **16-model rigged and animated 3D asset pack** (62 verified animation clips across `.blend`, `.fbx`, `.glb`, `.gltf`, `.obj`, `.stl`, `.ply`, `.usdc`, and `.abc`) built in Blender 5.2 (`C:/argon/chess_table` and mirrored to `C:/3dassets/argon/chess_table`) for **Player vs. NPC Tabletop Chess** in the **Chess Lawn (`chess-lawn`)** map of `C:/claude/vrcozy`.

---

## 1. Architectural Design & Tabletop Dimensions (Matching Reference Photo)

Modeled after the luxury outdoor Italian two-tone marble pedestal chess table (`il_1588xN.6916912488_oq7k.webp`):
- **Tabletop Surface Height (`TABLE_TOP_Z`):** **`0.740 m`** (`74.0 cm`)
- **Tabletop Total Footprint:** **`0.780 m × 0.780 m`** (`5.4 cm` thick chamfered **Carrara White Veined Marble** slab with a `13.0 cm` wide border around the playfield for captured pieces and the chess clock)
- **Inlaid 64-Square Playfield (`8 × 8`):** **`0.520 m × 0.520 m`** (`6.5 cm × 6.5 cm` per square with `1.4 mm` V-groove slate joints, framed by an inlaid **Gold Brass Pinstripe**)
  - **`Square_a1` (`(-0.2275, -0.2275, 0.740)`):** Dark (**Nero Marquina Black Veined Marble**), bottom-left from White's (`-Y`) perspective
  - **`Square_h1` (`(+0.2275, -0.2275, 0.740)`):** Light (**Carrara White Veined Marble**), bottom-right from White's (`-Y`) perspective ("white on right")
- **Two-Tone Architectural Pedestal Base:**
  - **Stepped White Veined Marble Plinth:** `0.540 m × 0.540 m` floor base (`Z = 0.000` to `0.058 m`)
  - **Four Square White Veined Marble Corner Pillars:** `0.110 m × 0.110 m` columns at `(±0.180, ±0.180) m` (`0.470 m` outer span)
  - **Four Recessed Polished Black Veined Marble Side Panels:** Set `2.8 cm` inside the white corner pillars with top/bottom gold brass trim bars
  - **Felt-Lined Slide-Out Storage Drawer (`Piece_Drawer` bone):** Built into the `+X` upper pedestal apron with a brass pull handle
- **Two Round Marble & Cushion Drum Chairs (`cozy_chess_round_chair`):**
  - **`0.424 m` diameter × `0.463 m` seat height**, placed at `Chair_White_Spot (0.000, -0.680, 0.000)` (Player / White side) and `Chair_Black_Spot (0.000, +0.680, 0.000)` (NPC / Black side, rotated `180°`)
  - Fluted **Carrara White Veined Marble** drum column with **8 vertical recessed Nero Marquina Black Marble flutes**, a **Gold Brass collar ring**, and a plump **tufted sage-cream garden cushion** with a central brass button tuft

---

## 2. Complete Asset Catalog (16 Models Across 9 Formats)

### 2.1 Table, Round Drum Chair, Analog Clock & Complete Assembled Station (Assets 1–4)

| # | Asset Name | Rig | Dimensions `(X, Y, Z)` | Baked Animations (`moving > 0` verified) | Gameplay Socket Empties (`Empty` Nodes) |
| :-: | :--- | :--- | :---: | :--- | :--- |
| **1** | `cozy_chess_marble_table` | `Table_Rig` | `0.780 × 0.780 × 0.740 m` | `Move_Guide_Pulse`, `Drawer_Slide_Open`, `Board_Reset_Sweep` | **`Square_a1`..`Square_h8` (64 sockets)**, **`Captured_W_01`..`16`**, **`Captured_B_01`..`16`**, `Clock_Spot`, `Chair_White_Spot`, `Chair_Black_Spot`, **`NPC_IK_Hand_Target`** (100 total empties) |
| **2** | `cozy_chess_round_chair` | `Chair_Rig` | `0.424 × 0.424 × 0.463 m` | `Chair_Sit_Cushion_Squish`, `Chair_Swivel_Idle`, `Chair_Slide_In_Out` | `Seat_Origin`, `NPC_Spine_Anchor`, `Foot_Rest_L`, `Foot_Rest_R`, `NPC_Hand_Rest_L`, `NPC_Hand_Rest_R` |
| **3** | `cozy_chess_clock_analog` | `Clock_Rig` | `0.176 × 0.064 × 0.102 m` | `Clock_Tick_Loop`, `Press_White_Turn`, `Press_Black_Turn`, `Flag_Fall_Time_Out` | `Clock_Base`, `Hit_Button_White`, `Hit_Button_Black` |
| **4** | `cozy_chess_station_set` | `Station_Rig` | `0.780 × 1.784 × 0.845 m` | `Station_Attract_Idle`, `Opening_Move_e2e4_e7e5_Demo`, `NPC_Knight_Develop_Demo` | `Player_White_Seat`, `NPC_Black_Seat`, `Board_Center`, `NPC_IK_Hand_Socket` |

### 2.2 Twelve Standalone Rigged Staunton Chess Pieces (Assets 5–16)

Every standalone piece (`cozy_chess_white_*` and `cozy_chess_black_*`) sits on an **octagonal marble plinth (`4.41 cm` diameter)** with a **felt base pad** (`#1F5C3A` green felt for White, `#7A2228` crimson felt for Black) and a **polished Gold Brass collar band** (`#D9A84E`). Each piece is rigged with a 3-bone armature (`Root` → `Body_Tilt` → `Crown_Accent`) and **4 baked gameplay clips**:
1. `Piece_Lift_Hop` (`36f`): Lifts `4.8 cm` into the air with a natural forward tilt when picked up, arcs, and settles cleanly.
2. `Piece_Slide_Place` (`30f`): Smooth tabletop slide-in and tactile rim rock when placed on a square.
3. `Piece_Capture_Tip_Fall` (`40f`): Struck by an opposing piece, rocks onto its base edge, and topples `90°` onto its side.
4. `King_Check_Shiver` (`36f`): Rapid nervous tremor when placed in check or threatened.

| # | Asset Name | Side & Piece | Height (`Z`) | Base Diameter | Materials (3) | Socket Empties (`Empty` Nodes) |
| :-: | :--- | :--- | :---: | :---: | :--- | :--- |
| **5** | `cozy_chess_white_king` | White King | `10.50 cm` (`0.105 m`) | `4.41 cm` | `Chess_Piece_White_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Green` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.095)`, `Crown_Tip` `(0,0,0.105)` |
| **6** | `cozy_chess_white_queen` | White Queen | `9.24 cm` (`0.092 m`) | `4.41 cm` | `Chess_Piece_White_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Green` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.082)`, `Crown_Tip` `(0,0,0.092)` |
| **7** | `cozy_chess_white_bishop` | White Bishop | `8.09 cm` (`0.081 m`) | `4.41 cm` | `Chess_Piece_White_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Green` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.071)`, `Crown_Tip` `(0,0,0.081)` |
| **8** | `cozy_chess_white_knight` | White Knight | `7.67 cm` (`0.077 m`) | `4.41 cm` | `Chess_Piece_White_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Green` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.067)`, `Crown_Tip` `(0,0,0.077)` |
| **9** | `cozy_chess_white_rook` | White Rook | `6.30 cm` (`0.063 m`) | `4.41 cm` | `Chess_Piece_White_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Green` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.053)`, `Crown_Tip` `(0,0,0.063)` |
| **10** | `cozy_chess_white_pawn` | White Pawn | `4.94 cm` (`0.049 m`) | `4.41 cm` | `Chess_Piece_White_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Green` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.039)`, `Crown_Tip` `(0,0,0.049)` |
| **11** | `cozy_chess_black_king` | Black King | `10.50 cm` (`0.105 m`) | `4.41 cm` | `Chess_Piece_Black_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Crimson` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.095)`, `Crown_Tip` `(0,0,0.105)` |
| **12** | `cozy_chess_black_queen` | Black Queen | `9.24 cm` (`0.092 m`) | `4.41 cm` | `Chess_Piece_Black_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Crimson` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.082)`, `Crown_Tip` `(0,0,0.092)` |
| **13** | `cozy_chess_black_bishop` | Black Bishop | `8.09 cm` (`0.081 m`) | `4.41 cm` | `Chess_Piece_Black_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Crimson` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.071)`, `Crown_Tip` `(0,0,0.081)` |
| **14** | `cozy_chess_black_knight` | Black Knight | `7.67 cm` (`0.077 m`) | `4.41 cm` | `Chess_Piece_Black_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Crimson` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.067)`, `Crown_Tip` `(0,0,0.077)` |
| **15** | `cozy_chess_black_rook` | Black Rook | `6.30 cm` (`0.063 m`) | `4.41 cm` | `Chess_Piece_Black_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Crimson` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.053)`, `Crown_Tip` `(0,0,0.063)` |
| **16** | `cozy_chess_black_pawn` | Black Pawn | `4.94 cm` (`0.049 m`) | `4.41 cm` | `Chess_Piece_Black_Marble`, `Chess_Gold_Brass`, `Chess_Felt_Crimson` | `Piece_Base` `(0,0,0)`, `Grab_Top` `(0,0,0.039)`, `Crown_Tip` `(0,0,0.049)` |

---

## 3. Shared Scene-Linear Material Palette (`chess_utils.py`)

| Material Name | Base Hex | Vein / Accent Hex | Roughness | Metallic | Usage |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `Chess_Marble_White_Veined` | `#F3F0EA` | `#B8BDC4` | `0.16` | `0.00` | Tabletop border, 32 light squares, 4 corner pillars, stepped plinth, chair drum |
| `Chess_Marble_Black_Veined` | `#1B1E24` | `#7C828D` | `0.14` | `0.02` | 32 dark squares, 4 recessed pedestal panels, chair drum flutes, clock hands |
| `Chess_Piece_White_Marble` | `#F7F3EB` | `#D5CFC3` | `0.15` | `0.00` | All 6 standalone White chess pieces |
| `Chess_Piece_Black_Marble` | `#22252C` | `#5E6470` | `0.14` | `0.04` | All 6 standalone Black chess pieces |
| `Chess_Gold_Brass` | `#D9A84E` | `#B3822C` | `0.22` | `0.88` | Piece collars, King cross, Queen coronet pearls, board pinstripe frame, clock bezels/buttons, chair ring & tuft button |
| `Chess_Felt_Green` | `#1F5C3A` | `#16442A` | `0.85` | `0.00` | White piece base pads & slide-out storage drawer interior |
| `Chess_Felt_Crimson` | `#7A2228` | `#58161B` | `0.85` | `0.00` | Black piece base pads |
| `Chess_Cushion_Cream_Sage` | `#DCE2D5` | `#B8C4AE` | `0.68` | `0.00` | Plump round tufted seat cushion on `cozy_chess_round_chair` |
| `Chess_Cushion_Piping` | `#4A5D4E` | `#364539` | `0.55` | `0.00` | Contrasting welt cord piping seams on round chair cushion |
| `Chess_Walnut_Wood` | `#5A3824` | `#3E2415` | `0.34` | `0.00` | Vintage mechanical chess clock body casing |
| `Chess_Clock_Dial_Cream` | `#FAF4E4` | `#E5D9BF` | `0.28` | `0.00` | Twin analog clock dial faces |
| `Chess_Clock_Flag_Red` | `#D93829` | `#A82418` | `0.32` | `0.00` | Hanging mechanical timeout flags on clock dials |
| `Chess_Groove_Slate` | `#343840` | `#23262C` | `0.45` | `0.00` | Recessed V-groove mortar bed between the 64 marble squares |
| `Chess_Highlight_Glow` | `#F5C445` | `#F5C445` | `0.18` | `0.40` | Emissive move-guide highlight frames (`Move_Highlight_From` / `To`) |

---

## 4. How to Wire Player vs. NPC Gameplay in `C:/claude/vrcozy`

1. **Spawning the Set:**
   - Place `cozy_chess_marble_table` at your desired lawn/terrace coordinate.
   - Spawn two instances of `cozy_chess_round_chair` at `table.Chair_White_Spot` (`(0, -0.68, 0)`, facing `+Y`) and `table.Chair_Black_Spot` (`(0, +0.68, 0)`, rotated `180°` facing `-Y`).
   - Spawn `cozy_chess_clock_analog` at `table.Clock_Spot` (`(-0.33, 0, 0.74)`).
   - Instantiate the 32 standalone pieces by matching each piece's `Piece_Base` `(0,0,0)` to the corresponding `Square_<file><rank>` socket on the table (`Square_a1`..`Square_h2` for White, `Square_a7`..`Square_h8` for Black, with Black pieces rotated `180°` around Z so Black Knights look toward White).
2. **Sitting the NPC & Driving NPC Moves via IK:**
   - Attach your NPC's hip/root to `NPC_Spine_Anchor` on the Black chair (`(0, +0.68, 0.460)`) and rest the NPC's hands on `NPC_Hand_Rest_L` and `NPC_Hand_Rest_R` while waiting (`Chair_Swivel_Idle`).
   - When it is the NPC's turn to move a piece from `fromSq` (e.g. `Square_e7`) to `toSq` (e.g. `Square_e5`):
     1. **Reach (`0.0–0.35 s`):** Lerp the NPC's right-hand IK target from `NPC_Hand_Rest_R` to `movingPiece.Grab_Top`.
     2. **Lift & Arc (`0.35–0.85 s`):** Trigger `Piece_Lift_Hop` (or `Piece_Slide_Place`) on `movingPiece` while interpolating `movingPiece.position` from `table[fromSq]` to `table[toSq]` ( keeping the NPC's right-hand IK locked to `movingPiece.Grab_Top`).
     3. **Capture (if `toSq` is occupied):** At `t = 0.65 s`, play `Piece_Capture_Tip_Fall` on the captured piece, then move it to the next open `Captured_W_01..16` socket on the left border.
     4. **Tap Clock & Return (`0.85–1.20 s`):** Lerp the NPC's right-hand IK to `clock.Hit_Button_Black`, play `Press_Black_Turn` on `cozy_chess_clock_analog`, and return the NPC hand to `NPC_Hand_Rest_R`.
