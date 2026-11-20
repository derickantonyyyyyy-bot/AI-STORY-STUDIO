"""
AI Story Studio — Blender 3D scene prototype.

Run:
  blender -b -P scripts/blender_scene.py -- out/story-props.json out/blender-story.mp4

This prototype creates a stylized 3D forest set, a simple cartoon character,
animated limbs, camera movement, and scene-to-scene lighting changes.
It intentionally does not claim character-rig lip-sync or audio yet.
"""
import bpy
import json
import math
import os
import sys
from mathutils import Vector

def args_after_dashes():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) < 2:
        raise SystemExit("Usage: blender -b -P scripts/blender_scene.py -- <story-props.json> <output.mp4>")
    return os.path.abspath(args[0]), os.path.abspath(args[1])

def mat(name, color, roughness=0.82):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1)
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    material.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = roughness
    return material

def assign(obj, material):
    obj.data.materials.append(material)
    return obj

def uv_sphere(name, location, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.shade_smooth()
    return assign(obj, material)

def cylinder(name, location, radius, depth, material, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    return assign(obj, material)

def cone(name, location, radius, depth, material):
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=radius, radius2=0, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    return assign(obj, material)

def key(obj, frame, location=None, rotation=None):
    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)

def build_tree(x, y, scale, trunk_mat, leaf_mat, index):
    trunk = cylinder(f"TreeTrunk_{index}", (x, y, 1.45 * scale), .23 * scale, 2.9 * scale, trunk_mat)
    crown1 = cone(f"TreeCrownA_{index}", (x, y, 3.2 * scale), 1.25 * scale, 2.5 * scale, leaf_mat)
    crown2 = cone(f"TreeCrownB_{index}", (x, y, 4.15 * scale), .92 * scale, 2.0 * scale, leaf_mat)
    return [trunk, crown1, crown2]

def build_character():
    skin = mat("Character_Skin", (.78, .48, .31))
    shirt = mat("Character_TealShirt", (.12, .42, .39))
    trousers = mat("Character_Trousers", (.12, .19, .28))
    hair = mat("Character_Hair", (.12, .075, .055))
    eyes = mat("Character_Eyes", (.025, .025, .02))
    shoes = mat("Character_Shoes", (.08, .055, .045))

    root = bpy.data.objects.new("CharacterRoot", None)
    bpy.context.collection.objects.link(root)
    body = uv_sphere("CharacterBody", (0, 0, 1.55), (.58, .38, .78), shirt)
    head = uv_sphere("CharacterHead", (0, -.02, 2.55), (.52, .48, .56), skin)
    cap = uv_sphere("CharacterHair", (0, .015, 2.91), (.53, .48, .29), hair)
    left_eye = uv_sphere("Eye_L", (-.19, -.455, 2.62), (.055, .035, .085), eyes)
    right_eye = uv_sphere("Eye_R", (.19, -.455, 2.62), (.055, .035, .085), eyes)
    mouth = uv_sphere("CharacterSmile", (0, -.482, 2.39), (.12, .025, .035), hair)
    parts = [body, head, cap, left_eye, right_eye, mouth]
    for side, x in [("L", -.25), ("R", .25)]:
        arm = cylinder(f"Arm_{side}", (x * 2.0, 0, 1.72), .13, .82, skin)
        arm.rotation_euler[1] = (-.22 if side == "L" else .22)
        leg = cylinder(f"Leg_{side}", (x, 0, .68), .16, .78, trousers)
        shoe = uv_sphere(f"Shoe_{side}", (x, -.12, .28), (.23, .34, .13), shoes)
        parts.extend([arm, leg, shoe])
    for obj in parts:
        obj.parent = root
    return root, [o for o in parts if o.name.startswith("Arm_")], head


def build_xylem_reveal():
    """Build a clean, non-graphic educational tree cross-section with animated water beads."""
    root = bpy.data.objects.new("XylemRevealRoot", None)
    bpy.context.collection.objects.link(root)
    bark = mat("Xylem_CutBark", (.30, .14, .065))
    wood = mat("Xylem_Wood", (.72, .48, .24))
    ring_mat = mat("Xylem_GrowthRings", (.38, .22, .10))
    tube_mat = mat("Xylem_Tubes", (.08, .48, .62), .35)
    water_mat = mat("Xylem_Water", (.12, .72, 1.0), .2)

    # A circular trunk cross-section faces the incoming camera.
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.05, depth=.18, location=(0, 0, 0))
    disk = bpy.context.object
    disk.name = "Tree_CrossSection_Wood"
    disk.rotation_euler[0] = math.radians(90)
    assign(disk, wood)
    disk.parent = root
    disk.matrix_parent_inverse = root.matrix_world.inverted()

    bpy.ops.mesh.primitive_torus_add(major_radius=.84, minor_radius=.035, major_segments=64, minor_segments=12, location=(0, -.105, 0))
    ring = bpy.context.object
    ring.name = "Tree_Growth_Ring"
    ring.rotation_euler[0] = math.radians(90)
    assign(ring, ring_mat)
    ring.parent = root
    ring.matrix_parent_inverse = root.matrix_world.inverted()

    # Parallel xylem vessels sit behind the cut surface.
    for i, x in enumerate([-.62, -.31, 0, .31, .62]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.075, depth=2.5, location=(x, .42, 1.35))
        tube = bpy.context.object
        tube.name = f"Xylem_Vessel_{i+1}"
        assign(tube, tube_mat)
        tube.parent = root
        tube.matrix_parent_inverse = root.matrix_world.inverted()

    beads = []
    for i, x in enumerate([-.62, -.31, 0, .31, .62]):
        bead = uv_sphere(f"Water_Drop_{i+1}", (x, .20, .25 + (i % 2) * .25), (.105, .105, .105), water_mat)
        bead.parent = root
        bead.matrix_parent_inverse = root.matrix_world.inverted()
        beads.append(bead)

    focus = bpy.data.objects.new("XylemRevealFocus", None)
    bpy.context.collection.objects.link(focus)
    focus.location = (0, 3.0, 1.25)
    return root, focus, beads

