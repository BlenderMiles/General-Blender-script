import bpy

def update_render_visibility():
    # Ensure we're in object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Get the current view layer
    view_layer = bpy.context.view_layer
    
    # Sync OBJECT visibility (viewport -> render)
    for obj in bpy.context.scene.objects:
        obj.hide_render = obj.hide_get()
    
    # Sync COLLECTION visibility (viewport -> render)
    for collection in bpy.data.collections:
        # Check if collection is hidden in the current view layer
        layer_collection = view_layer.layer_collection.children.get(collection.name)
        if layer_collection:
            # Use the layer_collection's hide_viewport for actual visibility state
            collection.hide_render = layer_collection.hide_viewport
        else:
            # Fallback to collection's own hide_viewport if not found in view layer
            collection.hide_render = collection.hide_viewport

# Run the function
update_render_visibility()
#print("Render visibility synced for objects and collections")