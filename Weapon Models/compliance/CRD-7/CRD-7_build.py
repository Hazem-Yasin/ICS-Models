"""
CRD-7 -- Compliance Restraint Device. Build script for Blender 5.x. v3, "hard" industrial look.

Run:  blender --background --python CRD-7_build.py -- <ICS-Models root>
Writes: Weapon Models/compliance/CRD-7/CRD-7.blend, Weapon Models/exports/CRD-7.fbx, Weapon Models/compliance/CRD-7/previews/*.png
Spec:   _specs/CRD-7.md   Canon: ICS-Writing/canon/weapons/compliance/CRD-7 ...md

Units: metres. Forward = -Y (the prongs). Up = +Z. Origin = centre of the grip.
Body coordinates below are measured from the body centre; OFFY moves the
grip centre to the origin.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crd7_textures as tx  # noqa: E402  (body texture set + shared detail dimensions)

ROOT = sys.argv[sys.argv.index("--") + 1]
PREVIEW_DIR = os.path.join(ROOT, "Weapon Models", "compliance", "CRD-7", "previews")
TEX_DIR = os.path.join(ROOT, "Weapon Models", "compliance", "CRD-7", "textures")
EXPORT_DIR = os.path.join(ROOT, "Weapon Models", "exports")
os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(TEX_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# ---- dimensions (m) --------------------------------------------------------
BODY_W, BODY_L, BODY_H = 0.050, 0.115, 0.030     # [PROPOSAL] canon: "size of a TV remote"
BODY_R = 0.004                                    # edge radius; flat side seat stays 22 mm
TOP = BODY_H / 2
HOUS_W, HOUS_L, HOUS_H = 0.038, 0.030, 0.022      # prong shroud
HOUS_Y = -0.0675
POCKET_DEPTH = 0.009
PRONG_R, PRONG_SPACING = 0.0022, 0.020
OFFY = -0.025                                     # grip centre -> origin

# ---- scene reset -----------------------------------------------------------
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


def place(ob, x, y, z):
    ob.location = (x, y + OFFY, z)
    return ob


def smooth(ob, angle=35):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
        except Exception:
            for p in ob.data.polygons:
                p.use_smooth = True


def rbox(name, size, r, segs=5):
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


def cyl(name, r, depth, axis="Z", segs=48):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=depth)
    if axis == "X":
        m = Matrix.Rotation(math.radians(90), 4, "Y")
    elif axis == "Y":
        m = Matrix.Rotation(math.radians(90), 4, "X")
    else:
        m = Matrix.Identity(4)
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    return mesh_from_bm(name, bm)


def sphere(name, r, segs=24):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=segs // 2, radius=r)
    return mesh_from_bm(name, bm)


def arc(name, r_in, r_out, a0, a1, thick, steps=24):
    """Flat annular arc from angle a0 to a1 (degrees), extruded +Z."""
    bm = bmesh.new()
    outer = [(r_out * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
              r_out * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]
    inner = [(r_in * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
              r_in * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps, -1, -1)]
    verts = [bm.verts.new((x, y, 0)) for x, y in outer + inner]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    mv = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, thick), verts=mv)
    return mesh_from_bm(name, bm)


def rprism(name, size, r, segs=4):
    """Box with only its vertical (Z) edges rounded: a rounded-rectangle outline extruded in Z."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    vert = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 1e-9]
    bmesh.ops.bevel(bm, geom=vert, offset=r, offset_type="OFFSET", profile=0.5, segments=segs, affect="EDGES")
    return mesh_from_bm(name, bm)


def ellipsoid(name, radii, u=8, v=6):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    for vt in bm.verts:
        vt.co.x *= radii[0]
        vt.co.y *= radii[1]
        vt.co.z *= radii[2]
    return mesh_from_bm(name, bm)


def boolean_cut(ob, cutter):
    mod = ob.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


# ---- materials -------------------------------------------------------------
mm = 0.001


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


def to_image(name, data, srgb, save=True):
    h, w = data.shape[:2]
    img = bpy.data.images.new(name, w, h, alpha=False)
    img.colorspace_settings.name = "sRGB" if srgb else "Non-Color"
    if data.ndim == 2:
        data = np.stack([data] * 3, -1)
    rgba = np.concatenate([np.clip(data, 0, 1), np.ones((h, w, 1))], -1).astype(np.float32)
    img.pixels.foreach_set(rgba.ravel())
    if save:
        img.filepath_raw = os.path.join(TEX_DIR, name + ".png")
        img.file_format = "PNG"
        img.save()
    return img


def textured(m, albedo=None, rough=None, normal=None):
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    for img, inp in ((albedo, "Base Color"), (rough, "Roughness")):
        if img is not None:
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = img
            nt.links.new(t.outputs["Color"], bsdf.inputs[inp])
    if normal is not None:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = normal
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(t.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])


M_BODY = mat("CRD-7_body", (0.17, 0.175, 0.185), 0.6)          # matte grey; textured below
M_METAL = mat("CRD-7_prong", (0.72, 0.73, 0.75), 0.30, 1.0)
M_BLUE = mat("CRD-7_logo_blue", (0.012, 0.027, 0.085), 0.45)  # ICS Deep Blue #1A2E52
M_GOLD = mat("CRD-7_logo_gold", (0.58, 0.39, 0.075), 0.35, 0.8)  # ICS Warm Gold #C9A84C
M_LENS = mat("CRD-7_emitter_lens", (0.02, 0.02, 0.03), 0.12)
M_AMBER = mat("CRD-7_indicator_charged", (1.0, 0.45, 0.02), 0.3, emit=(1.0, 0.5, 0.05), strength=1.6)
M_RED = mat("CRD-7_indicator_discharged", (0.9, 0.02, 0.02), 0.3, emit=(1.0, 0.03, 0.02), strength=1.6)
M_RED.use_fake_user = True   # swap onto the indicator for the discharged state
M_LED_ON = mat("CRD-7_led_on", (1.0, 0.45, 0.02), 0.25, emit=(1.0, 0.45, 0.04), strength=5.0)
M_LED_OFF = mat("CRD-7_led_off", (0.10, 0.035, 0.012), 0.18)
M_BRASS = mat("CRD-7_brass", (0.55, 0.38, 0.14), 0.34, 1.0)
M_GLASS = mat("CRD-7_glass", (0.85, 0.90, 0.95), 0.05)
for _k in ("Transmission Weight", "Alpha"):
    try:
        M_GLASS.node_tree.nodes["Principled BSDF"].inputs[_k].default_value = 0.92 if _k.startswith("Trans") else 0.55
    except KeyError:
        pass
M_GLASS.node_tree.nodes["Principled BSDF"].inputs["IOR"].default_value = 1.46
M_FUSEGLASS = mat("CRD-7_fuse_glass", (0.30, 0.27, 0.22), 0.1)       # smoked: the fuse in the holder has blown
M_FUSEGLASS.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.7
M_SOCK_RED = mat("CRD-7_socket_red", (0.45, 0.02, 0.015), 0.35)
M_SOCK_BLK = mat("CRD-7_socket_black", (0.012, 0.012, 0.014), 0.35)

