"""
Point to Mesh Distance Node - Compute distances from points to mesh surface
"""

import numpy as np


class PointToMeshDistanceNode:
    """
    Point to Mesh Distance - Compute distance from a point to nearest mesh surface.

    For each point in a point cloud, finds the closest point on the mesh surface
    and computes the distance. Returns both the distance values and statistics.
    Useful for proximity analysis and error measurements.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trimesh": ("TRIMESH",),
                "point_cloud": ("POINT_CLOUD",),
            },
            "optional": {
                "return_closest_points": (["true", "false"], {"default": "false"}),
            }
        }

    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "STRING")
    RETURN_NAMES = ("min_distance", "max_distance", "mean_distance", "info")
    FUNCTION = "compute_distance"
    CATEGORY = "geompack/distance"

    def compute_distance(self, trimesh, point_cloud, return_closest_points="false"):
        """
        Compute distances from points to mesh surface.

        Args:
            trimesh: Input trimesh.Trimesh object
            point_cloud: Point cloud dictionary with 'points' array
            return_closest_points: Whether to compute closest surface points

        Returns:
            tuple: (min_distance, max_distance, mean_distance, info_string)
        """
        # Extract points from point cloud
        if isinstance(point_cloud, dict):
            points = point_cloud['points']
        else:
            points = point_cloud

        print(f"[PointToMeshDistance] Computing distances for {len(points):,} points to mesh")
        print(f"[PointToMeshDistance] Mesh: {len(trimesh.vertices):,} vertices, {len(trimesh.faces):,} faces")

        # Use trimesh's proximity query to find closest points and distances
        closest_points, distances, triangle_ids = trimesh.nearest.on_surface(points)

        # Compute statistics
        min_dist = float(np.min(distances))
        max_dist = float(np.max(distances))
        mean_dist = float(np.mean(distances))
        median_dist = float(np.median(distances))
        std_dist = float(np.std(distances))

        # Find percentiles
        percentile_25 = float(np.percentile(distances, 25))
        percentile_75 = float(np.percentile(distances, 75))
        percentile_95 = float(np.percentile(distances, 95))

        # Count points within certain distance thresholds
        threshold_01 = np.sum(distances < 0.1)
        threshold_05 = np.sum(distances < 0.5)
        threshold_10 = np.sum(distances < 1.0)

        info = f"""Point to Mesh Distance Analysis:

Input:
  Point Cloud: {len(points):,} points
  Mesh: {len(trimesh.vertices):,} vertices, {len(trimesh.faces):,} faces

Distance Statistics:
  Minimum: {min_dist:.6f}
  Maximum: {max_dist:.6f}
  Mean: {mean_dist:.6f}
  Median: {median_dist:.6f}
  Std Dev: {std_dist:.6f}

Percentiles:
  25th: {percentile_25:.6f}
  75th: {percentile_75:.6f}
  95th: {percentile_95:.6f}

Distance Distribution:
  < 0.1: {threshold_01:,} points ({100.0 * threshold_01 / len(points):.1f}%)
  < 0.5: {threshold_05:,} points ({100.0 * threshold_05 / len(points):.1f}%)
  < 1.0: {threshold_10:,} points ({100.0 * threshold_10 / len(points):.1f}%)

Note: Distances are computed as Euclidean distance from each point
to the nearest point on the mesh surface.
"""

        print(f"[PointToMeshDistance] Min: {min_dist:.6f}, Max: {max_dist:.6f}, Mean: {mean_dist:.6f}")

        return (min_dist, max_dist, mean_dist, info)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "GeomPackPointToMeshDistance": PointToMeshDistanceNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackPointToMeshDistance": "Point to Mesh Distance",
}
