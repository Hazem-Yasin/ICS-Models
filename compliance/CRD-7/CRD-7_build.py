"""
CRD-7 -- Compliance Restraint Device. Build script for Blender 5.x.

Run:  blender --background --python CRD-7_build.py -- <ICS-Models root>
Writes: compliance/CRD-7/CRD-7.blend, exports/CRD-7.fbx, compliance/CRD-7/previews/*.png
Spec:   _specs/CRD-7.md   Canon: ICS-Writing/canon/weapons/compliance/CRD-7 ...md

Units: metres. Forward = -Y (the prongs). Up = +Z. Origin = centre of the grip.
Body coordinates below are measured from the body centre; OFFY moves the
grip centre to the origin.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = sys.argv[sys.argv.index("--") + 1]
PREVIEW_DIR = os.path.join(ROOT, "compliance", "CRD-7", "previews")
EXPORT_DIR = os.path.join(ROOT, "exports")
os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# ---- dimensions (m) --------------------------------------------------------
BODY_W, BODY_L, BODY_H = 0.050, 0.115, 0.030     # [PROPOSAL] canon: "size of a TV remote"
BODY_R = 0.004                                    # edge radius; flat side seat stays 22 mm
TOP = BODY_H / 2
HOUS_W, HOUS_L, HOUS_H = 0.038, 0.030, 0.022      # prong shroud
HOUS_Y = -0.0675
POCKET_DEPTH = 0.009
PRONG_R, PRONG_SPACING = 0.0022, 0.020
OFFY = -0.025                                     # grip centre -> origin

# ---- scene reset -----------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
coll = scene.collection


def link(ob):
    coll.objects.link(ob)
    return ob


def mesh_from_bm(name, bm):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


def place(ob, x, y, z):
    ob.location = (x, y + OFFY, z)
    return ob


def smooth(ob, angle=35):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
        except Exception:
            for p in ob.data.polygons:
                p.use_smooth = True


def rbox(name, size, r, segs=5):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    if r > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, offset_type="OFFSET",
                        profile=0.5, segments=segs, affect="EDGES", clamp_overlap=True)
    return mesh_from_bm(name, bm)


def cyl(name, r, depth, axis="Z", segs=48):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=depth)
    if axis == "X":
        m = Matrix.Rotation(math.radians(90), 4, "Y")
    elif axis == "Y":
        m = Matrix.Rotation(math.radians(90), 4, "X")
    else:
        m = Matrix.Identity(4)
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    return mesh_from_bm(name, bm)


def sphere(name, r, segs=24):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=segs // 2, radius=r)
    return mesh_from_bm(name, bm)


def arc(name, r_in, r_out, a0, a1, thick, steps=24):
    """Flat annular arc from angle a0 to a1 (degrees), extruded +Z."""
    bm = bmesh.new()
    outer = [(r_out * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
              r_out * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]
    inner = [(r_in * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
              r_in * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps, -1, -1)]
    verts = [bm.verts.new((x, y, 0)) for x, y in outer + inner]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    mv = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, thick), verts=mv)
    return mesh_from_bm(name, bm)


def boolean_cut(ob, cutter):
    mod = ob.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


# ---- materials -------------------------------------------------------------
def mat(name, color, rough=0.5, metal=0.0, emit=None, strength=0.0):
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


M_BODY = mat("CRD-7_body", (0.17, 0.175, 0.185), 0.6)          # matte grey
M_SHROUD = mat("CRD-7_shroud", (0.075, 0.078, 0.085), 0.6)
M_METAL = mat("CRD-7_prong", (0.72, 0.73, 0.75), 0.30, 1.0)
M_BLUE = mat("CRD-7_logo_blue", (0.012, 0.027, 0.085), 0.45)  # ICS Deep Blue #1A2E52
M_GOLD = mat("CRD-7_logo_gold", (0.58, 0.39, 0.075), 0.35, 0.8)  # ICS Warm Gold #C9A84C
M_TEXT = mat("CRD-7_text", (0.80, 0.80, 0.78), 0.6)
M_BUTTON = mat("CRD-7_button", (0.70, 0.70, 0.68), 0.5)
M_LENS = mat("CRD-7_emitter_lens", (0.02, 0.02, 0.03), 0.12)
M_AMBER = mat("CRD-7_indicator_charged", (1.0, 0.45, 0.02), 0.3, emit=(1.0, 0.5, 0.05), strength=1.6)
M_RED = mat("CRD-7_indicator_discharged", (0.9, 0.02, 0.02), 0.3, emit=(1.0, 0.03, 0.02), strength=1.6)
M_RED.use_fake_user = True   # swap onto the indicator for the discharged state


def finish(ob, material, angle=35):
    ob.data.materials.append(material)
    smooth(ob, angle)
    return ob


parts = []

# ---- body ------------------------------------------------------------------
body = rbox("CRD-7_body", (BODY_W, BODY_L, BODY_H), BODY_R, 3)
place(body, 0, 0, 0)

# side emitter recess (+X): 15 mm aperture, 2.5 mm deep, undocumented in the training module
cut = cyl("cut_emitter", 0.0075, 0.006, "X", 32)
place(cut, BODY_W / 2, 0, 0)
boolean_cut(body, cut)

# rear cap: quarter-turn release slot and a small battery-port recess
cap = cyl("CRD-7_cap", 0.0105, 0.0016, "Y", 32)
place(cap, 0, BODY_L / 2, 0)
slot = rbox("cut_slot", (0.015, 0.0016, 0.0017), 0)
place(slot, 0, BODY_L / 2 + 0.0008, 0.0)
boolean_cut(cap, slot)
port = rbox("cut_port", (0.007, 0.0016, 0.003), 0)
place(port, 0, BODY_L / 2 + 0.0008, -0.0065)
boolean_cut(cap, port)
finish(cap, M_SHROUD, 40)

finish(body, M_BODY, 40)

# ---- prong shroud and prongs ----------------------------------------------
shroud = rbox("CRD-7_shroud", (HOUS_W, HOUS_L, HOUS_H), 0.004, 5)
place(shroud, 0, HOUS_Y, 0)
front = HOUS_Y - HOUS_L / 2
pocket = rbox("cut_pocket", (0.030, POCKET_DEPTH + 0.0005, 0.013), 0.001, 3)
place(pocket, 0, front + (POCKET_DEPTH - 0.0005) / 2, 0)   # opens through the front face
boolean_cut(shroud, pocket)
finish(shroud, M_SHROUD, 40)

pocket_bottom = front + POCKET_DEPTH          # y of the pocket floor
prong_len = 0.018
for sx, tag in ((-1, "L"), (1, "R")):
    p = cyl(f"CRD-7_prong_{tag}", PRONG_R, prong_len, "Y", 16)
    place(p, sx * PRONG_SPACING / 2, pocket_bottom - prong_len / 2, 0)
    finish(p, M_METAL, 60)
    tip = sphere(f"CRD-7_prong_tip_{tag}", PRONG_R, 12)
    place(tip, sx * PRONG_SPACING / 2, pocket_bottom - prong_len, 0)
    finish(tip, M_METAL, 90)
    collar = cyl(f"CRD-7_prong_collar_{tag}", PRONG_R * 1.6, 0.003, "Y", 16)
    place(collar, sx * PRONG_SPACING / 2, pocket_bottom - 0.0015, 0)
    finish(collar, M_SHROUD, 60)

# ---- emitter lens (+X), sits at the bottom of the recess -------------------
lens = cyl("CRD-7_emitter_lens", 0.0069, 0.0004, "X", 24)
place(lens, BODY_W / 2 - 0.0025 + 0.0002, 0, 0)
finish(lens, M_LENS, 40)

# ---- contact indicator (-X side) ------------------------------------------
ind = rbox("CRD-7_indicator", (0.0007, 0.024, 0.0045), 0.0002, 2)
place(ind, -BODY_W / 2 + 0.0001, -0.002, 0)
finish(ind, M_AMBER, 40)

# ---- thumb button [PROPOSAL] ----------------------------------------------
btn = rbox("CRD-7_button", (0.017, 0.012, 0.0035), 0.0014, 4)
place(btn, 0, 0.022, TOP + 0.0008)
finish(btn, M_BUTTON, 40)

# ---- logo: ouroboros mark, no serpent -- a deep-blue circle with a gold arc --
LOGO_Y = -0.023
disc = cyl("CRD-7_logo_disc", 0.0105, 0.0006, "Z", 32)
place(disc, 0, LOGO_Y, TOP + 0.0001)
finish(disc, M_BLUE, 30)
gold = arc("CRD-7_logo_arc", 0.0058, 0.0074, 40, 330, 0.0005)
place(gold, 0, LOGO_Y, TOP + 0.0004)
finish(gold, M_GOLD, 30)
for ang in (40, 330):                           # round the arc ends
    cx = 0.0066 * math.cos(math.radians(ang))
    cy = 0.0066 * math.sin(math.radians(ang))
    capd = cyl(f"CRD-7_logo_arc_end_{ang}", 0.0008, 0.0005, "Z", 8)
    place(capd, cx, LOGO_Y + cy, TOP + 0.0004 + 0.00025)
    finish(capd, M_GOLD, 30)


# ---- printed text ----------------------------------------------------------
def text(name, s, size, y):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = s
    cu.size = size
    cu.extrude = 0.00012
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = link(bpy.data.objects.new(name, cu))
    ob.rotation_euler = (0, 0, math.pi)          # reads from the grip end
    place(ob, 0, y, TOP + 0.00015)
    cu.materials.append(M_TEXT)
    cu.resolution_u = 2
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    mob = link(bpy.data.objects.new(name + "_mesh", me))
    mob.matrix_world = ob.matrix_world
    bpy.data.objects.remove(ob, do_unlink=True)
    return mob


text("CRD-7_text_1", "Asset Welfare Series - CRD-7", 0.0021, -0.002)
text("CRD-7_text_2", "For compassionate use only.", 0.0018, 0.002)

# ---- root, mount points -----------------------------------------------------
root = link(bpy.data.objects.new("CRD-7", None))
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 0.02
mounts = {
    "mount_CRD-7X_emitter": (BODY_W / 2, 0, 0),                  # 15 mm aperture, 22 mm seat
    "mount_CRD-7R_battery_port": (0, BODY_L / 2 + 0.0008, -0.0065),  # centre of the port cut on the rear cap
    "mount_prongs": (0, front, 0),
}
for n, (x, y, z) in mounts.items():
    e = link(bpy.data.objects.new(n, None))
    e.empty_display_type = "ARROWS"
    e.empty_display_size = 0.006
    place(e, x, y, z)
    e.parent = root
allmesh = [o for o in coll.objects if o.type == "MESH"]
for o in allmesh:
    o.parent = root
# Printed text is preview geometry only; in the game it is a decal on the body texture.
decal = [o for o in allmesh if o.name.startswith("CRD-7_text")]
geo = [o for o in allmesh if o not in decal]

tris = sum(len(p.vertices) - 2 for o in geo for p in o.data.polygons)
print(f"STATS decal_preview_triangles={sum(len(p.vertices) - 2 for o in decal for p in o.data.polygons)}")
print(f"STATS parts={len(geo)} triangles={tris}")
for o in sorted(geo, key=lambda o: -len(o.data.polygons))[:6]:
    print("  ", o.name, sum(len(p.vertices) - 2 for p in o.data.polygons))

# ---- save and export --------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "compliance", "CRD-7", "CRD-7.blend"))
bpy.ops.object.select_all(action="DESELECT")
for o in [root] + geo + [o for o in coll.objects if o.name.startswith("mount_")]:
    o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(EXPORT_DIR, "CRD-7.fbx"), use_selection=True,
                         object_types={"MESH", "EMPTY"}, apply_scale_options="FBX_SCALE_ALL",
                         add_leaf_bones=False, mesh_smooth_type="FACE")

# ---- studio and previews ----------------------------------------------------
floor = link(bpy.data.objects.new("studio_floor", bpy.data.meshes.new("studio_floor")))
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.5)
bm.to_mesh(floor.data)
bm.free()
floor.location = (0, 0, -BODY_H / 2 - 0.0002)
floor.data.materials.append(mat("studio_floor", (0.45, 0.44, 0.42), 0.75))

world = bpy.data.worlds.new("studio")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.88, 0.88, 0.90, 1)
bg.inputs["Strength"].default_value = 0.30
scene.world = world


def sun(name, rot, energy, angle=12, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, "SUN")
    ld.energy = energy
    ld.angle = math.radians(angle)
    ld.color = color
    o = link(bpy.data.objects.new(name, ld))
    o.rotation_euler = [math.radians(a) for a in rot]


sun("key", (50, 0, 35), 1.15, 10, (1.0, 0.96, 0.9))
sun("fill", (60, 0, -120), 0.35, 25, (0.9, 0.93, 1.0))
sun("rim", (110, 0, 160), 0.55, 15)

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1500, 1000
scene.view_settings.view_transform = "Standard"

cam_data = bpy.data.cameras.new("cam")
cam = link(bpy.data.objects.new("cam", cam_data))
scene.camera = cam
target = link(bpy.data.objects.new("cam_target", None))
target.location = (0, -0.045, 0)
con = cam.constraints.new("TRACK_TO")
con.target = target
con.track_axis = "TRACK_NEGATIVE_Z"
con.up_axis = "UP_Y"


def shot(name, loc, lens=85, ortho=None):
    cam.location = loc
    cam_data.lens = lens
    if ortho:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho
    else:
        cam_data.type = "PERSP"
    scene.render.filepath = os.path.join(PREVIEW_DIR, f"CRD-7_{name}.png")
    bpy.ops.render.render(write_still=True)


shot("hero", (0.30, -0.36, 0.20), 95)
shot("side_emitter", (0.40, -0.02, 0.05), 100)
shot("rear_indicator", (-0.34, 0.30, 0.16), 95)
target.location = (0, -0.035, 0)
con.mute = True
cam.rotation_euler = (0, 0, math.pi)          # straight down, prongs at the top of the frame
shot("top", (0.0, -0.035, 0.6), ortho=0.22)
print("DONE")
