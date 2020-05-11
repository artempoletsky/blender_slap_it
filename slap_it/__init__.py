bl_info = {
    "name": "Slap it!",
    "author": "Artem Poletsky",
    "version": (2, 0, 0),
    "blender": (2, 80, 0),
# "location": "View3D > Add > Mesh > New Object",
    "description": "A simple decals addon",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

if "bpy" in locals():
    import importlib
    importlib.reload(slap_it)
    SlapItOperator = slap_it.SlapItOperator
    importlib.reload(slice_it)
    SliceItOperator = slice_it.SliceItOperator

else:
    from .slap_it import SlapItOperator
    from .slice_it import SliceItOperator

import bpy

def menu_func(self, context):
    layout = self.layout
    layout.separator()

    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator(SlapItOperator.bl_idname, text=SlapItOperator.bl_label)
    layout.operator(SliceItOperator.bl_idname, text=SliceItOperator.bl_label)

classes = (
    SlapItOperator,
    SliceItOperator
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
