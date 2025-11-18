"""
Fix inconsistent normal orientations.
"""

import trimesh


class FixNormalsNode:
    """
    Fix inconsistent normal orientations.

    Ensures all face normals point consistently (all outward or all inward).
    Uses graph traversal to propagate consistent orientation across the trimesh.
    Essential for proper rendering and boolean operations.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trimesh": ("TRIMESH",),
            },
        }

    RETURN_TYPES = ("TRIMESH", "STRING")
    RETURN_NAMES = ("fixed_mesh", "info")
    FUNCTION = "fix_normals"
    CATEGORY = "geompack/repair"

    def fix_normals(self, trimesh):
        """
        Fix inconsistent face normal orientations.

        Args:
            trimesh: Input trimesh.Trimesh object

        Returns:
            tuple: (fixed_trimesh, info_string)
        """
        print(f"[FixNormals] Input: {len(trimesh.vertices)} vertices, {len(trimesh.faces)} faces")

        # Create a copy to avoid modifying the original
        fixed_mesh = trimesh.copy()

        # Check initial winding consistency
        was_consistent = fixed_mesh.is_winding_consistent

        # Fix normals - this reorients faces for consistent winding
        fixed_mesh.fix_normals()

        # Check if it's now consistent
        is_consistent = fixed_mesh.is_winding_consistent

        info = f"""Normal Orientation Fix:

Before: {'Consistent' if was_consistent else 'Inconsistent'}
After:  {'Consistent' if is_consistent else 'Inconsistent'}

Vertices: {len(fixed_mesh.vertices):,}
Faces: {len(fixed_mesh.faces):,}

{'✓ Normals are now consistently oriented!' if is_consistent else '⚠ Some inconsistencies may remain (check mesh topology)'}
"""

        print(f"[FixNormals] {'✓' if is_consistent else '⚠'} Normal orientation: {was_consistent} -> {is_consistent}")

        return (fixed_mesh, info)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "GeomPackFixNormals": FixNormalsNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackFixNormals": "Fix Normals",
}
