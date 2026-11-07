# ICS Art Book

> **Images not included.** The ten Wikimedia reference images embedded below are not in this repository, so their links show as broken. Each keeps its own licence: see `CREDITS.md` for authors, licences and Commons links, and download them into `_reference/images/` to restore them.

*The visual reference for every model in this repo. It says what ICS looks like, what we borrow from other games and from the real world, and what we refuse. Canon lives in `ICS-Writing` (`design/ART_DIRECTION.md`, `canon/weapons/`, Doc 2.32); this book turns it into a modeller's checklist. Anything marked **[PROPOSAL]** is a modelling decision the author has not ruled on.*

**Read this first:** the image folders hold only pictures that are Creative Commons or public domain, with credits in `CREDITS.md`. Commercial game art (BioShock, Prey, Alien: Isolation, SOMA, Dead Space, Hardspace: Shipbreaker, Papers, Please) is **not** bundled, because it is copyrighted. For those games this book gives the lesson in words. If you want the stills beside the notes, put them in `private/` (see `private/README.md`). That folder is git-ignored and never committed.

---

## 1. The one-line brief

**The best place you have ever worked, and it never changes.** Warm, rounded, clean, friendly. The horror is what the friendliness is for. (`ART_DIRECTION.md`)

Five pillars, from canon:

| Pillar | What it means for a model |
|---|---|
| **Warm is the threat** | Compliance tools look like office supplies and wellness gadgets, not weapons. |
| **The light does not change; the people do** | Do not dirty or damage a prop to say "it got worse". |
| **Rounded forms** | Bevel every edge. No sharp corners on anything ICS made. (Doc 2.32) |
| **Cold is honest** | Raw, angular, unfinished objects are the ones that tell the truth: Level 0, crawlways, improvised and found items. |
| **Nothing is decorative** | Every object is a BES instrument or evidence. No clutter for its own sake. |

## 2. The two visual registers

Every model belongs to one of these. Decide before you start; it fixes the shape language.

| | **ICS-made** (compliance tools, furniture, fittings) | **Not ICS** (improvised, found, Level 0) |
|---|---|---|
| Edges | Rounded, 3–4 mm bevels on small props | Sharp, cut, snapped, welded |
| Surface | Matte, moulded, even | Raw metal, tape, rust-free but plain (the floor of Level 0 is clean) |
| Colour | Grey, warm white, Deep Blue and Gold accents | Metal grey, tape colours, whatever was to hand |
| Marking | Ouroboros mark (circle with an arc, **no serpent**), rounded sans-serif text | Hand marks, Cycle 1 notation, none |
| Light reading | Looks good under 2,700K | Reads under Level 0 emergency red |

The wrong thing to do is to make an ICS tool look menacing. The right thing is to make it look **reassuring** and let the player work out what it does. The reference for that is the 1950s consumer radio below.

## 3. Palette

All from Doc 2.32 and `ART_DIRECTION.md` unless marked.

| Name | Hex | Use |
|---|---|---|
| ICS Deep Blue | `#1A2E52` | The circle of the mark; badge; accents |
| ICS Warm Gold | `#C9A84C` | The arc of the mark; lettering |
| Body grey **[PROPOSAL]** | about `#2B2D2F` to `#46484A` | Moulded tool bodies (CRD-7 uses a matte grey) |
| Warm white **[PROPOSAL]** | about `#E8E2D4` | Walls, desks, soft goods |
| Indicator amber | emissive, about `#FF7A0D` | "Charged / active" lamps (CRD-7) |
| Emergency red | steady, low, even | Level 0 only |

Light for previews: key 2,700K-ish warm, soft fill, no hard black. Level 0 previews use red monochrome with visible cold-metal specular.

## 4. Real-world references (CC / public domain)

### 4.1 The "friendly tool" look: mid-century consumer design

![Transistor radios TR-1 and T3](images/real-world/Transistor-radio-model-TR-1-left-model-T3-right-LACMA-Octobe.jpg)

*Transistor radios: model TR-1 (left, designed 1954, Regency) and model T3 (right). CC BY-SA 4.0, Superraptor123.*

**Take:** a small hand-held object with one big round dial, a perforated speaker grille, a tiny printed logo and soft corners. This is the template for the CRD-7: palm-sized, calm, with a single circular mark and no visible mechanism. The T3 (right) is the cleaner of the two and the closer match to the ICS "rounded, no sharp angles" rule. The Commons page gives no maker for the T3; treat the Braun link as our own knowledge until checked.
**Avoid:** the cream-and-brass nostalgia. ICS grey is cooler and more clinical than the TR-1.

![Braun Phonosuper SK4](images/real-world/1956-Braun-Phonosuper-SK4-Schneewittchensarg.jpg)

*Braun Phonosuper SK 4, 1956. CC0, Alf van Beem.*

**Take:** restraint. Flat planes, one honest control row, a clear lid, nothing extra. Use it for desk devices, terminals and anything that sits in a Manager's office.

### 4.2 The "institution that looks calm": architecture

