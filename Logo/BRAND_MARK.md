# ICS Earth Branch mark: brand kit

**Canon:** `ICS-Writing/canon/documents/2.32` (Earth Branch Brand Identity, v9.1). Canon wins over this file.
**Single source of geometry:** `Logo/src/ics_brand.py` (pure Python; raster helpers need numpy). `Logo/src/ics_brand_bpy.py` builds the same outline as Blender meshes. The SVG kit, the label decal and the 3D marks on the models all come from it, so they cannot drift apart.
**Rebuild the kit:** `python3 Logo/build_brand.py` writes `Logo/svg/` and `Logo/png/`. Needs `ffmpeg` (librsvg) for PNGs. Fonts are in `Logo/fonts/` (Nunito, Varela Round, OFL licence).

## What is canon

- Two elements only: a clean, unbroken Deep Blue circle `#1A2E52` and **one** Warm Gold arc `#C9A84C`.
- The arc begins below and outside the circle (lower left), rises up and over, and comes to rest at the base (lower right). It never extends beyond the circle again, and there is no second arc: a visible entry, no visible exit.
- Isolated, the arc reads as a fishhook. Staff are told that is coincidence. The Board reads the mark as an ouroboros with the serpent removed.
- Wordmark: clean rounded sans-serif, no sharp angles. Tagline: "Because You're Worth the Investment."
- Scope: Earth Branch only. There is no ICS corporate mark. PTKW badges carry no ICS logo. The Maintenance-Bar has none, by design.

## What is `[PROPOSAL]` (everything below the canon line)

| Item | Value | Why |
|---|---|---|
| Arc path | clockwise spiral, 216° to −100° (316° of sweep) | Gives the entry at lower left and the rest at the base |
| Arc radius | 1.30 R at the tail to 0.70 R at rest | The tail starts outside the circle and finishes inside it |
| Arc width | 0.050 R at the tail, 0.150 R at the crown, 0.085 R at rest | Reads as a hook, not a plain ring |
| Ends | round caps | "No sharp angles" |
| Knock-out gap | 0.050 R cut from the circle around the arc | The gold never touches the blue, so the arc passes through the world |
| Small variant | heavier arc (0.14 / 0.27 / 0.20 R), gap 0.10 R | For under 32 px / 8 mm |
| Minimum size | 16 px / 5 mm (small variant); full mark from 32 px | From the true-size test strip |
| Clear space | 0.5 R on every side of the bounding box | |
| Paper white | `#F4F1EA` | Off-white for the "globe in white" treatments |
| Wordmark | "ICS" built from round-capped strokes (stroke 0.17, C opens right as an echo of the arc) | Canon asks for rounded and gives no letterforms |
| Lockups | horizontal, horizontal with tagline, stacked, reversed, mono | |
| Treatments | on-white, reversed (paper circle on blue), trailer (white circle, gold arc, `#0B1426`), gold-on-white, one-colour blue / black / white | Trailer and gold-on-white are from the trailer notes |

## Files

`Logo/svg/` and `Logo/png/`: `ics-mark`, `-small`, `-mono-blue|black|white`, `-reversed`, `-on-white`, `-trailer`, `-gold-on-white`, `ics-arc-isolated`, `ics-icon-512|64`, `ics-lockup-horizontal`, `-horizontal-tagline`, `-reversed`, `-mono`, `-stacked`, `ics-wordmark`, plus the sheets `ics-mark-construction`, `ics-mark-clearspace`, `ics-brand-sheet`.

**Seal and emblem (all `[PROPOSAL]`, added 2026-11-08):** `ics-seal` (blue), `ics-seal-metal` (engraved on brushed grey, for the keychain disc, Doc 2.33 item 6, and the badge holder), `ics-emblem` (reversed) and `ics-emblem-paper`. See the next section.

## 3D model (editable)