# trim materials: one shared 1024 px atlas, one 512 px swatch each (0 ABS, 1 rubber, 2 steel, 3 red plastic)
trim_maps = tx.make_trim(TEX_DIR)
TRIM_IMG = {k: to_image(f"CRD-7_trim_{k}", trim_maps[k], k == "albedo") for k in ("albedo", "rough", "normal")}
M_ABS = mat("CRD-7_trim_abs", (0.04, 0.042, 0.048), 0.6)
M_RUBBER = mat("CRD-7_grip_rubber", (0.012, 0.012, 0.013), 0.86)
M_STEEL = mat("CRD-7_steel", (0.30, 0.31, 0.33), 0.34, 0.9)
M_BUTTON = mat("CRD-7_button", (0.27, 0.018, 0.016), 0.44)
SWATCH = {M_ABS: 0, M_RUBBER: 1, M_STEEL: 2, M_BUTTON: 3}
for m_ in SWATCH:
    textured(m_, TRIM_IMG["albedo"], TRIM_IMG["rough"], TRIM_IMG["normal"])
    if m_ is M_STEEL:
        m_.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.9

# the screen: emission image, amber when charged; the red image is the discharged swap-in
lcd_img = {k: to_image(f"CRD-7_lcd_{k}", tx.make_lcd(TEX_DIR, k == "charged"), True)
           for k in ("charged", "discharged")}


def lcd_mat(name, img):
    m = mat(name, (0.005, 0.005, 0.006), 0.16)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 1.7
    return m


M_LCD = lcd_mat("CRD-7_screen_charged", lcd_img["charged"])
M_LCD_RED = lcd_mat("CRD-7_screen_discharged", lcd_img["discharged"])
M_LCD_RED.use_fake_user = True


def finish(ob, material, angle=35):
    # Boolean cuts leave an empty slot 0 behind; clear it so every face uses this material
    ob.data.materials.clear()
    ob.data.materials.append(material)
    for p in ob.data.polygons:
        p.material_index = 0
    smooth(ob, angle)
    return ob


def trim(ob, material, angle=40, span=40.0):
    """finish() plus box-projected UVs into the material's atlas swatch (local mm, +-span/2 fills the swatch)."""
    finish(ob, material, angle)
    sw = SWATCH[material]
    u0, v0 = 0.5 * (sw % 2), 0.5 * (sw // 2)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        k = max(range(3), key=lambda i: abs(n[i]))
        for lp in f.loops:
            p = lp.vert.co * 1000.0
            a, b = ((p.x, p.y), (p.x, p.z), (p.y, p.z))[(2, 1, 0).index(k)]
            lp[uvl].uv = (u0 + min(max(0.25 + 0.5 * a / span, 0.01), 0.49),
                          v0 + min(max(0.25 + 0.5 * b / span, 0.01), 0.49))
    bm.to_mesh(ob.data)
    bm.free()
    return ob


# printed small parts: brass asset plate, maintenance tag, evidence tape [PROPOSAL story props]
plate_maps = tx.make_plates(TEX_DIR)
M_PLATE = mat("CRD-7_asset_plate", (0.5, 0.4, 0.2), 0.40, 0.85)
M_TAG = mat("CRD-7_service_tag", (0.6, 0.5, 0.3), 0.85)
M_TAPE = mat("CRD-7_evidence_tape", (0.03, 0.05, 0.12), 0.45)
for _m, _k in ((M_PLATE, "plate"), (M_TAG, "tag"), (M_TAPE, "tape")):
    textured(_m, to_image(f"CRD-7_{_k}", plate_maps[_k], True))

# ---- extra builders --------------------------------------------------------
def prism_poly(name, pts, height):
    """Closed 2D outline (x, y) in mm, extruded +Z by height (mm). Origin at the outline's local (0, 0, 0)."""
    bm = bmesh.new()
    face = bm.faces.new([bm.verts.new((x * mm, y * mm, 0)) for x, y in pts])
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, vec=(0, 0, height * mm), verts=[e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)])
    return mesh_from_bm(name, bm)


def ribbed(name, half_len, base_t, rib_h, centres, w_base, w_top, height, sx):
    """A plate with ribs: x outward (mm), y along the length, extruded in Z. sx = +1 / -1 picks the side."""
    pts = [(0, -half_len), (0, half_len), (base_t, half_len)]
    for yc in sorted(centres, reverse=True):
        pts += [(base_t, yc + w_base / 2), (base_t + rib_h, yc + w_top / 2),
                (base_t + rib_h, yc - w_top / 2), (base_t, yc - w_base / 2)]
    pts += [(base_t, -half_len)]
    return prism_poly(name, [(sx * x, y) for x, y in pts], height)


def sweep(P, radius, sides=6, closed=False, name="tube", swatch=1):
    """Tube along a numpy polyline P (mm, body frame). Parallel-transport frames, optional end caps."""
    P = np.asarray(P, float)
    n = len(P)
    T = (np.roll(P, -1, 0) - np.roll(P, 1, 0)) if closed else np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1)[:, None]
    n0 = np.cross(T[0], (0, 0, 1.0))
    if np.linalg.norm(n0) < 1e-6:
        n0 = np.cross(T[0], (1.0, 0, 0))
    N = [n0 / np.linalg.norm(n0)]
    for i in range(1, n):
        v = N[-1] - np.dot(N[-1], T[i]) * T[i]
        N.append(v / np.linalg.norm(v))
    N = np.array(N)
    B = np.cross(T, N)
    r = np.broadcast_to(np.asarray(radius, float), (n,))
    bm = bmesh.new()
    rings = []
    for i in range(n):
        ring = []
        for j in range(sides):
            a = math.tau * j / sides
            q = P[i] + r[i] * (math.cos(a) * N[i] + math.sin(a) * B[i])
            ring.append(bm.verts.new((q[0] * mm, q[1] * mm + OFFY, q[2] * mm)))
        rings.append(ring)
    u0, v0 = 0.5 * (swatch % 2), 0.5 * (swatch // 2)
    uvl = bm.loops.layers.uv.verify()
    idx = {v: (i, j) for i, ring in enumerate(rings) for j, v in enumerate(ring)}
    segs = n if closed else n - 1
    for i in range(segs):
        a, b = rings[i], rings[(i + 1) % n]
        for j in range(sides):
            f = bm.faces.new((a[j], a[(j + 1) % sides], b[(j + 1) % sides], b[j]))
            for lp in f.loops:
                ri, rj = idx[lp.vert]
                lp[uvl].uv = (u0 + 0.05 + 0.4 * (ri % 16) / 16.0, v0 + 0.05 + 0.4 * rj / sides)
    if not closed:
        for ring in (rings[0], rings[-1][::-1]):
            f = bm.faces.new(ring)
            for lp in f.loops:
                lp[uvl].uv = (u0 + 0.25, v0 + 0.25)
    return mesh_from_bm(name, bm)


def plate_box(name, size, r, material, segs=1):
    """Thin printed plate: top face is planar-mapped 0..1 into the material's image, every other face samples one corner."""
    ob = rbox(name, size, r, segs)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for lp in f.loops:
            p = lp.vert.co
            if f.normal.z > 0.9:
                lp[uvl].uv = (min(max(p.x / size[0] + 0.5, 0.0), 1.0), min(max(p.y / size[1] + 0.5, 0.0), 1.0))
            else:
                lp[uvl].uv = (0.5, 0.5)
    bm.to_mesh(ob.data)
    bm.free()
    finish(ob, material, 30)
    return ob


def xz_prism(name, pts, y0, y1):
    """Closed (x, z) outline in mm, extruded along Y from y0 to y1 (mm, body frame)."""
    bm = bmesh.new()
    face = bm.faces.new([bm.verts.new((x * mm, y0 * mm, z * mm)) for x, z in pts])
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, vec=(0, (y1 - y0) * mm, 0), verts=[e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)])
    ob = mesh_from_bm(name, bm)
    ob.location = (0, OFFY, 0)
    return ob


