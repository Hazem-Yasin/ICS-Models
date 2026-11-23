# ICS logo detail study  `[PROPOSAL]`

**Canon wins.** Doc 2.32 (`ICS-Writing/canon/documents/2.32 — Brand Identity The Logo.md`) fixes the mark. This folder does not redraw it: the circle and the arc are read, unchanged, from `Logo/src/ics_brand.py`. What it proposes is the detail around the mark: a seal, metal and enamel finishes, true-size checks, and four of the objects canon names (the Level 1 wall, the Tier 3 badge, the welcome folder and the keychain; the bottle, badge holder, handbook and brochure, UI screens and weapon logos are under Not done). **Nothing here is canon.** Every `<title>` carries `[PROPOSAL…]`. It edits nothing in `svg/`, `png/`, `build_brand.py`, `BRAND_MARK.md`, the canon or the Writing kit.

## Why it exists

The ask: the ICS logo looks bland beside the emblems of the corporations in games such as *Fallout*, and the answer should come from the ICS-Writing lore. The lore presents the logo as friendly ("clean, friendly", on the handbook cover, 2.20:3) and the wordmark as "approachable, warm" with "no sharp angles" (2.32:48, a rule about the wordmark, not the mark; "friendly" is not a 2.32 word). The menace sits in the restricted versions of the same document (the arc as a fishhook: 2.32:164 in the PTKW addendum, and 2.32:247 under "The Arc Is the Hook", heading at 245). So the detail added here is craft (metal, enamel, lettering, ticks, rays), not menace, and no piece shows the arc on its own.

## Direction given

The author answered three of four questions on 2026-11-12. Their words, as typed:

- **Base mark:** *yeah but if we can more details, for example BONES coffee company from fallout and poseidon energy also from fallout and the brotherhood of steel*
- **Style:** *Retro-futurist, more Fallout*
- **Seal text:** *it should have the ICS text written in the middle and on top of it it should say Interplanetary, and remove the "because you are worth the investment"*
- **Finish** (brushed metal against polished gold and enamel): not answered.

My reading, not confirmed: keep the canon mark and add detail in the manner of those emblems; "ICS" in the middle, "INTERPLANETARY" arched on top, the bottom tagline gone. The answers do not say where the canon arc sits once "ICS" is in the middle. My lookup through fallout.wiki's API did not turn up a BONES coffee emblem, so v2 takes nothing from it. The cues taken from the other two are general motifs, read from reference images that stay outside the repo: a broad ring, arched lettering, stars, a thin inner ring and a tilted orbit (Poseidon Energy); cogs and rivets (Brotherhood of Steel). No emblem is copied or traced, and the sawtooth gear is not used.

## Files (`out/`)

Open the SVGs in a browser. The PNGs are previews of the same SVGs, drawn by librsvg; the five v2 SVGs were also rendered in headless Chrome (see Limits).

