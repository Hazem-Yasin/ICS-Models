"""
ICS Earth Branch mark: single source of geometry. Pure Python (no numpy) for the core, so plain `python3` can build the
SVG masters; the `raster_*` helpers import numpy lazily and are meant for the Blender texture scripts.

Canon (ICS-Writing/canon/documents/2.32): a circle (ICS Deep Blue #1A2E52) and ONE gold arc (Warm Gold #C9A84C).
The arc begins below and outside the circle (lower left), rises up and over, and comes to rest at the base (lower
right) -- it never leaves the circle again. Rounded everything, no sharp angles. Isolated, the arc reads as a
fishhook (the PTKW note). Board reading: an ouroboros with the serpent removed.

Everything below the canon line is a [PROPOSAL] and is listed in Logo/BRAND_MARK.md: exact arc angles / radii /
width profile, the knock-out gap between arc and circle, the stroke-built "ICS" wordmark, the small-size optical
variant, lockups and clear space.

Coordinates: mark space, circle radius = 1.0, centre (0, 0), +y up (maths convention). SVG writers flip y.
"""
import math

BLUE_HEX = "#1A2E52"
GOLD_HEX = "#C9A84C"
BLUE_LIN = (0.012, 0.027, 0.085)   # linear, as used in the Blender scripts
GOLD_LIN = (0.58, 0.39, 0.075)
PAPER_HEX = "#F4F1EA"              # [PROPOSAL] warm off-white used for the "globe in white" treatments

# ---- the arc [PROPOSAL geometry] --------------------------------------------------------------------------------
# Clockwise spiral. Angles in degrees, 0 = +x, 90 = up. th0 = where the tail starts (lower left, outside the circle);
# th1 = where it comes to rest (lower right, inside the circle edge). Radius spirals from R0 (outside) to R1 (inside).
ARC = dict(th0=216.0, th1=-100.0, r0=1.30, r1=0.70, q=1.0, a=0.90,
           w0=0.050, wm=0.150, w1=0.085, tm=0.50)
# Optical variant for marks rendered under ~32 px or ~8 mm (floor 16 px / 5 mm): heavier arc, wider gap, blunter ends.
ARC_SMALL = dict(ARC, w0=0.14, wm=0.27, w1=0.20, r0=1.27)
GAP = 0.050          # knock-out ring cut out of the circle around the arc, in circle radii
GAP_SMALL = 0.10


def _smooth(u):
    return 0.5 - 0.5 * math.cos(math.pi * u)


def width_at(t, p=ARC):
    tm = p["tm"]
    if t < tm:
        return p["w0"] + (p["wm"] - p["w0"]) * math.sin((t / tm) * math.pi / 2)
    return p["wm"] + (p["w1"] - p["wm"]) * _smooth((t - tm) / (1 - tm))


def centerline(p=ARC, n=480, upto=1.0):
    """Points (x, y, width) along the arc, t in [0, upto]."""
    out = []
    for i in range(n + 1):
        t = upto * i / n
        th = math.radians(p["th0"] + (p["th1"] - p["th0"]) * (t ** p["a"]))
        r = p["r1"] + (p["r0"] - p["r1"]) * (1 - t) ** p["q"]
        out.append((r * math.cos(th), r * math.sin(th), width_at(t, p)))
    return out