`Logo/ICS-Logo.blend`, built by `Logo/ICS-Logo_build.py` (previews in `Logo/previews/`). It is the emblem as real geometry, 1 m wide, standing upright and facing -Y. Collections: `Base`, `Rings`, `Ticks`, `Text`, `Mark`, `Ribbon`, `Plaque`, all parented to `ICS-Logo_ROOT`. Three materials drive every colour: `ICS-Logo_blue`, `_gold`, `_paper`.
- **Edit wording:** the five text objects are live Blender text. The two ring texts bend through a Curve modifier on the `ICS-Logo_path_top` / `_bottom` circles, so a new string follows the ring.
- **Edit the mark:** the mark meshes come from `ics_brand_bpy.build_mark`, so change the arc in `ics_brand.py` and rebuild rather than sculpting by hand.
- Hand edits are lost on rebuild: copy the `.blend` first, or edit the script.
- Ticks are three merged meshes (minor, major, zero), not 300 objects.

## ICS-Mark: the parametric 3D mark `[PROPOSAL]`

`Logo/ICS-Mark.blend`, built by `Logo/ICS-Mark_build.py` (previews `Logo/previews/ICS-Mark_front|angle|detail.png`). First piece of the rebuild: the canon mark alone (Doc 2.32), as ONE object `ICS-Mark` with a Geometry Nodes modifier `ICS-Mark`, then Bevel and WeightedNormal modifiers. Radius 1 = the circle, flat in XY facing +Z. Scale the object for real sizes (CRD-7 face R 9 mm = scale 0.009).
- **Sliders** (Properties > Modifiers > ICS-Mark): arc start/end angle, start/end radius, angle curve, radius curve, width tail/crown/rest, crown position, arc resolution, arc flatness, groove gap, groove depth, disc thickness, disc segments. Changing one rebuilds the mesh live; checked by script (crown width 0.15 to 0.30 and resolution 160 to 80 both change the evaluated mesh).
- **Defaults** are `ics_brand.ARC` exactly. Gold arc bbox in 3D matches the 2D outline within 0.01 circle radii.
- **Bake back:** `Logo/ICS-Mark_params.py` run in Blender prints the `ARC = dict(...)` for `ics_brand.py`. The 2D kit and the weapon builds still read `ics_brand.py`, not the `.blend`.
- **Build `[PROPOSAL]`:** Deep Blue enamel disc that is literally unbroken, with the gold arc lying in a shallow groove cut into it, instead of the flat knock-out gap. The groove is cut by a Boolean (exact) from the arc tube plus an end sphere at each end. Do not join those cutters into one mesh first: it self-intersects and the disc vanishes. `Groove Gap = 0` switches the cut off.
- **Defaults I used for questions the author has not answered:** disc is Deep Blue (not white), groove build, text around the mark only on the seal.
- Blender 5.2 detail: set a slider from Python with `modifier.properties.inputs[<socket identifier>]["value"]`; names do not work as keys.
- Next on the rebuild list: ICS-Seal and ICS-Emblem on top of this, one layout source in `ics_brand.py`, static Nunito ExtraBold ring text, game versions (high-poly, low-poly with baked maps, decal), real-size copies.

## ICS-Seal and ICS-Emblem: 3D, built on the mark `[PROPOSAL]`

`Logo/ICS-Seal.blend` and `Logo/ICS-Emblem.blend`, both from `Logo/ICS-Seal_build.py` (run `ICS-Mark_build.py` first; previews `Logo/previews/ICS-Seal_*.png`, `ICS-Emblem_*.png`). 1 m wide, upright, facing -Y.
- **One layout source:** `Logo/src/ics_seal.py` holds every radius, font size, per-letter ring position, the 300 ticks, the ribbon and the dates line. `build_brand.py` (2D) and `ICS-Seal_build.py` (3D) both read it. After moving the code into it, the four 2D SVGs came out byte-identical to the old ones.
- **The mark inside is the live `ICS-Mark`** (appended from `ICS-Mark.blend`), so its sliders still work in the seal: select `ICS-Seal_mark` > Modifiers. Reversed colours as in the 2D seal: paper disc, gold arc, Deep Blue field. The disc is thinner here (an inlay).
- **Lettering:** one text object per letter, placed on the ring by the shared layout. Retype a letter in edit mode, or change the string in `ics_seal.py` and rebuild (that re-spaces the ring).
- **Font limit:** Blender cannot load the variable Nunito, so the 3D letters are Varela Round with a faux-bold offset; the 2D kit uses Nunito ExtraBold. A static Nunito ExtraBold instance needs `fontTools`, which is not installed (installing it was blocked this session). The per-letter advances in `ics_seal.ADV` are still estimates.
- **3D-only addition:** the dates line gets a small Deep Blue backing plate, because as an object it cannot float on the page.
- Hand edits are lost on rebuild.

