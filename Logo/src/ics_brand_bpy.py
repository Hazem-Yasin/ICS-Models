"""
Blender side of the ICS mark: real geometry built from the same outline as the SVG kit (Logo/src/ics_brand.py), so the
3D mark on a model matches the artwork. Needs bpy; import it from a build script after putting Logo/src on sys.path.

build_mark(prefix, R, blue_mat, gold_mat, ...) makes, in the XY plane facing +Z with the mark centred on its bounding box:
  <prefix>_disc  deep-blue disc with the knock-out gap cut around the arc   (thickness t_blue)
  <prefix>_arc   gold arc, round ends                                       (thickness t_gold, sitting on top)
Both are returned as a list. The caller rotates / parents them. All shapes are [PROPOSAL] geometry, see BRAND_MARK.md.
"""
import math

import bmesh
import bpy

import ics_brand as b


def _poly_obj(name, poly, thick, z0=0.0):
    bm = bmesh.new()
    face = bm.faces.new([bm.verts.new((x, y, z0)) for x, y in poly])
    bmesh.ops.triangulate(bm, faces=[face], quad_method="BEAUTY", ngon_method="EAR_CLIP")
    geom = list(bm.faces)
    res = bmesh.ops.extrude_face_region(bm, geom=geom)
    bmesh.ops.translate(bm, vec=(0, 0, thick), verts=[v for v in res["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def build_mark(prefix, R, blue_mat, gold_mat, small=False, t_blue=0.0004, t_gold=0.0005, circle_segs=72, arc_steps=90):
    p = b.ARC_SMALL if small else b.ARC
    gap = b.GAP_SMALL if small else b.GAP
    x0, x1, y0, y1 = b.mark_bbox(small)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

    def sh(poly):
        return [((x - cx) * R, (y - cy) * R) for x, y in poly]

    arc_poly = sh(b.arc_outline(p, n=arc_steps, cap_steps=10))
    cut_poly = sh(b.arc_outline(p, n=arc_steps, cap_steps=10, grow=gap))
    circ = sh([(math.cos(2 * math.pi * i / circle_segs), math.sin(2 * math.pi * i / circle_segs)) for i in range(circle_segs)])

    disc = _poly_obj(f"{prefix}_disc", circ, t_blue)
    cutter = _poly_obj("tmp_ko", cut_poly, t_blue * 6, -t_blue * 2)
    mod = disc.modifiers.new("ko", "BOOLEAN")
    mod.operation, mod.solver, mod.object = "DIFFERENCE", "EXACT", cutter
    with bpy.context.temp_override(object=disc, active_object=disc, selected_objects=[disc]):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

    arc = _poly_obj(f"{prefix}_arc", arc_poly, t_gold, t_blue * 0.25)
    for ob, m in ((disc, blue_mat), (arc, gold_mat)):
        ob.data.materials.append(m)
        for pl in ob.data.polygons:
            pl.use_smooth = False
    return [disc, arc]
