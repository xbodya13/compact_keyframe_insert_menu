from typing import *


bl_info = {
    "name": "Compact keyframe insert menu",
    "category": "Animation",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Compact keyframe insert menu",
    "wiki_url": "https://github.com/xbodya13/compact_keyframe_insert_menu",
    "tracker_url": "https://github.com/xbodya13/compact_keyframe_insert_menu/issues"
}

import bpy






def use_visual_update(self,context):
    key_set=context.scene.keying_sets_all[BUILTIN_KSI_transform.bl_label]
    key_set.use_insertkey_override_visual=key_set.use_insertkey_visual=context.scene.compact_keyframe_insert_menu.use_visual

    return None

class KeySettings(bpy.types.PropertyGroup):

    use_location: bpy.props.BoolProperty(name="Location",default=True)
    use_rotation: bpy.props.BoolProperty(name="Rotation",default=True)
    use_scale: bpy.props.BoolProperty(name="Scale",default=True)

    use_visual: bpy.props.BoolProperty(name="Visual",default=False,update=use_visual_update)
    use_delta: bpy.props.BoolProperty(name="Delta",default=False)

    use_local_rotation:bpy.props.BoolProperty(name="Local rotation",description="Insert keyframes on local rotation of FreeIK nodes",default=True)
    use_linked:bpy.props.BoolProperty(name="Linked",description="Insert keyframes on FreeIK nodes which are connected to selected",default=True)




def items_from_key_sets(self,context):
    key_sets_to_replace=(
    'Location','Rotation','Scaling','BUILTIN_KSI_LocRot','LocRotScale','BUILTIN_KSI_LocScale','BUILTIN_KSI_RotScale',
    'BUILTIN_KSI_DeltaLocation','BUILTIN_KSI_DeltaRotation','BUILTIN_KSI_DeltaScale','BUILTIN_KSI_VisualLoc',
    'BUILTIN_KSI_VisualRot','BUILTIN_KSI_VisualScaling','BUILTIN_KSI_VisualLocRot','BUILTIN_KSI_VisualLocRotScale',
    'BUILTIN_KSI_VisualLocScale','BUILTIN_KSI_VisualRotScale')

    items=[]

    active_bl_idname=BUILTIN_KSI_transform.bl_idname
    key_set=bpy.context.scene.keying_sets_all.active
    if key_set is not None:
        if key_set.bl_idname not in key_sets_to_replace:
            active_bl_idname=key_set.bl_idname


    x=1
    for key_set in context.scene.keying_sets_all:
        if key_set.bl_idname not in key_sets_to_replace:
            if key_set.bl_idname==active_bl_idname:
                items.append((key_set.bl_label,key_set.bl_label,key_set.bl_description,'NONE',0))
            else:
                items.append((key_set.bl_label,key_set.bl_label,key_set.bl_description,'NONE',x))
            x+=1

    # items.append(('TRANSFORM',"Transform","Insert a keyframe for transform related properties",'NONE',x+1))

    return items








class CompactKeyframeInsertMenuInsert(bpy.types.Operator):

    bl_idname = "anim.compact_keyframe_insert_menu_insert"
    bl_label = "Insert keyframe"

    @classmethod
    def poll(self, context):
        return context.mode in ('OBJECT','POSE')
    def execute(self, context):
        return bpy.ops.anim.compact_keyframe_insert_menu('INVOKE_DEFAULT',mode='INSERT')

class CompactKeyframeInsertMenuChange(bpy.types.Operator):

    bl_idname = "anim.compact_keyframe_insert_menu_change"
    bl_label = "Change keying set"

    @classmethod
    def poll(self, context):
        return context.mode in ('OBJECT','POSE')

    # def invoke(self,context,event):
    #     return bpy.ops.anim.compact_keyframe_insert_menu('INVOKE_DEFAULT',mode='CHANGE')

    def execute(self, context):
        return bpy.ops.anim.compact_keyframe_insert_menu('INVOKE_DEFAULT',mode='CHANGE')







