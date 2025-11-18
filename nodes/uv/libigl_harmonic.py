"""
Harmonic UV Parameterization using libigl.

Simple, fast UV unwrapping using harmonic (Laplacian) mapping.
Guarantees valid (non-overlapping) UVs with fixed boundary.
Less feature-preserving than LSCM or ABF, but very stable.
"""

import numpy as np
import trimesh as trimesh_module


class LibiglHarmonicNode:
    """
    Harmonic UV Parameterization using libigl.

    Simple, fast UV unwrapping using harmonic (Laplacian) mapping.
    Guarantees valid (non-overlapping) UVs with fixed boundary.
    Less feature-preserving than LSCM or ABF, but very stable.
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
        Harmonic UV parameterization using libigl.

        Args:
            trimesh: Input trimesh_module.Trimesh object

        Returns:
            tuple: (unwrapped_trimesh_module.Trimesh,)
        """
        try:
            import igl
        except ImportError:
            raise ImportError("libigl not installed (should be in requirements.txt)")

        print(f"[LibiglHarmonic] Input: {len(trimesh.vertices)} vertices, {len(trimesh.faces)} faces")

        # Harmonic requires fixing boundary vertices
        # Find boundary loop
        # Convert TrackedArray to pure numpy array for igl compatibility
        boundary_loop = igl.boundary_loop(np.asarray(trimesh.faces, dtype=np.int32))

        if len(boundary_loop) == 0:
            raise ValueError("Mesh has no boundary - harmonic parameterization requires an open mesh")

        # Map boundary to circle/square
        # Simple circular boundary
        bnd_angles = np.linspace(0, 2 * np.pi, len(boundary_loop), endpoint=False)
        bnd_uv = np.column_stack([
            0.5 + 0.5 * np.cos(bnd_angles),
            0.5 + 0.5 * np.sin(bnd_angles)
        ])

        # Compute harmonic parameterization
        # Convert TrackedArray to pure numpy for igl compatibility
        uv = igl.harmonic(
            np.asarray(trimesh.vertices, dtype=np.float64),
            np.asarray(trimesh.faces, dtype=np.int32),
            boundary_loop.astype(np.int32),
            bnd_uv.astype(np.float64),
            1  # Laplacian type
        )

        # Create unwrapped mesh (copy original)
        unwrapped = trimesh.copy()

        # Store UV coordinates in visual
        from trimesh.visual import TextureVisuals
        unwrapped.visual = TextureVisuals(uv=uv)

        # Add metadata
        unwrapped.metadata['uv_unwrap'] = {
            'algorithm': 'libigl_harmonic',
            'boundary_vertices': len(boundary_loop),
            'guarantees_valid_uvs': True
        }

        print(f"[LibiglHarmonic] Complete - simple harmonic mapping with {len(boundary_loop)} boundary vertices")

        return (unwrapped,)


NODE_CLASS_MAPPINGS = {
    "GeomPackLibiglHarmonic": LibiglHarmonicNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackLibiglHarmonic": "UV Unwrap (libigl Harmonic)",
}
