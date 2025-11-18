"""Skeleton extraction and visualization module."""

from .extract_skeleton import NODE_CLASS_MAPPINGS as EXTRACT_MAPPINGS
from .extract_skeleton import NODE_DISPLAY_NAME_MAPPINGS as EXTRACT_DISPLAY
from .mesh_from_skeleton import NODE_CLASS_MAPPINGS as MESH_MAPPINGS
from .mesh_from_skeleton import NODE_DISPLAY_NAME_MAPPINGS as MESH_DISPLAY
from .visualize_skeleton import NODE_CLASS_MAPPINGS as VISUALIZE_MAPPINGS
from .visualize_skeleton import NODE_DISPLAY_NAME_MAPPINGS as VISUALIZE_DISPLAY

# Also import from parent skeleton.py for other nodes (ExtractSkeleton, SkeletonToTrimesh, SkeletonToMesh)

# Combine all mappings
NODE_CLASS_MAPPINGS = {
    **EXTRACT_MAPPINGS,
    **MESH_MAPPINGS,
    **VISUALIZE_MAPPINGS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **EXTRACT_DISPLAY,
    **MESH_DISPLAY,
    **VISUALIZE_DISPLAY,
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
