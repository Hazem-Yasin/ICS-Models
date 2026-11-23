"""
CRD-7 texture sets (v3, "hard" look). Procedural numpy plus text rendered through Blender.

  make(tex_dir)       body atlas, 2048 px: albedo, normal, roughness. Six box-projected tiles (top, bottom, +X, -X, front, rear)
                      at 12 px per mm. Chipped paint over pale plastic, moulded grain, panel grooves, grime, scratches,
                      printed text, underside label, peeling sticker.
  make_trim(tex_dir)  trim atlas, 1024 px, four 512 px swatches: 0 dark ABS, 1 rubber, 2 dark steel, 3 red button plastic.
  make_lcd(tex_dir, charged)  the screen image (emission colour): amber when charged, red when discharged.

Canon: "Asset Welfare Series - CRD-7", "For compassionate use only.", amber charged / red discharged, 40 V safety capacitor,
12-hour Compassionate Use certification, Planetary Disciplinary Protocol (Doc 2.14). Everything else printed, labelled,
scratched or displayed here is a [PROPOSAL].
"""
import math
import os
import time

import bpy
import numpy as np

STORY_WEAR = True   # small local marks: grease round the controls, scratched initials, a worn ICS stencil. False = clean metal
TEX = 2048
PXMM = 12.0                       # texels per mm
AWMM = TEX / PXMM                 # atlas edge, mm
f32 = np.float32

# ---- body geometry shared with the build script (mm, body-centred) ---------------
BODY_W, BODY_L, BODY_H = 50.0, 115.0, 30.0
TOP_Z = BODY_H / 2
SEAM_Z, SEAM_W, SEAM_D = -9.0, 0.7, 0.6          # groove below mid-height
BTN_X, BTN_Y = 0.0, 24.0                          # thumb button
LOGO_Y = -37.0
LCD_Y = 0.5
LCD_W = 32.2
LCD_PX_W, LCD_PX_H = 1280, 528
LCD_H = LCD_W * LCD_PX_H / LCD_PX_W                # square pixels

# ---- atlas layout: (origin x, origin y, width, height) in mm, y up -----------------
TILES = {
    "top": (1.0, 54.0, 50.0, 115.0),
    "bottom": (53.0, 54.0, 50.0, 115.0),
    "px": (105.0, 54.0, 30.0, 115.0),
    "mx": (137.0, 54.0, 30.0, 115.0),
    "front": (1.0, 21.0, 50.0, 30.0),
    "rear": (53.0, 21.0, 50.0, 30.0),
}


def proj(tile, x, y, z):
    """Body-local mm -> tile coordinates (tu right, tv up). Tiles are drawn as seen with the prongs at the top."""
    if tile == "top":
        return 25.0 - x, BODY_L / 2 - y
    if tile == "bottom":
        return x + 25.0, BODY_L / 2 - y
    if tile == "px":
        return z + 15.0, BODY_L / 2 - y
    if tile == "mx":
        return 15.0 - z, BODY_L / 2 - y
    if tile == "front":
        return x + 25.0, z + 15.0
    return 25.0 - x, z + 15.0                      # rear


def tile_of(n, c):
    """Pick the tile for a face from its normal n and centre c (mm)."""
    nx, ny, nz = n
    cx, cy, cz = c
    if cz > TOP_Z - 2.0 and abs(cx) < 22.0 and abs(cy) < 54.0:
        return "top"                               # pocket and recess walls on the top face
    if cz < -TOP_Z + 2.0 and abs(cx) < 22.0 and abs(cy) < 54.0:
        return "bottom"
    if abs(cx) >= BODY_W / 2 - 3.0 and abs(cz) < 10.5 and abs(cy) < BODY_L / 2 - 4.5:
        return "px" if cx > 0 else "mx"            # flat sides, emitter recess, seam
    a = (abs(nx), abs(ny), abs(nz))
    k = a.index(max(a))
    if k == 2:
        return "top" if nz > 0 else "bottom"
    if k == 1:
        return "front" if ny < 0 else "rear"
    return "px" if nx > 0 else "mx"


def encode_srgb(c):
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(np.clip(c, 1e-6, 1), 1 / 2.4) - 0.055)


