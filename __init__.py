# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

bl_info = {
    "name": "TransportFever2 model",
    "author": "Nosrith",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Import TransportFever2 model",
    "category": "Import-Export"
}

import array
import os
import time

if "bpy" in locals():
    import importlib
    if "import_tpf2mdl" in locals():
        importlib.reload(import_tpf2mdl)

import bpy
from bpy_extras.io_utils import (
        ImportHelper,
        path_reference_mode,
        )
from bpy.props import (
        StringProperty,
        )


class ImportTPF2ModelOperator(bpy.types.Operator, ImportHelper):
    """Load a TransportFever2 model file"""
    bl_idname = "import_scene.tpf2mdl"
    bl_label = "Import TransportFever2 Model"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".mdl"
    filter_glob: StringProperty(
        default="*.mdl",
        options={'HIDDEN'},
    )
    tpf2_app_path: StringProperty(
        name="App path",
        description="App path",
        default="C:\\Program Files (x86)\\Steam\\steamapps\\common\\Transport Fever 2",
    )

    path_mode: path_reference_mode

    check_extension = True

    def execute(self, context):
        from . import import_tpf2mdl
        return import_tpf2mdl.execute(context, self.filepath, self)

    def draw(self, context):
        pass


class OBJ_PT_import_tpf2path(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"
    bl_label = "TPF2 Paths"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "IMPORT_SCENE_OT_tpf2mdl"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "tpf2_app_path")


def menu_func_import(self, context):
    self.layout.operator(ImportTPF2ModelOperator.bl_idname, text="TPF2 model (.mdl)")


classes = (
    ImportTPF2ModelOperator,
    OBJ_PT_import_tpf2path,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
