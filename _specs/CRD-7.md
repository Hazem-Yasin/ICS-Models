# CRD-7 — Compliance Restraint Device

**Canon:** `ICS-Writing/canon/weapons/compliance/CRD-7 — Compliance Restraint Device.md`
**Category:** Compliance Tool
**Acquired:** Found. Level 5 security storage locker, Phase 2 (a transitioned PTKW officer's issue).
**Base tool for:** CRD-7R (Compliance Reversal), CRD-7X (Extended Burst)
**Look:** v3 "hard industrial" (author's call, 2026-11-07, after Alien: Isolation prop references): dense panel detail, visible fasteners, a bright accent on a dark body, wear where hands go. This **overrides** the brief's usual ICS shape language ("rounded corners, no sharp edges") for this item only. The silhouette stays a fat remote with a two-pin plug.
**Status:** modelled and textured (v4: v3 hard look plus mechanics and story-wear pass; 2048 px body atlas, 1024 px trim atlas, plate images, LCD images). Not rigged. Triangle budget lifted by the author. Poses are static: flaps open, shutter open, mode flag at RANGED, prong guard hinged up.

## Silhouette
A fat dark remote with a two-pin plug at the front, like a travel adaptor. v1/v2 were friendly and domestic; v3 is a worn industrial instrument, with the pins still the first thing you see.

## Dimensions (cm)
| Part | Size | Source |
|---|---|---|
| Body | 11.5 x 5.0 x 3.0 | [PROPOSAL] canon says only "size of a TV remote" |
| Prong shroud | 3.0 long, 3.8 x 2.2 | [PROPOSAL] |
| Prongs | 2 x 1.8 long, 4.4 mm dia, 20 mm apart | [PROPOSAL] |
| Side emitter aperture | 15 mm dia | CRD-7X: "approximately 15mm wide", recessed, smooth rim |
| Emitter ring seat | 22 mm | CRD-7X: the ACS-9 focusing ring is 22 mm |
| Weight | not given | |

## Materials and wear
| Part | Material | Note |
|---|---|---|
| Body | bare brushed gunmetal (metallic 1, roughness ~0.36) | v3b, author's call: pure metal, no paint chips, scratches, tally or grime. Brushed lines, panel grooves, dark printed text. Label paper and sticker are non-metal |
| Shroud, collars, rear cap, bezels, feet-less trim | dark ABS (trim atlas swatch 0) | |
| Grip pads, cord, feet, wrist loop | pebbled black rubber (swatch 1) | |
| Screws, shutter, slider, eyelet, dial collar, LED rings | dark brushed steel (swatch 2) | |
| Thumb button, dial seal mark | red plastic, scuffed (swatch 3) | [PROPOSAL] colour |
| LCD | emissive image, amber (charged) / red (discharged) | `CRD-7_screen_charged`, `CRD-7_screen_discharged` (stored for swapping) |
| Charge LEDs | emissive amber x4 lit, 1 dark | |
| Prongs | brushed steel | |
| Logo | deep blue disc `#1A2E52` with the knock-out gap, gold spiral arc `#C9A84C`, 3D mesh from `Logo/src/ics_brand_bpy.py` (R = 9 mm, rotated 180° to read upright from the prong end) | Doc 2.32. Circle plus one arc, no serpent. Arc geometry, gap, size and position are [PROPOSAL], see `_brand/BRAND_MARK.md` |
| Indicator strip | emissive, amber (charged) / red (discharged) | canon. Red material is stored in the file for swapping |
| Emitter lens | near-black glass | |

## Printed text and surface detail
"Asset Welfare Series - CRD-7" and "For compassionate use only." (canon) are now baked into the albedo; there are no text meshes.
v2 detail, all [PROPOSAL] unless noted:
- Moulding seam groove round the body, below mid-height. Geometry.
- Recessed pocket round the thumb button, and a shallow dish in the button. Geometry.
- Underside label: ICS Earth Branch / Security Issue CRD-7, serial, barcode, "Safety capacitor 40 V" (40 V is canon, from the CRD-7R mod).
- Half-peeled "Compassionate Use Certified - 12 H" sticker (the 12-hour certification is canon).
- Previous owner's tally scratched near the button (five-bar gate and three singles).

v3 "hard look" additions, all [PROPOSAL]:
- **LCD** on the top face in a bezel: "READY", five-segment charge bar, "CONTACT 90 s" (90 s is canon), "CHG 100%". Discharged variant reads "DISCHARGED / RECHARGE / CHG 0%" in red.
- **Five charge LEDs** under the screen (four lit, one dark), with steel rings.
- **Rubber grip pads**, ribbed, in pockets on both sides of the rear half. They replace the v2 finger dimples.
- **Battery door** on the underside with two screws and a thumb notch, plus four rubber feet. Sits on the CRD-7R end ("BATTERY - 1/4 TURN").
- **Safety switch**: recessed panel, track, steel slider parked at SAFE, four corner screws, "SAFE / LIVE" stencils.
- **Emitter service panel**: the side emitter now sits in a channel with a steel shutter slid open beside it ("TEST" stencil). The emitter is still visible, not hidden (open question 4 still stands).
- **Sealed service dial** on the -X side: knurled ABS dial in a steel collar, red seal mark. Stencils "AMBER = CHARGED / RED = DISCHARGED" (canon colours).
- **Screws**: top-plate corners, shroud, switch panel, battery door. Slotted cross heads, shared mesh.
- **Shroud vents**: five slits on the top.
- **Button guard rails** either side of the red thumb button.
- **Wrist lanyard**: steel eyelet boss and ring on the rear, 3 mm coiled rubber cord, cord lock, wrist loop. Geometry, about 5,600 triangles in the coil.
- **Texture**: brushed bare metal (paint, chips, scratches and grime removed on request), panel grooves, stencils ("THIS END TO ASSET", "CHARGE", "ICS-EP CLASS 2 40 V DO NOT SUBMERGE" on the rear, "COMPLIANT WITH PLANETARY DISCIPLINARY PROTOCOL 2.14" on the underside; Doc 2.14 is canon).

v4 additions, author said "do them all" (2026-11-07), all [PROPOSAL]:
- **Rear charging port** with brass contacts and a rubber flap on a strap (flap shown open). "CHG" stencil.
- **Test jack** on the top face: red and black sockets behind a hinged steel flap (shown open), "+" / "-" stencils.
- **Fuse holder** on the +X side: replaceable clear cap in a steel bezel, visible glass fuse, smoked glass ("blown"). "FUSE 2 A" stencil.
- **Mode thumb-wheel**: ridged wheel in a slot on the +X edge for the three modes; a **mode window** with a flag flipped by the shutter ("CONTACT" / "RANGED" labels).
- **Holster rail grooves**: two dovetail grooves on the underside. The belt clip is a separate attachment, `CRD-7-clip`.
- **Hinged prong guard**: hollow steel cap on a spring hinge pin, shown flipped up.
- **Spring-loaded prongs**: shroud plunger slots at x +/-10 mm with plunger blocks, stems and springs, so the pins ride visibly.
- **Story wear, behind `STORY_WEAR = True` in `crd7_textures.py`** (set False for a clean unit): grease smudges where hands go, scratched "R.H." initials on the underside, a mostly worn-off "PROPERTY OF ICS" stencil on the +X side, a Form ICS-W3 paper sliver tucked under the label (a nod to the Yusra-Cache note).
- **Brass asset plate** ("ASSET No. ICS-SEC-1182 / PTKW LVL 5 STORE") with two rivets.
- **Blue evidence tape** ("ICS SECURITY SEALED") across the battery door.
- **Paper maintenance tag** on a string loop from the lanyard eyelet: "CRD-7 S/N 3382", last serviced "CYC 288", next due "CYC 290", handwritten "overdue?".
- Leftover scuffs on the shroud, button and cord were not stripped (offered, not decided).

**Engine-side notes (not geometry):**
- Idle hum rising to a whine as the capacitor charges on fire.
- LCD flicker when the capacitor is low.
- Amber indicator strip fades to red on discharge (swap `CRD-7_indicator` material).
- Mode flag and mode window should follow the wheel; the mode wheel should rotate (pivot at the axle).
- Prong guard, port flaps, test-jack flap and shutter are separate objects with pivots at their hinges for animation.

## Mount points (empties, children of `CRD-7`)
| Empty | For | Note |
|---|---|---|
| `mount_CRD-7X_emitter` | CRD-7X | side aperture, 22 mm seat for the ACS-9 brushed-aluminium ring. Canon: it "does not match" the grey housing |
| `mount_CRD-7R_battery_port` | CRD-7R | rear cap, quarter-turn release, the battery access port |
| `mount_prongs` | | prong pocket |
| `mount_holster_rails` | `CRD-7-clip` | centre of the underside rail grooves, 11 mm forward of the grip centre |

CRD-7R "looks mostly the same": no external part. Heatshrink is visible only through the battery port, so it needs a texture variant rather than new geometry.

## Rig / animation
None on the model. First-person: grip the rear half, thumb on the button. Indicator swaps between amber and red on discharge.

## Budget
Game mesh: **19,120 triangles**, 105 parts (v4 with the brand-kit logo; the new logo mesh adds about 1.3k triangles net over the old four-part placeholder). v3 was 12,992 triangles, 61 parts. The earlier 3,000 budget was lifted by the author for this item. Of those, the lanyard coil is 5,624 and the loop and eyelet ring about 770, so the **lanyard alone is about half**; drop `CRD-7_lanyard_*` (about 6,400) for a version without it (about 11,400). Textures in `Weapon Models/compliance/CRD-7/textures/`, built by `crd7_textures.py`: body atlas 2048 px, trim atlas 1024 px, two 1280 x 528 LCD images, each with albedo/normal/roughness where relevant.

## Export
`Weapon Models/exports/CRD-7.fbx`. Source: `Weapon Models/compliance/CRD-7/CRD-7.blend`, generated by `Weapon Models/compliance/CRD-7/CRD-7_build.py`. Preview stills in `Weapon Models/compliance/CRD-7/previews/`.

## Open questions
1. **Dimensions.** All [PROPOSAL] except the emitter.
2. **Firing control.** Canon names none. [PROPOSAL] a single thumb button on top.
3. **Prongs.** Fixed in v1. Canon is silent on retracting.
4. **Emitter hiding.** Canon calls it "undocumented"; v3 shows it with a shutter slid open beside the lens. Should the shutter be closed by default (hidden), and should the CRD-7X mount then slide it open?
5. **Charged vs discharged.** Canon gives only the light colour. Is there a sound, a hum, a prong glow?
6. ~~Body colour.~~ Settled in v2: darker matte grey.
7. ~~Button colour.~~ v3: red. [PROPOSAL]; canon is silent, so say if you want ICS gold or grey instead.
8. **Invented text.** The label wording, serial number and sticker are [PROPOSAL]; confirm or change.
9. **Look override.** The brief says ICS items have rounded, soft shapes. v3 follows the author's request for a harder, denser look. Keep that for the other compliance tools, or only for the CRD-7?
10. **Lanyard.** Invented. Keep it (adds a physics/cloth candidate in engine), shorten it, or drop it?
11. **LCD wording and the 5-LED row.** Invented; confirm or change.
12. **v4 invented items.** Charge port, test jack, fuse, thumb-wheel, rails, prong guard, plungers, brass plate, evidence tape, service tag, R.H. initials and the ICS-W3 sliver are all [PROPOSAL]. Keep, trim, or drop any?
13. **Prong guard and flaps.** Shown open for display. Should the in-game default be closed?
14. **Story wear.** Is the "R.H." initials mark acceptable, or is it an unintended name hook? Set `STORY_WEAR = False` to remove all of it.
