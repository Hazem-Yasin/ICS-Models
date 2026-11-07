# ICS-Models

3D models for *ICS: Interplanetary Corporate Solutions*. Canon lives in the sibling repo `ICS-Writing`; this repo holds only the art made from it. When the two disagree, canon wins.

Start here: `canon/weapons/OVERVIEW.md` in ICS-Writing, then the spec brief for the item in `_specs/`.

## Layout

| Folder | Holds |
|---|---|
| `Weapon Models/` | Everything for weapons and tools. List of all 20 items: `Weapon Models/WEAPONS.md`. Holds the five folders below |
| `Weapon Models/compliance/` | ICS-issued tools: ACS-9, CCN-Spoofer, CRD-7, EIMU-Jammer, PTKW-Baton |
| `Weapon Models/improvised/` | Maintenance-Bar, Pressurized-Pipe-Tool, Olfactory-Canister, AIDEN-Unit |
| `Weapon Models/found/` | Level-0-Device, Rania-Hatch-Kit, Yusra-Cache |
| `Weapon Models/attachments/` | Modifications, built as parts that mount on a base tool (see below) |
| `_shared/` | Materials, wear textures, hand/grip reference, scale reference (1.80 m player) |
| `Weapon Models/exports/` | Game-ready FBX/GLB, one per item. Never edit by hand. |
| `_specs/` | One brief per item, plus `TEMPLATE.md` |

## Conventions

1. **Name by canon ID.** `Maintenance-Bar.blend`, `CRD-7.blend`, `ACS-9D.blend`. The name is the filename in `ICS-Writing/canon/weapons/`, so the two repos can be matched by script.
2. **Modifications are attachments.** A modification is a separate part parented to its base tool at a named mount point, not a second copy of the weapon. Read `canon/weapons/MODIFICATIONS.md` before modelling a base tool, so the mount points exist.
3. **Write the brief first.** Copy `_specs/TEMPLATE.md`, fill it from the canon file, and mark anything you invent as `[PROPOSAL]`. Model after that.
4. **Shape language.** Compliance tools follow the ICS look in `design/ART_DIRECTION.md`: rounded corners, no sharp edges, soft transitions. Improvised and found items break it on purpose: raw, angular, unfinished. The silhouette tells the player who made the object.
5. **Units and axes.** Blender metric, 1 unit = 1 m, scale applied, Z up, forward -Y. Pivot at the grip.
6. **Exports.** `<CanonID>.fbx`, plus `<CanonID>_LOD1.fbx` if the budget demands one. Material slots named `<CanonID>_<part>`.
7. **Blender 5.2.** Keep `.blend` files in the item's folder; no `.blend1` backups (ignored).
8. **Large files** (`.blend`, `.fbx`, `.glb`, `.png`, `.tga`) are set to Git LFS in `.gitattributes`. Install Git LFS before the first commit of a binary, or remove those lines.

## Order of work

1. Maintenance-Bar (simplest object, raw look, no electronics)
2. The five compliance tools
3. Found items
4. Attachments, in the order the player meets them (Phase 3 onward)

## Status

See `_specs/INDEX.md`.
