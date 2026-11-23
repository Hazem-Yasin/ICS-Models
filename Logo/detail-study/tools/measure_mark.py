"""
Numbers quoted in README.md, so a reader can reproduce them.  [PROPOSAL]  Read-only: imports Logo/src/ics_brand.py, prints
to the terminal, writes nothing.  Stdlib only.

    python3 -B Logo/detail-study/tools/measure_mark.py

1. How much of the circle's rim the knock-out channel removes.  Doc 2.32:29 says "A clean, unbroken circle."  The channel is
   the arc polygon grown by GAP (ics_brand.GAP / GAP_SMALL), exactly as the SVG mask in ics_brand.mark_group draws it.  A rim
   sample counts as removed if it lies inside that grown polygon.  Resolution: 360 / SAMPLES degrees.  The same count is
   repeated with the margin set to 0, which is what BRAND_MARK.md:95 offers as the fix: the arc's own body still covers the rim.
2. Where the arc comes to rest, in degrees from straight down (negative = left of down), and how steeply it crosses the rim.
   BRAND_MARK.md:10 says the arc rests at "the base (lower right)".
3. The bounding box of the whole mark, in circle radii.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "src"))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import ics_brand as B  # noqa: E402  (read-only)

SAMPLES = 1440


def inside(poly, x, y):
    """Ray-casting point-in-polygon."""
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def edge_dist2(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    qx, qy = ax + t * dx, ay + t * dy
    return (px - qx) ** 2 + (py - qy) ** 2


def removed(poly, gap, x, y):
    if inside(poly, x, y):
        return True
    g2 = gap * gap
    for i in range(len(poly)):
        a, b = poly[i - 1], poly[i]
        if edge_dist2(x, y, a[0], a[1], b[0], b[1]) <= g2:
            return True
    return False


def rim_cut(arc, gap):
    poly = B.arc_outline(arc)
    flags = []
    for k in range(SAMPLES):
        a = 2 * math.pi * k / SAMPLES
        flags.append(removed(poly, gap, math.cos(a), math.sin(a)))
    total = 360.0 * sum(flags) / SAMPLES
    if all(flags) or not any(flags):
        return total, []
    start = flags.index(False)                         # rotate so no run wraps past the end of the list
    runs, k = [], 0
    while k < SAMPLES:
        idx = (start + k) % SAMPLES
        if flags[idx]:
            j = k
            while j < SAMPLES and flags[(start + j) % SAMPLES]:
                j += 1
            runs.append((360.0 * ((start + k) % SAMPLES) / SAMPLES, 360.0 * (j - k) / SAMPLES))
            k = j
        else:
            k += 1
    return total, runs


def rest_and_crossing(arc):
    """Centreline end point and the angle between the arc and the rim where the centreline crosses r = 1."""
    end = math.radians(arc["th1"])
    x, y = arc["r1"] * math.cos(end), arc["r1"] * math.sin(end)
    from_down = math.degrees(math.atan2(x, -y))        # 0 = straight down, negative = left of down
    pts = B.centerline(arc, n=4800)
    cross = None
    for i in range(1, len(pts)):
        r0, r1 = math.hypot(pts[i - 1][0], pts[i - 1][1]), math.hypot(pts[i][0], pts[i][1])
        if (r0 - 1.0) * (r1 - 1.0) <= 0 and r0 != r1:
            u = (1.0 - r0) / (r1 - r0)
            cx = pts[i - 1][0] + u * (pts[i][0] - pts[i - 1][0])
            cy = pts[i - 1][1] + u * (pts[i][1] - pts[i - 1][1])
            tx, ty = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
            rim_tx, rim_ty = -cy, cx                   # tangent of the unit circle at that point
            ang = math.degrees(math.acos(abs(tx * rim_tx + ty * rim_ty) / (math.hypot(tx, ty) * math.hypot(rim_tx, rim_ty))))
            cross = (math.degrees(math.atan2(cy, cx)), ang)
            break
    return (x, y), from_down, cross


def main():
    for name, arc, gap in (("full", B.ARC, B.GAP), ("small", B.ARC_SMALL, B.GAP_SMALL)):
        total, runs = rim_cut(arc, gap)
        (x, y), down, cross = rest_and_crossing(arc)
        bb = B.mark_bbox(name == "small")
        print(f"[{name}] knock-out margin each side of the gold {gap} R, arc widths {arc['w0']}/{arc['wm']}/{arc['w1']} R")
        print(f"  rim removed by the channel: {total:.1f} of 360 degrees ({SAMPLES} samples, +/-{360.0 / SAMPLES / 2:.2f})")
        for s, span in runs:
            print(f"    cut starts at {s:6.2f} deg (0 = +x, counter-clockwise) and spans {span:.2f} deg")
        total0, runs0 = rim_cut(arc, 0.0)              # margin set to 0: only the arc's own body is left on the rim
        print(f"  rim removed with the margin set to 0: {total0:.2f} of 360 degrees")
        for s, span in runs0:
            print(f"    cut starts at {s:6.2f} deg and spans {span:.2f} deg")
        print(f"  arc rests at centreline ({x:+.3f}, {y:+.3f}) R = {down:+.1f} deg from straight down (negative = left)")
        if cross:
            print(f"  centreline crosses the rim at {cross[0]:.1f} deg, at {cross[1]:.1f} deg to the rim tangent")
        print(f"  bounding box (xmin, xmax, ymin, ymax) in R: {tuple(round(v, 3) for v in bb)}")


if __name__ == "__main__":
    main()
