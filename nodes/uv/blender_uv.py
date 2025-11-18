"""
Unified Blender UV - Multiple UV projection methods via Blender.

Supports:
- smart_uv_project: Automatic seam-based unwrapping
- cube_projection: Project onto 6 cube faces
- cylinder_projection: Cylindrical projection
- sphere_projection: Spherical/equirectangular projection

Parameters are method-specific; unused ones are ignored.
"""

import trimesh as trimesh_module
import os
import subprocess
import tempfile
import math

from .._utils import blender_bridge


class BlenderUVNode:
    """
    Unified Blender UV - Multiple UV projection methods via Blender.

    Supports:
    - smart_uv_project: Automatic seam-based unwrapping
    - cube_projection: Project onto 6 cube faces
    - cylinder_projection: Cylindrical projection
    - sphere_projection: Spherical/equirectangular projection

    Parameters are method-specific; unused ones are ignored.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trimesh": ("TRIMESH",),
                "method": ([
                    "smart_uv_project",
                    "cube_projection",
                    "cylinder_projection",
                    "sphere_projection"
                ], {"default": "smart_uv_project"}),
            },
            "optional": {
                # Smart UV Project params
                "angle_limit": ("FLOAT", {
                    "default": 66.0,
                    "min": 1.0,
                    "max": 89.0,
                    "step": 1.0
                }),
                "island_margin": ("FLOAT", {
                    "default": 0.02,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                # Projection params
                "scale_to_bounds": (["true", "false"], {"default": "true"}),
                "cube_size": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1
                }),
                "cylinder_radius": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1
                }),
            }
        }

    RETURN_TYPES = ("TRIMESH", "STRING")
    RETURN_NAMES = ("unwrapped_mesh", "info")
    FUNCTION = "uv_project"
    CATEGORY = "geompack/uv"

    def uv_project(self, trimesh, method,
                   angle_limit=66.0, island_margin=0.02,
                   scale_to_bounds="true", cube_size=1.0, cylinder_radius=1.0):
        """
        Apply UV projection using Blender.

        Args:
            trimesh: Input mesh
            method: UV projection method
            [other params]: Method-specific parameters

        Returns:
            tuple: (unwrapped_mesh, info_string)
        """
        print(f"[BlenderUV] Input: {len(trimesh.vertices)} vertices, {len(trimesh.faces)} faces")
        print(f"[BlenderUV] Method: {method}")

        # Find Blender
        blender_path = blender_bridge.find_blender()

        # Create temp files
        with tempfile.NamedTemporaryFile(suffix='.obj', delete=False) as f_in:
            input_path = f_in.name
            trimesh.export(input_path)

        with tempfile.NamedTemporaryFile(suffix='.obj', delete=False) as f_out:
            output_path = f_out.name

        try:
            # Build method-specific script
            if method == "smart_uv_project":
                angle_limit_rad = math.radians(angle_limit)
                uv_script = f"""
bpy.ops.uv.smart_project(
    angle_limit={angle_limit_rad},
    island_margin={island_margin},
    area_weight=0.0,
    correct_aspect=True,
    scale_to_bounds={'True' if scale_to_bounds == 'true' else 'False'}
)
"""
                info_params = f"Angle Limit: {angle_limit}°\nIsland Margin: {island_margin}"

            elif method == "cube_projection":
                uv_script = f"""
bpy.ops.uv.cube_project(
    cube_size={cube_size},
    scale_to_bounds={'True' if scale_to_bounds == 'true' else 'False'}
)
"""
                info_params = f"Cube Size: {cube_size}"

            elif method == "cylinder_projection":
                uv_script = f"""
bpy.ops.uv.cylinder_project(
    radius={cylinder_radius},
    scale_to_bounds={'True' if scale_to_bounds == 'true' else 'False'}
)
"""
                info_params = f"Cylinder Radius: {cylinder_radius}"

            elif method == "sphere_projection":
                uv_script = f"""
bpy.ops.uv.sphere_project(
    scale_to_bounds={'True' if scale_to_bounds == 'true' else 'False'}
)
"""
                info_params = "Equirectangular projection"

            else:
                raise ValueError(f"Unknown method: {method}")

            # Complete Blender script
            script = f"""
import bpy

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import mesh
bpy.ops.wm.obj_import(filepath='{input_path}')

# Get imported object
obj = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj

# Switch to edit mode and unwrap
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
{uv_script}
bpy.ops.object.mode_set(mode='OBJECT')

# Export with UVs
bpy.ops.wm.obj_export(
    filepath='{output_path}',
    export_selected_objects=True,
    export_uv=True,
    export_materials=False
)
"""

            print(f"[BlenderUV] Running Blender in background mode...")
            result = subprocess.run(
                [blender_path, '--background', '--python-expr', script],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                raise RuntimeError(f"Blender failed: {result.stderr}")

            # Load the unwrapped mesh
            unwrapped = trimesh_module.load(output_path, process=False)

            if isinstance(unwrapped, trimesh_module.Scene):
                unwrapped = unwrapped.dump(concatenate=True)

            # Preserve metadata
            unwrapped.metadata = trimesh.metadata.copy()
            unwrapped.metadata['uv_unwrap'] = {
                'algorithm': f'blender_{method}',
                'method': method
            }

            info = f"""Blender UV Results:

Method: {method.replace('_', ' ').title()}
{info_params}

Input: {len(trimesh.vertices):,} vertices, {len(trimesh.faces):,} faces
Output: {len(unwrapped.vertices):,} vertices, {len(unwrapped.faces):,} faces

UV coordinates applied successfully.
"""

            print(f"[BlenderUV] Complete: {len(unwrapped.vertices)} vertices, {len(unwrapped.faces)} faces")
            return (unwrapped, info)

        finally:
            # Cleanup temp files
            if os.path.exists(input_path):
                os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)


NODE_CLASS_MAPPINGS = {
    "GeomPackBlenderUV": BlenderUVNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackBlenderUV": "UV Unwrap (Blender)",
}
