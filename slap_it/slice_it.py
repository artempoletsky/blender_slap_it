import bpy

oops = bpy.ops.object
mops = bpy.ops.mesh

def select_only(context, object):
    oops.select_all(action = 'DESELECT')
    context.view_layer.objects.active = object
    object.select_set(True)

class SliceItOperator(bpy.types.Operator):
    """Create slice decal"""
    bl_idname = "object.slice_it_operator"
    bl_label = "Slice it!"
    bl_options = {'REGISTER', 'UNDO'}

    thickness: bpy.props.FloatProperty(name="Slice thickness", default=0.1)
    remove_brush: bpy.props.BoolProperty(name="Remove brush object", default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 2

    def assign_material(self, context, slice_decal):
        return

    def unwrap_slice_decal(self, context, slice_decal):
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
        self.hide_source_objects(context, target, brush)
        select_only(context, slice_decal)
        oops.editmode_toggle()

        mops.select_mode(type='VERT', use_extend = False, use_expand = False)
        mops.intersect_boolean(operation = 'INTERSECT')
        mops.select_all(action = 'INVERT')
        mops.delete(type = 'VERT')
        # oops.editmode_toggle()
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
