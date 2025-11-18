"""
Remesh UV Node - Remesh with texture preservation using Blender
"""

import numpy as np
import trimesh as trimesh_module
import os
import subprocess
import tempfile

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def _extract_texture(mesh):
    """Extract texture from trimesh visual to temp file."""
    if not PIL_AVAILABLE:
        return None, None

    if not hasattr(mesh, 'visual'):
        return None, None

    uvs = None
    if hasattr(mesh.visual, 'uv'):
        uvs = mesh.visual.uv

    texture_image = None
    if hasattr(mesh.visual, 'material') and mesh.visual.material is not None:
        material = mesh.visual.material
        if hasattr(material, 'image'):
            img = material.image
            if isinstance(img, Image.Image):
                texture_image = img
            elif isinstance(img, str) and os.path.exists(img):
                texture_image = Image.open(img)

    if texture_image is None and uvs is not None:
        # Create checkerboard placeholder
        texture_image = Image.new('RGB', (512, 512), color=(200, 200, 200))
        arr = np.array(texture_image)
        for i in range(0, 512, 64):
            for j in range(0, 512, 64):
                if (i // 64 + j // 64) % 2 == 0:
                    arr[i:i+64, j:j+64] = [100, 100, 100]
        texture_image = Image.fromarray(arr)

    if texture_image is None:
        return None, uvs

    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    texture_image.save(temp_file.name)
    temp_file.close()
    return temp_file.name, uvs


def _load_as_comfy_image(texture_path):
    """Convert texture to ComfyUI IMAGE format."""
    if not PIL_AVAILABLE or not TORCH_AVAILABLE:
        return None

    img = Image.open(texture_path).convert("RGB")
    img_array = np.array(img).astype(np.float32) / 255.0
    return torch.from_numpy(img_array)[None,]


class BlenderRemeshWithTexture:
    """
    Remesh with texture preservation using Blender baking.

    Workflow:
    1. Remeshes the input geometry using selected algorithm
    2. Generates new UV coordinates for the remeshed surface
    3. Bakes the original texture onto the new UVs using Blender
    4. Returns remeshed mesh with baked texture
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trimesh": ("TRIMESH",),
                "remesh_method": (["voxel", "quadriflow"], {"default": "quadriflow"}),
                "voxel_size": ("FLOAT", {
                    "default": 0.05,
                    "min": 0.001,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "target_face_count": ("INT", {
                    "default": 5000,
                    "min": 100,
                    "max": 1000000,
                    "step": 100
                }),
                "texture_size": ([512, 1024, 2048, 4096], {"default": 2048}),
                "bake_margin": ("INT", {
                    "default": 16,
                    "min": 0,
                    "max": 64,
                    "step": 1
                }),
            },
        }

    RETURN_TYPES = ("TRIMESH", "IMAGE", "STRING")
    RETURN_NAMES = ("remeshed_mesh", "baked_texture", "info")
    FUNCTION = "remesh_with_texture"
    CATEGORY = "geompack/texture_remeshing"

    def remesh_with_texture(self, trimesh, remesh_method, voxel_size, target_face_count,
                           texture_size, bake_margin):
        """Remesh a textured mesh while preserving texture through Blender baking."""
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL required. Install: pip install Pillow")

        if not TORCH_AVAILABLE:
            raise RuntimeError("torch required. Install: pip install torch")

        from .._utils import blender_bridge

        print(f"[BlenderRemeshWithTexture] Input: {len(trimesh.vertices)} vertices, {len(trimesh.faces)} faces")

        # Extract texture from source mesh
        texture_path, original_uvs = _extract_texture(trimesh)
        if texture_path is None:
            raise ValueError("Input mesh must have texture data")

        # Find Blender
        blender_path = blender_bridge.find_blender()

        # Create temp files
        source_obj = tempfile.NamedTemporaryFile(suffix='_source.obj', delete=False)
        output_obj = tempfile.NamedTemporaryFile(suffix='_output.obj', delete=False)
        baked_texture = tempfile.NamedTemporaryFile(suffix='_baked.png', delete=False)

        try:
            # Export source mesh with UVs
            trimesh.export(source_obj.name, include_texture=True)
            source_obj.close()

            # Build Blender script
            if remesh_method == "voxel":
                remesh_code = f"obj.data.remesh_voxel_size = {voxel_size}\nbpy.ops.object.voxel_remesh()"
            else:
                remesh_code = f"bpy.ops.object.quadriflow_remesh(target_faces={target_face_count})"

            script = f"""
import bpy

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.ops.wm.obj_import(filepath='{source_obj.name}')
source_obj = bpy.context.selected_objects[0]
source_obj.name = 'Source'

bpy.ops.object.duplicate()
target_obj = bpy.context.selected_objects[0]
target_obj.name = 'Target'

bpy.context.view_layer.objects.active = target_obj
{remesh_code}

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

if len(source_obj.data.materials) > 0:
    source_mat = source_obj.data.materials[0]
else:
    source_mat = bpy.data.materials.new('SourceMat')
    source_obj.data.materials.append(source_mat)

source_mat.use_nodes = True
source_nodes = source_mat.node_tree.nodes
source_nodes.clear()

tex_coord = source_nodes.new('ShaderNodeTexCoord')
tex_image = source_nodes.new('ShaderNodeTexImage')
loaded_image = bpy.data.images.load('{texture_path}')
tex_image.image = loaded_image
bsdf = source_nodes.new('ShaderNodeBsdfDiffuse')
output_node = source_nodes.new('ShaderNodeOutputMaterial')
source_mat.node_tree.links.new(tex_coord.outputs['UV'], tex_image.inputs['Vector'])
source_mat.node_tree.links.new(tex_image.outputs['Color'], bsdf.inputs['Color'])
source_mat.node_tree.links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

if len(target_obj.data.materials) > 0:
    target_mat = target_obj.data.materials[0]
else:
    target_mat = bpy.data.materials.new('TargetMat')
    target_obj.data.materials.append(target_mat)

target_mat.use_nodes = True
target_nodes = target_mat.node_tree.nodes
target_nodes.clear()

bake_image = bpy.data.images.new('BakedTexture', {texture_size}, {texture_size})
bake_node = target_nodes.new('ShaderNodeTexImage')
bake_node.image = bake_image
bake_node.select = True
target_nodes.active = bake_node

bpy.ops.object.select_all(action='DESELECT')
source_obj.select_set(True)
target_obj.select_set(True)
bpy.context.view_layer.objects.active = target_obj

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.cycles.samples = 32
bpy.context.scene.render.bake.use_selected_to_active = True
bpy.context.scene.render.bake.margin = {bake_margin}
bpy.context.scene.render.bake.cage_extrusion = 0.1
bpy.context.scene.render.bake.use_pass_direct = False
bpy.context.scene.render.bake.use_pass_indirect = False
bpy.context.scene.render.bake.use_pass_color = True

bpy.ops.object.bake(type='DIFFUSE')

bake_image.filepath_raw = '{baked_texture.name}'
bake_image.file_format = 'PNG'
bake_image.save()

bpy.ops.object.select_all(action='DESELECT')
target_obj.select_set(True)
bpy.ops.wm.obj_export(
    filepath='{output_obj.name}',
    export_selected_objects=True,
    export_uv=True,
    export_materials=True
)
"""

            print(f"[BlenderRemeshWithTexture] Running Blender...")
            result = subprocess.run(
                [blender_path, '--background', '--python-expr', script],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                raise RuntimeError(f"Blender failed: {result.stderr}")

            # Load remeshed mesh
            remeshed = trimesh_module.load(output_obj.name, process=False)
            if isinstance(remeshed, trimesh_module.Scene):
                remeshed = remeshed.dump(concatenate=True)

            # Load texture as ComfyUI IMAGE
            comfy_image = _load_as_comfy_image(baked_texture.name)

            info = f"""Remesh with Texture (Blender)
Method: {remesh_method}
Vertices: {len(trimesh.vertices)} -> {len(remeshed.vertices)}
Faces: {len(trimesh.faces)} -> {len(remeshed.faces)}
Texture size: {texture_size}x{texture_size}
"""

            print(f"[BlenderRemeshWithTexture] Complete")
            return (remeshed, comfy_image, info)

        finally:
            # Cleanup
            for path in [source_obj.name, output_obj.name, texture_path, baked_texture.name]:
                if os.path.exists(path):
                    try:
                        os.unlink(path)
                    except:
                        pass


# Node mappings
NODE_CLASS_MAPPINGS = {
    "GeomPackRemeshUV": BlenderRemeshWithTexture,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackRemeshUV": "Remesh UV",
}
