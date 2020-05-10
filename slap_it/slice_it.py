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

def sort_loops(face):
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
            loops = sort_loops(f)
            print(loops)
            mesh.uv_layers.active.data[loops[0]].uv = [0, 0]
            mesh.uv_layers.active.data[loops[1]].uv = [1, 0]
            mesh.uv_layers.active.data[loops[2]].uv = [1, 1]
            mesh.uv_layers.active.data[loops[3]].uv = [0, 1]
        return

    def hide_source_objects(self, context, target, brush):
        select_only(context, target)
        brush.select_set(True)
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
        slice_decal = context.object
        oops.convert(target = 'MESH')

        brush_dupli.select_set(True)
        oops.join()
        # self.hide_source_objects(context, target, brush)
        select_only(context, slice_decal)
        oops.editmode_toggle()

        mops.select_mode(type='VERT', use_extend = False, use_expand = False)
        mops.intersect_boolean(operation = 'INTERSECT')
        mops.select_all(action = 'INVERT')
        mops.delete(type = 'VERT')
        mops.select_all(action = 'SELECT')
        mops.quads_convert_to_tris()
        mops.tris_convert_to_quads(face_threshold = math.pi, shape_threshold = math.pi)
        oops.editmode_toggle()

        collection = make_collection('Slice brushes', context.scene.collection)
        move_object_to_collection(context, brush, collection)
        context.view_layer.layer_collection.children['Slice brushes'].exclude = True
        #
        #
        # select_only(context, slice_decal)
        # oops.editmode_toggle()
        return slice_decal

    def slice(self, context, target, brush):
        slice_decal = self.create_slice_decal(context, target, brush)
        self.unwrap_slice_decal(context, slice_decal)
        self.assign_material(context, slice_decal)

    def execute(self, context):
        selected_objects = context.selected_objects
        active_object = context.view_layer.objects.active
        selected_objects.remove(active_object)
        self.slice(context, active_object, selected_objects[0])
        return {'FINISHED'}
