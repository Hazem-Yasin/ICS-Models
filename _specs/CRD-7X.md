# CRD-7X — Extended Burst

**Canon:** `ICS-Writing/canon/weapons/modifications/CRD-7X — Extended Burst.md`
**Category:** Modification (Amplification). Junction A. Phase 2.
**Base tool:** CRD-7
**Acquired:** Improvised at Junction A, from an ACS-9's secondary focusing ring.
**Look:** ICS-made part (brushed aluminium from an ACS-9). It is the one bright thing on the grey housing, and canon says it "does not match".
**Status:** modelled (v1, attachment). Not textured.

## Silhouette
A bright metal ring on the side of a grey remote, like a lens hood.

## Dimensions (cm)
| Part | Size | Source |
|---|---|---|
| Ring outer diameter | 2.2 | Canon: "The ring is 22mm diameter" |
| Ring bore | 1.5 | [PROPOSAL] matches the CRD-7 side aperture (15 mm), so the ring fits over it |
| Ring depth | 0.4 | [PROPOSAL] |

Canon also calls the ring "identical" to the aperture. That cannot be true of 22 mm and 15 mm, so the model follows the numbers. See open question 1.

## Materials and wear
| Part | Material | Note |
|---|---|---|
| Ring | brushed aluminium, metallic 1.0, roughness 0.3 | Canon: "brushed aluminum, slightly shinier than the matte grey housing" |

## Mount points
| Empty | Role |
|---|---|
| Root `CRD-7X` | Sits on `mount_CRD-7X_emitter` on the CRD-7. Origin = aperture centre on the side face. Local +X points out of the face. |

The ring's back face sits on the side face, covering the 15 mm recess.

## Rig / animation
None. The ring does not move, and nothing on it lights up.

## Budget
Game mesh: **880 triangles** (ring and epoxy bead, 2 parts). Spec target was under 500; the 40-segment revolve is denser than needed and can be halved. Texture: none (flat material).

## Export
`Weapon Models/exports/CRD-7X.fbx`: root empty `CRD-7X` and ring. Source `Weapon Models/attachments/CRD-7X/CRD-7X.blend`, built by `Weapon Models/attachments/CRD-7X/CRD-7X_build.py`. The build also renders the ring attached to the CRD-7 in `Weapon Models/attachments/CRD-7X/previews/`.

## Open questions
1. **Ring size.** Canon gives 22 mm and also says the ring matches the 15 mm aperture. The model uses 22 mm outer and 15 mm bore. Author to rule.
2. **Lens.** The fixed lens that disperses the field belongs to the emitter (CRD-7 canon), so no lens is modelled in the ring.
3. **Visibility of the emitter.** CRD-7 open question 4 is still open. If the side emitter is hidden, this ring needs a cover too.
4. **Scanner.** `MODIFICATIONS.md` says a modified tool flags on the Level 5 scanner. That is game logic, not geometry.
