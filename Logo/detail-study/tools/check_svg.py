"""
Static checks for the study SVGs.  Stdlib only.

    python3 -B Logo/detail-study/tools/check_svg.py Logo/detail-study/out/*.svg

For each file: every id is unique, every url(#id) reference resolves, and it resolves to the right kind of element
(fill/stroke -> gradient or pattern, clip-path -> clipPath, mask -> mask, filter -> filter), every <use> target exists,
the root has a viewBox, and the file parses as XML.  A duplicate id is the failure that matters most: librsvg resolves
the FIRST element with the id, so a gradient and a clipPath sharing an id silently drops the clip.
Exit status 1 if any file fails.
"""
import re
import sys
import xml.etree.ElementTree as ET

KIND = {
    "fill": {"linearGradient", "radialGradient", "pattern"},
    "stroke": {"linearGradient", "radialGradient", "pattern"},
    "clip-path": {"clipPath"},
    "mask": {"mask"},
    "filter": {"filter"},
}
URL = re.compile(r"url\(#([^)]+)\)")


def local(tag):
    return tag.rsplit("}", 1)[-1]


def check(path):
    problems = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        return [f"XML parse error: {e}"]
    if "viewBox" not in root.attrib:
        problems.append("root <svg> has no viewBox (librsvg crops it)")
    ids = {}
    for el in root.iter():
        i = el.attrib.get("id")
        if i is None:
            continue
        ids.setdefault(i, []).append(local(el.tag))
    for i, kinds in ids.items():
        if len(kinds) > 1:
            problems.append(f"duplicate id '{i}': {', '.join(kinds)}")
    for el in root.iter():
        for attr, ok in KIND.items():
            v = el.attrib.get(attr)
            if not v:
                continue
            for ref in URL.findall(v):
                if ref not in ids:
                    problems.append(f"{attr}=url(#{ref}) on <{local(el.tag)}> does not resolve")
                elif ids[ref][0] not in ok:
                    problems.append(f"{attr}=url(#{ref}) on <{local(el.tag)}> resolves to <{ids[ref][0]}>")
        href = el.attrib.get("{http://www.w3.org/1999/xlink}href") or el.attrib.get("href")
        if local(el.tag) == "use" and href:
            if href[1:] not in ids:
                problems.append(f"<use> target {href} does not resolve")
    return problems


def main(paths):
    bad = 0
    for p in paths:
        probs = check(p)
        name = p.replace("\\", "/").rsplit("/", 1)[-1]
        if probs:
            bad += 1
            print(f"FAIL {name}")
            for x in probs[:12]:
                print("   ", x)
            if len(probs) > 12:
                print(f"    ... and {len(probs) - 12} more")
        else:
            print(f"ok   {name}")
    print(f"{len(paths) - bad}/{len(paths)} files clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
