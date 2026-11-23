# ACS-9 — Acoustic Compliance System

**Canon:** `ICS-Writing/canon/weapons/compliance/ACS-9 — Acoustic Compliance System.md`
**Category:** Compliance Tool
**Acquired:** Found. Level 6 Behavioral Systems Storage, Phase 3 (a case with three others, unlocked). `design/INVENTORY.md` says "PTKW floor storage, Tier 3": see open question 11.
**Base tool for:** ACS-9D (Directed Beam, Phase 2, Junction A), ACS-9RS (Resonance Shell, Phase 4, Junction C)
**Look:** ICS shape language (soft, rounded, matte, one mark, one lamp). The CRD-7 hard-industrial override does **not** apply here. Not ruled on by the author.
**Status:** modelled v2. Triangle cap lifted by the author. Textured PBR, perforated grille, printed decals, two focusing rings, rear panel. Unit serial and printed wording are canon-backed where marked; the rest is `[PROPOSAL]`.
**In-game name:** "ACS-9 Presence Projector" (`design/INVENTORY.md`), 4 uses.

## Silhouette
A matte black cylinder with a carry handle over the top and a speaker-like grille at one end. Someone should be able to read it as a speaker or a torch, not a weapon.

## Dimensions (cm)
| Part | Size | Source |
|---|---|---|
| Overall length | 25 | Canon: "roughly 25cm long" |
| Body diameter | 8 | Canon: "roughly 8cm diameter" |
| Front bezel (aperture assembly) | 8.5 | ACS-9D canon: "directional aperture is 8.5cm diameter". Conflicts with the 8 cm body; see open question 1 |
| Grille recess | 7.2 across, 2.5 deep | [PROPOSAL] |
| Handle | 14 long, 2.4 wide, 4.5 tall | [PROPOSAL] |
| Focusing rings (2) | 22 mm outer, 15 mm bore, 4 mm deep | CRD-7X canon: 22 mm ring; two rings (primary, secondary) |
| Rear housing panel | 5.8 across | [PROPOSAL] size. Canon: a rear housing panel exists, held by two quarter-turn screws |
| Weight | not given | |

## Materials
All textures are procedural (`acs9_textures.py`), tiled, no external images. Finish choices are `[PROPOSAL]` unless the canon quote is given.

| Part | Material | Note |
|---|---|---|
| Body, bezel, handle, rear panel | matte black moulded ABS: fine grain, soft mottling, albedo about 0.035, roughness about 0.55 | Canon: "black cylinder" |
| Grille plate | same ABS, 177 holes of 2.6 mm in a hex-ish ring pattern, raised lip | Canon: "a recessed grille that looks like a speaker" |
| Speaker cloth | plain weave behind the plate | [PROPOSAL] |
| Handle grip | pebbled rubber (Worley domes) with seven transverse ribs | [PROPOSAL] |
| Focusing rings | brushed aluminium, metallic 1, streaks along the circumference | Canon (CRD-7X): "brushed aluminum, slightly shinier than the matte grey housing" |
| Slider knob, lamp bezel, quarter-turn screws | finer brushed dark steel, metallic 0.95 | [PROPOSAL] |
| Lamp | amber emissive lens (strength 1.8) | Colour backed by canon (Security Division indicator "amber, charged"). Presence on the ACS-9 is a [PROPOSAL] |
| ICS mark | deep blue disc `#1A2E52` with knock-out gap, gold spiral arc `#C9A84C` | Doc 2.32 palette and shape. Real mesh on the rear panel (R = 10.5 mm) and a raster on the label (R = 3.4 mm), both from `_shared/ics_brand.py`. Geometry is [PROPOSAL], see `Logo/BRAND_MARK.md` |

## Printed text and surface detail
| Item | Where | Content | Source |
|---|---|---|---|
| Label (62 × 17 mm film) | -X side, forward of mid-body | "ACS-9 ACOUSTIC COMPLIANCE SYSTEM", "SER. ICS-ACS-9-0012", "Safety-certified for use in occupied facilities.", "Extended exposure (over 4 hours continuous) is not recommended.", "Because You're Worth the Investment.", small mark | Serial: `ptkw/B-17` equipment log. Certification and exposure wording: ACS-9 canon file. Tagline: Doc 2.32. Layout, mark and the product line are [PROPOSAL] |
| Slider legend (60 × 10 mm) | +X side above the slider | printed 1, 2, 3 with gold tick marks of rising height | "marked 1, 2, 3" is canon. Font, tick style and tick heights are [PROPOSAL] |
| Rear panel text | below the mark | "ACS-9" | [PROPOSAL] |
| Seams | body | two shallow grooves at y = +0.080 and -0.088 (body centred) | [PROPOSAL] |

## Mount points
Positions are from the **grip origin** (v2), in metres. The mounts have not moved relative to the body; only the origin did.

| Empty | Position | Role |
|---|---|---|
| `mount_ACS-9D_shroud` | (0, -0.170, -0.069) | Front face centre. The directional baffle slides over the bezel and extends along -Y |
| `mount_ACS-9RS_plate` | (-0.030, -0.005, -0.0955) | Underside of the body, 3 cm off-centre to -X, mid-body. The resonance plate is cemented here |

