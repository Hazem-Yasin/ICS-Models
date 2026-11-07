"""Preview studio shared by the attachment build scripts (Blender 5.x).

Same look as the CRD-7 base build: warm key, cool fill, rim, grey floor, Cycles CPU.
Usage:  import studio; cam = studio.setup(scene, floor_z); cam.shot(...)
"""
import math
import os

import bmesh
import bpy


def _link(scene, ob):
    scene.collection.objects.link(ob)
    return ob


def _mat(name, color, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    return m


def _sun(scene, name, rot, energy, angle, color):
    ld = bpy.data.lights.new(name, "SUN")
    ld.energy = energy
    ld.angle = math.radians(angle)
    ld.color = color
    o = _link(scene, bpy.data.objects.new(name, ld))
    o.rotation_euler = [math.radians(a) for a in rot]


class Cam:
    def __init__(self, scene):
        self.scene = scene
        self.data = bpy.data.cameras.new("cam")
        self.ob = _link(scene, bpy.data.objects.new("cam", self.data))
        self.target = _link(scene, bpy.data.objects.new("cam_target", None))
        con = self.ob.constraints.new("TRACK_TO")
        con.target = self.target
        con.track_axis = "TRACK_NEGATIVE_Z"
        con.up_axis = "UP_Y"
        scene.camera = self.ob

    def shot(self, path, loc, target, lens=85, clip_start=0.002):
        self.ob.location = loc
        self.target.location = target
        self.data.lens = lens
        self.data.clip_start = clip_start
        self.data.type = "PERSP"
        self.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)


def setup(scene, floor_z, res=(1500, 1000), samples=48):
    floor = _link(scene, bpy.data.objects.new("studio_floor", bpy.data.meshes.new("studio_floor")))
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.5)
    bm.to_mesh(floor.data)
    bm.free()
    floor.location = (0, 0, floor_z)
    floor.data.materials.append(_mat("studio_floor", (0.45, 0.44, 0.42), 0.75))

    world = bpy.data.worlds.new("studio")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.88, 0.88, 0.90, 1)
    bg.inputs["Strength"].default_value = 0.30
    scene.world = world

    _sun(scene, "key", (50, 0, 35), 1.15, 10, (1.0, 0.96, 0.9))
    _sun(scene, "fill", (60, 0, -120), 0.35, 25, (0.9, 0.93, 1.0))
    _sun(scene, "rim", (110, 0, 160), 0.55, 15, (1, 1, 1))

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.view_settings.view_transform = "Standard"
    return Cam(scene)


def append_base(scene, blend_path):
    """Append every object of the CRD-7 base into the scene (copies, not links)."""
    with bpy.data.libraries.load(blend_path, link=False) as (src, dst):
        # parts and mount empties only; the base file also holds its own studio, lights and camera
        dst.objects = [n for n in src.objects if n.startswith(("CRD-7", "mount_"))]
    for ob in dst.objects:
        if ob is not None:
            scene.collection.objects.link(ob)
    return {ob.name: ob for ob in dst.objects if ob is not None}
