"""
Finishing toolkit for the ICS logo-detail study.  Stdlib only.  [PROPOSAL tooling]

Everything here is SVG that librsvg (ffmpeg's decoder) and browsers both draw: gradients, lighting filters, inner
shadows, grain.  Geometry for the Earth Branch mark is NOT defined here -- it is imported read-only from
Logo/src/ics_brand.py, so there is still exactly one source for the circle and the arc.
"""
import math
import random

BLUE = "#1A2E52"        # canon: ICS Deep Blue
GOLD = "#C9A84C"        # canon: ICS Warm Gold
PAPER = "#F4F1EA"       # [PROPOSAL] kit paper white
MIDNIGHT = "#0B1426"    # [PROPOSAL] trailer ground (Models kit)


def n(x):
    s = f"{x:.2f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


# ---- gradients ---------------------------------------------------------------------------------------------------------
def stops(lst):
    out = []
    for s in lst:
        o, c = s[0], s[1]
        a = s[2] if len(s) > 2 else None
        out.append(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>")
    return "".join(out)


def lin(uid, name, x1, y1, x2, y2, st, units="userSpaceOnUse"):
    return (f'<linearGradient id="{uid}-{name}" gradientUnits="{units}" x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" '
            f'y2="{n(y2)}">{stops(st)}</linearGradient>')


def rad(uid, name, cx, cy, r, st, fx=None, fy=None, units="userSpaceOnUse"):
    f = "" if fx is None else f' fx="{n(fx)}" fy="{n(fy)}"'
    return (f'<radialGradient id="{uid}-{name}" gradientUnits="{units}" cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"{f}>'
            f'{stops(st)}</radialGradient>')


GOLD_STOPS = [(0, "#F1E4AA"), (0.26, "#DABF6A"), (0.48, GOLD), (0.70, "#A88830"), (0.86, "#CBB058"), (1, "#E8D690")]
GOLD_DEEP_STOPS = [(0, "#D9C07A"), (0.4, "#B8963F"), (0.7, "#8C6D26"), (1, "#C4A552")]
STEEL_STOPS = [(0, "#F3F5F7"), (0.25, "#C9CFD5"), (0.5, "#9AA2AB"), (0.72, "#D4D9DE"), (0.9, "#8A929B"), (1, "#E6E9EC")]
ENAMEL_STOPS = [(0, "#2D4A7E"), (0.55, BLUE), (1, "#122244")]


# ---- filters -----------------------------------------------------------------------------------------------------------
def _reg(region):
    x, y, w, h = region
    return f'filterUnits="userSpaceOnUse" x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"'


def f_raise(uid, name, region, blur, scale, el=52, az=225, spec=0.0, spec_exp=24, spec_col="#FFF4CC",
            shadow=None, tint=None, plateau=None):
    """Raised metal/foil: the fill is multiplied by diffuse lighting from a blurred-alpha height map, optionally plus a
    specular term, optionally with a drop shadow = (dx, dy, blur, opacity).
    plateau: a feFuncA table (e.g. "0 .6 .95 1 1") that flattens the top of the height map, so the piece reads as a flat
    plate with a bevelled edge instead of a rounded tube."""
    dc = 1.0 / math.sin(math.radians(el))
    hm = ""
    if plateau:
        hm = (f'<feComponentTransfer in="hb" result="h"><feFuncA type="table" tableValues="{plateau}"/></feComponentTransfer>')
    s = [f'<filter id="{uid}-{name}" {_reg(region)} color-interpolation-filters="sRGB">',
         f'<feGaussianBlur in="SourceAlpha" stdDeviation="{n(blur)}" result="{"hb" if plateau else "h"}"/>' + hm,
         f'<feDiffuseLighting in="h" surfaceScale="{n(scale)}" diffuseConstant="{n(dc)}" lighting-color="#fff" '
         f'result="d"><feDistantLight azimuth="{az}" elevation="{el}"/></feDiffuseLighting>',
         '<feComposite in="SourceGraphic" in2="d" operator="arithmetic" k1="1" k2="0" k3="0" k4="0" result="lit"/>']
    last = "lit"
    if spec > 0:
        s.append(f'<feSpecularLighting in="h" surfaceScale="{n(scale)}" specularConstant="{n(spec)}" '
                 f'specularExponent="{n(spec_exp)}" lighting-color="{spec_col}" result="sp">'
                 f'<feDistantLight azimuth="{az}" elevation="{n(el - 6)}"/></feSpecularLighting>')
        s.append('<feComposite in="sp" in2="SourceAlpha" operator="in" result="sp2"/>')
        s.append('<feComposite in="lit" in2="sp2" operator="arithmetic" k1="0" k2="1" k3="1" k4="0" result="ls"/>')
        last = "ls"
    if shadow:
        dx, dy, sb, so = shadow
        s += [f'<feGaussianBlur in="SourceAlpha" stdDeviation="{n(sb)}" result="sb"/>',
              f'<feOffset in="sb" dx="{n(dx)}" dy="{n(dy)}" result="so"/>',
              f'<feFlood flood-color="#000" flood-opacity="{so}" result="sf"/>',
              '<feComposite in="sf" in2="so" operator="in" result="sh"/>',
              f'<feMerge><feMergeNode in="sh"/><feMergeNode in="{last}"/></feMerge>']
    else:
        s.append(f'<feOffset in="{last}" dx="0" dy="0"/>')
    s.append("</filter>")
    return "".join(s)


def f_inner(uid, name, region, blur, dx=0, dy=0, op=0.6, col="#000", shadow=None):
    """Inner shadow (a recessed or domed look), optionally with an outer drop shadow."""
    s = [f'<filter id="{uid}-{name}" {_reg(region)} color-interpolation-filters="sRGB">',
         '<feComponentTransfer in="SourceAlpha" result="inv"><feFuncA type="table" tableValues="1 0"/></feComponentTransfer>',
         f'<feGaussianBlur in="inv" stdDeviation="{n(blur)}" result="b"/>',
         f'<feOffset in="b" dx="{n(dx)}" dy="{n(dy)}" result="o"/>',
         f'<feFlood flood-color="{col}" flood-opacity="{op}" result="c"/>',
         '<feComposite in="c" in2="o" operator="in" result="s"/>',
         '<feComposite in="s" in2="SourceAlpha" operator="in" result="s2"/>']
    if shadow:
        sdx, sdy, sb, so = shadow
        s += [f'<feGaussianBlur in="SourceAlpha" stdDeviation="{n(sb)}" result="ob"/>',
              f'<feOffset in="ob" dx="{n(sdx)}" dy="{n(sdy)}" result="oo"/>',
              f'<feFlood flood-color="#000" flood-opacity="{so}" result="of"/>',
              '<feComposite in="of" in2="oo" operator="in" result="osh"/>',
              '<feMerge><feMergeNode in="osh"/><feMergeNode in="SourceGraphic"/><feMergeNode in="s2"/></feMerge>']
    else:
        s.append('<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="s2"/></feMerge>')
    s.append("</filter>")
    return "".join(s)


def f_blur(uid, name, region, sd):
    return (f'<filter id="{uid}-{name}" {_reg(region)}><feGaussianBlur stdDeviation="{n(sd)}"/></filter>')


def f_grain(uid, name, region, freq=0.85, octaves=2, seed=4, k=2.0, ink="0 0 0"):
    """Noise-only layer (use as a filtered <rect>); alpha = clamp(k*(R-0.5)) so only the upper half of the noise shows."""
    r, g, b = ink.split()
    return (f'<filter id="{uid}-{name}" {_reg(region)} color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="{octaves}" seed="{seed}" result="t"/>'
            f'<feColorMatrix in="t" type="matrix" values="0 0 0 0 {r}  0 0 0 0 {g}  0 0 0 0 {b}  {n(k)} 0 0 0 {n(-0.5 * k)}"/>'
            '</filter>')


def f_brushed(uid, name, region, fx=0.004, fy=0.55, seed=7, k=2.2, ink="1 1 1"):
    """Brushed-metal streaks: anisotropic noise (long in x, fine in y)."""
    r, g, b = ink.split()
    return (f'<filter id="{uid}-{name}" {_reg(region)} color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{fx} {fy}" numOctaves="2" seed="{seed}" result="t"/>'
            f'<feColorMatrix in="t" type="matrix" values="0 0 0 0 {r}  0 0 0 0 {g}  0 0 0 0 {b}  {n(k)} 0 0 0 {n(-0.5 * k)}"/>'
            '</filter>')


# ---- geometry helpers ------------------------------------------------------------------------------------------------
def cog_d(cx, cy, r0, amp, lobes, k=1.7, steps=1440, phase=0.0):
    """Closed path of a rounded, friendly cog (smooth, no corners): r = r0 + amp*tanh(k cos(N th)) / tanh(k)."""
    t = math.tanh(k)
    pts = []
    for i in range(steps):
        th = 2 * math.pi * i / steps
        r = r0 + amp * math.tanh(k * math.cos(lobes * th + phase)) / t
        pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts) + "Z"