# ---- text through Blender -------------------------------------------------------------
def _render_masks(items, w_px, h_px, w_mm, h_mm, tex_dir):
    """items: (channel 0-2, string, size mm, x mm, y mm from bottom-left, rotation deg). Returns three (h_px, w_px) arrays."""
    sc = bpy.data.scenes.new("crd7_mask")
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
    world = bpy.data.worlds.new("crd7_mask_world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0, 0, 0, 1)
    sc.world = world
    mats = []
    for ch in range(3):
        m = bpy.data.materials.new(f"crd7_mask_{ch}")
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
        cu = bpy.data.curves.new(f"crd7_txt_{i}", "FONT")
        cu.body = s
        cu.size = size
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.materials.append(mats[ch])
        ob = bpy.data.objects.new(f"crd7_txt_{i}", cu)
        ob.location = (x, y, 0.0)
        ob.rotation_euler = (0, 0, math.radians(rot))
        sc.collection.objects.link(ob)
        curves.append(cu)
    cd = bpy.data.cameras.new("crd7_mask_cam")
    cd.type = "ORTHO"
    cd.ortho_scale = max(w_mm, h_mm)
    cam = bpy.data.objects.new("crd7_mask_cam", cd)
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
    buf = np.power(np.clip(buf, 0, 1), 2.2)        # PNG is display-encoded; recover coverage
    return buf[..., 0], buf[..., 1], buf[..., 2]


# ---- text on the body: (channel, string, size mm, tile, tu, tv, rotation deg) --------
def _text_items():
    t = []
    t += [(0, "Asset Welfare Series - CRD-7", 2.1, "top", 25.0, BODY_L / 2 + 20.0, 0),    # canon
          (0, "For compassionate use only.", 1.8, "top", 25.0, BODY_L / 2 + 16.0, 0),     # canon
          (0, "THIS END TO ASSET", 1.5, "top", 25.0, BODY_L / 2 + 49.0, 0),               # [PROPOSAL]
          (0, "CHARGE", 1.0, "top", 25.0, BODY_L / 2 - 14.8, 0),
          (0, "LIVE", 1.0, "top", 31.5, BODY_L / 2 - 43.5, 0),
          (0, "SAFE", 1.0, "top", 18.5, BODY_L / 2 - 43.5, 0)]
    t += [(0, "TEST", 1.3, "px", 15.0, 68.5, 0),                              # [PROPOSAL] beside the side emitter
          (0, "AMBER = CHARGED", 1.1, "mx", 15.0, BODY_L / 2 + 22.0, 0),                  # canon colours
          (0, "RED = DISCHARGED", 1.1, "mx", 15.0, BODY_L / 2 + 24.5, 0)]
    t += [(1, "ICS EARTH BRANCH", 2.1, "bottom", 25.0, 63.2, 0),                           # [PROPOSAL] underside label
          (1, "SECURITY ISSUE  CRD-7", 1.5, "bottom", 25.0, 60.2, 0),
          (1, "Compliance Restraint Device", 1.35, "bottom", 25.0, 57.4, 0),
          (1, "S/N  CR7-04417-3382", 1.5, "bottom", 25.0, 52.9, 0),
          (1, "SAFETY CAPACITOR 40 V", 1.45, "bottom", 25.0, 50.2, 0),                    # 40 V is canon (CRD-7R)
          (1, "04417 3382 0017", 1.1, "bottom", 25.0, 39.8, 0),
          (0, "BATTERY  -  1/4 TURN", 1.0, "bottom", 25.0, 30.5, 0),
          (0, "COMPLIANT WITH PLANETARY DISCIPLINARY PROTOCOL 2.14", 0.95, "bottom", 25.0, 100.0, 0)]   # Doc 2.14 is canon
    t += [(0, "ICS-EP CLASS 2   40 V   DO NOT SUBMERGE", 1.0, "bottom", 25.0, BODY_L / 2 + 49.5, 0)]    # [PROPOSAL] regulatory strip
    t += [(0, "+", 1.3, "top", 42.9, BODY_L / 2 - 31.5, 0), (0, "-", 1.3, "top", 38.1, BODY_L / 2 - 31.5, 0),      # [PROPOSAL] test jack polarity
          (0, "CONTACT", 0.8, "top", 13.5, BODY_L / 2 - 41.3, 0), (0, "RANGED", 0.8, "top", 7.5, BODY_L / 2 - 41.3, 0),   # mode window labels
          (0, "FUSE  2 A", 1.0, "mx", 6.5, BODY_L / 2 - 21.5, 0),                                                   # [PROPOSAL] fuse holder
          (0, "CHG", 0.9, "rear", 41.5, 20.3, 0)]                                                                   # [PROPOSAL] charge port
    t += [(2, "COMPASSIONATE USE", 1.9, "bottom", 25.0, 90.6, 0),                          # sticker; 12-hour certification is canon
          (2, "CERTIFIED  -  12 H", 1.6, "bottom", 25.0, 87.2, 0)]
    return t


def make(tex_dir):
    """Body atlas. Returns dict(albedo (sRGB-encoded), normal, rough), float32."""
    t0 = time.time()
    rng = np.random.default_rng(2077)

    def vnoise(cells, octaves=1):
        out = np.zeros((TEX, TEX), f32)
        amp, tot = 1.0, 0.0
        for o in range(octaves):
            c = cells * 2 ** o
            g = rng.random((c + 1, c + 1)).astype(f32)
            xi = np.linspace(0, c, TEX, endpoint=False)
            i0 = xi.astype(int)
            f = (xi - i0).astype(f32)
            f = f * f * (3 - 2 * f)
            fx, fy = f[None, :], f[:, None]
            a, b = g[np.ix_(i0, i0)], g[np.ix_(i0, i0 + 1)]
            cc, d = g[np.ix_(i0 + 1, i0)], g[np.ix_(i0 + 1, i0 + 1)]
            out += amp * ((a * (1 - fx) + b * fx) * (1 - fy) + (cc * (1 - fx) + d * fx) * fy)
            tot += amp
            amp *= 0.5
        return out / tot

    def box3(a):
        s = a.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx or dy:
                    s += np.roll(np.roll(a, dy, 0), dx, 1)
        return s / 9

    def lerp(a, b, t):
        return a + (np.asarray(b, f32) - a) * t[..., None]

    def sstep(a, b, x):
        t = np.clip((x - a) / (b - a), 0, 1)
        return t * t * (3 - 2 * t)

    # ---- tile coordinate fields --------------------------------------------------
    ax = (np.arange(TEX, dtype=f32) + 0.5) / PXMM
    TU = np.zeros((TEX, TEX), f32)
    TV = np.zeros((TEX, TEX), f32)
    TW = np.ones((TEX, TEX), f32)
    TH = np.ones((TEX, TEX), f32)
    inside = np.zeros((TEX, TEX), bool)
    SL, M = {}, {}
    for name, (ox, oy, w, h) in TILES.items():
        r0, r1 = int(round(oy * PXMM)), int(round((oy + h) * PXMM))
        c0, c1 = int(round(ox * PXMM)), int(round((ox + w) * PXMM))
        SL[name] = (slice(r0, r1), slice(c0, c1))
        TU[r0:r1, c0:c1] = ax[None, c0:c1] - ox
        TV[r0:r1, c0:c1] = ax[r0:r1, None] - oy
        TW[r0:r1, c0:c1] = w
        TH[r0:r1, c0:c1] = h
        inside[r0:r1, c0:c1] = True
        M[name] = np.zeros((TEX, TEX), bool)
        M[name][r0:r1, c0:c1] = True
    D = np.where(inside, np.minimum(np.minimum(TU, TW - TU), np.minimum(TV, TH - TV)), 99.0).astype(f32)
    Z = np.full((TEX, TEX), 99.0, f32)
    Z[SL["px"]] = TU[SL["px"]] - 15.0
    Z[SL["mx"]] = 15.0 - TU[SL["mx"]]
    Z[SL["front"]] = TV[SL["front"]] - 15.0
    Z[SL["rear"]] = TV[SL["rear"]] - 15.0

    def rect(arr, tile, tu0, tv0, tu1, tv1, val=1.0):
        ox, oy, _, _ = TILES[tile]
        c0, c1 = int(round((ox + tu0) * PXMM)), int(round((ox + tu1) * PXMM))
        r0, r1 = int(round((oy + tv0) * PXMM)), int(round((oy + tv1) * PXMM))
        arr[r0:r1, c0:c1] = val

    def outline(arr, tile, tu0, tv0, tu1, tv1, w):
        rect(arr, tile, tu0, tv0, tu1, tv1, 1.0)
        rect(arr, tile, tu0 + w, tv0 + w, tu1 - w, tv1 - w, 0.0)

    def tri(arr, tile, p0, p1, p2):
        ox, oy, _, _ = TILES[tile]
        pts = np.array([[(ox + u) * PXMM, (oy + v) * PXMM] for u, v in (p0, p1, p2)])
        x0, y0 = np.floor(pts.min(0)).astype(int)
        x1, y1 = np.ceil(pts.max(0)).astype(int)
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        (ax_, ay_), (bx, by), (cx, cy) = pts
        den = (by - cy) * (ax_ - cx) + (cx - bx) * (ay_ - cy)
        l1 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
        l2 = ((cy - ay_) * (gx - cx) + (ax_ - cx) * (gy - cy)) / den
        arr[y0:y1, x0:x1] = np.maximum(arr[y0:y1, x0:x1], ((l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)).astype(f32))

    print(f"  tex: fields {time.time() - t0:.1f}s")

    # ---- base: matte grey paint over ABS, moulded grain -----------------------------
    METAL = np.array([0.34, 0.35, 0.37], f32)                    # dark gunmetal, F0 colour (metallic = 1)
    PALE = METAL
    streak = np.repeat(rng.random((1, TEX)).astype(f32), TEX, 0)  # brushed lines along the atlas rows
    streak = 0.5 * streak + 0.5 * np.repeat(box3(rng.random((1, TEX)).astype(f32)), TEX, 0)
    streak = (streak - streak.mean()) / streak.std()
    albedo = METAL[None, None, :] * (0.93 + 0.05 * vnoise(4, 3) + 0.03 * streak)[..., None]
    gr = streak
    height = 0.004 * streak                                       # mm, barely there
    rough = np.clip(0.36 + 0.04 * streak + 0.05 * vnoise(6, 3), 0, 1)

    # ---- chipped paint: edges first, heaviest at the prong end, plus sparse flakes --------
    edgeband = np.clip(1 - D / (0.9 + 2.2 * vnoise(35, 2)), 0, 1)
    chipn = np.clip((vnoise(55, 3) - 0.46) * 5, 0, 1)
    endb = np.where(M["front"], 1.7, 1 + 0.9 * np.clip(TV / TH, 0, 1) ** 2)
    wear = np.zeros((TEX, TEX), f32)                              # pure metal: no paint to chip
    bare = np.zeros((TEX, TEX), f32)
    albedo = lerp(albedo, PALE * (0.8 + 0.4 * vnoise(120, 2))[..., None], bare * 0.9)
    height = height - 0.07 * bare                                 # the paint has thickness
    rough = rough - 0.22 * bare

    # ---- grime: low-frequency dirt, thicker near edges ------------------------------------
    dirt = np.zeros((TEX, TEX), f32)

    # ---- panel grooves ------------------------------------------------------------------
    groove = np.zeros((TEX, TEX), f32)
    outline(groove, "top", 5.0, 3.5, 45.0, 110.0, 0.4)           # top cover plate
    groove = box3(groove)
    height = height - 0.08 * groove
    albedo = albedo * (1 - 0.5 * groove)[..., None]

    # ---- scratches and the previous owner's tally --------------------------------------
    scr = np.zeros((TEX, TEX), f32)

    def line(p0, p1, amp=1.0):
        n = int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) * PXMM * 2) + 2
        tt = np.linspace(0, 1, n)
        xs = ((p0[0] + (p1[0] - p0[0]) * tt) * PXMM).astype(int)
        ys = ((p0[1] + (p1[1] - p0[1]) * tt) * PXMM).astype(int)
        ok = (xs >= 0) & (xs < TEX) & (ys >= 0) & (ys < TEX)
        scr[ys[ok], xs[ok]] = np.maximum(scr[ys[ok], xs[ok]], amp)

    names = list(TILES)
    wts = np.array([4.0, 3.0, 2.0, 2.0, 1.5, 1.0])
    wts /= wts.sum()
    for _ in range(460):
        t = names[rng.choice(len(names), p=wts)]
        ox, oy, w, h = TILES[t]
        x0, y0 = ox + rng.uniform(0.5, w - 0.5), oy + rng.uniform(0.5, h - 0.5)
        ang = rng.uniform(0, math.pi) if rng.random() < 0.6 else rng.normal(math.pi / 2, 0.35)
        ln = rng.exponential(3.0) + 1.0
        x1 = min(max(x0 + ln * math.cos(ang), ox + 0.3), ox + w - 0.3)
        y1 = min(max(y0 + ln * math.sin(ang), oy + 0.3), oy + h - 0.3)
        line((x0, y0), (x1, y1), rng.uniform(0.45, 1.0))
    tox, toy, _, _ = TILES["top"]

    def tally(tu0, tv0, tu1, tv1):
        j = lambda: rng.normal(0, 0.12)  # noqa: E731
        for off in (0.0, 0.07):
            line((tox + tu0 + j() + off, toy + tv0 + j()), (tox + tu1 + j() + off, toy + tv1 + j()), 1.7)

    for k in range(4):
        tally(12.0 + 2.0 * k, 8.0, 12.0 + 2.0 * k + rng.normal(0, 0.1), 15.0)
    tally(10.4, 9.4, 19.8, 13.6)
    for k in range(3):
        tally(23.5 + 2.0 * k, 8.3, 23.5 + 2.0 * k, 15.2)
    scrs = np.zeros((TEX, TEX), f32)                              # pure metal: no scratch lines
    albedo = lerp(albedo, PALE * 1.15, scrs * (0.45 + 0.4 * vnoise(60, 2)))
    height = height - 0.05 * scrs
    rough = rough + 0.08 * scrs

    # ---- handling: thumb polish round the button, grime in the seam ---------------------
    r = np.sqrt(((TU - (25.0 - BTN_X)) / 13.0) ** 2 + ((TV - (BODY_L / 2 - BTN_Y)) / 11.0) ** 2)
    thumb = (np.clip(1 - r, 0, 1) ** 0.8 * M["top"]).astype(f32)
    thumb = thumb * 0
    seam = (np.exp(-(((Z - SEAM_Z) / 0.9) ** 2)) * (0.55 + 0.45 * vnoise(45, 2))).astype(f32)
    albedo = albedo * (1 - 0.6 * seam)[..., None]
    rough = rough + 0.10 * seam

    if STORY_WEAR:                                                # grease: dark soft smudges round the things hands touch
        gm = np.zeros((TEX, TEX), f32)
        for tile, tu, tv, r in (("mx", 15.0, 93.5, 9.0), ("mx", 15.0, 36.0, 7.0), ("px", 15.0, 38.0, 8.0),
                                ("px", 15.0, 57.5, 6.0), ("top", 3.2, 58.5, 5.5), ("top", 14.0, 88.0, 4.5), ("bottom", 25.0, 15.5, 12.0)):
            gm = np.maximum(gm, np.exp(-(((TU - tu) ** 2 + (TV - tv) ** 2) / (r * r))) * M[tile] * (0.55 + 0.9 * vnoise(40, 2)))
        gm = np.clip(gm, 0, 1).astype(f32)
        albedo = lerp(albedo, (0.020, 0.017, 0.012), gm * 0.55)
        rough = rough - 0.10 * gm

    print(f"  tex: wear and handling {time.time() - t0:.1f}s")

    # ---- printed text, arrow, stickers ----------------------------------------------------
    items = []
    for ch, s, size, tile, tu, tv, rot in _text_items():
        ox, oy, _, _ = TILES[tile]
        items.append((ch, s, size, ox + tu, oy + tv, rot))
    m_top, m_lab, m_cert = _render_masks(items, TEX, TEX, AWMM, AWMM, tex_dir)
    print(f"  tex: text render {time.time() - t0:.1f}s")

    arrow = np.zeros((TEX, TEX), f32)
    tri(arrow, "top", (22.8, 108.9), (27.2, 108.9), (25.0, 111.9))   # points at the prongs
    fade = np.clip(0.70 + 0.45 * (vnoise(150, 2) - 0.5) - 0.35 * wear, 0.25, 1.0)
    ink = np.clip(np.maximum(m_top, arrow) * fade, 0, 1)
    albedo = lerp(albedo, (0.012, 0.012, 0.014), ink * 0.92)      # dark print on bare metal

    stick = np.zeros((TEX, TEX), f32)
    rect(stick, "bottom", 10.5, 38.0, 39.5, 66.0)                      # label
    bars = np.zeros((TEX, TEX), f32)
    x, on = 12.0, True
    while x < 38.0:
        wbar = float(rng.choice([0.3, 0.3, 0.6, 0.9]))
        if on:
            rect(bars, "bottom", x, 41.5, min(x + wbar, 38.0), 47.5)
        x += wbar
        on = not on
    rect(bars, "bottom", 11.5, 55.2, 38.5, 55.45)
    stick = box3(stick)
    paper = np.array([0.46, 0.45, 0.41], f32)
    pcol = paper[None, None, :] * (0.80 + 0.35 * vnoise(30, 3))[..., None]
    pcol = pcol * (1 - 0.35 * np.clip(vnoise(90, 2) - 0.55, 0, 1) * 2)[..., None]
    albedo = lerp(albedo, pcol, stick)
    lab = np.clip(np.maximum(m_lab, bars), 0, 1) * stick
    albedo = lerp(albedo, (0.022, 0.022, 0.024), lab * 0.92)

    cert = np.zeros((TEX, TEX), f32)
    rect(cert, "bottom", 11.0, 78.0, 39.0, 94.0)                       # compassionate-use sticker, half peeled
    s = (TU - 39.0) + (TV - 94.0)
    cert = cert * (s <= -3.0) * M["bottom"]
    curl = ((s > -3.0) & (s < -2.4) & M["bottom"]).astype(f32) * (np.roll(cert, 3, 1) > 0)
    cert = box3(cert.astype(f32))
    ccol = np.array([0.13, 0.17, 0.26], f32)[None, None, :] * (0.7 + 0.5 * vnoise(25, 3))[..., None]
    albedo = lerp(albedo, ccol, cert * 0.85)
    albedo = lerp(albedo, (0.45, 0.46, 0.48), np.clip(curl, 0, 1))
    albedo = lerp(albedo, (0.58, 0.60, 0.64), np.clip(m_cert * cert * (0.55 + 0.3 * fade), 0, 1))

    cover = np.clip(stick + cert, 0, 1)
    height = height * (1 - 0.8 * cover) + 0.10 * stick + 0.06 * cert
    rough = lerp(rough[..., None].repeat(3, -1), (0.38, 0.38, 0.38), cover)[..., 0]

    stencil_a = np.zeros((TEX, TEX), f32)
    w3 = np.zeros((TEX, TEX), f32)
    if STORY_WEAR:                                                # previous owner's initials, a mostly worn-off ICS stencil, an ICS-W3 sliver
        bx, by, _, _ = TILES["bottom"]
        px_, py_, _, _ = TILES["px"]
        ex = [(0, "R.H.", 2.3, bx + 38.5, by + 77.0, -6),                       # scratched into the underside
              (1, "PROPERTY OF ICS", 2.4, px_ + 10.0, py_ + 97.5, 90),          # stencil on the +X side, mostly worn off
              (2, "ICS-W3", 0.9, bx + 40.2, by + 58.0, 90)]                     # printed on the paper sliver under the label
        m_ini, m_sten, m_w3 = _render_masks(ex, TEX, TEX, AWMM, AWMM, tex_dir)
        scr_i = np.clip(box3(m_ini) * (0.55 + 0.45 * vnoise(80, 2)), 0, 1)
        albedo = lerp(albedo, (0.62, 0.62, 0.65), scr_i * 0.7)
        height = height - 0.05 * scr_i
        patch = np.clip((vnoise(50, 3) - 0.40) * 4.0, 0, 1)
        stencil_a = np.clip(m_sten * patch * 0.9, 0, 1).astype(f32)
        albedo = lerp(albedo, (0.018, 0.045, 0.13), stencil_a)
        rough = np.where(stencil_a > 0.05, 0.62, rough)
        strip = np.zeros((TEX, TEX), f32)                                       # Form ICS-W3 paper tucked under the label's right edge
        rect(strip, "bottom", 33.0, 54.0, 41.0, 62.0)
        w3 = (box3(strip) * (1 - stick)).astype(f32)
        wcol = np.array([0.52, 0.48, 0.36], f32)[None, None, :] * (0.85 + 0.3 * vnoise(40, 3))[..., None]
        albedo = lerp(albedo, wcol, w3)
        albedo = lerp(albedo, (0.03, 0.03, 0.045), np.clip(m_w3 * w3, 0, 1) * 0.9)
        rough = np.where(w3 > 0.05, 0.85, rough)
        height = height + 0.06 * w3

    # ---- normal map from the height field (mm) ----------------------------------------------
    du = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * (PXMM / 2)
    dv = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * (PXMM / 2)
    nx, ny, nz = -du, -dv, np.ones_like(height)
    ln = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    normal = np.stack([nx / ln * 0.5 + 0.5, ny / ln * 0.5 + 0.5, nz / ln * 0.5 + 0.5], -1).astype(f32)

    print(f"  tex: body done {time.time() - t0:.1f}s")
    nonmetal = np.clip(np.maximum(np.maximum(np.maximum(ink, stencil_a), w3), np.maximum(cover, lab)), 0, 1)       # print, label paper and sticker are not metal
    rough = np.where(ink > 0.05, 0.55, rough)
    metal = (1.0 - nonmetal).astype(f32)
    return {"albedo": encode_srgb(np.clip(albedo, 0, 1)).astype(f32), "normal": normal, "metal": metal,
            "rough": np.clip(rough, 0.12, 1).astype(f32)}


