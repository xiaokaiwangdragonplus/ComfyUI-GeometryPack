"""
LSCM UV Parameterization using libigl.

Least Squares Conformal Maps - minimizes angle distortion.
Fast, conformal mapping suitable for texturing organic shapes.
No Blender dependency required.
"""

import numpy as np
import trimesh as trimesh_module


class LibiglLSCMNode:
    """
    LSCM UV Parameterization using libigl.

    Least Squares Conformal Maps - minimizes angle distortion.
    Fast, conformal mapping suitable for texturing organic shapes.
    No Blender dependency required.
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
        LSCM UV parameterization using libigl.

        Args:
            trimesh: Input trimesh_module.Trimesh object

        Returns:
            tuple: (unwrapped_trimesh_module.Trimesh,)
        """
        try:
            import igl
        except ImportError:
            raise ImportError("libigl not installed (should be in requirements.txt)")

        print(f"[LibiglLSCM] Input: {len(trimesh.vertices)} vertices, {len(trimesh.faces)} faces")

        # LSCM requires fixing 2 vertices for unique solution
        # Choose first and last vertex
        v_fixed = np.array([0, len(trimesh.vertices)-1], dtype=np.int32)
        uv_fixed = np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float64)

        # Compute LSCM parameterization
        # Convert TrackedArray to pure numpy array for igl compatibility
        uv_result = igl.lscm(
            np.asarray(trimesh.vertices, dtype=np.float64),
            np.asarray(trimesh.faces, dtype=np.int32),
            v_fixed,
            uv_fixed
        )
        # igl.lscm returns a tuple (uv_coords, sparse_matrix)
        uv = uv_result[0] if isinstance(uv_result, tuple) else uv_result

        # Normalize UVs to [0, 1] range
        uv_min = uv.min(axis=0)
        uv_max = uv.max(axis=0)
        uv_range = uv_max - uv_min

        # Avoid division by zero
        uv_range[uv_range < 1e-10] = 1.0

        uv_normalized = (uv - uv_min) / uv_range

        # Create unwrapped mesh (copy original)
        unwrapped = trimesh.copy()

        # Store UV coordinates in visual
        from trimesh.visual import TextureVisuals
        unwrapped.visual = TextureVisuals(uv=uv_normalized)

        # Add metadata
        unwrapped.metadata['uv_unwrap'] = {
            'algorithm': 'libigl_lscm',
            'conformal': True,
            'angle_preserving': True,
            'fixed_vertices': v_fixed.tolist()
        }

        print(f"[LibiglLSCM] Complete - conformal (angle-preserving) mapping")

        return (unwrapped,)


NODE_CLASS_MAPPINGS = {
    "GeomPackLibiglLSCM": LibiglLSCMNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackLibiglLSCM": "UV Unwrap (libigl LSCM)",
}
