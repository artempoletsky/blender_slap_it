import bpy


class SliceItOperator(bpy.types.Operator):
    """Create slice decal"""
    bl_idname = "object.slice_it_operator"
    bl_label = "Slice it!"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 2

    def assign_material(self, context, slice_decal):
        return

    def unwrap_slice_decal(self, context, slice_decal):
        return

    def create_slice_decal(self, context, target, brush):
        return target

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
