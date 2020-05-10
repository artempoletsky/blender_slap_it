import bpy
import math
import bmesh

oops = bpy.ops.object
mops = bpy.ops.mesh
uvops = bpy.ops.uv

def find_collection(context, item):
    collections = item.users_collection
    if len(collections) > 0:
        return collections[0]
    return context.scene.collection

def make_collection(collection_name, parent_collection):
    if collection_name in bpy.data.collections: # Does the collection already exist?
        return bpy.data.collections[collection_name]
    else:
        new_collection = bpy.data.collections.new(collection_name)
        parent_collection.children.link(new_collection) # Add the new collection under a parent
        return new_collection

def move_object_to_collection(context, object, new_collection):
    object_collection = find_collection(context, object)
    object_collection.objects.unlink(object)
    new_collection.objects.link(object)

def select_only(context, object):
    oops.select_all(action = 'DESELECT')
    context.view_layer.objects.active = object
    object.select_set(True)

from mathutils import geometry
 # mathutils.geometry.distance_point_to_plane(pt, plane_co, plane_no)

def is_face_on_surface(face, bm):
    median = face.calc_center_median()
    min_distance = float('inf')
    for f in bm.faces:
        d = abs(geometry.distance_point_to_plane(median, f.calc_center_median(), f.normal))
        min_distance = min(min_distance, d)
    # if min_distance == 0:
        # face.select_set(True)
    # print(min_distance, min_distance < 0.1)
    return min_distance == 0

def sort_tris_loops(face):
    return [l.index for l in face.loops]

def sort_quad_loops(face):
    if len(face.edges[0].link_faces) == 1 and len(face.edges[2].link_faces) == 1:
        loops = []
        loops.append(face.loops[3].index)
        loops.append(face.loops[0].index)
        loops.append(face.loops[1].index)
        loops.append(face.loops[2].index)
        return loops
    return [l.index for l in face.loops]

class SliceItOperator(bpy.types.Operator):
    """Create slice decal"""
    bl_idname = "object.slice_it_operator"
    bl_label = "Slice it!"
    bl_options = {'REGISTER', 'UNDO'}

    thickness: bpy.props.FloatProperty(name="Slice thickness", default=0.1)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 2

    def assign_material(self, context, slice_decal):
        mod = slice_decal.modifiers.new('Displace', 'DISPLACE')
        mod.strength = 0.01
        materials = slice_decal.data.materials
        materials.clear()
        materials.append(bpy.data.materials[0])
        return

    def unwrap_slice_decal(self, context, slice_decal):
        # print(len(context.object.data.uv_layers.active.data))
        oops.editmode_toggle()
        mops.select_all(action = 'SELECT')
        uvops.reset()
        oops.editmode_toggle()
        mesh = slice_decal.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        for f in bm.faces:
            if len(f.verts) == 4:
                loops = sort_quad_loops(f)
                mesh.uv_layers.active.data[loops[0]].uv = [0, 0]
                mesh.uv_layers.active.data[loops[1]].uv = [1, 0]
                mesh.uv_layers.active.data[loops[2]].uv = [1, 1]
                mesh.uv_layers.active.data[loops[3]].uv = [0, 1]
            else:
                loops = sort_tris_loops(f)
                mesh.uv_layers.active.data[loops[0]].uv = [0, 0]
                mesh.uv_layers.active.data[loops[1]].uv = [1, 0]
                mesh.uv_layers.active.data[loops[2]].uv = [0.5, 1]


    def hide_source_objects(self, context, objects):
        select_only(context, objects[0])
        for o in objects:
            o.select_set(True)
        oops.hide_view_set(unselected = False)

    def create_slice_decal(self, context, target, brush):
        select_only(context, brush)
        oops.duplicate()
        brush_dupli = context.object
        # solidify brush
        mod = brush_dupli.modifiers.new("SOLIDIFY", "SOLIDIFY")
        mod.offset = 0
        mod.thickness = self.thickness
        oops.convert(target = 'MESH')

        oops.editmode_toggle()
        mops.select_all(action = 'SELECT')
        oops.editmode_toggle()

        select_only(context, target)
        oops.editmode_toggle()
        mops.select_all(action = 'DESELECT')
        oops.editmode_toggle()
        oops.duplicate()
        oops.convert(target = 'MESH')
        target_dupli = context.object
        oops.duplicate()
        slice_decal = context.object

        brush_dupli.select_set(True)
        oops.join()
        if self._hide_source:
            self.hide_source_objects(context, [target, brush, target_dupli])
        select_only(context, slice_decal)
        oops.editmode_toggle()

        mops.select_mode(type='VERT', use_extend = False, use_expand = False)
        mops.intersect_boolean(operation = 'INTERSECT')
        bm = bmesh.from_edit_mesh(slice_decal.data)
        if self._stop_after_intersect:
            raise

        unselected_verts = [v for v in bm.verts if not v.select]
        if len(unselected_verts) != 0:
            mops.select_all(action = 'INVERT')
            mops.delete(type = 'VERT')
        else:
            mops.select_mode(type='FACE', use_extend = False, use_expand = False)
            source_bm = bmesh.new()
            source_bm.from_mesh(target_dupli.data)
            deleted_faces = [f for f in bm.faces if not is_face_on_surface(f, source_bm)]
            bmesh.ops.delete(bm, geom = deleted_faces, context = 'FACES')
            bmesh.update_edit_mesh(slice_decal.data, True)
            source_bm.free()

        mops.select_mode(type='FACE', use_extend = False, use_expand = False)
        if self._stop_before_triangulate:
            raise
        mops.select_all(action = 'DESELECT')
        non_quads = [f for f in bm.faces if len(f.verts) != 4]
        if len(non_quads):
            for f in non_quads:
                f.select_set(True)
            mops.quads_convert_to_tris()
            mops.tris_convert_to_quads(face_threshold = math.pi, shape_threshold = math.pi)
            # non_quads = [f for f in bm.faces if len(f.verts) != 4]
            # if len(non_quads):
            #     self.report({'ERROR'}, "Can\'t create quads mesh decal!")
            #     bm.free()
            #     return None

        bm.free()
        oops.editmode_toggle()

        collection = make_collection('Slice brushes', context.scene.collection)
        move_object_to_collection(context, brush, collection)
        context.view_layer.layer_collection.children['Slice brushes'].exclude = True

        select_only(context, target_dupli)
        oops.delete(use_global = False)
        select_only(context, slice_decal)
        # oops.editmode_toggle()
        return slice_decal

    def slice(self, context, target, brush):
        slice_decal = self.create_slice_decal(context, target, brush)
        if not slice_decal:
            return
        self.unwrap_slice_decal(context, slice_decal)
        self.assign_material(context, slice_decal)

    def execute(self, context):
        self._hide_source = False
        self._stop_after_intersect = False
        self._stop_before_triangulate = False
        selected_objects = context.selected_objects
        active_object = context.view_layer.objects.active
        selected_objects.remove(active_object)
        self.slice(context, active_object, selected_objects[0])
        return {'FINISHED'}
