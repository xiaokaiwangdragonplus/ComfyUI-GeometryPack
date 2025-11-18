"""
Preview mesh with VTK.js viewer including filters.

Displays mesh in an interactive VTK.js viewer with trackball controls
and filter controls (smoothing, outline, cutting plane).
Better for scientific visualization, mesh analysis, and large datasets.
"""

import trimesh as trimesh_module
import os
import tempfile
import uuid
from ._vtp_export import export_mesh_with_scalars_vtp

try:
    import folder_paths
    COMFYUI_OUTPUT_FOLDER = folder_paths.get_output_directory()
except:
    COMFYUI_OUTPUT_FOLDER = None


class PreviewMeshVTKWithNormalsNode:
    """
    Preview mesh with VTK.js scientific visualization viewer including filters.

    Displays mesh in an interactive VTK.js viewer with trackball controls
    and filter controls (smoothing, outline, cutting plane).
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
    FUNCTION = "preview_mesh_vtk_with_normals"
    CATEGORY = "geompack/visualization"

    def preview_mesh_vtk_with_normals(self, trimesh):
        """
        Export mesh to STL and prepare for VTK.js preview with filters.

        Args:
            trimesh: Input trimesh_module.Trimesh object

        Returns:
            dict: UI data for frontend widget
        """
        print(f"[PreviewMeshVTKWithNormals] Preparing preview: {len(trimesh.vertices)} vertices, {len(trimesh.faces)} faces")

        # Check if mesh has vertex attributes (scalar fields)
        has_vertex_attrs = hasattr(trimesh, 'vertex_attributes') and len(trimesh.vertex_attributes) > 0

        print(f"[PreviewMeshVTKWithNormals] hasattr(trimesh, 'vertex_attributes'): {hasattr(trimesh, 'vertex_attributes')}")
        if hasattr(trimesh, 'vertex_attributes'):
            print(f"[PreviewMeshVTKWithNormals] trimesh.vertex_attributes: {trimesh.vertex_attributes.keys()}")
            print(f"[PreviewMeshVTKWithNormals] Number of vertex attributes: {len(trimesh.vertex_attributes)}")

        # Generate unique filename
        # Use VTP format if we have vertex attributes, otherwise STL
        if has_vertex_attrs:
            filename = f"preview_vtk_normals_{uuid.uuid4().hex[:8]}.vtp"
            file_format = 'vtp'
            print(f"[PreviewMeshVTKWithNormals] Mesh has vertex attributes, using VTP format")
        else:
            filename = f"preview_vtk_normals_{uuid.uuid4().hex[:8]}.stl"
            file_format = 'stl'
            print(f"[PreviewMeshVTKWithNormals] No vertex attributes found, using STL format")

        # Use ComfyUI's output directory
        if COMFYUI_OUTPUT_FOLDER:
            filepath = os.path.join(COMFYUI_OUTPUT_FOLDER, filename)
        else:
            filepath = os.path.join(tempfile.gettempdir(), filename)

        # Export mesh with vertex attributes
        try:
            if file_format == 'vtp':
                # Export to VTK PolyData format (XML) which preserves vertex attributes
                export_mesh_with_scalars_vtp(trimesh, filepath)
                print(f"[PreviewMeshVTKWithNormals] Exported VTP with {len(trimesh.vertex_attributes)} scalar fields to: {filepath}")
            else:
                # Export to STL (no scalar data)
                trimesh.export(filepath, file_type='stl')
                print(f"[PreviewMeshVTKWithNormals] Exported to STL: {filepath}")
        except Exception as e:
            print(f"[PreviewMeshVTKWithNormals] Export failed: {e}")
            # Fallback to OBJ
            filename = filename.replace('.vtp', '.obj').replace('.stl', '.obj')
            filepath = filepath.replace('.vtp', '.obj').replace('.stl', '.obj')
            trimesh.export(filepath, file_type='obj')
            print(f"[PreviewMeshVTKWithNormals] Exported to OBJ: {filepath}")

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
            print(f"[PreviewMeshVTKWithNormals] Could not calculate volume/area: {e}")

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

        print(f"[PreviewMeshVTKWithNormals] Mesh info: watertight={is_watertight}, volume={volume}, area={area}, fields={len(field_names)}")

        return {"ui": ui_data}


NODE_CLASS_MAPPINGS = {
    "GeomPackPreviewMeshVTKWithNormals": PreviewMeshVTKWithNormalsNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackPreviewMeshVTKWithNormals": "Preview Mesh (VTK with Normals)",
}
