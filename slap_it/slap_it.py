import bpy

def view3d_find( return_area = False ):
    # returns first 3d view, normally we get from context
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces[0]
            rv3d = v3d.region_3d
            for region in area.regions:
                if region.type == 'WINDOW':
                    if return_area: return region, rv3d, v3d, area
                    return region, rv3d, v3d
    return None, None

def knife_override(selected, edit):


    region, rv3d, v3d, area = view3d_find(True)

    # Define context override dictionary for overriding the knife_project operator's context
    override = {
        'scene'            : bpy.context.scene,
        'region'           : region,
        'area'             : area,
        'space'            : v3d,
        'active_object'    : bpy.context.object,
        'window'           : bpy.context.window,
        'screen'           : bpy.context.screen,
        'selected_objects' : selected,
        'edit_object'      : edit
    }

    return override


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
        source_decal_object.select_set(False)

        C.view_layer.objects.active = target_object
        bpy.ops.object.duplicate()
        decal_object = C.object
        bpy.ops.object.convert(target='MESH')

        bpy.ops.object.select_all(action='DESELECT')

        source_decal_object.select_set(True)
        C.view_layer.objects.active = source_decal_object
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.editmode_toggle()

        override = knife_override([source_decal_object, decal_object], decal_object)

        bpy.ops.object.camera_add()
        camera = C.object
        old_camera = C.scene.camera
        C.scene.camera = camera
        bpy.ops.view3d.camera_to_view()
        camera.select_set(False)

        decal_object.select_set(True)
        source_decal_object.select_set(True)
        C.view_layer.objects.active = source_decal_object
        bpy.ops.view3d.view_axis(type='TOP', align_active=True, relative=False)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        C.view_layer.objects.active = decal_object
        bpy.ops.object.editmode_toggle()

        bpy.ops.mesh.knife_project(override);


        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_all(action='INVERT')
        #bpy.ops.mesh.select_linked_pick(deselect=True, delimit=set(), index=1)
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.editmode_toggle()
        C.view_layer.objects.active = source_decal_object
        decal_object.select_set(True)
        bpy.ops.object.make_links_data(type='MATERIAL')

        C.view_layer.objects.active = decal_object
        source_decal_object.select_set(False)
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')

        override = {'area': override['area'], 'region': override['region'], 'edit_object': decal_object}
        bpy.ops.uv.project_from_view(override, camera_bounds = False, scale_to_bounds=True, correct_aspect=True)

        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')


        decal_object.name = 'Slap ' + source_decal_object.name

        decal_object.select_set(True)
        C.view_layer.objects.active = decal_object


        bpy.ops.object.modifier_add(type='DISPLACE')

        mod = decal_object.modifiers["Displace"]
        mod.strength = 0.001

        bpy.ops.object.modifier_add(type='DATA_TRANSFER')

        decal_object.data.use_auto_smooth = True
        decal_object.cycles_visibility.shadow = False
        mod = decal_object.modifiers["DataTransfer"]
        mod.object = target_object
        mod.use_loop_data = True
        mod.data_types_loops = {'CUSTOM_NORMAL'}
        mod.loop_mapping = 'POLYINTERP_NEAREST'

        decal_object.select_set(False)

        camera.select_set(True)
        C.view_layer.objects.active = camera

#        bpy.ops.action.view_frame(override)
        bpy.ops.view3d.view_camera(override)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.object.delete()
        C.scene.camera = old_camera
        source_decal_object.select_set(True)
        C.view_layer.objects.active = source_decal_object

        return {'FINISHED'}
