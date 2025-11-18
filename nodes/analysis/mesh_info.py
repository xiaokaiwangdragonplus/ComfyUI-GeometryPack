"""
Mesh Info Node - Display detailed mesh information
"""

from .._utils import mesh_ops


class MeshInfoNode:
    """
    Display detailed mesh information and statistics.
    Now using trimesh for enhanced mesh analysis.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trimesh": ("TRIMESH",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("info",)
    FUNCTION = "get_mesh_info"
    CATEGORY = "geompack/analysis"

    def get_mesh_info(self, trimesh):
        """
        Get information about the trimesh.

        Args:
            trimesh: trimesh.Trimesh object

        Returns:
            tuple: (info_string,)
        """
        info = mesh_ops.compute_mesh_info(trimesh)
        return (info,)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "GeomPackMeshInfo": MeshInfoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackMeshInfo": "Mesh Info",
}
