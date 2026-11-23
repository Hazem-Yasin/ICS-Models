"""
ICS-Mark: the canon ICS Earth Branch mark (Doc 2.32) as a parametric Geometry Nodes asset.  Writes Logo/ICS-Mark.blend.

  "/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --python Logo/ICS-Mark_build.py -- "$(wslpath -w <ICS-Models root>)"

What it is: ONE object, `ICS-Mark`, with a Geometry Nodes modifier `ICS-Mark`. Every number of the mark is a slider in the
modifier panel (Properties > Modifiers): arc angles, radii, widths, groove, thickness. Change one and the mark rebuilds live.
  * disc  : Deep Blue enamel, an UNBROKEN circle (nothing is cut through it)           [PROPOSAL: enamel + groove build]
  * arc   : Warm Gold, round ends, sits in a shallow groove cut round it                 [PROPOSAL: groove replaces the flat knock-out gap]
  * Unit  : the circle has radius 1. Scale the object to the real size (R = 9 mm -> scale 0.009).
The defaults are exactly Logo/src/ics_brand.py ARC. To bake changed sliders back into the code, run Logo/ICS-Mark_params.py
inside Blender (it prints the dict). The 2D SVG kit and the 3D models on the weapons still read ics_brand.py.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = sys.argv[sys.argv.index("--") + 1]
LOGO = os.path.join(ROOT, "Logo")
sys.path.insert(0, os.path.join(LOGO, "src"))
import ics_brand as b  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---- materials ------------------------------------------------------------------------------------------------------
def mat(name, rgb, metallic, rough, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (*rgb, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = rough
    if coat:
        bs.inputs["Coat Weight"].default_value = coat
        bs.inputs["Coat Roughness"].default_value = 0.05
    m.diffuse_color = (*rgb, 1)
    return m


M_BLUE = mat("ICS-Mark_blue_enamel", b.BLUE_LIN, 0.0, 0.35, coat=1.0)     # glossy clear-coated enamel
M_GOLD = mat("ICS-Mark_gold", b.GOLD_LIN, 0.9, 0.30)

# ---- node-group helpers ---------------------------------------------------------------------------------------------
tree = bpy.data.node_groups.new("ICS-Mark", "GeometryNodeTree")
N, L = tree.nodes, tree.links
tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")

PARAMS = {}     # name -> (identifier, default)


def param(name, default, lo, hi, kind="NodeSocketFloat", sub=None, tip=""):
    s = tree.interface.new_socket(name, in_out="INPUT", socket_type=kind)
    s.min_value, s.max_value = lo, hi          # range first: a default set before it can be clamped by the old range
    s.default_value = default
    s.description = tip
    if sub:
        s.subtype = sub
    PARAMS[name] = (s.identifier, default)
    return s


A = b.ARC
param("Arc Start Angle", A["th0"], -720.0, 720.0, tip="degrees; where the tail begins (216 = lower left)")
param("Arc End Angle", A["th1"], -720.0, 720.0, tip="degrees; where the arc comes to rest (-100 = base)")
param("Arc Radius Start", A["r0"], 0.1, 3.0, tip="distance of the tail from the centre, in circle radii (>1 = outside the circle)")
param("Arc Radius End", A["r1"], 0.1, 3.0, tip="distance at the rest point (<1 = inside the circle)")
param("Arc Angle Curve", A["a"], 0.2, 3.0, tip="1 = even sweep; <1 spends more angle early")
param("Arc Radius Curve", A["q"], 0.2, 3.0, tip="1 = straight spiral")
param("Width Tail", A["w0"], 0.005, 0.6, tip="arc width at the tail, in circle radii")
param("Width Crown", A["wm"], 0.005, 0.6, tip="widest point of the arc")
param("Width Rest", A["w1"], 0.005, 0.6, tip="arc width at the rest point")
param("Crown Position", A["tm"], 0.05, 0.95, tip="where along the arc the widest point sits (0 = tail, 1 = rest)")
param("Arc Resolution", 160, 16, 600, kind="NodeSocketInt", tip="points along the arc")
param("Arc Flatness", 0.45, 0.05, 1.5, tip="height of the arc's dome compared with its half-width")
param("Groove Gap", 0.032, 0.0, 0.2, tip="channel around the arc, in circle radii (0 = no groove)")
param("Groove Depth", 0.9, 0.05, 3.0, tip="depth of the channel relative to its width")
param("Disc Thickness", 0.14, 0.02, 1.0, tip="thickness of the blue enamel disc, in circle radii")
param("Disc Segments", 160, 24, 512, kind="NodeSocketInt", tip="facets round the circle")

GI = N.new("NodeGroupInput")
GO = N.new("NodeGroupOutput")
GI.location, GO.location = (-1800, 0), (2400, 0)


def P(name):
    return GI.outputs[name]


_loc = [-1500, 400]


def node(typ, **kw):
    n = N.new(typ)
    for k, v in kw.items():
        setattr(n, k, v)
    n.location = tuple(_loc)
    _loc[0] += 40
    _loc[1] -= 60
    if _loc[1] < -900:
        _loc[0] += 260
        _loc[1] = 400
    return n


def wire(src, n, idx_or_name):
    if isinstance(src, (int, float)):
        n.inputs[idx_or_name].default_value = src
    elif src is not None:
        L.new(src, n.inputs[idx_or_name])


def M(op, a, b_=None, c=None):
    """Float math node; a / b_ / c are numbers or output sockets. Returns the output socket."""
    n = node("ShaderNodeMath", operation=op)
    wire(a, n, 0)
    if b_ is not None:
        wire(b_, n, 1)
    if c is not None:
        wire(c, n, 2)
    return n.outputs[0]


def mul(a, b_):
    return M("MULTIPLY", a, b_)


def add(a, b_):
    return M("ADD", a, b_)


def sub(a, b_):
    return M("SUBTRACT", a, b_)


# ---- the arc curve --------------------------------------------------------------------------------------------------
line = node("GeometryNodeCurvePrimitiveLine")
line.inputs["End"].default_value = (1, 0, 0)
rs = node("GeometryNodeResampleCurve")
L.new(line.outputs["Curve"], rs.inputs["Curve"])
L.new(P("Arc Resolution"), rs.inputs["Count"])
t = node("GeometryNodeSplineParameter").outputs["Factor"]

ang = M("RADIANS", add(P("Arc Start Angle"), mul(sub(P("Arc End Angle"), P("Arc Start Angle")), M("POWER", t, P("Arc Angle Curve")))))
rad = add(P("Arc Radius End"), mul(sub(P("Arc Radius Start"), P("Arc Radius End")), M("POWER", sub(1.0, t), P("Arc Radius Curve"))))
pos = node("ShaderNodeCombineXYZ")
L.new(mul(rad, M("COSINE", ang)), pos.inputs["X"])
L.new(mul(rad, M("SINE", ang)), pos.inputs["Y"])
setp = node("GeometryNodeSetPosition")
L.new(rs.outputs["Curve"], setp.inputs["Geometry"])
L.new(pos.outputs["Vector"], setp.inputs["Position"])

# width: before the crown an ease-out sine, after it a cosine ease (same as ics_brand.width_at)
tm = P("Crown Position")
wa = add(P("Width Tail"), mul(sub(P("Width Crown"), P("Width Tail")), M("SINE", mul(M("DIVIDE", t, tm), math.pi / 2))))
u = M("DIVIDE", sub(t, tm), sub(1.0, tm))
sm = sub(0.5, mul(0.5, M("COSINE", mul(u, math.pi))))
wb = add(P("Width Crown"), mul(sub(P("Width Rest"), P("Width Crown")), sm))
mask = M("LESS_THAN", t, tm)
width = add(mul(mask, wa), mul(sub(1.0, mask), wb))
half = mul(width, 0.5)


def tube(extra, zscale_socket, material):
    """Round tube along the arc (radius = half-width + extra) with a sphere at each end, flattened in Z.
    The radius travels as a named point attribute "rr", read back for the profile scale and for the end spheres.
    Returns (tube_mesh_socket, caps_mesh_socket), both flattened in Z and carrying `material`."""
    st = node("GeometryNodeStoreNamedAttribute", data_type="FLOAT", domain="POINT")
    st.inputs["Name"].default_value = "rr"
    L.new(setp.outputs["Geometry"], st.inputs["Geometry"])
    L.new(add(half, extra) if extra is not None else half, st.inputs["Value"])

    def rr():
        n_ = node("GeometryNodeInputNamedAttribute", data_type="FLOAT")
        n_.inputs["Name"].default_value = "rr"
        return n_.outputs["Attribute"]

    prof = node("GeometryNodeCurvePrimitiveCircle")
    prof.inputs["Resolution"].default_value = 28
    ctm = node("GeometryNodeCurveToMesh")
    L.new(st.outputs["Geometry"], ctm.inputs["Curve"])
    L.new(prof.outputs["Curve"], ctm.inputs["Profile Curve"])
    L.new(rr(), ctm.inputs["Scale"])
    ctm.inputs["Fill Caps"].default_value = True
    # end caps: a sphere on each of the two end points (Count mode with 2 points = the start and the end)
    ctp = node("GeometryNodeCurveToPoints", mode="COUNT")
    L.new(st.outputs["Geometry"], ctp.inputs["Curve"])
    ctp.inputs["Count"].default_value = 2
    sph = node("GeometryNodeMeshUVSphere")
    sph.inputs["Segments"].default_value = 28
    sph.inputs["Rings"].default_value = 14
    sph.inputs["Radius"].default_value = 1.0
    sc = node("ShaderNodeCombineXYZ")
    r_ = rr()
    L.new(r_, sc.inputs["X"])
    L.new(r_, sc.inputs["Y"])
    L.new(r_, sc.inputs["Z"])
    iop = node("GeometryNodeInstanceOnPoints")
    L.new(ctp.outputs["Points"], iop.inputs["Points"])
    L.new(sph.outputs["Mesh"], iop.inputs["Instance"])
    L.new(sc.outputs["Vector"], iop.inputs["Scale"])
    real = node("GeometryNodeRealizeInstances")
    L.new(iop.outputs["Instances"], real.inputs["Geometry"])
    out = []
    for src in (ctm.outputs["Mesh"], real.outputs["Geometry"]):
        tr = node("GeometryNodeTransform")
        L.new(src, tr.inputs["Geometry"])
        zs = node("ShaderNodeCombineXYZ")
        zs.inputs["X"].default_value = 1.0
        zs.inputs["Y"].default_value = 1.0
        L.new(zscale_socket, zs.inputs["Z"])
        L.new(zs.outputs["Vector"], tr.inputs["Scale"])
        sm_ = node("GeometryNodeSetMaterial")
        sm_.inputs["Material"].default_value = material
        L.new(tr.outputs["Geometry"], sm_.inputs["Geometry"])
        out.append(sm_.outputs["Geometry"])
    return out


# ---- the disc: an unbroken enamel circle, with the arc's channel cut into its face -----------------------------------
cyl = node("GeometryNodeMeshCylinder")
L.new(P("Disc Segments"), cyl.inputs["Vertices"])
cyl.inputs["Radius"].default_value = 1.0
L.new(P("Disc Thickness"), cyl.inputs["Depth"])
cyl.inputs["Side Segments"].default_value = 1
dz = node("ShaderNodeCombineXYZ")
L.new(mul(P("Disc Thickness"), -0.5), dz.inputs["Z"])
dtr = node("GeometryNodeTransform")
L.new(cyl.outputs["Mesh"], dtr.inputs["Geometry"])
L.new(dz.outputs["Vector"], dtr.inputs["Translation"])
dmat = node("GeometryNodeSetMaterial")
dmat.inputs["Material"].default_value = M_BLUE
L.new(dtr.outputs["Geometry"], dmat.inputs["Geometry"])

cut_tube, cut_caps = tube(P("Groove Gap"), P("Groove Depth"), M_BLUE)
# a groove of zero gap must not create coplanar slivers: skip the cut by switching the cutter off
bool_ = node("GeometryNodeMeshBoolean", operation="DIFFERENCE", solver="EXACT")
L.new(dmat.outputs["Geometry"], bool_.inputs["Mesh 1"])
# Mesh 2 is a multi-input socket: the tube and its end spheres are separate cutters (the solver unions them).
# Do NOT join them first: the joined mesh self-intersects and the exact solver then returns no disc.
L.new(cut_tube, bool_.inputs["Mesh 2"])
L.new(cut_caps, bool_.inputs["Mesh 2"])
gap_on = node("FunctionNodeCompare", data_type="FLOAT", operation="GREATER_THAN")
L.new(P("Groove Gap"), gap_on.inputs[0])
gap_on.inputs[1].default_value = 0.0005
sw = node("GeometryNodeSwitch", input_type="GEOMETRY")
L.new(gap_on.outputs["Result"], sw.inputs["Switch"])
L.new(dmat.outputs["Geometry"], sw.inputs["False"])
L.new(bool_.outputs["Mesh"], sw.inputs["True"])

# ---- the gold arc ---------------------------------------------------------------------------------------------------
g_tube, g_caps = tube(None, P("Arc Flatness"), M_GOLD)

join = node("GeometryNodeJoinGeometry")
for s in (sw.outputs["Output"], g_tube, g_caps):
    L.new(s, join.inputs["Geometry"])
smooth = node("GeometryNodeSetShadeSmooth")
L.new(join.outputs["Geometry"], smooth.inputs["Geometry"])
L.new(smooth.outputs["Geometry"], GO.inputs["Geometry"])

# ---- object ---------------------------------------------------------------------------------------------------------
col = bpy.data.collections.new("ICS-Mark")
scene.collection.children.link(col)
me = bpy.data.meshes.new("ICS-Mark")
ob = bpy.data.objects.new("ICS-Mark", me)
col.objects.link(ob)
ob["note"] = ("Canon: ICS-Writing Doc 2.32 (one Deep Blue circle, one Warm Gold arc). Enamel/groove build is [PROPOSAL]. "
              "Radius 1 = the circle; scale the object for real sizes. Edit the sliders in the Geometry Nodes modifier.")
gm = ob.modifiers.new("ICS-Mark", "NODES")
gm.node_group = tree
# slider defaults come from the node-group interface (set in param()), so nothing to assign here
bv = ob.modifiers.new("Bevel", "BEVEL")
bv.width, bv.segments, bv.limit_method, bv.angle_limit = 0.012, 3, "ANGLE", math.radians(40)
wn = ob.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
wn.keep_sharp = False
wn.weight = 50
ob.data.materials.append(M_BLUE)
ob.data.materials.append(M_GOLD)

# ---- check against the 2D source ------------------------------------------------------------------------------------
dg = bpy.context.evaluated_depsgraph_get()
ev = ob.evaluated_get(dg)
m = ev.to_mesh()
gold = [v.co for p in m.polygons if m.materials[p.material_index] and m.materials[p.material_index].name == M_GOLD.name for v in (m.vertices[i] for i in p.vertices)]
assert gold, "no gold faces in the evaluated mark"
xs, ys = [v.x for v in gold], [v.y for v in gold]
ol = b.arc_outline(b.ARC, n=240)
print(f"CHECK arc bbox 3D  x[{min(xs):.3f},{max(xs):.3f}] y[{min(ys):.3f},{max(ys):.3f}]")
print(f"CHECK arc bbox 2D  x[{min(x for x, _ in ol):.3f},{max(x for x, _ in ol):.3f}] y[{min(y for _, y in ol):.3f},{max(y for _, y in ol):.3f}]")
tris = sum(len(p.vertices) - 2 for p in m.polygons)
print(f"STATS verts={len(m.vertices)} triangles={tris}")
ev.to_mesh_clear()

# ---- preview studio -------------------------------------------------------------------------------------------------
pv = bpy.data.collections.new("Preview")
scene.collection.children.link(pv)
world = bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
bgn = world.node_tree.nodes["Background"]
bgn.inputs["Color"].default_value = (0.22, 0.23, 0.26, 1)
bgn.inputs["Strength"].default_value = 0.6
for nm, loc, e, sz in (("key", (-1.6, -2.4, 2.2), 70, 2.0), ("fill", (2.4, -2.0, 0.6), 28, 2.5), ("rim", (0.6, -1.6, -2.0), 24, 2.0)):
    ld = bpy.data.lights.new(nm, "AREA")
    ld.energy, ld.size = e, sz
    lo = bpy.data.objects.new(nm, ld)
    pv.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = (Vector((0, 0, 0)) - lo.location).to_track_quat("-Z", "Y").to_euler()
cam_d = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("ICS-Mark_cam", cam_d)
pv.objects.link(cam)
scene.camera = cam
scene.render.engine = "CYCLES"
scene.view_settings.view_transform = "Standard"
scene.cycles.samples = 64
scene.cycles.use_denoising = False
scene.render.resolution_x = scene.render.resolution_y = 1200
os.makedirs(os.path.join(LOGO, "previews"), exist_ok=True)

# the mark faces +Z; for the previews stand it up so it faces -Y like the other models
ob.rotation_euler = (math.radians(90), 0, 0)


def shoot(fname, loc, target, ortho=None, lens=70):
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam_d.type, cam_d.ortho_scale = "ORTHO", ortho
    else:
        cam_d.type, cam_d.lens = "PERSP", lens
    scene.render.filepath = os.path.join(LOGO, "previews", fname)
    bpy.ops.render.render(write_still=True)


shoot("ICS-Mark_front.png", (0, -6, -0.08), (0, 0, -0.08), ortho=3.1)
shoot("ICS-Mark_angle.png", (2.6, -5.2, 2.2), (-0.15, 0, 0.05), lens=60)
shoot("ICS-Mark_detail.png", (0.55, -1.7, -0.95), (0.25, 0, -0.55), lens=90)     # the rest point: groove, dome, round end

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(LOGO, "ICS-Mark.blend"))
print("saved ICS-Mark.blend")
print("exit 0")
