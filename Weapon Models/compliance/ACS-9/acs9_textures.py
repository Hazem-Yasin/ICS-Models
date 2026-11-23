"""
ACS-9 texture sets (v2, ICS soft look). Procedural numpy, tileable, no external image assets.

Sets (all seamless, mapped by tiling UVs in ACS-9_build.py):
  abs     moulded matte ABS: fine grain + soft mottling.      albedo (body, grille plate, slider track), roughness, normal
  rubber  pebbled rubber (periodic Worley domes).             albedo, roughness, normal
  alu     brushed aluminium, streaks along U.                 albedo, roughness, normal
  steel   finer brushed dark steel (slider knob, screws).     albedo, roughness, normal
  cloth   plain-weave speaker cloth behind the grille.        albedo, roughness, normal

Albedo tint is baked into each albedo PNG (the FBX exporter only follows a direct image link on Base Color).
Everything here is a [PROPOSAL] for surface finish; canon only says "black", "matte", "brushed aluminum" (focus ring).
"""
import os

import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "Logo", "src"))
import ics_brand as brand  # noqa: E402  (single source of the ICS mark geometry)

f32 = np.float32


def srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def gnoise(n, seed, sx, sy):
    """Periodic gaussian band-limited noise, normalised to roughly [-1, 1]. sx, sy: cut-off in cycles/pixel."""
    rng = np.random.default_rng(seed)
    F = np.fft.fft2(rng.standard_normal((n, n)))
    fx = np.fft.fftfreq(n)[None, :]
    fy = np.fft.fftfreq(n)[:, None]
    filt = np.exp(-(fx / sx) ** 2 - (fy / sy) ** 2)
    filt[0, 0] = 0.0
    h = np.real(np.fft.ifft2(F * filt))
    return np.clip(h / (3.0 * h.std() + 1e-9), -1, 1).astype(f32)


