"""
ACS-9 -- Acoustic Compliance System. Build script for Blender 5.x. v2: ICS soft look, textured PBR materials,
triangle budget lifted by the author.

Run:  blender --background --python ACS-9_build.py -- <ICS-Models root>
Writes: Weapon Models/compliance/ACS-9/ACS-9.blend (+ textures/), Weapon Models/exports/ACS-9.fbx,
        Weapon Models/compliance/ACS-9/previews/*.png
Spec:   _specs/ACS-9.md   Canon: ICS-Writing/canon/weapons/compliance/ACS-9 ...md
Textures: acs9_textures.py (procedural numpy, printed decals through Blender text curves)

Units: metres. The long axis is Y. Forward (the grille) = -Y, the handle and slider are up (+Z) and to +X.
ORIGIN = the centre of the rubber grip (v2; v1 used the body centre). All geometry is built in body-centred
coordinates and shifted by -ORIGIN at the end, so the mount empties move with it: rebuild any attachment.

Canon used: ~25 cm x 8 cm black cylinder, handle on the body, recessed speaker-like grille, 3-position slider
marked 1 2 3, ICS logo at the base, serial ICS-ACS-9-0012 (B-17), two 22 mm focusing rings (CRD-7X: the secondary is
reached through the rear housing panel, held by two quarter-turn screws), certification text printed on the label.
Everything else is a [PROPOSAL]; see the spec.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = sys.argv[sys.argv.index("--") + 1]
sys.path.insert(0, os.path.join(ROOT, "_shared"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import studio  # noqa: E402
import acs9_textures as tx  # noqa: E402

OUT = os.path.join(ROOT, "Weapon Models", "compliance", "ACS-9")
PREVIEW_DIR = os.path.join(OUT, "previews")
TEX_DIR = os.path.join(OUT, "textures")
EXPORT_DIR = os.path.join(ROOT, "Weapon Models", "exports")
for d in (PREVIEW_DIR, TEX_DIR, EXPORT_DIR):
    os.makedirs(d, exist_ok=True)

# ---- dimensions (m) --------------------------------------------------------
BODY_R = 0.040            # canon: 8 cm across
Y_REAR, Y_FRONT = 0.125, -0.125   # canon: 25 cm long
BEZEL_R = 0.0425          # ACS-9D canon: 8.5 cm aperture assembly
BEZEL_BACK = -0.095       # where the bezel starts
SEGS = 72
REAR_FILLET = 0.008
RING_R_OUT, RING_R_IN = 0.011, 0.0075                      # CRD-7X canon: 22 mm focusing ring
HC = 0.045                                                  # handle centre y [PROPOSAL]
GRIP_Z = 0.069
ORIGIN = Vector((0.0, HC, GRIP_Z))                          # pivot at the grip centre

# recess stack, front to back (y)
RECESS_R, RECESS_FLOOR = 0.0360, -0.1000
PLATE_F, PLATE_B = -0.1210, -0.1180
CLOTH_Y = -0.1170
RING1 = (-0.1150, -0.1110)
RING2 = (-0.1080, -0.1040)

# rear panel
PANEL_R = 0.0290
PANEL_Y = Y_REAR - 0.0001                                  # face of the panel
MARK_Z = 0.007

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
coll = scene.collection


def link(ob):
    coll.objects.link(ob)
    return ob


def mesh_from_bm(name, bm):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


def smooth(ob, angle=35):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
        except Exception:
            for p in ob.data.polygons:
                p.use_smooth = True


def finish(ob, material, angle=35):
    ob.data.materials.clear()
    ob.data.materials.append(material)
    for p in ob.data.polygons:
        p.material_index = 0
    smooth(ob, angle)
    return ob


def revolve(name, pts, steps=SEGS):
    """Revolve a closed (radius, y) profile 360 degrees about the Y axis."""
    bm = bmesh.new()
    vs = [bm.verts.new((r, y, 0)) for r, y in pts]
    es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 1, 0), dvec=(0, 0, 0),
                   angle=math.tau, steps=steps, use_merge=True, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    return mesh_from_bm(name, bm)


def fillet(cx, cy, r, a0, a1, n):
    """Points on an arc in (radius, y): angle measured from +radius toward +y."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def rbox(name, size, r, segs=2):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    if r > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, offset_type="OFFSET",
                        profile=0.5, segments=segs, affect="EDGES", clamp_overlap=True)
    return mesh_from_bm(name, bm)


