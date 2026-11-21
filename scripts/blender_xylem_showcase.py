"""
AI Story Studio — single-shot cinematic xylem showcase.

Run:
  blender -b -P scripts/blender_xylem_showcase.py -- out/xylem-showcase.mp4

Creates one 12-second vertical educational 3D shot. No external assets required.
"""
import bpy
import math
import os
import sys
from mathutils import Vector

FPS = 30
DURATION = 12
END = FPS * DURATION

def output_arg():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return os.path.abspath(args[0] if args else "out/xylem-showcase.mp4")

def material(name, color, roughness=0.65, metallic=0.0, subsurface=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface
    return m

def emissive(name, color, strength=1.5):
    m = material(name, color, 0.25)
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Emission Color"].default_value = (*color, 1)
    bsdf.inputs["Emission Strength"].default_value = strength
    return m

def apply_mat(obj, mat):
    obj.data.materials.append(mat)
    return obj

def add_surface_texture(mat, scale=5.0, detail=3.0, bump_strength=0.16, distance=0.08):
    """Subtle procedural grain; keeps the stylized look while avoiding flat surfaces."""
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    noise.inputs["Roughness"].default_value = 0.72
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = distance
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat

def smooth(obj):
    if obj.type == "MESH":
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj

def uv(name, loc, scale, mat, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    smooth(o)
    return apply_mat(o, mat)

def cylinder(name, loc, radius, depth, mat, vertices=64, rotation=(0,0,0), bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    apply_mat(o, mat)
    if bevel:
        mod = o.modifiers.new("Soft_Edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new("Weighted_Normals", "WEIGHTED_NORMAL")
    return o

def curve_tube(name, points, radius, mat, resolution=16):
    c = bpy.data.curves.new(name, "CURVE")
    c.dimensions = "3D"
    c.resolution_u = 16
    c.bevel_depth = radius
    c.bevel_resolution = 4
    s = c.splines.new("BEZIER")
    s.bezier_points.add(len(points)-1)
    for bp, co in zip(s.bezier_points, points):
        bp.co = co
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

def add_text(body, loc, size, mat, name):
    c = bpy.data.curves.new(name, "FONT")
    c.body = body
    c.size = size
    c.align_x = "CENTER"
    c.extrude = 0.001
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(mat)
    return o

def key_location(obj, frame, loc):
    obj.location = loc
    obj.keyframe_insert(data_path="location", frame=frame)

def animate_scale(obj, frame, scale):
    obj.scale = scale
    obj.keyframe_insert(data_path="scale", frame=frame)

def main():
    output = output_arg()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene

    engines = {e.identifier for e in scene.render.bl_rna.properties["engine"].enum_items}
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
    scene.render.resolution_x = 720
    scene.render.resolution_y = 1280
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = END
    scene.render.image_settings.media_type = "VIDEO"
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = output
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"

    # Palette: warm earth, honey wood, deep botanical greens, luminous water.
    soil = material("Rich_Soil", (0.105, 0.052, 0.026), 0.96)
    soil_edge = material("Soil_Cutaway", (0.19, 0.095, 0.047), 0.92)
    bark = material("Warm_Bark", (0.20, 0.085, 0.038), 0.78)
    wood = material("Fresh_Wood", (0.76, 0.53, 0.29), 0.58)
    ring_dark = material("Growth_Rings", (0.43, 0.26, 0.12), 0.72)
    root_mat = material("Root_Fibres", (0.49, 0.28, 0.13), 0.72)
    green = material("Leaf_Green", (0.055, 0.26, 0.105), 0.48, subsurface=0.04)
    green_light = material("Leaf_Highlight", (0.16, 0.42, 0.17), 0.42, subsurface=0.05)
    xylem_mat = material("Xylem_Teal", (0.035, 0.32, 0.39), 0.34, metallic=0.08)
    water = emissive("Glowing_Water", (0.08, 0.68, 1.0), 2.2)
    gold = emissive("Warm_Label", (1.0, 0.68, 0.28), 0.8)
    white = material("Soft_White", (0.88, 0.94, 0.96), 0.45)

    # Fine procedural surface detail for bark, wood and soil.
    add_surface_texture(soil, scale=7.5, detail=4.0, bump_strength=0.22, distance=0.12)
    add_surface_texture(bark, scale=8.0, detail=5.0, bump_strength=0.24, distance=0.10)
    add_surface_texture(wood, scale=12.0, detail=3.0, bump_strength=0.12, distance=0.045)
    add_surface_texture(root_mat, scale=10.0, detail=3.0, bump_strength=0.14, distance=0.045)

    # Dark teal studio world and a broad soil cross-section platform.
    world = bpy.data.worlds.new("Deep_Teal_Studio") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.035, 0.052, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.32

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.85, -0.05))
    soil_block = bpy.context.object
    soil_block.name = "Cutaway_Soil_Block"
    soil_block.dimensions = (8.0, 2.2, 1.55)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_mat(soil_block, soil)
    bevel = soil_block.modifiers.new("Rounded_Soil_Edge", "BEVEL")
    bevel.width = 0.16
    bevel.segments = 5
    soil_block.modifiers.new("Soil_Normals", "WEIGHTED_NORMAL")

    # Subtle soil pebbles and fine root hairs on the front-facing cutaway.
    pebble_mat = material("Soil_Pebbles", (0.28, 0.16, 0.09), 0.9)
    for i in range(34):
        x = -3.6 + (i * 0.43) % 7.2
        z = -0.55 + ((i * 17) % 100) / 100 * 1.0
        y = -0.29
        peb = uv("Soil_Pebble", (x, y, z), (0.035+(i%3)*0.012, 0.025, 0.025+(i%2)*0.012), pebble_mat, 16, 10)

    # Main trunk rises from the soil, with taper and soft bark ridges.
    trunk = cylinder("Tree_Trunk", (0, 0.0, 2.55), 0.53, 5.6, bark, 64, bevel=0.12)
    trunk.scale.x = 0.88
    trunk.scale.y = 0.88
    for i in range(9):
        x = -0.38 + i * 0.095
        curve_tube("Bark_Ridge", [(x, -0.47, 0.0), (x*0.9, -0.49, 1.4), (x*0.75, -0.45, 3.1), (x*0.7, -0.36, 5.0)], 0.018, root_mat)

    # Root network fans out across the visible front of the soil.
    root_paths = [
        [(0,-0.34,0.30),(-0.45,-0.40,0.12),(-1.25,-0.40,0.02),(-2.5,-0.35,-0.22),(-3.45,-0.3,-0.35)],
        [(0,-0.36,0.26),(0.55,-0.42,0.12),(1.35,-0.40,-0.04),(2.45,-0.35,-0.22),(3.45,-0.3,-0.32)],
        [(-0.12,-0.39,0.28),(-0.62,-0.43,-0.18),(-1.05,-0.4,-0.55),(-1.8,-0.35,-0.65)],
        [(0.12,-0.39,0.28),(0.62,-0.43,-0.18),(1.08,-0.4,-0.55),(1.85,-0.35,-0.67)],
        [(-0.06,-0.40,0.25),(-0.18,-0.45,-0.22),(-0.35,-0.4,-0.58),(-0.5,-0.34,-0.72)],
        [(0.05,-0.40,0.25),(0.20,-0.45,-0.24),(0.42,-0.4,-0.58),(0.62,-0.34,-0.72)]
    ]
    for i, pts in enumerate(root_paths):
        curve_tube("Primary_Root", pts, 0.10 if i < 2 else 0.065, root_mat)
        # Thin branching rootlets.
        for j in range(2):
            p = pts[1]
            side = -1 if (i+j)%2 else 1
            curve_tube("Fine_Rootlet", [p, (p[0]+side*0.25, p[1]-0.025, p[2]-0.22), (p[0]+side*0.52, p[1], p[2]-0.32)], 0.018, root_mat)

    # A compact canopy anchors the tree visually without distracting from the reveal.
    for i, (x,z,s) in enumerate([(-1.0,5.3,0.85),(0,5.8,1.05),(1.0,5.25,0.82),(-.45,6.25,.72),(.55,6.35,.70)]):
        uv("Canopy_Cluster", (x,0.15,z), (s,0.48,s*0.82), green if i%2 else green_light)

    # Cross-section plate is a clean educational cutaway, facing the camera.
    disc = cylinder("Tree_Cross_Section", (0,-0.72,3.15), 1.12, 0.16, wood, 96, (math.radians(90),0,0), 0.035)
    # Growth rings on the front plane.
    for radius in [0.35,0.57,0.78,0.96]:
        bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=0.018, major_segments=96, minor_segments=10, location=(0,-0.82,3.15), rotation=(math.radians(90),0,0))
        apply_mat(bpy.context.object, ring_dark)
    # Central pith.
    uv("Tree_Pith", (0,-0.835,3.15), (0.13,0.035,0.13), ring_dark, 24, 16)

    # Clearly visible xylem vessel openings distributed within the wood section.
    vessel_positions = [(-.50,3.36),(-.22,3.58),(.12,3.54),(.48,3.34),(-.48,2.98),(-.14,2.82),(.22,2.91),(.52,3.02),(0,3.18)]
    for i,(x,z) in enumerate(vessel_positions):
        # dark rim and teal inner lumen
        uv("Vessel_Rim", (x,-0.855,z), (0.105,0.028,0.105), ring_dark, 24, 16)
        uv("Xylem_Vessel", (x,-0.89,z), (0.073,0.025,0.073), xylem_mat, 24, 16)
        # tiny luminous water bead inside each visible vessel
        bead = uv("Water_Bead", (x,-0.925,z), (0.035,0.018,0.035), water, 20, 12)
        bead.location.z = z - 0.20
        bead.keyframe_insert(data_path="location", frame=70 + (i % 3) * 12)
        bead.location.z = z + 0.20
        bead.keyframe_insert(data_path="location", frame=190 + (i % 3) * 12)
        bead.location.z = z - 0.20
        bead.keyframe_insert(data_path="location", frame=310 + (i % 3) * 12)

    # A few visible vertical water channels beside the cross-section connect the idea.
    for i,x in enumerate([-0.34,0.0,0.34]):
        channel = curve_tube("Water_Transport_Channel", [(x,-0.56,0.55),(x*0.96,-0.56,1.45),(x*0.92,-0.56,2.35),(x*0.88,-0.56,3.0)], 0.035, xylem_mat)
        for j in range(4):
            z0 = 0.7 + j*0.56
            drop = uv("Ascending_Water_Drop", (x,-0.64,z0), (0.055,0.045,0.075), water, 20, 12)
            drop.location.z = z0 - 0.25
            drop.keyframe_insert(data_path="location", frame=1 + j*18)
            drop.location.z = z0 + 0.65
            drop.keyframe_insert(data_path="location", frame=105 + j*18)
            drop.location.z = z0 + 1.55
            drop.keyframe_insert(data_path="location", frame=210 + j*18)
            drop.location.z = z0 + 2.35
            drop.keyframe_insert(data_path="location", frame=END)

    # No floating 3D labels: clean, synchronized captions will be composited later.

    # Camera: establish the root system, then travel into the trunk cross-section.
    bpy.ops.object.camera_add(location=(0,-15.8,4.15))
    camera = bpy.context.object
    camera.name = "Showcase_Camera"
    camera.data.lens = 48
    camera.data.clip_start = 0.01
    target = bpy.data.objects.new("Camera_Target", None)
    bpy.context.collection.objects.link(target)
    target.location = (0,0.0,2.45)
    track = camera.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    scene.camera = camera

    key_location(camera, 1, (0,-16.8,4.35))
    key_location(camera, 125, (0,-14.0,3.75))
    key_location(camera, 245, (0,-10.8,3.45))
    key_location(camera, END, (0,-9.7,3.35))
    for frame, loc in [(1,(0,0,2.45)),(125,(0,0,2.75)),(245,(0,-0.35,3.05)),(END,(0,-0.45,3.12))]:
        target.location = loc
        target.keyframe_insert(data_path="location", frame=frame)
    for frame,lens in [(1,40),(125,44),(245,52),(END,56)]:
        camera.data.lens = lens
        camera.data.keyframe_insert(data_path="lens", frame=frame)

    # Three-point studio lighting with soft highlights and a cool rim.
    bpy.ops.object.light_add(type="AREA", location=(-5,-7,9))
    key_light = bpy.context.object
    key_light.data.energy = 1500
    key_light.data.shape = "DISK"
    key_light.data.size = 7
    key_light.rotation_euler = (math.radians(25),0,math.radians(-25))
    bpy.ops.object.light_add(type="AREA", location=(5,-1,6))
    fill = bpy.context.object
    fill.data.energy = 850
    fill.data.color = (0.45,0.72,1.0)
    fill.data.size = 6
    fill.rotation_euler = (math.radians(35),0,math.radians(125))
    bpy.ops.object.light_add(type="AREA", location=(0,4,8))
    rim = bpy.context.object
    rim.data.energy = 1800
    rim.data.color = (0.35,0.75,1.0)
    rim.data.size = 5
    rim.rotation_euler = (math.radians(20),0,math.radians(180))

    # Blender's default keyframe interpolation is Bezier; avoid legacy
    # Action.fcurves access because Blender 5.x uses layered actions.

    scene.camera.data.dof.use_dof = True
    scene.camera.data.dof.focus_object = target
    scene.camera.data.dof.aperture_fstop = 7.1
    scene.render.filepath = output
    os.makedirs(os.path.dirname(output), exist_ok=True)
    bpy.ops.render.render(animation=True)
    print("Xylem showcase rendered:", output)

if __name__ == "__main__":
    main()
