"""
Visualize Skeleton Node - Create visual representation of skeleton data
"""

import numpy as np
import trimesh


class VisualizeSkeletonNode:
    """
    Visualize Skeleton - Create a colored mesh visualization of skeleton structure.

    Converts skeleton data (vertices and edges) into a solid mesh with colored
    joints and bones for better visualization. Each bone can be colored based
    on various metrics like length, depth, or a custom scheme.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "skeleton": ("SKELETON",),
                "visualization_mode": (["simple", "colored_by_depth", "colored_by_length"], {
                    "default": "simple"
                }),
            },
            "optional": {
                "joint_radius": ("FLOAT", {"default": 0.02, "min": 0.001, "max": 0.1, "step": 0.001}),
                "bone_radius": ("FLOAT", {"default": 0.01, "min": 0.001, "max": 0.05, "step": 0.001}),
            }
        }

    RETURN_TYPES = ("TRIMESH", "STRING")
    RETURN_NAMES = ("visualization_mesh", "info")
    FUNCTION = "visualize"
    CATEGORY = "geompack/skeleton"

    def visualize(self, skeleton, visualization_mode, joint_radius=0.02, bone_radius=0.01):
        """
        Create colored visualization mesh from skeleton.

        Args:
            skeleton: Skeleton dictionary with 'vertices' and 'edges'
            visualization_mode: Coloring scheme for visualization
            joint_radius: Radius for joint spheres
            bone_radius: Radius for bone cylinders

        Returns:
            tuple: (visualization_mesh, info_string)
        """
        vertices = skeleton["vertices"]
        edges = skeleton["edges"]

        print(f"[VisualizeSkeleton] Creating visualization: {len(vertices)} joints, {len(edges)} bones")
        print(f"[VisualizeSkeleton] Mode: {visualization_mode}")

        meshes = []
        vertex_colors = []

        # Compute coloring based on mode
        if visualization_mode == "colored_by_depth":
            # Compute graph depth from root (assume vertex 0 is root)
            depths = self._compute_depths(vertices, edges)
            max_depth = max(depths) if depths else 1
            # Color map: blue (low depth) to red (high depth)
            joint_colors = [self._depth_to_color(d / max_depth) for d in depths]
        elif visualization_mode == "colored_by_length":
            # Color bones by their length
            bone_lengths = []
            for edge in edges:
                start = vertices[edge[0]]
                end = vertices[edge[1]]
                length = np.linalg.norm(end - start)
                bone_lengths.append(length)
            max_length = max(bone_lengths) if bone_lengths else 1
            # Use same color for all joints, color bones by length
            joint_colors = [(0.7, 0.7, 0.7, 1.0)] * len(vertices)
        else:  # simple
            # Single color for all
            joint_colors = [(0.8, 0.3, 0.3, 1.0)] * len(vertices)

        # Create joint spheres
        for i, (vertex, color) in enumerate(zip(vertices, joint_colors)):
            sphere = trimesh.creation.uv_sphere(radius=joint_radius, count=[8, 8])
            sphere.apply_translation(vertex)
            # Apply color
            sphere.visual.vertex_colors = np.array([color] * len(sphere.vertices))
            meshes.append(sphere)

        # Create bone cylinders
        for idx, edge in enumerate(edges):
            start = vertices[edge[0]]
            end = vertices[edge[1]]

            # Calculate cylinder parameters
            direction = end - start
            length = np.linalg.norm(direction)

            if length < 1e-6:
                continue  # Skip degenerate bones

            # Create cylinder along Z-axis
            cylinder = trimesh.creation.cylinder(
                radius=bone_radius,
                height=length,
                sections=8
            )

            # Calculate rotation to align with bone direction
            z_axis = np.array([0, 0, 1])
            bone_direction = direction / length

            # Rotation axis and angle
            rotation_axis = np.cross(z_axis, bone_direction)
            rotation_axis_norm = np.linalg.norm(rotation_axis)

            if rotation_axis_norm > 1e-6:
                rotation_axis = rotation_axis / rotation_axis_norm
                rotation_angle = np.arccos(np.clip(np.dot(z_axis, bone_direction), -1.0, 1.0))

                # Create rotation matrix
                from trimesh.transformations import rotation_matrix
                rotation = rotation_matrix(rotation_angle, rotation_axis)
                cylinder.apply_transform(rotation)

            # Translate to midpoint
            midpoint = (start + end) / 2
            cylinder.apply_translation(midpoint)

            # Color bone
            if visualization_mode == "colored_by_length":
                bone_color = self._length_to_color(bone_lengths[idx] / max_length)
            elif visualization_mode == "colored_by_depth":
                # Use average depth of endpoints
                avg_depth = (depths[edge[0]] + depths[edge[1]]) / 2
                bone_color = self._depth_to_color(avg_depth / max_depth)
            else:
                bone_color = (0.5, 0.5, 0.8, 1.0)

            cylinder.visual.vertex_colors = np.array([bone_color] * len(cylinder.vertices))
            meshes.append(cylinder)

        # Combine all meshes
        if not meshes:
            raise ValueError("No geometry created from skeleton")

        combined_mesh = trimesh.util.concatenate(meshes)

        info = f"""Skeleton Visualization:

Skeleton Structure:
  Joints: {len(vertices)}
  Bones: {len(edges)}

Visualization:
  Mode: {visualization_mode}
  Joint Radius: {joint_radius}
  Bone Radius: {bone_radius}

Output Mesh:
  Vertices: {len(combined_mesh.vertices):,}
  Faces: {len(combined_mesh.faces):,}
  Colored: Yes

Note: Colored visualization helps identify skeleton structure.
"""

        print(f"[VisualizeSkeleton] Created visualization: {len(combined_mesh.vertices)} vertices, "
              f"{len(combined_mesh.faces)} faces")

        return (combined_mesh, info)

    def _compute_depths(self, vertices, edges):
        """Compute graph depth from root (BFS)"""
        from collections import deque

        depths = [0] * len(vertices)
        visited = [False] * len(vertices)

        # Build adjacency list
        adj = [[] for _ in range(len(vertices))]
        for edge in edges:
            adj[edge[0]].append(edge[1])
            adj[edge[1]].append(edge[0])

        # BFS from root (vertex 0)
        queue = deque([0])
        visited[0] = True
        depths[0] = 0

        while queue:
            v = queue.popleft()
            for neighbor in adj[v]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    depths[neighbor] = depths[v] + 1
                    queue.append(neighbor)

        return depths

    def _depth_to_color(self, t):
        """Map depth (0-1) to color: blue -> cyan -> green -> yellow -> red"""
        if t < 0.25:
            # Blue to cyan
            s = t / 0.25
            return (0.0, s, 1.0, 1.0)
        elif t < 0.5:
            # Cyan to green
            s = (t - 0.25) / 0.25
            return (0.0, 1.0, 1.0 - s, 1.0)
        elif t < 0.75:
            # Green to yellow
            s = (t - 0.5) / 0.25
            return (s, 1.0, 0.0, 1.0)
        else:
            # Yellow to red
            s = (t - 0.75) / 0.25
            return (1.0, 1.0 - s, 0.0, 1.0)

    def _length_to_color(self, t):
        """Map length (0-1) to color: green -> yellow -> red"""
        if t < 0.5:
            # Green to yellow
            s = t / 0.5
            return (s, 1.0, 0.0, 1.0)
        else:
            # Yellow to red
            s = (t - 0.5) / 0.5
            return (1.0, 1.0 - s, 0.0, 1.0)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "GeomPackVisualizeSkeleton": VisualizeSkeletonNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackVisualizeSkeleton": "Visualize Skeleton",
}
