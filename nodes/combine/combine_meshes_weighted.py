"""
Combine Meshes Weighted Node - Combine meshes with weighted blending
"""

import numpy as np
import trimesh as trimesh_module


class CombineMeshesWeightedNode:
    """
    Combine Meshes (Weighted) - Blend multiple meshes with individual weights.

    Combines up to 4 meshes, scaling each by a weight factor before concatenation.
    This allows for creating weighted compositions where certain meshes can be
    scaled or emphasized relative to others.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mesh_a": ("TRIMESH",),
                "weight_a": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}),
            },
            "optional": {
                "mesh_b": ("TRIMESH",),
                "weight_b": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "mesh_c": ("TRIMESH",),
                "weight_c": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "mesh_d": ("TRIMESH",),
                "weight_d": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("TRIMESH", "STRING")
    RETURN_NAMES = ("combined_mesh", "info")
    FUNCTION = "combine_weighted"
    CATEGORY = "geompack/combine"

    def combine_weighted(self, mesh_a, weight_a,
                        mesh_b=None, weight_b=1.0,
                        mesh_c=None, weight_c=1.0,
                        mesh_d=None, weight_d=1.0):
        """
        Combine multiple meshes with weighted scaling.

        Args:
            mesh_a: First mesh (required)
            weight_a: Weight for mesh_a
            mesh_b, mesh_c, mesh_d: Optional additional meshes
            weight_b, weight_c, weight_d: Weights for optional meshes

        Returns:
            tuple: (combined_mesh, info_string)
        """
        meshes = []
        weights = []
        mesh_info = []

        # Collect meshes and weights
        if mesh_a is not None:
            meshes.append(mesh_a)
            weights.append(weight_a)
            mesh_info.append(('A', len(mesh_a.vertices), len(mesh_a.faces), weight_a))

        if mesh_b is not None:
            meshes.append(mesh_b)
            weights.append(weight_b)
            mesh_info.append(('B', len(mesh_b.vertices), len(mesh_b.faces), weight_b))

        if mesh_c is not None:
            meshes.append(mesh_c)
            weights.append(weight_c)
            mesh_info.append(('C', len(mesh_c.vertices), len(mesh_c.faces), weight_c))

        if mesh_d is not None:
            meshes.append(mesh_d)
            weights.append(weight_d)
            mesh_info.append(('D', len(mesh_d.vertices), len(mesh_d.faces), weight_d))

        print(f"[CombineMeshesWeighted] Combining {len(meshes)} meshes with weights")

        # Apply weights by scaling meshes
        scaled_meshes = []
        for mesh, weight, info in zip(meshes, weights, mesh_info):
            if weight != 1.0:
                # Scale mesh by weight
                scaled_mesh = mesh.copy()
                scaled_mesh.apply_scale(weight)
                scaled_meshes.append(scaled_mesh)
                print(f"[CombineMeshesWeighted] Mesh {info[0]}: scaled by {weight}")
            else:
                scaled_meshes.append(mesh)
                print(f"[CombineMeshesWeighted] Mesh {info[0]}: no scaling (weight=1.0)")

        # Concatenate scaled meshes
        if len(scaled_meshes) == 1:
            result = scaled_meshes[0].copy()
        else:
            result = trimesh_module.util.concatenate(scaled_meshes)

        # Preserve metadata from first mesh
        result.metadata = mesh_a.metadata.copy()
        result.metadata['combined_weighted'] = {
            'num_meshes': len(meshes),
            'weights': weights,
            'mesh_info': mesh_info,
            'total_vertices': len(result.vertices),
            'total_faces': len(result.faces)
        }

        # Build info string
        mesh_lines = []
        for name, verts, faces, weight in mesh_info:
            mesh_lines.append(f"  Mesh {name}: {verts:,} vertices, {faces:,} faces, weight={weight}")

        info = f"""Combine Meshes (Weighted) Results:

Number of Meshes Combined: {len(meshes)}

Input Meshes:
{chr(10).join(mesh_lines)}

Combined Result:
  Total Vertices: {len(result.vertices):,}
  Total Faces: {len(result.faces):,}
  Connected Components: {len(trimesh_module.graph.connected_components(result.face_adjacency)[1])}

Note: Each mesh was scaled by its weight before combining.
Weights affect the size/scale of each mesh component.
"""

        print(f"[CombineMeshesWeighted] Result: {len(result.vertices)} vertices, {len(result.faces)} faces")
        return (result, info)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "GeomPackCombineMeshesWeighted": CombineMeshesWeightedNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackCombineMeshesWeighted": "Combine Meshes (Weighted)",
}
