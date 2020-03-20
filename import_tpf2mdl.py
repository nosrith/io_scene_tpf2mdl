import os.path
import re
import struct
import lupa

import bpy
from bpy_extras.wm_utils.progress_report import ProgressReport
from mathutils import Matrix


def execute(context, filepath, operator):
    return ImportTPF2Model(context, filepath, operator).execute()


class ImportTPF2Model:
    def __init__(self, context, filepath, operator):
        self.context = context
        self.filepath = filepath
        self.mod_res_path = filepath[0 : (filepath.rindex("models") - 1)]
        self.ext_package_paths = [
            os.path.join(operator.tpf2_app_path, "res", "scripts", "?.lua")
        ]
        self.current_collection = None
        self.auto_node_index = 0

    def execute(self):
        with ProgressReport(self.context.window_manager) as progress:
            progress.enter_substeps(1, "Importing OBJ {}...".format(self.filepath))

            data = self.load_lua_data(self.filepath)

            for lod_index in data["lods"]:
                self.current_collection = bpy.data.collections.new("lod{}".format(lod_index - 1))
                bpy.context.scene.collection.children.link(self.current_collection)

                lod_data = data["lods"][lod_index]
                self.parse_node(lod_data["node"], None)

            progress.leave_substeps("Finished importing: {}".format(self.filepath))

            return {'FINISHED'}

    def parse_node(self, node_data, parent_obj):
        if "name" in node_data:
            name = node_data["name"]
        else:
            name = "Node{}".format(self.auto_node_index)
            self.auto_node_index += 1

        if "mesh" in node_data:
            obj = bpy.data.objects.new(name, self.load_mesh(node_data["mesh"]))
        else:
            obj = bpy.data.objects.new(name, None)

        self.current_collection.objects.link(obj)
        if parent_obj is not None:
            obj.parent = parent_obj

        if "transf" in node_data:
            transf_data = list(node_data["transf"].values())
            transf_mat = Matrix((transf_data[0:4], transf_data[4:8], transf_data[8:12], transf_data[12:16])).transposed()
        else:
            transf_mat = Matrix.Identity(4)
        obj.matrix_local = transf_mat

        if "children" in node_data:
            for child_node_data in node_data["children"].values():
                self.parse_node(child_node_data, obj)

    def load_mesh(self, mesh_rel_path):
        mesh_full_path = os.path.join(self.mod_res_path, "models", "mesh", mesh_rel_path)

        mesh_data = self.load_lua_data(mesh_full_path)

        with open(mesh_full_path + ".blob", "rb") as fin:
            blob_data = fin.read()

        vertices = self.get_array_data(mesh_data["vertexAttr"]["position"], blob_data, "f", 3)
        uvs = self.get_array_data(mesh_data["vertexAttr"]["uv0"], blob_data, "f", 2)
        faces = self.get_array_data(mesh_data["subMeshes"][1]["indices"]["position"], blob_data, "i", 3)

        mesh = bpy.data.meshes.new(os.path.basename(mesh_rel_path))
        mesh.from_pydata(vertices, [], faces)

        return mesh

    def load_lua_data(self, path):
        with open(path, encoding="utf-8") as fin:
            raw_data_text = fin.read()

        escaped_data_text = re.sub(r"_\((\".+?\")\)", r"\1", raw_data_text)

        ext_package_paths_str = ";".join(self.ext_package_paths).replace("\\", "\\\\")
        print(ext_package_paths_str)

        lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        lua.execute("\n".join([
            'package.path = package.path .. ";' + ext_package_paths_str + '"',
            escaped_data_text
        ]))
        return lua.globals().data()

    def get_array_data(self, meta, blob, fmt, num_comp):
        offset = meta["offset"]
        count = meta["count"]
        target_blob = blob[offset : (offset + count)]
        raw_array = list(map(lambda t: t[0], struct.iter_unpack(fmt, target_blob)))
        return [raw_array[i : (i + num_comp)] for i in range(0, len(raw_array), num_comp)]
