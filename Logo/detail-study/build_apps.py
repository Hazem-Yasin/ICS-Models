"""
Application pieces for the ICS Earth Branch seal.  [PROPOSAL] -- nothing here is canon.  Stdlib plus ffmpeg (librsvg) only.

    python3 -B Logo/detail-study/build_apps.py            # everything
    python3 -B Logo/detail-study/build_apps.py plaque     # plaque_steel + plaque_two_tone
    python3 -B Logo/detail-study/build_apps.py header folder keychain

Every object below is one the canon names.  Canon draws none of them, so all the artwork is [PROPOSAL]: what the "ICS seal"
shows (canon never says), every finish, the wall colour, the dimension line drawn on the plaque (the "approximately 2 meters"
itself is Level 1.md:51) and the synthetic slant on two folder-cover lines (the font has no italic).
    plaque     Level 1 arrival hall, south wall behind the welcome desk: "the ouroboros with the serpent removed, rendered in
               brushed metal, approximately 2 meters across"  (canon/facility/Level 1.md:51)
    header     Tier 3 badge, top 16 mm.  Canon: deep blue card, gold text, "ICS EARTH BRANCH", a small circular recess near the
               top-right corner (Doc 2.33:51-53; 2.46:30, 54).  [PROPOSAL]: the mark on the card, the 9 mm band, the 8 mm
               recess and its tone (almost the card's own).  design/BADGES_AND_UNIFORMS.md:48,50 tag the band "[CANON, Doc 2.32]" and the recess
               "[CANON]", but Doc 2.32 has no badge text and canon gives no such sizes (see README, audit finding brand-3).
    folder     Doc 2.33: thick card stock, ICS Deep Blue, gold seal embossed; cover text.  Carries the v2 gold seal, no tagline
    keychain   Doc 2.33 item 6: small metal disc, seal one side, smooth other side engraved, two rings.  Front: the v2 paper seal

Writes ONLY into Logo/detail-study/out/.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import build_study as BS  # noqa: E402  (sets up sys.path for the tools and src folders)
import ics_brand as B     # noqa: E402
import ics_finish as F    # noqa: E402
import seal_art as S      # noqa: E402
import seal_v2 as V       # noqa: E402

n = F.n
FONT = BS.FONT
write = BS.write


def text(s, cap_px, x, y, tracking_em=0.0, anchor="start"):
    """Outlined text with a given capital height.  Returns (path d, width px)."""
    size = S.size_for_cap(FONT, cap_px)
    return FONT.text_path(s, size, x, y, tracking_em * size, anchor)


# =============================================================================================================== wall plaque
def wall(u, W_, H_, reg):
    """A calm warm wall lit by a soft ceiling panel (no visible source).  The wall colour is not in canon: [PROPOSAL]."""
    d = [F.lin(u, "wall", 0, 0, 0, H_, [(0, "#F3ECDD"), (0.5, "#E6DCC7"), (1, "#CDBFA3")]),
         F.rad(u, "glow", W_ * 0.5, H_ * 0.12, W_ * 0.78, [(0, "#FFF8E6", 0.80), (1, "#FFF8E6", 0.0)]),
         F.rad(u, "vig", W_ * 0.5, H_ * 0.5, W_ * 0.82, [(0.55, "#3B2C14", 0.0), (1, "#3B2C14", 0.26)]),
         F.f_grain(u, "grain", reg, freq=0.9, octaves=2, seed=5, k=1.6)]
    b = (f'<rect width="{W_}" height="{H_}" fill="url(#{u}-wall)"/>'
         f'<rect width="{W_}" height="{H_}" fill="url(#{u}-glow)"/>'
         f'<rect width="{W_}" height="{H_}" filter="url(#{u}-grain)" opacity="0.05"/>'
         f'<rect width="{W_}" height="{H_}" fill="url(#{u}-vig)"/>')
    return "".join(d), b


def plaque(tone):
    """tone = 'steel' (one brushed metal, the literal reading of canon) | 'two' (Deep Blue disc, Warm Gold arc)."""
    W_, H_ = 1600, 1000
    u = "wp" + tone[0]
    reg = (0, 0, W_, H_)
    ppm = 380.0                                           # px per metre
    xmin, xmax, ymin, ymax = B.mark_bbox(False)
    RC = 2.0 / (xmax - xmin) * ppm                        # overall mark width = 2.0 m
    cx = W_ / 2 - RC * (xmin + xmax) / 2
    cy = 450 + RC * (ymin + ymax) / 2
    poly, gap = S.mark_geometry(cx, cy, RC)
    wd, wb = wall(u, W_, H_, reg)
    D = [wd]
    if tone == "steel":
        disc_st = [(0, "#E6E9EC"), (0.40, "#BDC3C9"), (0.64, "#D3D7DC"), (1, "#A0A7AF")]
        arc_st = [(0, "#EEF0F2"), (0.35, "#C7CCD2"), (0.62, "#DDE0E4"), (1, "#A9B0B8")]
        wh_d, bk_d, wh_a, bk_a = 0.34, 0.20, 0.38, 0.20
    else:
        disc_st = [(0, "#2E4A7C"), (0.5, F.BLUE), (1, "#12223F")]
        arc_st = F.GOLD_STOPS
        wh_d, bk_d, wh_a, bk_a = 0.14, 0.30, 0.34, 0.22
    D.append(F.lin(u, "discg", cx - RC, cy - RC, cx + RC, cy + RC, disc_st))
    D.append(F.lin(u, "arcg", cx - 1.3 * RC, cy - 1.1 * RC, cx + RC, cy + RC, arc_st))
    D.append(S._ko_mask(u, reg, poly, gap))
    D.append(f'<clipPath id="{u}-disc"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(RC)}"/></clipPath>')
    D.append(f'<clipPath id="{u}-arc"><polygon points="{poly}"/></clipPath>')
    # light from the ceiling panel: straight down, so the bevel lights from the top and the shadow falls straight down
    D.append(F.f_raise(u, "plate", reg, blur=2.2, scale=3.2, el=56, az=270, spec=0.22, spec_exp=30, spec_col="#FFFFFF",
                       shadow=(0, 13, 13, 0.36), plateau="0 .6 .95 1 1"))
    D.append(F.f_brushed(u, "bw", reg, fx=0.0035, fy=0.50, seed=3, k=2.4, ink="1 1 1"))
    D.append(F.f_brushed(u, "bk", reg, fx=0.0035, fy=0.50, seed=11, k=2.4, ink="0 0 0"))
    D.append(F.lin(u, "sheen", cx - 1.4 * RC, cy - 0.9 * RC, cx + 1.1 * RC, cy + 0.6 * RC,
                   [(0, "#fff", 0.0), (0.42, "#fff", 0.0), (0.55, "#fff", 0.26), (0.68, "#fff", 0.0), (1, "#fff", 0.0)]))

    def brush(wh, bk):
        return (f'<rect width="{W_}" height="{H_}" filter="url(#{u}-bw)" opacity="{wh}"/>'
                f'<rect width="{W_}" height="{H_}" filter="url(#{u}-bk)" opacity="{bk}"/>'
                f'<rect width="{W_}" height="{H_}" fill="url(#{u}-sheen)"/>')

    body = [wb]
    body.append(f'<g filter="url(#{u}-plate)"><g mask="url(#{u}-ko)">'
                f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(RC)}" fill="url(#{u}-discg)"/>'
                f'<g clip-path="url(#{u}-disc)">{brush(wh_d, bk_d)}</g></g></g>')
    body.append(f'<g filter="url(#{u}-plate)"><polygon points="{poly}" fill="url(#{u}-arcg)"/>'
                f'<g clip-path="url(#{u}-arc)">{brush(wh_a, bk_a)}</g></g>')
    # a dimension line under the mark: the overall width is the 2 m the canon gives
    yl = cy + RC * (-ymin) + 78
    xl, xr = cx + RC * xmin, cx + RC * xmax
    ink = "#7B6B4C"
    body.append(f'<g stroke="{ink}" stroke-width="1.6" fill="none" stroke-opacity="0.8">'
                f'<line x1="{n(xl)}" y1="{n(yl)}" x2="{n(xr)}" y2="{n(yl)}"/>'
                f'<line x1="{n(xl)}" y1="{n(yl - 9)}" x2="{n(xl)}" y2="{n(yl + 9)}"/>'
                f'<line x1="{n(xr)}" y1="{n(yl - 9)}" x2="{n(xr)}" y2="{n(yl + 9)}"/></g>')
    lab, lw = text("approx. 2 m", 17, (xl + xr) / 2, yl - 14, 0.10, "middle")
    body.append(f'<path d="{lab}" fill="{ink}" fill-opacity="0.85"/>')
    title = ("ICS Earth Branch logo, arrival hall south wall, one brushed metal [PROPOSAL finish]" if tone == "steel" else
             "ICS Earth Branch logo, arrival hall south wall, Deep Blue and Warm Gold brushed metal [PROPOSAL finish]")
    return F.doc(W_, H_, "".join(body), "".join(D), title=title), 1400


# ============================================================================================================== badge header
def badge_header():
    """Top 16 mm of the Tier 3 card at 14 px per mm: the 9 mm header band, the recess (8 mm, top right, almost the card's own
    colour) and 7 mm of card below.  [PROPOSAL] the band, both sizes, the recess tone and the mark's place on the card.
    Canon: Tier 3 = deep blue with gold lettering (Doc 2.33:51, 2.46:54); "ICS EARTH BRANCH" printed on it (2.33:53); a
    circular recess near the top-right corner (2.33:51, 2.46:30)."""
    px = 14.0
    W_, H_ = round(85.6 * px), round(16.0 * px)
    u = "bh"
    reg = (0, 0, W_, H_)
    band = 9.0 * px
    r3 = 3.0 * px
    RC = 3.0 * px
    xmin, xmax, ymin, ymax = B.mark_bbox(True)
    ox = 3.5 * px - xmin * RC
    oy = band / 2 + RC * (ymin + ymax) / 2
    d, b = S.flat_mark(u, ox, oy, RC, reg, disc=F.PAPER, arc=F.GOLD, small=True)
    cap = 2.5 * px
    x_text = ox + xmax * RC + 3.0 * px
    wm, ww = text("ICS EARTH BRANCH", cap, x_text, band / 2 + cap / 2, 0.14)
    rc_x, rc_y, rc_r = W_ - 3.5 * px - 4.0 * px, band / 2, 4.0 * px
    defs = [d,
            F.lin(u, "card", 0, 0, W_, H_, [(0, "#223966"), (0.6, F.BLUE), (1, "#162847")]),
            F.f_inner(u, "rec", reg, blur=2.6, dx=0, dy=2.6, op=0.45, col="#050B18")]
    outline = f'M0,{H_}L0,{r3}Q0,0 {r3},0L{W_ - r3},0Q{W_},0 {W_},{r3}L{W_},{H_}Z'
    body = [f'<path d="{outline}" fill="url(#{u}-card)"/>',
            f'<path d="{outline}" fill="none" stroke="#6F86B4" stroke-opacity="0.45" stroke-width="1.4"/>',
            f'<line x1="{n(r3)}" y1="{n(band)}" x2="{n(W_ - r3)}" y2="{n(band)}" stroke="{F.GOLD}" stroke-opacity="0.55" stroke-width="2"/>',
            b, f'<path d="{wm}" fill="{F.GOLD}"/>',
            f'<g filter="url(#{u}-rec)"><circle cx="{n(rc_x)}" cy="{n(rc_y)}" r="{n(rc_r)}" fill="#16294B"/></g>',
            f'<circle cx="{n(rc_x)}" cy="{n(rc_y)}" r="{n(rc_r)}" fill="none" stroke="#7F96C4" stroke-opacity="0.28" stroke-width="1.2"/>']
    return F.doc(W_, H_, "".join(body), "".join(defs), title="ICS Tier 3 card, top 16 mm [PROPOSAL placement]"), W_


# ========================================================================================================== folder cover
def folder_cover():
    W_, H_ = 1300, 1650
    u = "fc"
    reg = (0, 0, W_, H_)
    x0, y0, fw, fh = 150, 140, 1000, 1370
    rr = 18
    cxs = x0 + fw / 2
    R = 285.0
    cys = y0 + 180 + R
    D, Bd = [], []
    D.append(F.lin(u, "ground", 0, 0, 0, H_, [(0, "#EDE7DA"), (1, "#D9D0BD")]))
    D.append(F.rad(u, "card", x0 + 0.3 * fw, y0 + 0.2 * fh, 1.25 * fh, [(0, "#27457A"), (0.55, F.BLUE), (1, "#12223F")]))
    D.append(F.lin(u, "crease", x0 + 56, 0, x0 + 112, 0,
                   [(0, "#000", 0.0), (0.30, "#000", 0.30), (0.46, "#fff", 0.10), (0.58, "#000", 0.16), (1, "#000", 0.0)]))
    D.append(F.lin(u, "foil", 0, y0 + 880, 0, y0 + 1010, F.GOLD_STOPS))
    D.append(F.f_raise(u, "stock", reg, blur=3.0, scale=4.0, el=52, az=225, spec=0.0, shadow=(12, 22, 26, 0.34),
                       plateau="0 .5 .9 1 1"))
    D.append(F.f_raise(u, "tfoil", reg, blur=1.5, scale=2.6, el=50, az=225, spec=0.15, spec_exp=40, spec_col="#FFF6D6",
                       shadow=(2, 3.5, 2.5, 0.50), plateau="0 .6 .95 1 1"))
    D.append(F.f_grain(u, "wv1", reg, freq="0.95 0.035", octaves=2, seed=4, k=1.8, ink="1 1 1"))
    D.append(F.f_grain(u, "wv2", reg, freq="0.035 0.95", octaves=2, seed=9, k=1.8, ink="0 0 0"))
    D.append(f'<clipPath id="{u}-cardclip"><rect x="{x0}" y="{y0}" width="{fw}" height="{fh}" rx="{rr}"/></clipPath>')
    Bd.append(f'<rect width="{W_}" height="{H_}" fill="url(#{u}-ground)"/>')
    Bd.append(f'<g filter="url(#{u}-stock)"><rect x="{x0}" y="{y0}" width="{fw}" height="{fh}" rx="{rr}" fill="url(#{u}-card)"/>'
              f'<g clip-path="url(#{u}-cardclip)">'
              f'<rect x="{x0}" y="{y0}" width="{fw}" height="{fh}" filter="url(#{u}-wv1)" opacity="0.07"/>'
              f'<rect x="{x0}" y="{y0}" width="{fw}" height="{fh}" filter="url(#{u}-wv2)" opacity="0.10"/>'
              f'<rect x="{x0}" y="{y0}" width="{fw}" height="{fh}" fill="url(#{u}-crease)"/></g></g>')
    sd, sb, info = V.seal2(u + "s", cxs, cys, R, theme="gold", region=reg)
    D.append(sd)
    Bd.append(sb)

    def line(s, cap, y, track, bold=0.0, slant=0.0, fill=None, op=1.0):
        d_, w_ = text(s, cap, cxs, y, track, "middle")
        size = S.size_for_cap(FONT, cap)
        sw = f' stroke="url(#{u}-foil)" stroke-width="{n(bold * size)}" stroke-linejoin="round"' if bold else ""
        tf = f' transform="translate({n(cxs)} {n(y)}) skewX({slant}) translate({n(-cxs)} {n(-y)})"' if slant else ""
        return f'<g{tf}><path d="{d_}" fill="url(#{u}-foil)"{sw} fill-opacity="{op}"/></g>'

    ty = y0 + 930
    Bd.append(f'<g filter="url(#{u}-tfoil)">'
              + line("Welcome to ICS.", 64, ty, 0.01, bold=0.045)
              + line("Your future starts here.", 36, ty + 92, 0.02, slant=-10)
              + line("— ICS Earth Branch, People & Culture Division", 17, y0 + fh - 96, 0.07, slant=-10, op=0.9)
              + '</g>')
    return F.doc(W_, H_, "".join(Bd), "".join(D), title="ICS onboarding folder cover, gold seal embossed [PROPOSAL finish]"), 1000, info


# ============================================================================================================== keychain
def ring_wire(u, cx, cy, r, w):
    """A plain closed ring of wire seen from the front (no split drawn): dark under-stroke, steel body, thin highlight."""
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="none" stroke="#5E656E" stroke-width="{n(w + 4)}"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="none" stroke="url(#{u}-steel)" stroke-width="{n(w)}"/>'
            f'<circle cx="{n(cx - 1.5)}" cy="{n(cy - 2)}" r="{n(r)}" fill="none" stroke="#fff" stroke-opacity="0.55" '
            f'stroke-width="{n(w * 0.22)}"/>')


def ear_fillets(x, y, R, ear_up, ear_r, rf=30.0, steps=22):
    """Pendant ear on a round coin.  Two concave fillet webs (one each side) that blend the ear circle into the coin circle,
    so the silhouette has no sharp inner corners (rounded-object rule).  Returns one path d (fill both webs)."""
    ex, ey = x, y - ear_up
    a, b = ear_r + rf, R + rf
    t = (ear_up * ear_up + b * b - a * a) / (2 * ear_up)
    h = math.sqrt(b * b - t * t)
    out = []
    for sgn in (-1.0, 1.0):
        fx_, fy_ = x + sgn * h, y - t
        t1 = (ex + ear_r * (fx_ - ex) / a, ey + ear_r * (fy_ - ey) / a)
        t2 = (x + R * (fx_ - x) / b, y + R * (fy_ - y) / b)
        a1 = math.atan2(t1[1] - fy_, t1[0] - fx_)
        a2 = math.atan2(t2[1] - fy_, t2[0] - fx_)
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi            # shorter way round
        pts = [(fx_ + rf * math.cos(a1 + da * k / steps), fy_ + rf * math.sin(a1 + da * k / steps)) for k in range(steps + 1)]
        pts += [(x, y - 0.9 * R), (ex, ey + 0.95 * ear_r)]
        out.append("M" + " L".join(f"{n(px)},{n(py)}" for px, py in pts) + "Z")
    return "".join(out)


def keychain():
    W_, H_ = 1700, 1120
    u = "kc"
    reg = (0, 0, W_, H_)
    R = 300.0
    # The v2 seal's rim is a scalloped cog (ics_finish.cog_d): 0.9715 R in the troughs, 0.9985 R on the crests.  The ear's fillet webs
    # are built tangent to the circle through the troughs, so their thin ends finish under the rim; built for a circle of R they
    # showed as two small points outside the scallops.  The back coin gets the same outline, so both faces share one silhouette.
    cog = dict(r0=V.PLAN2["cog_r0"] * R, amp=V.PLAN2["cog_amp"] * R, lobes=V.PLAN2["cog_lobes"])
    R_trough = cog["r0"] - cog["amp"]
    fx, fy = 470.0, 720.0           # front coin centre
    bx, by = 1230.0, 720.0          # back coin centre
    ear_r, hole_r, ear_up = 62.0, 25.0, R + 30.0
    hx, hy = fx, fy - ear_up        # hole centre (front)
    D, Bd = [], []
    D.append(F.lin(u, "ground", 0, 0, 0, H_, [(0, "#EDE7DA"), (1, "#D9D0BD")]))
    D.append(F.lin(u, "gold", fx - R, fy - R - 90, fx + R, fy + R, F.GOLD_STOPS))
    D.append(F.lin(u, "steel", 0, 0, W_, H_, F.STEEL_STOPS))
    D.append(F.rad(u, "back", bx - 0.3 * R, by - 0.4 * R, 1.5 * R,
                   [(0, "#F1E4AA"), (0.35, "#DABF6A"), (0.7, "#C9A84C"), (1, "#A88830")]))
    D.append(F.f_raise(u, "foil", reg, blur=2.6, scale=3.6, el=48, az=225, spec=0.20, spec_exp=46, spec_col="#FFF6D6",
                       shadow=(5, 11, 10, 0.34), plateau="0 .55 .92 1 1"))
    D.append(F.f_raise(u, "wire", reg, blur=2.4, scale=4.5, el=55, az=235, spec=0.30, spec_exp=36, spec_col="#fff",
                       shadow=(5, 10, 7, 0.32)))

    def ear_d(x, y):
        """The eyelet: a disc with an even-odd hole, centred ear_up above the coin centre."""
        return F.ring_d(x, y - ear_up, ear_r) + F.ring_d(x, y - ear_up, hole_r)

    def coin_d(x, y):
        """The coin outline: the same scalloped cog as the v2 seal's rim (no corner)."""
        return F.cog_d(x, y, cog["r0"], cog["amp"], cog["lobes"], k=1.5, steps=720)

    # --- two key rings (drawn closed, no split shown), both threaded through the hole: (direction in degrees, SVG axes, radius, wire width, which side is in front)
    specs = [(-122.0, 138.0, 17.0, +1), (-58.0, 92.0, 14.0, -1)]
    rings = []
    for deg, r_, w_, side in specs:
        ang = math.radians(deg)
        rings.append((hx + r_ * math.cos(ang), hy + r_ * math.sin(ang), r_, w_, ang, side))
    Bd.append(f'<rect width="{W_}" height="{H_}" fill="url(#{u}-ground)"/>')
    Bd.append(f'<g filter="url(#{u}-wire)">' + "".join(ring_wire(u, a, b, r_, w_) for a, b, r_, w_, _g, _s in rings) + '</g>')
    # --- front coin: ear + fillet webs in gold, then the seal over it
    Bd.append(f'<g filter="url(#{u}-foil)"><path d="{ear_d(fx, fy)}" fill="url(#{u}-gold)" fill-rule="evenodd"/>'
              f'<path d="{ear_fillets(fx, fy, R_trough, ear_up, ear_r)}" fill="url(#{u}-gold)"/></g>')
    sd, sb, info = V.seal2(u + "f", fx, fy, R, theme="paper", region=reg)
    D.append(sd)
    Bd.append(sb)
    # --- inside the hole: the rings again, clipped to the hole, so the eyelet's drop shadow does not haze the wire seen through it
    D.append(f'<clipPath id="{u}-hole"><circle cx="{n(hx)}" cy="{n(hy)}" r="{n(hole_r)}"/></clipPath>')
    Bd.append(f'<g clip-path="url(#{u}-hole)"><g filter="url(#{u}-wire)">'
              + "".join(ring_wire(u, a, b, r_, w_) for a, b, r_, w_, _g, _s in rings) + '</g></g>')
    # --- over-under: one side of each ring crosses in FRONT of the ear (clip = a half-plane through the hole centre, limited to the
    #     ear and with the hole itself left out, so the wire runs into the hole's rim and is seen continuing through it from the layer below)
    L = 420.0
    for k_, (a, b, r_, w_, ang, side) in enumerate(rings):
        dx_, dy_ = math.cos(ang), math.sin(ang)
        nx_, ny_ = -dy_ * side, dx_ * side
        poly = [(hx - L * dx_, hy - L * dy_), (hx + L * dx_, hy + L * dy_),
                (hx + L * dx_ + L * nx_, hy + L * dy_ + L * ny_), (hx - L * dx_ + L * nx_, hy - L * dy_ + L * ny_)]
        pts = " ".join(f"{n(px)},{n(py)}" for px, py in poly)
        D.append(f'<clipPath id="{u}-half{k_}"><polygon points="{pts}"/></clipPath>')
        D.append(f'<clipPath id="{u}-ear{k_}"><path d="{F.ring_d(hx, hy, ear_r + 6)}{F.ring_d(hx, hy, hole_r)}" clip-rule="evenodd"/></clipPath>')
        Bd.append(f'<g clip-path="url(#{u}-half{k_})"><g clip-path="url(#{u}-ear{k_})"><g filter="url(#{u}-wire)">'
                  + ring_wire(u, a, b, r_, w_) + '</g></g></g>')
    # --- back coin: same silhouette, smooth spun finish, one engraved line
    Bd.append(f'<g filter="url(#{u}-foil)"><path d="{ear_d(bx, by)}" fill="url(#{u}-back)" fill-rule="evenodd"/>'
              f'<path d="{ear_fillets(bx, by, R_trough, ear_up, ear_r)}" fill="url(#{u}-back)"/>'
              f'<path d="{coin_d(bx, by)}" fill="url(#{u}-back)"/></g>')
    D.append(f'<clipPath id="{u}-bdisc"><path d="{coin_d(bx, by)}"/></clipPath>')
    Bd.append(f'<g clip-path="url(#{u}-bdisc)">{F.sunburst(bx, by, R * 1.02, count=360, theta0=-40, peak=0.26, power=2.0)}</g>')
    line = "Your future is our investment."
    cap = 17.0
    size = S.size_for_cap(FONT, cap)
    lw = FONT.text_width(line, size, 0.05 * size)
    d_, _w = text(line, cap, bx, by + cap / 2, 0.05, "middle")
    Bd.append(f'<g transform="translate({n(0.9)} {n(1.2)})"><path d="{d_}" fill="#FFF1C0" fill-opacity="0.55"/></g>'
              f'<path d="{d_}" fill="#5A4313" fill-opacity="0.88"/>')
    return F.doc(W_, H_, "".join(Bd), "".join(D), title="ICS keychain, seal side and smooth side [PROPOSAL finish]"), 1500, info, lw / (2 * R)


# ===================================================================================================================== main
def main(which):
    todo = set(which) or {"plaque", "header", "folder", "keychain"}
    if "plaque" in todo:
        for tone, name in (("steel", "plaque_steel"), ("two", "plaque_two_tone")):
            svg, w = plaque(tone)
            write(name, svg, w)
    if "header" in todo:
        svg, w = badge_header()
        write("badge_header", svg, w)
    if "folder" in todo:
        svg, w, info = folder_cover()
        write("folder_cover", svg, w)
        print("folder seal", info)
    if "keychain" in todo:
        svg, w, info, frac = keychain()
        write("keychain", svg, w)
        print("keychain seal", info, "engraved line spans", round(frac, 2), "of the coin diameter")


if __name__ == "__main__":
    main(sys.argv[1:])