def arc_y(name, r_in, r_out, a0, a1, thick, steps=24):
    """Flat annular arc (degrees) in the XZ plane, extruded along +Y. Used for the gold arc of the mark."""
    bm = bmesh.new()
    ang = [math.radians(a0 + (a1 - a0) * i / steps) for i in range(steps + 1)]
    outer = [(r_out * math.cos(a), r_out * math.sin(a)) for a in ang]
    inner = [(r_in * math.cos(a), r_in * math.sin(a)) for a in reversed(ang)]
    face = bm.faces.new([bm.verts.new((x, y, 0)) for x, y in outer + inner])
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, vec=(0, 0, thick), verts=[e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)])
    bmesh.ops.transform(bm, matrix=Matrix.Rotation(math.radians(-90), 4, "X"), verts=bm.verts)   # +Z -> +Y
    return mesh_from_bm(name, bm)


def yz_prism(name, pts, half_w, bevel=0.0028, segs=3):
    """Closed (y, z) outline extruded across X by +-half_w, edges softened."""
    bm = bmesh.new()
    face = bm.faces.new([bm.verts.new((-half_w, y, z)) for y, z in pts])
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, vec=(2 * half_w, 0, 0), verts=[e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)])
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, offset_type="OFFSET", profile=0.5,
                    segments=segs, affect="EDGES", clamp_overlap=True)
    return mesh_from_bm(name, bm)


def merge(name, obs):
    """Join objects (no parent, transforms in matrix_basis) into one mesh object."""
    bm = bmesh.new()
    for ob in obs:
        me = ob.data.copy()
        me.transform(ob.matrix_basis)
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    for ob in obs:
        bpy.data.objects.remove(ob, do_unlink=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


def boolean_cut(ob, cutter):
    mod = ob.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def wrap_patch(name, side, yc, w, h, psic, off=0.0002, nu=40, nv=8):
    """Thin printed film wrapped on the body cylinder. side +1 = +X face, -1 = -X face. w along Y, h along the arc,
    psic = angle (rad) of the patch centre above the XY plane. UV 0..1 covers the film as seen from outside."""
    R = BODY_R + off
    bm = bmesh.new()
    grid = [[None] * (nv + 1) for _ in range(nu + 1)]
    uvs = {}
    for i in range(nu + 1):
        fu = i / nu
        for j in range(nv + 1):
            fv = j / nv
            psi = psic + (fv - 0.5) * h / R
            v = bm.verts.new((side * R * math.cos(psi), yc + (fu - 0.5) * w, R * math.sin(psi)))
            grid[i][j] = v
            uvs[v] = (fu if side > 0 else 1.0 - fu, fv)
    uvl = bm.loops.layers.uv.verify()
    for i in range(nu):
        for j in range(nv):
            a, b, c, d = grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]
            f = bm.faces.new((a, b, c, d) if side > 0 else (a, d, c, b))
            for lp in f.loops:
                lp[uvl].uv = uvs[lp.vert]
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


# ---- UV helpers (before the origin shift; matrix_basis is the world matrix, nothing is parented yet) ----
def uv_box(ob, tile):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    M = ob.matrix_basis
    R3 = M.to_3x3()
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = R3 @ f.normal
        ax = max(range(3), key=lambda k: abs(n[k]))
        for lp in f.loops:
            p = M @ lp.vert.co
            u, v = ((p.y, p.z), (p.x, p.z), (p.x, p.y))[ax]
            lp[uvl].uv = (u / tile, v / tile)
    bm.to_mesh(ob.data)
    bm.free()


def uv_rev(ob, tile, radius):
    """Surfaces of revolution about the local Y axis: whole repeats around, y along V. Faces that look along Y use planar UVs."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    N = max(1, round(math.tau * radius / tile))
    oy = ob.matrix_basis.translation.y
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        if abs(f.normal.y) > 0.9:
            for lp in f.loops:
                lp[uvl].uv = (lp.vert.co.x / tile, lp.vert.co.z / tile)
            continue
        c = f.calc_center_median()
        pc = math.atan2(c.z, c.x)
        for lp in f.loops:
            p = lp.vert.co
            d = (math.atan2(p.z, p.x) - pc + math.pi) % math.tau - math.pi
            lp[uvl].uv = ((pc + d) / math.tau * N, (p.y + oy) / tile)
    bm.to_mesh(ob.data)
    bm.free()


def uv_rear(ob, size):
    """Planar UVs for the decal on the rear panel, as seen from behind (viewer right = -X)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    M = ob.matrix_basis
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for lp in f.loops:
            p = M @ lp.vert.co
            lp[uvl].uv = (-p.x / size + 0.5, p.z / size + 0.5)
    bm.to_mesh(ob.data)
    bm.free()


