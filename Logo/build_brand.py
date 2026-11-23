"""
Builds the ICS Earth Branch brand kit from Logo/src/ics_brand.py: SVG masters, lockups, construction sheet, and PNG
exports. Plain python3 + ffmpeg (librsvg). Run from anywhere:  python3 Logo/build_brand.py
Everything here is a [PROPOSAL] on top of Doc 2.32; see Logo/BRAND_MARK.md.
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))
import ics_brand as b  # noqa: E402
import ics_seal as sl  # noqa: E402

SVG = os.path.join(HERE, "svg")
PNG = os.path.join(HERE, "png")
for d in (SVG, PNG):
    os.makedirs(d, exist_ok=True)

BLUE, GOLD, PAPER = b.BLUE_HEX, b.GOLD_HEX, b.PAPER_HEX
TAGLINE = "Because You’re Worth the Investment."
FONT = "Nunito, 'Varela Round', 'Arial Rounded MT Bold', sans-serif"


def doc(w, h, body, bg=None, title=""):
    bgr = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<title>{title}</title>{bgr}{body}</svg>')


def save(name, w, h, body, bg=None, title="", png=True, png_w=None):
    p = os.path.join(SVG, name + ".svg")
    open(p, "w", encoding="utf-8").write(doc(w, h, body, bg, title or name))
    if png:
        out = os.path.join(PNG, name + ".png")
        sc = ["-vf", f"scale={png_w}:-1:flags=lanczos"] if png_w else []
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p] + sc + [out], check=True)


# The mark's bounding box in mark units (circle radius 1): the tail reaches about x -1.30 .. 1.0, y -1.0 .. 1.30
def mark_box():
    pts = b.arc_outline()
    xs = [p[0] for p in pts] + [-1, 1]
    ys = [p[1] for p in pts] + [-1, 1]
    return min(xs), max(xs), min(ys), max(ys)


X0, X1, Y0, Y1 = mark_box()
MW, MH = X1 - X0, Y1 - Y0


def mark_only(name, size=1024, blue=BLUE, gold=GOLD, bg=None, small=False, pad=0.08, title="", png_w=None):
    s = size * (1 - 2 * pad) / max(MW, MH)
    ox = size / 2 - s * (X0 + X1) / 2
    oy = size / 2 + s * (Y0 + Y1) / 2
    save(name, size, size, b.mark_group(ox, oy, s, blue, gold, small=small, uid="k"), bg, title or name, png_w=png_w)


# ---- 1. marks: colour, optical-small, one-colour, reversed, trailer -------------------------------------------------
mark_only("ics-mark", title="ICS Earth Branch mark")
mark_only("ics-mark-small", small=True, title="ICS Earth Branch mark, small-size optical variant")
mark_only("ics-mark-mono-blue", blue=BLUE, gold=BLUE, title="Mark, one colour: Deep Blue")
mark_only("ics-mark-mono-black", blue="#111111", gold="#111111", title="Mark, one colour: black")
mark_only("ics-mark-mono-white", blue="#FFFFFF", gold="#FFFFFF", bg=BLUE, title="Mark, one colour: white on Deep Blue")
mark_only("ics-mark-reversed", blue=PAPER, gold=GOLD, bg=BLUE, title="Mark reversed: paper circle, gold arc, Deep Blue field")
mark_only("ics-mark-on-white", bg="#FFFFFF", title="Mark on white")
mark_only("ics-mark-trailer", blue="#FFFFFF", gold=GOLD, bg="#0B1426",
          title="Trailer treatment: the globe in white, the arc in gold")
# gold-on-white title card (Trailer 3): arc gold, circle outline-free white -> arc alone is visible; use paper
mark_only("ics-mark-gold-on-white", blue=PAPER, gold=GOLD, bg="#FFFFFF", title="Gold on white title card")

# ---- 2. the hook, isolated (the PTKW note; internal asset) -----------------------------------------------------------
sz = 1024
s = sz * 0.84 / max(MW, MH)
save("ics-arc-isolated", sz, sz,
     b.mark_group(sz / 2 - s * (X0 + X1) / 2, sz / 2 + s * (Y0 + Y1) / 2, s, BLUE, GOLD, circle=False, uid="h"),
     bg="#FFFFFF", title="The arc alone. It resembles a fishhook; the resemblance is coincidental.")

# ---- 3. app icon / favicon: circle crop of the mark on Deep Blue -----------------------------------------------------
def icon(name, size, rounded=True):
    r = size * 0.22 if rounded else 0
    s = size * 0.60 / 2
    ox, oy = size * 0.50 + s * 0.10, size * 0.50 - s * 0.06
    body = (f'<rect width="{size}" height="{size}" rx="{r:.1f}" fill="{BLUE}"/>'
            + b.mark_group(ox, oy, s, PAPER, GOLD, small=True, uid="i"))
    save(name, size, size, body, title=name)


icon("ics-icon-512", 512)
icon("ics-icon-64", 64)

# ---- 4. lockups -------------------------------------------------------------------------------------------------------
def lockup_h(name, bg=None, blue=BLUE, gold=GOLD, word=BLUE, tagline=False, h=400):
    s = h * 0.46
    pad = h * 0.14
    ox = pad + s * (-X0)
    oy = pad + s * Y1
    mark_h = s * MH
    cap = s * 1.15                                    # wordmark cap height
    wx = pad + s * MW + s * 0.36
    wy = pad + mark_h * 0.60 + cap / 2                # vertically centred on the circle (circle centre at oy)
    wy = oy + cap / 2 - (0.16 * s if tagline else 0)
    wm, adv = b.wordmark_svg(wx, wy, cap, word)
    width = wx + max(adv, cap * 0.19 * 19.5 if tagline else 0) + pad
    height = pad * 2 + mark_h
    body = b.mark_group(ox, oy, s, blue, gold, uid=name[-6:]) + wm
    if tagline:
        ty = height - pad * 0.15
        body += (f'<text x="{wx:.1f}" y="{oy + 0.80 * s:.1f}" font-family="{FONT}" font-weight="600" '
                 f'font-size="{cap * 0.19:.1f}" fill="{word}" letter-spacing="{cap * 0.004:.2f}">{TAGLINE}</text>')
    save(name, int(width), int(height), body, bg, name)


lockup_h("ics-lockup-horizontal", bg="#FFFFFF")
lockup_h("ics-lockup-horizontal-tagline", bg="#FFFFFF", tagline=True)
lockup_h("ics-lockup-reversed", bg=BLUE, blue=PAPER, word="#FFFFFF", tagline=True)
lockup_h("ics-lockup-mono", bg="#FFFFFF", blue=BLUE, gold=BLUE, word=BLUE)


def lockup_stacked(name, bg=BLUE, blue=PAPER, word="#FFFFFF", sizew=1200, sizeh=1400):
    s = 330
    ox = sizew / 2 - s * (X0 + X1) / 2
    oy = 150 + s * Y1
    wm, adv = b.wordmark_svg(0, 0, 150, word)
    wx = sizew / 2 - adv / 2
    wy = oy + s * 1.0 + 270
    wm, adv = b.wordmark_svg(wx, wy, 150, word)
    body = b.mark_group(ox, oy, s, blue, GOLD, uid="st") + wm
    body += (f'<text x="{sizew / 2}" y="{wy + 105}" text-anchor="middle" font-family="{FONT}" font-weight="600" '
             f'font-size="40" fill="{word}">{TAGLINE}</text>')
    save(name, sizew, sizeh, body, bg, name)


lockup_stacked("ics-lockup-stacked")

# ---- 5. wordmark alone ----------------------------------------------------------------------------------------------------
wm, adv = b.wordmark_svg(60, 260, 200, BLUE)
save("ics-wordmark", int(adv + 120), 320, wm, "#FFFFFF", "ICS wordmark (stroke-built, all ends round)")

# ---- 6. construction sheet -------------------------------------------------------------------------------------------------
def construction():
    W, H = 1900, 1250
    s = 380
    ox, oy = 560, 600
    guides = [f'<circle cx="{ox}" cy="{oy}" r="{s}" fill="none" stroke="#7A8AA8" stroke-width="2" stroke-dasharray="10 8"/>']
    for r in (1.30, 1.15, 0.70):
        guides.append(f'<circle cx="{ox}" cy="{oy}" r="{s * r:.1f}" fill="none" stroke="#C0C8D8" stroke-width="1.5" '
                      f'stroke-dasharray="4 8"/>')
    guides.append(f'<line x1="{ox - s * 1.5}" y1="{oy}" x2="{ox + s * 1.5}" y2="{oy}" stroke="#C0C8D8" stroke-width="1.5"/>')
    guides.append(f'<line x1="{ox}" y1="{oy - s * 1.5}" x2="{ox}" y2="{oy + s * 1.5}" stroke="#C0C8D8" stroke-width="1.5"/>')
    P = b.ARC
    import math
    for label, th, rr, dx, dy in (("tail  216° · r 1.30", P["th0"], P["r0"], -30, 36),
                                  ("rest  −100° · r 0.70", P["th1"], P["r1"], 20, 140)):
        x = ox + s * rr * math.cos(math.radians(th))
        y = oy - s * rr * math.sin(math.radians(th))
        guides.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#D1342B"/>')
        guides.append(f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" font-family="{FONT}" font-size="22" fill="#D1342B">{label}</text>')
    notes = [
        "ICS EARTH BRANCH MARK — CONSTRUCTION [PROPOSAL]",
        "",
        "Unit = circle radius (R). Circle: Deep Blue #1A2E52.",
        "Arc: Warm Gold #C9A84C, one stroke, round ends, no sharp angles.",
        f"Arc path: clockwise spiral, 216° → −100° (316° of sweep),",
        "radius 1.30 R → 0.70 R, so it starts outside the circle and",
        "comes to rest inside it, at the base. It never leaves again.",
        f"Width: {P['w0']:.3f} R at the tail, {P['wm']:.3f} R at the crown (t = {P['tm']:.2f}), {P['w1']:.3f} R at rest.",
        f"Knock-out: a {b.GAP:.3f} R gap is cut from the circle around the arc,",
        "so the gold never touches the blue (a hook through the world,",
        "not a ring painted on it).",
        "",
        "Small-size variant (under 32 px / 8 mm; floor 16 px / 5 mm):",
        "heavier arc, wider gap.",
        "",
        "Entry is visible: the tail, outside, lower left.",
        "Exit is not represented: there is no second arc.",
    ]
    t = "".join(f'<text x="1110" y="{150 + i * 36}" font-family="{FONT}" font-size="{24 if i == 0 else 21}" '
                f'font-weight="{800 if i == 0 else 500}" fill="{BLUE}">{ln}</text>' for i, ln in enumerate(notes))
    body = "".join(guides[:1]) + b.mark_group(ox, oy, s, BLUE, GOLD, uid="c") + "".join(guides[1:]) + t
    save("ics-mark-construction", W, H, body, "#FFFFFF", "Construction", png_w=1900)


construction()

# ---- 7. clear space and minimum sizes ---------------------------------------------------------------------------------------
def clearspace():
    W, H = 1800, 900
    s = 250
    ox = 330 + s * (-X0) - 330
    ox, oy = 540, 470
    cs = s * 0.5      # clear space = 0.5 R on all sides of the mark's bounding box
    bx0, bx1 = ox + s * X0, ox + s * X1
    by0, by1 = oy - s * Y1, oy - s * Y0
    body = (f'<rect x="{bx0 - cs:.1f}" y="{by0 - cs:.1f}" width="{bx1 - bx0 + 2 * cs:.1f}" height="{by1 - by0 + 2 * cs:.1f}" '
            f'fill="none" stroke="#D1342B" stroke-width="2" stroke-dasharray="8 6"/>'
            f'<rect x="{bx0:.1f}" y="{by0:.1f}" width="{bx1 - bx0:.1f}" height="{by1 - by0:.1f}" fill="none" stroke="#7A8AA8" stroke-width="1.5"/>'
            + b.mark_group(ox, oy, s, BLUE, GOLD, uid="cl"))
    body += (f'<text x="{bx0 - cs:.0f}" y="{by0 - cs - 20:.0f}" font-family="{FONT}" font-size="22" fill="#D1342B">'
             f'clear space = 0.5 R on every side</text>')
    x = 1000
    body += f'<text x="{x}" y="120" font-family="{FONT}" font-weight="800" font-size="26" fill="{BLUE}">MINIMUM SIZES  [PROPOSAL]</text>'
    for i, (px, lab, small) in enumerate(((96, "96 px  · full mark", False), (48, "48 px  · full mark", False),
                                          (24, "24 px  · optical-small variant", True),
                                          (16, "16 px  · optical-small variant (floor)", True))):
        sc = px / MW
        yy = 220 + i * 150
        body += b.mark_group(x + 60 + sc * (-X0), yy + sc * Y1 - px / 2, sc, BLUE, GOLD, small=small, uid=f"ms{i}")
        body += f'<text x="{x + 200}" y="{yy + 10}" font-family="{FONT}" font-size="22" fill="{BLUE}">{lab}</text>'
    save("ics-mark-clearspace", W, H, body, "#FFFFFF", "Clear space and minimum sizes", png_w=1800)


clearspace()

# ---- 8. context sheet: every treatment on one page -----------------------------------------------------------------------------
def sheet():
    W, H = 2000, 1500
    body = ""
    cells = [("ics-mark", "#FFFFFF", BLUE, GOLD), ("ics-mark-reversed", BLUE, PAPER, GOLD),
             ("trailer", "#0B1426", "#FFFFFF", GOLD), ("mono blue", "#FFFFFF", BLUE, BLUE),
             ("mono white", BLUE, "#FFFFFF", "#FFFFFF"), ("mono black", "#E9E6DE", "#111111", "#111111")]
    for i, (lab, bg, bl, go) in enumerate(cells):
        cx, cy = 80 + (i % 3) * 620, 80 + (i // 3) * 520
        body += f'<rect x="{cx}" y="{cy}" width="580" height="480" rx="26" fill="{bg}" stroke="#C0C8D8"/>'
        s = 150
        body += b.mark_group(cx + 290 + s * 0.15, cy + 220 - s * 0.15, s, bl, go, uid=f"sh{i}")
        col = "#FFFFFF" if bg in (BLUE, "#0B1426") else BLUE
        body += f'<text x="{cx + 290}" y="{cy + 450}" text-anchor="middle" font-family="{FONT}" font-size="22" fill="{col}">{lab}</text>'
    # small sizes strip
    for j, px in enumerate((16, 24, 32, 48, 64, 96, 128)):
        sc = px / MW
        body += b.mark_group(120 + j * 170 + sc * (-X0), 1190 + sc * Y1, sc, BLUE, GOLD, small=px <= 24, uid=f"sz{j}")
    body += f'<text x="80" y="1130" font-family="{FONT}" font-size="22" font-weight="800" fill="{BLUE}">small sizes</text>'
    save("ics-brand-sheet", W, H, body, "#FFFFFF", "Brand sheet", png_w=2000)


sheet()

# ---- 9. [PROPOSAL] the seal: the canon mark inside a text ring, for badges, wall plates and the boot screen --------------
# Canon mark unchanged. Added around it: "ICS · EARTH BRANCH" on the top band, "LABOR SOURCE #349" (Doc 2.01) on the
# bottom band, a gold hairline and a paper hairline. Reversed colours (paper disc, gold arc) because the seal sits on Deep Blue.
# Layout (radii, font sizes, per-letter positions) lives in src/ics_seal.py, shared with the 3D builds.
def ring_text(letters, fs, color, weight=800):
    """SVG <text> per letter from ics_seal.ring_letters(); letters are placed one by one because librsvg ignores <textPath>."""
    return "".join(f'<text transform="translate({x:.2f},{y:.2f}) rotate({rot:.2f})" text-anchor="middle" '
                   f'font-family="{FONT}" font-weight="{weight}" font-size="{fs:.1f}" fill="{color}">{ch}</text>'
                   for ch, x, y, rot in letters)


def seal_body(size, mark_fill, mark_gold, ring, band, field, uid):
    """Seal: field disc, double ring, text on two arcs, the canon mark in the middle."""
    L = sl.seal_layout(size)
    c = L["c"]
    return (
        f'<circle cx="{c}" cy="{c}" r="{L["R"]:.2f}" fill="{field}"/>'
        f'<circle cx="{c}" cy="{c}" r="{L["ring_r"]:.2f}" fill="none" stroke="{ring}" stroke-width="{L["ring_w"]:.2f}"/>'
        f'<circle cx="{c}" cy="{c}" r="{L["hair_in_r"]:.2f}" fill="none" stroke="{ring}" stroke-width="{L["hair_w"]:.2f}"/>'
        f'<circle cx="{c}" cy="{c}" r="{L["hair_out_r"]:.2f}" fill="none" stroke="{ring}" stroke-width="{L["hair_w"]:.2f}"/>'
        + ring_text(L["top"], L["fs"], band)
        + ring_text(L["bottom"], L["fs_bot"], band)
        + b.mark_group(c, c, L["mark_r"], mark_fill, mark_gold, uid=uid + "m")
    )


# ---- 10. [PROPOSAL] the full emblem: seal + 300 cycle ticks + dates + tagline ribbon -----------------------------------
# Everything added is drawn from canon facts: 300 ticks = Cycle 300 (v9.1 guidelines are issued in Cycle 300); the Earth
# Branch opened in Cycle 290 (story/STORY.md); tagline from Doc 2.32; "LABOR SOURCE #349" from Doc 2.01. Rounded ends only.
def emblem_body(W, H, field, ink, gold, paper, mark_fill, uid, metal=False):
    L = sl.emblem_layout(W)
    c = cy = L["c"]
    parts = [f'<circle cx="{c}" cy="{cy}" r="{L["R"]:.1f}" fill="{field}"/>']
    # 300 ticks, a long one every 25 (twelve "months"), a gold one at the top (the present cycle)
    for t in L["ticks"]:
        a = math.radians(t["ang"])
        col = gold if t["kind"] == "zero" else ink
        parts.append(f'<line x1="{c + t["r0"] * math.sin(a):.2f}" y1="{cy - t["r0"] * math.cos(a):.2f}" x2="{c + t["r1"] * math.sin(a):.2f}" '
                     f'y2="{cy - t["r1"] * math.cos(a):.2f}" stroke="{col}" stroke-width="{t["w"]:.2f}" stroke-linecap="round"/>')
    parts.append(f'<circle cx="{c}" cy="{cy}" r="{L["ring_outer_r"]:.1f}" fill="none" stroke="{ink}" stroke-width="{L["ring_w"]:.2f}"/>')
    parts.append(f'<circle cx="{c}" cy="{cy}" r="{L["ring_inner_r"]:.1f}" fill="none" stroke="{ink}" stroke-width="{L["ring_w"]:.2f}"/>')
    parts.append(ring_text(L["top"], L["fs"], ink))
    parts.append(ring_text(L["bottom"], L["fs_bot"], ink))
    # two small round studs on the horizontal axis, between the text arcs
    for sx, sy in L["studs"]:
        parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{L["stud_r"]:.1f}" fill="{gold}"/>')
    parts.append(b.mark_group(c, cy, L["mark_r"], mark_fill, gold, uid=uid + "m"))
    # ribbon with the tagline: rounded ends, notched tails are replaced by round tabs (no sharp angles)
    rb, ds = L["ribbon"], L["dates"]
    rx, ry, rw, rh, ins = rb["x"], rb["y"], rb["w"], rb["h"], rb["inset"]
    parts.append(f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}" rx="{rh / 2:.1f}" fill="{gold}"/>')
    parts.append(f'<rect x="{rx + ins:.1f}" y="{ry + ins:.1f}" width="{rw - 2 * ins:.1f}" height="{rh - 2 * ins:.1f}" '
                 f'rx="{(rh - 2 * ins) / 2:.1f}" fill="none" stroke="{field}" stroke-width="{rb["line_w"]:.2f}"/>')
    parts.append(f'<text x="{c}" y="{rb["text_y"]:.1f}" text-anchor="middle" font-family="{FONT}" font-weight="800" '
                 f'font-size="{rb["text_size"]:.1f}" fill="{BLUE}" letter-spacing="{rb["tracking"]:.2f}">{sl.TAGLINE_CAPS}</text>')
    parts.append(f'<text x="{c}" y="{ds["y"]:.1f}" text-anchor="middle" font-family="{FONT}" font-weight="700" '
                 f'font-size="{ds["size"]:.1f}" fill="{ink}" letter-spacing="{ds["tracking"]:.2f}">{sl.DATES}</text>')
    return "".join(parts)


def emblem(name, field, ink, gold, paper, mark_fill, bg=None, metal=False):
    W, H = 1100, 1210
    body = emblem_body(W, H, field, ink, gold, paper, mark_fill, "em")
    save(name, W, H, body, bg, name)


emblem("ics-emblem", BLUE, PAPER, GOLD, PAPER, PAPER)
emblem("ics-emblem-paper", PAPER, BLUE, GOLD, PAPER, BLUE, bg=None)


def seal(name, size=1024, metal=False):
    if metal:
        # [PROPOSAL] brushed-metal plate: dark engraved mark and lettering, like the Level 1 wall piece
        grad = ('<defs><linearGradient id="stl" x1="0" y1="0" x2="1" y2="1">'
                '<stop offset="0" stop-color="#E9ECEF"/><stop offset="0.45" stop-color="#8E969E"/>'
                '<stop offset="0.55" stop-color="#C9CFD5"/><stop offset="1" stop-color="#5E656C"/></linearGradient></defs>')
        save(name, size, size, grad + seal_body(size, "#2B3036", "#2B3036", "#2B3036", "#2B3036", "url(#stl)", "sm"),
             None, name)
        return
    # reversed for Deep Blue fields: paper disc, gold arc, Deep Blue ground carries the lettering in paper
    save(name, size, size, seal_body(size, PAPER, GOLD, PAPER, PAPER, BLUE, "sl"), None, name)


seal("ics-seal", 1024)
seal("ics-seal-metal", 1024, metal=True)
print("brand kit written to", HERE)