![Presidio Modelo courtyard](images/real-world/Presidio-Modelo-Interior-courtyard.jpg)

*Presidio Modelo, interior courtyard, about 1940. Public domain.*

**Take:** repetition and symmetry. Rounded blocks around an open courtyard, identical windows, a central dome, every window facing in. A building that is orderly because it is built to watch. [Check before publishing: the Commons description says only "Interior courtyard" and a 1940 date. The building is a former prison on Isla de la Juventud, Cuba, and our notes describe it as built on a panopticon plan. That is not in the file and has not been verified here.] Use it for facility massing, corridors of identical doors, and the sense that the architecture is looking back. Keep ICS's warmth and curves, and drop the stone.

![Chrysler Building elevator doors](images/real-world/Elevator-doors-of-Chrysler-Building-1927-30.jpg)

*Elevator doors, Chrysler Building, 1927–30. CC BY-SA 4.0, SiefkinDR.*

**Take (as a counterexample):** this is the decorated, ornamental past that BioShock's Rapture borrowed. ICS deliberately is **not** this. Per `ART_DIRECTION.md`, "BioShock has Rapture's art deco because Rapture is a dream that went wrong. ICS is a dream that works." Use it only for the Board-adjacent and upper-level fixtures if the author ever wants old money in the building. **[PROPOSAL]**

### 4.3 The "real working space": a lived-in station

![ISS Destiny laboratory at night](images/real-world/ISS-47-The-International-Space-Station-s-Destiny-Laboratory-.jpg)

*International Space Station, Destiny Laboratory at night, Expedition 47. NASA, public domain.*

**Take:** what a real working space looks like when nothing is hidden: cable bundles, labelled panels, velcro, laptops on arms, status LEDs in green and blue. ICS hides all of this behind panels on the public levels. Use it for **Levels 0 and 5 and the maintenance network**, where the truth is exposed. Also useful for LED colour and size on terminals.

## 5. Game references

### 5.1 The Stanley Parable (images included, CC BY-SA)

The closest tonal match in the list: an office that is ordinary, slightly funny and slightly wrong. We look at its **rooms**, not its jokes.

