"""
GeometryPack PreStartup Script
Copies example 3D assets and workflows to ComfyUI folders on startup.
"""
import os
import shutil

def copy_example_assets():
    """Copy all files and folders from assets/ directory to ComfyUI input/3d directory."""
    try:
        import folder_paths
        
        input_folder = folder_paths.get_input_directory()
        custom_node_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create input/3d subdirectory
        input_3d_folder = os.path.join(input_folder, "3d")
        os.makedirs(input_3d_folder, exist_ok=True)
        
        # Copy entire assets/ folder structure
        assets_folder = os.path.join(custom_node_dir, "assets")
        if not os.path.exists(assets_folder):
            print(f"[GeometryPack] Warning: assets folder not found at {assets_folder}")
            return
        
        copied_count = 0
        for root, dirs, files in os.walk(assets_folder):
            # Calculate relative path from assets folder
            rel_path = os.path.relpath(root, assets_folder)
            
            # Create corresponding subdirectory in destination
            if rel_path != '.':
                dest_dir = os.path.join(input_3d_folder, rel_path)
                os.makedirs(dest_dir, exist_ok=True)
            else:
                dest_dir = input_3d_folder
            
            # Copy files
            for file in files:
                source_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, file)
                
                if not os.path.exists(dest_file):
                    shutil.copy2(source_file, dest_file)
                    copied_count += 1
                    # Show relative path for clarity
                    rel_dest = os.path.join(rel_path, file) if rel_path != '.' else file
                    print(f"[GeometryPack] Copied {rel_dest} to input/3d/")
        
        if copied_count > 0:
            print(f"[GeometryPack] [OK] Copied {copied_count} asset(s) to {input_3d_folder}")
        else:
            print(f"[GeometryPack] All assets already exist in {input_3d_folder}")
            
    except Exception as e:
        print(f"[GeometryPack] Error copying assets: {e}")

def copy_example_workflows():
    """Copy workflow files to ComfyUI user workflows directory with GeometryPack- prefix."""
    try:
        import folder_paths
        
        input_folder = folder_paths.get_input_directory()
        custom_node_dir = os.path.dirname(os.path.abspath(__file__))
        
        workflows_src = os.path.join(custom_node_dir, "workflows")
        if not os.path.exists(workflows_src):
            print(f"[GeometryPack] Warning: workflows folder not found at {workflows_src}")
            return
        
        # Get user workflows directory
        comfyui_root = os.path.dirname(input_folder)
        user_workflows_dir = os.path.join(comfyui_root, "user", "default", "workflows")
        os.makedirs(user_workflows_dir, exist_ok=True)
        
        # Copy each workflow with prefix
        copied_count = 0
        for workflow_file in os.listdir(workflows_src):
            if workflow_file.endswith('.json'):
                source_workflow = os.path.join(workflows_src, workflow_file)
                dest_workflow = os.path.join(user_workflows_dir, f"GeometryPack-{workflow_file}")
                
                if not os.path.exists(dest_workflow):
                    shutil.copy2(source_workflow, dest_workflow)
                    copied_count += 1
                    print(f"[GeometryPack] Copied workflow: GeometryPack-{workflow_file}")
        
        if copied_count > 0:
            print(f"[GeometryPack] [OK] Copied {copied_count} workflow(s) to {user_workflows_dir}")
        else:
            print(f"[GeometryPack] All workflows already exist in {user_workflows_dir}")
            
    except Exception as e:
        print(f"[GeometryPack] Error copying workflows: {e}")

# Run on import
copy_example_assets()
copy_example_workflows()