# Maintenance-Bar — Maintenance Bar

**Canon:** `ICS-Writing/canon/weapons/improvised/Maintenance-Bar.md`
**Category:** Improvised Tool
**Acquired:** Found. Pulled from a loose bracket in the maintenance corridor within the first hour.
**Base tool:** none. It is the base for BAR-FL (Fragment Launcher).
**Look:** raw. It is ICS structural rebar, not an ICS product: no logo, no label, no rounded finish.
**Status:** modelled v1. Build script `Weapon Models/improvised/Maintenance-Bar/Maintenance-Bar_build.py`; 672 triangles; grip pivot 10 cm from the bent end; bent end rises 24 degrees [PROPOSAL]; sheared end cut at 25 degrees [PROPOSAL]; rib pitch 7 mm [PROPOSAL].

## Silhouette
A plain straight bar with ribbed rebar surface and two cut ends, one freshly sheared, one with a bracket-bent kink.

## Dimensions (cm, from canon)
| Part | Length | Diameter | Weight |
|---|---|---|---|
| Bar | 45 | 1.2 | about 400 g (BAR-FL) |

## Materials and wear
| Part | Material | Condition |
|---|---|---|
| Bar | carbon-steel rebar, matte grey, slightly rough | Rolled ribs, dull scale, rust at one end where it sat in the wall |

Canon: "matte grey, slightly rough to the grip, heavier than it looks." One state is enough for the base item.

## Mount points
BAR-FL (Fragment Launcher) presses a pipe coupling joint over the bar: 22 cm long, 15 mm interior, 3 mm tolerance. Keep the bar a true 12 mm cylinder along its length so the sleeve fits. No mount point is needed on the bar itself.

## Animation / rig needs
None. First-person hold: single hand grip near one end.

## Budget
Under 1,500 triangles. One 1024 px texture set (albedo, normal, roughness).

## Export
`Weapon Models/exports/Maintenance-Bar.fbx`

## Open questions
1. **Where it is found.** The file says "Level 0 maintenance corridor" in the header and "Level 2 maintenance corridor" in the body. Not a modelling problem, but the author should settle it.
2. **Ribbing.** Canon gives no pattern. [PROPOSAL] standard diagonal-rib rebar, because it is the first thing a player reads as rebar.
3. **Does the bar show the Level 0 prying use?** Canon has it prying panels. [PROPOSAL] no separate model; the first-person animation does it.
