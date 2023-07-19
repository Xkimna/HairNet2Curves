import bpy
import os
import shutil
import subprocess
from bpy.types import Operator, Panel
from bpy.props import StringProperty
import bpy.utils.previews
from mathutils import Vector
from . import m_geometrynode


bl_info = {
    "name": "HairNet2Curves",
    "description": "Use HairNet to generate hair curves from pictures",
    "author": "kiana",
    "version": (2, 2),
    "blender": (3, 5, 0),
    "location": "View3D > Tools",
    "warning": "",
    "category": "Development",
}


def env_install():
    addon_path = os.path.dirname(os.path.abspath(__file__))
    req_path = os.path.join(addon_path, 'setup\\requirements.txt')
    cmd = 'cmd /k pip install -r "{}"'.format(req_path)
    try:
        subprocess.Popen(cmd, shell=True)
    except OSError as e:
        print("ERROR:", e)


def get_system_python_executable():
    command = 'py -0p'

    try:
        result = subprocess.check_output(command, shell=True, universal_newlines=True)
        lines = result.strip().split('\n')
        python_executable = lines[-1].strip().split('       ')[-1].strip()
        return python_executable
    except subprocess.CalledProcessError as e:
        print("Error to find python.exe:", e)


def update_save_path(self, context):
    if not self.is_save:
        context.scene.save_path = ""


