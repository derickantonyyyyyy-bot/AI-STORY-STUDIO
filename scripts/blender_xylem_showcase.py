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
    green = material("Leaf_Green", (0.045, 0.22, 0.075), 0.38, subsurface=0.08)
    green_light = material("Leaf_Highlight", (0.12, 0.34, 0.12), 0.34, subsurface=0.09)
    xylem_mat = material("Xylem_Teal", (0.035, 0.32, 0.39), 0.34, metallic=0.08)
    water = emissive("Glowing_Water", (0.08, 0.68, 1.0), 2.2)
    gold = emissive("Warm_Label", (1.0, 0.68, 0.28), 0.8)
    white = material("Soft_White", (0.88, 0.94, 0.96), 0.45)

    # Fine procedural surface detail for bark, wood and soil.
    add_surface_texture(soil, scale=7.5, detail=4.0, bump_strength=0.22, distance=0.12)
    add_surface_texture(bark, scale=8.0, detail=5.0, bump_strength=0.24, distance=0.10)
    add_surface_texture(wood, scale=12.0, detail=3.0, bump_strength=0.12, distance=0.045)
    add_surface_texture(root_mat, scale=10.0, detail=3.0, bump_strength=0.14, distance=0.045)
    add_surface_texture(green, scale=5.5, detail=2.5, bump_strength=0.08, distance=0.025)
    add_surface_texture(green_light, scale=6.5, detail=2.0, bump_strength=0.06, distance=0.02)
    add_surface_texture(xylem_mat, scale=9.0, detail=3.0, bump_strength=0.10, distance=0.025)

    # Dark teal studio world and a broad soil cross-section platform.
    world = bpy.data.worlds.new("Deep_Teal_Studio") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world = world
    world.use_nodes = True
    # Soft cinematic blue studio environment: brighter than the earlier dark teal,
    # while keeping enough contrast for the bark, roots and glowing xylem.
    # V19: a lighter, softer blue studio world lifts the whole scene without washing out the wood.
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.12, 0.23, 0.34, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.62

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
    # V25: carve a real short passage through the trunk so the vessel mouth
    # is not merely drawn over the solid bark surface.
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=0.305, depth=1.42,
        location=(0,-0.02,3.28), rotation=(math.radians(90),0,0)
    )
    trunk_cutter = bpy.context.object
    trunk_cutter.name = "Temporary_Xylem_Boolean_Cutter"
    boolean = trunk.modifiers.new("True_Xylem_Entrance", "BOOLEAN")
    boolean.operation = "DIFFERENCE"
    boolean.solver = "EXACT"
    boolean.object = trunk_cutter
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.modifier_apply(modifier=boolean.name)
    bpy.data.objects.remove(trunk_cutter, do_unlink=True)
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

    # V12: branch structure connects the canopy clusters back to the trunk.
    canopy_centres = [(-1.0,5.3,0.85),(0,5.8,1.05),(1.0,5.25,0.82),(-.45,6.25,.72),(.55,6.35,.70)]
    for i, (x,z,s) in enumerate(canopy_centres):
        # Smaller foliage masses let the individual leaves and branch network define the silhouette.
        # Keep the old foliage mass only as a subtle depth layer; the leaf
        # silhouettes and branching structure should define the crown.
        uv("Canopy_Cluster", (x,0.15,z), (s*0.09,0.075,s*0.085), green if i%2 else green_light)
    branch_mat = material("Canopy_Branches", (0.19,0.075,0.032), 0.82)
    for i, (x,z,s) in enumerate(canopy_centres):
        start_x = -0.08 if x < 0 else 0.08
        curve_tube("Canopy_Main_Branch",
                   [(start_x,0.02,4.55),(start_x*1.5,-0.01,4.95),
                    (x*0.52,-0.02,5.20),(x,-0.02,z-0.08)],
                   0.055 if i < 3 else 0.038, branch_mat)
        for side in (-1,1):
            curve_tube("Canopy_Side_Twig",
                       [(x*0.58,-0.04,5.12),(x*0.78+side*0.12,-0.06,5.32),
                        (x+side*0.20,-0.08,z+0.06)],
                       0.018, branch_mat)
        # A small hierarchy of secondary twigs fans outward from each main branch.
        # These stay visible between the smaller foliage masses.
        for side in (-1,1):
            for level in (0,1):
                root_x = x * (0.72 + level * 0.12)
                root_z = 5.18 + level * 0.20
                tip_x = x + side * (0.34 + level * 0.12)
                tip_z = z + (0.18 if level == 0 else -0.10)
                curve_tube("Fine_Canopy_Twig",
                           [(root_x,-0.10,root_z),
                            (root_x + side*0.12,-0.12,root_z+0.12),
                            (tip_x,-0.12,tip_z)],
                           0.010 if level == 0 else 0.008, branch_mat)

    # V12: fuller oval leaves, arranged around visible branching twigs.
    leaf_vein = material("Leaf_Veins", (0.24, 0.48, 0.19), 0.58)
    def make_leaf(name, center, length, width, direction, mat):
        direction = Vector(direction).normalized()
        side = direction.cross(Vector((0, 1, 0)))
        if side.length < 0.001:
            side = direction.cross(Vector((1, 0, 0)))
        side.normalize()
        normal = direction.cross(side).normalized()
        verts = []
        # Seven stations create a fuller oval blade with a softly rounded tip.
        profile = [(0.0,0.10),(0.16,0.52),(0.34,0.86),(0.52,1.0),
                   (0.70,0.88),(0.86,0.55),(1.0,0.10)]
        for t, w in profile:
            p = Vector(center) + direction * (length * (t - 0.5))
            camber = math.sin(t * math.pi) * length * 0.035
            verts.extend([
                tuple(p - side * (width * w) + normal * camber),
                tuple(p + normal * (camber + length * 0.012)),
                tuple(p + side * (width * w) + normal * camber)
            ])
        faces = []
        for k in range(len(profile)-1):
            a = k * 3
            faces.extend([(a,a+1,a+4,a+3),(a+1,a+2,a+5,a+4)])
        mesh = bpy.data.meshes.new(name + "_Mesh")
        mesh.from_pydata(verts, [], faces)
        mesh.materials.append(mat)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        solid = obj.modifiers.new("Leaf_Thickness", "SOLIDIFY")
        solid.thickness = 0.009
        smooth(obj)
        vein_points = [
            tuple(Vector(center) + direction * (length * (t-0.5))
                  + normal * (length * 0.035 * math.sin(t*math.pi)))
            for t in (0.04,0.24,0.48,0.72,0.94)
        ]
        curve_tube(name + "_Centre_Vein", vein_points, 0.0035, leaf_vein, 8)
        return obj

    for ci, (cx, cz, spread) in enumerate(canopy_centres):
        # Leaves sit along the outer twig network, with varied depth and angle
        # so the canopy reads as one branching crown instead of five round blobs.
        for li in range(26):
            # Golden-angle spacing plus gentle deterministic variation avoids a radial rosette.
            angle = li * 2.399963 + ci * 0.83 + 0.20 * math.sin(li * 1.73 + ci)
            angle += 0.10 * math.sin(li * 0.47 + ci * 1.9)
            # Uneven radial and angular spacing breaks the radial rosette pattern;
            # neighboring branches overlap into a more continuous crown silhouette.
            radial = 0.22 + 0.78 * ((li * 13 + ci * 7) % 17) / 16.0
            center = (cx + math.cos(angle) * spread * radial,
                      -0.34 + 0.16 * math.sin(li * 1.7 + ci),
                      cz + math.sin(angle) * spread * radial * 0.72)
            direction = (math.cos(angle + 0.45),
                         0.18 * math.sin(li * 1.1 + ci),
                         0.34 + 0.42 * math.sin(angle))
            leaf_length = 0.38 + (li % 7) * 0.047
            leaf_direction = Vector(direction).normalized()
            leaf_base = Vector(center) - leaf_direction * (leaf_length * 0.43)
            # A fine, curved twig reaches each leaf base so blades visibly grow
            # from the branch network instead of appearing as detached shapes.
            anchor_angle = angle - 0.22 * math.sin(li * 1.4 + ci)
            twig_anchor = Vector((cx + math.cos(anchor_angle) * spread * 0.34,
                                  -0.18 + 0.035 * math.sin(li + ci),
                                  cz + math.sin(anchor_angle) * spread * 0.27))
            twig_mid = twig_anchor.lerp(leaf_base, 0.58)
            twig_mid.z += 0.035 * math.sin(angle * 2.0 + ci)
            curve_tube("Leaf_Attachment_Twig",
                       [tuple(twig_anchor), tuple(twig_mid), tuple(leaf_base)],
                       0.010, branch_mat, 8)
            make_leaf("Canopy_Leaf", center, leaf_length,
                      0.118 + (li % 4) * 0.017, direction,
                      green_light if (li + ci) % 5 == 0 else green)

    # V22: organic vertical bark opening with one clear xylem lumen.
    # Remove the decorative nested circles and let the exposed wood grain,
    # vertical channels and single vessel entrance explain the structure.
    cutaway_frame = uv("Organic_Bark_Cutaway_Edge", (0,-0.485,3.05),
                        (0.39,0.060,1.02), bark, 48, 32)
    cutaway_wood = uv("Exposed_Vertical_Trunk_Wood", (0,-0.548,3.05),
                      (0.315,0.040,0.94), wood, 48, 32)
    for i in range(9):
        x = -0.24 + i * 0.060
        curve_tube("Vertical_Wood_Grain",
                   [(x,-0.595,2.35),(x*0.98,-0.598,2.78),
                    (x*0.94,-0.598,3.32),(x*0.90,-0.59,3.76)],
                   0.007, ring_dark)

    # V23: leave the vessel mouth genuinely open. A thin annular bark/wood
    # lip frames the entrance, but no disc or filled oval sits across the lumen.
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.292, minor_radius=0.018,
        major_segments=96, minor_segments=12,
        location=(0,-0.705,3.28), rotation=(math.radians(90),0,0)
    )
    apply_mat(bpy.context.object, wood)
    bpy.context.object.name = "Open_Xylem_Entrance_Lip"

    # Five slim xylem channels converge toward the open vessel mouth.
    for i,x in enumerate([-0.21,-0.105,0.0,0.105,0.21]):
        curve_tube("Embedded_Xylem_Channel",
                   [(x,-0.606,2.18),(x*0.98,-0.610,2.62),
                    (x*0.94,-0.610,3.10),(x*0.90,-0.605,3.88)],
                   0.018, xylem_mat)
        if i in (1,2,3):
            flow_drop = uv("Ascending_Water_Streak",
                           (x,-0.635,2.45), (0.012,0.014,0.075),
                           water, 20, 12)
            for frame,z in [(1,2.20),(90,2.85),(180,3.42),(270,3.80),(END,4.05)]:
                flow_drop.location.z = z + (i-2)*0.06
                flow_drop.keyframe_insert(data_path="location", frame=frame)
    # The central channel continues directly through the entrance and into
    # the lumen, making the transition visually continuous.
    curve_tube("Xylem_To_Vessel_Connector",
               [(0,-0.61,3.28),(0,-0.74,3.28),(0,-0.92,3.28),
                (0,-1.10,3.28)], 0.032, xylem_mat, 10)

    # V5 internal-vessel macro tunnel. This is a clean educational cutaway:
    # an open ring-and-fibre structure aligned with the camera's forward path.
    # It visually continues the xylem from the trunk window into a vessel lumen.
    tunnel_y_start = -0.72
    tunnel_y_end = 8.0
    tunnel_radius = 0.31
    tunnel_ring_mat = material("Vessel_Wall_Rings", (0.025, 0.19, 0.24), 0.38, metallic=0.12)
    tunnel_fibre_mat = material("Vessel_Inner_Fibres", (0.07, 0.39, 0.43), 0.42)
    # Continuous inner vessel wall: an open-ended cylindrical surface keeps
    # the macro view enclosed instead of exposing the dark studio through gaps.
    wall_verts = []
    wall_faces = []
    wall_segments = 96
    for yy in (tunnel_y_start, tunnel_y_end):
        for j in range(wall_segments):
            a = 2.0 * math.pi * j / wall_segments
            wall_verts.append((math.cos(a) * (tunnel_radius - 0.018), yy,
                               3.28 + math.sin(a) * (tunnel_radius - 0.018)))
    for j in range(wall_segments):
        jn = (j + 1) % wall_segments
        wall_faces.append((j, jn, wall_segments + jn, wall_segments + j))
    wall_mesh = bpy.data.meshes.new("Vessel_Inner_Wall_Mesh")
    wall_mesh.from_pydata(wall_verts, [], wall_faces)
    wall_mesh.materials.append(tunnel_ring_mat)
    add_surface_texture(tunnel_ring_mat, scale=12.0, detail=3.0, bump_strength=0.08, distance=0.02)
    add_surface_texture(tunnel_fibre_mat, scale=8.0, detail=2.0, bump_strength=0.06, distance=0.018)
    wall_obj = bpy.data.objects.new("Continuous_Vessel_Inner_Wall", wall_mesh)
    bpy.context.collection.objects.link(wall_obj)
    for poly in wall_mesh.polygons:
        poly.use_smooth = True

    # Sparse, shallow wall ridges give depth without creating a tunnel
    # full of repeated circular hoops in the final macro composition.
    for k in range(7):
        yy = tunnel_y_start + k * 1.20
        bpy.ops.mesh.primitive_torus_add(
            major_radius=tunnel_radius - 0.008, minor_radius=0.010,
            major_segments=48, minor_segments=8,
            location=(0, yy, 3.28), rotation=(math.radians(90), 0, 0)
        )
        apply_mat(bpy.context.object, tunnel_ring_mat)
        bpy.context.object.name = "Subtle_Vessel_Wall_Ridge"
    # Four longitudinal fibres define the inside of the vessel.
    for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
        x = math.cos(angle) * tunnel_radius
        z = 3.28 + math.sin(angle) * tunnel_radius
        curve_tube(
            "Longitudinal_Vessel_Fibre",
            [(x, tunnel_y_start + n*(tunnel_y_end-tunnel_y_start)/5, z) for n in range(6)],
            0.018, tunnel_fibre_mat
        )
    # One continuous central stream carries the viewer's eye into the lumen.
    flow_mat = emissive("Xylem_Flow_Glow", (0.025, 0.42, 0.82), 1.05)
    curve_tube("Central_Water_Flow", [(0, tunnel_y_start+0.1, 3.28),
               (0, 1.2, 3.28), (0, 4.2, 3.28), (0, tunnel_y_end-0.2, 3.28)],
               0.048, flow_mat)

    # V13: three slim helical flow filaments make the stream read as directional
    # transport through the vessel, rather than isolated decorative beads.
    filament_mat = emissive("Water_Flow_Filaments", (0.035, 0.48, 0.82), 1.15)
    for lane in range(3):
        phase = lane * (math.tau / 4.0)
        points = []
        for step in range(13):
            t = step / 12.0
            yy = tunnel_y_start + 0.18 + t * (tunnel_y_end - tunnel_y_start - 0.36)
            angle = phase + t * math.tau * 2.1
            radius = 0.135
            points.append((radius * math.cos(angle), yy,
                           3.28 + radius * math.sin(angle)))
        curve_tube("Helical_Water_Flow_Filament", points, 0.030, filament_mat, 8)

    # Animate the filament glow so the vessel wall carries moving-looking
    # highlights even between the individual water pulses.
    filament_bsdf = filament_mat.node_tree.nodes.get("Principled BSDF")
    for frame, strength in [(1,0.45),(75,1.25),(150,0.55),(225,1.35),(END,0.55)]:
        filament_bsdf.inputs["Emission Strength"].default_value = strength
        filament_bsdf.inputs["Emission Strength"].keyframe_insert(
            data_path="default_value", frame=frame)

    # Keep the macro stream visually simple: one central flow and three
    # helical filaments, rather than several competing parallel ribbons.

    # V20: replace bead-like macro droplets with short travelling streaks.
    # Each streak is aligned tangentially to the helical path so it reads as a
    # moving highlight in the head-on vessel view, not as another round bead.
    for i in range(6):
        streak = uv("Travelling_Water_Flow_Streak", (0,0,3.28),
                    (0.016,0.016,0.145), filament_mat, 20, 12)
        phase = i * 2.399963
        offset = (i % 4) * 0.28
        for frame, yy, turns in [(1,-0.10+offset,0.0),
                                 (120,1.05+offset,1.25),
                                 (240,2.55+offset,2.55),
                                 (END,4.05+offset,3.85)]:
            angle = phase + turns * math.tau
            radius = 0.19
            streak.location = (radius*math.cos(angle), yy,
                               3.28 + radius*math.sin(angle))
            tangent = Vector((-math.sin(angle), 0.0, math.cos(angle)))
            streak.rotation_euler = tangent.to_track_quat("Z", "Y").to_euler()
            streak.keyframe_insert(data_path="location", frame=frame)
            streak.keyframe_insert(data_path="rotation_euler", frame=frame)

    # No floating 3D labels: clean, synchronized captions will be composited later.

    # V6 camera journey: preserve the V5 establishing shot and trunk approach,
    # then travel only partway into the vessel so the final tunnel remains readable.
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

    # A gradual, continuous dolly-in; the final target sits on the actual
    # front-facing xylem window rather than the trunk's centre.
    key_location(camera, 1, (0,-14.2,4.32))
    key_location(camera, 105, (0,-15.8,4.05))
    key_location(camera, 210, (0,-8.2,3.55))
    # V24: keep the camera just outside the solid trunk, aligned with the
    # open vessel mouth. The trunk is a solid mesh, so moving through its
    # volume would occlude the view; looking through the mouth reveals the lumen.
    # V27: keep the camera outside the trunk and look through the real
    # Boolean-carved entrance along the vessel axis. A wider macro lens keeps
    # the complete mouth in frame while preserving the tunnel depth.
    key_location(camera, 275, (0,-2.00,3.28))
    key_location(camera, END, (0,-2.00,3.28))
    for frame, loc in [
        (1,(0,0.0,2.45)),
        (105,(0,-0.12,2.72)),
        (210,(0,-0.55,3.05)),
        (275,(0,3.25,3.28)),
        (END,(0,4.10,3.28))
    ]:
        target.location = loc
        target.keyframe_insert(data_path="location", frame=frame)
    # V28: the later lens keyframes are the active ones in Blender. Keep
    # the establishing/approach framing, then use a genuinely wider macro
    # lens for the final view through the vessel entrance.
    for frame,lens in [(1,48),(105,40),(210,48),(275,28),(END,28)]:
        camera.data.lens = lens
        camera.data.keyframe_insert(data_path="lens", frame=frame)

    # Three-point studio lighting with soft highlights and a cool rim.
    bpy.ops.object.light_add(type="AREA", location=(-5,-7,9))
    key_light = bpy.context.object
    key_light.data.energy = 1850
    key_light.data.shape = "DISK"
    key_light.data.size = 7
    key_light.rotation_euler = (math.radians(25),0,math.radians(-25))
    bpy.ops.object.light_add(type="AREA", location=(5,-1,6))
    fill = bpy.context.object
    fill.data.energy = 1150
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
    scene.camera.data.dof.aperture_fstop = 16.0
    scene.render.filepath = output
    os.makedirs(os.path.dirname(output), exist_ok=True)
    bpy.ops.render.render(animation=True)
    print("Xylem showcase rendered:", output)

if __name__ == "__main__":
    main()
