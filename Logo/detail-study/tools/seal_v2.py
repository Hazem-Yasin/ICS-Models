"""
Seal v2 for the ICS mark: the retro-futurist, "more Fallout" pass.  Stdlib only.  [PROPOSAL tooling -- nothing here is canon]

    seal2(...)   badge with INTERPLANETARY arched on top, "ICS" across the middle of the disc, and nothing where the tagline
                 used to be (a row of planets, or optionally a canon-quoted second line)

Two options were added after the author said "feel free to choose whatever let's get it done" (2026-11-12).  Both are off by
default, so the five earlier seal2_* pieces rebuild byte for byte: theme="gold" (gold foil only, no ground, to lay on a Deep Blue
object such as the folder cover, Doc 2.33:3) and ics_on="band" ("ICS" arched along the bottom of the band, the disc left clean).

What the author asked for (2026-11-12): keep the canon mark, add detail in the manner of Poseidon Energy / the Brotherhood of
Steel, retro-futurist and more Fallout, "ICS" in the middle, "INTERPLANETARY" on top, and remove the tagline.

Read from the references, not copied: a thick band with big arched lettering, a star each side of it, a bold central
emblem, gears and rivets, a crimped bottle-cap edge.  Every form is rounded (Doc 2.32:48 "no sharp angles"); the Brotherhood's
sawtooth gear is NOT used for that reason.  The scalloped rim comes from ics_finish.cog_d, which has no corner.

The circle, the arc and the channel between them are still read from Logo/src/ics_brand.py through seal_art.mark_layers.
Nothing here edits them.  seal_art.py is untouched, so the v1 files rebuild byte for byte.

Open and flagged: lettering across the disc sits against "a clean, unbroken circle" (Doc 2.32:29) and "There is no ICS corporate
mark" (2.32:5).  Only user-specified words are drawn by default.  `bottom=` takes an optional canon-quoted second line.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import ics_finish as F     # noqa: E402
import seal_art as S       # noqa: E402

n = F.n

PLAN2 = dict(
    cog_r0=0.985, cog_amp=0.0135, cog_lobes=36,   # scalloped outer edge of the gold rim
    rim_in=0.925,                                  # gold rim runs from the scallops in to here
    rivet_r=0.953, rivet_rb=0.0105,                # one rivet on each of the 36 lobes
    tick_base=0.868, tick_minor=0.888, tick_major=0.906, hair=0.858,   # the 349-tick dial, on the navy
    band_in=0.660,                                 # the lettering band is hair .. band_in
    top_cap=0.130, sub_cap=0.090,                  # cap heights of INTERPLANETARY and the optional second line
    bezel_out=0.660, field=0.634,
    rc=0.40,                                       # mark circle radius (v1 used 0.415)
    ics_cap=0.46,                                  # cap height of the centre "ICS", in mark radii
    star_out=0.070, star_in=0.037,                 # the stars each side of the band (Poseidon cue)
    spark_r=0.036, spark_at=70.5,                  # 4-point sparkles at 180 +/- this, i.e. between each star and the planet row
    ics_band_track=0.28,                           # ics_on="band": tracking of the arched "ICS", in em
    band_lead=5.0, band_dot0=9.0,                  # ics_on="band": degrees from the end of "ICS" to the hairline and to the first planet
)

CREAM = "#F6F1E3"


# ---- rounded shapes ---------------------------------------------------------------------------------------------------------
def rounded_poly_d(pts, radii):
    """Closed path through `pts` with every corner replaced by a quadratic curve.  radii[i] is the distance from vertex i
    where the curve starts, capped at 45% of the shorter neighbouring edge."""
    m = len(pts)
    cuts = []
    for i in range(m):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % m]
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        d = min(radii[i], 0.45 * l1, 0.45 * l2)
        cuts.append(((p1[0] + v1[0] / l1 * d, p1[1] + v1[1] / l1 * d), p1, (p1[0] + v2[0] / l2 * d, p1[1] + v2[1] / l2 * d)))
    out = [f"M{n(cuts[0][0][0])},{n(cuts[0][0][1])}"]
    for i, (a, p, b) in enumerate(cuts):
        if i:
            out.append(f"L{n(a[0])},{n(a[1])}")
        out.append(f"Q{n(p[0])},{n(p[1])} {n(b[0])},{n(b[1])}")
    return "".join(out) + "Z"


def star_d(cx, cy, r_out, r_in, points=5, rot=0.0, round_out=0.30, round_in=0.10):
    """A star with every corner rounded.  rot = degrees clockwise from point-up."""
    pts, radii = [], []
    for j in range(2 * points):
        outer = j % 2 == 0
        pts.append(F.polar(cx, cy, r_out if outer else r_in, rot + 180.0 * j / points))
        radii.append(r_out * round_out if outer else r_in * round_in * 2)
    return rounded_poly_d(pts, radii)


def sparkle_d(cx, cy, r, pinch=0.16):
    """A 4-point atomic-age sparkle with concave sides.  The tips are sharp as a path; stroke it with a round join (in the
    fill colour) to round them, as seal2() does."""
    p = pinch * r
    return (f"M{n(cx)},{n(cy - r)}Q{n(cx + p)},{n(cy - p)} {n(cx + r)},{n(cy)}Q{n(cx + p)},{n(cy + p)} {n(cx)},{n(cy + r)}"
            f"Q{n(cx - p)},{n(cy + p)} {n(cx - r)},{n(cy)}Q{n(cx - p)},{n(cy - p)} {n(cx)},{n(cy - r)}Z")


def crown_d(cx, cy, r_a, r_long, r_short, count, start=0.0):
    """Radial ticks of alternating length, to be stroked with round caps: a ring of capsule rays."""
    d = []
    for i in range(count):
        a = start + 360.0 * i / count
        r_b = r_long if i % 2 == 0 else r_short
        x1, y1 = F.polar(cx, cy, r_a, a)
        x2, y2 = F.polar(cx, cy, r_b, a)
        d.append(f"M{n(x1)},{n(y1)}L{n(x2)},{n(y2)}")
    return "".join(d)


# ---- the badge --------------------------------------------------------------------------------------------------------------
def seal2(uid, cx, cy, R, theme="paper", region=None, bottom=None, n_ticks=349, orbit=True, flat=False, metal="gold",
          ics_on="disc"):
    """Return (defs, body, info) for a v2 badge of radius R centred at (cx, cy).
    theme: paper = navy medallion, cream field, navy-enamel disc with cream "ICS"
           night = navy medallion, dark field, cream-enamel disc with navy "ICS"
           gold  = gold foil only: no medallion and no field disc, a gold-foil mark disc with Deep Blue "ICS" on it; made to lay
                   on a Deep Blue object (the folder cover: "the gold seal embossed on the cover", Doc 2.33:3)
    bottom: None = a row of planets in the band (adds no words); or a string such as "CORPORATE SOLUTIONS" for a second arched
            line.  The default adds no wording the author did not specify.
    orbit: a pale tilted orbit with one small planet, drawn behind the mark.
    flat: flat enamel disc (see seal_art.mark_layers).
    metal: "gold" (polished gold and enamel) or "steel" (steel and enamel; smooth sheen, no brush texture).  Only the rim, lettering and ornaments change.
           The mark's own arc stays canon Warm Gold in both, because mark_layers draws it.
    ics_on: "disc" = "ICS" across the middle of the mark (what the author asked for).  "band" = "ICS" arched along the bottom of
            the band, as big as INTERPLANETARY, with the planet row running out from it; nothing is drawn on the disc, so the
            circle stays unlettered (Doc 2.32:29).  Cannot be combined with bottom=, which wants the same stretch of band."""
    P = PLAN2
    f = S.font()
    k = R / 556.0
    reg = region if region is not None else (cx - 1.14 * R, cy - 1.14 * R, 2.28 * R, 2.28 * R)
    if theme not in ("paper", "night", "gold"):
        raise ValueError(f"theme must be paper, night or gold, not {theme!r}")
    if ics_on not in ("disc", "band"):
        raise ValueError(f"ics_on must be disc or band, not {ics_on!r}")
    if ics_on == "band" and bottom:
        raise ValueError("ics_on='band' puts ICS on the bottom of the band, so bottom= must be None")
    paper = theme == "paper"
    gold = theme == "gold"
    disc = "blue" if paper else ("gold" if gold else "cream")
    steel = metal == "steel"
    ms = F.STEEL_STOPS if steel else F.GOLD_STOPS
    D, B = [], []

    # gradients
    D.append(F.lin(uid, "gold", cx - R, cy - R, cx + R, cy + R, ms))
    D.append(F.lin(uid, "gold2", cx + R, cy - R, cx - R, cy + R, ms))
    if not gold:                                   # the gold master has no ground of its own: the object under it is the ground
        D.append(F.rad(uid, "navy", cx - 0.35 * R, cy - 0.45 * R, 1.5 * R, [(0, "#294676"), (0.5, F.BLUE), (1, "#112043")]))
        if paper:
            D.append(F.rad(uid, "field", cx - 0.2 * R, cy - 0.3 * R, 1.0 * R, [(0, "#FBF8F1"), (0.7, "#F1ECDF"), (1, "#E3DBC8")]))
        else:
            D.append(F.rad(uid, "field", cx - 0.2 * R, cy - 0.3 * R, 1.0 * R, [(0, "#16294F"), (0.7, "#0E1C3A"), (1, "#081329")]))
    # filters
    if not gold:
        D.append(F.f_inner(uid, "medal", reg, blur=10 * k, dx=-3 * k, dy=-6 * k, op=0.50, col="#040A18",
                           shadow=(8 * k, 16 * k, 16 * k, 0.34 if paper else 0.60)))
    D.append(F.f_raise(uid, "foil", reg, blur=2.6 * k, scale=3.6 * k, el=48, az=225, spec=0.20, spec_exp=46,
                       spec_col="#FFFFFF" if steel else "#FFF6D6", shadow=(3 * k, 6 * k, 5 * k, 0.30), plateau="0 .55 .92 1 1"))
    D.append(F.f_raise(uid, "tfoil", reg, blur=1.2 * k, scale=2.4 * k, el=50, az=225, spec=0.0,
                       shadow=(1.6 * k, 2.8 * k, 2.2 * k, 0.50), plateau="0 .6 .95 1 1"))
    if ics_on == "disc":                           # this filter is only for the "ICS" across the disc
        D.append(F.f_raise(uid, "ics", reg, blur=2.0 * k, scale=3.0 * k, el=52, az=225, spec=0.10, spec_exp=30,
                           spec_col="#FFFFFF", shadow=(2.2 * k, 4.4 * k, 3.6 * k, 0.55), plateau="0 .5 .9 1 1"))
    if not gold:
        D.append(F.f_inner(uid, "recess", reg, blur=9 * k, dx=0, dy=7 * k, op=0.40, col="#000"))

    # navy medallion under everything (none for the gold master)
    if not gold:
        B.append(f'<g filter="url(#{uid}-medal)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(P["rim_in"] * R + 2 * k)}" fill="url(#{uid}-navy)"/></g>')

    # gold rim with a scalloped (crimped) edge: a smooth cog, so no corner anywhere
    rim_d = F.cog_d(cx, cy, P["cog_r0"] * R, P["cog_amp"] * R, P["cog_lobes"], k=1.5, steps=720) + F.ring_d(cx, cy, P["rim_in"] * R)
    D.append(f'<clipPath id="{uid}-rimclip"><path d="{rim_d}" clip-rule="evenodd"/></clipPath>')
    B.append(f'<g filter="url(#{uid}-foil)"><path d="{rim_d}" fill="url(#{uid}-gold)" fill-rule="evenodd"/></g>')
    B.append(f'<g clip-path="url(#{uid}-rimclip)">{F.sunburst(cx, cy, R * 1.02, count=240, theta0=-40, peak=0.22, power=2.2)}</g>')
    B.append(f'<g filter="url(#{uid}-tfoil)">'
             + F.beads(cx, cy, P["rivet_r"] * R, P["cog_lobes"], P["rivet_rb"] * R, f"url(#{uid}-gold2)") + '</g>')

    # dial: one tick per planet in the portfolio (349), longer at each quarter -- same as v1, same [PROPOSAL] caveats
    if n_ticks:
        quarter = {round(i * n_ticks / 4.0) % n_ticks for i in range(4)}
        d = []
        for i in range(n_ticks):
            a = 360.0 * i / n_ticks
            ro = P["tick_major"] if i in quarter else P["tick_minor"]
            x1, y1 = F.polar(cx, cy, P["tick_base"] * R, a)
            x2, y2 = F.polar(cx, cy, ro * R, a)
            d.append(f"M{n(x1)},{n(y1)}L{n(x2)},{n(y2)}")
        B.append(f'<path d="{"".join(d)}" fill="none" stroke="url(#{uid}-gold)" stroke-width="{n(2.1 * k)}" stroke-linecap="round"/>')
    B.append(F.hairline_ring(cx, cy, (P["hair"] * R,), f"url(#{uid}-gold)", 2.0 * k))
    B.append(F.tick_ring(cx, cy, (P["band_in"] + 0.012) * R, (P["hair"] - 0.010) * R, 480, f"url(#{uid}-gold)", sw=0.9 * k, op=0.07))

    # the band: INTERPLANETARY on top, a star each side, and either a row of planets or a second line underneath
    mid = (P["hair"] + P["band_in"]) / 2 * R
    gold_ink = f' fill="url(#{uid}-gold)" stroke="url(#{uid}-gold)"'
    size_t = S.size_for_cap(f, P["top_cap"] * R)
    cap_t = f.cap_height(size_t)
    t_svg, t_deg = F.ring_text(f, "INTERPLANETARY", cx, cy, mid - cap_t / 2, size_t, 0.09, 0.0, top=True, bold=0.080, extra=gold_ink)
    parts = [t_svg]
    b_deg = 0.0
    if bottom:
        size_b = S.size_for_cap(f, P["sub_cap"] * R)
        cap_b = f.cap_height(size_b)
        b_svg, b_deg = F.ring_text(f, bottom, cx, cy, mid + cap_b / 2, size_b, 0.12, 180.0, top=False, bold=0.07, extra=gold_ink)
        parts.append(b_svg)
    ics_deg = 0.0
    if ics_on == "band":
        # "ICS" along the bottom of the band, the same cap height and weight as INTERPLANETARY above it
        c_svg, ics_deg = F.ring_text(f, "ICS", cx, cy, mid + cap_t / 2, size_t, P["ics_band_track"], 180.0, top=False,
                                     bold=0.080, extra=gold_ink)
        parts.append(c_svg)
    B.append(f'<g filter="url(#{uid}-tfoil)">{"".join(parts)}</g>')
    stars = "".join(f'<path d="{star_d(*F.polar(cx, cy, mid, a), P["star_out"] * R, P["star_in"] * R, rot=0.0)}"/>' for a in (90.0, 270.0))
    B.append(f'<g filter="url(#{uid}-tfoil)" fill="url(#{uid}-gold2)">{stars}</g>')
    planets_info = 0
    if ics_on == "band":
        # [PROPOSAL] ornament only, no wording: the planet row runs out from "ICS" on both sides, each planet smaller than the last
        half = ics_deg / 2.0
        offs, o = [], half + P["band_dot0"]
        for step in (0.0, 11.5, 9.5, 8.0, 6.5):
            o += step
            offs.append(o)
        sizes = (0.0200, 0.0150, 0.0115, 0.0088, 0.0068)
        lead, end = half + P["band_lead"], offs[-1] + 5.0
        arcs = _arc_d(cx, cy, mid, 180.0 - end, 180.0 - lead) + _arc_d(cx, cy, mid, 180.0 + lead, 180.0 + end)
        B.append(f'<path d="{arcs}" fill="none" stroke="url(#{uid}-gold)" stroke-width="{n(1.1 * k)}" stroke-opacity="0.7" '
                 f'stroke-linecap="round"/>')
        dots = []
        for off, sz in zip(offs, sizes):
            for sgn in (-1, 1):
                x, y = F.polar(cx, cy, mid, 180.0 + sgn * off)
                dots.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(sz * R)}"/>')
                planets_info += 1
        B.append(f'<g filter="url(#{uid}-tfoil)" fill="url(#{uid}-gold2)">{"".join(dots)}</g>')
    elif not bottom:
        # [PROPOSAL] ornament only: planets on a hairline orbit across the bottom of the band.  Adds no wording.
        spec = [(0, 0.0), (1, 15.5), (2, 27.0), (3, 36.5), (4, 44.5), (5, 51.0)]
        size_by = {0: 0.0, 1: 0.0200, 2: 0.0150, 3: 0.0115, 4: 0.0088, 5: 0.0068}
        B.append(f'<path d="{_arc_d(cx, cy, mid, 180.0 - 56.0, 180.0 + 56.0)}" fill="none" stroke="url(#{uid}-gold)" '
                 f'stroke-width="{n(1.1 * k)}" stroke-opacity="0.7" stroke-linecap="round"/>')
        dots = []
        for idx, off in spec[1:]:
            for sgn in (-1, 1):
                x, y = F.polar(cx, cy, mid, 180.0 + sgn * off)
                dots.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(size_by[idx] * R)}"/>')
                planets_info += 1
        B.append(f'<g filter="url(#{uid}-tfoil)" fill="url(#{uid}-gold2)">{"".join(dots)}</g>')
        # the ringed planet at the centre of the row
        px, py = F.polar(cx, cy, mid, 180.0)
        pr = 0.034 * R
        rx, ry = 0.064 * R, 0.017 * R
        ring = f'transform="rotate(-16 {n(px)} {n(py)})"'
        back = f'M{n(px - rx)},{n(py)}A{n(rx)},{n(ry)} 0 0,1 {n(px + rx)},{n(py)}'
        front = f'M{n(px - rx)},{n(py)}A{n(rx)},{n(ry)} 0 0,0 {n(px + rx)},{n(py)}'
        B.append(f'<g filter="url(#{uid}-tfoil)">'
                 f'<path d="{back}" {ring} fill="none" stroke="url(#{uid}-gold)" stroke-width="{n(3.2 * k)}" stroke-linecap="round"/>'
                 f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(pr)}" fill="url(#{uid}-gold2)"/>'
                 f'<path d="{front}" {ring} fill="none" stroke="url(#{uid}-gold)" stroke-width="{n(3.2 * k)}" stroke-linecap="round"/></g>')
        planets_info += 1
    if not bottom:
        # [PROPOSAL] a sparkle each side of the planet row, the same weight on both sides
        sp = []
        for sgn in (-1, 1):
            sx, sy = F.polar(cx, cy, mid, 180.0 + sgn * P["spark_at"])
            sp.append(f'<path d="{sparkle_d(sx, sy, P["spark_r"] * R)}"/>')
        B.append(f'<g filter="url(#{uid}-tfoil)" fill="url(#{uid}-gold2)" stroke="url(#{uid}-gold2)" stroke-width="{n(2.2 * k)}" '
                 f'stroke-linejoin="round">{"".join(sp)}</g>')

    # bezel
    RF = P["field"] * R
    bez_d = F.annulus_d(cx, cy, P["bezel_out"] * R, RF)
    B.append(f'<g filter="url(#{uid}-foil)"><path d="{bez_d}" fill="url(#{uid}-gold2)" fill-rule="evenodd"/></g>')
    B.append(F.hairline_ring(cx, cy, ((P["bezel_out"] + 0.011) * R,), f"url(#{uid}-gold)", 1.2 * k, 0.55))

    # field: dark-or-cream ground, soft wedge rays, a crown of round-tipped rays, an orbit with one planet
    D.append(f'<clipPath id="{uid}-fieldclip"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(RF)}"/></clipPath>')
    if not gold:
        B.append(f'<g filter="url(#{uid}-recess)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(RF)}" fill="url(#{uid}-field)"/></g>')
    metal_col = "#8A94A0" if steel else "#C9A84C"
    ray_col = ("#7B8591" if steel else "#B08F3C") if paper else (metal_col if gold else "#8FA9D6")
    D.append(F.rad(uid, "rayfade", cx, cy, RF,
                   [(0, ray_col, 0.0), (0.46, ray_col, 0.0), (0.72, ray_col, 0.16 if paper else 0.10),
                    (1, ray_col, 0.30 if paper else 0.20)]))
    wedges = []
    for i in range(0, 72, 2):
        x0, y0 = F.polar(cx, cy, RF, 360.0 * i / 72)
        x1, y1 = F.polar(cx, cy, RF, 360.0 * (i + 1) / 72)
        wedges.append(f"M{n(cx)},{n(cy)}L{n(x0)},{n(y0)}A{n(RF)},{n(RF)} 0 0,1 {n(x1)},{n(y1)}Z")
    B.append(f'<g clip-path="url(#{uid}-fieldclip)"><path d="{"".join(wedges)}" fill="url(#{uid}-rayfade)"/></g>')
    crown_col = metal_col if (paper or gold) else "#9DB4DC"
    B.append(f'<path d="{crown_d(cx, cy, 0.553 * R, 0.620 * R, 0.585 * R, 72, start=0.0)}" fill="none" stroke="{crown_col}" '
             f'stroke-opacity="{0.78 if (paper or gold) else 0.55}" stroke-width="{n(0.0105 * R)}" stroke-linecap="round"/>')
    ox = oy = None
    if orbit:
        rx_o, ry_o, tilt = 0.585 * R, 0.205 * R, -24.0
        oc = ("#5F6A77" if steel else "#8C6D26") if paper else (metal_col if gold else "#9DB4DC")
        B.append(f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx_o)}" ry="{n(ry_o)}" transform="rotate({tilt} {n(cx)} {n(cy)})" '
                 f'fill="none" stroke="{oc}" stroke-opacity="{0.75 if (paper or gold) else 0.60}" stroke-width="{n(2.6 * k)}"/>')
        t = math.radians(18.0)      # the visible upper-right end of the orbit, clear of the arc (205 sat on the arc's thin tail)
        ex, ey = rx_o * math.cos(t), ry_o * math.sin(t)
        c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        ox, oy = cx + ex * c - ey * s, cy + ex * s + ey * c
        B.append(f'<g filter="url(#{uid}-tfoil)"><circle cx="{n(ox)}" cy="{n(oy)}" r="{n(0.021 * R)}" fill="url(#{uid}-gold2)"/></g>')

    # the mark, then "ICS" across its middle
    RC = P["rc"] * R
    md, mb = S.mark_layers(uid + "m", cx, cy, RC, reg, disc=disc, ground_dark=not paper, flat=flat)
    D.append(md)
    B.append(mb)
    w_i = 0.0
    if ics_on == "disc":
        size_i = S.size_for_cap(f, P["ics_cap"] * RC)
        cap_i = f.cap_height(size_i)
        d_i, w_i = f.text_path("ICS", size_i, cx, cy + cap_i / 2, 0.07 * size_i, "middle")
        ink = CREAM if paper else F.BLUE
        B.append(f'<g filter="url(#{uid}-ics)"><path d="{d_i}" fill="{ink}" stroke="{ink}" stroke-width="{n(0.075 * size_i)}" '
                 f'stroke-linejoin="round"/></g>')
    info = dict(top_deg=round(t_deg, 1), bottom_deg=round(b_deg, 1), planets=planets_info, ics_w_over_RC=round(w_i / RC, 3),
                RC=round(RC, 1))
    if ics_on == "band":
        info["ics_band_deg"] = round(ics_deg, 1)
    return "".join(D), "".join(B), info


def _arc_d(cx, cy, r, a0, a1):
    """Open SVG arc from a0 to a1 degrees (clockwise from top), radius r."""
    x0, y0 = F.polar(cx, cy, r, a0)
    x1, y1 = F.polar(cx, cy, r, a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    return f"M{n(x0)},{n(y0)}A{n(r)},{n(r)} 0 {large},1 {n(x1)},{n(y1)}"