def orient(ob, cx, cy, cz):
    """Rotate so local x, y, z map to the given world directions."""
    ob.rotation_euler = Matrix(((cx[0], cy[0], cz[0]), (cx[1], cy[1], cz[1]), (cx[2], cy[2], cz[2]))).to_euler()
    return ob


def hinge(ob, px, py, pz, rx_deg):
    """Swing an already-placed (unrotated) object about an X-parallel hinge line through body-frame point (px, py, pz) mm."""
    pv = Vector((px * mm, py * mm + OFFY, pz * mm))
    ob.data.transform(Matrix.Translation(ob.location - pv))
    ob.location = pv
    ob.rotation_euler = (math.radians(rx_deg), 0, 0)
    return ob


def make_screw_template():
    """Slotted cross screw head: base at z=0, top at +0.7 mm. Instances share the mesh."""
    head = cyl("tmp_screw", 1.45 * mm, 0.7 * mm, "Z", 14)
    head.data.transform(Matrix.Translation((0, 0, 0.35 * mm)))
    for sz in ((2.4 * mm, 0.40 * mm, 0.8 * mm), (0.40 * mm, 2.4 * mm, 0.8 * mm)):
        c = rbox("cut_slot_x", sz, 0, 1)
        c.location.z = 0.7 * mm
        boolean_cut(head, c)
    trim(head, M_STEEL, 50)
    return head


screw_tpl = make_screw_template()
screw_n = [0]


def screw(x, y, z, face="top", sink=0.12):
    """Screw head on a surface at body-frame point (x, y, z) mm. face: top, bottom, px, mx."""
    screw_n[0] += 1
    ob = link(bpy.data.objects.new(f"CRD-7_screw_{screw_n[0]:02d}", screw_tpl.data))
    rot = {"top": (0, 0, 0), "bottom": (math.pi, 0, 0), "px": (0, math.pi / 2, 0), "mx": (0, -math.pi / 2, 0)}[face]
    dx, dz = {"top": (0, -sink), "bottom": (0, sink), "px": (-sink, 0), "mx": (sink, 0)}[face]
    ob.rotation_euler = rot
    ob.location = ((x + dx) * mm, y * mm + OFFY, (z + dz) * mm)
    return ob


parts = []

# ---- body ------------------------------------------------------------------
body = rbox("CRD-7_body", (BODY_W, BODY_L, BODY_H), BODY_R, 3)
place(body, 0, 0, 0)

# side emitter recess (+X): 15 mm aperture, ~3 mm deep, undocumented in the training module
cut = cyl("cut_emitter", 0.0075, 0.006, "X", 32)
place(cut, BODY_W / 2, 0, 0)
boolean_cut(body, cut)

# moulding seam [PROPOSAL]: a thin groove all the way round, below mid-height, where two shells would meet
seam_o = rprism("cut_seam_o", (BODY_W + 0.004, BODY_L + 0.004, tx.SEAM_W * mm), BODY_R + 0.002, 4)
seam_i = rprism("cut_seam_i", (BODY_W - 2 * tx.SEAM_D * mm, BODY_L - 2 * tx.SEAM_D * mm, tx.SEAM_W * mm * 3),
                BODY_R - tx.SEAM_D * mm, 4)
for o in (seam_o, seam_i):
    place(o, 0, 0, tx.SEAM_Z * mm)
boolean_cut(seam_o, seam_i)
boolean_cut(body, seam_o)

# rubber grip pockets [PROPOSAL]: both sides, rear half, 0.9 mm deep
PAD_Y, PAD_Z, PAD_LEN, PAD_H = 41.5, 0.5, 24.0, 16.0
for sx in (-1, 1):
    pk = rbox("cut_pad", (1.8 * mm, PAD_LEN * mm, (PAD_H + 1.0) * mm), 0.4 * mm, 1)
    place(pk, sx * BODY_W / 2, PAD_Y * mm, PAD_Z * mm)
    boolean_cut(body, pk)

# emitter shutter channel [PROPOSAL]: a rail on the +X face from the aperture toward the rear, 1.2 mm deep
ch = rbox("cut_channel", (2.4 * mm, 37.0 * mm, 17.0 * mm), 0.5 * mm, 1)
place(ch, BODY_W / 2, 9.0 * mm, 0)
boolean_cut(body, ch)

# top face: LCD pocket, safety-switch panel, thumb-button pocket
LCD_CY = tx.LCD_Y * mm
lp = rprism("cut_lcd", ((tx.LCD_W + 4.0) * mm, (tx.LCD_H + 2.0) * mm, 3.0 * mm), 1.3 * mm, 3)
place(lp, 0, LCD_CY, TOP)
boolean_cut(body, lp)

SW_Y = 48.5 * mm
sp = rprism("cut_safety", (26.0 * mm, 9.0 * mm, 2.2 * mm), 1.0 * mm, 3)
place(sp, 0, SW_Y, TOP)
boolean_cut(body, sp)

BTN_Y = tx.BTN_Y * mm
pocket_top = rprism("cut_btn_pocket", (0.0195, 0.0145, 0.002), 0.0025, 3)
place(pocket_top, 0, BTN_Y, TOP)
boolean_cut(body, pocket_top)

# underside: battery door recess [PROPOSAL], 1.2 mm deep, at the CRD-7R end
DOOR_Y = 42.0
dr = rprism("cut_door", (36.0 * mm, 22.0 * mm, 2.4 * mm), 2.0 * mm, 3)
place(dr, 0, DOOR_Y * mm, -TOP)
boolean_cut(body, dr)

# ---- v4 [PROPOSAL] cuts: mode thumb-wheel slot, test jack pocket, mode window, fuse recess, charge port, holster rails ----
WHEEL_X, WHEEL_Y, WHEEL_R = 19.9, -1.0, 5.5
JACK_X, JACK_Y = -15.5, 37.0
WIN_X, WIN_Y = 14.5, 37.0
FUSE_Y = 21.5
CHG_X = -16.5
RAIL_X = 18.5
wc = rbox("cut_wheel_slot", (2.2 * mm, 11.6 * mm, 12.0 * mm), 0.3 * mm, 1)
place(wc, WHEEL_X * mm, WHEEL_Y * mm, TOP - 5.5 * mm)
boolean_cut(body, wc)
jc = rprism("cut_jack", (11.6 * mm, 7.6 * mm, 6.0 * mm), 0.9 * mm, 3)
place(jc, JACK_X * mm, JACK_Y * mm, TOP)
boolean_cut(body, jc)
wn = rprism("cut_mode_window", (10.0 * mm, 4.0 * mm, 4.4 * mm), 0.8 * mm, 3)
place(wn, WIN_X * mm, WIN_Y * mm, TOP)
boolean_cut(body, wn)
fc = cyl("cut_fuse", 4.2 * mm, 5.0 * mm, "X", 32)
place(fc, -(BODY_W / 2 - 1.5 * mm) - 0.0005, FUSE_Y * mm, 0)
boolean_cut(body, fc)
pc = rbox("cut_charge", (6.0 * mm, 6.0 * mm, 4.4 * mm), 0.5 * mm, 1)
place(pc, CHG_X * mm, BODY_L / 2, 0)
boolean_cut(body, pc)
for sx in (-1, 1):                    # dovetail rail grooves along the underside, ending before the battery door
    rail = xz_prism("cut_rail", [(sx * (RAIL_X - 1.5), -15.3), (sx * (RAIL_X + 1.5), -15.3),
                                 (sx * (RAIL_X + 2.2), -12.5), (sx * (RAIL_X - 2.2), -12.5)], -50.0, 28.0)
    boolean_cut(body, rail)

