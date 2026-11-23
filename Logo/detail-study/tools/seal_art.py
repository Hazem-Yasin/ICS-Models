"""
Detailed-seal art for the ICS Earth Branch mark.  Stdlib only.  [PROPOSAL tooling -- every output is a study, not canon]

    mark_layers(...)  the canon mark alone (disc + arc + knock-out channel) with a chosen finish
    flat_mark(...)    the same geometry with no finish at all (small sizes, one colour, stencil)
    seal(...)         the engraved medallion around the mark: gold rim with a legend, a 349-tick dial, ring lettering,
                      bezel, guilloche field

The circle, the arc and the channel between them are NOT defined here.  They are read from Logo/src/ics_brand.py (the
Models kit's single source), so a change to the mark there flows through every study piece.  Nothing here edits that file.

Why the detail is where it is: canon (Doc 2.32) fixes the circle and the arc and says nothing about what surrounds them.
Every layer added below sits OUTSIDE the mark or is a finish on it.  Nothing is drawn across the disc except shading, and
the only cut in it is the channel around the arc that ics_brand already defines (the PTKW layer reads the circle as "a
complete thing", Doc 2.32:100), so the extra richness never touches the construction.

Every function returns SVG strings; ids are prefixed with `uid`, so several seals can share one document.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.normpath(os.path.join(HERE, "..", ".."))
for _p in (os.path.join(LOGO, "src"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import ics_brand as B      # noqa: E402  (read-only geometry)
import ics_finish as F     # noqa: E402
from ttf_outline import TTF  # noqa: E402

n = F.n
_FONT = None


def font():
    global _FONT
    if _FONT is None:
        _FONT = TTF(os.path.join(LOGO, "fonts", "VarelaRound-Regular.ttf"))
    return _FONT


# ---- the mark -------------------------------------------------------------------------------------------------------------
DISC_STOPS = {
    "blue": [(0, "#2B4778"), (0.5, F.BLUE), (1, "#132446")],
    "cream": [(0, "#FFFDF8"), (0.55, "#F2ECDD"), (1, "#D8CFB8")],
    "gold": F.GOLD_STOPS,
}
# flat-enamel colour of each disc: the middle stop of the shaded version (blue is canon Deep Blue)
FLAT_DISC = {"blue": F.BLUE, "cream": "#F2ECDD"}


def mark_geometry(cx, cy, RC, small=False):
    """(polygon points of the arc, knock-out margin in px: the clear band left on each side of the gold) for a mark whose circle has radius RC and centre (cx, cy).
    small=True selects the optical small-size cut (ARC_SMALL, GAP_SMALL) used under ~8 mm / ~32 px."""
    p, g = (B.ARC_SMALL, B.GAP_SMALL) if small else (B.ARC, B.GAP)
    return B._pts(B.arc_outline(p), cx, cy, RC), g * RC


def _ko_mask(uid, region, poly, gap):
    x0, y0, rw, rh = region
    return (f'<mask id="{uid}-ko" maskUnits="userSpaceOnUse" x="{n(x0)}" y="{n(y0)}" width="{n(rw)}" height="{n(rh)}">'
            f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(rw)}" height="{n(rh)}" fill="#fff"/>'
            f'<polygon points="{poly}" fill="#000" stroke="#000" stroke-width="{2 * gap:.2f}" stroke-linejoin="round"/></mask>')


def flat_mark(uid, cx, cy, RC, region, disc="#1A2E52", arc="#C9A84C", small=False):
    """The mark with no finish: (defs, body).  `small=True` uses the optical small-size cut from ics_brand."""
    poly, gap = mark_geometry(cx, cy, RC, small)
    d = _ko_mask(uid, region, poly, gap)
    b = (f'<g mask="url(#{uid}-ko)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(RC)}" fill="{disc}"/></g>'
         f'<polygon points="{poly}" fill="{arc}"/>')
    return d, b


def mark_layers(uid, cx, cy, RC, region, disc="blue", ground_dark=False, gloss=True, flat=False):
    """The finished mark: enamel (or foil) disc with the channel cut out, plus a raised gold-foil arc with a bevelled edge,
    a faint spun-metal sheen and a hairline edge.  Returns (defs, body).  `disc` is blue | cream | gold.
    Default disc = domed enamel (radial shading, inner shadow, spherical highlight).  `flat=True` = flat enamel: one even
    field of the disc colour with no shading, highlight or shadow (blue and cream only; the gold foil disc is unchanged)."""
    k = RC / 233.0
    poly, gap = mark_geometry(cx, cy, RC)
    d, b = [], []
    d.append(F.rad(uid, "enamel", cx - 0.30 * RC, cy - 0.40 * RC, 1.45 * RC, DISC_STOPS[disc]))
    d.append(F.lin(uid, "agold", cx - 1.25 * RC, cy - 1.15 * RC, cx + 1.0 * RC, cy + 0.95 * RC, F.GOLD_STOPS))
    d.append(_ko_mask(uid, region, poly, gap))
    d.append(f'<clipPath id="{uid}-disc"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(RC)}"/></clipPath>')
    d.append(f'<clipPath id="{uid}-arc"><polygon points="{poly}"/></clipPath>')
    d.append(F.f_blur(uid, "bl", region, 20 * k))
    sh = 0.55 if ground_dark else 0.30
    if disc == "gold":
        d.append(F.f_raise(uid, "dfoil", region, blur=2.6 * k, scale=3.6 * k, el=48, az=225, spec=0.22, spec_exp=46,
                           spec_col="#FFF6D6", shadow=(3 * k, 6 * k, 5 * k, 0.34), plateau="0 .55 .92 1 1"))
        dome = "dfoil"
    else:
        ic = "#040A18" if disc == "blue" else "#5A4E34"
        d.append(F.f_inner(uid, "dome", region, blur=8 * k, dx=-3 * k, dy=-5 * k, op=0.55 if disc == "blue" else 0.34,
                           col=ic, shadow=(5 * k, 10 * k, 10 * k, sh)))
        dome = "dome"
    d.append(F.f_raise(uid, "afoil", region, blur=2.6 * k, scale=3.6 * k, el=48, az=225, spec=0.22, spec_exp=46,
                       spec_col="#FFF6D6", shadow=(3 * k, 6 * k, 5 * k, 0.34 if not ground_dark else 0.55),
                       plateau="0 .55 .92 1 1"))
    inner = f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(RC)}" fill="url(#{uid}-enamel)"/>'
    if gloss and disc == "blue":
        gx, gy = cx - 0.28 * RC, cy - 0.60 * RC
        inner += (f'<g clip-path="url(#{uid}-disc)"><ellipse cx="{n(gx)}" cy="{n(gy)}" rx="{n(0.62 * RC)}" ry="{n(0.30 * RC)}" '
                  f'fill="#fff" fill-opacity="0.10" transform="rotate(-26 {n(gx)} {n(gy)})" filter="url(#{uid}-bl)"/></g>')
    if flat and disc != "gold":
        b.append(f'<g mask="url(#{uid}-ko)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(RC)}" fill="{FLAT_DISC[disc]}"/></g>')
    else:
        b.append(f'<g filter="url(#{uid}-{dome})"><g mask="url(#{uid}-ko)">{inner}</g></g>')
    b.append(f'<g filter="url(#{uid}-afoil)"><polygon points="{poly}" fill="url(#{uid}-agold)"/></g>')
    b.append(f'<g clip-path="url(#{uid}-arc)">{F.sunburst(cx, cy, 1.5 * RC, count=240, theta0=-40, peak=0.13, power=2.6)}</g>')
    b.append(f'<polygon points="{poly}" fill="none" stroke="#7A5C1C" stroke-opacity="0.60" stroke-width="{n(1.1 * k)}" '
             f'stroke-linejoin="round"/>')
    return "".join(d), "".join(b)


# ---- the seal -------------------------------------------------------------------------------------------------------------
# Radial plan, in units of the seal radius R (outside in).  One table so every study piece lays out the same way.
PLAN = dict(
    rim_in=0.945,            # gold rim: R .. rim_in, carries the legend
    legend_cap=0.0235,       # cap height of the legend
    tick_base=0.890,         # dial: ticks stand on this circle and reach outward
    tick_minor=0.914,
    tick_major=0.936,
    hair=0.878,              # hairline under the dial
    text_mid=0.785,          # mid-cap radius of the ring lettering
    top_cap=0.095,
    bot_cap=0.060,
    bezel_out=0.701,         # inner gold bezel
    field=0.675,             # field radius
    rc=0.415,                # mark circle radius
)


def size_for_cap(f, cap_px):
    """Font size (px per em) whose capital height is `cap_px`."""
    return cap_px / f.cap_height(1.0)


def _cyclic_legend(f, text, cx, cy, r_base, size, color_extra):
    """Outlined text repeated so that it closes the circle exactly (seamless legend)."""
    cap = f.cap_height(size)
    rm = r_base + cap / 2
    k = size / f.upm
    base_adv = sum(f.advance_units(c) * k for c in text)
    reps = max(1, int(round(2 * math.pi * rm / (base_adv * 1.18))))
    s = text * reps
    advs = sum(f.advance_units(c) * k for c in s)
    tr = (2 * math.pi * rm - advs) / len(s)
    svg, _ = F.ring_text(f, s, cx, cy, r_base, size, tr / size, 0.0, top=True, extra=color_extra)
    return svg, reps


def seal(uid, cx, cy, R, theme="paper", region=None, legend="INTERPLANETARY CORPORATE SOLUTIONS · ",
         top_txt="ICS · EARTH BRANCH", bot_txt="BECAUSE YOU’RE WORTH THE INVESTMENT", n_ticks=349, plan=None,
         rays=True, rays_n=72, flat=False):
    """Return (defs, body, info) for a seal of radius R centred at (cx, cy).
    theme: paper = navy medallion, cream field, navy-enamel disc (the primary mark's colours)
           night = navy medallion, dark field, cream-enamel disc (the reversed mark)
           gold  = gold foil only, no ground: for stamping or embossing onto an object
    `legend=None` drops the rim legend; `n_ticks=0` drops the dial; `rays=False` drops the faint sunray hatching;
    `flat=True` swaps the domed enamel disc for flat enamel (see mark_layers)."""
    P = dict(PLAN)
    if plan:
        P.update(plan)
    f = font()
    k = R / 556.0
    if region is None:
        m = 0.14 * R
        region = (cx - R - m, cy - R - m, 2 * (R + m), 2 * (R + m))
    reg = region
    base = theme in ("paper", "night")
    cream_field = theme == "paper"
    disc = {"paper": "blue", "night": "cream", "gold": "gold"}[theme]
    ground_dark = theme != "paper"
    D, Bd = [], []

    # gradients
    D.append(F.lin(uid, "gold", cx - R, cy - R, cx + R, cy + R, F.GOLD_STOPS))
    D.append(F.lin(uid, "gold2", cx + R, cy - R, cx - R, cy + R, F.GOLD_STOPS))
    D.append(F.rad(uid, "navy", cx - 0.35 * R, cy - 0.45 * R, 1.5 * R, [(0, "#294676"), (0.5, F.BLUE), (1, "#112043")]))
    if cream_field:
        D.append(F.rad(uid, "field", cx - 0.2 * R, cy - 0.3 * R, 1.0 * R, [(0, "#FBF8F1"), (0.7, "#F1ECDF"), (1, "#E3DBC8")]))
    else:
        D.append(F.rad(uid, "field", cx - 0.2 * R, cy - 0.3 * R, 1.0 * R, [(0, "#16294F"), (0.7, "#0E1C3A"), (1, "#081329")]))
    # filters
    D.append(F.f_inner(uid, "medal", reg, blur=10 * k, dx=-3 * k, dy=-6 * k, op=0.50, col="#040A18",
                       shadow=(8 * k, 16 * k, 16 * k, 0.34 if theme == "paper" else 0.60)))
    D.append(F.f_raise(uid, "foil", reg, blur=2.6 * k, scale=3.6 * k, el=48, az=225, spec=0.20, spec_exp=46,
                       spec_col="#FFF6D6", shadow=(3 * k, 6 * k, 5 * k, 0.30), plateau="0 .55 .92 1 1"))
    D.append(F.f_raise(uid, "tfoil", reg, blur=1.1 * k, scale=2.2 * k, el=50, az=225, spec=0.0,
                       shadow=(1.5 * k, 2.5 * k, 2 * k, 0.45), plateau="0 .6 .95 1 1"))
    D.append(F.f_inner(uid, "recess", reg, blur=9 * k, dx=0, dy=7 * k, op=0.40, col="#000"))

    # medallion base
    if base:
        Bd.append(f'<g filter="url(#{uid}-medal)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(R)}" fill="url(#{uid}-navy)"/></g>')

    # rim
    rim_d = F.annulus_d(cx, cy, R, P["rim_in"] * R)
    D.append(f'<clipPath id="{uid}-rimclip"><path d="{rim_d}" clip-rule="evenodd"/></clipPath>')
    Bd.append(f'<g filter="url(#{uid}-foil)"><path d="{rim_d}" fill="url(#{uid}-gold)" fill-rule="evenodd"/></g>')
    Bd.append(f'<g clip-path="url(#{uid}-rimclip)">{F.sunburst(cx, cy, R * 1.02, count=240, theta0=-40, peak=0.22, power=2.2)}</g>')
    legend_reps = 0
    if legend:
        size_l = size_for_cap(f, P["legend_cap"] * R)
        cap_l = f.cap_height(size_l)
        r_l = (1.0 + P["rim_in"]) / 2 * R - cap_l / 2
        eng, legend_reps = _cyclic_legend(f, legend, cx, cy, r_l, size_l, ' fill="#6E5115" fill-opacity="0.78"')
        hi, _ = _cyclic_legend(f, legend, cx, cy, r_l, size_l, ' fill="#FFF3C4" fill-opacity="0.45"')
        Bd.append(f'<g transform="translate({n(0.7 * k)} {n(0.8 * k)})">{hi}</g>{eng}')

    # dial: one tick per planet in the portfolio (349), a longer tick at each quarter; every tick is the same gold.
    # [PROPOSAL] 349 is the "349-planet portfolio" (Doc 2.29:233) and "349 Labor Sources" (Doc 2.24:96, staff-wide).  No tick
    # is marked as Earth: Doc 2.24:85 calls Earth Labor Source #349, while Doc 2.29:262 says Global documents never use the term.
    if n_ticks:
        quarter = {round(i * n_ticks / 4.0) % n_ticks for i in range(4)}
        d = []
        for i in range(n_ticks):
            a = 360.0 * i / n_ticks
            ro = P["tick_major"] if i in quarter else P["tick_minor"]
            x1, y1 = F.polar(cx, cy, P["tick_base"] * R, a)
            x2, y2 = F.polar(cx, cy, ro * R, a)
            d.append(f"M{n(x1)},{n(y1)}L{n(x2)},{n(y2)}")
        Bd.append(f'<path d="{"".join(d)}" fill="none" stroke="url(#{uid}-gold)" stroke-width="{n(2.2 * k)}" stroke-linecap="round"/>')
    Bd.append(F.hairline_ring(cx, cy, (P["hair"] * R,), f"url(#{uid}-gold)", 2.0 * k))
    if base and rays:
        Bd.append(F.tick_ring(cx, cy, (P["bezel_out"] + 0.02) * R, (P["hair"] - 0.012) * R, 480, f"url(#{uid}-gold)",
                              sw=0.9 * k, op=0.10))

    # ring lettering
    size_t = size_for_cap(f, P["top_cap"] * R)
    size_b = size_for_cap(f, P["bot_cap"] * R)
    cap_t, cap_b = f.cap_height(size_t), f.cap_height(size_b)
    mid = P["text_mid"] * R
    gold_ink = f' fill="url(#{uid}-gold)" stroke="url(#{uid}-gold)"'
    t_svg, t_deg = F.ring_text(f, top_txt, cx, cy, mid - cap_t / 2, size_t, 0.15, 0.0, top=True, bold=0.035, extra=gold_ink)
    b_svg, b_deg = F.ring_text(f, bot_txt, cx, cy, mid + cap_b / 2, size_b, 0.14, 180.0, top=False, bold=0.045, extra=gold_ink)
    Bd.append(f'<g filter="url(#{uid}-tfoil)">{t_svg}{b_svg}</g>')
    bead_deg = ((t_deg / 2) + (180.0 - b_deg / 2)) / 2             # halfway between the end of the top text and the start of the bottom
    Bd.append(f'<g filter="url(#{uid}-tfoil)">'
              + F.beads(cx, cy, mid, 1, 0.0165 * R, f"url(#{uid}-gold)", start_deg=bead_deg)
              + F.beads(cx, cy, mid, 1, 0.0165 * R, f"url(#{uid}-gold)", start_deg=360.0 - bead_deg) + '</g>')

    # bezel
    RF = P["field"] * R
    bez_d = F.annulus_d(cx, cy, P["bezel_out"] * R, RF)
    Bd.append(f'<g filter="url(#{uid}-foil)"><path d="{bez_d}" fill="url(#{uid}-gold2)" fill-rule="evenodd"/></g>')
    Bd.append(F.hairline_ring(cx, cy, ((P["bezel_out"] + 0.012) * R,), f"url(#{uid}-gold)", 1.2 * k, 0.55))

    # field: sunrise rays (alternating wedges that fade in from the mark) under a fine engine-turned lace at the edge
    if base:
        D.append(f'<clipPath id="{uid}-fieldclip"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(RF)}"/></clipPath>')
        Bd.append(f'<g filter="url(#{uid}-recess)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(RF)}" fill="url(#{uid}-field)"/></g>')
        ray_col = "#B08F3C" if cream_field else "#8FA9D6"
        D.append(F.rad(uid, "rayfade", cx, cy, RF,
                       [(0, ray_col, 0.0), (0.46, ray_col, 0.0), (0.74, ray_col, 0.12 if cream_field else 0.08),
                        (1, ray_col, 0.24 if cream_field else 0.16)]))
        wedges = []
        for i in range(0, 2 * rays_n, 2):
            a0 = 360.0 * i / (2 * rays_n)
            a1 = 360.0 * (i + 1) / (2 * rays_n)
            x0, y0 = F.polar(cx, cy, RF, a0)
            x1, y1 = F.polar(cx, cy, RF, a1)
            wedges.append(f"M{n(cx)},{n(cy)}L{n(x0)},{n(y0)}A{n(RF)},{n(RF)} 0 0,1 {n(x1)},{n(y1)}Z")
        Bd.append(f'<g clip-path="url(#{uid}-fieldclip)"><path d="{"".join(wedges)}" fill="url(#{uid}-rayfade)"/></g>')
        # three hairline rings and a ring of beads close the field off from the bezel
        Bd.append(F.hairline_ring(cx, cy, tuple(RF * f_ for f_ in (0.80, 0.90, 0.972)), f"url(#{uid}-gold)", 1.0 * k, 0.55))
        Bd.append(F.beads(cx, cy, RF * 0.935, 96, 1.5 * k, f"url(#{uid}-gold)", extra=' fill-opacity="0.75"'))
    else:
        D.append(f'<clipPath id="{uid}-fieldclip"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(RF)}"/></clipPath>')
        d1, b1 = F.rosette(uid, "r1", cx, cy, RF * 0.985, count=72, k=0.62, rot0=0.0, stroke=f"url(#{uid}-gold)", sw=0.8 * k, op=0.30)
        D.append(d1)
        Bd.append(f'<g clip-path="url(#{uid}-fieldclip)">{b1}</g>')

    # the mark
    RC = P["rc"] * R
    md, mb = mark_layers(uid + "m", cx, cy, RC, reg, disc=disc, ground_dark=ground_dark, flat=flat)
    D.append(md)
    Bd.append(mb)
    info = dict(top_deg=round(t_deg, 1), bot_deg=round(b_deg, 1), bead_deg=round(bead_deg, 1), legend_reps=legend_reps,
                arc_reach=round(1.3 * P["rc"] / P["field"], 3), RC=round(RC, 1))
    return "".join(D), "".join(Bd), info
