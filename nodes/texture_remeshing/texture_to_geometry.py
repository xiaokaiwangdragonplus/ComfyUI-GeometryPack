"""
Texture to Geometry Node - Convert texture heightmap to 3D geometry
"""

import numpy as np
import trimesh


class TextureToGeometryNode:
    """
    Texture to Geometry - Convert a heightmap texture to 3D mesh geometry.

    Takes an IMAGE (heightmap) and converts it to a displacement-mapped mesh.
    The brightness of each pixel determines the height/displacement of the
    corresponding vertex. Useful for creating terrain, embossed surfaces, or
    converting 2D textures to 3D relief.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "height_scale": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "number"
                }),
                "base_resolution": ("INT", {
                    "default": 128,
                    "min": 16,
                    "max": 512,
                    "step": 16,
                    "tooltip": "Resolution of the base mesh (width/height in vertices)"
                }),
            },
            "optional": {
                "invert_height": (["false", "true"], {"default": "false"}),
                "smooth_normals": (["true", "false"], {"default": "true"}),
            }
        }

    RETURN_TYPES = ("TRIMESH", "STRING")
    RETURN_NAMES = ("mesh", "info")
    FUNCTION = "texture_to_geometry"
    CATEGORY = "geompack/texture_remeshing"

    def texture_to_geometry(self, image, height_scale, base_resolution,
                           invert_height="false", smooth_normals="true"):
        """
        Convert heightmap image to 3D mesh.

        Args:
            image: Input IMAGE tensor (B, H, W, C) from ComfyUI
            height_scale: Scale factor for height displacement
            base_resolution: Resolution of base mesh grid
            invert_height: Invert the heightmap (dark=high, light=low)
            smooth_normals: Compute smooth vertex normals

        Returns:
            tuple: (mesh, info_string)
        """
        try:
            import torch
            from PIL import Image
        except ImportError:
            raise RuntimeError("torch and PIL required. Install with: pip install torch Pillow")

        print(f"[TextureToGeometry] Converting texture to geometry")

        # Extract image from ComfyUI tensor format (B, H, W, C)
        if isinstance(image, torch.Tensor):
            # Get first image in batch
            img_array = image[0].cpu().numpy()
        else:
            img_array = np.array(image)

        # Convert to grayscale for heightmap
        if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
            # RGB to grayscale using standard weights
            heightmap = 0.299 * img_array[:, :, 0] + 0.587 * img_array[:, :, 1] + 0.114 * img_array[:, :, 2]
        else:
            heightmap = img_array[:, :, 0]

        print(f"[TextureToGeometry] Heightmap size: {heightmap.shape}, range: [{heightmap.min():.3f}, {heightmap.max():.3f}]")

        # Resize heightmap to base resolution
        heightmap_pil = Image.fromarray((heightmap * 255).astype(np.uint8))
        heightmap_pil = heightmap_pil.resize((base_resolution, base_resolution), Image.Resampling.LANCZOS)
        heightmap = np.array(heightmap_pil).astype(np.float32) / 255.0

        # Invert if requested
        if invert_height == "true":
            heightmap = 1.0 - heightmap

        # Create grid mesh
        width, height = base_resolution, base_resolution

        # Generate vertices
        vertices = []
        for y in range(height):
            for x in range(width):
                # Normalize x, y to [-1, 1]
                nx = (x / (width - 1)) * 2.0 - 1.0
                ny = (y / (height - 1)) * 2.0 - 1.0

                # Get height from heightmap
                h = heightmap[y, x] * height_scale

                vertices.append([nx, ny, h])

        vertices = np.array(vertices, dtype=np.float32)

        # Generate faces (triangles)
        faces = []
        for y in range(height - 1):
            for x in range(width - 1):
                # Current vertex index
                i = y * width + x

                # Create two triangles per quad
                # Triangle 1: (i, i+1, i+width)
                faces.append([i, i + 1, i + width])
                # Triangle 2: (i+1, i+width+1, i+width)
                faces.append([i + 1, i + width + 1, i + width])

        faces = np.array(faces, dtype=np.int32)

        # Create trimesh
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

        # Compute normals
        if smooth_normals == "true":
            mesh.fix_normals()

        print(f"[TextureToGeometry] Created mesh: {len(vertices)} vertices, {len(faces)} faces")

        # Compute statistics
        height_min = vertices[:, 2].min()
        height_max = vertices[:, 2].max()
        height_range = height_max - height_min

        info = f"""Texture to Geometry Results:

Input:
  Heightmap Size: {img_array.shape[0]}x{img_array.shape[1]}
  Base Resolution: {base_resolution}x{base_resolution}
  Height Scale: {height_scale}
  Inverted: {invert_height}

Output Mesh:
  Vertices: {len(vertices):,}
  Faces: {len(faces):,}
  Height Range: [{height_min:.3f}, {height_max:.3f}] (span: {height_range:.3f})
  Bounds: {mesh.bounds.tolist()}

Note: Heightmap brightness controls vertex displacement in Z-axis.
"""

        return (mesh, info)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "GeomPackTextureToGeometry": TextureToGeometryNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackTextureToGeometry": "Texture to Geometry",
}
