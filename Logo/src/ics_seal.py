"""
ICS seal and emblem: the ONE layout source for the 2D kit (Logo/build_brand.py) and the 3D builds (Logo/ICS-Seal_build.py).
Pure Python. Every number is in design pixels of a canvas (seal: size x size, emblem: W x H), y DOWN as in SVG, then the
3D side converts. All of it is [PROPOSAL] around the canon mark (Doc 2.32); facts used: "LABOR SOURCE #349" (Doc 2.01),
300 ticks = Cycle 300, Earth Branch opened Cycle 290, tagline from Doc 2.32.

Canon mark inside: circle radius `mark_r`, centred on the seal centre (the arc's tail reaches ~1.3 x that).
"""
import math

TOP_TEXT = "ICS · EARTH BRANCH"
BOTTOM_TEXT = "LABOR SOURCE #349"
TAGLINE_CAPS = "BECAUSE YOU’RE WORTH THE INVESTMENT"
DATES = "EST. CYCLE 290 · CYCLE 300"

# Approximate Nunito ExtraBold cap advances (em). Letters are placed one by one so nothing depends on <textPath>.
ADV = {"A": .70, "B": .68, "C": .66, "D": .74, "E": .60, "H": .74, "I": .30, "L": .56, "N": .76, "O": .78, "R": .68,
       "S": .60, "U": .72, "W": 1.0, "#": .70, " ": .28, "·": .30, "3": .62, "4": .62, "9": .62}


def ring_letters(txt, c, r, fs, top=True, track=0.20):
    """Per-letter placement on a ring of radius r about (c, c). Returns [(char, x, y, rot_deg)] in SVG space (y down,
    rot clockwise). top=True: reads clockwise, letters stand outward from r. top=False: reads left to right along the
    bottom, letters stand inward from r (so both read upright). Spaces are skipped."""
    adv = [(ADV.get(ch, .65) + track) * fs for ch in txt]
    total = sum(adv) - track * fs
    out = []
    pos = -total / 2
    for ch, a in zip(txt, adv):
        mid = pos + (a - track * fs) / 2
        th = math.degrees(mid / r)
        pos += a
        if ch == " ":
            continue
        if top:
            out.append((ch, c + r * math.sin(math.radians(th)), c - r * math.cos(math.radians(th)), th))
        else:
            out.append((ch, c + r * math.sin(math.radians(th)), c + r * math.cos(math.radians(th)), -th))
    return out


def seal_layout(size):
    """Seal: field disc, outer ring + two hairlines, text on two arcs, the canon mark in the middle."""
    c = size / 2
    fs = size * 0.052
    r_base = size * 0.318
    sw = size * 0.0045
    hair = size * 0.0026
    return dict(
        size=size, c=c, R=size * 0.47, fs=fs, fs_bot=fs * 0.80, r_top=r_base, r_bot=r_base + 0.72 * fs * 0.80,
        ring_r=size * 0.47 - sw * 1.5, ring_w=sw,
        hair_in_r=r_base - fs * 0.30, hair_out_r=r_base + fs * 1.02, hair_w=hair,
        mark_r=size * 0.200,
        top=ring_letters(TOP_TEXT, c, r_base, fs, True),
        bottom=ring_letters(BOTTOM_TEXT, c, r_base + 0.72 * fs * 0.80, fs * 0.80, False),
    )


def emblem_layout(W):
    """Emblem: seal-like disc with 300 cycle ticks, two hairline rings, studs, ribbon with the tagline, dates line."""
    c = W / 2
    R = W * 0.46
    fs = W * 0.046
    r_top = R * 0.675
    r_bot = r_top + 0.72 * fs * 0.80
    ticks = []
    for i in range(300):
        major = i % 25 == 0
        ticks.append(dict(i=i, ang=i * 1.2, r0=R * 0.965, r1=R * (0.915 if major else 0.945),
                          w=W * (0.0042 if major else 0.0022), kind="zero" if i == 0 else ("major" if major else "minor")))
    rw, rh, ry = W * 0.84, W * 0.108, W * 0.905
    return dict(
        W=W, c=c, R=R, fs=fs, fs_bot=fs * 0.80, r_top=r_top, r_bot=r_bot,
        ring_outer_r=R * 0.895, ring_inner_r=R * 0.545, ring_w=W * 0.003,
        ticks=ticks, studs=[(c - R * 0.72, c), (c + R * 0.72, c)], stud_r=W * 0.0085,
        mark_r=W * 0.178,
        ribbon=dict(x=(W - rw) / 2, y=ry, w=rw, h=rh, inset=W * 0.012, line_w=W * 0.0028,
                    text_size=rh * 0.285, text_y=ry + rh * 0.62, tracking=rh * 0.012),
        dates=dict(y=ry + rh + W * 0.052, size=W * 0.026, tracking=W * 0.006),
        top=ring_letters(TOP_TEXT, c, r_top, fs, True),
        bottom=ring_letters(BOTTOM_TEXT, c, r_bot, fs * 0.80, False),
    )