def worley(n, cells, seed, jitter=0.85):
    """Periodic distance-to-nearest-feature-point, in cell units."""
    rng = np.random.default_rng(seed)
    gi, gj = np.meshgrid(np.arange(cells), np.arange(cells), indexing="ij")
    py = (gi + 0.5 + (rng.random((cells, cells)) - 0.5) * jitter) / cells
    px = (gj + 0.5 + (rng.random((cells, cells)) - 0.5) * jitter) / cells
    ys, xs = (np.mgrid[0:n, 0:n] + 0.5) / n
    ci = (ys * cells).astype(int)
    cj = (xs * cells).astype(int)
    d = np.full((n, n), 9.0, dtype=f32)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            ri, rj = ci + di, cj + dj
            qy = py[ri % cells, rj % cells] + (ri // cells)
            qx = px[ri % cells, rj % cells] + (rj // cells)
            d = np.minimum(d, np.hypot(qy - ys, qx - xs).astype(f32))
    return d * cells


def weave(n, threads):
    ys, xs = np.mgrid[0:n, 0:n] / n * threads
    i, j = np.floor(xs).astype(int), np.floor(ys).astype(int)
    u, v = xs - i, ys - j
    over = ((i + j) % 2) == 0
    h = np.where(over, 0.65 + 0.35 * np.sin(np.pi * u), 0.65 + 0.35 * np.sin(np.pi * v))
    h = h - 0.30 * (~over)
    return np.clip(h, 0, 1).astype(f32)


def normal_map(h, strength):
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5 * strength
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5 * strength
    l = np.sqrt(dx * dx + dy * dy + 1.0)
    return np.stack([-dx / l * 0.5 + 0.5, -dy / l * 0.5 + 0.5, 1.0 / l * 0.5 + 0.5], -1).astype(f32)


def grey(v):
    v = np.clip(v, 0, 1).astype(f32)
    return np.stack([v, v, v], -1)


def tinted(tint, variation):
    t = np.array(tint, dtype=f32)[None, None, :]
    return srgb(np.clip(t * variation[..., None], 0, 1)).astype(f32)


def save_png(path, rgb):
    h, w = rgb.shape[:2]                                  # row 0 = bottom (Blender order)
    a = np.concatenate([rgb, np.ones((h, w, 1), f32)], -1)
    img = bpy.data.images.new("acs9_tmp", w, h, alpha=False)
    img.colorspace_settings.name = "Non-Color"           # raw bytes: sRGB encoding is done above
    img.pixels.foreach_set(a.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def make(tex_dir):
    """Write every map. Returns {key: path}; keys are '<set>_rough', '<set>_normal' and '<name>_albedo'."""
    os.makedirs(tex_dir, exist_ok=True)
    out = {}

    def put(key, rgb):
        p = os.path.join(tex_dir, f"ACS-9_{key}.png")
        save_png(p, rgb)
        out[key] = p

    # ---- ABS: moulded grain + soft mottling -------------------------------------
    n = 1024
    fine = gnoise(n, 11, 0.22, 0.22)
    mott = gnoise(n, 12, 0.020, 0.020)
    put("abs_rough", grey(0.55 + 0.10 * mott + 0.08 * fine))
    put("abs_normal", normal_map(0.8 * fine + 0.2 * mott, 0.40))
    put("body_albedo", tinted((0.035, 0.036, 0.040), 1.0 + 0.10 * mott + 0.05 * fine))
    put("grille_albedo", tinted((0.018, 0.018, 0.020), 1.0 + 0.10 * mott + 0.05 * fine)[::2, ::2])
    put("track_albedo", tinted((0.010, 0.010, 0.011), 1.0 + 0.10 * mott)[::2, ::2])

    # ---- rubber: periodic pebbles -------------------------------------------------
    m = 512
    d = worley(m, 14, 21)
    pebble = np.clip(1.0 - d * 1.15, 0, 1) ** 0.6
    pebble = (pebble + 0.12 * gnoise(m, 22, 0.2, 0.2)).astype(f32)
    put("rubber_rough", grey(0.72 + 0.18 * (1.0 - pebble)))
    put("rubber_normal", normal_map(pebble, 8.0))
    put("rubber_albedo", tinted((0.012, 0.012, 0.013), 0.70 + 0.30 * pebble))

    # ---- brushed aluminium: streaks along U ---------------------------------------
    streak = gnoise(m, 31, 0.004, 0.30)
    hair = gnoise(m, 32, 0.012, 0.16)
    put("alu_rough", grey(0.30 + 0.10 * streak + 0.05 * hair))
    put("alu_normal", normal_map(0.7 * streak + 0.3 * hair, 0.5))
    put("ring_albedo", tinted((0.80, 0.81, 0.83), 1.0 + 0.05 * streak))

    # ---- dark steel: finer brushing ----------------------------------------------
    s2 = gnoise(m, 41, 0.006, 0.34)
    put("steel_rough", grey(0.36 + 0.10 * s2))
    put("steel_normal", normal_map(s2, 0.4))
    put("steel_albedo", tinted((0.30, 0.31, 0.33), 1.0 + 0.06 * s2))

    # ---- speaker cloth: plain weave, 16 threads per tile ----------------------------
    w = weave(m, 16)
    put("cloth_rough", grey(0.88 - 0.12 * w))
    put("cloth_normal", normal_map(w, 10.0))
    put("cloth_albedo", tinted((0.016, 0.016, 0.018), 0.55 + 0.45 * w))
    return out


# ---- text and printed decals ---------------------------------------------------
def render_masks(items, w_px, h_px, w_mm, h_mm, tex_dir):
    """items: (channel 0-2, string, size mm, x mm, y mm from bottom-left, rotation deg). Returns three (h_px, w_px) coverage arrays."""
    import math
    sc = bpy.data.scenes.new("acs9_mask")
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 16
    sc.cycles.use_denoising = False
    sc.cycles.filter_width = 1.2
    sc.render.resolution_x, sc.render.resolution_y = w_px, h_px
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    world = bpy.data.worlds.new("acs9_mask_world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0, 0, 0, 1)
    sc.world = world
    mats = []
    for ch in range(3):
        m = bpy.data.materials.new(f"acs9_mask_{ch}")
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = tuple(1.0 if i == ch else 0.0 for i in range(3)) + (1.0,)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        mats.append(m)
    curves = []
    for i, (ch, s, size, x, y, rot) in enumerate(items):
        cu = bpy.data.curves.new(f"acs9_txt_{i}", "FONT")
        cu.body = s
        cu.size = size
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.materials.append(mats[ch])
        ob = bpy.data.objects.new(f"acs9_txt_{i}", cu)
        ob.location = (x, y, 0.0)
        ob.rotation_euler = (0, 0, math.radians(rot))
        sc.collection.objects.link(ob)
        curves.append(cu)
    cd = bpy.data.cameras.new("acs9_mask_cam")
    cd.type = "ORTHO"
    cd.ortho_scale = max(w_mm, h_mm)
    cam = bpy.data.objects.new("acs9_mask_cam", cd)
    cam.location = (w_mm / 2, h_mm / 2, 10.0)
    sc.collection.objects.link(cam)
    sc.camera = cam
    path = os.path.join(tex_dir, "_mask.png")
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True, scene=sc.name)
    img = bpy.data.images.load(path)
    img.colorspace_settings.name = "Non-Color"
    buf = np.empty(w_px * h_px * 4, np.float32)
    img.pixels.foreach_get(buf)
    buf = buf.reshape(h_px, w_px, 4)[..., :3].copy()
    bpy.data.images.remove(img)
    os.remove(path)
    bpy.data.scenes.remove(sc)
    for cu in curves:
        bpy.data.curves.remove(cu)
    buf = np.power(np.clip(buf, 0, 1), 2.2)
    return buf[..., 0], buf[..., 1], buf[..., 2]


def _grid(w, h, ppm):
    ys, xs = np.mgrid[0:h, 0:w]
    return (xs + 0.5) / ppm, (ys + 0.5) / ppm            # mm, y up (row 0 = bottom)


def outline(w, h, ppm, inset, corner, line):
    """Rounded-rectangle outline, coverage 0..1. inset, corner, line in mm."""
    x, y = _grid(w, h, ppm)
    hw, hh = w / ppm / 2, h / ppm / 2
    qx = np.abs(x - hw) - (hw - corner)
    qy = np.abs(y - hh) - (hh - corner)
    sd = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - corner
    return np.clip(0.5 - (np.abs(sd + inset) - line / 2) * ppm, 0, 1).astype(f32)


def ring(w, h, ppm, cx, cy, r, line):
    x, y = _grid(w, h, ppm)
    return np.clip(0.5 - (np.abs(np.hypot(x - cx, y - cy) - r) - line / 2) * ppm, 0, 1).astype(f32)


def rect(w, h, ppm, x0, y0, x1, y1):
    x, y = _grid(w, h, ppm)
    return ((x >= x0) & (x <= x1) & (y >= y0) & (y <= y1)).astype(f32)


def disc(w, h, ppm, cx, cy, r):
    x, y = _grid(w, h, ppm)
    return np.clip(0.5 - (np.hypot(x - cx, y - cy) - r) * ppm, 0, 1).astype(f32)


def arc_mask(w, h, ppm, cx, cy, gap_deg):
    """1 everywhere except a wedge of +-gap_deg about +x from (cx, cy). Multiplied into a ring() to make an open arc."""
    x, y = _grid(w, h, ppm)
    return (np.abs(np.degrees(np.arctan2(y - cy, x - cx))) > gap_deg).astype(f32)


def _compose(tex_dir, name, base, layers, w, h):
    lin = np.ones((h, w, 3), f32) * np.array(base, f32)[None, None, :]
    for cov, col in layers:
        lin = lin * (1 - cov[..., None]) + np.array(col, f32)[None, None, :] * cov[..., None]
    p = os.path.join(tex_dir, f"ACS-9_{name}_albedo.png")
    save_png(p, srgb(lin).astype(f32))
    return p


INK = (0.012, 0.012, 0.013)
BLUE = (0.012, 0.027, 0.085)       # ICS Deep Blue #1A2E52 (linear)
GOLD = (0.58, 0.39, 0.075)         # ICS Warm Gold #C9A84C (linear)
BODY_LIN = (0.035, 0.036, 0.040)
LABEL_FILM = (0.46, 0.45, 0.42)    # pale warm-grey printed film [PROPOSAL]
LEGEND_INK = (0.50, 0.50, 0.52)


def make_prints(tex_dir):
    """Three printed decals. Sizes in mm must match ACS-9_build.py (LABEL_*, LEGEND_*, REAR_*).
    label  : -X side. Canon: serial ICS-ACS-9-0012, 'safety-certified for use in occupied facilities',
             'Extended exposure (over 4 hours continuous) is not recommended'. Layout, mark and tagline are [PROPOSAL].
    legend : +X side above the slider. Printed 1 2 3 and gold tick marks. Canon: slider marked 1, 2, 3.
    rear   : rear panel, under the mark. 'ACS-9' only. [PROPOSAL]
    """
    out = {}
    # ---- label, 62 x 17 mm at 24 px/mm ----------------------------------------------------------------
    ppm, wm, hm = 24, 62.0, 17.0
    w, h = int(wm * ppm), int(hm * ppm)
    m0, m1, _ = render_masks([
        (0, "ACS-9   ACOUSTIC COMPLIANCE SYSTEM", 1.55, 36.0, 13.2, 0),
        (0, "SER. ICS-ACS-9-0012", 1.5, 36.0, 9.9, 0),
        (0, "Safety-certified for use in occupied facilities.", 1.0, 36.0, 6.6, 0),
        (0, "Extended exposure (over 4 hours continuous) is not recommended.", 0.95, 36.0, 4.5, 0),
        (1, "Because You're Worth the Investment.", 0.9, 36.0, 2.3, 0)], w, h, wm, hm, tex_dir)
    # ICS mark from Logo/src/ics_brand.py: bounding box centred at (8.0, 8.5) mm, circle radius 3.4 mm (8 mm tall) [PROPOSAL size]
    R = 3.4
    bx0, bx1, by0, by1 = brand.mark_bbox()
    ccx = 8.0 - (bx0 + bx1) / 2 * R
    ccy = 8.5 - (by0 + by1) / 2 * R
    mb, mg = brand.raster_mark(w, h, ppm * R, ccx * ppm, ccy * ppm)
    layers = [(outline(w, h, ppm, 0.45, 1.3, 0.15), INK), (mb, BLUE), (mg, GOLD), (m0, INK), (m1, BLUE)]
    out["label"] = _compose(tex_dir, "label", LABEL_FILM, layers, w, h)
    # ---- slider legend, 60 x 10 mm -----------------------------------------------------------------
    wm, hm = 60.0, 10.0
    w, h = int(wm * ppm), int(hm * ppm)
    xs = (14.0, 30.0, 46.0)                      # y = -0.016, 0, +0.016 from the slider centre
    m0, _, _ = render_masks([(0, str(i + 1), 3.0, x, 6.6, 0) for i, x in enumerate(xs)], w, h, wm, hm, tex_dir)
    ticks = np.zeros((h, w), f32)
    for x, th in zip(xs, (1.0, 1.7, 2.4)):
        ticks = np.maximum(ticks, rect(w, h, ppm, x - 0.3, 1.2, x + 0.3, 1.2 + th))
    out["legend"] = _compose(tex_dir, "legend", BODY_LIN, [(m0, LEGEND_INK), (ticks, GOLD)], w, h)
    # ---- rear panel text, 60 x 60 mm at 20 px/mm ------------------------------------------------------
    ppm, wm, hm = 20, 60.0, 60.0
    w, h = int(wm * ppm), int(hm * ppm)
    m0, _, _ = render_masks([(0, "ACS-9", 2.6, 30.0, 8.5, 0)], w, h, wm, hm, tex_dir)
    out["rear"] = _compose(tex_dir, "rear", BODY_LIN, [(m0, LEGEND_INK)], w, h)
    return out