def ring_d(cx, cy, r):
    return f"M{n(cx - r)},{n(cy)}a{n(r)},{n(r)} 0 1,0 {n(2 * r)},0a{n(r)},{n(r)} 0 1,0 {n(-2 * r)},0Z"


def annulus_d(cx, cy, r_out, r_in):
    """Even-odd annulus path."""
    return ring_d(cx, cy, r_out) + ring_d(cx, cy, r_in)


def polar(cx, cy, r, deg_cw_from_top):
    a = math.radians(deg_cw_from_top)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def ticks_d(cx, cy, r_in, r_minor, r_major, count, major_every, start_deg=0.0, skip=()):
    d = []
    for i in range(count):
        if i in skip:
            continue
        a = start_deg + 360.0 * i / count
        ro = r_major if (major_every and i % major_every == 0) else r_minor
        x1, y1 = polar(cx, cy, r_in, a)
        x2, y2 = polar(cx, cy, ro, a)
        d.append(f"M{n(x1)},{n(y1)}L{n(x2)},{n(y2)}")
    return "".join(d)


def ring_text(font, text, cx, cy, r_base, size, track_em, center_deg, top=True, bold=0.0, extra=""):
    """Outlined text on a circle.  Returns (svg, total_angle_deg).  r_base = baseline radius: for top text the glyph
    tops point outward from it; for bottom text (upright to the viewer) the baseline is the OUTER edge and the tops point
    toward the centre.  Spacing is measured on the mid-cap circle so the tracking looks even."""
    cap = font.cap_height(size)
    k = size / font.upm
    advs = [font.advance_units(c) * k for c in text]
    tr = track_em * size
    rm = r_base + cap / 2 if top else r_base - cap / 2
    total = sum(advs) + tr * (len(text) - 1)
    d_all = []
    s = 0.0
    for ch, adv in zip(text, advs):
        mid = s + adv / 2
        ang = (mid - total / 2) / rm            # radians from the centre of the text
        deg = math.degrees(ang)
        phi = center_deg + deg if top else center_deg - deg
        px, py = polar(cx, cy, r_base, phi)
        rot = phi if top else phi + 180.0
        d, _a = font.path_xf(ch, size, px, py, rot, -adv / 2)
        if d:
            d_all.append(d)
        s += adv + tr
    sw = f' stroke-width="{n(bold * size)}" stroke-linejoin="round"' if bold else ""
    return f'<path d="{"".join(d_all)}"{sw}{extra}/>', math.degrees(total / rm)


