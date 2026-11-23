"""
How close do the v2 "ICS" letters come to the knock-out channel, the gold arc and the disc rim?  [PROPOSAL] study tool.

Read-only: imports the mark geometry from Logo/src/ics_brand.py and the v2 plan from tools/seal_v2.py, prints numbers, writes
nothing.

    python3 -B Logo/detail-study/tools/measure_ics.py

Units: the v2 badge is drawn at R = 556 in a 1200-unit canvas, and the mark's circle has radius RC = 0.40 R (PLAN2["rc"]).
Every distance is printed in canvas units and as a fraction of RC.  Positions are in SVG coordinates (y down).

What is measured, against the same geometry the SVG draws:
  - the letters are the outlined glyphs plus a stroke of 0.075 * size (half of that on each side), set as v2 sets them;
  - the gold arc is the polygon from ics_brand.arc_outline();
  - the knock-out channel is that polygon grown by GAP * RC on every side (the SVG mask strokes the polygon with 2 * GAP * RC:
    tools/seal_art._ko_mask here, and src/ics_brand.py lines 94-107; src/ics_seal.py has no mask).
    GAP is the clear margin left on each side of the gold, not the channel's half-width;
  - "ink to channel edge" is the distance from the letters to the part of the disc that stays: negative would mean overlap.
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

import ics_brand as B   # noqa: E402
import seal_art as S    # noqa: E402
import seal_v2 as V     # noqa: E402

R = 556.0
P = V.PLAN2
RC = P["rc"] * R
f = S.font()
size_i = S.size_for_cap(f, P["ics_cap"] * RC)
cap_i = f.cap_height(size_i)
d_i, w_i = f.text_path("ICS", size_i, 0.0, cap_i / 2, 0.07 * size_i, "middle")     # centred on the origin
half_stroke = 0.075 * size_i / 2


def flatten(d, steps=40):
    """SVG path d (absolute M/L/Q/Z) -> a list of dense point lists."""
    out, cur, start = [], None, None
    for cmd, args in re.findall(r"([MLQZ])([^MLQZ]*)", d):
        nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:e-?\d+)?", args)]
        if cmd == "M":
            if cur:
                out.append(cur)
            start = (nums[0], nums[1])
            cur = [start]
        elif cmd == "L":
            cur.append((nums[0], nums[1]))
        elif cmd == "Q":
            (x0, y0), (qx, qy, x1, y1) = cur[-1], nums
            for i in range(1, steps + 1):
                t = i / steps
                u = 1 - t
                cur.append((u * u * x0 + 2 * u * t * qx + t * t * x1, u * u * y0 + 2 * u * t * qy + t * t * y1))
        elif cmd == "Z":
            cur.append(start)
    if cur:
        out.append(cur)
    return out


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def inside(poly, x, y):
    c, j = False, len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def dist_to_poly(poly, x, y):
    """0 inside the polygon, else the distance to its nearest edge."""
    if inside(poly, x, y):
        return 0.0
    return min(seg_dist(x, y, poly[i][0], poly[i][1], poly[(i + 1) % len(poly)][0], poly[(i + 1) % len(poly)][1])
               for i in range(len(poly)))


def densify(poly, step):
    out = []
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        n = max(1, int(math.hypot(bx - ax, by - ay) / step))
        out += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n)]
    return out


def main():
    letters = [densify(c, 0.5) for c in flatten(d_i)]
    pts = [p for c in letters for p in c]
    print(f"R {R:g}  RC {RC:.1f}  'ICS' size {size_i:.1f}  cap {cap_i:.1f}  width {w_i:.1f} = {w_i / RC:.3f} RC  "
          f"half-stroke {half_stroke:.2f}")
    rmax = max(math.hypot(x, y) for x, y in pts) + half_stroke
    print(f"farthest ink from the centre: {rmax:.1f} = {rmax / RC:.3f} RC   (the disc rim is at 1.000 RC)")

    for label, arc, gap_rc in (("FULL cut (what v2 draws at every size)", B.ARC, B.GAP),
                               ("SMALL cut (not used by v2; for reference)", B.ARC_SMALL, B.GAP_SMALL)):
        poly = [(RC * x, -RC * y) for x, y in B.arc_outline(arc)]       # SVG coordinates, centre at (0, 0)
        gap = gap_rc * RC
        dense = densify(poly, 1.0)
        best = (1e9, None)
        for x, y in pts:
            d = 0.0 if inside(poly, x, y) else dist_to_poly(dense, x, y)
            if d < best[0]:
                best = (d, (x, y))
        d_arc = best[0] - half_stroke                  # ink edge to the gold arc
        d_chan = d_arc - gap                           # ink edge to the channel edge (the part of the disc that stays)
        ang = math.degrees(math.atan2(best[1][1], best[1][0]))
        centre_to_arc = dist_to_poly(dense, 0.0, 0.0)
        print(f"\n{label}"
              f"\n  nearest ink to the gold arc: {d_arc:.1f} ({d_arc / RC:.3f} RC)"
              f"\n  nearest ink to the channel edge: {d_chan:.1f} ({d_chan / RC:.3f} RC)   [negative = ink overlaps the channel]"
              f"\n  closest point ({best[1][0]:.1f}, {best[1][1]:.1f}), {ang:.0f} deg from +x"
              f"\n  knock-out margin each side of the gold: {gap:.1f}; centre to the nearest edge of the gold arc: "
              f"{centre_to_arc:.1f} = {centre_to_arc / RC:.3f} RC")
        for name, c in zip("ICS", letters):
            dm = min(0.0 if inside(poly, x, y) else dist_to_poly(dense, x, y) for x, y in c[::3])
            print(f"    {name}: ink to channel edge {dm - half_stroke - gap:.1f} ({(dm - half_stroke - gap) / RC:.3f} RC)")


if __name__ == "__main__":
    main()
