bl_info = {
    "name": "Slap it!",
    "author": "Artem Poletsky",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "A simple decals addon",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

import bpy

class SlapItOperator(bpy.types.Operator):
    """Slap decal on mesh"""
    bl_idname = "object.slap_it_operator"
    bl_label = "Slap it!"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 2

    def execute(self, context):
        
        C = bpy.context
        target_object = C.object
        selected = C.selected_objects
      
        selected.remove(target_object)
        source_decal_object = selected[0]
        target_object.select_set(False)

        C.view_layer.objects.active = source_decal_object
        bpy.ops.object.duplicate()

        active_object = C.object
        C.object.name = 'Slap ' + source_decal_object.name

        bpy.ops.object.modifier_add(type='SUBSURF')

        mod = active_object.modifiers["Subdivision"]
        mod.render_levels = 5
        mod.levels = 5
        mod.subdivision_type = 'SIMPLE'


        bpy.ops.object.modifier_add(type='SHRINKWRAP')

        mod = active_object.modifiers["Shrinkwrap"]
        mod.offset = 0.005
        mod.target = target_object
        mod.wrap_method = 'TARGET_PROJECT'
        mod.wrap_mode = 'ABOVE_SURFACE'

        bpy.ops.object.modifier_add(type='DECIMATE')

        mod = active_object.modifiers["Decimate"]
        mod.decimate_type = 'DISSOLVE'
        mod.angle_limit = 0.1

        bpy.ops.object.modifier_add(type='DATA_TRANSFER')

        active_object.data.use_auto_smooth = True
        mod = active_object.modifiers["DataTransfer"]
        mod.object = target_object
        mod.use_loop_data = True
        mod.data_types_loops = {'CUSTOM_NORMAL'}
        mod.loop_mapping = 'POLYINTERP_NEAREST'

        active_object.select_set(False)
        source_decal_object.select_set(True)
        C.view_layer.objects.active = source_decal_object
                
        return {'FINISHED'}

def menu_func(self, context):
    layout = self.layout
    layout.separator()

    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator('object.slap_it_operator', text='Slap it!')


def register():
    bpy.utils.register_class(SlapItOperator)
    
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)


def unregister():
    bpy.utils.unregister_class(SlapItOperator)
    
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
