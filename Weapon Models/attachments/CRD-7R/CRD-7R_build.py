"""
CRD-7R -- Compliance Reversal. Attachment build script for Blender 5.x.

Run:  blender --background --python CRD-7R_build.py -- <ICS-Models root>
Needs: Weapon Models/compliance/CRD-7/CRD-7.blend (run CRD-7_build.py first; it holds the mount empty).
Writes: Weapon Models/attachments/CRD-7R/CRD-7R.blend, Weapon Models/exports/CRD-7R.fbx, Weapon Models/attachments/CRD-7R/previews/*.png
Spec:   _specs/CRD-7R.md

Canon: the CRD-7R "looks mostly the same". The one visible change is the heatshrink
on the rewired discharge circuit, seen through the battery port, and a warmer indicator.
The part is the heatshrink sleeve (origin = centre of the port, long axis = X).
The indicator change is a material swap on the base CRD-7's own indicator strip.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix

ROOT = sys.argv[sys.argv.index("--") + 1]
sys.path.insert(0, os.path.join(ROOT, "_shared"))
import studio  # noqa: E402

OUT = os.path.join(ROOT, "Weapon Models", "attachments", "CRD-7R")
PREVIEW_DIR = os.path.join(OUT, "previews")
EXPORT_DIR = os.path.join(ROOT, "Weapon Models", "exports")
BASE_BLEND = os.path.join(ROOT, "Weapon Models", "compliance", "CRD-7", "CRD-7.blend")
os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# ---- dimensions (m) [PROPOSAL] ---------------------------------------------
SLEEVE_R = 0.0011
SLEEVE_LEN = 0.0055      # port window is 7 mm wide
SLEEVE_Y = -0.0008       # sits inside the 1.6 mm cap, behind the face

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def link(ob):
    scene.collection.objects.link(ob)
    return ob


def mat(name, color, rough, metal=0.0, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def cyl_x(name, r, length, segs=20):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=length)
    bmesh.ops.transform(bm, matrix=Matrix.Rotation(math.radians(90), 4, "Y"), verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    for p in me.polygons:
        p.use_smooth = True
    return ob


# the sleeve is a short tube lying across the port, with a flat swage at each end
M_SHRINK = mat("CRD-7R_heatshrink", (0.02, 0.02, 0.022), 0.5)
sleeve = cyl_x("CRD-7R_heatshrink", SLEEVE_R, SLEEVE_LEN)
sleeve.data.materials.append(M_SHRINK)
sleeve.location = (0, SLEEVE_Y, 0)

# the original blue cylinder cap's wire tails, just visible as two short leads
leads = []
for i, dz in enumerate((-0.0007, 0.0007)):
    w = cyl_x(f"CRD-7R_lead_{i}", 0.00035, 0.0016, 8)
    w.data.materials.append(mat(f"CRD-7R_lead_{i}", (0.65, 0.33, 0.16), 0.35, 1.0))
    w.location = (SLEEVE_LEN / 2 + 0.0006, SLEEVE_Y, dz)
    leads.append(w)

root = link(bpy.data.objects.new("CRD-7R", None))
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 0.02
for o in [sleeve] + leads:
    o.parent = root

geo = [sleeve] + leads
tris = sum(len(p.vertices) - 2 for o in geo for p in o.data.polygons)
print(f"STATS parts={len(geo)} triangles={tris}")

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CRD-7R.blend"))
bpy.ops.object.select_all(action="DESELECT")
for o in [root] + geo:
    o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(EXPORT_DIR, "CRD-7R.fbx"), use_selection=True,
                         object_types={"MESH", "EMPTY"}, apply_scale_options="FBX_SCALE_ALL",
                         add_leaf_bones=False, mesh_smooth_type="FACE")

# ---- previews: attached to the CRD-7, indicator swapped to the warm orange ---
base = studio.append_base(scene, BASE_BLEND)
mount = base["mount_CRD-7R_battery_port"]
bpy.context.view_layer.update()
root.location = mount.matrix_world.translation.copy()
print("MOUNT", tuple(round(v, 4) for v in root.location))

ind = base["CRD-7_indicator"]
warm = mat("CRD-7R_indicator_warm", (1.0, 0.30, 0.02), 0.3, emit=(1.0, 0.36, 0.05), strength=1.9)
ind.data.materials[0] = warm

cam = studio.setup(scene, floor_z=-0.0152)
pv = lambda n: os.path.join(PREVIEW_DIR, f"CRD-7R_{n}.png")  # noqa: E731
tx, ty, tz = root.location
cam.shot(pv("hero"), (0.30, -0.36, 0.20), (0, -0.045, 0), 95)
cam.shot(pv("rear_indicator"), (-0.34, 0.30, 0.16), (0, -0.045, 0), 95)
cam.shot(pv("port_closeup"), (tx, ty + 0.07, tz + 0.012), (tx, ty, tz), 100)
print("DONE")
