"""Conversion module - mesh to point cloud and vice versa."""

from .mesh_to_pointcloud import NODE_CLASS_MAPPINGS as MESH_TO_PC_MAPPINGS
from .mesh_to_pointcloud import NODE_DISPLAY_NAME_MAPPINGS as MESH_TO_PC_DISPLAY
from .pointcloud_to_mesh import NODE_CLASS_MAPPINGS as PC_TO_MESH_MAPPINGS
from .pointcloud_to_mesh import NODE_DISPLAY_NAME_MAPPINGS as PC_TO_MESH_DISPLAY

# Also import from parent conversion.py for other nodes (StripMeshAdjacency, MeshToPointCloud)

# Combine all mappings
NODE_CLASS_MAPPINGS = {
    **MESH_TO_PC_MAPPINGS,
    **PC_TO_MESH_MAPPINGS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **MESH_TO_PC_DISPLAY,
    **PC_TO_MESH_DISPLAY,
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