# rear cap: quarter-turn release slot and a small battery-port recess
cap = cyl("CRD-7_cap", 0.0105, 0.0016, "Y", 32)
place(cap, 0, BODY_L / 2, 0)
slot = rbox("cut_slot", (0.015, 0.0016, 0.0017), 0)
place(slot, 0, BODY_L / 2 + 0.0008, 0.0)
boolean_cut(cap, slot)
port = rbox("cut_port", (0.007, 0.0016, 0.003), 0)
place(port, 0, BODY_L / 2 + 0.0008, -0.0065)
boolean_cut(cap, port)
trim(cap, M_ABS, 40)

finish(body, M_BODY, 40)


# ---- body UVs and texture set (box-projected into the atlas in crd7_textures) ---
def uv_body(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        c = f.calc_center_median() * 1000.0
        tile = tx.tile_of((n.x, n.y, n.z), (c.x, c.y, c.z))
        ox, oy, _, _ = tx.TILES[tile]
        for lp in f.loops:
            p = lp.vert.co * 1000.0
            tu, tv = tx.proj(tile, p.x, p.y, p.z)
            lp[uvl].uv = ((ox + tu) / tx.AWMM, (oy + tv) / tx.AWMM)
    bm.to_mesh(ob.data)
    bm.free()


uv_body(body)
maps = tx.make(TEX_DIR)
textured(M_BODY, to_image("CRD-7_body_albedo", maps["albedo"], True), to_image("CRD-7_body_roughness", maps["rough"], False),
         to_image("CRD-7_body_normal", maps["normal"], False))
_t = M_BODY.node_tree.nodes.new("ShaderNodeTexImage")                 # metallic mask: 1 = bare metal, 0 = print / paper
_t.image = to_image("CRD-7_body_metallic", maps["metal"], False)
M_BODY.node_tree.links.new(_t.outputs["Color"], M_BODY.node_tree.nodes["Principled BSDF"].inputs["Metallic"])

# ---- rubber grip pads: ribbed inserts in the pockets ------------------------------
for sx, tag in ((-1, "L"), (1, "R")):
    ys = [10.0 - 2.0 * k for k in range(11)]
    pad = ribbed(f"CRD-7_grip_{tag}", 12.0, 0.6, 0.45, ys, 1.5, 1.0, PAD_H, sx)
    place(pad, sx * (BODY_W / 2 - 0.9 * mm), PAD_Y * mm, (PAD_Z - PAD_H / 2) * mm)
    trim(pad, M_RUBBER, 40)

# ---- emitter shutter (steel, slid open toward the rear) [PROPOSAL] ------------------
sh = ribbed("CRD-7_shutter", 7.0, 1.0, 0.5, [-4.0, 0.0, 4.0], 1.4, 1.0, 16.2, 1)
place(sh, 23.9 * mm, 19.5 * mm, -8.1 * mm)
trim(sh, M_STEEL, 40)

# ---- LCD screen, bezel and charge LEDs [PROPOSAL] ---------------------------------
sc_bm = bmesh.new()
hw, hh = tx.LCD_W / 2, tx.LCD_H / 2
uvl = sc_bm.loops.layers.uv.verify()
vs = [sc_bm.verts.new((x * mm, y * mm, 0)) for x, y in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
fc = sc_bm.faces.new(vs)
for lp_, (u, v) in zip(fc.loops, ((1, 1), (0, 1), (0, 0), (1, 0))):   # seen from above, prongs up: image left = +X
    lp_[uvl].uv = (u, v)
screen = mesh_from_bm("CRD-7_screen", sc_bm)
if screen.data.polygons[0].normal.z < 0:
    screen.data.polygons[0].flip()
    screen.data.update()
place(screen, 0, LCD_CY, TOP - 0.9 * mm)
finish(screen, M_LCD, 30)

fo = rprism("tmp_bezel_o", ((tx.LCD_W + 3.0) * mm, (tx.LCD_H + 1.4) * mm, 1.15 * mm), 1.0 * mm, 3)
fi = rprism("cut_bezel_i", ((tx.LCD_W - 0.4) * mm, (tx.LCD_H - 0.4) * mm, 3.0 * mm), 0.5 * mm, 3)
place(fo, 0, LCD_CY, TOP - 0.825 * mm)
place(fi, 0, LCD_CY, TOP - 0.825 * mm)
boolean_cut(fo, fi)
fo.name = "CRD-7_screen_bezel"
trim(fo, M_ABS, 30)

for k, lx in enumerate((-10.0, -5.0, 0.0, 5.0, 10.0)):
    ring = cyl(f"CRD-7_led_ring_{k + 1}", 1.75 * mm, 0.5 * mm, "Z", 14)
    place(ring, lx * mm, 11.0 * mm, TOP + 0.05 * mm)
    trim(ring, M_STEEL, 40)
    led = ellipsoid(f"CRD-7_led_{k + 1}", (1.2 * mm, 1.2 * mm, 0.85 * mm), 12, 6)
    place(led, lx * mm, 11.0 * mm, TOP + 0.15 * mm)
    finish(led, M_LED_ON if k < 4 else M_LED_OFF, 60)

# ---- safety switch [PROPOSAL]: recessed panel, track, slider at SAFE, four corner screws -------
trk = rprism("CRD-7_safety_track", (17.0 * mm, 2.4 * mm, 0.5 * mm), 1.0 * mm, 3)
place(trk, 0, SW_Y, TOP - 1.1 * mm + 0.25 * mm)
trim(trk, M_ABS, 30)
knob = rbox("CRD-7_safety_slider", (5.0 * mm, 3.6 * mm, 2.1 * mm), 0.5 * mm, 1)
place(knob, 6.5 * mm, SW_Y, TOP - 1.0 * mm + 1.0 * mm)
trim(knob, M_STEEL, 40)
for sx_, sy_ in ((-11.4, -3.2), (11.4, -3.2), (-11.4, 3.2), (11.4, 3.2)):
    screw(sx_, SW_Y / mm + sy_, TOP / mm - 1.1)

# top plate screws, four corners
for sx_, sy_ in ((-17.5, -50.0), (17.5, -50.0), (-17.5, 51.0), (17.5, 51.0)):
    screw(sx_, sy_, TOP / mm)

# ---- thumb button, red, flanked by guard rails [PROPOSAL] ---------------------------------
btn = rbox("CRD-7_button", (0.017, 0.012, 0.0035), 0.0014, 4)
place(btn, 0, BTN_Y, TOP + 0.0007)
dish = sphere("cut_dish", 0.030, 12)                    # R30 dish, 0.35 mm deep: a thumb rest
place(dish, 0, BTN_Y, TOP + 0.0007 + 0.00175 + 0.030 - 0.00035)
boolean_cut(btn, dish)
trim(btn, M_BUTTON, 40)
for sx, tag in ((-1, "L"), (1, "R")):
    g = rbox(f"CRD-7_button_guard_{tag}", (1.8 * mm, 13.0 * mm, 2.6 * mm), 0.4 * mm, 1)
    place(g, sx * 11.8 * mm, BTN_Y, TOP + 1.0 * mm)
    trim(g, M_ABS, 40)

# ---- battery door on the underside [PROPOSAL]: ties to the CRD-7R battery port -------------
door = rprism("CRD-7_battery_door", (35.4 * mm, 21.4 * mm, 1.1 * mm), 1.8 * mm, 3)
place(door, 0, DOOR_Y * mm, -TOP + 0.55 * mm)
nt_ = rbox("cut_door_notch", (7.0 * mm, 3.0 * mm, 2.0 * mm), 0.6 * mm, 1)
place(nt_, 0, (DOOR_Y - 10.7) * mm, -TOP)
boolean_cut(door, nt_)
trim(door, M_ABS, 30)
for sx_ in (-14.0, 14.0):
    screw(sx_, DOOR_Y, -TOP / mm, "bottom")
for fx_, fy_ in ((-13.5, -47.0), (13.5, -47.0), (-13.5, 26.0), (13.5, 26.0)):
    ft = cyl(f"CRD-7_foot_{'L' if fx_ < 0 else 'R'}{'F' if fy_ < 0 else 'B'}", 2.4 * mm, 0.9 * mm, "Z", 16)
    place(ft, fx_ * mm, fy_ * mm, -TOP - 0.3 * mm)
    trim(ft, M_RUBBER, 40)

# ---- sealed service dial on the -X side [PROPOSAL] --------------------------------------------
col = cyl("CRD-7_dial_collar", 6.3 * mm, 0.9 * mm, "X", 32)
place(col, -(BODY_W / 2 + 0.2 * mm) + 0.0, -36.0 * mm, 0)
trim(col, M_STEEL, 40)
star = [(( 5.6 if i % 2 == 0 else 5.0) * math.cos(math.tau * i / 48), (5.6 if i % 2 == 0 else 5.0) * math.sin(math.tau * i / 48))
        for i in range(48)]
dial = prism_poly("CRD-7_dial", star, 3.4)
dial.rotation_euler = (0, -math.pi / 2, 0)
place(dial, -(BODY_W / 2 + 0.65 * mm), -36.0 * mm, 0)
trim(dial, M_ABS, 55)
dcap = cyl("CRD-7_dial_cap", 3.1 * mm, 0.6 * mm, "X", 24)
place(dcap, -(BODY_W / 2 + 0.65 * mm + 3.4 * mm), -36.0 * mm, 0)
trim(dcap, M_STEEL, 40)
mark = rbox("CRD-7_dial_mark", (0.5 * mm, 0.8 * mm, 3.2 * mm), 0.15 * mm, 1)       # red paint-marker seal line
place(mark, -(BODY_W / 2 + 0.65 * mm + 3.4 * mm), -36.0 * mm, 4.1 * mm)
trim(mark, M_BUTTON, 40)

# ---- prong shroud and prongs ----------------------------------------------
shroud = rbox("CRD-7_shroud", (HOUS_W, HOUS_L, HOUS_H), 0.004, 3)
place(shroud, 0, HOUS_Y, 0)
front = HOUS_Y - HOUS_L / 2
pocket = rbox("cut_pocket", (0.030, POCKET_DEPTH + 0.0005, 0.013), 0.001, 3)
place(pocket, 0, front + (POCKET_DEPTH - 0.0005) / 2, 0)   # opens through the front face
boolean_cut(shroud, pocket)
for k, vy in enumerate((-61.5, -65.0, -68.5, -72.0, -75.5)):   # vent slits on the shroud top [PROPOSAL]
    v = rbox("cut_vent", (16.0 * mm, 1.3 * mm, 4.0 * mm), 0.3 * mm, 1)
    place(v, 0, vy * mm, HOUS_H / 2)
    boolean_cut(shroud, v)
for sx in (-1, 1):                 # [PROPOSAL] plunger slots over the prongs: you can see the spring-loaded carriage ride in them
    sl_ = rbox("cut_plunger_slot", (2.4 * mm, 9.0 * mm, 5.0 * mm), 0.4 * mm, 1)
    place(sl_, sx * 10.0 * mm, -75.5 * mm, 9.7 * mm)
    boolean_cut(shroud, sl_)
trim(shroud, M_ABS, 40)
for sx_ in (-16.5, 16.5):
    screw(sx_, -76.5, HOUS_H / 2 * 1000.0 - 0.0)

pocket_bottom = front + POCKET_DEPTH          # y of the pocket floor
prong_len = 0.018
for sx, tag in ((-1, "L"), (1, "R")):
    p = cyl(f"CRD-7_prong_{tag}", PRONG_R, prong_len, "Y", 16)
    place(p, sx * PRONG_SPACING / 2, pocket_bottom - prong_len / 2, 0)
    finish(p, M_METAL, 60)
    tip = sphere(f"CRD-7_prong_tip_{tag}", PRONG_R, 8)
    place(tip, sx * PRONG_SPACING / 2, pocket_bottom - prong_len, 0)
    finish(tip, M_METAL, 90)
    collar = cyl(f"CRD-7_prong_collar_{tag}", PRONG_R * 1.6, 0.003, "Y", 16)
    place(collar, sx * PRONG_SPACING / 2, pocket_bottom - 0.0015, 0)
    trim(collar, M_ABS, 60)

# ---- emitter lens (+X), sits at the bottom of the recess -------------------
lens = cyl("CRD-7_emitter_lens", 0.0069, 0.0004, "X", 24)
place(lens, BODY_W / 2 - 0.0025 + 0.0002, 0, 0)
finish(lens, M_LENS, 40)

# ---- contact indicator (-X side) ------------------------------------------
ind = rbox("CRD-7_indicator", (0.0007, 0.024, 0.0045), 0.0002, 2)
place(ind, -BODY_W / 2 + 0.00032, -0.002, 0)
finish(ind, M_AMBER, 40)

# ---- logo: the ICS Earth Branch mark (circle + one gold arc, no serpent), from Logo/src/ics_brand.py -------------------
# Real geometry built from the same outline as the SVG kit. Sizes and the knock-out gap are [PROPOSAL], see Logo/BRAND_MARK.md.
sys.path.insert(0, os.path.join(ROOT, "Logo", "src"))
import ics_brand_bpy as brand  # noqa: E402
LOGO_Y = tx.LOGO_Y * mm
for _ob in brand.build_mark("CRD-7_logo", 0.0090, M_BLUE, M_GOLD, small=False, t_blue=0.0005, t_gold=0.0005):
    _ob.rotation_euler = (0, 0, math.pi)       # reads upright with the prongs at the top of the frame, like the printed text
    place(_ob, 0, LOGO_Y, TOP + 0.0001)
    finish(_ob, M_BLUE if _ob.name.endswith("_disc") else M_GOLD, 30)
    if _ob.name.endswith("_arc"):
        _ob.location.z += 0.0003

# ---- wrist lanyard [PROPOSAL]: rear eyelet, coiled cord, cord lock and a wrist loop --------
EYE_X = 17.5
boss = rbox("CRD-7_eyelet_boss", (5.0 * mm, 3.0 * mm, 6.5 * mm), 0.5 * mm, 1)
place(boss, EYE_X * mm, (BODY_L / 2 + 1.0) * mm, 0)
trim(boss, M_STEEL, 40)
th = np.linspace(0, math.tau, 28, endpoint=False)
ring_pts = np.stack([np.full_like(th, EYE_X), BODY_L / 2 + 4.6 + 3.4 * np.cos(th), 3.4 * np.sin(th)], -1)
eye = sweep(ring_pts, 0.75, 6, True, "CRD-7_eyelet_ring", 2)
finish(eye, M_STEEL, 50)

b0, b1, b2, b3 = (np.array(v, float) for v in ((EYE_X, BODY_L / 2 + 8.0, 0.0), (EYE_X, 80.0, -14.0), (30.0, 90.0, -12.2), (56.0, 112.0, -12.2)))
tt = np.linspace(0, 1, 700)[:, None]
cur = (1 - tt) ** 3 * b0 + 3 * (1 - tt) ** 2 * tt * b1 + 3 * (1 - tt) * tt ** 2 * b2 + tt ** 3 * b3
seg = np.linalg.norm(np.diff(cur, axis=0), axis=1)
arcl = np.concatenate([[0], np.cumsum(seg)])
PITCH, COIL_R = 3.0, 2.2
n_pts = int(arcl[-1] / PITCH * 12)
sl = np.linspace(0, arcl[-1], n_pts)
cen = np.stack([np.interp(sl, arcl, cur[:, i]) for i in range(3)], -1)
Tc = np.gradient(cen, axis=0)
Tc /= np.linalg.norm(Tc, axis=1)[:, None]
Nc = [np.cross(Tc[0], (0, 0, 1.0))]
Nc[0] /= np.linalg.norm(Nc[0])
for i in range(1, n_pts):
    v = Nc[-1] - np.dot(Nc[-1], Tc[i]) * Tc[i]
    Nc.append(v / np.linalg.norm(v))
Nc = np.array(Nc)
Bc = np.cross(Tc, Nc)
ph = sl / PITCH * math.tau
helix = cen + COIL_R * (np.cos(ph)[:, None] * Nc + np.sin(ph)[:, None] * Bc)
cord = sweep(helix, 0.5, 6, False, "CRD-7_lanyard_coil", 1)
finish(cord, M_RUBBER, 40)

end = cen[-1]
dirv = Tc[-1] * np.array([1, 1, 0])
dirv /= np.linalg.norm(dirv)
lock = cyl("CRD-7_lanyard_lock", 1.7 * mm, 6.0 * mm, "Y", 12)
lock.rotation_euler = (0, 0, math.atan2(-dirv[0], dirv[1]))
place(lock, end[0] * mm, end[1] * mm, end[2] * mm)
trim(lock, M_ABS, 50)
LOOP_R = 9.0
lc = end + dirv * (LOOP_R + 2.5)
th2 = np.linspace(0, math.tau, 36, endpoint=False)
loop_pts = np.stack([lc[0] + LOOP_R * np.cos(th2), lc[1] + LOOP_R * np.sin(th2), np.full_like(th2, -13.9)], -1)
wloop = sweep(loop_pts, 0.9, 6, True, "CRD-7_lanyard_loop", 1)
finish(wloop, M_RUBBER, 40)


# =====================================================================================================
# v4 [PROPOSAL] additions: real-device mechanics, wear, story props
# =====================================================================================================
# ---- thumb-wheel for the three modes (+X, beside the screen) -------------------------------------
wheel_pts = [((5.5 if i % 2 == 0 else 5.0) * math.cos(math.tau * i / 36), (5.5 if i % 2 == 0 else 5.0) * math.sin(math.tau * i / 36))
             for i in range(36)]
wheel = prism_poly("CRD-7_mode_wheel", wheel_pts, 1.6)
wheel.rotation_euler = (0, -math.pi / 2, 0)
place(wheel, (WHEEL_X + 0.8) * mm, WHEEL_Y * mm, 11.0 * mm)
trim(wheel, M_ABS, 50)
axle = cyl("CRD-7_mode_wheel_axle", 1.2 * mm, 2.6 * mm, "X", 12)
place(axle, WHEEL_X * mm, WHEEL_Y * mm, 11.0 * mm)
trim(axle, M_STEEL, 50)

# ---- mode window: a flag flipped by the shutter (RANGED while the shutter is open) ----------------
flag = rbox("CRD-7_mode_flag", (3.8 * mm, 2.4 * mm, 1.0 * mm), 0.25 * mm, 1)
place(flag, (WIN_X + 3.0) * mm, WIN_Y * mm, 13.3 * mm)
trim(flag, M_BUTTON, 40)
rail_m = rbox("CRD-7_mode_flag_track", (9.0 * mm, 0.6 * mm, 0.4 * mm), 0.1 * mm, 1)
place(rail_m, WIN_X * mm, WIN_Y * mm, 12.9 * mm)
trim(rail_m, M_STEEL, 40)
pane = rbox("CRD-7_mode_window_glass", (10.6 * mm, 4.6 * mm, 0.35 * mm), 0.15 * mm, 1)
place(pane, WIN_X * mm, WIN_Y * mm, 14.7 * mm)
finish(pane, M_GLASS, 30)

# ---- test jack: two sockets behind a hinged steel flap, for checking the 40 V capacitor ----------
for sx_, mt, tg in ((-2.4, M_SOCK_RED, "red"), (2.4, M_SOCK_BLK, "black")):
    jx = JACK_X + sx_
    col_ = cyl(f"CRD-7_jack_{tg}", 1.8 * mm, 2.0 * mm, "Z", 16)
    place(col_, jx * mm, JACK_Y * mm, 13.0 * mm)
    finish(col_, mt, 40)
    hole_ = cyl(f"CRD-7_jack_{tg}_bore", 0.95 * mm, 0.12 * mm, "Z", 12)
    place(hole_, jx * mm, JACK_Y * mm, 14.04 * mm)
    finish(hole_, M_ABS, 40)
    pin_ = cyl(f"CRD-7_jack_{tg}_pin", 0.42 * mm, 0.9 * mm, "Z", 8)
    place(pin_, jx * mm, JACK_Y * mm, 13.9 * mm)
    finish(pin_, M_METAL, 40)
jflap = rprism("CRD-7_jack_flap", (12.6 * mm, 8.6 * mm, 0.9 * mm), 0.8 * mm, 2)
place(jflap, JACK_X * mm, (JACK_Y - 0.0) * mm, TOP + 0.45 * mm)
trim(jflap, M_STEEL, 40)
hinge(jflap, JACK_X, JACK_Y + 4.5, TOP / mm + 0.45, -112)
jhinge = cyl("CRD-7_jack_hinge", 0.55 * mm, 11.0 * mm, "X", 10)
place(jhinge, JACK_X * mm, (JACK_Y + 4.5) * mm, TOP + 0.45 * mm)
trim(jhinge, M_STEEL, 40)

# ---- replaceable fuse holder (-X): steel bezel, clear cap, a blown glass fuse inside -------------
fuse_cap = cyl("CRD-7_fuse_cap", 3.3 * mm, 4.6 * mm, "X", 24)
place(fuse_cap, -23.3 * mm, FUSE_Y * mm, 0)
finish(fuse_cap, M_GLASS, 40)
bez_th = np.linspace(0, math.tau, 24, endpoint=False)
bez = sweep(np.stack([np.full_like(bez_th, -24.9), FUSE_Y + 3.85 * np.cos(bez_th), 3.85 * np.sin(bez_th)], -1), 0.5, 6, True, "CRD-7_fuse_bezel", 2)
finish(bez, M_STEEL, 50)
f_gl = cyl("CRD-7_fuse_body", 1.05 * mm, 3.2 * mm, "X", 12)
place(f_gl, -23.7 * mm, FUSE_Y * mm, 0)
finish(f_gl, M_FUSEGLASS, 40)
for sx_, nm in ((-1, "a"), (1, "b")):
    ec = cyl(f"CRD-7_fuse_end_{nm}", 1.15 * mm, 0.7 * mm, "X", 12)
    place(ec, (-23.7 + sx_ * 1.9) * mm, FUSE_Y * mm, 0)
    finish(ec, M_METAL, 40)
    wr = cyl(f"CRD-7_fuse_wire_{nm}", 0.14 * mm, 1.0 * mm, "X", 5)
    place(wr, (-23.7 + sx_ * 1.0) * mm, FUSE_Y * mm, 0)
    finish(wr, M_METAL, 40)

# ---- charge port (rear, beside the cap) with a rubber flap, open -------------------------------------
for k_, zc in enumerate((-1.1, 1.1)):
    ct = rbox(f"CRD-7_charge_contact_{k_ + 1}", (4.2 * mm, 0.5 * mm, 0.9 * mm), 0.12 * mm, 1)
    place(ct, CHG_X * mm, BODY_L / 2 - 2.8 * mm, zc * mm)
    finish(ct, M_BRASS, 40)
cflap = rbox("CRD-7_charge_flap", (8.8 * mm, 1.3 * mm, 7.8 * mm), 0.4 * mm, 1)
place(cflap, CHG_X * mm, BODY_L / 2 + 0.65 * mm, 0)
trim(cflap, M_RUBBER, 40)
hinge(cflap, CHG_X, BODY_L / 2 * 1000.0, 3.9, 38)
cstrap = rbox("CRD-7_charge_flap_strap", (4.4 * mm, 1.0 * mm, 1.6 * mm), 0.3 * mm, 1)
place(cstrap, CHG_X * mm, BODY_L / 2 + 0.5 * mm, 4.1 * mm)
trim(cstrap, M_RUBBER, 40)

# ---- prong guard: hinged steel cap, spring hinge pin, flipped up --------------------------------
GP_Y, GP_Z = -81.8, 12.0
g_out = rbox("CRD-7_guard", (33.0 * mm, 12.8 * mm, 19.0 * mm), 0.9 * mm, 2)
place(g_out, 0, -88.9 * mm, 0)
g_in = rbox("cut_guard_in", (30.6 * mm, 13.8 * mm, 16.6 * mm), 0.5 * mm, 1)
place(g_in, 0, -87.2 * mm, 0)
boolean_cut(g_out, g_in)
trim(g_out, M_STEEL, 40)
g_tab = rbox("CRD-7_guard_tab", (8.0 * mm, 1.6 * mm, 2.2 * mm), 0.4 * mm, 1)
place(g_tab, 0, -95.8 * mm, -8.0 * mm)
trim(g_tab, M_STEEL, 40)
g_arms = []
for sx in (-1, 1):
    a_ = rbox(f"CRD-7_guard_arm_{'L' if sx < 0 else 'R'}", (3.0 * mm, 3.2 * mm, 5.0 * mm), 0.5 * mm, 1)
    place(a_, sx * 12.0 * mm, GP_Y * mm, 10.9 * mm)
    trim(a_, M_STEEL, 40)
    g_arms.append(a_)
for ob_ in [g_out, g_tab] + g_arms:
    hinge(ob_, 0, GP_Y, GP_Z, -78)
for sx in (-1, 1):
    ear = rbox(f"CRD-7_guard_ear_{'L' if sx < 0 else 'R'}", (3.0 * mm, 3.2 * mm, 2.8 * mm), 0.5 * mm, 1)
    place(ear, sx * 5.5 * mm, GP_Y * mm, 11.9 * mm)
    trim(ear, M_STEEL, 40)
gpin = cyl("CRD-7_guard_pin", 0.9 * mm, 35.0 * mm, "X", 12)
place(gpin, 0, GP_Y * mm, GP_Z * mm)
trim(gpin, M_STEEL, 50)
for sx in (-1, 1):
    hd = cyl("CRD-7_guard_pin_head", 1.4 * mm, 0.9 * mm, "X", 12)
    place(hd, sx * 17.8 * mm, GP_Y * mm, GP_Z * mm)
    trim(hd, M_STEEL, 50)
ph_ = np.linspace(0, 5 * math.tau, 64)
spring_pts = np.stack([13.9 + 3.0 * ph_ / (5 * math.tau), GP_Y + 1.7 * np.cos(ph_), GP_Z + 1.7 * np.sin(ph_)], -1)
sprg = sweep(spring_pts, 0.26, 5, False, "CRD-7_guard_spring", 2)
finish(sprg, M_STEEL, 50)

# ---- spring-loaded prongs: carriages riding in slots on the shroud top, with visible springs -----------
for sx, tag in ((-1, "L"), (1, "R")):
    cx_ = sx * 10.0
    blk = rbox(f"CRD-7_plunger_{tag}", (1.7 * mm, 3.8 * mm, 2.0 * mm), 0.3 * mm, 1)
    place(blk, cx_ * mm, -76.8 * mm, 8.4 * mm)
    trim(blk, M_STEEL, 40)
    stem = rbox(f"CRD-7_plunger_stem_{tag}", (0.9 * mm, 1.0 * mm, 5.0 * mm), 0.2 * mm, 1)
    place(stem, cx_ * mm, -76.8 * mm, 6.0 * mm)
    trim(stem, M_STEEL, 40)
    ph2 = np.linspace(0, 5 * math.tau, 60)
    sp2 = np.stack([cx_ + 0.75 * np.cos(ph2), -74.9 + 3.5 * ph2 / (5 * math.tau), 8.4 + 0.75 * np.sin(ph2)], -1)
    s2 = sweep(sp2, 0.17, 5, False, f"CRD-7_plunger_spring_{tag}", 2)
    finish(s2, M_STEEL, 50)

# ---- holster rails: nothing to add (the dovetail grooves are cut in the body); the belt clip is its own attachment ----

# ---- asset-number plate and rivets, underside [PROPOSAL story: this unit belonged to a transitioned PTKW officer] ----
plate_y = -13.5
plate = plate_box("CRD-7_asset_plate", (22.0 * mm, 7.4 * mm, 0.8 * mm), 0.5 * mm, M_PLATE)
plate.rotation_euler = (math.pi, 0, 0)
place(plate, 0, plate_y * mm, -TOP - 0.1 * mm)
for sx_ in (-1, 1):
    rv = cyl("CRD-7_asset_plate_rivet", 0.65 * mm, 0.35 * mm, "Z", 10)
    place(rv, sx_ * 9.4 * mm, plate_y * mm, -TOP - 0.62 * mm)
    finish(rv, M_BRASS, 50)

# ---- evidence tape across the battery-door seam [PROPOSAL story] -----------------------------------------
tape = plate_box("CRD-7_evidence_tape", (42.0 * mm, 6.0 * mm, 0.3 * mm), 0.1 * mm, M_TAPE)
tape.rotation_euler = (math.pi, 0, 0)
place(tape, 0, 51.5 * mm, -TOP - 0.1 * mm)

# ---- maintenance tag on a string from the eyelet [PROPOSAL story: service date, overdue] -----------------
A_ = np.array([EYE_X, BODY_L / 2 + 4.6, -3.4])
H_ = np.array([11.0, 68.0, -14.5])
dh = (H_ - A_)
dh[2] = 0
dh /= np.linalg.norm(dh)
uu = (H_ - A_) / np.linalg.norm(H_ - A_)
ww = np.array([0, 0, 1.0]) - uu[2] * uu
ww /= np.linalg.norm(ww)
mid_ = (A_ + H_) / 2
half_ = np.linalg.norm(H_ - A_) / 2
th3 = np.linspace(0, math.tau, 28, endpoint=False)
string_pts = mid_ + half_ * np.cos(th3)[:, None] * uu + 2.0 * np.sin(th3)[:, None] * ww
tstring = sweep(string_pts, 0.28, 4, True, "CRD-7_tag_string", 1)
finish(tstring, M_RUBBER, 40)
tag = plate_box("CRD-7_service_tag", (24.0 * mm, 14.0 * mm, 0.6 * mm), 0.3 * mm, M_TAG)
phi = math.atan2(dh[1], dh[0])
cen_ = H_ + 9.4 * dh
tag.rotation_euler = (0, 0, phi)
tag.location = (cen_[0] * mm, cen_[1] * mm + OFFY, -14.7 * mm)

# Printed text, the underside label, the sticker and the scratches are all in the body texture
# (crd7_textures.py), not geometry.

# ---- root, mount points -----------------------------------------------------
root = link(bpy.data.objects.new("CRD-7", None))
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 0.02
mounts = {
    "mount_CRD-7X_emitter": (BODY_W / 2, 0, 0),                  # 15 mm aperture, 22 mm seat
    "mount_CRD-7R_battery_port": (0, BODY_L / 2 + 0.0008, -0.0065),  # centre of the port cut on the rear cap
    "mount_prongs": (0, front, 0),
    "mount_holster_rails": (0, -11.0 * mm, -TOP),             # centre of the dovetail rails on the underside
}
for n, (x, y, z) in mounts.items():
    e = link(bpy.data.objects.new(n, None))
    e.empty_display_type = "ARROWS"
    e.empty_display_size = 0.006
    place(e, x, y, z)
    e.parent = root
bpy.data.objects.remove(screw_tpl, do_unlink=True)      # instances keep the shared screw mesh
allmesh = [o for o in coll.objects if o.type == "MESH"]
for o in allmesh:
    o.parent = root
geo = allmesh

tris = sum(len(p.vertices) - 2 for o in geo for p in o.data.polygons)
print(f"STATS parts={len(geo)} triangles={tris}")
for o in sorted(geo, key=lambda o: -len(o.data.polygons))[:8]:
    print("  ", o.name, sum(len(p.vertices) - 2 for p in o.data.polygons))

# ---- save and export --------------------------------------------------------
BLEND = os.path.join(ROOT, "Weapon Models", "compliance", "CRD-7", "CRD-7.blend")
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.file.make_paths_relative()            # textures/ sits next to the .blend; no machine-specific paths
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.object.select_all(action="DESELECT")
for o in [root] + geo + [o for o in coll.objects if o.name.startswith("mount_")]:
    o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(EXPORT_DIR, "CRD-7.fbx"), use_selection=True,
                         object_types={"MESH", "EMPTY"}, apply_scale_options="FBX_SCALE_ALL",
                         add_leaf_bones=False, mesh_smooth_type="FACE",
                         path_mode="COPY", embed_textures=True)

# ---- studio and previews ----------------------------------------------------
floor = link(bpy.data.objects.new("studio_floor", bpy.data.meshes.new("studio_floor")))
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.5)
bm.to_mesh(floor.data)
bm.free()
floor.location = (0, 0, -BODY_H / 2 - 0.0002)
floor.data.materials.append(mat("studio_floor", (0.45, 0.44, 0.42), 0.75))

