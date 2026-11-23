"""
Study outputs for the ICS Earth Branch mark, detail pass.  [PROPOSAL] -- nothing here is canon.
Stdlib plus ffmpeg (librsvg) only.

    python3 -B "Logo/detail-study/build_study.py"

Writes ONLY into Logo/detail-study/out/.  Geometry comes read-only from Logo/src/ics_brand.py; finishes and layout come
from Logo/detail-study/tools/.  Does not touch svg/, png/, build_brand.py, BRAND_MARK.md, or any canon or design file.
"""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.normpath(os.path.join(HERE, ".."))
for _p in (os.path.join(HERE, "tools"), os.path.join(LOGO, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ics_brand as B   # noqa: E402  (read-only geometry)
import ics_finish as F  # noqa: E402
import seal_art as S    # noqa: E402

OUT = os.path.join(HERE, "out")
CANVAS = 1200
MARK_RC = 380.0         # circle radius of the mark on the 1200-unit canvas
FONT = S.font()


def write(name, svg, png_width):
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(OUT, name + ".svg")
    with open(src, "w", encoding="utf-8") as fh:
        fh.write(svg)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", f"scale={png_width}:-1:flags=lanczos",
                    os.path.join(OUT, name + ".png")], check=True)
    print(f"{name}: svg {os.path.getsize(src) // 1024} KB, png {png_width} px wide")


def seal_svg(uid, theme, ground, title, **kw):
    d, b, info = S.seal(uid, CANVAS / 2, CANVAS / 2, 556.0, theme=theme, region=(0, 0, CANVAS, CANVAS), **kw)
    body = (f'<rect width="{CANVAS}" height="{CANVAS}" fill="{ground}"/>' if ground else "") + b
    return F.doc(CANVAS, CANVAS, body, d, title=title), info


def mark_centred(uid, RC, small, disc, arc):
    """The flat mark with its bounding box centred on the canvas: (defs, body)."""
    xmin, xmax, ymin, ymax = B.mark_bbox(small)
    cx = CANVAS / 2 - RC * (xmin + xmax) / 2
    cy = CANVAS / 2 + RC * (ymin + ymax) / 2
    return S.flat_mark(uid, cx, cy, RC, (0, 0, CANVAS, CANVAS), disc=disc, arc=arc, small=small)


def ladder():
    """Native-size check, 1 px = 1 px: the seal (row 1), the two-colour flat mark (row 2) and the mark in one ink (row 3)
    at 300, 150, 75, 38 and 24 px.  The two mark rows switch to the optical small-size cut in cells under 40 px; the seal
    row keeps the full artwork at every size.  Each artwork is defined once and placed with <use>, so the sheet stays small."""
    sizes = [300, 150, 75, 38, 24]
    rows = (("seal", "SEAL"), ("two", "MARK, TWO COLOURS"), ("ink", "MARK, ONE INK"))
    left, pad, gap, row, foot = 250, 30, 36, 300, 40
    W_ = left + pad + sum(sizes) + gap * (len(sizes) - 1)
    H_ = pad + len(rows) * (row + gap) + foot
    reg = (0, 0, CANVAS, CANVAS)
    defs, body = [], []
    d, inner, _ = S.seal("ls", CANVAS / 2, CANVAS / 2, 556.0, theme="paper", region=reg)
    defs += [d, f'<g id="ls-art">{inner}</g>']
    art = {("seal", False): "ls-art", ("seal", True): "ls-art"}
    for kind in ("two", "ink"):
        for small in (False, True):
            uid = f"lm-{kind}-{int(small)}"
            d, inner = mark_centred(uid, MARK_RC, small, F.BLUE, F.GOLD if kind == "two" else F.BLUE)
            defs += [d, f'<g id="{uid}-art">{inner}</g>']
            art[(kind, small)] = f"{uid}-art"
    ink = "#5A5140"
    size_lab = S.size_for_cap(FONT, 12)
    for r, (kind, label) in enumerate(rows):
        y0 = pad + r * (row + gap)
        lab, _w = FONT.text_path(label, S.size_for_cap(FONT, 11), pad, y0 + row / 2 + 5.5, 0.12 * S.size_for_cap(FONT, 11))
        body.append(f'<path d="{lab}" fill="{ink}"/>')
        x = left
        for s_ in sizes:
            y = y0 + (row - s_) / 2                                 # centred in its row
            body.append(f'<use xlink:href="#{art[(kind, s_ < 40)]}" transform="translate({x:.1f} {y:.1f}) scale({s_ / CANVAS:.5f})"/>')
            if r == len(rows) - 1:
                t, _w = FONT.text_path(f"{s_} px", size_lab, x + s_ / 2, y0 + row + 28, 0.06 * size_lab, "middle")
                body.append(f'<path d="{t}" fill="{ink}"/>')
            x += s_ + gap
    svg = F.doc(W_, H_, f'<rect width="{W_}" height="{H_}" fill="{F.PAPER}"/>' + "".join(body), "".join(defs),
                title="ICS mark and seal at true pixel sizes [PROPOSAL]")
    return svg, W_


def main():
    paper, ip = seal_svg("sp", "paper", F.PAPER, "ICS Earth Branch seal, paper ground [PROPOSAL]")
    night, inn = seal_svg("sn", "night", F.MIDNIGHT, "ICS Earth Branch seal, midnight ground [PROPOSAL]")
    gold, ig = seal_svg("sg", "gold", F.BLUE, "ICS Earth Branch seal, gold foil on Deep Blue [PROPOSAL]")
    write("seal_paper", paper, 1000)
    write("seal_night", night, 1000)
    write("seal_gold_on_blue", gold, 1000)
    flat, _ = seal_svg("sf", "paper", F.PAPER, "ICS Earth Branch seal, paper ground, flat enamel disc [PROPOSAL]", flat=True)
    write("seal_paper_flat", flat, 1000)
    d, b = mark_centred("ink", MARK_RC, False, F.BLUE, F.BLUE)
    ink = F.doc(CANVAS, CANVAS, f'<rect width="{CANVAS}" height="{CANVAS}" fill="{F.PAPER}"/>' + b, d,
                title="ICS mark in one ink [PROPOSAL]")
    write("mark_one_ink", ink, 1000)
    svg, w = ladder()
    write("size_ladder", svg, w)
    for name, inf in (("paper", ip), ("night", inn), ("gold", ig)):
        print(name, inf)


if __name__ == "__main__":
    main()