def arc_outline(p=ARC, n=480, upto=1.0, cap_steps=14, grow=0.0):
    """Closed polygon (list of (x, y)) of the arc with round caps. grow = extra half-width on each side (the knock-out)."""
    c = [(x, y, w + 2 * grow) for x, y, w in centerline(p, n, upto)]
    L, R = [], []
    for i, (x, y, w) in enumerate(c):
        a = c[max(i - 1, 0)]
        b = c[min(i + 1, len(c) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tx, ty) or 1.0
        tx, ty = tx / ln, ty / ln
        h = w / 2
        L.append((x - ty * h, y + tx * h))
        R.append((x + ty * h, y - tx * h))

    def cap(p0, p1):
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        h = math.hypot(p0[0] - p1[0], p0[1] - p1[1]) / 2
        a0 = math.atan2(p0[1] - cy, p0[0] - cx)
        return [(cx + h * math.cos(a0 - math.pi * j / cap_steps), cy + h * math.sin(a0 - math.pi * j / cap_steps))
                for j in range(1, cap_steps)]
    return L + cap(L[-1], R[-1]) + R[::-1] + cap(R[0], L[0])


def mark_bbox(small=False):
    """(x0, x1, y0, y1) of the whole mark (circle + arc) in mark units."""
    poly = arc_outline(ARC_SMALL if small else ARC, n=240)
    xs = [x for x, _ in poly] + [-1.0, 1.0]
    ys = [y for _, y in poly] + [-1.0, 1.0]
    return min(xs), max(xs), min(ys), max(ys)


# ---- SVG helpers -------------------------------------------------------------------------------------------------
def _pts(poly, ox, oy, s):
    return " ".join(f"{ox + s * x:.2f},{oy - s * y:.2f}" for x, y in poly)


def mark_group(ox, oy, s, blue=BLUE_HEX, gold=GOLD_HEX, small=False, upto=1.0, uid="m", circle=True, arc=True):
    """SVG <g> of the mark centred at (ox, oy), circle radius s px. The knock-out is a mask so one-colour versions work."""
    p = ARC_SMALL if small else ARC
    g = GAP_SMALL if small else GAP
    poly = _pts(arc_outline(p, upto=upto), ox, oy, s)
    parts = []
    if circle:
        if arc:
            parts.append(
                f'<mask id="{uid}-ko" maskUnits="userSpaceOnUse" x="{ox - 2 * s:.1f}" y="{oy - 2 * s:.1f}" '
                f'width="{4 * s:.1f}" height="{4 * s:.1f}"><rect x="{ox - 2 * s:.1f}" y="{oy - 2 * s:.1f}" '
                f'width="{4 * s:.1f}" height="{4 * s:.1f}" fill="#fff"/>'
                f'<polygon points="{poly}" fill="#000" stroke="#000" stroke-width="{2 * g * s:.2f}" '
                f'stroke-linejoin="round"/></mask>')
            parts.append(f'<circle cx="{ox}" cy="{oy}" r="{s}" fill="{blue}" mask="url(#{uid}-ko)"/>')
        else:
            parts.append(f'<circle cx="{ox}" cy="{oy}" r="{s}" fill="{blue}"/>')
    if arc:
        parts.append(f'<polygon points="{poly}" fill="{gold}"/>')
    return "<g>" + "".join(parts) + "</g>"


# ---- wordmark: "ICS" built from round-capped strokes [PROPOSAL] ---------------------------------------------------
# Cap height 1.0, stroke 0.215. Every end is a semicircle: there is no sharp angle anywhere in the letterforms.
WM_H = 1.0
WM_S = 0.17
WM_GAP = 0.20          # clear space between letters, measured between stroke edges


def _ell(cx, cy, rx, ry, deg0, deg1, n=40):
    return [(cx + rx * math.cos(math.radians(deg0 + (deg1 - deg0) * i / n)),
             cy + ry * math.sin(math.radians(deg0 + (deg1 - deg0) * i / n))) for i in range(n + 1)]


def wordmark_strokes(x0=0.0):
    """Returns ([polyline, ...], advance_width). Polylines are centrelines; stroke them with WM_S and round caps."""
    H, s = WM_H, WM_S
    strokes = []
    x = x0
    # I
    strokes.append([(x + s / 2, s / 2), (x + s / 2, H - s / 2)])
    x += s + WM_GAP
    # C: opening to the right, an echo of the open arc
    rx, ry = 0.33, (H - s) / 2
    cx, cy = x + s / 2 + rx, H / 2
    strokes.append(_ell(cx, cy, rx, ry, 42, 318, 60))
    x = cx + rx + s / 2 + WM_GAP - 0.03
    # S: two stacked ellipses, one continuous stroke
    ry = (H - s) / 4
    rx = 0.28
    cx = x + s / 2 + rx
    top = (cx, H - s / 2 - ry)
    bot = (cx, s / 2 + ry)
    up = _ell(top[0], top[1], rx, ry, 28, 270, 50)           # upper-right terminal, over the top, to the middle
    lo = _ell(bot[0], bot[1], rx, ry, 90, -152, 50)          # middle, round the right, to the lower-left terminal
    strokes.append(up + lo[1:])
    x = cx + rx + s / 2
    return strokes, x - x0


def wordmark_svg(ox, oy, h, color=BLUE_HEX):
    """<g> with the wordmark, cap height h px, baseline at oy (SVG y down), left edge ox."""
    strokes, w = wordmark_strokes()
    paths = []
    for pl in strokes:
        d = "M" + " L".join(f"{ox + h * x:.2f},{oy - h * y:.2f}" for x, y in pl)
        paths.append(f'<path d="{d}"/>')
    return (f'<g fill="none" stroke="{color}" stroke-width="{h * WM_S:.2f}" stroke-linecap="round" '
            f'stroke-linejoin="round">' + "".join(paths) + "</g>"), w * h


# ---- numpy raster helpers (Blender texture scripts) ----------------------------------------------------------------
def _np():
    import numpy as np
    return np


def _sdf_capsule_chain(X, Y, pts):
    """Signed distance (negative inside) to a chain of discs swept along pts = [(x, y, w)], round caps for free."""
    np = _np()
    sd = np.full(X.shape, 9.0, dtype=np.float32)
    for x, y, w in pts:
        np.minimum(sd, np.hypot(X - x, Y - y) - w / 2, out=sd)
    return sd


def raster_mark(w_px, h_px, ppu, cx, cy, small=False, upto=1.0):
    """Coverage maps of the mark on a w_px x h_px grid. ppu = pixels per mark unit (circle radius). (cx, cy) = centre in
    px from the bottom-left (row 0 = bottom, as Blender image rows). Returns (blue, gold) float32 arrays in 0..1."""
    np = _np()
    p = ARC_SMALL if small else ARC
    gap = GAP_SMALL if small else GAP
    ys, xs = np.mgrid[0:h_px, 0:w_px]
    X = ((xs + 0.5) - cx) / ppu
    Y = ((ys + 0.5) - cy) / ppu
    n = int(max(120, min(900, 3.5 * ppu)))
    sd_arc = _sdf_capsule_chain(X, Y, centerline(p, n, upto))
    sd_circle = np.hypot(X, Y) - 1.0
    gold = np.clip(0.5 - sd_arc * ppu, 0, 1)
    blue = np.clip(0.5 - sd_circle * ppu, 0, 1) * np.clip(0.5 + (sd_arc - gap) * ppu, 0, 1)
    return blue.astype(np.float32), gold.astype(np.float32)


def raster_wordmark(w_px, h_px, ppu, x0, y0):
    """Coverage of the ICS wordmark. ppu = pixels per cap height; (x0, y0) = baseline-left in px from bottom-left."""
    np = _np()
    ys, xs = np.mgrid[0:h_px, 0:w_px]
    X = ((xs + 0.5) - x0) / ppu
    Y = ((ys + 0.5) - y0) / ppu
    strokes, _ = wordmark_strokes()
    sd = np.full(X.shape, 9.0, dtype=np.float32)
    for pl in strokes:
        # densify to ~0.01 spacing, then chain of discs
        dense = []
        for (ax, ay), (bx, by) in zip(pl[:-1], pl[1:]):
            k = max(1, int(math.hypot(bx - ax, by - ay) / 0.012))
            dense += [(ax + (bx - ax) * j / k, ay + (by - ay) * j / k, WM_S) for j in range(k)]
        dense.append((pl[-1][0], pl[-1][1], WM_S))
        sd = np.minimum(sd, _sdf_capsule_chain(X, Y, dense))
    return np.clip(0.5 - sd * ppu, 0, 1).astype(np.float32)
