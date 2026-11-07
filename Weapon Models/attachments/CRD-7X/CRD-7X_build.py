"""
CRD-7X -- Extended Burst. Attachment build script for Blender 5.x.

Run:  blender --background --python CRD-7X_build.py -- <ICS-Models root>
Needs: Weapon Models/compliance/CRD-7/CRD-7.blend (run CRD-7_build.py first; it holds the mount empty).
Writes: Weapon Models/attachments/CRD-7X/CRD-7X.blend, Weapon Models/exports/CRD-7X.fbx, Weapon Models/attachments/CRD-7X/previews/*.png
Spec:   _specs/CRD-7X.md

The part is the ACS-9 focusing ring (22 mm outer, brushed aluminium) plus the epoxy
bead around it. Origin = centre of the aperture on the side face; +X points out of the face.
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

OUT = os.path.join(ROOT, "Weapon Models", "attachments", "CRD-7X")
PREVIEW_DIR = os.path.join(OUT, "previews")
EXPORT_DIR = os.path.join(ROOT, "Weapon Models", "exports")
BASE_BLEND = os.path.join(ROOT, "Weapon Models", "compliance", "CRD-7", "CRD-7.blend")
os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# ---- dimensions (m) --------------------------------------------------------
R_OUT = 0.011        # canon: 22 mm ring
R_IN = 0.0075        # [PROPOSAL] fits the 15 mm aperture
DEPTH = 0.004        # [PROPOSAL]
CHAMFER = 0.0004
BEAD = 0.0008        # [PROPOSAL] epoxy fillet width

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def link(ob):
    scene.collection.objects.link(ob)
    return ob


def spin_profile(name, pts, steps=40):
    """Revolve a closed profile (x = radius, z = along the axis) 360 degrees about Z."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, 0, z)) for x, z in pts]
    es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), dvec=(0, 0, 0),
                   angle=math.tau, steps=steps, use_merge=True, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # Z axis -> X axis (out of the side face)
    bmesh.ops.transform(bm, matrix=Matrix.Rotation(math.radians(90), 4, "Y"), verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


def mat(name, color, rough, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def finish(ob, material, angle=40):
    ob.data.materials.append(material)
    for p in ob.data.polygons:
        p.use_smooth = True
    try:
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
    except Exception:
        pass
    return ob


c = CHAMFER
ring = spin_profile("CRD-7X_ring", [
    (R_IN, 0), (R_OUT - c, 0), (R_OUT, c), (R_OUT, DEPTH - c),
    (R_OUT - c, DEPTH), (R_IN + c, DEPTH), (R_IN, DEPTH - c),
])
finish(ring, mat("CRD-7X_ring_aluminium", (0.80, 0.81, 0.83), 0.32, 1.0))

# epoxy fillet where the ring meets the housing (canon: "epoxied in place")
bead = spin_profile("CRD-7X_epoxy", [
    (R_OUT - 0.0003, 0), (R_OUT + BEAD, 0), (R_OUT + BEAD * 0.25, BEAD * 0.55), (R_OUT - 0.0003, BEAD * 0.9),
], steps=40)
finish(bead, mat("CRD-7X_epoxy", (0.62, 0.50, 0.30), 0.35), 60)

root = link(bpy.data.objects.new("CRD-7X", None))
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 0.02
for o in (ring, bead):
    o.parent = root

tris = sum(len(p.vertices) - 2 for o in (ring, bead) for p in o.data.polygons)
print(f"STATS parts=2 triangles={tris}")

# ---- save and export (attachment on its own) --------------------------------
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CRD-7X.blend"))
bpy.ops.object.select_all(action="DESELECT")
for o in (root, ring, bead):
    o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(EXPORT_DIR, "CRD-7X.fbx"), use_selection=True,
                         object_types={"MESH", "EMPTY"}, apply_scale_options="FBX_SCALE_ALL",
                         add_leaf_bones=False, mesh_smooth_type="FACE")

# ---- previews: attached to the CRD-7 ----------------------------------------
base = studio.append_base(scene, BASE_BLEND)
mount = base["mount_CRD-7X_emitter"]
bpy.context.view_layer.update()
root.location = mount.matrix_world.translation.copy()
print("MOUNT", tuple(round(v, 4) for v in root.location))

cam = studio.setup(scene, floor_z=-0.0152)
pv = lambda n: os.path.join(PREVIEW_DIR, f"CRD-7X_{n}.png")  # noqa: E731
tx, ty, tz = root.location
cam.shot(pv("hero"), (0.30, -0.36, 0.20), (0, -0.045, 0), 95)
cam.shot(pv("side"), (tx + 0.16, ty - 0.02, 0.05), (tx, ty, 0), 100)
cam.shot(pv("closeup"), (tx + 0.06, ty - 0.035, 0.02), (tx, ty, 0), 100)
print("DONE")
