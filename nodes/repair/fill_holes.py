"""
Fill holes in mesh by adding new faces.
"""

import trimesh


class FillHolesNode:
    """
    Fill holes in mesh by adding new faces.

    Identifies boundary loops (holes) and fills them with new triangular faces.
    Useful for mesh repair, creating watertight meshes for 3D printing, or
    closing gaps in scanned geometry.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trimesh": ("TRIMESH",),
            },
        }

    RETURN_TYPES = ("TRIMESH", "STRING")
    RETURN_NAMES = ("filled_mesh", "info")
    FUNCTION = "fill_holes"
    CATEGORY = "geompack/repair"

    def fill_holes(self, trimesh):
        """
        Fill holes in the trimesh.

        Args:
            trimesh: Input trimesh.Trimesh object

        Returns:
            tuple: (filled_trimesh, info_string)
        """
        print(f"[FillHoles] Input: {len(trimesh.vertices)} vertices, {len(trimesh.faces)} faces")

        # Check initial state
        was_watertight = trimesh.is_watertight
        initial_vertices = len(trimesh.vertices)
        initial_faces = len(trimesh.faces)

        # Create a copy
        filled_mesh = trimesh.copy()

        # Fill holes
        filled_mesh.fill_holes()

        # Check result
        is_watertight = filled_mesh.is_watertight
        final_vertices = len(filled_mesh.vertices)
        final_faces = len(filled_mesh.faces)

        added_vertices = final_vertices - initial_vertices
        added_faces = final_faces - initial_faces

        info = f"""Hole Filling Results:

Initial State:
  Vertices: {initial_vertices:,}
  Faces: {initial_faces:,}
  Watertight: {'Yes' if was_watertight else 'No'}

After Filling:
  Vertices: {final_vertices:,} (+{added_vertices})
  Faces: {final_faces:,} (+{added_faces})
  Watertight: {'✓ Yes' if is_watertight else '⚠ No'}

{'✓ All holes successfully filled!' if is_watertight and added_faces > 0 else ''}
{'ℹ No holes detected - mesh was already watertight.' if was_watertight else ''}
{'⚠ Some holes may remain (check mesh topology).' if not is_watertight and added_faces > 0 else ''}
"""

        print(f"[FillHoles] Added {added_faces} faces, Watertight: {was_watertight} -> {is_watertight}")

        return (filled_mesh, info)


NODE_CLASS_MAPPINGS = {
    "GeomPackFillHoles": FillHolesNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackFillHoles": "Fill Holes",
}
