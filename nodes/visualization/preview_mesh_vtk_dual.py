"""
Preview two meshes simultaneously with VTK.js viewer.

Combines two meshes with different vertex colors for easy visual comparison.
Useful for visualizing boolean operation inputs or comparing meshes side-by-side.
Exports to GLB format to preserve vertex colors.
"""

import trimesh as trimesh_module
import numpy as np
import os
import tempfile
import uuid

try:
    import folder_paths
    COMFYUI_OUTPUT_FOLDER = folder_paths.get_output_directory()
except:
    COMFYUI_OUTPUT_FOLDER = None


class PreviewMeshVTKDualNode:
    """
    Preview two meshes simultaneously with VTK.js viewer.

    Combines two meshes with different vertex colors for visual distinction.
    Perfect for comparing boolean operation inputs or any two meshes.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mesh_a": ("TRIMESH",),
                "mesh_b": ("TRIMESH",),
            },
            "optional": {
                "color_a": (["red", "blue", "green", "yellow", "cyan", "magenta", "orange", "purple"], {"default": "red"}),
                "color_b": (["red", "blue", "green", "yellow", "cyan", "magenta", "orange", "purple"], {"default": "blue"}),
                "opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "preview_dual_mesh"
    CATEGORY = "geompack/visualization"

    def preview_dual_mesh(self, mesh_a, mesh_b, color_a="red", color_b="blue", opacity=1.0):
        """
        Combine and preview two meshes with different colors.

        Args:
            mesh_a: First trimesh object
            mesh_b: Second trimesh object
            color_a: Color for mesh_a
            color_b: Color for mesh_b
            opacity: Opacity for both meshes (0.0-1.0)

        Returns:
            dict: UI data for frontend widget
        """
        print(f"[PreviewMeshVTKDual] Mesh A: {len(mesh_a.vertices)} vertices, {len(mesh_a.faces)} faces")
        print(f"[PreviewMeshVTKDual] Mesh B: {len(mesh_b.vertices)} vertices, {len(mesh_b.faces)} faces")
        print(f"[PreviewMeshVTKDual] Colors: {color_a}, {color_b}")

        # Color mapping (RGB values, brighter for better visibility)
        color_map = {
            "red": [255, 100, 100],
            "blue": [100, 150, 255],
            "green": [100, 255, 100],
            "yellow": [255, 255, 100],
            "cyan": [100, 255, 255],
            "magenta": [255, 100, 255],
            "orange": [255, 180, 100],
            "purple": [200, 100, 255],
        }

        # Calculate alpha channel from opacity
        alpha = int(opacity * 255)

        # Create copies to avoid modifying originals
        mesh_a_colored = mesh_a.copy()
        mesh_b_colored = mesh_b.copy()

        # Assign vertex colors to mesh_a
        color_a_rgba = color_map.get(color_a, [255, 100, 100]) + [alpha]
        mesh_a_colored.visual.vertex_colors = np.tile(
            color_a_rgba, (len(mesh_a.vertices), 1)
        ).astype(np.uint8)

        # Assign vertex colors to mesh_b
        color_b_rgba = color_map.get(color_b, [100, 150, 255]) + [alpha]
        mesh_b_colored.visual.vertex_colors = np.tile(
            color_b_rgba, (len(mesh_b.vertices), 1)
        ).astype(np.uint8)

        # Combine meshes
        try:
            combined = trimesh_module.util.concatenate([mesh_a_colored, mesh_b_colored])
            print(f"[PreviewMeshVTKDual] Combined mesh: {len(combined.vertices)} vertices, {len(combined.faces)} faces")
        except Exception as e:
            print(f"[PreviewMeshVTKDual] Failed to combine meshes: {e}")
            # Fallback: just use mesh_a
            combined = mesh_a_colored

        # Generate unique filename
        filename = f"preview_vtk_dual_{uuid.uuid4().hex[:8]}.glb"

        # Use ComfyUI's output directory
        if COMFYUI_OUTPUT_FOLDER:
            filepath = os.path.join(COMFYUI_OUTPUT_FOLDER, filename)
        else:
            filepath = os.path.join(tempfile.gettempdir(), filename)

        # Export to GLB (preserves vertex colors)
        try:
            combined.export(filepath, file_type='glb', include_normals=True)
            print(f"[PreviewMeshVTKDual] Exported to: {filepath}")
        except Exception as e:
            print(f"[PreviewMeshVTKDual] GLB export failed: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to OBJ
            filename = filename.replace('.glb', '.obj')
            filepath = filepath.replace('.glb', '.obj')
            combined.export(filepath, file_type='obj')
            print(f"[PreviewMeshVTKDual] Exported to OBJ fallback: {filepath}")

        # Calculate bounding box info
        bounds = combined.bounds
        extents = combined.extents
        max_extent = max(extents)

        # Individual mesh info
        bounds_a = mesh_a.bounds
        bounds_b = mesh_b.bounds

        # Return metadata for frontend widget
        ui_data = {
            "mesh_file": [filename],
            # Combined mesh info
            "vertex_count": [len(combined.vertices)],
            "face_count": [len(combined.faces)],
            "bounds_min": [bounds[0].tolist()],
            "bounds_max": [bounds[1].tolist()],
            "extents": [extents.tolist()],
            "max_extent": [float(max_extent)],
            # Mesh A info
            "mesh_a_vertices": [len(mesh_a.vertices)],
            "mesh_a_faces": [len(mesh_a.faces)],
            "mesh_a_bounds_min": [bounds_a[0].tolist()],
            "mesh_a_bounds_max": [bounds_a[1].tolist()],
            "mesh_a_watertight": [bool(mesh_a.is_watertight)],
            "mesh_a_color": [color_a],
            # Mesh B info
            "mesh_b_vertices": [len(mesh_b.vertices)],
            "mesh_b_faces": [len(mesh_b.faces)],
            "mesh_b_bounds_min": [bounds_b[0].tolist()],
            "mesh_b_bounds_max": [bounds_b[1].tolist()],
            "mesh_b_watertight": [bool(mesh_b.is_watertight)],
            "mesh_b_color": [color_b],
            # Visual settings
            "opacity": [float(opacity)],
        }

        print(f"[PreviewMeshVTKDual] Preview ready")

        return {"ui": ui_data}


NODE_CLASS_MAPPINGS = {
    "GeomPackPreviewMeshVTKDual": PreviewMeshVTKDualNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackPreviewMeshVTKDual": "Preview Mesh (VTK Dual)",
}