# ---- trim atlas: swatches for the small parts ---------------------------------------------
TRIM_N, TRIM_S = 1024, 512


def make_trim(tex_dir):
    """Swatch 0 dark ABS (shroud, cap), 1 rubber (grip, cord), 2 dark steel (screws, switch), 3 red plastic (button)."""
    rng = np.random.default_rng(404)
    S = TRIM_S
    N = TRIM_N

    def vn(cells, octaves=1):
        out = np.zeros((S, S), f32)
        amp, tot = 1.0, 0.0
        for o in range(octaves):
            c = cells * 2 ** o
            g = rng.random((c + 1, c + 1)).astype(f32)
            xi = np.linspace(0, c, S, endpoint=False)
            i0 = xi.astype(int)
            f = (xi - i0).astype(f32)
            f = f * f * (3 - 2 * f)
            fx, fy = f[None, :], f[:, None]
            a, b = g[np.ix_(i0, i0)], g[np.ix_(i0, i0 + 1)]
            cc, d = g[np.ix_(i0 + 1, i0)], g[np.ix_(i0 + 1, i0 + 1)]
            out += amp * ((a * (1 - fx) + b * fx) * (1 - fy) + (cc * (1 - fx) + d * fx) * fy)
            tot += amp
            amp *= 0.5
        return out / tot

    def blur(a):
        s = a.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx or dy:
                    s += np.roll(np.roll(a, dy, 0), dx, 1)
        return s / 9

    def scratches(n, length=60, amp=1.0):
        sc = np.zeros((S, S), f32)
        n = 0                                                   # clean surfaces: no scratch lines
        for _ in range(n):
            x0, y0 = rng.uniform(0, S), rng.uniform(0, S)
            ang = rng.uniform(0, math.pi)
            ln = rng.exponential(length) + 8
            tt = np.linspace(0, 1, int(ln) + 2)
            xs = np.clip((x0 + ln * math.cos(ang) * tt).astype(int), 0, S - 1)
            ys = np.clip((y0 + ln * math.sin(ang) * tt).astype(int), 0, S - 1)
            sc[ys, xs] = rng.uniform(0.4, 1.0) * amp
        return np.clip(blur(sc) * 3, 0, 1)

    alb = np.zeros((N, N, 3), f32)
    rgh = np.zeros((N, N), f32)
    hgt = np.zeros((N, N), f32)

    def put(i, a, r_, h_):
        col, row = i % 2, i // 2
        sl = (slice(row * S, (row + 1) * S), slice(col * S, (col + 1) * S))
        alb[sl], rgh[sl], hgt[sl] = a, r_, h_

    g = blur(rng.random((S, S)).astype(f32))
    g = (g - g.mean()) / g.std()
    # 0 dark ABS
    sc = scratches(40)
    a0 = np.array([0.040, 0.042, 0.048], f32) * (0.8 + 0.4 * vn(6, 3))[..., None]
    a0 = a0 + (sc * 0.07)[..., None]
    put(0, a0, np.clip(0.60 + 0.06 * g + 0.1 * sc, 0, 1), 0.02 * g - 0.04 * sc)
    # 1 rubber: pebbled
    peb = blur(blur(rng.random((S, S)).astype(f32)))
    peb = (peb - peb.mean()) / peb.std()
    a1 = np.array([0.012, 0.012, 0.013], f32) * (0.8 + 0.5 * vn(10, 2))[..., None]
    a1 = a1 + (np.clip(peb, 0, 3) * 0.004)[..., None]
    put(1, a1, np.clip(0.86 + 0.06 * vn(8, 2), 0, 1), 0.07 * peb)
    # 2 dark steel: brushed, scratched
    st = np.repeat(blur(rng.random((S, 1)).astype(f32)), S, axis=1)
    st = 0.6 * st + 0.4 * vn(4, 2) * 0 + 0.4 * np.repeat(rng.random((S, 1)).astype(f32), S, axis=1)
    sc = scratches(70, 40)
    a2 = np.array([0.30, 0.31, 0.33], f32) * (0.75 + 0.5 * st)[..., None]
    a2 = a2 * (1 - 0.25 * np.clip(vn(5, 3) - 0.5, 0, 1) * 2)[..., None] + (sc * 0.12)[..., None]
    put(2, a2, np.clip(0.34 + 0.22 * st + 0.1 * sc, 0, 1), 0.012 * (st - 0.5) - 0.03 * sc)
    # 3 red button plastic: scuffed, a lighter wear patch
    sc = scratches(55, 35)
    patch = np.clip((vn(3, 3) - 0.55) * 4, 0, 1)
    a3 = np.array([0.27, 0.018, 0.016], f32) * (0.85 + 0.3 * vn(7, 3))[..., None]
    a3 = a3 * (1 - 0.25 * np.clip(vn(9, 3) - 0.5, 0, 1) * 2)[..., None]
    a3 = a3 + (patch * 0.10 + sc * 0.13)[..., None] * np.array([1.0, 0.45, 0.4], f32)
    put(3, a3, np.clip(0.44 + 0.06 * g - 0.12 * patch + 0.08 * sc, 0, 1), 0.015 * g - 0.04 * sc)

    du = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) * 6.0
    dv = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) * 6.0
    nx, ny, nz = -du, -dv, np.ones_like(hgt)
    ln = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    normal = np.stack([nx / ln * 0.5 + 0.5, ny / ln * 0.5 + 0.5, nz / ln * 0.5 + 0.5], -1).astype(f32)
    return {"albedo": encode_srgb(np.clip(alb, 0, 1)).astype(f32), "normal": normal, "rough": np.clip(rgh, 0.1, 1).astype(f32)}