# 定义Blender操作面板
class MyPanel(Panel):
    bl_label = "HairNet2Curves"
    bl_idname = "OBJECT_PT_my_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HairNet2Curves"

    def draw(self, context):
        layout = self.layout

        # 1.Select a picture
        box = layout.box()
        box.operator("my_plugin.load_image", text="1. Select Image File", icon='FILE_IMAGE')
        image_path = context.scene.get("image_path", "")
        box.label(text="Selected images: " + image_path)
        box.operator_context = 'INVOKE_DEFAULT'

        layout.separator()

        # 3.Run predict.py
        # # 3.0 Image preprocessing
        # box = layout.box()
        # box.operator("my_plugin.preprocess", text="2. Image preprocessing", icon='NODE_TEXTURE')
        # 3.1 Setting
        box = layout.box()
        box.label(text="Setting:")
        # + Smooth or not
        box.prop(context.scene, "is_gaussian", text="Smooth strands")
        # + Import head.obj
        box.prop(context.scene, "is_head", text="Import head model")
        # + Select the save path, when not saved the output file is automatically saved in the temp file of the plugin
        box.prop(context.scene, "is_save", text="Save results：")
        if context.scene.is_save:
            box.operator("my_plugin.save_path", text="select save path", icon='FILEBROWSER')
            save_path = context.scene.get("save_path", "")
            box.label(text="Saved in: " + save_path)
            box.operator_context = 'INVOKE_DEFAULT'

        # 3.2 Run predict.py
        box.operator("my_plugin.run_main", text="2. Generate Hair", icon='PLAY')

        layout.separator()

        # 4.Mesh to curve
        # 4.1 Setting
        box = layout.box()
        box.label(text="Setting:")
        # + Attaching curves to the head
        box.prop(context.scene, "is_link_head", text="Snap to head model：")
        if context.scene.is_link_head:
            if context.object is not None:
                box.prop_search(context.object, "head_object", bpy.data, "objects", text="")

        box.operator("my_plugin.convert_to_hair_curves", text="3.Convert to Hair Curves", icon='STRANDS')


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    ckpt_file_path: bpy.props.StringProperty(
        name="CKPT File Path",
        subtype='FILE_PATH',
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ckpt'),
        description='Folder path to the pre-trained model. Replace it only when you have trained a new model!'
    )
    environment_file_path: bpy.props.StringProperty(
        name="Environment File Path",
        subtype='FILE_PATH',
        # default=r'D:\anaconda3\envs\tensorflow\python.exe',
        default=get_system_python_executable(),
        description='The path to the [python.exe] file of the network runtime environment'
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        split = row.split(factor=0.236)
        split.label(text="Configure Environment:")
        split_right = split.column()
        split_right.operator("my_plugin.env_install", text="Install", icon='SETTINGS')
        layout.prop(self, "ckpt_file_path")
        layout.prop(self, "environment_file_path")


class EnvInstallOperator(Operator):
    """Configure the runtime environment"""
    bl_idname = "my_plugin.env_install"
    bl_label = "Install Environment"

    def execute(self, context):
        env_install()
        return {'FINISHED'}


class LoadImageOperator(Operator):
    """Load a hair picture"""
    bl_idname = "my_plugin.load_image"
    bl_label = "Select a image"

    filepath: StringProperty(subtype="FILE_PATH")

    # @classmethod
    # def poll(cls, context):
    #     return context.object is not None

    def execute(self, context):
        self.report({'INFO'}, "Selected file: " + self.filepath)
        context.scene["image_path"] = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SelectSavePathOperator(Operator):
    """Select the path to save the .obj file for the hair mesh and the .png file for the hair preview"""
    bl_idname = "my_plugin.save_path"
    bl_label = "Select a save path"

    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        self.report({'INFO'}, "Selected file: " + self.filepath)
        context.scene["save_path"] = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class RunMainOperator(Operator):
    """Execute the hairnet program"""
    bl_idname = "my_plugin.run_main"
    bl_label = "Run Main"

    def execute(self, context):
        # predict 2D directions from a real hair map
        image_path = context.scene.get("image_path", "")
        preferences = bpy.context.preferences.addons[__name__].preferences
        env_dir = preferences.environment_file_path
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        main_dir = os.path.join(addon_dir, "hair_detection/main.py")

        # delete cache
        cache_path1 = os.path.join(addon_dir, "temp/orient_img")
        cache_path2 = os.path.join(addon_dir, "temp/orient_img_with_body")
        cache_path3 = os.path.join(addon_dir, "temp/orient_img_with_body_256")
        folder_paths = [cache_path1, cache_path2, cache_path3]

        for folder_path in folder_paths:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print(f"Cache cleared：{folder_path}")
            else:
                print(f"No cache：{folder_path}")

        # hair detection
        args = ["--workspace", addon_dir,
                "--image_path", image_path]
        cmd = [env_dir, main_dir] + args
        subprocess.Popen(cmd).wait()

        # hair orient2D
        exe_path = os.path.join(addon_dir, "hair_orient2D\\build\\Debug\\Orient2D.exe")
        arg1 = "1"
        arg2 = os.path.join(addon_dir, "temp\\")
        cmd = [exe_path, arg1, arg2]
        subprocess.Popen(cmd).wait()
        self.report({'INFO'}, 'Preprocess Finished')


        # network setting
        preferences = bpy.context.preferences.addons[__name__].preferences
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        env_dir = preferences.environment_file_path
        ckpt_dir = preferences.ckpt_file_path
        main_dir = os.path.join(addon_dir, "m_predict.py")
        input_dir = context.scene.get("image_path", "")
        input_preprocessed_dir = os.path.join(addon_dir, "temp\\orient_img_with_body_256\\input_preprocessed.exr.png")
        input_file_name = input_dir[input_dir.rfind("\\") + 1:input_dir.rfind(".")]
        save_dir = context.scene.get("save_path", "")
        is_gaussian = context.scene.is_gaussian

        args = ["--exp_dir", addon_dir,
                "--tgt_dir", input_preprocessed_dir,
                "--ckpt_dir", ckpt_dir,
                "--save_dir", save_dir,
                "--save_name", input_file_name,
                "--gaussian_flag", str(is_gaussian)]
        cmd = [env_dir, main_dir] + args

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        returncode = process.returncode

        if returncode == 0:
            print("Command executed successfully.")
            print("Output:", output.decode())
            if context.scene.is_head:
                bpy.ops.import_scene.obj(filepath=os.path.join(addon_dir, "head_model.obj"))
            if context.scene.is_save:
                bpy.ops.import_scene.obj(filepath=os.path.join(save_dir, input_file_name + "_output.obj"))
            else:
                bpy.ops.import_scene.obj(filepath=os.path.join(addon_dir, "temp/output.obj"))
        else:
            print(f"Command failed with return code: {returncode}")
            print("Output:", output.decode())
            print("Error:", error.decode())

        self.report({'INFO'}, 'Run Finished')

        return {'FINISHED'}


class ConvertToHairCurveOperator(bpy.types.Operator):
    """Convert selected object to curves and add a geometry node modifier with hair curve profile"""
    bl_idname = "my_plugin.convert_to_hair_curves"
    bl_label = "Convert To HairCurve Operator"

    def execute(self, context):
        # Get the selected object
        hair = bpy.context.active_object
        if hair is None:
            self.report({'ERROR'}, "No active object found")
            return {'CANCELLED'}

        # Convert the object to curve
        bpy.ops.object.convert(target='CURVE')

        # Convert the curve to curves
        bpy.ops.object.convert(target='CURVES')

        # Add a geometry node modifier: Surface Deform
        mod_curves = hair.modifiers.new(name="HairNet Surface Deform", type='NODES')
        mod_curves.node_group = bpy.data.node_groups.get("Surface Deform")

        if mod_curves.node_group is None:
            mod_curves.node_group = m_geometrynode.new_Surface_Deform_GeoNode_Group()

        if context.scene.is_link_head:
            head = bpy.context.object.head_object

            # Add a geometry node modifier: Rest Position
            has_modifier = False
            for modifier in head.modifiers:
                if modifier.type == 'NODES' and modifier.name == "HairNet Rest Position":
                    has_modifier = True
            if not has_modifier:
                mod_head = head.modifiers.new(name="HairNet Rest Position", type='NODES')
                mod_head.node_group = bpy.data.node_groups.get("'HairNet Rest Position")
                if mod_head.node_group is None:
                    mod_head.node_group = m_geometrynode.new_Rest_Position_GeoNode_Group()

            hair.data.surface = head
            hair.data.surface_uv_map = "UVMap"
            bpy.ops.curves.sculptmode_toggle()
            bpy.ops.curves.select_all(action='SELECT')
            bpy.ops.curves.snap_curves_to_surface(attach_mode='NEAREST')
            bpy.ops.curves.sculptmode_toggle()
            bpy.context.scene.render.hair_subdiv = 2

            # Add a geometry node modifier: Interspersed Restoration
            mod_curves2 = hair.modifiers.new(name="HairNet Interspersed Restoration", type='NODES')
            mod_curves2.node_group = m_geometrynode.new_Interspersed_Restoration_GeoNode_Group()
            mod_curves2.node_group = bpy.data.node_groups.get("HairNet Interspersed Restoration")
            if mod_curves2.node_group is None:
                mod_curves2.node_group = m_geometrynode.new_Interspersed_Restoration_GeoNode_Group()

        self.report({'INFO'}, 'Converted Finished')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MyPanel)
    bpy.utils.register_class(EnvInstallOperator)
    bpy.utils.register_class(AddonPreferences)
    # bpy.utils.register_class(ImagePreprocess)
    bpy.utils.register_class(LoadImageOperator)
    bpy.types.Scene.image_path = bpy.props.StringProperty(
        name="Image Path",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input_ref.png'),
        subtype="FILE_PATH"
    )
    bpy.types.Scene.is_gaussian = bpy.props.BoolProperty(name="Is Gaussian", default=True)
    bpy.types.Scene.is_head = bpy.props.BoolProperty(name="Is Head", default=True)
    bpy.types.Scene.is_save = bpy.props.BoolProperty(name="Is Save", default=False, update=update_save_path)
    bpy.utils.register_class(SelectSavePathOperator)
    bpy.types.Scene.save_path = bpy.props.StringProperty(
        name="Save Path",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp'),
        subtype="FILE_PATH"
    )
    bpy.utils.register_class(RunMainOperator)
    bpy.utils.register_class(ConvertToHairCurveOperator)
    bpy.types.Scene.is_link_head = bpy.props.BoolProperty(name="Is Link Head", default=True)
    bpy.types.Object.head_object = bpy.props.PointerProperty(type=bpy.types.Object)


def unregister():
    bpy.utils.unregister_class(MyPanel)
    bpy.utils.unregister_class(EnvInstallOperator)
    bpy.utils.unregister_class(AddonPreferences)
    # bpy.utils.unregister_class(ImagePreprocess)
    bpy.utils.unregister_class(LoadImageOperator)
    del bpy.types.Scene.image_path
    del bpy.types.Scene.is_gaussian
    del bpy.types.Scene.is_head
    del bpy.types.Scene.is_save
    bpy.utils.unregister_class(SelectSavePathOperator)
    del bpy.types.Scene.save_path
    bpy.utils.unregister_class(RunMainOperator)
    bpy.utils.unregister_class(ConvertToHairCurveOperator)
    del bpy.types.Scene.is_link_head
    del bpy.types.Object.head_object


if __name__ == "__main__":
    register()
