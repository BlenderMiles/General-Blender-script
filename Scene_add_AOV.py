# This script adds AOVs (Arbitrary Output Variables) to the active view layer
# based on the AOV Output nodes found in the materials of mesh objects in the scene.    

import bpy


def add_aovs_from_materials():
    # Get the current scene and active view layer
    scene = bpy.context.scene
    view_layer = bpy.context.view_layer
    
    # Enable compositing
    scene.use_nodes = True
    
    # Enable combined pass for RGB output
    view_layer.use_pass_combined = True
    
    # Set to store unique AOV names from materials
    aov_names = set()
    
    # Iterate through all mesh objects in the scene
    for obj in scene.objects:
        if obj.type == 'MESH' and obj.material_slots:
            # Check each material slot
            for slot in obj.material_slots:
                material = slot.material
                if material and material.use_nodes and material.node_tree:
                    # Search for AOV Output nodes in the material's node tree
                    for node in material.node_tree.nodes:
                        if node.type == 'OUTPUT_AOV':
                            # Use aov_name if available, else fall back to node name
                            aov_name = getattr(node, 'aov_name', node.name) if hasattr(node, 'aov_name') else node.name
                            if aov_name and aov_name not in aov_names:
                                aov_names.add(aov_name)
                                print(f"Found AOV '{aov_name}' in material '{material.name}' on object '{obj.name}'")
    
    # If no AOVs found, notify user
    if not aov_names:
        print("No AOV Output nodes found in materials attached to mesh objects.")
        return False
    
    # Add AOVs to the active view layer
    for aov_name in aov_names:
        # Check if AOV already exists
        if aov_name not in [aov.name for aov in view_layer.aovs]:
            aov = view_layer.aovs.add()
            aov.name = aov_name
            aov.type = 'COLOR'  # Default to VALUE; change to 'COLOR' if needed
            print(f"Added AOV '{aov_name}' to View Layer '{view_layer.name}'")
        else:
            print(f"AOV '{aov_name}' already exists in View Layer '{view_layer.name}'")
    
    # Verify AOVs in the view layer
    print("\nCurrent AOVs in View Layer:")
    for aov in view_layer.aovs:
        print(f"- {aov.name} (Type: {aov.type})")
    
    return True

# Execute the function and provide feedback
success = add_aovs_from_materials()
if success:
    print("AOVs and compositing nodes set up successfully!")
else:
    print("No AOVs were added. Check materials for AOV Output nodes.")