# ---- the screen ---------------------------------------------------------------------------
def make_lcd(tex_dir, charged=True):
    """Emission colour image, LCD_PX_W x LCD_PX_H. Amber when charged, red when discharged. [PROPOSAL] layout and wording."""
    W, H = LCD_PX_W, LCD_PX_H
    pxmm = W / LCD_W
    tint = np.array([1.0, 0.50, 0.07] if charged else [1.0, 0.07, 0.05], f32)
    items = []
    if charged:
        items += [(0, "READY", 4.7, 9.4, 8.6, 0), (1, "CONTACT  90 s", 1.7, 9.4, 3.1, 0), (1, "CHG 100%", 1.7, 25.0, 3.1, 0)]
    else:
        items += [(0, "DISCHARGED", 3.1, 9.9, 8.6, 0), (1, "RECHARGE", 1.7, 9.4, 3.1, 0), (1, "CHG 0%", 1.7, 25.0, 3.1, 0)]
    items += [(1, "CRD-7", 1.1, 4.5, 11.9, 0), (1, "ICS EARTH BRANCH", 1.0, 25.5, 11.9, 0)]
    m0, m1, _ = _render_masks(items, W, H, LCD_W, LCD_H, tex_dir)

    yy, xx = (np.mgrid[0:H, 0:W] + 0.5) / pxmm              # mm, y up
    fg = np.zeros((H, W), f32)
    # charge bar: five segments
    for k in range(5):
        x0 = 19.7 + k * 2.15
        seg = (xx >= x0) & (xx < x0 + 1.8) & (yy >= 6.4) & (yy < 10.6)
        if charged:
            fg = np.maximum(fg, seg.astype(f32))
        else:
            hollow = seg & ~((xx >= x0 + 0.28) & (xx < x0 + 1.52) & (yy >= 6.68) & (yy < 10.32))
            fg = np.maximum(fg, hollow.astype(f32) * 0.8)
    # frame and a rule under the header
    d_ = 0.6
    box = (xx > d_) & (xx < LCD_W - d_) & (yy > d_) & (yy < LCD_H - d_)
    box_in = (xx > d_ + 0.16) & (xx < LCD_W - d_ - 0.16) & (yy > d_ + 0.16) & (yy < LCD_H - d_ - 0.16)
    fg = np.maximum(fg, (box & ~box_in).astype(f32) * 0.5)
    fg = np.maximum(fg, ((np.abs(yy - 11.0) < 0.09) & (xx > 1.2) & (xx < LCD_W - 1.2)).astype(f32) * 0.45)
    lum = np.clip(np.maximum(fg, np.maximum(m0, m1 * 0.85)), 0, 1)
    # dot-matrix grid, scanlines, vignette, a faint glare
    grid = 0.82 + 0.18 * (np.abs(np.sin(xx * math.pi / 0.42)) * np.abs(np.sin(yy * math.pi / 0.42)))
    scan = 0.94 + 0.06 * np.sin(yy * math.pi / 0.21)
    vig = 1 - 0.35 * (((xx / LCD_W - 0.5) * 2) ** 2 + ((yy / LCD_H - 0.5) * 2) ** 2) ** 1.5
    img = (0.07 + 0.93 * lum * grid) * scan * vig
    img = img + 0.05 * np.clip(1 - np.abs((xx / LCD_W) - (yy / LCD_H) * 0.8 - 0.35) * 6, 0, 1) * (1 - lum)
    rgb = img[..., None] * tint[None, None, :] * np.array([0.9, 0.9, 0.9], f32)
    return encode_srgb(np.clip(rgb, 0, 1)).astype(f32)


