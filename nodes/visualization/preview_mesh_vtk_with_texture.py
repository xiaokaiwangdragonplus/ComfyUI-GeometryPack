"""
Preview mesh with VTK.js viewer optimized for textured/PBR meshes.

Exports mesh to GLB format to preserve textures, materials, UV coordinates,
and vertex colors. Uses VTK.js GLTFImporter for loading. Best choice for
meshes with textures or PBR materials.
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


class PreviewMeshVTKWithTextureNode:
    """
    Preview mesh with VTK.js viewer optimized for textured/PBR meshes.

    Exports mesh to GLB format to preserve textures, materials, UV coordinates,
    and vertex colors. Uses VTK.js GLTFImporter for loading. Best choice for
    meshes with textures or PBR materials.
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
    FUNCTION = "preview_mesh_vtk_with_texture"
    CATEGORY = "geompack/visualization"

    def preview_mesh_vtk_with_texture(self, trimesh):
        """
        Export mesh to GLB and prepare for VTK.js preview with texture support.

        Args:
            trimesh: Input trimesh_module.Trimesh object

        Returns:
            dict: UI data for frontend widget
        """
        print(f"[PreviewMeshVTKWithTexture] Preparing preview: {len(trimesh.vertices)} vertices, {len(trimesh.faces)} faces")

        # Check for texture/material information
        has_visual = hasattr(trimesh, 'visual') and trimesh.visual is not None
        visual_kind = None
        has_texture = False
        has_vertex_colors = False
        has_material = False

        if has_visual:
            visual_kind = trimesh.visual.kind
            if visual_kind == 'texture':
                has_texture = hasattr(trimesh.visual, 'material') and trimesh.visual.material is not None
                has_material = has_texture
                print(f"[PreviewMeshVTKWithTexture] Mesh has texture visual with material: {has_material}")
            elif visual_kind == 'vertex':
                has_vertex_colors = True
                print(f"[PreviewMeshVTKWithTexture] Mesh has vertex colors")
            elif visual_kind == 'face':
                print(f"[PreviewMeshVTKWithTexture] Mesh has face colors")

        # Generate unique filename - always use GLB for texture/material support
        filename = f"preview_vtk_texture_{uuid.uuid4().hex[:8]}.glb"

        # Use ComfyUI's output directory
        if COMFYUI_OUTPUT_FOLDER:
            filepath = os.path.join(COMFYUI_OUTPUT_FOLDER, filename)
        else:
            filepath = os.path.join(tempfile.gettempdir(), filename)

        # Export to GLB (preserves textures, materials, UVs, colors)
        try:
            trimesh.export(filepath, file_type='glb', include_normals=True)
            print(f"[PreviewMeshVTKWithTexture] Exported GLB to: {filepath}")
        except Exception as e:
            print(f"[PreviewMeshVTKWithTexture] GLB export failed: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to OBJ (loses textures but keeps geometry)
            filename = filename.replace('.glb', '.obj')
            filepath = filepath.replace('.glb', '.obj')
            trimesh.export(filepath, file_type='obj')
            print(f"[PreviewMeshVTKWithTexture] Exported to OBJ fallback: {filepath}")

        # Calculate bounding box info for camera setup
        bounds = trimesh.bounds
        extents = trimesh.extents
        max_extent = max(extents)

        # Check if mesh is watertight
        is_watertight = trimesh.is_watertight

        # Calculate volume and area
        volume = None
        area = None
        try:
            if is_watertight:
                volume = float(trimesh.volume)
            area = float(trimesh.area)
        except Exception as e:
            print(f"[PreviewMeshVTKWithTexture] Could not calculate volume/area: {e}")

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
            "has_texture": [has_texture],
            "has_vertex_colors": [has_vertex_colors],
            "has_material": [has_material],
            "visual_kind": [visual_kind if visual_kind else "none"],
        }

        # Add optional fields if available
        if volume is not None:
            ui_data["volume"] = [volume]
        if area is not None:
            ui_data["area"] = [area]

        print(f"[PreviewMeshVTKWithTexture] Mesh info: watertight={is_watertight}, texture={has_texture}, vertex_colors={has_vertex_colors}")

        return {"ui": ui_data}


NODE_CLASS_MAPPINGS = {
    "GeomPackPreviewMeshVTKWithTexture": PreviewMeshVTKWithTextureNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackPreviewMeshVTKWithTexture": "Preview Mesh (VTK with Texture)",
}