class CompactKeyframeInsertMenu(bpy.types.Operator):

    bl_idname = "anim.compact_keyframe_insert_menu"
    bl_label = "Select keying set"
    # bl_options = {'REGISTER', 'UNDO'}
    bl_options={'UNDO'}




    active_key_set:bpy.props.EnumProperty(name="Key sets",items=items_from_key_sets)

    use_location: bpy.props.BoolProperty(name="Location",default=True)
    use_rotation: bpy.props.BoolProperty(name="Rotation",default=True)
    use_scale: bpy.props.BoolProperty(name="Scale",default=True)

    use_visual: bpy.props.BoolProperty(name="Visual",default=False)
    use_delta: bpy.props.BoolProperty(name="Delta",default=False)

    use_local_rotation:bpy.props.BoolProperty(name="Local",default=True)
    use_linked:bpy.props.BoolProperty(name="Linked",default=True)


    mode:bpy.props.EnumProperty(name="Mode",
                                      items=[
                                          ('CHANGE',"Change","Change",'NONE',0),
                                          ('INSERT',"Insert","Insert",'NONE',1),

                                      ])




    @classmethod
    def poll(self, context):
        return True


    def execute(self, context):
        # print("EXECUTE")

        if self.mode=='INSERT':
            context.scene.keying_sets_all.active=context.scene.keying_sets_all[self.active_key_set]
            try:bpy.ops.anim.keyframe_insert()
            except:pass
        if self.mode=='CHANGE':
            context.scene.keying_sets_all.active=context.scene.keying_sets_all[self.active_key_set]


        return {'FINISHED'}

    def invoke(self,context,event):
        # print("INVOKE")

        if  hasattr(bpy.types.Scene,"free_ik_gv"):self.gv=bpy.types.Scene.free_ik_gv
        else:self.gv=None

        if (self.mode=='INSERT' and context.scene.keying_sets_all.active==None) or self.mode=='CHANGE':
            return context.window_manager.invoke_props_dialog(self)
        else:
            try:return  bpy.ops.anim.keyframe_insert()
            except:return {'FINISHED'}
    def check(self,context):
        return True

    def draw(self,context):


        self.layout.prop(self,"active_key_set",text="Keying set")


        if self.active_key_set==BUILTIN_KSI_transform.bl_label:
            self.layout.separator()

            row=self.layout.row()
            row.prop(context.scene.compact_keyframe_insert_menu,"use_location")
            row.prop(context.scene.compact_keyframe_insert_menu,"use_rotation")
            row.prop(context.scene.compact_keyframe_insert_menu,"use_scale")

            if self.gv is not None:
                if len(self.gv.nodes)!=0:
                    split=self.layout.split()
                    split.separator()
                    split.prop(context.scene.compact_keyframe_insert_menu,"use_local_rotation",text="Local")
                    split.separator()


            self.layout.separator()


            self.layout.prop(context.scene.compact_keyframe_insert_menu,"use_visual")

            if context.mode!='POSE':
                self.layout.prop(context.scene.compact_keyframe_insert_menu,"use_delta")

            if self.gv is not None:
                if len(self.gv.nodes)!=0:
                    self.layout.prop(context.scene.compact_keyframe_insert_menu,"use_linked")





    # def modal(self,context,event):
    #     print("MODAL")
    #     # time.sleep(1)
    #     return {'FINISHED'}


