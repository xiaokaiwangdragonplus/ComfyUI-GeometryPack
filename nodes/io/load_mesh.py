"""
Load Mesh Node - Load a mesh from file (OBJ, PLY, STL, OFF, etc.)
"""

import os

# ComfyUI folder paths
try:
    import folder_paths
    COMFYUI_INPUT_FOLDER = folder_paths.get_input_directory()
except:
    # Fallback if folder_paths not available (e.g., during testing)
    COMFYUI_INPUT_FOLDER = None

from .._utils import mesh_ops


class LoadMesh:
    """
    Load a mesh from file (OBJ, PLY, STL, OFF, etc.)
    Now returns trimesh.Trimesh objects for better mesh handling.
    """

    # Supported mesh extensions for file browser
    SUPPORTED_EXTENSIONS = ['.obj', '.ply', '.stl', '.off', '.gltf', '.glb', '.fbx', '.dae', '.3ds', '.vtp']

    @classmethod
    def INPUT_TYPES(cls):
        # Get list of available mesh files (like LoadImage does)
        mesh_files = cls.get_mesh_files()

        # If no files found, provide a default empty list
        if not mesh_files:
            mesh_files = ["No mesh files found in input/3d or input folders"]

        return {
            "required": {
                "file_path": (mesh_files, ),
            },
        }

    RETURN_TYPES = ("TRIMESH",)
    RETURN_NAMES = ("mesh",)
    FUNCTION = "load_mesh"
    CATEGORY = "geompack/io"

    @classmethod
    def get_mesh_files(cls):
        """Get list of available mesh files in input/3d and input folders."""
        mesh_files = []

        if COMFYUI_INPUT_FOLDER is not None:
            # Scan input/3d first
            input_3d = os.path.join(COMFYUI_INPUT_FOLDER, "3d")
            if os.path.exists(input_3d):
                for file in os.listdir(input_3d):
                    if any(file.lower().endswith(ext) for ext in cls.SUPPORTED_EXTENSIONS):
                        mesh_files.append(f"3d/{file}")

            # Then scan input root
            for file in os.listdir(COMFYUI_INPUT_FOLDER):
                file_path = os.path.join(COMFYUI_INPUT_FOLDER, file)
                if os.path.isfile(file_path):
                    if any(file.lower().endswith(ext) for ext in cls.SUPPORTED_EXTENSIONS):
                        mesh_files.append(file)

        return sorted(mesh_files)

    @classmethod
    def IS_CHANGED(cls, file_path):
        """Force re-execution when file changes."""
        if COMFYUI_INPUT_FOLDER is not None:
            # Check file modification time
            full_path = None
            input_3d_path = os.path.join(COMFYUI_INPUT_FOLDER, "3d", file_path)
            input_path = os.path.join(COMFYUI_INPUT_FOLDER, file_path)

            if os.path.exists(input_3d_path):
                full_path = input_3d_path
            elif os.path.exists(input_path):
                full_path = input_path

            if full_path and os.path.exists(full_path):
                return os.path.getmtime(full_path)

        return file_path

    def load_mesh(self, file_path):
        """
        Load mesh from file.

        Looks for files in ComfyUI's input/3d folder first, then input folder, then tries absolute path.

        Args:
            file_path: Path to mesh file (relative to input folder or absolute)

        Returns:
            tuple: (trimesh.Trimesh,)
        """
        if not file_path or file_path.strip() == "":
            raise ValueError("File path cannot be empty")

        # Try to find the file
        full_path = None
        searched_paths = []

        if COMFYUI_INPUT_FOLDER is not None:
            # First, try in ComfyUI input/3d folder
            input_3d_path = os.path.join(COMFYUI_INPUT_FOLDER, "3d", file_path)
            searched_paths.append(input_3d_path)
            if os.path.exists(input_3d_path):
                full_path = input_3d_path
                print(f"[LoadMesh] Found mesh in input/3d folder: {file_path}")

            # Second, try in ComfyUI input folder (for backward compatibility)
            if full_path is None:
                input_path = os.path.join(COMFYUI_INPUT_FOLDER, file_path)
                searched_paths.append(input_path)
                if os.path.exists(input_path):
                    full_path = input_path
                    print(f"[LoadMesh] Found mesh in input folder: {file_path}")

        # If not found in input folders, try as absolute path
        if full_path is None:
            searched_paths.append(file_path)
            if os.path.exists(file_path):
                full_path = file_path
                print(f"[LoadMesh] Loading from absolute path: {file_path}")
            else:
                # Generate error message with all searched paths
                error_msg = f"File not found: '{file_path}'\nSearched in:"
                for path in searched_paths:
                    error_msg += f"\n  - {path}"
                raise ValueError(error_msg)

        # Load the mesh
        loaded_mesh, error = mesh_ops.load_mesh_file(full_path)

        if loaded_mesh is None:
            raise ValueError(f"Failed to load mesh: {error}")

        print(f"[LoadMesh] Loaded: {len(loaded_mesh.vertices)} vertices, {len(loaded_mesh.faces)} faces")

        return (loaded_mesh,)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "GeomPackLoadMesh": LoadMesh,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackLoadMesh": "Load Mesh",
}
