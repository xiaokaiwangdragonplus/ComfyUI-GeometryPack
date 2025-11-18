"""
Remeshing - Mesh topology modification and refinement operations
"""

from .remesh import RemeshNode
from .refine import RefineMeshNode

__all__ = [
    'RemeshNode',
    'RefineMeshNode',
]

NODE_CLASS_MAPPINGS = {
    "GeomPackRemesh": RemeshNode,
    "GeomPackRefineMesh": RefineMeshNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackRemesh": "Remesh",
    "GeomPackRefineMesh": "Refine Mesh",
}
