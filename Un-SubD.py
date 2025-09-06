#This script creates a -1 Level SubD mesh that better approximates the limit surface of a SubD mesh.
#It uses an iterative solver to adjust vertex positions based on their neighbors.
#works best on Closed Meshes with mostly quads.
#Usage: Select a SubD mesh object and run the script. A new object named "Cage" will be created.
#might need to adjust the number of iterations for different meshes.
# not ganteed to work on all meshes.

import bpy
import bmesh
import mathutils

obj = bpy.context.active_object
mesh = obj.data
bm_fine = bmesh.new()
bm_fine.from_mesh(mesh)
bm_fine.verts.ensure_lookup_table()

# Make copy for un-subdivide
copy_obj = obj.copy()
copy_mesh = mesh.copy()
copy_obj.data = copy_mesh
bpy.context.collection.objects.link(copy_obj)
bpy.context.view_layer.objects.active = copy_obj

# Add and apply decimate modifier for un-subdivide
mod = copy_obj.modifiers.new(name="UnSub", type='DECIMATE')
mod.decimate_type = 'UNSUBDIV'
mod.iterations = 2
bpy.ops.object.modifier_apply(modifier=mod.name)

# KDTree for closest match
kd = mathutils.kdtree.KDTree(len(bm_fine.verts))
for i in range(len(bm_fine.verts)):
    kd.insert(bm_fine.verts[i].co, i)
kd.balance()

# Get v_indices
v_indices = []
for v in copy_mesh.vertices:
    co, index, dist = kd.find(v.co)
    v_indices.append(index)  # Assume closest is correct

bm_fine.free()

# Create bmesh for coarse
bm = bmesh.new()
bm.from_mesh(copy_mesh)
bm.verts.ensure_lookup_table()

# Iterative solve for limit positions
for _ in range(20):
    for i, vert in enumerate(bm.verts):
        n = len(vert.link_edges)
        if n < 3:
            continue
        adjacent = [e.other_vert(vert) for e in vert.link_edges]
        diags = []
        for poly in vert.link_faces:
            for pv in poly.verts:
                if pv != vert and pv not in adjacent:
                    diags.append(pv)
        sum_adj = mathutils.Vector((0,0,0))
        for adj in adjacent:
            sum_adj += adj.co
        sum_diag = mathutils.Vector((0,0,0))
        for d in diags:
            sum_diag += d.co
        w_v = n / (n + 5.0)
        w_adj_sum = 4.0 / (n * (n + 5.0))
        w_diag_sum = 1.0 / (n * (n + 5.0))
        term_adj = w_adj_sum * sum_adj
        term_diag = w_diag_sum * sum_diag
        L = mesh.vertices[v_indices[i]].co
        new_co = (L - term_adj - term_diag) / w_v
        vert.co = new_co

bm.to_mesh(copy_mesh)
copy_mesh.update()

# Rename
copy_obj.name = "Cage"
copy_mesh.name = "Cage"

bm.free()