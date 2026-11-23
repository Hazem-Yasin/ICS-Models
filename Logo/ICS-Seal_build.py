"""
ICS-Seal and ICS-Emblem as editable 3D models, built on the parametric ICS-Mark.  [PROPOSAL] around the canon mark.
Writes Logo/ICS-Seal.blend and Logo/ICS-Emblem.blend (+ previews in Logo/previews/).

  "/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --python Logo/ICS-Seal_build.py -- "$(wslpath -w <ICS-Models root>)"

Run Logo/ICS-Mark_build.py first: this script appends the `ICS-Mark` object (with its Geometry Nodes sliders) from
Logo/ICS-Mark.blend, so the mark in the seal is still fully parametric.

Layout (radii, font sizes, per-letter positions, ticks, ribbon) comes from Logo/src/ics_seal.py, the same file the 2D kit
(Logo/build_brand.py) reads, so the SVG and the 3D model cannot drift apart.  1 unit = 1 m; the seal is ~1 m wide.
Standing in the XZ plane, facing -Y (numpad 1 = front view).  Colours follow the 2D "reversed" seal: Deep Blue field,
paper-white mark disc, gold arc.

How to edit in Blender:
  * Mark:     select ICS-Seal_mark > Properties > Modifiers > ICS-Mark (all sliders live).
  * Colours:  materials ICS-Seal_blue / _gold / _paper (the mark disc uses ICS-Seal_paper_enamel).
  * Words:    ring letters are one text object each (ICS-Seal_L_top_00 ...). Change a letter in edit mode (Tab), or change the
              string in src/ics_seal.py and rebuild, which also re-spaces the ring.
  * Hand edits are lost on rebuild; copy the .blend first.
FONT NOTE: Blender cannot load the variable Nunito, so the 3D lettering is Varela Round (also rounded, OFL) with a faux-bold
offset. The 2D kit uses Nunito ExtraBold. A static Nunito ExtraBold instance would need fontTools (not installed here).
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
import ics_seal as sl            # noqa: E402

MARK_BLEND = os.path.join(LOGO, "ICS-Mark.blend")
assert os.path.exists(MARK_BLEND), "run Logo/ICS-Mark_build.py first"
T0 = 0.020          # base plate thickness (m)


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def build(kind):
    name = "ICS-Seal" if kind == "seal" else "ICS-Emblem"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    S = 1024.0 if kind == "seal" else 1100.0
    L = sl.seal_layout(S) if kind == "seal" else sl.emblem_layout(S)
    K = 1.0 / S
    C = L["c"]

    def P(x, y):                     # design px (y down) -> metres in the logo plane (y up), centre at origin
        return ((x - C) * K, -(y - C) * K)

    def material(nm, rgb, metallic, rough, coat=0.0):
        m = bpy.data.materials.new(nm)
        m.use_nodes = True
        bs = m.node_tree.nodes["Principled BSDF"]
        bs.inputs["Base Color"].default_value = (*rgb, 1)
        bs.inputs["Metallic"].default_value = metallic
        bs.inputs["Roughness"].default_value = rough
        if coat:
            bs.inputs["Coat Weight"].default_value = coat
            bs.inputs["Coat Roughness"].default_value = 0.05
        m.diffuse_color = (*rgb, 1)
        return m

    M_BLUE = material(f"{name}_blue", b.BLUE_LIN, 0.0, 0.5)
    M_GOLD = material(f"{name}_gold", b.GOLD_LIN, 0.55, 0.38)
    M_PAPER = material(f"{name}_paper", lin(b.PAPER_HEX), 0.0, 0.55)
    M_PAPER_ENAMEL = material(f"{name}_paper_enamel", lin(b.PAPER_HEX), 0.0, 0.6, coat=0.3)

    # ---- structure ----------------------------------------------------------------------------------------------------
    top = bpy.data.collections.new(name)
    scene.collection.children.link(top)
    cols = {}
    for n in ("Base", "Rings", "Ticks", "Letters", "Mark", "Ribbon", "Text"):
        c_ = bpy.data.collections.new(f"{name}_{n}")
        top.children.link(c_)
        cols[n] = c_
    root = bpy.data.objects.new(f"{name}_ROOT", None)
    root.empty_display_type = "ARROWS"
    root.empty_display_size = 0.15
    root.rotation_euler = (math.radians(90), 0, 0)       # logo plane XY -> XZ, faces -Y
    top.objects.link(root)
    root["note"] = f"Rebuilt by Logo/ICS-Seal_build.py. Layout: Logo/src/ics_seal.py. Canon mark: Doc 2.32. Extras are [PROPOSAL]."

    def put(ob, col, mat=None, loc=None):
        for c_ in list(ob.users_collection):
            c_.objects.unlink(ob)
        cols[col].objects.link(ob)
        ob.parent = root
        if mat is not None:
            ob.data.materials.append(mat)
        if loc is not None:
            ob.location = loc
        return ob

    def finish(bm, nm):
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        me = bpy.data.meshes.new(nm)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(nm, me)
        scene.collection.objects.link(ob)
        return ob

    def circle_poly(r, n=192):
        return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]

    def pill_poly(cx, cy, w, h, n=40):
        r = h / 2
        pts = []
        for i in range(n):
            a = -math.pi / 2 + math.pi * i / (n - 1)
            pts.append((cx + w / 2 - r + r * math.cos(a), cy + r * math.sin(a)))
        for i in range(n):
            a = math.pi / 2 + math.pi * i / (n - 1)
            pts.append((cx - w / 2 + r + r * math.cos(a), cy + r * math.sin(a)))
        return pts

    def band(nm, outer, inner, z0, t):
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
        return finish(bm, nm)

    def ring(nm, r, width, z0, t):
        return band(nm, circle_poly((r + width / 2) * K), circle_poly((r - width / 2) * K), z0, t)

    # ---- base plate and hairline rings (all from the shared layout) ---------------------------------------------------------
    base = brand._poly_obj(f"{name}_base", circle_poly(L["R"] * K), T0, 0.0)
    put(base, "Base", M_BLUE)
    bev = base.modifiers.new("Bevel", "BEVEL")
    bev.width, bev.segments, bev.limit_method = 0.0025, 3, "ANGLE"
    for p in base.data.polygons:
        p.use_smooth = True
    if kind == "seal":
        rings = (("ring_outer", L["ring_r"], L["ring_w"]), ("hair_in", L["hair_in_r"], L["hair_w"]),
                 ("hair_out", L["hair_out_r"], L["hair_w"]))
    else:
        rings = (("ring_outer", L["ring_outer_r"], L["ring_w"]), ("ring_inner", L["ring_inner_r"], L["ring_w"]))
    for nm, r, w in rings:
        put(ring(f"{name}_{nm}", r, w, T0, 0.0018), "Rings", M_PAPER)

    # ---- 300 cycle ticks (emblem only): three merged meshes, rounded by a Bevel modifier -------------------------------------
    if kind == "emblem":
        bms = {"minor": bmesh.new(), "major": bmesh.new(), "zero": bmesh.new()}
        for t in L["ticks"]:
            a = math.radians(t["ang"])
            r0, r1, w = t["r0"] * K, t["r1"] * K, t["w"] * K
            rm, ln = (r0 + r1) / 2, abs(r0 - r1)
            rad, tan = Vector((math.sin(a), math.cos(a))), Vector((math.cos(a), -math.sin(a)))
            cen = rad * rm
            cs = [cen + rad * (sx * ln / 2) + tan * (sy * w / 2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            bm = bms[t["kind"]]
            lo = [bm.verts.new((p.x, p.y, T0)) for p in cs]
            hi = [bm.verts.new((p.x, p.y, T0 + 0.0022)) for p in cs]
            bm.faces.new(hi)
            for i in range(4):
                j = (i + 1) % 4
                bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
        for k, bm in bms.items():
            ob = put(finish(bm, f"{name}_ticks_{k}"), "Ticks", M_GOLD if k == "zero" else M_PAPER)
            bv = ob.modifiers.new("Bevel", "BEVEL")
            bv.width, bv.segments, bv.limit_method = 0.0005, 2, "ANGLE"
        for i, (sx, sy) in enumerate(L["studs"]):
            px, py = P(sx, sy)
            st = brand._poly_obj(f"{name}_stud_{i}", circle_poly(L["stud_r"] * K, 32), 0.004, T0)
            put(st, "Rings", M_GOLD, loc=(px, py, 0))

    # ---- the mark: the parametric ICS-Mark appended from ICS-Mark.blend ----------------------------------------------------
    with bpy.data.libraries.load(MARK_BLEND, link=False) as (src, dst):
        dst.objects = ["ICS-Mark"]
    mk = dst.objects[0]
    mk.name = f"{name}_mark"
    for c_ in list(mk.users_collection):
        c_.objects.unlink(mk)
    cols["Mark"].objects.link(mk)
    mk.parent = root
    mk.rotation_euler = (0, 0, 0)            # in the .blend it was stood up for its previews
    gm = mk.modifiers["ICS-Mark"]
    # reversed treatment (as the 2D seal): the disc is paper, not blue. Swap every blue material in the node tree and slot.
    blue_old = bpy.data.materials["ICS-Mark_blue_enamel"]
    for nd in gm.node_group.nodes:
        if nd.bl_idname == "GeometryNodeSetMaterial" and nd.inputs["Material"].default_value == blue_old:
            nd.inputs["Material"].default_value = M_PAPER_ENAMEL
    mk.data.materials.clear()
    mk.data.materials.append(M_PAPER_ENAMEL)
    mk.data.materials.append(bpy.data.materials["ICS-Mark_gold"])
    ident = {i.name: i.identifier for i in gm.node_group.interface.items_tree if getattr(i, "in_out", "") == "INPUT"}
    thick = 0.07                                         # thinner disc than the standalone mark: a plate inlay, not a coin
    gm.properties.inputs[ident["Disc Thickness"]]["value"] = thick
    s = L["mark_r"] * K
    mk.scale = (s, s, s)
    mk.location = (0, 0, T0 + thick * s)                 # disc bottom sits on the base plate
    mk["note"] = "Parametric: Properties > Modifiers > ICS-Mark. Radius 1 = the circle (scaled here to the seal)."

    # ---- lettering: one text object per letter, placed by the shared ring layout -----------------------------------------------
    font = bpy.data.fonts.load(os.path.join(LOGO, "fonts", "VarelaRound-Regular.ttf"))

    def text(nm, body, size, mat, col, loc=(0, 0, 0), rot=0.0, extrude=0.0028, ay="BOTTOM_BASELINE", spacing=1.0):
        d = bpy.data.curves.new(nm, "FONT")
        d.body, d.font, d.size = body, font, size
        d.extrude, d.align_x = extrude, "CENTER"
        try:
            d.align_y = ay
        except TypeError:
            d.align_y = "BOTTOM"
        d.space_character = spacing
        d.offset = size * 0.012          # Varela Round has one weight; this thickens the outline a little
        d.resolution_u = 6
        d.materials.append(mat)
        ob = bpy.data.objects.new(nm, d)
        scene.collection.objects.link(ob)
        ob.rotation_euler = (0, 0, rot)
        return put(ob, col, loc=loc)

    for grp, letters, fs in (("top", L["top"], L["fs"]), ("bottom", L["bottom"], L["fs_bot"])):
        for i, (ch, x, y, rot) in enumerate(letters):
            px, py = P(x, y)
            text(f"{name}_L_{grp}_{i:02d}", ch, fs * K, M_PAPER, "Letters", loc=(px, py, T0), rot=-math.radians(rot))

    # ---- emblem extras: ribbon, tagline, dates -----------------------------------------------------------------------------
    if kind == "emblem":
        rb, ds = L["ribbon"], L["dates"]
        rx, ry = P(rb["x"] + rb["w"] / 2, rb["y"] + rb["h"] / 2)
        pill = lambda w, h: [(rx + px * K, ry + py * K) for px, py in pill_poly(0, 0, w, h)]   # noqa: E731
        rib = brand._poly_obj(f"{name}_ribbon", pill(rb["w"], rb["h"]), 0.012, T0)
        put(rib, "Ribbon", M_GOLD)
        ins, lw = rb["inset"], rb["line_w"]
        outl = band(f"{name}_ribbon_outline", pill(rb["w"] - 2 * ins + lw, rb["h"] - 2 * ins + lw),
                    pill(rb["w"] - 2 * ins - lw, rb["h"] - 2 * ins - lw), T0 + 0.012, 0.0016)
        put(outl, "Ribbon", M_BLUE)
        tag = text(f"{name}_tagline", sl.TAGLINE_CAPS, rb["text_size"] * K, M_BLUE, "Ribbon", loc=(rx, ry, T0 + 0.012),
                   ay="CENTER", spacing=1.05, extrude=0.0022)
        bpy.context.view_layer.update()
        tag.data.size *= (rb["w"] * 0.80 * K) / tag.dimensions.x          # fit to 80% of the ribbon, like the 2D layout
        tag.data.offset = tag.data.size * 0.012
        # [PROPOSAL, 3D only] the 2D dates line floats on the page; as an object it needs a small blue backing plate
        pw, ph = S * 0.50, S * 0.050
        dx, dy = P(C, ds["y"] - ph * 0.12)
        plq = brand._poly_obj(f"{name}_dates_plate", [(dx + x * K, dy + y * K) for x, y in pill_poly(0, 0, pw, ph)], 0.012, 0.0)
        put(plq, "Text", M_BLUE)
        text(f"{name}_dates", sl.DATES, ds["size"] * K, M_PAPER, "Text", loc=(dx, dy, 0.012), ay="CENTER", spacing=1.3,
             extrude=0.0018)

    # ---- preview studio ----------------------------------------------------------------------------------------------
    pv = bpy.data.collections.new("Preview")
    scene.collection.children.link(pv)
    world = bpy.data.worlds.new("w")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.30, 0.31, 0.34, 1)
    bg.inputs["Strength"].default_value = 0.25
    for nm, loc, e, sz in (("key", (-1.2, -1.6, 1.4), 28, 1.6), ("fill", (1.6, -1.2, 0.2), 10, 2.0), ("rim", (0.4, -1.2, -1.0), 10, 1.5)):
        ld = bpy.data.lights.new(nm, "AREA")
        ld.energy, ld.size = e, sz
        lo = bpy.data.objects.new(nm, ld)
        pv.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector((0, 0, 0)) - lo.location).to_track_quat("-Z", "Y").to_euler()
    cam_d = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new(f"{name}_cam", cam_d)
    pv.objects.link(cam)
    scene.camera = cam
    scene.render.engine = "CYCLES"
    scene.view_settings.view_transform = "Standard"
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

    if kind == "seal":
        shoot(f"{name}_front.png", (0, -3, 0), (0, 0, 0), ortho_scale=1.06)
        shoot(f"{name}_angle.png", (0.8, -1.5, 0.45), (0, 0, 0), lens=50)
    else:
        shoot(f"{name}_front.png", (0, -3, -0.07), (0, 0, -0.07), ortho_scale=1.34)
        shoot(f"{name}_angle.png", (0.8, -1.6, 0.35), (0, 0, -0.06), lens=50)

    nobj = len([o for o in scene.objects if o.parent == root])
    print(f"STATS {name} objects={nobj} letters={len(L['top']) + len(L['bottom'])}")
    out = os.path.join(LOGO, f"{name}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print("saved", out)


build("seal")
build("emblem")
print("exit 0")
