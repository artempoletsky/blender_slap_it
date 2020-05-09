import bpy


class SliceItOperator(bpy.types.Operator):
    """Create slice decal"""
    bl_idname = "object.slice_it_operator"
    bl_label = "Slice it!"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 2

    def execute(self, context):
        return {'FINISHED'}