world = bpy.data.worlds.new("studio")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.88, 0.88, 0.90, 1)
bg.inputs["Strength"].default_value = 0.30
scene.world = world


def sun(name, rot, energy, angle=12, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, "SUN")
    ld.energy = energy
    ld.angle = math.radians(angle)
    ld.color = color
    o = link(bpy.data.objects.new(name, ld))
    o.rotation_euler = [math.radians(a) for a in rot]


sun("key", (50, 0, 35), 1.15, 10, (1.0, 0.96, 0.9))
sun("fill", (60, 0, -120), 0.35, 25, (0.9, 0.93, 1.0))
sun("rim", (110, 0, 160), 0.55, 15)

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1500, 1000
scene.view_settings.view_transform = "Standard"

cam_data = bpy.data.cameras.new("cam")
cam = link(bpy.data.objects.new("cam", cam_data))
scene.camera = cam
target = link(bpy.data.objects.new("cam_target", None))
target.location = (0, -0.045, 0)
con = cam.constraints.new("TRACK_TO")
con.target = target
con.track_axis = "TRACK_NEGATIVE_Z"
con.up_axis = "UP_Y"


def shot(name, loc, lens=85, ortho=None):
    cam.location = loc
    cam_data.lens = lens
    if ortho:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho
    else:
        cam_data.type = "PERSP"
    scene.render.filepath = os.path.join(PREVIEW_DIR, f"CRD-7_{name}.png")
    bpy.ops.render.render(write_still=True)


