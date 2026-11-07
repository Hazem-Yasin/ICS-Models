# CRD-7R — Compliance Reversal

**Canon:** `ICS-Writing/canon/weapons/modifications/CRD-7R — Compliance Reversal.md`
**Category:** Modification (Lethalization). Junction B. Phase 3.
**Base tool:** CRD-7
**Look:** Looks almost the same as the CRD-7 from outside. Canon: "mostly the same". The only visible changes are a sleeve in the battery port and a warmer indicator.
**Status:** modelled (v1, attachment). Internal parts (capacitor, wiring) are not modelled.

## Silhouette
The same grey remote. You only notice it up close, at the rear port, or from the indicator colour.

## Dimensions (cm)
| Part | Size | Source |
|---|---|---|
| Port window (in base) | 0.7 × 0.3 | Base build, `CRD-7_build.py` |
| Heatshrink sleeve diameter | 0.22 | [PROPOSAL] fits the 0.3 cm port height |
| Heatshrink sleeve length | 0.55 | [PROPOSAL] fits the 0.7 cm port width |

## Materials and wear
| Part | Material | Note |
|---|---|---|
| Heatshrink | matte near-black, roughness 0.5 | Canon: "heatshrink tubing"; visible only through the port |
| Indicator (variant) | emissive orange, colour `(1.0, 0.36, 0.05)`, strength 1.9 | Canon: "slightly brighter, warmer orange" than the amber 1.6 of the CRD-7. [PROPOSAL] values |

The indicator is a material swap on the CRD-7's own indicator strip, not new geometry.

## Mount points
| Empty | Role |
|---|---|
| Root `CRD-7R` | Sits on `mount_CRD-7R_battery_port` on the CRD-7. Origin = centre of the port cut. |

The base mount was at the cap centre. It moved to the port centre (z −6.5 mm) to match the cut. Rebuilt in CRD-7 v1.1.

## Rig / animation
None. The quarter-turn release is a canon mechanic, not a model animation.

## Budget
Game mesh: **132 triangles** (sleeve and two leads, 3 parts). Spec target was under 100. Texture: the indicator uses the same emissive material.

## Export
`Weapon Models/exports/CRD-7R.fbx`: root empty `CRD-7R` and sleeve. Source `Weapon Models/attachments/CRD-7R/CRD-7R.blend`, built by `Weapon Models/attachments/CRD-7R/CRD-7R_build.py`. Previews in `Weapon Models/attachments/CRD-7R/previews/` show the CRD-7R with the warm indicator.

## Open questions
1. **Port visibility.** Canon says the sleeve is visible "if you look", so it is modelled as a visible window, not a hidden part. Author to confirm.
2. **Capacitor label.** Canon names the 40 V cap "ICS-C-40V-SAFE" and its replacement "ICS-EL-47". Neither is visible in the model. A label could go on the sleeve later as a texture decal.
3. **Indicator values.** The brightness and colour are [PROPOSAL]. In the v1 renders the warm orange reads as yellow-amber and is hard to tell from the CRD-7's amber, so the canon "slightly brighter, warmer orange" is not yet visible. Push the hue toward red-orange and tune in-engine.
4. **Lethal configuration.** Canon's effects of the 75 V mode are game logic. Nothing in the geometry shows them.
