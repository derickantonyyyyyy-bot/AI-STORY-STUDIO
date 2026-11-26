"""
AI STORY STUDIO — reusable stylized character foundation
Run:
  blender -b -P scripts/blender_character_foundation.py -- out/character-foundation.mp4
Creates a rigged, expressive cartoon character, a simple studio, and a short wave/blink preview.
"""
import bpy, math, os, sys, shutil, subprocess
from mathutils import Vector

FPS = 30
DURATION = 4
END = FPS * DURATION

def output_path():
    args = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    return os.path.abspath(args[0] if args else "out/character-foundation.mp4")

def mat(name, color, rough=0.48, subsurface=0.06, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metallic
    if "Subsurface Weight" in p.inputs:
        p.inputs["Subsurface Weight"].default_value = subsurface
    return m

def smooth(o):
    if o.type == "MESH":
        for f in o.data.polygons: f.use_smooth = True
    return o

def uv(name, loc, scale, material, seg=32, rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    smooth(o); o.data.materials.append(material)
    return o

def capsule(name, a, b, radius, material, depth_scale=1.0):
    a,b=Vector(a),Vector(b); mid=(a+b)*0.5; d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=d.length, location=mid)
    o=bpy.context.object; o.name=name
    o.rotation_mode="QUATERNION"; o.rotation_quaternion=d.to_track_quat("Z","Y")
    o.data.materials.append(material)
    bevel=o.modifiers.new("Soft_Limb_Edges","BEVEL"); bevel.width=radius*0.72; bevel.segments=4
    o.modifiers.new("Weighted_Normals","WEIGHTED_NORMAL")
    ja=uv(name+"_JointA", a, (radius,radius*depth_scale,radius), material)
    jb=uv(name+"_JointB", b, (radius,radius*depth_scale,radius), material)
    return [o, ja, jb]

def curve(name, points, radius, material):
    c=bpy.data.curves.new(name,"CURVE"); c.dimensions="3D"; c.bevel_depth=radius; c.bevel_resolution=4
    s=c.splines.new("BEZIER"); s.bezier_points.add(len(points)-1)
    for bp,co in zip(s.bezier_points,points):
        bp.co=co; bp.handle_left_type="AUTO"; bp.handle_right_type="AUTO"
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(material)
    return o

def make_rig():
    data=bpy.data.armatures.new("StoryCharacter_Rig")
    arm=bpy.data.objects.new("StoryCharacter_Rig",data); bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active=arm; arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bones = {
      "root":((0,0,0.12),(0,0,0.72),None),
      "pelvis":((0,0,0.72),(0,0,1.18),"root"),
      "spine":((0,0,1.18),(0,0,2.05),"pelvis"),
      "neck":((0,0,2.05),(0,0,2.30),"spine"),
      "head":((0,0,2.30),(0,0,3.18),"neck"),
      "upper_arm.L":((-.34,0,1.98),(-.70,0,1.48),"spine"),
      "forearm.L":((-.70,0,1.48),(-.72,-.01,1.02),"upper_arm.L"),
      "upper_arm.R":((.34,0,1.98),(.70,0,1.48),"spine"),
      "forearm.R":((.70,0,1.48),(.72,-.01,1.02),"upper_arm.R"),
      "thigh.L":((-.19,0,.78),(-.22,0,.40),"pelvis"),
      "shin.L":((-.22,0,.40),(-.22,-.02,.08),"thigh.L"),
      "thigh.R":((.19,0,.78),(.22,0,.40),"pelvis"),
      "shin.R":((.22,0,.40),(.22,-.02,.08),"thigh.R")
    }
    for name,(head,tail,parent) in bones.items():
        b=data.edit_bones.new(name); b.head=head; b.tail=tail
        if parent: b.parent=data.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.show_in_front=True
    return arm

def attach(obj, arm, bone):
    world=obj.matrix_world.copy()
    obj.parent=arm; obj.parent_type="BONE"; obj.parent_bone=bone
    obj.matrix_world=world

def main():
    out=output_path()
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene
    engines={e.identifier for e in scene.render.bl_rna.properties["engine"].enum_items}
    scene.render.engine="BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else ("BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else "CYCLES")
    scene.render.resolution_x=720; scene.render.resolution_y=1280; scene.render.resolution_percentage=100
    scene.render.fps=FPS; scene.frame_start=1; scene.frame_end=END
    # Blender builds without FFmpeg support cannot write video directly.
    # Render a PNG sequence first; encode it to MP4 if an ffmpeg executable is available.
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGB"
    frame_dir=os.path.splitext(out)[0]+"_frames"
    os.makedirs(frame_dir,exist_ok=True)
    scene.render.filepath=os.path.join(frame_dir,"frame_")
    scene.view_settings.view_transform="AgX"
    scene.render.film_transparent=False

    skin=mat("Warm_Caramel_Skin",(0.62,0.34,0.20),0.42,0.12)
    shirt=mat("Teal_Tshirt",(0.025,0.34,0.39),0.55,0.04)
    pants=mat("Deep_Navy_Trousers",(0.035,0.075,0.16),0.62,0.02)
    shoes=mat("Soft_Charcoal_Shoes",(0.025,0.035,0.05),0.6,0.0)
    hair=mat("Dark_Brown_Hair",(0.055,0.025,0.018),0.5,0.02)
    white=mat("Eye_Whites",(0.94,0.96,1.0),0.28,0.02)
    iris=mat("Hazel_Iris",(0.24,0.12,0.045),0.28,0.0)
    black=mat("Pupils",(0.008,0.012,0.018),0.22,0.0)
    brow=mat("Eyebrows",(0.07,0.028,0.018),0.65,0.0)
    mouth=mat("Mouth",(0.16,0.035,0.035),0.6,0.0)

    rig=make_rig()
    # Torso and pelvis
    torso=uv("TShirt_Torso",(0,0,1.62),(.43,.28,.62),shirt); attach(torso,rig,"spine")
    pelvis=uv("Trouser_Hips",(0,0,.91),(.34,.25,.27),pants); attach(pelvis,rig,"pelvis")
    # Neck and head
    neck=uv("Neck",(0,0,2.20),(.16,.16,.22),skin); attach(neck,rig,"neck")
    head=uv("Expressive_Head",(0,-.015,2.70),(.43,.36,.53),skin,48,32); attach(head,rig,"head")
    haircap=uv("Hair_Cap",(0,.005,3.00),(.445,.365,.30),hair,48,24); attach(haircap,rig,"head")
    fringe=uv("Hair_Front",(0,-.31,2.96),(.30,.10,.16),hair); attach(fringe,rig,"head")
    # Ears
    for side in (-1,1):
        ear=uv("Ear",(side*.425,-.005,2.69),(.105,.09,.15),skin); attach(ear,rig,"head")
    # Face features on the front (-Y)
    for side in (-1,1):
        eye=uv("Eye_White",(side*.17,-.337,2.77),(.105,.045,.135),white); attach(eye,rig,"head")
        ir=uv("Iris",(side*.17,-.378,2.765),(.052,.025,.073),iris); attach(ir,rig,"head")
        pu=uv("Pupil",(side*.17,-.399,2.765),(.025,.014,.043),black); attach(pu,rig,"head")
        gl=uv("Eye_Glint",(side*.185,-.412,2.795),(.012,.008,.018),white); attach(gl,rig,"head")
        brow_obj=curve("Eyebrow",[(side*.08,-.355,2.94),(side*.17,-.37,2.97),(side*.27,-.35,2.94)],.025,brow)
        attach(brow_obj,rig,"head")
        # Smile corners and cheek tint details
        cheek=uv("Cheek",(side*.27,-.315,2.57),(.075,.018,.045),skin); attach(cheek,rig,"head")
    smile=curve("Friendly_Smile",[(-.12,-.354,2.535),(0,-.372,2.505),(.12,-.354,2.535)],.018,mouth); attach(smile,rig,"head")
    nose=uv("Nose",(0,-.375,2.66),(.065,.075,.075),skin); attach(nose,rig,"head")

    # Arms and hands, split into independently rigged upper/lower sections
    for side,label in [(-1,"L"),(1,"R")]:
        sh=(side*.36,0,1.98); el=(side*.69,-.005,1.48); wr=(side*.72,-.025,1.06)
        upper=capsule("Upper_Arm_"+label,sh,el,.145,shirt,.82)
        for part in upper: attach(part,rig,"upper_arm."+label)
        elbow=uv("Elbow_"+label,el,(.14,.13,.14),shirt); attach(elbow,rig,"upper_arm."+label)
        fore=capsule("Forearm_"+label,el,wr,.105,skin,.90)
        for part in fore: attach(part,rig,"forearm."+label)
        hand=uv("Hand_"+label,(side*.73,-.035,.98),(.14,.11,.16),skin); attach(hand,rig,"forearm."+label)
    # Legs and shoes
    for side,label in [(-1,"L"),(1,"R")]:
        hip=(side*.19,0,.84); knee=(side*.22,0,.40); ankle=(side*.22,-.015,.11)
        thigh=capsule("Thigh_"+label,hip,knee,.19,pants,.82)
        for part in thigh: attach(part,rig,"thigh."+label)
        shin=capsule("Shin_"+label,knee,ankle,.125,pants,.85)
        for part in shin: attach(part,rig,"shin."+label)
        foot=uv("Sneaker_"+label,(side*.22,-.12,.075),(.17,.28,.095),shoes); attach(foot,rig,"shin."+label)

    # Wave animation: the character's left arm (screen-right) lifts and waves.
    scene.frame_set(1)
    upper=rig.pose.bones["upper_arm.R"]
    fore=rig.pose.bones["forearm.R"]
    upper.rotation_mode="XYZ"; fore.rotation_mode="XYZ"
    for frame,ang in [(1,0),(12,-.75),(22,-.95),(31,-.55),(42,-.95),(60,-.75),(90,-.75),(120,-.75)]:
        upper.rotation_euler[1]=ang
        upper.keyframe_insert(data_path="rotation_euler",frame=frame)
        fore.rotation_euler[1]=(-.18 if frame<12 else -.55)
        fore.keyframe_insert(data_path="rotation_euler",frame=frame)
    # Gentle head nod
    headbone=rig.pose.bones["head"]; headbone.rotation_mode="XYZ"
    for f,a in [(1,0),(35,.035),(65,0),(95,-.025),(120,0)]:
        headbone.rotation_euler[0]=a; headbone.keyframe_insert(data_path="rotation_euler",frame=f)
    # Lighting and studio backdrop
    world=bpy.data.worlds.new("Soft_Blue_Studio") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world=world; world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=(.18,.30,.43,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=.55
    floor_mat=mat("Studio_Floor",(0.48,.68,.78),.82,0)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.035))
    bpy.context.object.name="Studio_Floor"; bpy.context.object.data.materials.append(floor_mat)
    def area(name,loc,power,size,color,target):
        bpy.ops.object.light_add(type="AREA",location=loc)
        l=bpy.context.object; l.name=name; l.data.energy=power; l.data.shape="DISK"; l.data.size=size; l.data.color=color
        l.rotation_euler=(Vector(target)-l.location).to_track_quat("-Z","Y").to_euler()
    area("Key_Softbox",(-3,-4,5),520,4.0,(1.0,.82,.68),(0,0,1.7))
    area("Fill_Softbox",(3,-2,3.2),360,3.0,(.62,.82,1.0),(0,0,1.8))
    area("Rim_Light",(0,2,4.2),650,3.0,(.45,.78,1.0),(0,0,2))
    bpy.ops.object.camera_add(location=(0,-8.8,2.35))
    cam=bpy.context.object; cam.name="Character_Camera"
    cam.rotation_euler=(Vector((0,0,1.58))-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.type="ORTHO"; cam.data.ortho_scale=7.2; scene.camera=cam
    scene.camera.data.lens=50
    # Blender 5.x uses layered Actions, so the legacy Action.fcurves
    # collection is not available. Blender's default keyframe interpolation
    # is BEZIER; leave it unchanged for smooth pose-to-pose motion.
    scene.frame_set(1)
    os.makedirs(os.path.dirname(out),exist_ok=True)
    # Save an editable Blender project alongside the preview.
    blend_path=os.path.splitext(out)[0]+".blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    bpy.ops.render.render(animation=True)
    ffmpeg=shutil.which("ffmpeg")
    if ffmpeg:
        pattern=os.path.join(frame_dir,"frame_%04d.png")
        cmd=[ffmpeg,"-y","-framerate",str(FPS),"-i",pattern,"-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart",out]
        subprocess.run(cmd,check=True)
        print("CHARACTER_PREVIEW:",out)
    else:
        print("FFMPEG_NOT_FOUND: PNG frames saved in",frame_dir)
        print("Install FFmpeg and run this command from PowerShell:")
        print('ffmpeg -y -framerate 30 -i "'+os.path.join(frame_dir,"frame_%04d.png")+'" -c:v libx264 -pix_fmt yuv420p "'+out+'"')
    print("EDITABLE_BLEND:",blend_path)

if __name__=="__main__":
    main()
