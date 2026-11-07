"""
Maintenance-Bar -- 45 cm length of ICS structural rebar. Build script for Blender 5.x.

Run:  blender --background --python Maintenance-Bar_build.py -- <ICS-Models root>
Writes: Weapon Models/improvised/Maintenance-Bar/Maintenance-Bar.blend, textures/*.png,
        Weapon Models/exports/Maintenance-Bar.fbx, Weapon Models/improvised/Maintenance-Bar/previews/*.png
Spec:   _specs/Maintenance-Bar.md

Raw look: not an ICS product. No logo, no label, no rounded finish.
Axis along -Y (forward). Origin = centre of the one-hand grip, 10 cm from the bracket-bent end.
The geometry is a true 12 mm cylinder (ribs are in the normal map) so the BAR-FL coupling fits.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

ROOT = sys.argv[sys.argv.index("--") + 1]
sys.path.insert(0, os.path.join(ROOT, "_shared"))
import studio  # noqa: E402

OUT = os.path.join(ROOT, "Weapon Models", "improvised", "Maintenance-Bar")
TEX_DIR = os.path.join(OUT, "textures")
PREVIEW_DIR = os.path.join(OUT, "previews")
EXPORT_DIR = os.path.join(ROOT, "Weapon Models", "exports")
for d in (TEX_DIR, PREVIEW_DIR, EXPORT_DIR):
    os.makedirs(d, exist_ok=True)

# ---- dimensions (m) --------------------------------------------------------
LENGTH = 0.45          # canon: 45 cm
R_CORE = 0.0054        # core radius; the longitudinal ribs reach R_RIB
R_RIB = 0.0060         # canon-derived: 12 mm nominal diameter over the ribs
S_GRIP = 0.10          # [PROPOSAL] grip centre, measured from the bent end
KINK_DEG = 24          # [PROPOSAL] bracket bend
KINK_AT = 0.020        # bend starts this far from the bent end
KINK_RAMP = 0.014
SHEAR_DEG = 25         # [PROPOSAL] angle of the freshly sheared cut
SEG = 24               # sides; vertices 0 and SEG/2 carry the longitudinal ribs
TEX = 1024
RNG = np.random.default_rng(1138)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def link(ob):
    scene.collection.objects.link(ob)
    return ob


# ---- centre line -----------------------------------------------------------
def phi(s):
    """Direction angle below the axis (the bent end rises toward +Z going back)."""
    if s <= KINK_AT:
        return math.radians(KINK_DEG)
    if s >= KINK_AT + KINK_RAMP:
        return 0.0
    t = (s - KINK_AT) / KINK_RAMP
    return math.radians(KINK_DEG) * (1 - t * t * (3 - 2 * t))


def centre(s_list):
    """Integrate the centre line; the straight part runs along -Y at z=0 through the grip."""
    s_ref = KINK_AT + KINK_RAMP
    pts = {}
    # forward of s_ref the bar is straight
    y_ref = -(s_ref - S_GRIP)
    # walk back from s_ref to 0 in small steps
    n = 400
    ds = s_ref / n
    y, z = y_ref, 0.0
    walk = {round(s_ref, 6): (y, z)}
    for i in range(n):
        s = s_ref - i * ds
        a = phi(s - ds / 2)
        y += math.cos(a) * ds     # going back toward +Y
        z += math.sin(a) * ds     # and rising
        walk[round(s - ds, 6)] = (y, z)
    keys = np.array(sorted(walk))
    for s in s_list:
        if s >= s_ref:
            pts[s] = (-(s - S_GRIP), 0.0)
        else:
            k = keys[np.abs(keys - s).argmin()]
            pts[s] = walk[round(float(k), 6)]
    return pts


# ring stations along the bar (m from the bent end)
STATIONS = [0.0, 0.009, 0.018, 0.022, 0.026, 0.030, 0.034, 0.10, 0.20, 0.30, 0.40,
            LENGTH - 0.012, LENGTH - 0.006, LENGTH]
cl = centre(STATIONS)


def tangent(s):
    a, b = max(s - 0.002, 0.0), min(s + 0.002, LENGTH)
    pa, pb = centre([a, b])[a], centre([a, b])[b]
    t = Vector((0, pb[0] - pa[0], pb[1] - pa[1]))
    return t.normalized()


def radius_at(i):
    """Octagonal-ish bar with a rib at vertices 0 and SEG/2; tiny roughness jitter."""
    base = R_RIB if i % (SEG // 2) == 0 else R_CORE
    return base


# ---- mesh ------------------------------------------------------------------
bm = bmesh.new()
rings = []
for si, s in enumerate(STATIONS):
    y, z = cl[s]
    t = tangent(s)
    ex = Vector((1, 0, 0))
    ey = t.cross(ex).normalized()        # the other cross-section axis, in the bend plane
    ring = []
    last = si == len(STATIONS) - 1
    for i in range(SEG):
        th = math.tau * i / SEG
        r = radius_at(i) * (1 + RNG.normal(0, 0.012))
        if last:
            r *= 1.05                    # sheared steel mushrooms slightly at the cut
        lx, ly = math.cos(th) * r, math.sin(th) * r
        p = Vector((0, y, z)) + ex * lx + ey * ly
        if last:
            # slanted shear plane: slide each vertex along the axis by its offset across the cut
            p += t * (math.tan(math.radians(SHEAR_DEG)) * lx)
            p += t * RNG.normal(0, 0.0003)
        ring.append(bm.verts.new(p))
    rings.append((s, ring))

faces = []
for (s0, r0), (s1, r1) in zip(rings, rings[1:]):
    for i in range(SEG):
        j = (i + 1) % SEG
        f = bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        faces.append((f, s0, s1, i))

# end caps (triangle fans round a centre vertex)
for (s, ring), rev in ((rings[0], True), (rings[-1], False)):
    c = Vector(sum((v.co for v in ring), Vector()) / SEG)
    cv = bm.verts.new(c)
    for i in range(SEG):
        j = (i + 1) % SEG
        tri = (cv, ring[j], ring[i]) if rev else (cv, ring[i], ring[j])
        faces.append((bm.faces.new(tri), s, s, i))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# UVs: u = around, v = along the bar (0 at the bent end, rust end)
uv = bm.loops.layers.uv.new("UVMap")
for f, s0, s1, i in faces:
    for loop in f.loops:
        v = loop.vert
        # which ring station and which side is this?
        idx = None
        for ri, (s, ring) in enumerate(rings):
            if v in ring:
                idx = (ri, ring.index(v))
                break
        if idx is None:                              # cap centre
            loop[uv].uv = (0.5, 0.5 if f.calc_center_median().y > 0 else 0.5)
            continue
        ri, k = idx
        u = k / SEG
        if f.verts[0] not in [x for _, rg in rings for x in rg] and False:
            pass
        loop[uv].uv = (u, STATIONS[ri] / LENGTH)
# fix the seam: faces joining the last side back to the first
for f, s0, s1, i in faces:
    if s0 != s1 and i == SEG - 1:
        for loop in f.loops:
            if loop[uv].uv[0] == 0.0:
                loop[uv].uv = (1.0, loop[uv].uv[1])
# caps: sit on the flat-grey part of the texture, away from rust and ribs
for f, s0, s1, i in faces:
    if s0 == s1:
        for loop in f.loops:
            loop[uv].uv = (0.5, 0.30 if s0 == 0.0 else 0.5)

me = bpy.data.meshes.new("Maintenance-Bar_bar")
bm.to_mesh(me)
bm.free()
bar = link(bpy.data.objects.new("Maintenance-Bar_bar", me))


# ---- textures (1024 px set: albedo, normal, roughness) ---------------------
ASPECT = LENGTH / (math.tau * R_RIB)   # UV is ~12x longer than it is wide; stretch cells to match


def noise(n, cells, octaves=1):
    """Value noise, periodic round the bar (x), square in real-world mm (cells across = cells, along = cells*ASPECT)."""
    out = np.zeros((n, n))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        cx = cells * 2 ** o
        cy = max(int(round(cx * ASPECT)), 1)
        g = RNG.random((cy + 1, cx + 1))
        g[:, -1] = g[:, 0]
        xi = np.linspace(0, cx, n, endpoint=False)
        yi = np.linspace(0, cy, n, endpoint=False)
        x0, y0 = xi.astype(int), yi.astype(int)
        fx = xi - x0
        fy = yi - y0
        fx = (fx * fx * (3 - 2 * fx))[None, :]
        fy = (fy * fy * (3 - 2 * fy))[:, None]
        a, b = g[np.ix_(y0, x0)], g[np.ix_(y0, x0 + 1)]
        c, d = g[np.ix_(y0 + 1, x0)], g[np.ix_(y0 + 1, x0 + 1)]
        out += amp * ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy)
        tot += amp
        amp *= 0.5
    return out / tot


# image axes: x = u (around), y = v (along; row 0 = v 0, the rust end)
yy, xx = np.mgrid[0:TEX, 0:TEX] / TEX
v_mm = yy * LENGTH * 1000
u = xx

PITCH = 7.0                                      # [PROPOSAL] rib pitch, mm
phase = v_mm / PITCH + u * 1.0                    # one pitch of shift per turn -> diagonal, wraps cleanly
saw = phase - np.floor(phase)
rib = np.clip(1 - np.abs(saw - 0.5) * 2 / 0.42, 0, 1)   # raised band, 42% of the pitch
rib = rib * rib * (3 - 2 * rib)
gap = np.minimum(np.abs(u - 0.0), np.abs(u - 1.0))
gap = np.minimum(gap, np.abs(u - 0.5))
mask = np.clip((gap - 0.035) / 0.03, 0, 1)        # no transverse ribs over the two longitudinal ribs
height = (rib * mask + 0.9 * (1 - mask)) * 0.0007  # metres; ribs ~0.7 mm tall
height += (noise(TEX, 64, 3) - 0.5) * 0.00012     # pitting

mm_per_px_u = math.pi * R_RIB * 2 * 1000 / TEX
mm_per_px_v = LENGTH * 1000 / TEX
dh_du = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) / (2 * mm_per_px_u / 1000)
dh_dv = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) / (2 * mm_per_px_v / 1000)
nx, ny, nz = -dh_du, -dh_dv, np.ones_like(height)
ln = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
normal = np.stack([nx / ln * 0.5 + 0.5, ny / ln * 0.5 + 0.5, nz / ln * 0.5 + 0.5], -1)

# albedo: matte grey steel, dark mill scale in the troughs, rust where it sat in the wall
mottle = noise(TEX, 8, 4)
fine = noise(TEX, 96, 2)
grey = 0.20 + 0.05 * (mottle - 0.5) + 0.03 * (fine - 0.5)
grey = grey * (0.82 + 0.18 * (rib * mask + (1 - mask)))      # troughs darker
albedo = np.stack([grey * 0.98, grey, grey * 1.04], -1)
rustness = np.clip(1.0 - yy / 0.20, 0, 1)                    # strongest at the bent end, gone by 20%
rustness = np.clip(rustness * (0.35 + 1.0 * noise(TEX, 3, 4)) - 0.10, 0, 1)
rustness = np.clip(rustness * 1.5, 0, 0.85)
patch = np.clip((noise(TEX, 2, 3) - 0.66) * 5, 0, 1) * 0.40   # a few orange patches elsewhere
rustness = np.maximum(rustness, patch)
rust_col = np.stack([0.17 + 0.06 * fine, 0.075 + 0.03 * fine, 0.040 + 0.015 * fine], -1)
albedo = albedo * (1 - rustness[..., None]) + rust_col * rustness[..., None]
rough = np.clip(0.80 + 0.10 * (mottle - 0.5) + 0.12 * rustness, 0, 1)


def to_image(name, data, srgb):
    img = bpy.data.images.new(name, TEX, TEX, alpha=False)
    img.colorspace_settings.name = "sRGB" if srgb else "Non-Color"
    if data.ndim == 2:
        data = np.stack([data] * 3, -1)
    rgba = np.concatenate([np.clip(data, 0, 1), np.ones((TEX, TEX, 1))], -1).astype(np.float32)
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = os.path.join(TEX_DIR, name + ".png")
    img.file_format = "PNG"
    img.save()
    return img


def encode_srgb(c):
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(np.clip(c, 1e-6, 1), 1 / 2.4) - 0.055)


img_a = to_image("Maintenance-Bar_albedo", encode_srgb(albedo), True)
img_n = to_image("Maintenance-Bar_normal", normal, False)
img_r = to_image("Maintenance-Bar_roughness", rough, False)

# ---- material --------------------------------------------------------------
m = bpy.data.materials.new("Maintenance-Bar_rebar")
m.use_nodes = True
nt = m.node_tree
bsdf = nt.nodes["Principled BSDF"]
for nm, img, inp, cs in (("albedo", img_a, "Base Color", "sRGB"), ("roughness", img_r, "Roughness", "Non-Color")):
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    t.image.colorspace_settings.name = cs
    nt.links.new(t.outputs["Color"], bsdf.inputs[inp])
tn = nt.nodes.new("ShaderNodeTexImage")
tn.image = img_n
tn.image.colorspace_settings.name = "Non-Color"
nm_node = nt.nodes.new("ShaderNodeNormalMap")
nm_node.inputs["Strength"].default_value = 1.0
nt.links.new(tn.outputs["Color"], nm_node.inputs["Color"])
nt.links.new(nm_node.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Metallic"].default_value = 0.35
bar.data.materials.append(m)
for p in bar.data.polygons:
    p.use_smooth = True
try:
    with bpy.context.temp_override(object=bar, active_object=bar, selected_objects=[bar]):
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
except Exception:
    pass

root = link(bpy.data.objects.new("Maintenance-Bar", None))
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 0.02
bar.parent = root

tris = sum(len(p.vertices) - 2 for p in bar.data.polygons)
dims = bar.dimensions
print(f"STATS triangles={tris} dims_m=({dims.x:.4f},{dims.y:.4f},{dims.z:.4f})")

# ---- save and export --------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Maintenance-Bar.blend"), compress=True)
bpy.ops.object.select_all(action="DESELECT")
for o in (root, bar):
    o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(EXPORT_DIR, "Maintenance-Bar.fbx"), use_selection=True,
                         object_types={"MESH", "EMPTY"}, apply_scale_options="FBX_SCALE_ALL",
                         add_leaf_bones=False, mesh_smooth_type="FACE",
                         path_mode="COPY", embed_textures=True)

# ---- previews ----------------------------------------------------------------
cam = studio.setup(scene, floor_z=-0.0064)
pv = lambda n: os.path.join(PREVIEW_DIR, f"Maintenance-Bar_{n}.png")  # noqa: E731
cam.shot(pv("hero"), (0.42, 0.22, 0.26), (0, -0.10, 0), 42)
cam.shot(pv("side"), (0.0, -0.10, 0.55), (0, -0.10, 0), 28)
cam.shot(pv("bent_end"), (0.07, 0.17, 0.045), (0, 0.095, 0.01), 95)
cam.shot(pv("sheared_end"), (0.07, -0.43, 0.05), (0, -0.355, 0), 95)
print("DONE")
