"""
v2 seal pieces for the ICS Earth Branch mark.  [PROPOSAL] -- nothing here is canon.  Stdlib plus ffmpeg (librsvg) only.

    python3 -B Logo/detail-study/build_seal_v2.py            # everything
    python3 -B Logo/detail-study/build_seal_v2.py paper      # just one piece (names below)

    seal2_paper       the badge on a paper ground
    seal2_night       the badge on a midnight ground (cream disc, navy "ICS")
    seal2_steel       as seal2_paper in steel and enamel instead of polished gold; smooth sheen, no brush texture (the finish
                      question is still open; the mark's own arc stays canon Warm Gold)
    seal2_corporate   as seal2_paper with "CORPORATE SOLUTIONS" arched underneath instead of the planet row (canon-quoted
                      wording, but wording the author did not ask for)
    seal2_ladder      native-size check at 300 / 150 / 75 / 38 / 24 px
    seal2_band        the alternate: "ICS" arched along the bottom of the band, as big as INTERPLANETARY, and the disc left
                      clean (Doc 2.32:29 "a clean, unbroken circle", 2.32:5 "There is no ICS corporate mark").  Added under the
                      author's "feel free to choose whatever let's get it done"; the middle-of-the-disc pieces stay the default
    seal2_band_night  the same on the midnight ground

Writes ONLY into Logo/detail-study/out/ and only files named seal2_*.  Does not touch v1 outputs, svg/, png/, or any canon,
design or generator file.
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

import ics_finish as F    # noqa: E402
import seal_art as S      # noqa: E402
import seal_v2 as V       # noqa: E402

OUT = os.path.join(HERE, "out")
CANVAS = 1200
FONT = S.font()


def write(name, svg, png_width):
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(OUT, name + ".svg")
    with open(src, "w", encoding="utf-8") as fh:
        fh.write(svg)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", f"scale={png_width}:-1:flags=lanczos",
                    os.path.join(OUT, name + ".png")], check=True)
    print(f"{name}: svg {os.path.getsize(src) // 1024} KB, png {png_width} px wide")


def piece(uid, theme, ground, title, **kw):
    d, b, info = V.seal2(uid, CANVAS / 2, CANVAS / 2, 556.0, theme=theme, region=(0, 0, CANVAS, CANVAS), **kw)
    body = f'<rect width="{CANVAS}" height="{CANVAS}" fill="{ground}"/>' + b
    return F.doc(CANVAS, CANVAS, body, d, title=title), info


def ladder():
    """Native-size check, 1 px = 1 px, of the v2 badge on paper and on midnight."""
    sizes = [300, 150, 75, 38, 24]
    left, pad, gap, row, foot = 250, 30, 36, 300, 40
    W_ = left + pad + sum(sizes) + gap * (len(sizes) - 1)
    rows = (("PAPER", "paper", F.PAPER), ("MIDNIGHT", "night", F.MIDNIGHT))
    H_ = pad + len(rows) * (row + gap) + foot
    reg = (0, 0, CANVAS, CANVAS)
    defs, body = [], []
    ink = "#5A5140"
    size_lab = S.size_for_cap(FONT, 12)
    for r, (label, theme, ground) in enumerate(rows):
        uid = f"l2{theme[0]}"
        d, inner, _ = V.seal2(uid, CANVAS / 2, CANVAS / 2, 556.0, theme=theme, region=reg)
        defs += [d, f'<g id="{uid}-art">{inner}</g>']
        y0 = pad + r * (row + gap)
        body.append(f'<rect x="{left - 14}" y="{y0}" width="{W_ - left + 14 - pad + 14}" height="{row}" fill="{ground}"/>')
        lab, _w = FONT.text_path(label, S.size_for_cap(FONT, 11), pad, y0 + row / 2 + 5.5, 0.12 * S.size_for_cap(FONT, 11))
        body.append(f'<path d="{lab}" fill="{ink}"/>')
        x = left
        for s_ in sizes:
            y = y0 + (row - s_) / 2
            body.append(f'<use xlink:href="#{uid}-art" transform="translate({x:.1f} {y:.1f}) scale({s_ / CANVAS:.5f})"/>')
            if r == len(rows) - 1:
                t, _w = FONT.text_path(f"{s_} px", size_lab, x + s_ / 2, y0 + row + 28, 0.06 * size_lab, "middle")
                body.append(f'<path d="{t}" fill="{ink}"/>')
            x += s_ + gap
    svg = F.doc(W_, H_, f'<rect width="{W_}" height="{H_}" fill="{F.PAPER}"/>' + "".join(body), "".join(defs),
                title="ICS v2 seal at true pixel sizes [PROPOSAL]")
    return svg, W_


def main(which):
    todo = which or ["paper", "night", "steel", "corporate", "ladder", "band", "band_night"]
    if "paper" in todo:
        svg, info = piece("p2", "paper", F.PAPER, "ICS seal v2, paper ground [PROPOSAL]")
        write("seal2_paper", svg, 1000)
        print("paper", info)
    if "night" in todo:
        svg, info = piece("n2", "night", F.MIDNIGHT, "ICS seal v2, midnight ground [PROPOSAL]")
        write("seal2_night", svg, 1000)
        print("night", info)
    if "steel" in todo:
        svg, info = piece("s2", "paper", F.PAPER, "ICS seal v2, steel [PROPOSAL]", metal="steel")
        write("seal2_steel", svg, 1000)
        print("steel", info)
    if "corporate" in todo:
        svg, info = piece("c2", "paper", F.PAPER, "ICS seal v2, second line CORPORATE SOLUTIONS [PROPOSAL]",
                          bottom="CORPORATE SOLUTIONS")
        write("seal2_corporate", svg, 1000)
        print("corporate", info)
    if "ladder" in todo:
        svg, w = ladder()
        write("seal2_ladder", svg, w)
    if "band" in todo:
        svg, info = piece("b2", "paper", F.PAPER, "ICS seal v2, ICS on the band, disc clean [PROPOSAL]", ics_on="band")
        write("seal2_band", svg, 1000)
        print("band", info)
    if "band_night" in todo:
        svg, info = piece("bn2", "night", F.MIDNIGHT, "ICS seal v2, ICS on the band, disc clean, midnight [PROPOSAL]", ics_on="band")
        write("seal2_band_night", svg, 1000)
        print("band_night", info)


if __name__ == "__main__":
    main(sys.argv[1:])
