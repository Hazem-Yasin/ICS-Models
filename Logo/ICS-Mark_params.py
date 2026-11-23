"""
Print the current ICS-Mark slider values as an ics_brand.py ARC dict.  Run inside Blender with ICS-Mark.blend open:

  Text Editor > Open this file > Run Script      (or, headless:)
  "/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background Logo/ICS-Mark.blend --python Logo/ICS-Mark_params.py

Copy the printed ARC line into Logo/src/ics_brand.py, then rerun Logo/build_brand.py and the model builds.
Only the arc shape is baked back (angles, radii, widths, crown). Resolution, groove and disc sliders exist only in 3D.
Blender 5.2: modifier inputs are read by socket identifier, as inputs[identifier]["value"].
"""
import bpy

ob = bpy.data.objects["ICS-Mark"]
gm = ob.modifiers["ICS-Mark"]
ident = {i.name: i.identifier for i in gm.node_group.interface.items_tree if getattr(i, "in_out", "") == "INPUT"}
inp = gm.properties.inputs


def val(name):
    return float(inp[ident[name]]["value"])


arc = dict(
    th0=val("Arc Start Angle"), th1=val("Arc End Angle"),
    r0=val("Arc Radius Start"), r1=val("Arc Radius End"),
    q=val("Arc Radius Curve"), a=val("Arc Angle Curve"),
    w0=val("Width Tail"), wm=val("Width Crown"), w1=val("Width Rest"), tm=val("Crown Position"),
)
print("ARC = dict(" + ", ".join(f"{k}={v:.4g}" for k, v in arc.items()) + ")")
print("(3D only: groove gap %.4g, depth %.4g, thickness %.4g)" % (val("Groove Gap"), val("Groove Depth"), val("Disc Thickness")))
