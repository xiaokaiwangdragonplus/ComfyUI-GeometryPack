"""
Preview mesh with interactive 3D viewer.

Displays mesh in an interactive Three.js viewer with orbit controls.
Allows rotating, panning, and zooming to inspect the mesh geometry.
"""

import trimesh as trimesh_module
import os
import tempfile
import uuid

try:
    import folder_paths
    COMFYUI_OUTPUT_FOLDER = folder_paths.get_output_directory()
except:
    COMFYUI_OUTPUT_FOLDER = None


class PreviewMeshNode:
    """
    Preview mesh with interactive 3D viewer.

    Displays mesh in an interactive Three.js viewer with orbit controls.
    Allows rotating, panning, and zooming to inspect the mesh geometry.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trimesh": ("TRIMESH",),
            },
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "preview_mesh"
    CATEGORY = "geompack/visualization"

    def preview_mesh(self, trimesh):
        """
        Export mesh to GLB and prepare for 3D preview.

        Args:
            trimesh: Input trimesh_module.Trimesh object

        Returns:
            dict: UI data for frontend widget
        """
        print(f"[PreviewMesh] Preparing preview: {len(trimesh.vertices)} vertices, {len(trimesh.faces)} faces")

        # Generate unique filename
        filename = f"preview_{uuid.uuid4().hex[:8]}.glb"

        # Use ComfyUI's output directory
        if COMFYUI_OUTPUT_FOLDER:
            filepath = os.path.join(COMFYUI_OUTPUT_FOLDER, filename)
        else:
            filepath = os.path.join(tempfile.gettempdir(), filename)

        # Export to GLB (best format for Three.js)
        try:
            trimesh.export(filepath, file_type='glb')
            print(f"[PreviewMesh] Exported to: {filepath}")
        except Exception as e:
            print(f"[PreviewMesh] Export failed: {e}")
            # Fallback to OBJ
            filename = filename.replace('.glb', '.obj')
            filepath = filepath.replace('.glb', '.obj')
            trimesh.export(filepath, file_type='obj')
            print(f"[PreviewMesh] Exported to OBJ: {filepath}")

        # Calculate bounding box info for camera setup
        bounds = trimesh.bounds
        extents = trimesh.extents
        max_extent = max(extents)

        # Return metadata for frontend widget
        return {
            "ui": {
                "mesh_file": [filename],
                "vertex_count": [len(trimesh.vertices)],
                "face_count": [len(trimesh.faces)],
                "bounds_min": [bounds[0].tolist()],
                "bounds_max": [bounds[1].tolist()],
                "extents": [extents.tolist()],
                "max_extent": [float(max_extent)],
            }
        }


NODE_CLASS_MAPPINGS = {
    "GeomPackPreviewMesh": PreviewMeshNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackPreviewMesh": "Preview Mesh",
}
