"""Combine/split operations module."""

from .combine_meshes import NODE_CLASS_MAPPINGS as COMBINE_MAPPINGS
from .combine_meshes import NODE_DISPLAY_NAME_MAPPINGS as COMBINE_DISPLAY
from .append_mesh import NODE_CLASS_MAPPINGS as APPEND_MAPPINGS
from .append_mesh import NODE_DISPLAY_NAME_MAPPINGS as APPEND_DISPLAY
from .combine_meshes_weighted import NODE_CLASS_MAPPINGS as WEIGHTED_MAPPINGS
from .combine_meshes_weighted import NODE_DISPLAY_NAME_MAPPINGS as WEIGHTED_DISPLAY

# Also import from parent combine.py for other nodes (SplitComponents, FilterComponents)

# Combine all mappings
NODE_CLASS_MAPPINGS = {
    **COMBINE_MAPPINGS,
    **APPEND_MAPPINGS,
    **WEIGHTED_MAPPINGS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **COMBINE_DISPLAY,
    **APPEND_DISPLAY,
    **WEIGHTED_DISPLAY,
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
