import bpy
import bmesh
import math
import sys
from mathutils import Vector, Euler, Matrix
from mathutils.geometry import delaunay_2d_cdt

sys.path.insert(0, "C:/argon/bowling")
sys.path.insert(0, "C:/argon/rapa_nui")
from bowling_utils import (
    PALETTE, init_scene, ensure_mat_slot, make_empty,
    make_frame_from_dir_and_normal, add_box, add_lofted_tube,
    save_and_export_bowling
)

# USBC regulation bowling ball diameter = 8.55 in = 21.7 cm (0.217 m), radius = 0.1085 m
BALL_DIAMETER = 0.2170
BALL_RADIUS   = 0.1085


def make_oriented_empty(name, location, z_dir, up_hint=(0.0, 0.0, 1.0), parent=None):
    """Creates an Empty whose local +Z axis points along `z_dir`."""
    emp = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(emp)
    emp.empty_display_type = 'ARROWS'
    emp.empty_display_size = 0.04
    rot_m = make_frame_from_dir_and_normal(z_dir, up_hint)
    if parent is not None:
        emp.parent = parent
    emp.location = Vector(location)
    emp.rotation_mode = 'XYZ'
    emp.rotation_euler = rot_m.to_euler('XYZ')
    return emp


def finalize_plain_mesh(mesh_name, bm, mat_names, merge_doubles=False):
    if merge_doubles:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0002)
    mesh = bpy.data.meshes.new(mesh_name)
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = False
    obj = bpy.data.objects.new(mesh_name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = Vector((0.0, 0.0, 0.0))
    for m in mat_names:
        ensure_mat_slot(obj, m)
    return obj


# ==============================================================================
# Clean 2D Stroke Definitions for Inlaid Weight Numerals (0, 1, 2, 4, 6, 8)
# Each digit lives in normalized [-0.5, +0.5] x [-0.5, +0.5] box
# ==============================================================================
def get_digit_polylines(ch):
    if ch == '1':
        return [
            [(-0.18, 0.34), (0.04, 0.48), (0.04, -0.48)],
            [(-0.22, -0.48), (0.28, -0.48)],
        ]
    elif ch == '0':
        pts = []
        for i in range(9):
            a = i * (2.0 * math.pi / 8.0)
            pts.append((0.32 * math.cos(a), 0.46 * math.sin(a)))
        return [pts]
    elif ch == '2':
        return [[
            (-0.30, 0.28), (-0.18, 0.46), (0.16, 0.46), (0.30, 0.28),
            (0.26, 0.06), (-0.32, -0.46), (0.32, -0.46)
        ]]
    elif ch == '4':
        return [
            [(0.14, -0.48), (0.14, 0.48), (-0.32, -0.12), (0.32, -0.12)],
        ]
    elif ch == '6':
        loop = []
        for i in range(9):
            a = i * (2.0 * math.pi / 8.0)
            loop.append((0.30 * math.cos(a), -0.16 + 0.30 * math.sin(a)))
        stem = [(-0.28, -0.12), (-0.18, 0.28), (0.04, 0.46), (0.24, 0.42)]
        return [loop, stem]
    elif ch == '8':
        top_loop = []
        bot_loop = []
        for i in range(9):
            a = i * (2.0 * math.pi / 8.0)
            top_loop.append((0.26 * math.cos(a),  0.23 + 0.23 * math.sin(a)))
            bot_loop.append((0.30 * math.cos(a), -0.24 + 0.24 * math.sin(a)))
        return [top_loop, bot_loop]
    return []


def add_spherical_stroke_ribbon(bm, pts_2d, center_dir, right_hint, width, r_surf, mat_idx):
    """Projects a 2D polyline onto the sphere of radius `r_surf` around `center_dir` with outward normals."""
    w_dir = Vector(center_dir).normalized()
    u_dir = Vector(right_hint)
    u_dir = (u_dir - u_dir.dot(w_dir) * w_dir).normalized()
    v_dir = w_dir.cross(u_dir).normalized()

    def to_sphere(u, v):
        d = u * u + v * v
        w = math.sqrt(max(1e-6, r_surf * r_surf - d))
        return u * u_dir + v * v_dir + w * w_dir

    n = len(pts_2d)
    if n < 2:
        return
    hw = width * 0.5
    left_v = []
    right_v = []
    for i in range(n):
        p = Vector(pts_2d[i])
        if i == 0:
            t = (Vector(pts_2d[1]) - p).normalized()
        elif i == n - 1:
            t = (p - Vector(pts_2d[i - 1])).normalized()
        else:
            t1 = (p - Vector(pts_2d[i - 1])).normalized()
            t2 = (Vector(pts_2d[i + 1]) - p).normalized()
            t = (t1 + t2)
            if t.length < 1e-5:
                t = t1
            else:
                t.normalize()
        perp = Vector((-t.y, t.x))
        p_l = p + perp * hw
        p_r = p - perp * hw
        left_v.append(bm.verts.new(to_sphere(p_l.x, p_l.y)))
        right_v.append(bm.verts.new(to_sphere(p_r.x, p_r.y)))

    for i in range(n - 1):
        try:
            f = bm.faces.new((right_v[i], right_v[i + 1], left_v[i + 1], left_v[i]))
            f.material_index = mat_idx
            f.normal_update()
            fc = (right_v[i].co + right_v[i + 1].co + left_v[i + 1].co + left_v[i].co) * 0.25
            if f.normal.dot(fc) < 0.0:
                f.normal_flip()
        except ValueError:
            pass


def add_inlaid_weight_number(bm, weight_str, center_dir, right_hint, mat_idx, r_surf):
    """Draws 1- or 2-digit weight number on the sphere surface beside the finger/thumb holes."""
    digits = list(weight_str)
    digit_w = 0.0175
    digit_h = 0.0280
    stroke_w = 0.0040
    gap = 0.0045
    total_w = len(digits) * digit_w + (len(digits) - 1) * gap
    start_x = -0.5 * total_w + 0.5 * digit_w

    for di, ch in enumerate(digits):
        cx = start_x + di * (digit_w + gap)
        for poly in get_digit_polylines(ch):
            pts_scaled = [(cx + px * digit_w, py * digit_h) for px, py in poly]
            add_spherical_stroke_ribbon(bm, pts_scaled, center_dir, right_hint, stroke_w, r_surf, mat_idx)


def add_coral_lanes_back_mark(bm, back_dir, right_hint, mat_brass, mat_accent, r_surf):
    """Adds a small mid-century Coral Lanes 4-point starburst & ring mark on the far side (+Y) of the ball."""
    # Outer ring (8-gon)
    ring_pts = []
    for i in range(9):
        a = i * (2.0 * math.pi / 8.0)
        ring_pts.append((0.016 * math.cos(a), 0.016 * math.sin(a)))
    add_spherical_stroke_ribbon(bm, ring_pts, back_dir, right_hint, 0.0026, r_surf, mat_accent)
    # 2 crossed starburst rays in brass
    add_spherical_stroke_ribbon(bm, [(-0.022, 0.0), (0.022, 0.0)], back_dir, right_hint, 0.0030, r_surf + 0.0001, mat_brass)
    add_spherical_stroke_ribbon(bm, [(0.0, -0.022), (0.0, 0.022)], back_dir, right_hint, 0.0030, r_surf + 0.0001, mat_brass)


# ==============================================================================
# Build One House Ball (`cozy_bowling_ball_06lb` .. `_16lb`)
# ==============================================================================
def build_house_ball(weight_lb, model_name, mats, is_youth_span=False, hole_mat_idx=1):
    """
    Builds a 21.7 cm (R = 0.1085 m) regulation bowling ball centered at (0, 0, 0)
    with 3 real 6-7 cm deep radial holes pointing at (0, 0, 0), wavy 1950s swirl,
    inlaid brass weight numeral beside the holes, far-side Coral Lanes mark,
    and the 4 required Empties:
      - Ball_Center at (0, 0, 0)
      - Thumb_Hole at thumb hole mouth, local +Z pointing into hole
      - Finger_Hole_Middle at middle finger hole mouth, local +Z pointing into hole
      - Finger_Hole_Ring at ring finger hole mouth, local +Z pointing into hole
    """
    init_scene()
    bm = bmesh.new()

    R = BALL_RADIUS  # 0.1085 m (diameter = 0.2170 m = 21.7 cm)

    # Grip cap center direction: facing -Y front, tilted +12° toward +Z so viewed from the front (-Y)
    # the thumb hole sits directly below the two finger holes and the weight numeral sits beside them.
    cap_tilt_rad = math.radians(12.0)
    u_cap = Vector((0.0, -math.cos(cap_tilt_rad), math.sin(cap_tilt_rad))).normalized()
    e1 = Vector((1.0, 0.0, 0.0))                     # +X right
    e2 = u_cap.cross(e1).normalized()                # Up along the front hemisphere

    def lift_to_sphere(u, v, rad=R):
        d2 = u * u + v * v
        w = math.sqrt(max(1e-8, rad * rad - d2))
        return u * e1 + v * e2 + w * u_cap

    # Hole layout in the (e1, e2) tangent plane of the front grip cap:
    # Lighter balls (6, 8, 10 lb) have a slightly shorter span and smaller holes than 12, 14, 16 lb.
    if is_youth_span:
        holes_spec = [
            ("Finger_Hole_Middle", -0.0170,  0.0235, 0.0105, 0.060),  # 2.10 cm dia, 6.0 cm deep
            ("Finger_Hole_Ring",    0.0170,  0.0235, 0.0105, 0.060),  # 2.10 cm dia, 6.0 cm deep
            ("Thumb_Hole",          0.0000, -0.0265, 0.0125, 0.068),  # 2.50 cm dia, 6.8 cm deep
        ]
    else:
        holes_spec = [
            ("Finger_Hole_Middle", -0.0195,  0.0265, 0.0118, 0.062),  # 2.36 cm dia, 6.2 cm deep
            ("Finger_Hole_Ring",    0.0195,  0.0265, 0.0118, 0.062),  # 2.36 cm dia, 6.2 cm deep
            ("Thumb_Hole",          0.0000, -0.0305, 0.0138, 0.070),  # 2.76 cm dia, 7.0 cm deep
        ]

    # Cap boundary at theta_cap = 36 deg around u_cap
    N_LON = 20
    N_HOLE_SIDES = 8
    theta_cap = math.radians(36.0)
    r_cap_2d = R * math.sin(theta_cap)

    # Build 2D vertices & constraint edges for Constrained Delaunay Triangulation of the front grip cap
    cdt_verts_2d = []
    cdt_edges = []

    # 1. Outer cap boundary ring (indices 0 .. N_LON-1)
    for i in range(N_LON):
        phi = i * (2.0 * math.pi / N_LON)
        cdt_verts_2d.append(Vector((r_cap_2d * math.cos(phi), r_cap_2d * math.sin(phi))))
    for i in range(N_LON):
        cdt_edges.append((i, (i + 1) % N_LON))

    # 2. Three 8-gon hole rims
    hole_ring_indices = []
    for h_name, hcx, hcy, hr, hdepth in holes_spec:
        start_idx = len(cdt_verts_2d)
        idxs = []
        for k in range(N_HOLE_SIDES):
            ang = k * (2.0 * math.pi / N_HOLE_SIDES)
            cdt_verts_2d.append(Vector((hcx + hr * math.cos(ang), hcy + hr * math.sin(ang))))
            idxs.append(start_idx + k)
        for k in range(N_HOLE_SIDES):
            cdt_edges.append((idxs[k], idxs[(k + 1) % N_HOLE_SIDES]))
        hole_ring_indices.append((h_name, hcx, hcy, hr, hdepth, idxs))

    # 3. A few helper Steiner points between/around the holes so cap triangles stay smoothly curved on the sphere
    steiner_pts = [
        ( 0.000,  0.002),
        (-0.038,  0.000),
        ( 0.038,  0.000),
        ( 0.000,  0.046),
        (-0.032, -0.036),
        ( 0.032, -0.036),
    ]
    for sx, sy in steiner_pts:
        cdt_verts_2d.append(Vector((sx, sy)))

    # Run 2D Constrained Delaunay Triangulation
    verts_out, edges_out, faces_out, orig_v, orig_e, orig_f = delaunay_2d_cdt(
        cdt_verts_2d, cdt_edges, [], 2, 1e-5
    )

    # Lift all CDT vertices onto the exact sphere surface (|p| = R)
    cap_bm_verts = [bm.verts.new(lift_to_sphere(v2.x, v2.y, R)) for v2 in verts_out]

    # Map original input vertex index -> new CDT vertex index
    input_to_cdt = {}
    for cdt_i, orig_list in enumerate(orig_v):
        for inp_i in orig_list:
            input_to_cdt[inp_i] = cdt_i

    # Create cap faces (excluding faces inside the 3 hole interiors or outside the cap polygon)
    for f_indices in faces_out:
        if len(f_indices) < 3:
            continue
        c2 = sum((verts_out[idx] for idx in f_indices), Vector((0.0, 0.0))) / len(f_indices)
        if c2.length > r_cap_2d * 1.001:
            continue
        inside_hole = False
        for _, hcx, hcy, hr, _, _ in hole_ring_indices:
            if math.hypot(c2.x - hcx, c2.y - hcy) < hr * 0.90:
                inside_hole = True
                break
        if inside_hole:
            continue
        f_verts = [cap_bm_verts[idx] for idx in f_indices]
        try:
            f = bm.faces.new(f_verts)
            f.material_index = 0
            f.normal_update()
            fc = sum((v.co for v in f_verts), Vector((0.0, 0.0, 0.0))) / len(f_verts)
            if f.normal.dot(fc) < 0.0:
                f.normal_flip()
        except ValueError:
            pass

    # Extrude the 3 hole rims radially inward along u_in = -p_mouth.normalized() by 6-7 cm!
    hole_mouth_data = []
    for h_name, hcx, hcy, hr, hdepth, inp_idxs in hole_ring_indices:
        p_mouth = lift_to_sphere(hcx, hcy, R)
        u_in = (-p_mouth).normalized()
        hole_mouth_data.append((h_name, p_mouth, u_in))

        rim_bverts = [cap_bm_verts[input_to_cdt[ii]] for ii in inp_idxs]
        # Bottom ring recessed by `hdepth` (6.0-7.0 cm) along u_in toward the ball's origin (0,0,0)
        bot_bverts = [bm.verts.new(rv.co + u_in * hdepth) for rv in rim_bverts]

        for k in range(N_HOLE_SIDES):
            k_next = (k + 1) % N_HOLE_SIDES
            v0 = rim_bverts[k]
            v1 = rim_bverts[k_next]
            v2 = bot_bverts[k_next]
            v3 = bot_bverts[k]
            try:
                f_wall = bm.faces.new((v0, v1, v2, v3))
                f_wall.material_index = hole_mat_idx
                f_wall.normal_update()
                wall_mid = (v0.co + v1.co) * 0.5 - p_mouth
                # Inside a hole, the wall normal should point inward toward the hole centerline (-wall_mid)
                if f_wall.normal.dot(wall_mid) > 0.0:
                    f_wall.normal_flip()
            except ValueError:
                pass

        # Fan-triangulate the 8-gon bottom cap (6 triangles)
        for k in range(1, N_HOLE_SIDES - 1):
            try:
                f_bot = bm.faces.new((bot_bverts[0], bot_bverts[k], bot_bverts[k + 1]))
                f_bot.material_index = hole_mat_idx
                f_bot.normal_update()
                if f_bot.normal.dot(-u_in) < 0.0:
                    f_bot.normal_flip()
            except ValueError:
                pass

    # Now build the remainder of the sphere from theta = 36 deg to theta = 180 deg (-u_cap)
    # Using latitude rings warped slightly into a smooth 1950s S-curve swirl wave while keeping |p| == R!
    outer_ring_bverts = [cap_bm_verts[input_to_cdt[i]] for i in range(N_LON)]
    theta_deg_steps = [54.0, 72.0, 90.0, 108.0, 126.0, 144.0, 162.0]
    rings_bverts = [outer_ring_bverts]

    for t_deg in theta_deg_steps:
        t_rad = math.radians(t_deg)
        # Smooth S-wave modulation damped to 0 at cap boundary (36°) and back pole (180°)
        env = math.sin(math.pi * (t_deg - 36.0) / (180.0 - 36.0))
        ring_v = []
        for i in range(N_LON):
            phi = i * (2.0 * math.pi / N_LON)
            wave = 0.17 * math.sin(2.0 * phi - 0.45) + 0.08 * math.cos(phi + 0.6)
            t_eff = max(math.radians(39.0), min(math.radians(176.0), t_rad + env * wave))
            st = math.sin(t_eff)
            ct = math.cos(t_eff)
            p_sph = R * (st * math.cos(phi) * e1 + st * math.sin(phi) * e2 + ct * u_cap)
            ring_v.append(bm.verts.new(p_sph))
        rings_bverts.append(ring_v)

    # Quad bands between consecutive latitude rings
    for r_i in range(len(rings_bverts) - 1):
        r_a = rings_bverts[r_i]
        r_b = rings_bverts[r_i + 1]
        for i in range(N_LON):
            i_next = (i + 1) % N_LON
            v0, v1, v2, v3 = r_a[i], r_a[i_next], r_b[i_next], r_b[i]
            try:
                f = bm.faces.new((v0, v1, v2, v3))
                # Primary wavy swirl ribbon on band 2 (72..90 deg) + secondary swirl streak on band 4 (108..126 deg)
                is_swirl = (r_i == 2) or (r_i == 4 and (i in (2, 3, 4, 5, 6, 12, 13, 14, 15, 16)))
                f.material_index = 1 if is_swirl else 0
                f.normal_update()
                fc = (v0.co + v1.co + v2.co + v3.co) * 0.25
                if f.normal.dot(fc) < 0.0:
                    f.normal_flip()
            except ValueError:
                pass

    # Back pole vertex at theta = 180 deg (-u_cap * R)
    v_pole = bm.verts.new(-R * u_cap)
    last_ring = rings_bverts[-1]
    for i in range(N_LON):
        i_next = (i + 1) % N_LON
        try:
            f = bm.faces.new((last_ring[i], last_ring[i_next], v_pole))
            f.material_index = 0
            f.normal_update()
            fc = (last_ring[i].co + last_ring[i_next].co + v_pole.co) / 3.0
            if f.normal.dot(fc) < 0.0:
                f.normal_flip()
        except ValueError:
            pass

    # Inlaid Weight Numeral ("6", "8", "10", "12", "14", "16") beside the holes (front-right, matching Figure 1)
    num_dir = Vector((0.42, -0.89, -0.06)).normalized()
    add_inlaid_weight_number(
        bm, str(weight_lb),
        center_dir=num_dir,
        right_hint=Vector((0.89, 0.42, 0.0)),
        mat_idx=2,
        r_surf=R + 0.0004
    )

    # Small Coral Lanes starburst & ring mark on the far side (+Y)
    add_coral_lanes_back_mark(
        bm,
        back_dir=-u_cap,
        right_hint=Vector((-1.0, 0.0, 0.0)),
        mat_brass=2,
        mat_accent=1,
        r_surf=R + 0.0004
    )

    mesh_obj = finalize_plain_mesh(f"Ball_{weight_lb:02d}lb_Mesh", bm, mats, merge_doubles=False)

    # Required Empties:
    # 1. Ball_Center at the origin (0, 0, 0)
    make_empty("Ball_Center", (0.0, 0.0, 0.0), parent=mesh_obj)
    # 2. Thumb_Hole, Finger_Hole_Middle, Finger_Hole_Ring at each hole's mouth with local +Z pointing into the hole
    for h_name, p_mouth, u_in in hole_mouth_data:
        make_oriented_empty(h_name, p_mouth, z_dir=u_in, up_hint=(0.0, 0.0, 1.0), parent=mesh_obj)

    save_and_export_bowling(model_name, animated=False)


# ==============================================================================
# Build All 6 House Balls (6, 8, 10, 12, 14, 16 lb)
# ==============================================================================
def build_all_six_house_balls():
    # 6 lb: Lilac, cream swirl, brass numeral ("6")
    build_house_ball(
        6, "cozy_bowling_ball_06lb",
        mats=["Bowling_Ball_Lilac", "Bowling_Cream_Pearl", "Bowling_Gold_Brass"],
        is_youth_span=True, hole_mat_idx=0
    )
    # 8 lb: Coral, cream swirl, brass numeral ("8")
    build_house_ball(
        8, "cozy_bowling_ball_08lb",
        mats=["Bowling_Coral_Pink", "Bowling_Cream_Pearl", "Bowling_Gold_Brass"],
        is_youth_span=True, hole_mat_idx=0
    )
    # 10 lb: Sunflower, cream swirl, brass numeral ("10")
    build_house_ball(
        10, "cozy_bowling_ball_10lb",
        mats=["Bowling_Ball_Sunflower", "Bowling_Cream_Pearl", "Bowling_Gold_Brass"],
        is_youth_span=True, hole_mat_idx=0
    )
    # 12 lb: Teal, seafoam swirl, brass numeral ("12")
    build_house_ball(
        12, "cozy_bowling_ball_12lb",
        mats=["Bowling_Teal_Seafoam", "Bowling_Ball_Seafoam", "Bowling_Gold_Brass"],
        is_youth_span=False, hole_mat_idx=0
    )
    # 14 lb: Ocean blue, navy swirl, brass numeral ("14")
    build_house_ball(
        14, "cozy_bowling_ball_14lb",
        mats=["Bowling_Ball_Ocean", "Bowling_Ball_Navy", "Bowling_Gold_Brass"],
        is_youth_span=False, hole_mat_idx=1
    )
    # 16 lb: Obsidian, gold flecks/swirl & brass numeral ("16"), cream accent mark
    build_house_ball(
        16, "cozy_bowling_ball_16lb",
        mats=["Bowling_Obsidian_Ball", "Bowling_Gold_Brass", "Bowling_Cream_Pearl"],
        is_youth_span=False, hole_mat_idx=0
    )


# ==============================================================================
# 2. cozy_bowling_ball_rack_empty (3-Tier A-Frame Rack, Empty, with Slot_Ball_1..9)
# ==============================================================================
def build_ball_rack_empty():
    init_scene()
    bm = bmesh.new()

    # Materials:
    # 0: Bowling_Chrome_Steel - tubular A-frame & 3 pairs of cradle rails
    # 1: Bowling_Teal_Seafoam - base plinth
    # 2: Bowling_Coral_Pink   - top header sign
    # 3: Bowling_Obsidian_Ball- rubber floor pad
    # 4: Bowling_Gold_Brass   - header frame, upright caps & 9 slot saddle markers
    mats = [
        "Bowling_Chrome_Steel", "Bowling_Teal_Seafoam", "Bowling_Coral_Pink",
        "Bowling_Obsidian_Ball", "Bowling_Gold_Brass"
    ]

    # Heavy Base Plinth (Z = 0.00 to 0.09 m, width = 1.16 m, depth = 0.44 m)
    add_box(bm, (0.0, 0.0, 0.04), 1.16, 0.44, 0.08, mat_idx=1)
    add_box(bm, (0.0, 0.0, 0.085), 1.10, 0.38, 0.01, mat_idx=3)

    # Exact geometry for a 21.7 cm ball (R = 0.1085 m) resting on two rails of radius r_rail = 0.015 m
    # spaced at Y = +-0.075 m:
    # Vertical center offset above rail centerline: dz = sqrt((0.1085 + 0.0150)^2 - 0.075^2) = 0.0981 m.
    # Three tiers spaced 0.34 m apart vertically so there is >10.5 cm of clear hand reach-in space above every ball:
    #   - Top tier:    rail Z = 0.840 m -> Slot_Ball_1..3 center Z = 0.9381 m (ball top = 1.0466 m)
    #   - Middle tier: rail Z = 0.500 m -> Slot_Ball_4..6 center Z = 0.5981 m (ball top = 0.7066 m, 11.8 cm below top rail)
    #   - Bottom tier: rail Z = 0.160 m -> Slot_Ball_7..9 center Z = 0.2581 m (ball top = 0.3666 m, 11.8 cm below mid rail)
    # Horizontal slot centers at X = -0.290, 0.000, +0.290 m (7.3 cm clear between adjacent 21.7 cm balls).
    SLOT_XS = (-0.290, 0.000, 0.290)
    TIER_RAIL_ZS = (0.840, 0.500, 0.160)   # Top tier first!
    RAIL_Y = 0.075
    RAIL_R = 0.015
    DZ_BALL_ON_RAIL = math.sqrt((BALL_RADIUS + RAIL_R) ** 2 - RAIL_Y ** 2)  # 0.09812 m

    # Left & Right A-Frame Chrome Uprights (`X = +-0.48 m`, Z = 0.08 to 1.22 m)
    for sx in (-0.48, 0.48):
        add_lofted_tube(bm, [((sx, -0.16, 0.08), 0.022), ((sx, -0.06, 1.20), 0.020)], sides=8, mat_idx=0)
        add_lofted_tube(bm, [((sx,  0.16, 0.08), 0.022), ((sx,  0.06, 1.20), 0.020)], sides=8, mat_idx=0)
        # Side cross-braces at each tier
        for rz in TIER_RAIL_ZS:
            add_lofted_tube(bm, [((sx, -0.08, rz), 0.014), ((sx, 0.08, rz), 0.014)], sides=6, mat_idx=0)
        add_box(bm, (sx, 0.0, 1.20), 0.045, 0.15, 0.04, mat_idx=4)

    # Top Header Sign ("HOUSE BALLS — 6 TO 16 LB") raised to Z = 1.26 m so top-tier balls (top at 1.047 m) have >14 cm reach-in room
    add_box(bm, (0.0, 0.0, 1.26), 0.68, 0.04, 0.11, mat_idx=2)
    add_box(bm, (0.0, 0.0, 1.26), 0.72, 0.03, 0.13, mat_idx=4)

    # 3 Pairs of Horizontal Chrome Cradle Rails + Brass Slot Saddle Rings marking each of the 9 slots
    for rz in TIER_RAIL_ZS:
        for ry in (-RAIL_Y, RAIL_Y):
            add_lofted_tube(bm, [((-0.48, ry, rz), RAIL_R), ((0.48, ry, rz), RAIL_R)], sides=8, mat_idx=0)
            # Subtle brass saddle rings on the rail flanking each ball's resting contact point
            for sx in SLOT_XS:
                for collar_dx in (-0.055, 0.055):
                    cx = sx + collar_dx
                    add_lofted_tube(
                        bm,
                        [((cx - 0.008, ry, rz), RAIL_R + 0.0025), ((cx + 0.008, ry, rz), RAIL_R + 0.0025)],
                        sides=8, mat_idx=4
                    )

    mesh_obj = finalize_plain_mesh("BallRack_Empty_Mesh", bm, mats, merge_doubles=False)

    # 9 Slot Empties: Slot_Ball_1..3 (top tier, L->R), Slot_Ball_4..6 (middle tier, L->R), Slot_Ball_7..9 (bottom tier, L->R)
    slot_num = 1
    for rz in TIER_RAIL_ZS:
        ball_center_z = round(rz + DZ_BALL_ON_RAIL, 4)
        for sx in SLOT_XS:
            make_empty(f"Slot_Ball_{slot_num}", (sx, 0.0, ball_center_z), parent=mesh_obj)
            slot_num += 1

    save_and_export_bowling("cozy_bowling_ball_rack_empty", animated=False)


if __name__ == "__main__":
    build_all_six_house_balls()
    build_ball_rack_empty()