def galaxy_dots(cx, cy, r_min, r_max, arms=3, count=1400, pitch_deg=21.0, seed=11, colors=("#8FA6C9", "#B9C7DD"),
                size=(1.1, 3.4), spread=0.030, cw=True, core=0.55):
    """A suggestion of a galaxy: dots scattered along logarithmic spiral arms (Handbook cover, Origin Narrative).
    r in px.  Returns an SVG <g> of <circle>s."""
    rnd = random.Random(seed)
    c = 1.0 / math.tan(math.radians(pitch_deg))
    out = []
    for _ in range(count):
        a = rnd.randrange(arms)
        u = rnd.random() ** 1.7                 # denser toward the middle
        r = r_min + (r_max - r_min) * u
        th = 2 * math.pi * a / arms + c * math.log(r / r_min) * (1 if cw else -1)
        th += rnd.gauss(0, spread * (r_max / r) ** 0.35 * 2.2)
        rr = r + rnd.gauss(0, spread * r_max * 0.55)
        if rr < r_min * 0.8 or rr > r_max * 1.02:
            continue
        x, y = cx + rr * math.cos(th), cy + rr * math.sin(th)
        sz = size[0] + (size[1] - size[0]) * (rnd.random() ** 3)
        op = 0.25 + 0.7 * rnd.random() * (1 - 0.45 * (rr - r_min) / (r_max - r_min))
        col = colors[0] if rnd.random() < 0.6 else colors[1]
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(sz)}" fill="{col}" fill-opacity="{op:.2f}"/>')
    return "<g>" + "".join(out) + "</g>"


