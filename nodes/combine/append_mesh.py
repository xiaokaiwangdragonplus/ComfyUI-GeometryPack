"""
Append Mesh Node - Append one mesh to another
"""

import numpy as np
import trimesh as trimesh_module


class AppendMeshNode:
    """
    Append Mesh - Add a secondary mesh to a primary mesh.

    Appends mesh_b to mesh_a, preserving the order. Unlike combine which accepts
    multiple optional inputs, this takes two required inputs and always appends
    in a specific order (mesh_a first, then mesh_b).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mesh_a": ("TRIMESH",),
                "mesh_b": ("TRIMESH",),
            }
        }

    RETURN_TYPES = ("TRIMESH", "STRING")
    RETURN_NAMES = ("appended_mesh", "info")
    FUNCTION = "append"
    CATEGORY = "geompack/combine"

    def append(self, mesh_a, mesh_b):
        """
        Append mesh_b to mesh_a.

        Args:
            mesh_a: Primary mesh
            mesh_b: Mesh to append

        Returns:
            tuple: (appended_mesh, info_string)
        """
        print(f"[AppendMesh] Appending meshes")
        print(f"[AppendMesh] Mesh A: {len(mesh_a.vertices)} vertices, {len(mesh_a.faces)} faces")
        print(f"[AppendMesh] Mesh B: {len(mesh_b.vertices)} vertices, {len(mesh_b.faces)} faces")

        # Concatenate the meshes
        result = trimesh_module.util.concatenate([mesh_a, mesh_b])

        # Preserve metadata from first mesh
        result.metadata = mesh_a.metadata.copy()
        result.metadata['appended'] = {
            'mesh_a_vertices': len(mesh_a.vertices),
            'mesh_a_faces': len(mesh_a.faces),
            'mesh_b_vertices': len(mesh_b.vertices),
            'mesh_b_faces': len(mesh_b.faces),
            'total_vertices': len(result.vertices),
            'total_faces': len(result.faces)
        }

        # Build info string
        info = f"""Append Mesh Results:

Mesh A:
  Vertices: {len(mesh_a.vertices):,}
  Faces: {len(mesh_a.faces):,}

Mesh B:
  Vertices: {len(mesh_b.vertices):,}
  Faces: {len(mesh_b.faces):,}

Appended Result:
  Total Vertices: {len(result.vertices):,}
  Total Faces: {len(result.faces):,}
  Connected Components: {len(trimesh_module.graph.connected_components(result.face_adjacency)[1])}

Note: Mesh B is appended to Mesh A.
Components remain separate within the combined mesh.
"""

        print(f"[AppendMesh] Result: {len(result.vertices)} vertices, {len(result.faces)} faces")
        return (result, info)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "GeomPackAppendMesh": AppendMeshNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackAppendMesh": "Append Mesh",
}