class BUILTIN_KSI_transform(bpy.types.KeyingSetInfo):
    bl_label="Transform"
    bl_idname='TRANSFORM'
    # bl_options={'INSERTKEY_NEEDED','INSERTKEY_VISUAL'}
    bl_options=set()

    # poll - test for whether Keying Set can be used at all

    def get_gv(self):
        if  hasattr(bpy.types.Scene,"free_ik_gv"):return bpy.types.Scene.free_ik_gv
        else:return None


    def get_items(self,context):

        items=set()
        if context.mode=='POSE':
            items=set(context.selected_pose_bones)

        if context.mode=='OBJECT':
            items=set(context.selected_objects)

        return items

    def get_linked_items(self,context):
        gv=self.get_gv()
        linked_items=set()

        if gv is not None and context.scene.compact_keyframe_insert_menu.use_linked:
            selected_clusters=set()

            for node in gv.clustered_nodes:
                if node.is_selected :
                    if not (node.is_bone and context.mode=='OBJECT'):
                        selected_clusters.add(node.cluster)

            for cluster in selected_clusters:
                for node in cluster.nodes:
                    if not node.is_selected:
                        linked_items.add(node.source)
        return linked_items


    def poll(self,context):
        # print("POLL")


        settings=context.scene.compact_keyframe_insert_menu
        if settings.use_location or settings.use_rotation or settings.use_scale:
            items=self.get_items(context)
            if len(items)!=0:
                return True
        return False

        # return context.active_object or context.selected_objects

    # iterator - go over all relevant data, calling generate()
    def iterator(self,context,ks):
        # print("ITERATOR")
        items=self.get_items(context)

        gv=self.get_gv()
        if gv is not None:
            gv.is_indirect_key_create=False


        for item in items:
            # print(item)
            self.generate(context,ks,item)



    # generator - populate Keying Set with property paths to use

    def generate_source(self,context,ks,item):

        if type(item)==bpy.types.PoseBone:
            base_path='pose.bones["{}"].'.format(item.name)
            fcurve_holder=item.id_data
            group_name=item.name
        else:
            base_path=""
            fcurve_holder=item
            group_name="Object Transforms"


        if context.scene.compact_keyframe_insert_menu.use_delta and context.mode=='OBJECT':
            location_name="delta_location"
            rotation_name="delta_rotation_euler"
            scale_name="delta_scale"
        else:
            location_name="location"

            if item.rotation_mode=='QUATERNION':rotation_name="rotation_quaternion"
            elif item.rotation_mode=='AXIS_ANGLE':rotation_name="rotation_axis_angle"
            else:rotation_name="rotation_euler"

            scale_name="scale"


        if context.scene.compact_keyframe_insert_menu.use_location:
            ks.paths.add(fcurve_holder,base_path+location_name,group_method='NAMED', group_name=group_name)
        if context.scene.compact_keyframe_insert_menu.use_rotation:
            ks.paths.add(fcurve_holder,base_path+rotation_name,group_method='NAMED', group_name=group_name)
        if context.scene.compact_keyframe_insert_menu.use_scale:
            ks.paths.add(fcurve_holder,base_path+scale_name,group_method='NAMED', group_name=group_name)

        if  hasattr(bpy.types.Scene,"free_ik_gv"):gv=bpy.types.Scene.free_ik_gv
        else:gv=None

        if gv and context.scene.compact_keyframe_insert_menu.use_local_rotation:
            if item in gv.nodes_dictionary:
                if gv.nodes_dictionary[item].frame_parent is not None:
                    if item.rotation_mode=='QUATERNION':ks.paths.add(fcurve_holder,base_path+"free_ik_local_quaternion",group_method='NAMED', group_name=group_name)
                    elif item.rotation_mode=='AXIS_ANGLE':ks.paths.add(fcurve_holder,base_path+"free_ik_local_axis_angle",group_method='NAMED', group_name=group_name)
                    else:ks.paths.add(fcurve_holder,base_path+"free_ik_local_euler",group_method='NAMED', group_name=group_name)



    def generate(self,context,ks,item):
        # print("GENERATOR",item)

        gv=self.get_gv()
        # print(gv,gv.is_indirect_key_create)
        if gv is not None:
            if not hasattr(gv,"is_indirect_key_create"):
                gv.is_indirect_key_create=False


            if not gv.is_indirect_key_create:
                linked_items=self.get_linked_items(context)
                for linked_item in linked_items:
                    self.generate_source(context,ks,linked_item)

            gv.is_indirect_key_create=True

        self.generate_source(context,ks,item)


class KeyMapOperator(bpy.types.Operator):
    bl_idname = "preferences.compact_keyframe_insert_menu_ui"
    bl_label="Keymap operator"

    mode:bpy.props.EnumProperty(name="Mode",
                                      items=[
                                          ('MAKE',"","",'NONE',0),
                                          ('CLEAR',"","",'NONE',1),
                                          ('RESTORE',"","",'NONE',2),
                                          ('RESOLVE',"","",'NONE',3)
                                      ]
                                      )
    target_idname:bpy.props.StringProperty()
    # target_keymap_name:bpy.props.StringProperty()
    conflict_keymap_names: bpy.props.StringProperty()
    id_to_resolve: bpy.props.IntProperty()

    def execute(self, context):

        if self.mode=='MAKE':
            context.keymap_items.new(idname=self.target_idname,type='NONE',value='PRESS',head=True)

        if self.mode=='CLEAR':
            context.keymap_items.remove(context.keymap_items.from_id(self.id_to_resolve))
        if self.mode=='RESTORE':
            keymap_item=context.keymap_items.from_id(self.id_to_resolve)
            # print(dir(keymap_item))
            # print(keymap_item.propvalue,keymap_item.map_type)
            keymap_item.map_type='KEYBOARD'
            keymap_item.value='PRESS'
            keymap_item.type='NONE'
            keymap_item.key_modifier='NONE'
            keymap_item.any=False
            keymap_item.ctrl=False
            keymap_item.oskey=False
            keymap_item.alt=False
            keymap_item.shift=False

        if self.mode=='RESOLVE':
            keymap_holder=bpy.context.window_manager.keyconfigs.user.keymaps
            conflict_keymaps=[keymap_holder[name] for name in self.conflict_keymap_names.split(',')]

            active_item=context.keymap.keymap_items.from_id(self.id_to_resolve)
            for conflict_keymap in conflict_keymaps:
                # print(conflict_keymap)
                for keymap_item in conflict_keymap.keymap_items:
                    if keymap_item.active and keymap_item.compare(active_item) and keymap_item!=active_item:
                        keymap_item.active=False








        return {'FINISHED'}


