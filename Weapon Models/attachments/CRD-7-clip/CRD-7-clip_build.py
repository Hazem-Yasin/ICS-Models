"""
CRD-7-clip -- belt/holster clip. Attachment build script for Blender 5.x.  [PROPOSAL] (not in canon)

Run:  blender --background --python CRD-7-clip_build.py -- <ICS-Models root>
Needs: Weapon Models/compliance/CRD-7/CRD-7.blend (run CRD-7_build.py first; it holds mount_holster_rails).
Writes: attachments/CRD-7-clip/CRD-7-clip.blend, exports/CRD-7-clip.fbx, previews/*.png
Spec:   _specs/CRD-7.md (holster rails)

A spring-steel clip with two dovetail tongues that slide into the underside rail grooves from the rear
(the battery door is at the rear, so the clip stops short of it). Origin = the mount_holster_rails empty,
centre of the rails on the underside face. +Z points into the body, -Z away from it, Y runs along the tool.
"""
import math
import os
import sys

import bmesh
import bpy

ROOT = sys.argv[sys.argv.index("--") + 1]
sys.path.insert(0, os.path.join(ROOT, "_shared"))
import studio  # noqa: E402

OUT = os.path.join(ROOT, "Weapon Models", "attachments", "CRD-7-clip")
PREVIEW_DIR = os.path.join(OUT, "previews")
EXPORT_DIR = os.path.join(ROOT, "Weapon Models", "exports")
BASE_BLEND = os.path.join(ROOT, "Weapon Models", "compliance", "CRD-7", "CRD-7.blend")
os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)
mm = 0.001
RAIL_X = 18.5        # matches CRD-7_build.py

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def link(ob):
    scene.collection.objects.link(ob)
    return ob


def extrude_x(name, pts_yz, x0, x1):
    """Closed (y, z) outline in mm extruded along X from x0 to x1 (mm)."""
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new((x0 * mm, y * mm, z * mm)) for y, z in pts_yz])
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=((x1 - x0) * mm, 0, 0), verts=[e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


def extrude_y(name, pts_xz, y0, y1):
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new((x * mm, y0 * mm, z * mm)) for x, z in pts_xz])
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, (y1 - y0) * mm, 0), verts=[e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


steel = bpy.data.materials.new("CRD-7-clip_steel")
steel.use_nodes = True
b = steel.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.20, 0.205, 0.22, 1)
b.inputs["Roughness"].default_value = 0.38
b.inputs["Metallic"].default_value = 0.9


def finish(ob, angle=40):
    ob.data.materials.append(steel)
    for p in ob.data.polygons:
        p.use_smooth = True
    try:
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
    except Exception:
        pass


parts = []
# tongues: neck 3 mm at the underside face, 4.4 mm head 2.5 mm up inside the groove; 76 mm long, stops 2 mm short of each groove end
for sx in (-1, 1):
    t = extrude_y(f"CRD-7-clip_tongue_{'L' if sx < 0 else 'R'}",
                  [(sx * (RAIL_X - 1.35), 0), (sx * (RAIL_X + 1.35), 0), (sx * (RAIL_X + 2.05), 2.5), (sx * (RAIL_X - 2.05), 2.5)],
                  -37.0, 37.0)
    finish(t)
    parts.append(t)
# base plate under the body
plate = extrude_y("CRD-7-clip_plate", [(-23.0, -0.4), (23.0, -0.4), (23.0, -2.4), (-23.0, -2.4)], -37.0, 37.0)
finish(plate)
parts.append(plate)
# spring strap: leaves the rear edge of the plate, drops 22 mm, folds forward (side profile in Y-Z, 34 mm wide)
strap = extrude_x("CRD-7-clip_strap",
                  [(37.0, -2.4), (37.0, -0.4), (40.5, -0.4), (40.5, -26.0), (14.0, -26.0), (14.0, -23.6), (38.1, -23.6), (38.1, -2.4)],
                  -17.0, 17.0)
finish(strap)
parts.append(strap)
lip = extrude_x("CRD-7-clip_lip", [(14.0, -23.6), (14.0, -26.0), (10.5, -21.0), (12.7, -20.2)], -17.0, 17.0)
finish(lip)
parts.append(lip)
for sx in (-1, 1):                      # two rivets on the plate
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=1.4 * mm, radius2=1.2 * mm, depth=0.7 * mm)
    bmesh.ops.translate(bm, vec=(sx * 12.0 * mm, 20.0 * mm, -2.75 * mm), verts=bm.verts)
    me = bpy.data.meshes.new("rv")
    bm.to_mesh(me)
    bm.free()
    rv = link(bpy.data.objects.new(f"CRD-7-clip_rivet_{'L' if sx < 0 else 'R'}", me))
    finish(rv, 60)
    parts.append(rv)

root = link(bpy.data.objects.new("CRD-7-clip", None))
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 0.02
for o in parts:
    o.parent = root
tris = sum(len(p.vertices) - 2 for o in parts for p in o.data.polygons)
print(f"STATS parts={len(parts)} triangles={tris}")

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CRD-7-clip.blend"))
bpy.ops.object.select_all(action="DESELECT")
for o in [root] + parts:
    o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(EXPORT_DIR, "CRD-7-clip.fbx"), use_selection=True,
                         object_types={"MESH", "EMPTY"}, apply_scale_options="FBX_SCALE_ALL",
                         add_leaf_bones=False, mesh_smooth_type="FACE")

# ---- previews: on the CRD-7, flipped to show the underside --------------------
base = studio.append_base(scene, BASE_BLEND)
mount = base["mount_holster_rails"]
root.parent = base["CRD-7"]                       # rides with the tool; mount is parented to the same root
root.location = mount.location.copy()
base["CRD-7"].rotation_euler = (0, math.pi, 0)    # flip over so the clip faces the camera (about Y: prongs stay at the top)
bpy.context.view_layer.update()
print("MOUNT", tuple(round(v, 4) for v in mount.location))
cam = studio.setup(scene, floor_z=-0.0152 - 0.0275)
pv = lambda n: os.path.join(PREVIEW_DIR, f"CRD-7-clip_{n}.png")  # noqa: E731
cam.shot(pv("hero"), (0.20, 0.14, 0.17), (0, -0.030, 0.02), 85)
cam.shot(pv("side"), (0.30, -0.03, 0.05), (0, -0.01, 0.025), 90)
print("DONE")