shot("hero", (0.30, -0.36, 0.20), 95)
shot("side_emitter", (0.40, -0.02, 0.05), 100)
shot("rear_indicator", (-0.34, 0.30, 0.16), 95)
target.location = (0.02, 0.04, -0.010)
shot("lanyard", (0.18, 0.30, 0.22), 85)
target.location = (0.0, -0.085, 0.01)
shot("prong_guard", (0.14, -0.30, 0.14), 90)
target.location = (-0.006, 0.030, 0.0)
shot("rear_ports", (-0.17, 0.26, 0.10), 100)
target.location = (-0.025, -0.0035, 0.0)
shot("side_fuse", (-0.30, -0.06, 0.05), 100)
con.mute = True
cam.rotation_euler = (0, 0, math.pi)          # straight down, prongs at the top of the frame
shot("top", (0.0, -0.035, 0.6), ortho=0.22)
shot("top_detail", (0.0, -0.025, 0.6), ortho=0.10)
shot("logo", (0.0, tx.LOGO_Y * mm + OFFY, 0.6), ortho=0.032)
shot("shroud_top", (0.0, -0.085, 0.6), ortho=0.075)
shot("top_controls", (0.0, 0.002, 0.6), ortho=0.11)
# underside label: flip the tool over (about Y, so the prong end stays at the top of the frame)
root.rotation_euler = (0, math.pi, 0)
floor.location.z = -(BODY_H / 2 + 0.0030)
shot("underside", (0.0, -0.035, 0.6), ortho=0.22)
print("DONE")
