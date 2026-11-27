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

def make_controller(name, location, parent=None):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=location)
    e=bpy.context.object; e.name=name
    if parent:
        e.parent=parent
    return e

def attach(obj, controller):
    # Empty controllers avoid bone-length scaling on child meshes.
    world=obj.matrix_world.copy()
    obj.parent=controller
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
    # Stable object-space controllers keep every mesh at its authored size.
    root_ctrl=make_controller("CTRL_Root",(0,0,0))
    body_ctrl=make_controller("CTRL_Body",(0,0,1.18),root_ctrl)
    head_ctrl=make_controller("CTRL_Head",(0,0,2.30),body_ctrl)
    shoulder_l=make_controller("CTRL_Shoulder_L",(-.36,0,1.98),body_ctrl)
    elbow_l=make_controller("CTRL_Elbow_L",(-.69,-.005,1.48),shoulder_l)
    shoulder_r=make_controller("CTRL_Shoulder_R",(.36,0,1.98),body_ctrl)
    elbow_r=make_controller("CTRL_Elbow_R",(.69,-.005,1.48),shoulder_r)
    hip_l=make_controller("CTRL_Hip_L",(-.19,0,.84),body_ctrl)
    hip_r=make_controller("CTRL_Hip_R",(.19,0,.84),body_ctrl)
    # Torso and pelvis
    torso=uv("TShirt_Torso",(0,0,1.62),(.34,.235,.51),shirt); attach(torso,body_ctrl)
    pelvis=uv("Trouser_Hips",(0,0,.91),(.30,.225,.24),pants); attach(pelvis,body_ctrl)
    # Neck and head
    neck=uv("Neck",(0,0,2.20),(.13,.13,.19),skin); attach(neck,body_ctrl)
    head=uv("Expressive_Head",(0,-.015,2.70),(.36,.31,.44),skin,48,32); attach(head,head_ctrl)
    haircap=uv("Hair_Cap",(0,.005,2.98),(.385,.33,.245),hair,48,24); attach(haircap,head_ctrl)
    fringe=uv("Hair_Front",(0,-.285,2.94),(.27,.075,.12),hair); attach(fringe,head_ctrl)
    # Ears
    for side in (-1,1):
        ear=uv("Ear",(side*.385,-.005,2.69),(.075,.07,.12),skin); attach(ear,head_ctrl)
    # Face features on the front (-Y)
    for side in (-1,1):
        eye=uv("Eye_White",(side*.145,-.300,2.78),(.070,.035,.090),white); attach(eye,head_ctrl)
        ir=uv("Iris",(side*.145,-.337,2.775),(.040,.020,.052),iris); attach(ir,head_ctrl)
        pu=uv("Pupil",(side*.145,-.356,2.775),(.024,.014,.036),black); attach(pu,head_ctrl)
        gl=uv("Eye_Glint",(side*.132,-.370,2.798),(.010,.007,.013),white); attach(gl,head_ctrl)
        brow_obj=curve("Eyebrow",[(side*.065,-.310,2.925),(side*.145,-.325,2.945),(side*.225,-.310,2.925)],.016,brow)
        attach(brow_obj,head_ctrl)
        # Smile corners and cheek tint details
        cheek=uv("Cheek",(side*.235,-.285,2.57),(.055,.012,.035),skin); attach(cheek,head_ctrl)
    smile=curve("Friendly_Smile",[(-.10,-.318,2.535),(0,-.332,2.515),(.10,-.318,2.535)],.012,mouth); attach(smile,head_ctrl)
    nose=uv("Nose",(0,-.335,2.66),(.040,.048,.048),skin); attach(nose,head_ctrl)

    # Arms and hands, split into independently rigged upper/lower sections
    for side,label in [(-1,"L"),(1,"R")]:
        sh=(side*.36,0,1.98); el=(side*.69,-.005,1.48); wr=(side*.72,-.025,1.06)
        upper_ctrl=shoulder_l if label=="L" else shoulder_r
        fore_ctrl=elbow_l if label=="L" else elbow_r
        upper=capsule("Upper_Arm_"+label,sh,el,.090,shirt,.90)
        for part in upper: attach(part,upper_ctrl)
        elbow=uv("Elbow_"+label,el,(.088,.080,.088),shirt); attach(elbow,upper_ctrl)
        fore=capsule("Forearm_"+label,el,wr,.068,skin,.92)
        for part in fore: attach(part,fore_ctrl)
        hand=uv("Hand_"+label,(side*.73,-.035,.98),(.080,.060,.085),skin); attach(hand,fore_ctrl)
        # Five rounded fingers, subtly splayed for a readable hand silhouette.
        finger_offsets=[(-.048,-.045,.025),(-.024,-.060,.008),(0,-.065,-.004),(.024,-.060,.008),(.048,-.045,.025)]
        finger_lengths=[.075,.095,.105,.095,.070]
        for fi,((dx,dy,dz),flen) in enumerate(zip(finger_offsets,finger_lengths)):
            fx=side*.73+dx
            finger=uv("Finger_%s_%d"%(label,fi+1),(fx,-.055,.91+dz),(.015,.020,flen*.52),skin,20,16)
            attach(finger,fore_ctrl)
    # Legs and shoes
    for side,label in [(-1,"L"),(1,"R")]:
        hip=(side*.19,0,.84); knee=(side*.22,0,.40); ankle=(side*.22,-.015,.11)
        hip_ctrl=hip_l if label=="L" else hip_r
        thigh=capsule("Thigh_"+label,hip,knee,.115,pants,.90)
        for part in thigh: attach(part,hip_ctrl)
        shin=capsule("Shin_"+label,knee,ankle,.082,pants,.92)
        for part in shin: attach(part,hip_ctrl)
        foot=uv("Sneaker_"+label,(side*.22,-.12,.075),(.12,.19,.065),shoes); attach(foot,hip_ctrl)

    # Wave animation: the character's left arm (screen-right) lifts and waves.
    scene.frame_set(1)
    # Key the controller empties directly: no armature deformation or scale surprises.
    for frame,angle in [(1,0),(12,-.75),(22,-.95),(31,-.55),(42,-.95),(60,-.75),(90,-.75),(120,-.75)]:
        shoulder_r.rotation_euler[1]=angle
        shoulder_r.keyframe_insert(data_path="rotation_euler",frame=frame)
        elbow_r.rotation_euler[1]=(-.10 if frame<12 else -.42)
        elbow_r.keyframe_insert(data_path="rotation_euler",frame=frame)
    for f,a in [(1,0),(35,.025),(65,0),(95,-.018),(120,0)]:
        head_ctrl.rotation_euler[0]=a
        head_ctrl.keyframe_insert(data_path="rotation_euler",frame=f)
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
    cam.data.type="ORTHO"; cam.data.ortho_scale=5.0; scene.camera=cam
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