(These are `mounts` minus `ORIGIN` in `ACS-9_build.py`. Read them from the .blend when building an attachment.)

Attachments build with their origin at the mount. **Never move a mount without rebuilding every attachment.** No ACS-9 attachment exists yet. `_shared/studio.py` `append_base` now takes a `prefixes` argument; pass `("ACS-9", "mount_")`.

## Animation / rig needs
- **Slider:** three positions. Knob posed at position 2 (centre). Positions 1 and 3 sit at y = -0.016 and +0.016 [PROPOSAL]. The printed legend matches. No rig.
- **Lamp:** a single lit state. Charged/discharged behaviour (amber to dark) is a game-side note, not geometry.
- **Focusing rings:** two separate parts, removable. The secondary is the source part for CRD-7X. The equipment log shows a secondary ring missing on return.
- **Rear panel and quarter-turn screws:** separate parts, posed closed. The screws turn 90 degrees to release the panel.

## Budget
The 3,000-triangle hand-held cap (art book §6) is **lifted for the ACS-9 by the author**. **Built: 29,484 triangles, 21 parts** (from the build's `STATS` line). The grille plate is 12.6k of that (177 cut holes). If a lighter version is needed, replace the holes with a normal map and the plate drops to about 1k.
Texture set: 20 PNGs in `textures/` (plus five stale orphan files, see HANDOVER) (ABS 1024, rubber / aluminium / steel / cloth 512, three decals at 20 to 24 px/mm). FBX embeds them (5.6 MB).

## Export
`Weapon Models/exports/ACS-9.fbx`. Built by `Weapon Models/compliance/ACS-9/ACS-9_build.py` with `acs9_textures.py`, which writes `ACS-9.blend`, `textures/`, and the previews in the same folder.

## Pivot
v2: origin is the **centre of the rubber grip**, matching the README convention (grip centre). v1 used the body centre. Moving it changed every mount coordinate.

## Canon found while researching v2
- Serial `ICS-ACS-9-0012`; signed out for calibration testing Q3 Week 2, returned Week 4 with the secondary focusing ring missing (`ptkw/B-17`).
- Two 22 mm focusing rings in the emitter assembly; the secondary is reached by removing the rear housing panel, held by two quarter-turn screws (`CRD-7X`).
- Discharge indicator "amber, charged" on the security-division tool (`enemies/PTKW-Security-Division.md`).
- "ACS-9 calibration documentation" exists (`C-15`, `B-17`).
- Tool UI lives on the tool, "the ACS-9 slider" (`design/VERBS.md`).
- The `design-team/04 — ENV-SYS-3` cross-reference in the weapon file is really `ptkw/B-04 — ENV-SYS-3 Olfactory Primer Request`. A grep of Doc 2.18 for acoustic, infrasound and ACS returned nothing; Level 4 describes only the cafeteria ceiling acoustic panels. Neither the Doc 2.18 acoustic section nor the Level 4 BES design intent exists in the files searched.

## Open questions
1. **Body vs aperture.** Canon gives 8 cm body and an 8.5 cm aperture in the ACS-9D brief. The model uses an 8.0 cm body and an 8.5 cm front bezel [PROPOSAL]. Author to rule.
2. **"Rear surface" for the ACS-9RS plate.** Canon says the plate covers about 60% of the rear surface and sits "3cm off-centre to the left". The model puts the mount on the underside, offset to -X. A 20 × 30 cm plate cannot sit on an 8 cm cylinder, so the plate must be cut down or the canon corrected.
3. **ICS mark "at the base".** Modelled on the rear panel (+Y). Confirm "base" means the rear end, away from the grille.
4. **Lamp.** Not in the ACS-9 canon. Amber matches the Security Division indicator. Confirm, or remove.
5. **Handle position.** Canon says "a carrying handle on one end". The model runs the handle over the rear half. Confirm.
6. **Perforated grille.** Done with 177 cut holes. An earlier orphan ACS-9 existed in this folder (backed up at `GitHub/_backups/ACS-9-orphan-2026-11-08/`). Say if you want anything from it restored.
7. **Soft or hard look.** Built to the soft ICS look. Undecided for other compliance tools (CRD-7 open question 9).
8. **Printed label wording.** Only the serial, certification and exposure lines are canon. The product line, tagline placement and mark are mine. Tagline is canon (Doc 2.32) but its use on a tool is a `[PROPOSAL]`.
9. **Logo.** Done: the brand-kit mark (`Logo/`). The arc geometry and the knock-out gap are [PROPOSAL]; open questions are in `Logo/BRAND_MARK.md`.
10. **ACS-9D tube length.** Canon says the baffle is cut to 18 cm, and also calls it a "1.2-meter metal cylinder". Needed before the attachment is built.
11. **Storage location.** Weapon file says Level 6 Behavioral Systems storage; `INVENTORY.md` says "PTKW floor storage, requires Tier 3 access". Also Phase 2 (ACS-9D) vs Phase 3 (ACS-9 found).
12. **Which end is "rear".** The ACS-9RS text and the base text may use different ends.