![Stanley's office](images/stanley-parable/The-Stanley-Parable-Screenshot-01.jpg)

*Stanley's office. CC BY-SA 3.0, Galactic Cafe.*

**Take:** one pool of light in a large dark room, a worker seen from behind, and furniture that is dull and specific (grey filing cabinet, corner desk, in-trays). Staging for the Work Floor B desks. **Avoid:** the dark. The ICS floor is bright.

![Office floor with numbered doors](images/stanley-parable/The-Stanley-Parable-Screenshot-03.jpg)

*Open-plan floor, doors 420 and 425. CC BY-SA 3.0, Galactic Cafe.*

**Take:** a floor where every surface is the same beige, every door is numbered, the ceiling is a grid of fluorescent panels, and the only decoration is a plant. That is the ICS corridor in outline. Replace the green-beige with 2,700K warm white; the repeated numbered doors and the ceiling grid are right.

![Ultra Deluxe office area](images/stanley-parable/Stanley-parable-UD-screenshot.jpg)

*The Stanley Parable: Ultra Deluxe, office area. CC BY-SA 4.0, Viator NL.*

**Take:** a cleaner, higher-resolution version of the same idea; useful for how to light a modern office with tight, saturated colour.

![Executive office](images/stanley-parable/The-Stanley-Parable-Screenshot-05.jpg)

*An executive's room with leather, wood panelling and a painting. CC BY-SA 3.0, Galactic Cafe.*

**Take (as contrast):** the old-fashioned executive room. In ICS the Manager and Director offices are *not* this; they are frosted glass and warm composite (`canon/facility/Level 3.md`). Use only if you need a contrast for the Board's rooms.

![Maintenance space with red light](images/stanley-parable/The-Stanley-Parable-Screenshot-07.jpg)

*A service space: ductwork, shelving of boxes, red spill from a doorway. CC BY-SA 3.0, Galactic Cafe.*

**Take:** the **Level 0** read. Blue-grey ducts, plain cardboard on a wire shelf, red light entering through an open door. Raw pipes plus red emergency light is the canon Level 0. Keep the floors clean (canon).

### 5.2 BioShock

*No images bundled. Drop your own in `private/bioshock/`.*

**Take:** an unmistakable place built on one idea, where every prop belongs to the same design language, and where audio logs and posters tell the history. For ICS this means every prop must obey the same shape language, and posters rotate while smiles stay.
**Do not copy:** art deco and decay. ICS's look is mid-century clean and does not rust. The author's phrase in canon: "in the style of BioShock" is about *how much the environment tells*, not about the look.

### 5.3 Prey (2017)

*No images bundled. Drop your own in `private/prey/`.*

**Take:** a space station that is half corporate lobby, half laboratory, with a retro-futurist finish and objects the player can pick up and use. The lesson for modelling is **objects that look like office supplies but are tools**. Hearth and ICS-OS are acknowledged in the handoff as taking cues from Prey's terminals and email.
**Avoid:** the Typhon organic forms. ICS has no creature design.

### 5.4 Alien: Isolation

*No images bundled. Drop your own in `private/alien-isolation/`.*

**Take:** "used future." Chunky 1970s industrial controls, CRT monitors, cable and tape on a working station. This is the register for the **Level 0 and maintenance** props: chunky, labelled, practical, and lit by a few coloured lamps.
**Avoid:** the grime. ICS stays clean, even in the red.

### 5.5 SOMA

*No images bundled. Drop your own in `private/soma/`.*

**Take:** isolated, working machinery in a deep, enclosed place; terminals and consoles that look half-human because someone has left things on them. Useful for how a station reads as inhabited, and for terminals with a personal note stuck to them (the Manager's `smiling-man` note, `design/DEVICES.md`).
**Avoid:** the fleshy-machine merge. ICS is human and mechanical, never both.

### 5.6 Dead Space

*No images bundled. Drop your own in `private/dead-space/`.*

**Take:** UI that lives *in the world*: a gauge on the tool itself, not a menu. For ICS tools, the amber charge lamp on the CRD-7 is exactly this: state is read from the object. Industrial detail on hard-surface props also reads well.
**Avoid:** gore, dismemberment, and anything weapon-shaped. Canon: no firearms and no gore.

### 5.7 Hardspace: Shipbreaker

*No images bundled. Drop your own in `private/shipbreaker/`.*

**Take:** corporate-owned labour shown through clean, readable props: colour-coded tools, hazard stripes, a contract on the wall. A good model for how **maintenance tools** (the Maintenance-Bar) are marked with a company hand, and for readable silhouettes at distance.

### 5.8 Papers, Please

*No images bundled. Drop your own in `private/papers-please/`.*

**Take:** bureaucratic objects as the whole aesthetic: stamps, forms, a booth. Use for the paper side of ICS: badges, forms with the ICS-IR3 layout, stamps, and clipboards (CLEO's prop).

## 6. Weapon and tool design rules

Canon: three categories only. (`canon/weapons/OVERVIEW.md`, `MODIFICATIONS.md`)

| Category | Look | Examples | Reference |
|---|---|---|---|
| **Compliance** | Looks like a wellness gadget or an office device. Rounded, matte, one mark, one lamp. Never looks like a weapon. | CRD-7, ACS-9 | Braun and Regency radios (4.1) |
| **Improvised** | Looks like what it is made from. Angular, taped, plain. | Maintenance-Bar | ISS photo, Stanley Parable 07 (4.3, 5.1) |
| **Found** | A real object doing something it was not made for. Do not restyle it. | None briefed yet | Any real photo of that object |

Modelling rules, from the CRD-7 build:

1. **Name by canon ID** and write the brief in `_specs/` first. Dimensions come from canon, with [PROPOSAL] flags where canon is silent.
2. **Modifications are attachments**, not separate meshes. Give the base tool **mount-point empties** (`mount_<attachment>`) and build the attachment separately.
3. **State on the object.** Charge or contact is shown by a lamp on the tool (amber charged, red discharged), not by a HUD.
4. **Printed text and logos are decals**, not geometry, in the game mesh. Preview geometry is fine.
5. **Budget:** hand-held tool under 3,000 triangles. (CRD-7 v1 is 2,448.)
6. Blender metric, 1 unit = 1 m, Z up, forward -Y, pivot at the grip.

## 7. Never

Copied from `ART_DIRECTION.md` section 8, because it is the easiest thing to get wrong:

- No gore, no dismemberment, no blood.
- No horror lighting on Levels 1–6.
- No dirty floors on Level 0. The floor is clean, and nothing is cleaning it.
- No mascots redrawn as sinister. Smiles stay as they are.
- No colour grade that says "dystopia".
- No firearms.

## 8. Open art questions (from canon)

1. Pre-ICS glyphs on Level 0 have no visual reference yet.
2. Mascot rendering style: colours and shapes are canon, rendering is not.
3. Palette for the PTKW wing: grey with white lettering for the badge, nothing for the environment.
4. How the Board is ever shown. Currently: never.
5. Whether the CRD-7 side emitter is visible (pending author ruling).

## 9. What is missing

Honest list of gaps in this collection:

- **No licensed game screenshots** except The Stanley Parable. Everything else must come from you via `private/`.
- **No ICS-specific concept art.** The mascots, the mark and the corridors exist only as text so far.
- **No close references for hard-surface tools** (grips, hinges, button feel). The best next additions are photos of 1950s–70s hand-held devices: Braun, Olivetti, early remote controls, hearing aids.
- **No reference for the Level 0 maintenance look in colour** other than the Stanley Parable service room and the ISS photo.

Good next collections (all searchable as CC/PD on Wikimedia Commons): Dieter Rams product shots, 1960s office interiors, Olivetti typewriters, mid-century hospital and clinic equipment, rebar and steel pipe close-ups for the Maintenance-Bar.

---

*→ See: `CREDITS.md` for licences. `private/README.md` for adding your own stills. `../_specs/` for per-model briefs. `ICS-Writing/design/ART_DIRECTION.md` for canon.*