def main():
    props_path, output_path = args_after_dashes()
    with open(props_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    story = payload.get("story", payload)
    scenes = story.get("scenes", [])
    if not scenes:
        raise SystemExit("No scenes found in story-props JSON.")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    available_engines = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
    if "BLENDER_EEVEE_NEXT" in available_engines:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    elif "BLENDER_EEVEE" in available_engines:
        scene.render.engine = "BLENDER_EEVEE"
    else:
        raise SystemExit(f"No supported Eevee render engine found. Available engines: {sorted(available_engines)}")
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    # Blender 5.x requires selecting VIDEO media before the FFMPEG format.
    scene.render.image_settings.media_type = "VIDEO"
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.filepath = output_path
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.world.color = (.035, .055, .07)
    scene.view_settings.view_transform = "Standard"

    ground_mat = mat("ForestFloor", (.075, .19, .12))
    trunk_mat = mat("TreeBark", (.19, .095, .045))
    leaf_mats = [
        mat("Leaves_Deep", (.045, .20, .12)),
        mat("Leaves_Mid", (.08, .31, .16)),
        mat("Leaves_Light", (.17, .39, .20)),
    ]
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = "ForestGround"
    assign(ground, ground_mat)

    tree_index = 0
    for row_y, count, spread, scale in [(5, 7, 13, 1.2), (10, 9, 17, 1.55), (16, 11, 22, 1.9)]:
        for i in range(count):
            x = -spread + (2 * spread * i / max(1, count - 1))
            build_tree(x, row_y + (i % 2) * 1.2, scale * (.8 + (i % 3) * .12),
                       trunk_mat, leaf_mats[i % len(leaf_mats)], tree_index)
            tree_index += 1

    root, arms, head = build_character()
    xylem_root, xylem_focus, water_beads = build_xylem_reveal()
    bpy.ops.object.camera_add(location=(0, -11, 4.0))
    camera = bpy.context.object
    camera.name = "StoryCamera"
    target = Vector((0, 3, 2.0))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 42
    # Keep emotional close-ups aimed at the character instead of empty forest space.
    focus = bpy.data.objects.new("CharacterFocus", None)
    bpy.context.collection.objects.link(focus)
    focus.location = (0, 3, 2.0)
    track = camera.constraints.new(type="TRACK_TO")
    track.target = focus
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    scene.camera = camera

    bpy.ops.object.light_add(type="AREA", location=(-5, -3, 9))
    key_light = bpy.context.object
    key_light.data.energy = 1700
    key_light.data.shape = "DISK"
    key_light.data.size = 7
    key_light.rotation_euler = (math.radians(25), 0, math.radians(-25))
    bpy.ops.object.light_add(type="AREA", location=(5, 5, 6))
    rim_light = bpy.context.object
    rim_light.data.energy = 1100
    rim_light.data.color = (.48, .68, 1.0)
    rim_light.data.size = 6
    rim_light.rotation_euler = (math.radians(35), 0, math.radians(150))

    total_frames = sum(int(s.get("duration_seconds", 10)) for s in scenes) * scene.render.fps
    scene.frame_start = 1
    scene.frame_end = total_frames
    cursor = 1
    for index, item in enumerate(scenes):
        duration = int(item.get("duration_seconds", 10)) * scene.render.fps
        start, end = cursor, cursor + duration - 1
        key(root, start, (0, 0, 0), (0, 0, 0))
        key(root, start + duration // 2, (0, .45, 0), (0, 0, .04 if index % 2 == 0 else -.04))
        key(root, end, (0, .9, 0), (0, 0, 0))
        for arm_i, arm in enumerate(arms):
            base = -.18 if arm_i == 0 else .18
            key(arm, start, rotation=(base, 0, 0))
            key(arm, start + duration // 3, rotation=(base + .55, 0, 0))
            key(arm, start + (2 * duration) // 3, rotation=(base - .28, 0, 0))
            key(arm, end, rotation=(base, 0, 0))
        key(camera, start, (0, -11, 4.0))
        key(camera, end, ((-0.45 if index % 2 else 0.45), -9.2, 3.7))

        # Emotion-led punch-in at the scene's dramatic beat, followed by a release.
        emotion = str(item.get("emotion", "neutral")).lower()
        emotion_lenses = {
            "neutral": 42, "happy": 48, "sad": 64, "surprised": 60,
            "worried": 62, "curious": 54, "determined": 52, "awe": 56,
        }
        base_lens = 42
        close_lens = emotion_lenses.get(emotion, base_lens)
        beat = start + duration // 2
        punch_frame = max(start + 2, beat - 5)
        release_frame = min(end - 2, beat + max(8, duration // 5))
        camera.data.lens = base_lens
        camera.data.keyframe_insert(data_path="lens", frame=start)
        camera.data.lens = base_lens
        camera.data.keyframe_insert(data_path="lens", frame=punch_frame)
        camera.data.lens = close_lens
        camera.data.keyframe_insert(data_path="lens", frame=beat)
        camera.data.lens = close_lens
        camera.data.keyframe_insert(data_path="lens", frame=release_frame)
        camera.data.lens = base_lens
        camera.data.keyframe_insert(data_path="lens", frame=end)

        # Reveal the tree's internal water-transport system as a continuous camera dive.
        transition_type = str(item.get("transition_type", "cut")).lower()
        xylem_root.scale = (.001, .001, .001)
        xylem_root.keyframe_insert(data_path="scale", frame=start)
        if transition_type in ("xray_reveal", "cross_section"):
            reveal_frame = min(end - 2, start + 18)
            xylem_root.scale = (1, 1, 1)
            xylem_root.keyframe_insert(data_path="scale", frame=reveal_frame)
            xylem_root.keyframe_insert(data_path="scale", frame=end)
            key(camera, start, (0, -11, 4.0))
            key(camera, reveal_frame, (0, .25, 2.8))
            key(camera, end, (0, .10, 2.8))
            key(focus, start, (0, 3.0, 2.0))
            key(focus, reveal_frame, (0, 3.0, 1.25))
            key(focus, end, (0, 3.0, 1.25))
            camera.data.lens = 24
            camera.data.keyframe_insert(data_path="lens", frame=reveal_frame)
            camera.data.lens = 38
            camera.data.keyframe_insert(data_path="lens", frame=min(end, reveal_frame + 10))
            for bead_i, bead in enumerate(water_beads):
                z0 = .20 + (bead_i % 2) * .25
                key(bead, reveal_frame, (bead.location.x, bead.location.y, z0))
                key(bead, min(end, reveal_frame + 42), (bead.location.x, bead.location.y, z0 + 1.75))
        else:
            xylem_root.keyframe_insert(data_path="scale", frame=end)

        transition_start = max(start, end - 12)
        if transition_type == "whip_pan":
            current_x = camera.location.x
            key(camera, transition_start, (current_x, camera.location.y, camera.location.z))
            key(camera, end - 3, (current_x + (2.8 if index % 2 == 0 else -2.8),
                                  camera.location.y, camera.location.z))
            key(camera, end, (current_x, camera.location.y, camera.location.z))
        elif transition_type == "dolly_zoom":
            base_y = camera.location.y
            camera.data.lens = 42
            camera.data.keyframe_insert(data_path="lens", frame=transition_start)
            key(camera, transition_start, (camera.location.x, base_y, camera.location.z))
            camera.data.lens = 24
            camera.data.keyframe_insert(data_path="lens", frame=end - 3)
            key(camera, end - 3, (camera.location.x, base_y + 2.2, camera.location.z))
            camera.data.lens = 42
            camera.data.keyframe_insert(data_path="lens", frame=end)
            key(camera, end, (camera.location.x, base_y, camera.location.z))

        # Small head tilts reinforce the selected emotion without overacting.
        head_tilt = {
            "sad": 0.12, "worried": 0.10, "curious": -0.13,
            "surprised": -0.08, "awe": -0.10, "happy": 0.04,
            "determined": 0.02, "neutral": 0.0,
        }.get(emotion, 0.0)
        key(head, start, rotation=(head_tilt * 0.35, 0, 0))
        key(head, beat, rotation=(head_tilt, 0, 0))
        key(head, end, rotation=(head_tilt * 0.35, 0, 0))
        cursor += duration

    # Blender 5.2 uses layered actions; default keyframe interpolation is already Bezier.
    # Avoid legacy Action.fcurves access so this script works across Blender versions.
    scene.render.filepath = output_path
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bpy.ops.render.render(animation=True)
    print(f"Rendered Blender prototype: {output_path}")

if __name__ == "__main__":
    main()
