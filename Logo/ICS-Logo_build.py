"""
ICS Earth Branch emblem as an editable 3D model.  Writes Logo/ICS-Logo.blend and previews in Logo/previews/.

Run (Blender 5.2, from WSL):
  "/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --python Logo/ICS-Logo_build.py -- "$(wslpath -w <ICS-Models root>)"

Everything is generated; hand edits in the .blend are lost on rebuild, so change this script (or copy the .blend first).
Layout copies Logo/build_brand.py section 10 (the emblem), 1 unit = 1 m, emblem 1 m wide, standing in the XZ plane and
facing -Y (so numpad 1 = front view). The mark itself comes from Logo/src/ics_brand.py, the single source of its geometry.

How to edit in Blender:
  * Words:      select a text object (e.g. ICS-Logo_text_top), Tab into edit mode and retype, or change the string in
                Properties > Data > ... The ring texts bend live through a Curve modifier, so any wording follows the ring.
  * Colours:    Materials ICS-Logo_blue / _gold / _paper. Change one and every part using it follows.
  * Thickness:  Properties > Data > Geometry > Extrude on text; Bevel modifier on the base plate.
  * Tick ring:  one mesh per tick weight (minor / major / zero). They are not text; edit in edit mode.
All shapes beyond the canon mark (Doc 2.32) are [PROPOSAL], see Logo/BRAND_MARK.md.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = sys.argv[sys.argv.index("--") + 1]
LOGO = os.path.join(ROOT, "Logo")
sys.path.insert(0, os.path.join(LOGO, "src"))
import ics_brand as b            # noqa: E402
import ics_brand_bpy as brand    # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"

W = 1100.0
K = 1.0 / W            # metres per design pixel
CX = CY = W / 2        # emblem centre in design pixels
R = W * 0.46           # seal radius
FS = W * 0.046         # ring text size
T0 = 0.020             # base plate thickness


def P(x, y):           # design px (y down) -> metres in the logo plane (y up), centre at origin
    return ((x - CX) * K, -(y - CY) * K)


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def material(name, rgb, metallic, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (*rgb, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*rgb, 1)
    return m


M_BLUE = material("ICS-Logo_blue", b.BLUE_LIN, 0.0, 0.5)
M_GOLD = material("ICS-Logo_gold", b.GOLD_LIN, 0.55, 0.38)
M_PAPER = material("ICS-Logo_paper", lin(b.PAPER_HEX), 0.0, 0.55)

# ---- scene structure ------------------------------------------------------------------------------------------------
top = bpy.data.collections.new("ICS-Logo")
scene.collection.children.link(top)
COLS = {}
for n in ("Base", "Rings", "Ticks", "Text", "Mark", "Ribbon", "Plaque"):
    c = bpy.data.collections.new(f"ICS-Logo_{n}")
    top.children.link(c)
    COLS[n] = c

root = bpy.data.objects.new("ICS-Logo_ROOT", None)
root.empty_display_type = "ARROWS"
root.empty_display_size = 0.15
root.rotation_euler = (math.radians(90), 0, 0)      # logo plane XY -> XZ, faces -Y
top.objects.link(root)
root["note"] = "Rebuilt by Logo/ICS-Logo_build.py. Canon: ICS-Writing Doc 2.32. Extras are [PROPOSAL], see Logo/BRAND_MARK.md"


def put(ob, col, mat=None, z=0.0, loc=None):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    COLS[col].objects.link(ob)
    ob.parent = root
    if mat is not None:
        ob.data.materials.append(mat)
    if loc is not None:
        ob.location = loc
    return ob


def finish(bm, name):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


def circle_poly(r, n=160):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def pill_poly(cx, cy, w, h, n=40):
    """Stadium outline, always 2*n points, so an outer and an inner pill pair up point by point."""
    r = h / 2
    pts = []
    for i in range(n):
        a = -math.pi / 2 + math.pi * i / (n - 1)
        pts.append((cx + w / 2 - r + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(n):
        a = math.pi / 2 + math.pi * i / (n - 1)
        pts.append((cx - w / 2 + r + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def band(name, outer, inner, z0, t):
    """Solid band between two equal-length loops, from z0 up by t."""
    bm = bmesh.new()
    n = len(outer)
    lo = [bm.verts.new((*outer[i], z0)) for i in range(n)]
    li = [bm.verts.new((*inner[i], z0)) for i in range(n)]
    uo = [bm.verts.new((*outer[i], z0 + t)) for i in range(n)]
    ui = [bm.verts.new((*inner[i], z0 + t)) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((uo[i], uo[j], ui[j], ui[i]))
        bm.faces.new((lo[i], li[i], li[j], lo[j]))
        bm.faces.new((lo[i], lo[j], uo[j], uo[i]))
        bm.faces.new((li[j], li[i], ui[i], ui[j]))
    return finish(bm, name)


def ring(name, r, width, z0, t, n=192):
    return band(name, circle_poly(r + width / 2, n), circle_poly(r - width / 2, n), z0, t)


def smooth(ob):
    for p in ob.data.polygons:
        p.use_smooth = True


# ---- base plate -----------------------------------------------------------------------------------------------------
base = brand._poly_obj("ICS-Logo_base", circle_poly(R * K, 192), T0, 0.0)
put(base, "Base", M_BLUE)
bev = base.modifiers.new("Bevel", "BEVEL")
bev.width, bev.segments, bev.limit_method = 0.0025, 3, "ANGLE"

# ---- hairline rings (paper) -----------------------------------------------------------------------------------------
for nm, rr, ww in (("ring_outer", 0.895, 0.003), ("ring_inner", 0.545, 0.003)):
    put(ring(f"ICS-Logo_{nm}", R * rr * K, W * ww * K, T0, 0.0018), "Rings", M_PAPER)
put(ring("ICS-Logo_ring_rim", R * 0.985 * K, W * 0.006 * K, T0, 0.0025), "Rings", M_GOLD)   # [PROPOSAL] gold rim bead

# ---- 300 cycle ticks: minor, major (every 25th) and the gold zero tick ----------------------------------------------
ticks = {"minor": bmesh.new(), "major": bmesh.new(), "zero": bmesh.new()}


def tick_box(bm, ang, r_a, r_b, w, z0, h):
    rm, ln = (r_a + r_b) / 2, abs(r_a - r_b)
    rad, tan = Vector((math.sin(ang), math.cos(ang))), Vector((math.cos(ang), -math.sin(ang)))
    cen = rad * rm
    c = [cen + rad * (sx * ln / 2) + tan * (sy * w / 2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    lo = [bm.verts.new((p.x, p.y, z0)) for p in c]
    hi = [bm.verts.new((p.x, p.y, z0 + h)) for p in c]
    bm.faces.new(hi)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))


for i in range(300):
    kind = "zero" if i == 0 else ("major" if i % 25 == 0 else "minor")
    r0, r1 = R * 0.965 * K, R * (0.915 if kind != "minor" else 0.945) * K
    w = W * (0.0042 if kind != "minor" else 0.0022) * K
    tick_box(ticks[kind], math.radians(i * 1.2), r0, r1, w, T0, 0.0022)
for kind, bm in ticks.items():
    put(finish(bm, f"ICS-Logo_ticks_{kind}"), "Ticks", M_GOLD if kind == "zero" else M_PAPER)

# ---- studs ----------------------------------------------------------------------------------------------------------
for nm, sx in (("stud_L", -1), ("stud_R", 1)):
    st = brand._poly_obj(f"ICS-Logo_{nm}", circle_poly(W * 0.0085 * K, 32), 0.004, T0)
    put(st, "Rings", M_GOLD, loc=(sx * R * 0.72 * K, 0, 0))

# ---- the canon mark -------------------------------------------------------------------------------------------------
Rm = W * 0.178 * K
x0, x1, y0, y1 = b.mark_bbox(False)
mcx, mcy = (x0 + x1) / 2, (y0 + y1) / 2
disc, arc = brand.build_mark("ICS-Logo_mark", Rm, M_PAPER, M_GOLD, t_blue=0.006, t_gold=0.0085, circle_segs=96, arc_steps=120)
for ob in (disc, arc):
    ob.data.materials.clear()
disc.data.materials.append(M_PAPER)
arc.data.materials.append(M_GOLD)
put(disc, "Mark", loc=(mcx * Rm, mcy * Rm, T0))
put(arc, "Mark", loc=(mcx * Rm, mcy * Rm, T0))

# ---- text -----------------------------------------------------------------------------------------------------------
FONT = bpy.data.fonts.load(os.path.join(LOGO, "fonts", "VarelaRound-Regular.ttf"))


def text(name, body, size, mat, col, loc=(0, 0, 0), extrude=0.0028, ax="CENTER", ay="BOTTOM", spacing=1.0, bold=0.012):
    d = bpy.data.curves.new(name, "FONT")
    d.body, d.font, d.size = body, FONT, size
    d.extrude, d.align_x, d.align_y = extrude, ax, ay
    d.space_character = spacing
    d.offset = size * bold                 # Varela Round has one weight; this thickens the outline
    d.resolution_u = 6
    d.materials.append(mat)
    ob = bpy.data.objects.new(name, d)
    scene.collection.objects.link(ob)
    return put(ob, col, loc=loc)


def path_circle(name, r, cw, start_deg, n=240):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sp.points.add(n - 1)
    for i in range(n):
        a = math.radians(start_deg + (-1 if cw else 1) * 360 * i / n)
        sp.points[i].co = (r * math.cos(a), r * math.sin(a), 0, 1)
    sp.use_cyclic_u = True
    ob = bpy.data.objects.new(name, cu)
    scene.collection.objects.link(ob)
    put(ob, "Text")
    ob.hide_render = True
    ob.hide_viewport = False
    return ob


r_top = R * 0.675 * K
r_bot = r_top + 0.72 * FS * 0.80 * K
# top: clockwise from 12 o'clock, letters stand outward. bottom: counter-clockwise from 6 o'clock, letters stand inward
pt = path_circle("ICS-Logo_path_top", r_top, True, 90)
pb = path_circle("ICS-Logo_path_bottom", r_bot, False, -90)
tt = text("ICS-Logo_text_top", "ICS · EARTH BRANCH", FS * K, M_PAPER, "Text", loc=(0, 0, T0), spacing=1.25)
tb = text("ICS-Logo_text_bottom", "LABOR SOURCE #349", FS * 0.80 * K, M_PAPER, "Text", loc=(0, 0, T0), spacing=1.25)
for t_ob, c_ob in ((tt, pt), (tb, pb)):
    m = t_ob.modifiers.new("Curve", "CURVE")
    m.object, m.deform_axis = c_ob, "POS_X"
    c_ob.location = (0, 0, T0)

# ribbon (gold pill, blue inner outline, blue tagline) and the dates plaque
rw, rh = W * 0.84, W * 0.108
rcy = W * 0.905 + rh / 2
rx, ry = P(CX, rcy)
rib = brand._poly_obj("ICS-Logo_ribbon", [(rx + px * K, ry + py * K) for px, py in pill_poly(0, 0, rw, rh)], 0.012, T0)
put(rib, "Ribbon", M_GOLD)
inset = W * 0.012
outl = band("ICS-Logo_ribbon_outline",
            [(rx + px * K, ry + py * K) for px, py in pill_poly(0, 0, rw - 2 * inset, rh - 2 * inset)],
            [(rx + px * K, ry + py * K) for px, py in pill_poly(0, 0, rw - 2 * inset - W * 0.0056, rh - 2 * inset - W * 0.0056)],
            T0 + 0.012, 0.0016)
put(outl, "Ribbon", M_BLUE)
tag = text("ICS-Logo_text_tagline", "BECAUSE YOU’RE WORTH THE INVESTMENT", rh * 0.285 * K, M_BLUE, "Ribbon",
           loc=(rx, ry, T0 + 0.012), ay="CENTER", spacing=1.05, extrude=0.0022)
bpy.context.view_layer.update()
want = rw * 0.80 * K
tag.data.size *= want / tag.dimensions.x
tag.data.offset = tag.data.size * 0.012

pw, ph = W * 0.50, W * 0.050
px_, py_ = P(CX, W * 1.065 - ph * 0.12)
plq = brand._poly_obj("ICS-Logo_plaque", [(px_ + x * K, py_ + y * K) for x, y in pill_poly(0, 0, pw, ph)], 0.012, 0.0)
put(plq, "Plaque", M_BLUE)
dts = text("ICS-Logo_text_dates", "EST. CYCLE 290 · CYCLE 300", W * 0.026 * K, M_PAPER, "Plaque", loc=(px_, py_, 0.012),
           ay="CENTER", spacing=1.3, extrude=0.0018)

smooth(base)           # only the round base plate is smooth-shaded; ribbon and plaque stay flat-faced

# ---- preview studio (not part of the logo; own collection) ----------------------------------------------------------
pv = bpy.data.collections.new("Preview")
scene.collection.children.link(pv)


def obj(o):
    pv.objects.link(o)
    return o


world = bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.30, 0.31, 0.34, 1)
bg.inputs["Strength"].default_value = 0.5
for nm, loc, e, sz in (("key", (-1.2, -1.6, 1.4), 60, 1.6), ("fill", (1.6, -1.2, 0.2), 25, 2.0), ("rim", (0.4, -1.2, -1.0), 25, 1.5)):
    ld = bpy.data.lights.new(nm, "AREA")
    ld.energy, ld.size = e, sz
    lo = obj(bpy.data.objects.new(nm, ld))
    lo.location = loc
    d = Vector((0, 0, 0)) - lo.location
    lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

cam_d = bpy.data.cameras.new("cam")
cam = obj(bpy.data.objects.new("ICS-Logo_cam", cam_d))
scene.camera = cam
scene.render.engine = "CYCLES"
scene.view_settings.view_transform = "Standard"   # brand colours as specified, no filmic wash-out
scene.cycles.samples = 48
scene.cycles.use_denoising = False
scene.render.resolution_x = scene.render.resolution_y = 1400
os.makedirs(os.path.join(LOGO, "previews"), exist_ok=True)


def shoot(fname, loc, target, ortho_scale=None, lens=60):
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if ortho_scale:
        cam_d.type, cam_d.ortho_scale = "ORTHO", ortho_scale
    else:
        cam_d.type, cam_d.lens = "PERSP", lens
    scene.render.filepath = os.path.join(LOGO, "previews", fname)
    bpy.ops.render.render(write_still=True)


shoot("ICS-Logo_front.png", (0, -3, -0.1), (0, 0, -0.1), ortho_scale=1.3)
shoot("ICS-Logo_angle.png", (0.75, -1.5, 0.35), (0, 0, -0.04), lens=50)

blend = os.path.join(LOGO, "ICS-Logo.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend)
print("saved", blend)
print("exit 0")
