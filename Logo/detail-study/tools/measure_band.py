"""
How much room does the arched "ICS" have on the band of the v2 seal (seal2(..., ics_on="band"))?  [PROPOSAL] study tool.

Read-only: imports tools/seal_v2.py and tools/ics_finish.py, prints numbers, writes nothing.  Stdlib only.

    python3 -B Logo/detail-study/tools/measure_band.py

Units: the v2 badge is drawn at R = 556 in a 1200-unit canvas.  Radii are printed in canvas units and as a fraction of R; angles
in degrees away from straight down.  Everything is measured against the same functions the SVG is drawn with.

What is measured:
  1. The "ICS" ink (the outlined glyphs, plus half of the 0.080 em stroke ring_text paints) against the band it sits in: the hairline
     under the dial (PLAN2["hair"]), the hairline round the bezel (bezel_out + 0.011) and the bezel itself (bezel_out).  The same
     figures for the INTERPLANETARY line, which uses the same cap height, are printed beside them.
  2. The room beside the letters along the band: ink to the start of the hairline, ink to the first planet, last planet and end of the
     hairline to the sparkle, sparkle to the star.  Distances are along the straight line between centres, less both radii, so they
     are a lower bound for the sparkle (its sides are concave).
  3. That the disc is left alone: the last layer of the badge is exactly the mark_layers() output (nothing drawn over the disc), the
     "ics" filter is not defined, and the badge reports the same top-text span as the default layout.

Not measured: how the lettering reads at small sizes (there is no v2 small-size cut yet; see README, Not done).
"""
import math
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.normpath(os.path.join(HERE, "..", ".."))
for _p in (os.path.join(LOGO, "src"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ics_finish as F   # noqa: E402
import seal_art as S     # noqa: E402
import seal_v2 as V      # noqa: E402
from measure_ics import flatten, densify  # noqa: E402  (import runs only module-level set-up; main() is guarded)

R = 556.0
P = V.PLAN2
K = R / 556.0
f = S.font()
mid = (P["hair"] + P["band_in"]) / 2 * R
size_t = S.size_for_cap(f, P["top_cap"] * R)
cap_t = f.cap_height(size_t)
BOLD = 0.080
half_stroke = BOLD * size_t / 2


def dev_from_bottom(x, y):
    """Degrees away from straight down of the point (x, y), centre at the origin, y down."""
    theta = math.degrees(math.atan2(x, -y))          # clockwise from the top
    return abs((theta - 180.0 + 540.0) % 360.0 - 180.0)


def ink_of(svg):
    """(radii, deviations) of the dense outline points of a ring_text() path."""
    d = re.search(r' d="([^"]+)"', svg).group(1)
    pts = [p for c in flatten(d) for p in densify(c, 0.5)]
    return [math.hypot(x, y) for x, y in pts], [dev_from_bottom(x, y) for x, y in pts]


def main():
    ics_svg, ics_deg = F.ring_text(f, "ICS", 0.0, 0.0, mid + cap_t / 2, size_t, P["ics_band_track"], 180.0, top=False,
                                   bold=BOLD, extra="")
    top_svg, top_deg = F.ring_text(f, "INTERPLANETARY", 0.0, 0.0, mid - cap_t / 2, size_t, 0.09, 0.0, top=True,
                                   bold=BOLD, extra="")
    # the tool and the badge must agree on the span, or this file has drifted from seal_v2.py
    _d, _b, info = V.seal2("m", 600.0, 600.0, R, theme="paper", region=(0, 0, 1200, 1200), ics_on="band")
    assert abs(info["ics_band_deg"] - round(ics_deg, 1)) < 1e-9, (info["ics_band_deg"], ics_deg)

    hair = P["hair"] * R
    bez_hair = (P["bezel_out"] + 0.011) * R
    bez = P["bezel_out"] * R
    print(f"R {R:g}  band {P['band_in'] * R:.1f} .. {hair:.1f} = {(P['hair'] - P['band_in']):.3f} R wide, mid-band radius {mid:.1f}")
    print(f"cap height of both lines {cap_t:.1f} = {cap_t / R:.3f} R   (PLAN2 top_cap {P['top_cap']})   size {size_t:.1f}   "
          f"half-stroke {half_stroke:.2f}")
    print(f"tracking: ICS {P['ics_band_track']} em, INTERPLANETARY 0.09 em")
    print(f"angular span of the lettering (advance widths, tracked): ICS {ics_deg:.1f}, INTERPLANETARY {top_deg:.1f}")

    for name, svg in (("ICS", ics_svg), ("INTERPLANETARY", top_svg)):
        rr, dv = ink_of(svg)
        r_lo, r_hi = min(rr) - half_stroke, max(rr) + half_stroke
        print(f"\n{name} ink: radius {r_lo:.1f} .. {r_hi:.1f}  ({r_lo / R:.3f} .. {r_hi / R:.3f} R)")
        print(f"  to the hairline under the dial (outer, {hair:.1f}, 2.0 wide):   {hair - 1.0 * K - r_hi:6.1f}  ({(hair - 1.0 * K - r_hi) / R:.3f} R)")
        print(f"  to the bezel hairline (inner, {bez_hair:.1f}, 1.2 wide):         {r_lo - (bez_hair + 0.6 * K):6.1f}  ({(r_lo - (bez_hair + 0.6 * K)) / R:.3f} R)")
        print(f"  to the bezel edge (inner, {bez:.1f}):                    {r_lo - bez:6.1f}  ({(r_lo - bez) / R:.3f} R)")
        if name == "ICS":
            ink_half = max(dv)
            print(f"  ink reaches {ink_half:.2f} deg either side of straight down (the tracked advance-width span is {ics_deg / 2:.2f})")

    # --- room beside the letters along the band
    ink_half = max(ink_of(ics_svg)[1])
    half = ics_deg / 2.0
    offs, o = [], half + P["band_dot0"]
    for step in (0.0, 11.5, 9.5, 8.0, 6.5):
        o += step
        offs.append(o)
    sizes = (0.0200, 0.0150, 0.0115, 0.0088, 0.0068)
    arc = lambda deg: math.radians(deg) * mid      # length along the mid-band circle   # noqa: E731
    lead, end = half + P["band_lead"], offs[-1] + 5.0
    print("\nalong the band (arc length on the mid-band circle, canvas units; 'gap' = edge to edge)")
    print(f"  ICS ink to the start of the hairline ({lead:.2f} deg):           {arc(lead - ink_half):6.1f}")
    r1 = sizes[0] * R
    print(f"  ICS ink to the first planet (centre {offs[0]:.2f} deg, r {r1:.1f}): gap {arc(offs[0] - ink_half) - r1:6.1f}")
    print(f"  planet centres at {', '.join(f'{x:.1f}' for x in offs)} deg either side of straight down")

    def pos(deg):
        return F.polar(0.0, 0.0, mid, 180.0 + deg)

    spark_deg, spark_r = P["spark_at"], P["spark_r"] * R
    sx, sy = pos(spark_deg)
    lx, ly = pos(offs[-1])
    gap_planet = math.hypot(sx - lx, sy - ly) - spark_r - sizes[-1] * R
    ex, ey = pos(end)
    gap_hair = math.hypot(sx - ex, sy - ey) - spark_r - 0.55 * K
    print(f"  last planet ({offs[-1]:.1f} deg) to the sparkle ({spark_deg:.1f} deg, r {spark_r:.1f}): gap {gap_planet:6.1f}")
    print(f"  end of the hairline ({end:.1f} deg) to the sparkle:                    gap {gap_hair:6.1f}")
    star_deg = 90.0
    ax, ay = F.polar(0.0, 0.0, mid, 270.0)         # the star at 270 deg clockwise from the top; same distance as the one at 90
    bx_, by_ = F.polar(0.0, 0.0, mid, 180.0 + spark_deg)
    star_r = P["star_out"] * R
    print(f"  sparkle to the star ({star_deg:.0f} deg from the top, outer radius {star_r:.1f}): gap "
          f"{math.hypot(ax - bx_, ay - by_) - star_r - spark_r:6.1f}")
    print(f"  INTERPLANETARY's advance span ends {top_deg / 2:.1f} deg from the top and the stars sit at 90, so along the band the "
          f"last letter is {arc(90.0 - top_deg / 2) - star_r:.1f} from a star's edge")

    # --- the disc is left alone
    reg = (0, 0, 1200, 1200)
    d_def, b_def, info_def = V.seal2("m", 600.0, 600.0, R, theme="paper", region=reg)
    d_band, b_band, info_band = V.seal2("m", 600.0, 600.0, R, theme="paper", region=reg, ics_on="band")
    md, mb = S.mark_layers("mm", 600.0, 600.0, P["rc"] * R, reg, disc="blue", ground_dark=False, flat=False)
    print("\nthe disc")
    print(f"  last layer of the band badge is exactly mark_layers() output:      {b_band.endswith(mb)}")
    print(f"  the default badge holds it too, followed by the 'ICS' group:       {mb in b_def and not b_def.endswith(mb)}")
    print(f"  the 'ics' filter is defined in the band badge / the default badge: {'m-ics' in d_band} / {'m-ics' in d_def}")
    print(f"  top-text span, band badge / default badge:                         {info_band['top_deg']} / {info_def['top_deg']}")
    print(f"  mark_layers defs contained unchanged in both:                      {md in d_band and md in d_def}")


if __name__ == "__main__":
    main()