# ---- textures and materials -------------------------------------------------
maps = tx.make(TEX_DIR)
prints = tx.make_prints(TEX_DIR)


def mat(name, color, rough=0.5, metal=0.0, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def load(path, srgb):
    img = bpy.data.images.load(path)
    img.colorspace_settings.name = "sRGB" if srgb else "Non-Color"
    return img


def pbr(name, albedo, rough=None, normal=None, metal=0.0, base_rough=0.5, nstrength=1.0):
    m = mat(name, (0.5, 0.5, 0.5), base_rough, metal)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    for path, inp, srgb in ((albedo, "Base Color", True), (rough, "Roughness", False)):
        if path:
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = load(path, srgb)
            nt.links.new(t.outputs["Color"], bsdf.inputs[inp])
    if normal:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = load(normal, False)
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = nstrength
        nt.links.new(t.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return m


M_BODY = pbr("ACS-9_body", maps["body_albedo"], maps["abs_rough"], maps["abs_normal"])
M_GRILLE = pbr("ACS-9_grille", maps["grille_albedo"], maps["abs_rough"], maps["abs_normal"])
M_TRACK = pbr("ACS-9_slider_plate", maps["track_albedo"], maps["abs_rough"], maps["abs_normal"])
M_CLOTH = pbr("ACS-9_cloth", maps["cloth_albedo"], maps["cloth_rough"], maps["cloth_normal"])
M_RUBBER = pbr("ACS-9_rubber", maps["rubber_albedo"], maps["rubber_rough"], maps["rubber_normal"])
M_RING = pbr("ACS-9_focus_ring", maps["ring_albedo"], maps["alu_rough"], maps["alu_normal"], metal=1.0)   # brushed aluminium (CRD-7X canon)
M_STEEL = pbr("ACS-9_steel", maps["steel_albedo"], maps["steel_rough"], maps["steel_normal"], metal=0.95)
M_BLUE = mat("ACS-9_logo_blue", (0.012, 0.027, 0.085), 0.45)         # ICS Deep Blue #1A2E52
M_GOLD = mat("ACS-9_logo_gold", (0.58, 0.39, 0.075), 0.35, 0.8)      # ICS Warm Gold #C9A84C
M_LAMP = mat("ACS-9_lamp", (1.0, 0.45, 0.02), 0.25, emit=(1.0, 0.5, 0.05), strength=1.8)   # amber = charged (canon: security-division indicator)
M_LABEL = pbr("ACS-9_label", prints["label"], base_rough=0.38)
M_LEGEND = pbr("ACS-9_legend", prints["legend"], base_rough=0.5)
M_REAR = pbr("ACS-9_rear_panel", prints["rear"], maps["abs_rough"], None)

geo = []

# ---- body: rear panel seat, fillet, two seam grooves ---------------------------
def groove(y, w=0.0020, d=0.0008):
    return [(BODY_R, y + w), (BODY_R - d, y + w * 0.6), (BODY_R - d, y - w * 0.6), (BODY_R, y - w)]


body_pts = [(0.0, Y_REAR - 0.0010), (PANEL_R + 0.0005, Y_REAR - 0.0010), (PANEL_R + 0.0005, Y_REAR), (BODY_R - REAR_FILLET, Y_REAR)]
body_pts += fillet(BODY_R - REAR_FILLET, Y_REAR - REAR_FILLET, REAR_FILLET, 90, 0, 5)[1:]
body_pts += groove(0.080) + groove(-0.088)
body_pts += [(BODY_R, BEZEL_BACK - 0.003), (0.0, BEZEL_BACK - 0.003)]
body = revolve("ACS-9_body", body_pts)
uv_rev(body, 0.04, BODY_R)
geo.append(finish(body, M_BODY))

# ---- front bezel: deep recess for the grille stack ---------------------------------
bez_pts = [(0.0, BEZEL_BACK), (BEZEL_R - 0.002, BEZEL_BACK)]
bez_pts += fillet(BEZEL_R - 0.002, BEZEL_BACK - 0.002, 0.002, 90, 0, 3)[1:]
bez_pts += [(BEZEL_R, Y_FRONT + 0.005)]
bez_pts += fillet(BEZEL_R - 0.005, Y_FRONT + 0.005, 0.005, 0, -90, 5)[1:]
bez_pts += [(RECESS_R + 0.0012, Y_FRONT), (RECESS_R, Y_FRONT + 0.0010), (RECESS_R, RECESS_FLOOR), (0.0, RECESS_FLOOR)]
bezel = revolve("ACS-9_bezel", bez_pts)
uv_rev(bezel, 0.04, BEZEL_R)
geo.append(finish(bezel, M_BODY))

# ---- perforated grille plate: concentric rings of holes, raised retaining lip ----------
plate_pts = [(0.0, PLATE_B), (RECESS_R - 0.0003, PLATE_B), (RECESS_R - 0.0003, PLATE_F), (0.0338, PLATE_F),
             (0.0338, PLATE_F - 0.0007), (0.0318, PLATE_F - 0.0007), (0.0318, PLATE_F), (0.0, PLATE_F)]
plate = revolve("ACS-9_grille", plate_pts, 96)
cb = bmesh.new()
pitch, hole_r = 0.0042, 0.0013
holes = 0
for k in range(0, 8):
    rk = pitch * k
    n = 1 if k == 0 else max(6, round(math.tau * rk / pitch))
    for i in range(n):
        a = math.tau * i / n + (0.0 if k % 2 == 0 else math.pi / n)
        M = Matrix.Translation((rk * math.cos(a), (PLATE_F + PLATE_B) / 2, rk * math.sin(a))) @ Matrix.Rotation(math.pi / 2, 4, "X")
        bmesh.ops.create_cone(cb, cap_ends=True, segments=14, radius1=hole_r, radius2=hole_r, depth=0.008, matrix=M)
        holes += 1
cutter = mesh_from_bm("grille_cutter", cb)
boolean_cut(plate, cutter)
uv_rev(plate, 0.04, 0.03)
geo.append(finish(plate, M_GRILLE, 40))
print(f"grille holes: {holes}")

# ---- speaker cloth behind the plate -------------------------------------------------
cloth = revolve("ACS-9_cloth", [(0.0, CLOTH_Y + 0.0002), (RECESS_R - 0.0003, CLOTH_Y + 0.0002),
                                (RECESS_R - 0.0003, CLOTH_Y - 0.0002), (0.0, CLOTH_Y - 0.0002)], 72)
uv_rev(cloth, 0.02, 0.02)
geo.append(finish(cloth, M_CLOTH))

# ---- the two focusing rings (primary, secondary), 22 mm, brushed aluminium --------------
def ring_part(name, y_front, y_back):
    c = 0.0004
    mid = (y_front + y_back) / 2
    pts = [(RING_R_IN, y_back), (RING_R_OUT - c, y_back), (RING_R_OUT, y_back + c), (RING_R_OUT, y_front - c),
           (RING_R_OUT - c, y_front), (RING_R_IN + c, y_front), (RING_R_IN, y_front - c),
           (RING_R_IN, mid + 0.0005), (RING_R_IN + 0.0003, mid), (RING_R_IN, mid - 0.0005)]   # inner groove
    r = revolve(name, pts, 64)
    uv_rev(r, 0.04, RING_R_OUT)
    return finish(r, M_RING, 40)


geo.append(ring_part("ACS-9_focus_ring_primary", RING1[0], RING1[1]))
geo.append(ring_part("ACS-9_focus_ring_secondary", RING2[0], RING2[1]))

# ---- carrying handle over the rear half [PROPOSAL] ---------------------------------
HW = 0.012
arch = [(HC - 0.070, 0.034), (HC - 0.057, 0.075), (HC + 0.057, 0.075), (HC + 0.070, 0.034),
        (HC + 0.058, 0.034), (HC + 0.047, 0.063), (HC - 0.047, 0.063), (HC - 0.058, 0.034)]
h = yz_prism("ACS-9_handle", arch, HW)
uv_box(h, 0.04)
geo.append(finish(h, M_BODY, 40))
for i, s in enumerate((-1, 1)):
    col = rbox(f"ACS-9_handle_collar_{i + 1}", (0.030, 0.019, 0.011), 0.003, 3)
    col.location = (0, HC + s * 0.0635, 0.0392)
    uv_box(col, 0.04)
    geo.append(finish(col, M_BODY, 40))

# grip: rubber sleeve with transverse ribs
parts = [rbox("g_core", (0.027, 0.086, 0.0150), 0.005, 3)]
parts[0].location = (0, HC, GRIP_Z)
for i in range(7):
    rb = rbox(f"g_rib_{i}", (0.0285, 0.0020, 0.0166), 0.0007, 2)
    rb.location = (0, HC - 0.036 + i * 0.012, GRIP_Z)
    parts.append(rb)
grip = merge("ACS-9_handle_grip", parts)
uv_box(grip, 0.03)
geo.append(finish(grip, M_RUBBER, 40))

# ---- power slider, side +X: slotted plate, knob at position 2, printed legend --------
SX = 0.0399
sp = rbox("ACS-9_slider_plate", (0.0034, 0.054, 0.0150), 0.0014, 2)
sp.location = (SX, 0.0, 0.0)
slot = rbox("slot_cutter", (0.010, 0.044, 0.0050), 0.0015, 2)
slot.location = (SX + 0.001, 0.0, 0.0)
boolean_cut(sp, slot)
uv_box(sp, 0.04)
geo.append(finish(sp, M_TRACK, 40))

kp = [rbox("k_cap", (0.0050, 0.0130, 0.0085), 0.0016, 3), rbox("k_stem", (0.0034, 0.0036, 0.0036), 0.0004, 1)]
kp[0].location = (0.0443, 0.0, 0.0)
kp[1].location = (0.0405, 0.0, 0.0)
for i in range(4):
    r_ = rbox(f"k_ridge_{i}", (0.0010, 0.0011, 0.0075), 0.0003, 1)
    r_.location = (0.0472, -0.0045 + i * 0.0030, 0.0)
    kp.append(r_)
knob = merge("ACS-9_slider", kp)
uv_box(knob, 0.02)
geo.append(finish(knob, M_STEEL, 40))      # position 2 (centre). Positions 1 / 3 at y = -/+ 0.016

legend = wrap_patch("ACS-9_slider_legend", +1, 0.0, 0.060, 0.010, math.asin(0.0128 / BODY_R), 0.00025, 40, 4)
geo.append(finish(legend, M_LEGEND, 40))

# ---- amber lamp, side +X, forward of the slider [PROPOSAL colour backed by the security-division indicator] -----
def revolve_x(name, pts, y_loc, steps=40):
    r = revolve(name, pts, steps)
    r.data.transform(Matrix.Rotation(math.radians(-90), 4, "Z"))          # local +Y -> +X
    r.location = (0, y_loc, 0)
    return r


LY = -0.045
lh = revolve_x("ACS-9_lamp_bezel", [(0.0034, 0.0385), (0.0052, 0.0385), (0.0052, 0.0408), (0.0049, 0.0413),
                                   (0.0037, 0.0413), (0.0034, 0.0409)], LY)
uv_box(lh, 0.02)
geo.append(finish(lh, M_STEEL, 40))
ll = revolve_x("ACS-9_lamp", [(0.0, 0.0390), (0.0035, 0.0390), (0.0035, 0.0402), (0.0028, 0.0410), (0.0, 0.0412)], LY)
geo.append(finish(ll, M_LAMP, 40))

# ---- serial / certification label, side -X (wrapped film) ---------------------------------------------
label = wrap_patch("ACS-9_label", -1, -0.050, 0.062, 0.017, 0.0, 0.00025, 48, 8)
geo.append(finish(label, M_LABEL, 40))

# ---- rear housing panel: removable, two quarter-turn screws, printed text, ICS mark ---------------
panel = revolve("ACS-9_rear_panel", [(0.0, Y_REAR - 0.0009), (PANEL_R, Y_REAR - 0.0009), (PANEL_R, PANEL_Y - 0.0004),
                                     (PANEL_R - 0.0004, PANEL_Y), (0.0, PANEL_Y)], 72)
uv_rear(panel, 0.060)
geo.append(finish(panel, M_REAR, 40))

for i, sx in enumerate((-1, 1)):
    sc = revolve(f"ACS-9_qt_screw_{i + 1}", [(0.0, PANEL_Y), (0.0048, PANEL_Y), (0.0048, PANEL_Y + 0.0012),
                                              (0.0040, PANEL_Y + 0.0020), (0.0, PANEL_Y + 0.0022)], 40)
    sc.location = (sx * 0.0150, 0.0, -0.0150)
    sl = rbox("slot_cutter", (0.0100, 0.0016, 0.0013), 0.0002, 1)
    sl.location = (sx * 0.0150, PANEL_Y + 0.0022, -0.0150)
    boolean_cut(sc, sl)
    uv_rev(sc, 0.02, 0.0048)
    geo.append(finish(sc, M_STEEL, 40))

# ICS mark: real geometry from Logo/src/ics_brand.py (same outline as the SVG kit), laid on the rear panel facing +Y so it
# reads correctly from behind. Mark space (x, y, thickness) -> world (-x, thickness, y). Size and relief are [PROPOSAL].
sys.path.insert(0, os.path.join(ROOT, "Logo", "src"))
import ics_brand_bpy as brand  # noqa: E402
for _ob in brand.build_mark("ACS-9_mark", 0.0105, M_BLUE, M_GOLD, small=False, t_blue=0.0004, t_gold=0.0005):
    _ob.data.transform(Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
    _ob.location = (0, PANEL_Y, MARK_Z)
    geo.append(finish(_ob, M_BLUE if _ob.name.endswith("_disc") else M_GOLD, 40))

# ---- shift every part so the origin sits at the grip; root and mounts --------------------------------------------
for o in geo:
    o.data.transform(Matrix.Translation(-ORIGIN) @ o.matrix_basis)
    o.matrix_basis = Matrix.Identity(4)

root = link(bpy.data.objects.new("ACS-9", None))
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 0.03
mounts = {
    "mount_ACS-9D_shroud": (0.0, Y_FRONT, 0.0),                                   # front face centre; baffle extends along -Y
    "mount_ACS-9RS_plate": (-0.030, 0.040, -math.sqrt(BODY_R ** 2 - 0.030 ** 2)),   # underside, 3 cm to -X
}
for n, loc in mounts.items():
    e = link(bpy.data.objects.new(n, None))
    e.empty_display_type = "ARROWS"
    e.empty_display_size = 0.01
    e.location = Vector(loc) - ORIGIN
    e.parent = root
for o in geo:
    o.parent = root

tris = sum(len(p.vertices) - 2 for o in geo for p in o.data.polygons)
print(f"STATS parts={len(geo)} triangles={tris}")
for o in sorted(geo, key=lambda o: -len(o.data.polygons))[:10]:
    print("  ", o.name, sum(len(p.vertices) - 2 for p in o.data.polygons))

# ---- save and export (before the studio is added) ----------------------------------------------------------
BLEND = os.path.join(OUT, "ACS-9.blend")
bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=False)
bpy.ops.file.make_paths_relative()                 # textures/ sits next to the .blend; no machine-specific paths
bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=False)
bpy.ops.object.select_all(action="DESELECT")
for o in [root] + geo + [o for o in coll.objects if o.name.startswith("mount_")]:
    o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(EXPORT_DIR, "ACS-9.fbx"), use_selection=True,
                         object_types={"MESH", "EMPTY"}, apply_scale_options="FBX_SCALE_ALL",
                         add_leaf_bones=False, mesh_smooth_type="FACE", path_mode="COPY", embed_textures=True)