**v1, the first pass** (made before the author's answers; its seals carry the tagline, which the author has since asked to drop):

| File | Shows | PNG px | SVG KiB |
|---|---|---|---|
| `seal_paper` | The seal on a paper ground, domed navy-enamel disc | 1000×1000 | 432.1 |
| `seal_paper_flat` | Same, flat enamel disc (`flat=True`) | 1000×1000 | 431.9 |
| `seal_night` | Midnight ground, cream disc | 1000×1000 | 431.9 |
| `seal_gold_on_blue` | Gold foil only, on Deep Blue (the stamping or embossing master) | 1000×1000 | 415.4 |
| `mark_one_ink` | The mark in one ink (Deep Blue on paper) | 1000×1000 | 27.7 |
| `size_ladder` | Seal, two-colour mark and one-ink mark at 300/150/75/38/24 px, 1 px = 1 px | 1011×1078 | 580.4 |
| `plaque_steel` | Level 1 south wall, one brushed metal | 1400×875 | 53.7 |
| `plaque_two_tone` | Same wall, Deep Blue and Warm Gold brushed metal | 1400×875 | 53.7 |
| `badge_header` | Top 16 mm of the Tier 3 card | 1198×224 | 35.1 |
| `folder_cover` | Onboarding folder, gold seal embossed | 1000×1269 | 468.2 |
| `keychain` | Seal side and smooth side | 1500×988 | 495.4 |

**v2, the retro-futurist pass** (after the answers: "ICS" in the middle, "INTERPLANETARY" arched on top, no tagline):

| File | Shows | PNG px | SVG KiB |
|---|---|---|---|
| `seal2_paper` | The v2 badge on a paper ground: navy-enamel disc, polished gold | 1000×1000 | 151.6 |
| `seal2_night` | Midnight ground, cream disc, navy "ICS" | 1000×1000 | 151.4 |
| `seal2_steel` | Steel and enamel instead of polished gold: smooth sheen, no brush texture; the mark's arc stays canon Warm Gold | 1000×1000 | 151.5 |
| `seal2_corporate` | As `seal2_paper` with "CORPORATE SOLUTIONS" arched underneath in place of the planet row | 1000×1000 | 162.6 |
| `seal2_ladder` | v2 on paper and on midnight at 300/150/75/38/24 px, 1 px = 1 px | 1011×742 | 327.9 |

Totals: v1 PNG 10,006,708 B (9.54 MiB), SVG 3,507,868 B (3.35 MiB); v2 PNG 4,310,345 B (4.11 MiB), SVG 967,732 B (0.92 MiB); all of `out/`: PNG 14,317,053 B (13.65 MiB), SVG 4,475,600 B (4.27 MiB). All 16 SVGs are self-contained: 0 `<text>`, 0 `<image>`, 0 `<script>`, 0 external references. Lettering is outlined to paths, because librsvg ignores `<textPath>` and a file should not depend on installed fonts. `*.png` is Git LFS in `ICS-Models/.gitattributes`; the PNGs rebuild from the SVGs, so whether to commit them at all is open (nothing is staged; if committed, the 16 PNGs would add 13.65 MiB of LFS objects).

**Ladder labels are cell widths.** At the "24 px" cell the drawn mark is about 17.8 px wide and the seal about 22.2 px (300 → 217.3 / 278.0; 150 → 108.6 / 139.0; 75 → 54.3 / 69.5; 38 → 28.2 / 35.2). Cells under 40 px use the small cut. The seal row reuses one artwork at every size.

**The v2 ladder** draws each badge once and scales it into the cell, so the "24 px" cell holds a 22.2 px badge. Sizes in px, from the code (R = 556 in a 1200 canvas):

| Cell | Badge | Mark circle | Mark with arc | "ICS" cap height | "INTERPLANETARY" cap height |
|---|---|---|---|---|---|
| 300 | 278.0 | 111.2 | 127.2 | 25.6 | 18.1 |
| 150 | 139.0 | 55.6 | 63.6 | 12.8 | 9.0 |
| 75 | 69.5 | 27.8 | 31.8 | 6.4 | 4.5 |
| 38 | 35.2 | 14.1 | 16.1 | 3.2 | 2.3 |
| 24 | 22.2 | 8.9 | 10.2 | 2.0 | 1.4 |

By eye in `seal2_ladder.png`: the arched word is readable at 300 and 150 and not at 75 and below; "ICS" is small but visible at 75 and not legible at 38 or 24. The v2 mark is drawn in the full cut at every size. Against the 32 px switch to the small cut (`BRAND_MARK.md:24–25`; `ics_brand.py:29` says "marks rendered under ~32 px"), the 75 px cell holds a mark 31.8 px wide, just under the switch, and the 38 and 24 px cells hold marks 16.1 and 10.2 px wide, well under it; the 24 px cell is also under the 16 px floor. A v2 small-size cut is not built.

## Rebuild

From the `ICS-Models` root. Python 3 (stdlib only) and ffmpeg with librsvg.

```
python3 -B Logo/detail-study/build_study.py                      # 6 pieces (12 files): the four seals, mark_one_ink, size_ladder
python3 -B Logo/detail-study/build_apps.py [plaque|header|folder|keychain]   # 5 pieces (10 files; plaque makes two); no argument builds all
python3 -B Logo/detail-study/build_seal_v2.py [paper|night|steel|corporate|ladder]   # 5 pieces (10 files); no argument builds all
python3 -B Logo/detail-study/tools/check_svg.py Logo/detail-study/out/*.svg   # XML, viewBox, duplicate ids, url(#…) and <use> targets
python3 -B Logo/detail-study/tools/measure_mark.py              # the numbers quoted under "Measured"
python3 -B Logo/detail-study/tools/measure_ics.py               # the v2 "ICS" clearance numbers (about 8 s)
```

The builders write only into `out/`. All noise is seeded, so a rebuild is deterministic: a fresh copy of the tools rebuilt all 32 files in `out/` byte-for-byte (ffmpeg 7.1.5, this machine). `check_svg.py` reports 16 of 16 clean.

| Tool | Does |
|---|---|
| `tools/ttf_outline.py` | Stdlib TrueType reader (simple and composite glyphs, cmap 0/4/6/12, hmtx); turns text into paths. No kerning. It opens a variable font but reads only its default master (`Nunito[wght].ttf`: ExtraLight, wght 200) |
| `tools/ics_finish.py` | Gradients, lighting and shadow filters, grain, brushed streaks, rosette, tick ring, ring text; and the helpers v2 uses (the scalloped rim `cog_d`, `sunburst`, `beads`) |
| `tools/seal_art.py` | `seal(...)`, `mark_layers(...)`, `flat_mark(...)`; the v1 layer plan and the three themes |
| `tools/seal_v2.py` | `seal2(...)` and `PLAN2`: the v2 badge (rim, band, field, the mark, "ICS"; `metal="gold"` or `"steel"`) |
| `tools/check_svg.py` | Static SVG checks (a shared `clip-path` id fails silently in librsvg; this catches it) |
| `tools/measure_mark.py` | Read-only; measures the mark in `ics_brand.py` |
| `tools/measure_ics.py` | Read-only; how close the v2 "ICS" letters come to the gold arc and the knock-out channel |

## What is canon

- **Two elements** (2.32:26, "The Mark — Two Elements"): a circle (line 29, "A clean, unbroken circle", ICS Deep Blue `#1A2E52`, line 40) and an arc (line 32, "A single sweeping arc that begins below the circle, rises up and over, and comes to rest at the base", ICS Warm Gold `#C9A84C`, line 42). Line 34: "Together: a world, and the path that brings you home to it." (`BRAND_MARK.md:9` says "Two elements only"; canon's heading is "Two Elements", and the one "only" in its Global Access part, at line 5, limits that document to the Earth Branch mark.)
- **Scope** (2.32:5): "This document describes the ICS Earth Branch mark only. This is not the ICS corporate mark. There is no ICS corporate mark." 2.32 holds three versions (line 3): the Global Access guidelines (lines 9–73), a restricted PTKW addendum, "Behavioral Design Rationale" (77–176), and a Board "Origin Record" (180 onward). The fishhook reading sits in the PTKW addendum under "On the Shape of the Arc — Protocol for Design Staff" (162–176, line 164) and again in the Board record under "The Arc Is the Hook" (245–255, line 247). The ouroboros reading sits in the Board record under "The Shape" (187–197, line 189).
- **Wordmark type** (2.32:48): "a clean, rounded sans-serif". Canon names no typeface. Its classes: "ICS rounded corporate font" (2.31:21, 2.45:3), "warm sans-serif" (2.20:3), "Very friendly font" (2.07:3), "warm serif" (Level 3:38), "large, generous typeface" (Level 1:33), "standard monospace" (2.21:3).
- **Tagline** (2.32:54): "Because You're Worth the Investment." It occurs 5 times in 3 canon files (2.20:182, 2.32 ×3, 2.62:24) and 30 times in 12 `.md` files under ICS-Writing (also `design/` ART_DIRECTION ×1, HEARTH ×2, ICS_OS ×1, LOGO ×1; `meta/` HANDOFF_CARTOGRAPHER ×1; `reference/` ICS_Rigged_Sphere_MASTER_REFERENCE ×15, appendix_a_recovered ×2; `story/` trailers ×1, Trailer 2 ×1). 2.32:56 calls it "Six words"; as written it has five (six if "You're" is expanded). Three other taglines compete with it: "You Belong Here." (Level 3:26), "ICS Earth Branch — Where Everyone Belongs." (2.31:27) and "Your future is our investment." (2.33:163). "Your future starts here." (2.33:7–9, 2.26:8) is a near-tagline. Level 3:36 adds that the AIDEN corridor posters rotate quarterly, "a different design, a different tagline".
- **The wall** (Level 1.md:51): "the ouroboros with the serpent removed, rendered in brushed metal, approximately 2 meters across", south wall, behind the welcome desk. The railing above is "the same brushed metal" (Level 2.md:28); the badge holder is "brushed metal with the Earth Branch logo" (TV_SCREENS.md:130).
- **The badge** (2.33:51–54, 68; 2.46:30, 54): a hard plastic card, deep blue with gold text; printed "ICS EARTH BRANCH" and "EMPLOYEE — TIER 3"; "a small circular indentation near the top-right corner", called a "design accent"; "Embedded in the circular recess, upper right face." Tier 3 is "Deep blue / gold lettering"; Tier 1 is "Midnight blue / platinum lettering" (2.46:52); PTKW is "Grey / white lettering, governance seal" (2.46:55).
- **The welcome pack** (2.33): folder in "ICS Deep Blue with the gold seal embossed on the cover" (line 3), cover lines "Welcome to ICS." / "Your future starts here." / "— ICS Earth Branch, People & Culture Division" (7–9); bottle "Deep blue with the gold ICS seal" (143), laser-etched (145); keychain disc "ICS seal on one side, smooth on the other", engraved, two rings (159–163).
- **Finish words in canon:** brushed metal (3 lines: Level 1:51, Level 2:28, TV_SCREENS.md:130), brushed aluminum (CRD-7X:38), embossed (2.14:3, 2.33:3), engraved (2.33:161), laser-etched (2.33:145), stainless steel (2.33:143), stamped (2.27:3), polished (Level 1:45, of a floor). The words enamel, gilt, foil, hologram, watermark, chrome, lacquer and satin do not occur in canon; outside it, `design/BADGES_AND_UNIFORMS.md` uses "layered foil" (:24, PTKW and Director badges) and "hologram foil" (:131, the PTKW governance seal) for anti-forgery features, which are design notes about other marks, not the ICS seal. (2.36:117 has a "REASSIGNED" stamp on a shift card and Level 3:127 has "timestamped"; neither is a finish.)
- **What the "ICS seal" shows is never said.** Canon gives only where it appears and, on the folder and bottle, that it is gold (2.33:3, 143): stamped on the grey cover of a PTKW reference volume (2.27:3), embossed on the paper of a top-level policy document in the Director's locked drawer (2.14:3), and behind the Director in the annual video (2.37:117).
- **"Interplanetary" is not in 2.32, but canon uses it widely.** The mark document never uses the word; 40 of the 64 files in `canon/documents/` do, mostly in the names of divisions, the Board, HQ and documents ("ICS Interplanetary Governance Division", 2.14:5; "ICS Interplanetary Research Division", 2.16:5; the stamp on a PTKW reference volume, 2.27:3). It is also the public reading of the initials: "Public-facing name: Interplanetary Corporate Solutions" (2.02:4; also 2.29:233, 2.50:18); the initials "are read in public as Interplanetary Corporate Solutions and at PTKW level as Inflatable Crowd Solutions" (2.23:34; likewise 2.21:19); and a form handed to new staff is titled "ICS Global Solutions — Interplanetary Transit Waiver" (2.07:5). So the v2 seal leans on the public reading of the initials, the one used on the floor (its first word is the author's, and `seal2_corporate` adds the rest of the name); the PTKW reading ("Do not say the second reading on the floor", 2.21:19) is on no piece. The v2 top word is the author's instruction, not a quotation.
- **Wording safe on staff surfaces:** "ICS", "Earth Branch", the tagline, "300 years", "Interplanetary Corporate Solutions" and "349-planet portfolio" (both in the one glossary entry, 2.29:233). PTKW-only names (for example "Inflatable Crowd Solutions", 2.29:241) are kept off every piece.

## What is `[PROPOSAL]`

| Item | Value | Why |
|---|---|---|
| Mark | Unchanged from `ics_brand.py`: circle plus tapered arc, knock-out gap 0.050 R (small cut: arc 0.14/0.27/0.20 R, gap 0.10 R) | One geometry source (`BRAND_MARK.md:4`). The gap is the Models kit's own and sits badly with "unbroken": see Measured |
| Seal layers (v1) | Navy medallion (`paper` and `night` only) → gold rim (240-ray sunburst) with legend → 349-tick dial → hairline → 480-tick hatch (opacity 0.10, `paper` and `night` only, `seal_art.py:230–232`) → ring lettering with beads → inner bezel → field (72 sunrise wedges, three hairline rings and 96 beads on `paper` and `night`; an engine-turned rosette on the gold-only theme) → the mark | The detail the brief asked for. Added layers sit outside the mark or are finishes on it; the only cut in the disc is the channel `ics_brand` already makes |
| Themes | `paper` (cream field, navy-enamel disc), `night` (dark field, cream disc), `gold` (gold foil only) | `night` is one reading of the trailer's "the globe in white" (Trailer 2:12); `BRAND_MARK.md` open question 1 asks the same thing |
| Disc | Domed enamel with gloss, or flat | Domed `seal_paper` reads as a ball, `seal_paper_flat` as a disc. Your call |
| Rim legend (v1) | "INTERPLANETARY CORPORATE SOLUTIONS ·", repeated | The public-facing name (2.02:4, 2.29:233, 2.50:18). A default of `seal_art.seal` that no builder overrides; v2 drops it. Waits on the text ruling (question 4) |
| Top and bottom text (v1) | "ICS · EARTH BRANCH"; "BECAUSE YOU'RE WORTH THE INVESTMENT" | 2.33:53 and 2.32:54. The same defaults and the same wait; v2 drops both, and the author asked for the tagline to go |
| Dial | 349 ticks, a longer one at each quarter, all the same gold; none is marked as Earth | "349-planet portfolio" (2.29:233). The Models seal has 300, in `emblem_layout` (`ics_seal.py:59`, loop at 67); its plain `seal_layout` (42) has none |
| Left out | "LABOR SOURCE #349", the dates line, the two gold studs | "LABOR SOURCE #349" is contested (2.24:8, 85, 96 against 2.29:257, 262 and 2.01:11). The studs are unsourced (`BRAND_MARK.md:78`). The dates line ("EST. CYCLE 290 · CYCLE 300", `ics_seal.py:14`) is composed wording: the Branch opening in Cycle 290 is canon (`STORY.md:160`), the line is not. See question 4 and brand-3 |
| Finishes | Gold foil, steel, navy enamel with gloss, grain, brushed streaks, engine-turned rosette; v2 adds polished gold and enamel, and steel and enamel with a smooth sheen | Canon gives brushed metal, embossed, engraved; it never says enamel, foil or polished gold. "Spun-metal sheen" (`seal_art.py:79`) and "smooth spun finish" (`build_apps.py:289`) are code words, not canon |
| Plaque | 1600×1000 at 380 px/m; the mark is 2.0 m wide; dimension line "approx. 2 m"; the wall colour | The 2 m and the brushed metal are canon (Level 1:51). The wall colour, the dimension line and the two-tone split are not. `plaque_steel` is the literal canon reading (one brushed metal); `plaque_two_tone` is a blue disc with a gold arc |
| Badge header | 14 px/mm; mark in the small cut, circle radius 3 mm; 9 mm band; 8 mm recess at upper right, drawn almost the card's own colour (fill `#16294B`, within about one level of the card at the recess centre) and read through an inner shadow and a faint rim line; cap height 2.5 mm; gold text | Canon gives the colours, the text and "a small circular indentation"; every size and the mark's place on the card are proposal (brand-3). `build_apps.py` still says "darker" in its comments (lines 15 and 123–124); this row is the correction |
| Folder cover | 1300×1650; `gold` seal, radius 285; two cover lines slanted with `skewX(-10)` | Colour and embossed seal are canon (2.33:3). The font has no italic, so the slant is synthetic. The seal is the v1 `gold` seal, tagline included |
| Keychain | Front: paper seal on a gold ear. Back: a smooth gold coin with one engraved line, "Your future is our investment." Two plain steel rings, drawn closed | 2.33:159–163. Canon says "Two rings attached: one for keys, one for the badge lanyard" (159) and nothing about a split. The front is the v1 `paper` seal, tagline included |
| One-ink mark | Deep Blue on paper; disc and arc are the same ink, set apart only by the channel | Flat: one colour, no shading. The channel is a true cut (an SVG mask), so it shows whatever lies behind the mark; it is not a painted stripe |
| v2 wording | "INTERPLANETARY" arched on top (cap height 0.130 R, tracking 0.09 em); "ICS" across the middle; nothing else. `seal2_corporate` adds "CORPORATE SOLUTIONS" underneath | The author's words (Direction given). "CORPORATE SOLUTIONS" is canon-quoted (2.02:4) but was not asked for, so it is a variant, not the default. 2.32 never uses "interplanetary": see question 4 |
| v2 layers | Navy medallion → scalloped gold rim (36 lobes, 36 rivets, 240-ray sunburst) → 349 round-capped ticks, a longer one at each quarter → hairline and a faint 480-tick hatch (opacity 0.07, `seal_v2.py:164`) → the band: "INTERPLANETARY" on top, a star at each side, and on the lower arc 11 planets (a ringed one at the bottom, five graduated dots each side), two sparkles and a hairline orbit (`seal2_corporate` has its second line there instead) → gold bezel → the field: 36 sun rays, a 72-ray crown and a tilted orbit with one planet → the mark → "ICS" | The answer to "more details" and "retro-futurist". Layered like the v1 seal, with a band so that the mark sits on a field. Every form is rounded |
| v2 ornaments | The scalloped rim and its rivets, the stars, planets, sparkles and orbits, the sun rays and the crown | Ornament only: no canon meaning is claimed for any of it. General motifs read from the references, not copied. The rim is smooth-scalloped rather than sawtooth, in step with "no sharp angles" (2.32:48), a rule about the wordmark that I apply by analogy (inference) |
| v2 "ICS" | Varela Round, outlined, faux-bold stroke 0.075 × size, cap height 0.46 of the mark's radius, set across the disc; cream on the navy disc, navy on the cream disc | The author asked for "the ICS text written in the middle". It is the one place v2 puts type over the mark: see question 9 and ICS clearance |
| v2 metals | `gold` (polished gold and enamel) or `steel` (steel and enamel; smooth sheen, no brush texture, no `feTurbulence`). Only the rim, lettering and ornaments change; the mark's arc stays canon Warm Gold in both | The finish question is unanswered (question 5). Canon has brushed metal and never "polished gold" or "enamel"; `seal2_steel` is smooth, not brushed |

## Measured (`tools/measure_mark.py`)

R is the circle's radius. Rim samples: 1440, ±0.12°.

| | Full mark | Small cut |
|---|---|---|
| Knock-out margin each side of the gold (`GAP` / `GAP_SMALL`) | 0.050 R | 0.10 R |
| Rim removed by the channel | **118.5°** of 360°, one run from 349.0° (0° = +x, counter-clockwise) | **221.0°**, one run from 305.25° |
| Rim removed with the margin set to 0 | 72.75°, one run from 11.0° | 131.5°, one run from 349.0° |
| Arc rests at (centreline) | (−0.122, −0.689) R = **10.0° left of straight down** | same point |
| Centreline crosses the rim | at 46.7°, 6.4° to the tangent | at 54.7°, 6.1° |
| Bounding box (xmin, xmax, ymin, ymax) | (−1.287, 1.0, −1.0, 1.158) | (−1.308, 1.033, −1.0, 1.197) |
| Arc widths (start, middle, end) | 0.050 / 0.150 / 0.085 R | 0.14 / 0.27 / 0.20 R |

So every piece in `out/` inherits a channel that cuts about a third of the rim (more than half on the small cut), against "unbroken" (2.32:29, 100: "a complete thing has no gap you could walk through"). `BRAND_MARK.md:95` offers `GAP = 0` as the fix, but zeroing the margin does not make the rim whole: the arc's own body still covers 72.75° of it on the full cut, and 131.5° on the small cut with `GAP_SMALL` zeroed too. The 3D `ICS-Mark.blend` instead cuts a groove in an unbroken disc (`BRAND_MARK.md:95`); whether that satisfies "unbroken circle" is question 2. Any of these edits `ics_brand.py` and cascades into CRD-7 and ACS-9, so none is done here.

The arc's end is also inconsistent inside 2.32: "at the base" (32), "rest at the circle's base" (112), and "entering from the lower-left and resting at the lower-right" (122). Neither drawn end is lower right: 10.0° left of down here, 20.0° in the Writing kit.

## ICS clearance (`tools/measure_ics.py`)

The v2 "ICS" sits on the centre of the disc. R = 556 and the mark's circle is RC = 0.40 R = 222.4 in a 1200 canvas; distances are in canvas units, with the fraction of RC in brackets. The letters are the outlined glyphs plus half the 0.075 × size stroke on each side, as the SVG draws them; the knock-out is the arc's polygon grown by `GAP` × RC on every side. v2 draws the full cut at every size, so that column is what the pieces show; the small cut is for reference.

| | Full cut | Small cut |
|---|---|---|
| "ICS": size / cap height / width | 145.5 / 102.3 / 252.6 (1.136 RC, a little over half the disc's diameter) | same |
| Farthest ink from the centre | 128.9 (0.580 RC) | same |
| Nearest ink to the gold arc | 51.3 (0.231) | 36.4 (0.163) |
| Nearest ink to the channel edge | 40.2 (0.181) | 14.1 (0.063) |
| Closest point (x, y from the centre) | (117.3, 35.9), 17° from +x | (117.6, 35.2) |
| Knock-out margin each side of the gold | 11.1 | 22.2 |
| Centre to the nearest edge of the gold | 146.2 (0.658) | 133.5 (0.600) |
| Ink to the channel edge, I / C / S | 100.9 (0.454) / 75.1 (0.338) / 40.2 (0.181) | 77.1 (0.347) / 51.2 (0.230) / 14.1 (0.063) |

No letter touches the gold or the channel; the S is the nearest. These numbers say the letters fit. They do not say a word in the disc is allowed (question 9).

## Audit finding brand-3

An audit of ICS-Models run alongside this study found that several comments and docs claim more canon backing than canon gives. Checked against the canon lines:

- `design/BADGES_AND_UNIFORMS.md:48` ("Header band | Top 9 mm. Wordmark… the ouroboros without a serpent at left. [CANON, Doc 2.32]") and `:50` ("Circular, 8 mm, top right… [CANON]"): Doc 2.32 has no badge text, and canon has no 8 mm. Its only "9 mm" is a pistol (2.47:67). The badge band and recess here are therefore `[PROPOSAL]`; `build_apps.py` lines 13–16 say so.
- `design/BADGES_AND_UNIFORMS.md:15` ("The PTKW badge carries no ICS logo. The Board has no logo. [CANON]"): no verbatim canon line says it. The nearest are 2.21:3 ("No cover. No logo. No color.", a document) and 2.46:55.
- `BRAND_MARK.md:74` cites Doc 2.01 for "LABOR SOURCE #349". Canon is split: 2.24:8, 85, 96 (distributed to all Earth Branch staff) against 2.29:257, 262 (the term is not used in any global-access document) and 2.01:11 ("Earth's profile exists only at Board level"). The studs (`BRAND_MARK.md:78`) are unsourced, and the tick count is 300 there against 349 here.

## Relation to the other two logo kits

There are three logo systems and no ruling on which is the source (audit findings brand-1, repo-4, canon-1): the two kits compared below, and four older HTML files (three logo studies and a badges reference) in `ICS (Interplanetary Corporate Solutions)/ICS-_-RiggedSphere/.bob/artifacts/`, one of which draws a literal serpent (from its text; I did not render it). Both `Logo/` here and the Writing kit say they are the source (`BRAND_MARK.md:4`; `make_logo.py:9` says "single source of truth", scoped to `design/brand` and `LOGO.md`), and **0 of the 8 SVGs that share a name are byte-identical** (`ics-emblem`, `ics-lockup-horizontal`, `ics-lockup-stacked`, `ics-mark-mono-blue`, `ics-mark-mono-white`, `ics-mark-reversed`, `ics-mark-small`, `ics-mark`; 25 SVGs here, 13 SVGs in 20 files in the Writing kit). `Logo/` is untracked.

| | ICS-Models `Logo/` | ICS-Writing `design/brand/` |
|---|---|---|
| Mark | Solid disc, tapered gold arc cut by a knock-out gap | Hollow Deep Blue ring (stroke 18), thin gold arc (stroke 14) wholly outside it |
| Circle | Cut: 118.5° of rim | Unbroken (`LOGO.md:11`) |
| Arc | Enters the disc and rests at 10.0° left of down | Never touches: centreline 1.210 R to 1.720 R from the centre, ring outer edge 1.090 R, arc inner edge about 1.140 R; ends 20.0° left of down |
| Seal | Mark-centred; 300 ticks (`emblem_layout`); "LABOR SOURCE #349" (`ics_seal.py:12`) | Globe-centred, "no ring and no arc" (`LOGO.md:35`); 349 ticks (`make_logo.py:468`); "INTERPLANETARY CORPORATE" / "SOLUTIONS" (`make_logo.py:439`) |
| Minimum size | 32 px full, 16 px small (`BRAND_MARK.md:25`) | 48 px full, 24 px small (`LOGO.md:79`, tagged `[PROPOSAL]` there) |
| Wall | Not modelled (`BRAND_MARK.md:99`) | Level 1–4 signage: the arc "a thin painted or vinyl line, not a casting" (`LOGO.md:116`); canon's Level 1 logo is brushed metal (Level 1:51) |

(The Writing ring's R is its centreline radius, 100 units in a 397.1×392.1 viewBox.) This study's seals are mark-centred and have 349 ticks. The v1 ladder uses the small cut in cells under 40 px; the 38 px cell holds a mark about 28.2 px wide, under the 32 px switch in `BRAND_MARK.md:24–25` and `ics_brand.py:29`, so the choice agrees with it. The v2 ladder draws the full cut at every size (see Files).

## Limits

- **Renderers.** The PNGs are librsvg (through ffmpeg). The five v2 SVGs were also rendered in headless Chrome 157 (the Windows install, run from WSL with a scratch profile in `/tmp`) and look the same by eye. SSIM of the Chrome shot against the librsvg PNG, Chrome rescaled to the PNG's size: 0.9954 (`seal2_paper`), 0.9953 (`seal2_night`), 0.9952 (`seal2_steel`), 0.9951 (`seal2_corporate`), 0.9739 (`seal2_ladder`; the lower score is not diagnosed). The v1 SVGs have not been cross-checked, so their lighting, turbulence and gloss filters are unchecked outside librsvg. Edge and Firefox are installed on the Windows side and were not tried; I found no Inkscape or resvg.
- **Filters:** 112 `<filter>` tags across the 16 SVGs (64 in the 11 v1 files, 48 in the 5 v2 files); 99 set `color-interpolation-filters="sRGB"` and 13 do not. The 13 are the gloss blurs (`feGaussianBlur`, ids ending `-bl`). Seven are used (`kcfm-bl` in `keychain`, `spm-bl` in `seal_paper`, `lsm-bl` in `size_ladder`, `p2m-bl` in `seal2_paper`, `s2m-bl` in `seal2_steel`, `c2m-bl` in `seal2_corporate`, `l2pm-bl` in `seal2_ladder`) and six are unused definitions (`fcsm-bl`, `sgm-bl`, `snm-bl`, `sfm-bl`, `n2m-bl`, `l2nm-bl`). In librsvg the PNG is byte-identical with the blur unmarked, marked sRGB or marked linearRGB (a control run on v1; a control edit to another filter does change it). The SVG default is linearRGB, so a browser may draw the gloss a little differently; the Chrome check above covers v2 only. `feTurbulence` appears 8 times, all in v1 (`folder_cover` 2, `plaque_steel` 3, `plaque_two_tone` 3); v2 has none, and `seal2_steel` has no brushed texture.
- **Lettering:** Varela Round Regular (`Logo/fonts/`, the face the 3D seal uses because Blender cannot load the variable Nunito, `BRAND_MARK.md:63`), with a faux-bold stroke on some lines (v2's "ICS" and "INTERPLANETARY" included). Advance widths only (no kerning); no italic, hence the synthetic slant. The 2D Models kit uses Nunito ExtraBold (`ICS-Seal_build.py:21–22`, `ics_seal.py:16`); this study's reader opens `Nunito[wght].ttf` but reads only its default master (ExtraLight, wght 200), so it cannot draw ExtraBold. The v1 seal lettering is unreadable in the 38 px and 24 px cells of `size_ladder`; use the plain mark there. In the v2 ladder the arched word is unreadable at 75 px and below (see Files).
- **Wording.** v1: every string on a piece is quoted from canon or is a label. From canon: "ICS EARTH BRANCH" on the badge (2.33:53); the folder's three cover lines (2.33:7–9); the keychain line (2.33:163); the tagline on the v1 seal (2.32:54, set in capitals, without its full stop); the v1 seal's top text, the words of 2.32:9 and 2.33:53 with a middle dot added; and the v1 rim legend, the public-facing name (2.02:4). Labels: `SEAL`, `MARK, TWO COLOURS`, `MARK, ONE INK`, the pixel sizes on the ladder, and `approx. 2 m` on the plaque. v2: "INTERPLANETARY" and "ICS" are the author's words (2.32 never uses "interplanetary", but canon reads the initials that way in public: see What is canon); `seal2_corporate` adds "CORPORATE SOLUTIONS" (2.02:4), which was not asked for; the v2 ladder labels are `PAPER`, `MIDNIGHT` and the pixel sizes. The proposal is the arrangement (which string sits where, the dots, the ring layout), and the seal's wording still waits on question 4. Contested strings ("LABOR SOURCE #349") and PTKW-only names are left out. The PTKW governance seal is not designed anywhere (2.46:55 names it; `BADGES_AND_UNIFORMS.md:128–131` is a `[PROPOSAL]`), so none is drawn.

## Open questions

1. **Which kit is the source,** Models `Logo/` (disc, gap) or Writing `design/brand/` (ring, arc outside)? Or neither, with the older HTML studies in `ICS (Interplanetary Corporate Solutions)/ICS-_-RiggedSphere/.bob/artifacts/`? This gates every rebuild and any new model, so no model gets a mark until it is ruled. May detail change the mark, or only its finish and surroundings?
2. **"Unbroken" against the gap** (118.5° / 221.0° of the rim). `GAP = 0` alone does not close it (the arc's body still covers 72.75° / 131.5°; see Measured) and it cascades into CRD-7 and ACS-9. Keep the gap, draw the arc over an uncut disc, or take the Writing ring? `BRAND_MARK.md:95` notes that the 3D `ICS-Mark.blend` already uses a groove in an unbroken disc and asks whether that satisfies "unbroken circle".
3. **Where the arc rests.** "At the base" or "lower-right"? With "ICS" in the middle it is also a layout choice, because the S is the letter nearest the arc (ICS clearance).
4. **Text around the mark.** Is any allowed, and which wording on staff surfaces against PTKW surfaces: `> **ICS GLOBAL SOLUTIONS**` (the capitals masthead at 2.29:9; 2.06:5 reads "ICS Global Solutions — Earth Branch") or "Interplanetary Corporate Solutions" (2.02:4, 2.29:233), given 2.32:5? The v2 seal puts "INTERPLANETARY" over "ICS" at the author's request; 2.32 never uses the word and says "There is no ICS corporate mark" (2.32:5), while canon uses it for the public-facing name, for governance and research division names (2.14:5, 2.16:5, 2.27:3), and for the public reading of the initials (2.21:19, 2.23:34). Does a seal that puts INTERPLANETARY over ICS count as the corporate mark? "Labor Source" and "#349", dates, studs, 300 or 349 ticks? Which tagline: the author wants it off the seal, and the v1 folder cover and keychain still carry it.
5. **Finish.** The author chose "Retro-futurist, more Fallout" and left the finish open: brushed metal (canon) or polished gold and enamel? `seal2_paper` and `seal2_night` are polished gold and enamel, `seal2_steel` is steel and enamel; none is brushed. Domed or flat disc? Which circle colour on dark grounds?
6. **The seal on restricted documents.** The "ICS seal" is stamped on a PTKW reference volume (2.27:3) and embossed on a top-level policy document (2.14:3), while `BADGES_AND_UNIFORMS.md:15` says "The PTKW badge carries no ICS logo. The Board has no logo." That sentence is about a badge and the Board, so it may not conflict, but no canon line backs it either (brand-3). Does the seal count as the logo here?
7. **Handbook and brochure galaxy** (2.20:3, 2.19:3) against the trailers' globe (Trailer 2:12; `trailers.md:152`, 468). `STORY.md:166`, the Director's hand-drawn mark, is a circle and an arc with no globe. Which motif?
8. **Typography on posters:** rounded sans (2.32:48), warm sans (2.20:3) or warm serif (Level 3:38)?
9. **"ICS" across the disc.** 2.32 describes two elements (26), "a clean, unbroken circle" (29) and a mark only (5). The v2 seal puts the letters inside the circle, as asked. Is a word in the disc allowed, or should "ICS" sit on a band with the disc left clean?

## Not done

Handbook and brochure galaxy variant (`ics_finish.galaxy_dots` is an unused helper written for it); the older logo versions (2.37:93, 105); PTKW- and Board-register renderings (2.32:164, 245; 2.47:96; 2.48:93); the water bottle; the badge holder (TV_SCREENS.md:130); the UI boot logo and wallpaper (`UI_MENUS.md:88`, `ICS_OS.md:34, 36`); the weapon logos (CRD-7:36 on the face, ACS-9:34 at the base, AMB-3F:58 on the grip housing). After the v2 pass: the folder cover and keychain still use the v1 seal, tagline included; there is no v2 small-size cut; there is no "ICS on a band, disc clean" alternate; steel has no brushed texture (to build only if brushed metal is chosen); the v1 pieces have no Chrome or Edge check. No commit, no push, no deletion, no overwrite of `svg/` or `png/`.

*[PROPOSAL] New file. Proposed: a self-contained study folder (2026-11-12) that adds detail around the existing mark without touching it; the v2 pass (the same day) follows the author's answers quoted under Direction given. Nothing in it is canon. At writing (2026-11-12), none of the 82 files that were in `Logo/` before the study had changed (sha256, checked from `Logo/` against a list taken before the study began).*