class Preferences(bpy.types.AddonPreferences):

    bl_idname = __name__


    def check(self,context):
        return True

    def draw_keymap_item(self,layout,target_idname,target_keymap_name,target_label,conflict_keymap_names):
        # print()
        # print(target_label,target_keymap_name)

        keymap_holder=bpy.context.window_manager.keyconfigs.user.keymaps
        target_keymap=keymap_holder[target_keymap_name]
        conflict_keymaps=[keymap_holder[name] for name in conflict_keymap_names]
        for conflict_keymap in conflict_keymaps:
            conflict_keymap.keymap_items.update()

        target_item=None

        for keymap_item in target_keymap.keymap_items:
            if keymap_item.idname==target_idname:
                target_item=keymap_item
                break

        conflict_items=[]
        # print(target_item)
        if target_item is not None:
            for conflict_keymap in conflict_keymaps:
                for keymap_item in conflict_keymap.keymap_items:

                    # if keymap_item.compare(target_item):print(keymap_item)

                    if keymap_item.active and keymap_item.compare(target_item) and keymap_item!=target_item:
                        if keymap_item.type!='NONE' or keymap_item.key_modifier!='NONE' or any((keymap_item.any,keymap_item.ctrl,keymap_item.oskey,keymap_item.alt,keymap_item.shift)):
                            # print(keymap_item)
                            conflict_items.append(keymap_item)


        row=layout.row()
        row.label(text=target_label)
        if target_item is None:
            row.context_pointer_set("keymap_items",target_keymap.keymap_items)
            operator=row.operator(KeyMapOperator.bl_idname,text="Create mapping")
            operator.mode='MAKE'
            operator.target_idname=target_idname

        else:
            row.prop(target_item,"value")
            row.prop(target_item,"type",full_event=True,text="")

            row.context_pointer_set("keymap_items",target_keymap.keymap_items)
            operator=row.operator(KeyMapOperator.bl_idname,text="",icon='BACK')
            operator.mode='RESTORE'
            operator.id_to_resolve=target_item.id

            row.context_pointer_set("keymap_items",target_keymap.keymap_items)
            operator=row.operator(KeyMapOperator.bl_idname,text="",icon='X')
            operator.mode='CLEAR'
            operator.id_to_resolve=target_item.id

            if len(conflict_items)!=0:
                layout.context_pointer_set("keymap",target_keymap)
                operator=layout.operator(KeyMapOperator.bl_idname,text=f"Disable {len(conflict_items)} conflicting mappings ")
                operator.mode='RESOLVE'
                operator.id_to_resolve=target_item.id
                operator.conflict_keymap_names=",".join(conflict_keymap_names)

        layout.separator()

    def draw(self, context):
        layout = self.layout
        # layout.separator()

        target_keymap_name='3D View'
        conflict_keymap_names=(target_keymap_name,'Object Mode','Pose')

        self.draw_keymap_item(layout,target_idname=CompactKeyframeInsertMenuInsert.bl_idname,target_keymap_name='3D View',target_label="Insert key",conflict_keymap_names=conflict_keymap_names)
        self.draw_keymap_item(layout,target_idname=CompactKeyframeInsertMenuChange.bl_idname,target_keymap_name='3D View',target_label="Change keying set",conflict_keymap_names=conflict_keymap_names)





register_classes=[CompactKeyframeInsertMenu,KeySettings,BUILTIN_KSI_transform,CompactKeyframeInsertMenuInsert,CompactKeyframeInsertMenuChange,KeyMapOperator,Preferences]



def register():
    # os.system('cls')
    # print("I AM REGISTER")


    for register_class in register_classes:
        bpy.utils.register_class(register_class)

    bpy.types.Scene.compact_keyframe_insert_menu=bpy.props.PointerProperty(type=KeySettings)


    # print("REGISTER FINISHED")


def unregister():
    # print("I AM UNREGISTER")

    for register_class in register_classes:
        bpy.utils.unregister_class(register_class)

    # print("UNREGISTER FINISHED")