# ---- previews ----------------------------------------------------------------------------------------------
P = lambda x, y, z: (x - ORIGIN.x, y - ORIGIN.y, z - ORIGIN.z)  # noqa: E731  body-centred -> grip-origin coordinates
cam = studio.setup(scene, -BEZEL_R - 0.0002 - ORIGIN.z)
shot = lambda n, loc, tgt, lens=70: cam.shot(os.path.join(PREVIEW_DIR, f"ACS-9_{n}.png"), P(*loc), P(*tgt), lens)  # noqa: E731
shot("hero", (0.30, -0.42, 0.22), (0.0, 0.0, 0.015), 70)
shot("aperture", (0.05, -0.26, 0.05), (0.0, -0.115, 0.0), 85)
shot("rear_mark", (-0.07, 0.30, 0.05), (0.0, 0.125, 0.0), 90)
shot("side_slider", (0.40, 0.0, 0.05), (0.04, -0.01, 0.004), 120)
scene.view_settings.exposure = 1.6                  # the key light misses the -X side
shot("side_label", (-0.40, -0.05, 0.03), (-0.04, -0.05, 0.0), 120)
scene.view_settings.exposure = 0.0
shot("top_handle", (0.06, 0.045, 0.45), (0.0, 0.045, 0.05), 70)
print("DONE")