def doc(w, h, body, defs="", bg=None, title="ICS detail study"):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}"><title>{title}</title><defs>{defs}</defs>{b}{body}</svg>')


# ---- sheen helper -----------------------------------------------------------------------------------------------------
def sunburst(cx, cy, r, count=360, theta0=-35.0, peak=0.16, power=3.0, floor=0.0, color="#FFFFFF", jitter=0.0, seed=3):
    """Spun-metal 'sunray' sheen: `count` thin wedges from the centre; opacity = floor + peak * lobe(angle), with two opposite
    bright lobes at theta0 and theta0 + 180 deg (an anisotropic highlight).  Wedges overlap by 6% so no seams show.
    Returns an SVG <g>; clip it to its disc yourself."""
    rnd = random.Random(seed)
    out = []
    step = 2 * math.pi / count
    for i in range(count):
        a0 = i * step
        a1 = a0 + step * 1.06
        mid = math.degrees(a0 + step / 2)
        lobe = (0.5 + 0.5 * math.cos(math.radians(2 * (mid - theta0)))) ** power
        op = floor + peak * lobe + (rnd.random() - 0.5) * jitter
        if op <= 0.002:
            continue
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        out.append(f'<path d="M{n(cx)},{n(cy)}L{n(x0)},{n(y0)}L{n(x1)},{n(y1)}Z" fill-opacity="{op:.3f}"/>')
    return f'<g fill="{color}">' + "".join(out) + "</g>"


# ---- engine-turned / engraved detail ------------------------------------------------------------------------------------
def rosette(uid, name, cx, cy, r, count=90, k=0.5, rot0=0.0, stroke="#FFFFFF", sw=0.8, op=0.12):
    """Guilloche-style rosette: `count` ellipses (rx = r, ry = k * r), each turned 180/count degrees from the last.  Their
    envelope is a lace of petals (the engine-turned look under translucent enamel).  Returns (defs, body); the body is one
    <g> of <use>s, so the file stays small."""
    eid = f"{uid}-{name}-e"
    d = f'<ellipse id="{eid}" cx="{n(cx)}" cy="{n(cy)}" rx="{n(r)}" ry="{n(r * k)}"/>'
    step = 180.0 / count
    uses = "".join(f'<use xlink:href="#{eid}" transform="rotate({rot0 + i * step:.3f} {n(cx)} {n(cy)})"/>' for i in range(count))
    b = (f'<g fill="none" stroke="{stroke}" stroke-width="{n(sw)}" stroke-opacity="{op}">'
         f'<use xlink:href="#{eid}"/>{uses}</g>')
    return d, b


def hairline_ring(cx, cy, radii, stroke, sw=0.8, op=1.0):
    return (f'<g fill="none" stroke="{stroke}" stroke-width="{n(sw)}" stroke-opacity="{op}">'
            + "".join(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>' for r in radii) + "</g>")


def beads(cx, cy, r, count, rb, fill, start_deg=0.0, skip=(), extra=""):
    out = []
    for i in range(count):
        if i in skip:
            continue
        x, y = polar(cx, cy, r, start_deg + 360.0 * i / count)
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rb)}"/>')
    return f'<g fill="{fill}"{extra}>' + "".join(out) + "</g>"


def tick_ring(cx, cy, r_in, r_out, count, stroke, sw=1.0, start_deg=0.0, op=1.0):
    """`count` round-capped radial ticks (reeded-edge look)."""
    return (f'<path d="{ticks_d(cx, cy, r_in, r_out, r_out, count, 0, start_deg)}" fill="none" stroke="{stroke}" '
            f'stroke-width="{n(sw)}" stroke-linecap="round" stroke-opacity="{op}"/>')