## Seal and emblem `[PROPOSAL]`

The reference emblems the author supplied (Umbrella, Diamond Dogs, XCOM, Assassin's Creed and a knight crest) share one pattern: a central symbol held inside concentric rings, a ring of lettering, fine detail at the rim, a banner for the motto. The seal copies the pattern with ICS's own facts, so the extra detail is world information, not decoration.

| Part | Content | Source |
|---|---|---|
| Top ring text | ICS · EARTH BRANCH | Doc 2.32 |
| Bottom ring text | LABOR SOURCE #349 | Doc 2.01 (Earth is Labor Source #349) |
| Rim | 300 hairline ticks, one per Cycle, a long tick every 25, the tick at 0 in gold | `[PROPOSAL]`; the current Cycle is 300 |
| Banner (emblem only) | BECAUSE YOU'RE WORTH THE INVESTMENT, Deep Blue on Warm Gold | Doc 2.32 tagline |
| Date line (emblem only) | EST. CYCLE 290 · CYCLE 300 | STORY.md: Earth Branch opened in Cycle 290 |
| Two gold studs | left and right of the mark | `[PROPOSAL]` |

Technical note: ffmpeg's librsvg does not draw `<textPath>`, so ring text is set letter by letter with an approximate Nunito advance table (`_ADV` in `build_brand.py`). If a real SVG renderer is used later, the spacing may shift slightly.

## Where the mark is baked into the models

| Model | How | Size |
|---|---|---|
| CRD-7 (top face) | 3D mesh from `ics_brand_bpy.build_mark`: blue disc with the knock-out cut, gold arc on top | R = 9 mm, rotated 180° so it reads upright with the prongs at the top of the frame |
| ACS-9 rear panel | same mesh, rotated onto the +Y face | R = 10.5 mm |
| ACS-9 label | raster from `ics_brand.raster_mark`, composed into the label decal | R = 3.4 mm |

CRD-7X and CRD-7R were rebuilt on the new base; neither carries a mark of its own.

## Contradictions and open questions for the author

1. **Circle colour in the trailer.** The trailer notes say "the globe in white", while Doc 2.32 says the circle is Deep Blue. The kit has both (`ics-mark-trailer`, `ics-mark-reversed`). Which is canon for in-world trailers?
2. **"Unbroken circle" vs the arc entering from outside.** The PTKW text has the arc begin outside the circle. The mark honours that, and the knock-out gap makes the circle read as broken where the arc crosses it. If the circle must stay literally unbroken, set `GAP = 0` in `ics_brand.py` and rebuild everything. The 3D `ICS-Mark.blend` already uses a groove in an unbroken disc instead; author to say whether that satisfies "unbroken circle".
0. **Is text around the mark allowed?** Doc 2.32 says the mark is two elements only and the wordmark is separate. The seal and emblem put text around it. They are for seals, medallions and the keychain, not the primary logo. Author to rule.
3. **Handbook "galaxy".** The Origin brochure is described with a "suggestion of a galaxy in soft blues". Not designed here.
4. **Older logo versions** (Doc 2.37 ad archive, #038 and #071) are not designed.
5. **Level 1 south-wall logo** (about 2 m, brushed metal) and the badge-holder metal version have no model or map yet.
6. **Wordmark.** The stroke-built "ICS" is mine. If the author has a face in mind, swap it in `wordmark_strokes`.
7. **Micro size.** Below 16 px the arc is a speck. Decide whether a further-simplified micro mark (disc with a gold dot or tick) is wanted for UI use.
8. **Mark placement on weapons.** CRD-7 "on the face" and ACS-9 "at the base" are canon; the exact spot and size are mine. AMB-3 and AMB-3F ("on the grip housing") are not built yet and should use `build_mark`.
