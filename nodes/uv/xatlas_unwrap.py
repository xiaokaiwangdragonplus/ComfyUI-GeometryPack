"""
UV Unwrap mesh using xatlas library.

Fast, automatic UV unwrapping optimized for lightmaps and texture atlasing.
No Blender dependency required. Uses the same algorithm as Blender 3.6+
for UV packing.
"""

import numpy as np
import trimesh as trimesh_module


class XAtlasUVUnwrapNode:
    """
    UV Unwrap mesh using xatlas library.

    Fast, automatic UV unwrapping optimized for lightmaps and texture atlasing.
    No Blender dependency required. Uses the same algorithm as Blender 3.6+
    for UV packing.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trimesh": ("TRIMESH",),
            },
        }

    RETURN_TYPES = ("TRIMESH",)
    RETURN_NAMES = ("unwrapped_mesh",)
    FUNCTION = "uv_unwrap"
    CATEGORY = "geompack/uv"

    def uv_unwrap(self, trimesh):
        """
        UV unwrap mesh using xatlas.

        Args:
            trimesh: Input trimesh_module.Trimesh object

        Returns:
            tuple: (unwrapped_trimesh_module.Trimesh,)
        """
        try:
            import xatlas
        except ImportError:
            raise ImportError(
                "xatlas not installed. Install with: pip install xatlas\n"
                "This is required for fast UV unwrapping without Blender."
            )

        print(f"[XAtlasUVUnwrap] Input: {len(trimesh.vertices)} vertices, {len(trimesh.faces)} faces")

        # Parametrize with xatlas
        vmapping, indices, uvs = xatlas.parametrize(
            trimesh.vertices,
            trimesh.faces
        )

        # Create new mesh with UV-split vertices
        new_vertices = trimesh.vertices[vmapping]

        # Create trimesh with UV coordinates
        unwrapped = trimesh_module.Trimesh(
            vertices=new_vertices,
            faces=indices,
            process=False
        )

        # Store UV coordinates in visual
        from trimesh.visual import TextureVisuals
        unwrapped.visual = TextureVisuals(uv=uvs)

        # Preserve metadata
        unwrapped.metadata = trimesh.metadata.copy()
        unwrapped.metadata['uv_unwrap'] = {
            'algorithm': 'xatlas',
            'original_vertices': len(trimesh.vertices),
            'unwrapped_vertices': len(new_vertices),
            'vertex_duplication_ratio': len(new_vertices) / len(trimesh.vertices)
        }

        print(f"[XAtlasUVUnwrap] Output: {len(unwrapped.vertices)} vertices, {len(unwrapped.faces)} faces")
        print(f"[XAtlasUVUnwrap] Vertex duplication: {len(new_vertices)/len(trimesh.vertices):.2f}x")

        return (unwrapped,)


NODE_CLASS_MAPPINGS = {
    "GeomPackXAtlasUVUnwrap": XAtlasUVUnwrapNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackXAtlasUVUnwrap": "UV Unwrap (XAtlas)",
}
