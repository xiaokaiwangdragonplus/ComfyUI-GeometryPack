"""
Preview mesh with VTK.js scientific visualization viewer.

Displays mesh in an interactive VTK.js viewer with trackball controls.
Better for scientific visualization, mesh analysis, and large datasets.
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


class PreviewMeshVTKNode:
    """
    Preview mesh with VTK.js scientific visualization viewer.

    Displays mesh in an interactive VTK.js viewer with trackball controls.
    Better for scientific visualization, mesh analysis, and large datasets.
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
    FUNCTION = "preview_mesh_vtk"
    CATEGORY = "geompack/visualization"

    def preview_mesh_vtk(self, trimesh):
        """
        Export mesh to STL and prepare for VTK.js preview.

        Args:
            trimesh: Input trimesh_module.Trimesh object

        Returns:
            dict: UI data for frontend widget
        """
        print(f"[PreviewMeshVTK] Preparing preview: {len(trimesh.vertices)} vertices, {len(trimesh.faces)} faces")

        # Generate unique filename
        filename = f"preview_vtk_{uuid.uuid4().hex[:8]}.stl"

        # Use ComfyUI's output directory
        if COMFYUI_OUTPUT_FOLDER:
            filepath = os.path.join(COMFYUI_OUTPUT_FOLDER, filename)
        else:
            filepath = os.path.join(tempfile.gettempdir(), filename)

        # Export to STL (native format for VTK.js)
        try:
            trimesh.export(filepath, file_type='stl')
            print(f"[PreviewMeshVTK] Exported to: {filepath}")
        except Exception as e:
            print(f"[PreviewMeshVTK] Export failed: {e}")
            # Fallback to OBJ
            filename = filename.replace('.stl', '.obj')
            filepath = filepath.replace('.stl', '.obj')
            trimesh.export(filepath, file_type='obj')
            print(f"[PreviewMeshVTK] Exported to OBJ: {filepath}")

        # Calculate bounding box info for camera setup
        bounds = trimesh.bounds
        extents = trimesh.extents
        max_extent = max(extents)

        # Check if mesh is watertight
        is_watertight = trimesh.is_watertight

        # Calculate volume and area (only if watertight)
        volume = None
        area = None
        try:
            if is_watertight:
                volume = float(trimesh.volume)
            area = float(trimesh.area)
        except Exception as e:
            print(f"[PreviewMeshVTK] Could not calculate volume/area: {e}")

        # Get field names (vertex/face data arrays)
        field_names = []
        if hasattr(trimesh, 'vertex_attributes') and trimesh.vertex_attributes:
            field_names.extend([f"vertex.{k}" for k in trimesh.vertex_attributes.keys()])
        if hasattr(trimesh, 'face_attributes') and trimesh.face_attributes:
            field_names.extend([f"face.{k}" for k in trimesh.face_attributes.keys()])

        # Return metadata for frontend widget
        ui_data = {
            "mesh_file": [filename],
            "vertex_count": [len(trimesh.vertices)],
            "face_count": [len(trimesh.faces)],
            "bounds_min": [bounds[0].tolist()],
            "bounds_max": [bounds[1].tolist()],
            "extents": [extents.tolist()],
            "max_extent": [float(max_extent)],
            "is_watertight": [bool(is_watertight)],
        }

        # Add optional fields if available
        if volume is not None:
            ui_data["volume"] = [volume]
        if area is not None:
            ui_data["area"] = [area]
        if field_names:
            ui_data["field_names"] = [field_names]

        print(f"[PreviewMeshVTK] Mesh info: watertight={is_watertight}, volume={volume}, area={area}, fields={len(field_names)}")

        return {"ui": ui_data}


NODE_CLASS_MAPPINGS = {
    "GeomPackPreviewMeshVTK": PreviewMeshVTKNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackPreviewMeshVTK": "Preview Mesh (VTK)",
}