# ---- small printed parts: brass asset plate, maintenance tag, evidence tape ------------------
PLATE_MM = (22.0, 7.4)
TAG_MM = (24.0, 14.0)
TAPE_MM = (42.0, 6.0)
PLATE_PX = 24.0


def _px(wh):
    return int(wh[0] * PLATE_PX), int(wh[1] * PLATE_PX)


def make_plates(tex_dir):
    """Returns dict name -> sRGB float image (h, w, 3): plate, tag, tape. All three are [PROPOSAL] story props."""
    rng = np.random.default_rng(3382)
    out = {}

    def noise(h, w, cells):
        g = rng.random((cells + 1, cells + 1)).astype(f32)
        yi = np.linspace(0, cells, h, endpoint=False)
        xi = np.linspace(0, cells, w, endpoint=False)
        y0, x0 = yi.astype(int), xi.astype(int)
        fy, fx = (yi - y0)[:, None], (xi - x0)[None, :]
        a, b = g[np.ix_(y0, x0)], g[np.ix_(y0, x0 + 1)]
        c, d = g[np.ix_(y0 + 1, x0)], g[np.ix_(y0 + 1, x0 + 1)]
        return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

    # engraved brass plate: dark filled lettering, thin engraved border
    W, H = _px(PLATE_MM)
    w, h = PLATE_MM
    m0, _, _ = _render_masks([(0, "ASSET No.", 1.1, w / 2, h * 0.76, 0), (0, "ICS-SEC-1182", 1.95, w / 2, h * 0.48, 0),
                              (0, "PTKW  LVL 5 STORE", 0.95, w / 2, h * 0.19, 0)], W, H, w, h, tex_dir)
    brass = np.array([0.60, 0.43, 0.15], f32)
    streak = np.repeat(rng.random((1, W)).astype(f32), H, 0)
    img = brass[None, None, :] * (0.88 + 0.07 * streak + 0.10 * noise(H, W, 6))[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    edge = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy)) / PLATE_PX
    border = ((edge > 0.45) & (edge < 0.70)).astype(f32)
    ink = np.clip(np.maximum(m0, border), 0, 1)[..., None]
    img = img * (1 - 0.88 * ink) + np.array([0.035, 0.022, 0.010], f32) * 0.88 * ink
    out["plate"] = encode_srgb(np.clip(img, 0, 1)).astype(f32)

    # maintenance tag: manila card, printed form, handwritten dates in blue-black ink
    W, H = _px(TAG_MM)
    w, h = TAG_MM
    printed = _render_masks([
        (0, "ICS-EP SERVICE TAG", 1.25, w / 2 + 1.5, h * 0.85, 0), (0, "CRD-7   S/N 3382", 1.0, w / 2 + 1.5, h * 0.70, 0),
        (0, "LAST SERVICED", 0.85, 7.0, h * 0.54, 0), (0, "NEXT DUE", 0.85, 5.0, h * 0.30, 0)], W, H, w, h, tex_dir)[0]
    hw_, _, _ = _render_masks([(0, "CYC 288", 1.9, 17.2, h * 0.53, 2), (0, "CYC 290", 1.9, 15.2, h * 0.29, -3),
                               (0, "overdue?", 1.5, 14.5, h * 0.09, -5)], W, H, w, h, tex_dir)
    card = np.array([0.66, 0.58, 0.40], f32)
    img = card[None, None, :] * (0.88 + 0.12 * noise(H, W, 8) + 0.05 * (rng.random((H, W)).astype(f32) - 0.5))[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    img = img * (1 - 0.25 * np.clip(1 - np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy)) / 6.0, 0, 1))[..., None]
    hole = (((xx - 2.6 * PLATE_PX) ** 2 + (yy - H / 2) ** 2) < (0.9 * PLATE_PX) ** 2)
    pi = np.clip(printed, 0, 1)[..., None] * 0.85
    img = img * (1 - pi) + np.array([0.04, 0.04, 0.045], f32) * pi
    hi = np.clip(hw_, 0, 1)[..., None] * (0.75 + 0.25 * noise(H, W, 30))[..., None]
    img = img * (1 - hi) + np.array([0.03, 0.05, 0.16], f32) * hi
    img = np.where(hole[..., None], np.array([0.02, 0.02, 0.02], f32), img)
    out["tag"] = encode_srgb(np.clip(img, 0, 1)).astype(f32)

    # evidence tape: deep blue, repeating pale lettering
    W, H = _px(TAPE_MM)
    w, h = TAPE_MM
    m_t, _, _ = _render_masks([(0, "ICS SECURITY SEALED", 1.8, x, h / 2, 0) for x in (10.5, 31.5)], W, H, w, h, tex_dir)
    blue = np.array([0.020, 0.040, 0.115], f32)
    img = blue[None, None, :] * (0.85 + 0.25 * noise(H, W, 10))[..., None]
    pi = np.clip(m_t, 0, 1)[..., None] * 0.9
    img = img * (1 - pi) + np.array([0.60, 0.62, 0.70], f32) * pi
    out["tape"] = encode_srgb(np.clip(img, 0, 1)).astype(f32)
    return out
