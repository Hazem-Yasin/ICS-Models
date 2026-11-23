"""
Stdlib-only TrueType outliner: font file -> SVG path data.  [PROPOSAL tooling for the ICS logo-detail study]

Why: the brand kit's ring lettering was set with SVG <text>, one letter at a time, using an *estimated* advance table, so
spacing was uneven and depended on whichever renderer/font happened to be installed.  This reads the real glyph outlines
and advance widths out of the OFL fonts already in Logo/fonts/ (Varela Round is a static face), so ring text is exact,
fontless and identical in every renderer.

Supports simple + composite 'glyf' glyphs, cmap formats 0/4/6/12, hmtx.  No kerning (GPOS is ignored: the ring text is
tracked wide anyway).  Output coordinates: SVG convention (y down), baseline at y = 0, scaled to `size` px per em.
"""
import struct


class TTF:
    def __init__(self, path):
        d = open(path, "rb").read()
        self.d = d
        _, n = struct.unpack(">IH", d[:6])
        self.tables = {}
        for i in range(n):
            tag, _cs, off, ln = struct.unpack(">4sIII", d[12 + 16 * i:28 + 16 * i])
            self.tables[tag.decode("latin1")] = (off, ln)
        head = self.tables["head"][0]
        self.upm = struct.unpack(">H", d[head + 18:head + 20])[0]
        self.loca_fmt = struct.unpack(">h", d[head + 50:head + 52])[0]
        maxp = self.tables["maxp"][0]
        self.num_glyphs = struct.unpack(">H", d[maxp + 4:maxp + 6])[0]
        hhea = self.tables["hhea"][0]
        self.ascent, self.descent = struct.unpack(">hh", d[hhea + 4:hhea + 8])
        self.num_hm = struct.unpack(">H", d[hhea + 34:hhea + 36])[0]
        self._loca()
        self._cmap()
        self._hmtx()
        self._cache = {}

    # ---- tables ---------------------------------------------------------------------------------------------------
    def _loca(self):
        off, ln = self.tables["loca"]
        d = self.d
        n = self.num_glyphs + 1
        if self.loca_fmt == 0:
            self.loca = [2 * v for v in struct.unpack(">%dH" % n, d[off:off + 2 * n])]
        else:
            self.loca = list(struct.unpack(">%dI" % n, d[off:off + 4 * n]))
        self.glyf = self.tables["glyf"][0]

    def _hmtx(self):
        off, _ = self.tables["hmtx"]
        d = self.d
        self.adv = []
        for i in range(self.num_hm):
            a, _lsb = struct.unpack(">Hh", d[off + 4 * i:off + 4 * i + 4])
            self.adv.append(a)

    def _cmap(self):
        off, _ = self.tables["cmap"]
        d = self.d
        _ver, num = struct.unpack(">HH", d[off:off + 4])
        recs = []
        for i in range(num):
            pid, eid, so = struct.unpack(">HHI", d[off + 4 + 8 * i:off + 12 + 8 * i])
            recs.append((pid, eid, off + so))
        pref = [(3, 10), (0, 4), (0, 6), (3, 1), (0, 3), (0, 2), (0, 1), (0, 0)]
        pick = None
        for pe in pref:
            for pid, eid, so in recs:
                if (pid, eid) == pe:
                    pick = so
                    break
            if pick:
                break
        if pick is None:
            pick = recs[0][2]
        self.cmap = self._parse_cmap(pick)

    def _parse_cmap(self, o):
        d = self.d
        fmt = struct.unpack(">H", d[o:o + 2])[0]
        m = {}
        if fmt == 0:
            for c in range(256):
                g = d[o + 6 + c]
                if g:
                    m[c] = g
        elif fmt == 4:
            segx2 = struct.unpack(">H", d[o + 6:o + 8])[0]
            sc = segx2 // 2
            p = o + 14
            ends = struct.unpack(">%dH" % sc, d[p:p + segx2])
            p += segx2 + 2
            starts = struct.unpack(">%dH" % sc, d[p:p + segx2])
            p += segx2
            deltas = struct.unpack(">%dh" % sc, d[p:p + segx2])
            p += segx2
            ro_pos = p
            ros = struct.unpack(">%dH" % sc, d[p:p + segx2])
            for i in range(sc):
                for c in range(starts[i], ends[i] + 1):
                    if c == 0xFFFF:
                        continue
                    if ros[i] == 0:
                        g = (c + deltas[i]) & 0xFFFF
                    else:
                        gp = ro_pos + 2 * i + ros[i] + 2 * (c - starts[i])
                        g = struct.unpack(">H", d[gp:gp + 2])[0]
                        if g:
                            g = (g + deltas[i]) & 0xFFFF
                    if g:
                        m[c] = g
        elif fmt == 6:
            first, cnt = struct.unpack(">HH", d[o + 6:o + 10])
            for i in range(cnt):
                g = struct.unpack(">H", d[o + 10 + 2 * i:o + 12 + 2 * i])[0]
                if g:
                    m[first + i] = g
        elif fmt == 12:
            ng = struct.unpack(">I", d[o + 12:o + 16])[0]
            for i in range(ng):
                s, e, g = struct.unpack(">III", d[o + 16 + 12 * i:o + 28 + 12 * i])
                for c in range(s, e + 1):
                    m[c] = g + (c - s)
        else:
            raise ValueError("unsupported cmap format %d" % fmt)
        return m

    # ---- glyph outlines -------------------------------------------------------------------------------------------
    def gid(self, ch):
        return self.cmap.get(ord(ch), 0)

    def advance_units(self, ch):
        g = self.gid(ch)
        return self.adv[g] if g < len(self.adv) else self.adv[-1]

    def _contours(self, gid, depth=0):
        """Contours of one glyph in font units: list of lists of (x, y, on_curve)."""
        if gid in self._cache:
            return self._cache[gid]
        d = self.d
        a, b = self.loca[gid], self.loca[gid + 1]
        if a == b or depth > 6:
            return []
        g = self.glyf + a
        nc = struct.unpack(">h", d[g:g + 2])[0]
        p = g + 10
        out = []
        if nc >= 0:
            ends = struct.unpack(">%dH" % nc, d[p:p + 2 * nc]) if nc else ()
            p += 2 * nc
            ilen = struct.unpack(">H", d[p:p + 2])[0]
            p += 2 + ilen
            npts = (ends[-1] + 1) if nc else 0
            flags = []
            while len(flags) < npts:
                f = d[p]
                p += 1
                flags.append(f)
                if f & 8:
                    r = d[p]
                    p += 1
                    flags.extend([f] * r)
            xs, v = [], 0
            for f in flags:
                if f & 2:
                    dx = d[p]
                    p += 1
                    v += dx if f & 16 else -dx
                elif not (f & 16):
                    v += struct.unpack(">h", d[p:p + 2])[0]
                    p += 2
                xs.append(v)
            ys, v = [], 0
            for f in flags:
                if f & 4:
                    dy = d[p]
                    p += 1
                    v += dy if f & 32 else -dy
                elif not (f & 32):
                    v += struct.unpack(">h", d[p:p + 2])[0]
                    p += 2
                ys.append(v)
            s = 0
            for e in ends:
                out.append([(xs[i], ys[i], bool(flags[i] & 1)) for i in range(s, e + 1)])
                s = e + 1
        else:
            while True:
                fl, gi = struct.unpack(">HH", d[p:p + 4])
                p += 4
                if fl & 1:
                    a1, a2 = struct.unpack(">hh", d[p:p + 4])
                    p += 4
                else:
                    a1, a2 = struct.unpack(">bb", d[p:p + 2])
                    p += 2
                dx, dy = (a1, a2) if fl & 2 else (0, 0)
                m = [1.0, 0.0, 0.0, 1.0]
                if fl & 8:
                    s = struct.unpack(">h", d[p:p + 2])[0] / 16384.0
                    p += 2
                    m = [s, 0.0, 0.0, s]
                elif fl & 0x40:
                    sx, sy = struct.unpack(">hh", d[p:p + 4])
                    p += 4
                    m = [sx / 16384.0, 0.0, 0.0, sy / 16384.0]
                elif fl & 0x80:
                    t = struct.unpack(">hhhh", d[p:p + 8])
                    p += 8
                    m = [t[0] / 16384.0, t[1] / 16384.0, t[2] / 16384.0, t[3] / 16384.0]
                for c in self._contours(gi, depth + 1):
                    out.append([(m[0] * x + m[2] * y + dx, m[1] * x + m[3] * y + dy, on) for x, y, on in c])
                if not fl & 0x20:
                    break
        self._cache[gid] = out
        return out

    def path_d(self, ch, size, dx=0.0, dy=0.0, embolden=0.0):
        """SVG path data for one character, baseline at y=dy, left edge of the advance box at x=dx. size = px per em.
        Returns ('', advance_px) for blank glyphs."""
        k = size / self.upm
        g = self.gid(ch)
        adv = self.advance_units(ch) * k
        cs = self._contours(g)
        if not cs:
            return "", adv

        def T(x, y):
            return "%.2f,%.2f" % (dx + x * k, dy - y * k)

        parts = []
        for pts in cs:
            n = len(pts)
            if n < 2:
                continue
            if pts[0][2]:
                start, seq = pts[0], pts[1:]
            elif pts[-1][2]:
                start, seq = pts[-1], pts[:-1]
            else:
                start = ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2, True)
                seq = pts
            parts.append("M" + T(start[0], start[1]))
            off = None
            for x, y, on in seq:
                if on:
                    if off is None:
                        parts.append("L" + T(x, y))
                    else:
                        parts.append("Q%s %s" % (T(off[0], off[1]), T(x, y)))
                        off = None
                else:
                    if off is not None:
                        mx, my = (off[0] + x) / 2, (off[1] + y) / 2
                        parts.append("Q%s %s" % (T(off[0], off[1]), T(mx, my)))
                    off = (x, y)
            if off is not None:
                parts.append("Q%s %s" % (T(off[0], off[1]), T(start[0], start[1])))
            parts.append("Z")
        return "".join(parts), adv

    def path_xf(self, ch, size, tx, ty, rot_deg=0.0, ox=0.0, bold=0.0):
        """Like path_d, but the glyph is placed with a rotation: glyph-local point (ox + x*k, -y*k) is rotated clockwise by
        rot_deg about the local origin and then moved to (tx, ty).  Coordinates are baked into the path, so a gradient in
        userSpaceOnUse is sampled in canvas space (not in each letter's rotated frame).  Returns (d, advance_px)."""
        import math
        k = size / self.upm
        g = self.gid(ch)
        adv = self.advance_units(ch) * k
        cs = self._contours(g)
        if not cs:
            return "", adv
        c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))

        def T(x, y):
            lx, ly = ox + x * k, -y * k
            return "%.2f,%.2f" % (tx + lx * c - ly * s, ty + lx * s + ly * c)

        parts = []
        for pts in cs:
            if len(pts) < 2:
                continue
            if pts[0][2]:
                start, seq = pts[0], pts[1:]
            elif pts[-1][2]:
                start, seq = pts[-1], pts[:-1]
            else:
                start = ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2, True)
                seq = pts
            parts.append("M" + T(start[0], start[1]))
            off = None
            for x, y, on in seq:
                if on:
                    if off is None:
                        parts.append("L" + T(x, y))
                    else:
                        parts.append("Q%s %s" % (T(off[0], off[1]), T(x, y)))
                        off = None
                else:
                    if off is not None:
                        parts.append("Q%s %s" % (T(off[0], off[1]), T((off[0] + x) / 2, (off[1] + y) / 2)))
                    off = (x, y)
            if off is not None:
                parts.append("Q%s %s" % (T(off[0], off[1]), T(start[0], start[1])))
            parts.append("Z")
        return "".join(parts), adv

    def cap_height(self, size):
        """Height of capital H in px (measured from its outline)."""
        cs = self._contours(self.gid("H"))
        top = max(y for c in cs for _x, y, _o in c)
        return top * size / self.upm

    def text_width(self, s, size, tracking=0.0):
        k = size / self.upm
        return sum(self.advance_units(c) * k for c in s) + tracking * max(len(s) - 1, 0)

    def text_path(self, s, size, x=0.0, y=0.0, tracking=0.0, anchor="start"):
        """One path d for a straight line of text. anchor: start | middle | end. Returns (d, width)."""
        w = self.text_width(s, size, tracking)
        cx = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0.0)
        ds = []
        for c in s:
            d, a = self.path_d(c, size, cx, y)
            ds.append(d)
            cx += a + tracking
        return "".join(ds), w


if __name__ == "__main__":
    import sys
    f = TTF(sys.argv[1])
    print("upm", f.upm, "glyphs", f.num_glyphs, "cap(100px)=%.1f" % f.cap_height(100))
    for ch in "ICS EARTH BRANCH ·’#349":
        print(repr(ch), f.gid(ch), "%.1f" % (f.advance_units(ch) * 100 / f.upm))
