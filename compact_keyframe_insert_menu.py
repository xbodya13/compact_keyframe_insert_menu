from typing import *


bl_info = {
    "name": "Compact keyframe insert menu",
    "category": "Animation",
    "version": (1, 0),
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


class Preferences(bpy.types.AddonPreferences):

    bl_idname = __name__


    def check(self,context):
        return True

    def draw(self, context):
        layout = self.layout
        # layout.separator()

        modes=('Object Mode','Pose')
        labels=("Object mode shortcuts:","Pose mode shortcuts:")
        for mode,label in zip(modes,labels):
            insert_keymap_item=None
            change_keymap_item=None



            keymap=bpy.context.window_manager.keyconfigs.user.keymaps[mode]
            keymap_items=keymap.keymap_items
            keymap_items.update()


            for keymap_item in keymap_items:
                if keymap_item.idname==CompactKeyframeInsertMenuInsert.bl_idname:
                    insert_keymap_item=keymap_item
                if keymap_item.idname==CompactKeyframeInsertMenuChange.bl_idname:
                    change_keymap_item=keymap_item


            work_keymap_items=[insert_keymap_item,change_keymap_item]
            work_conflicts=[[],[]]
            work_labels=["Insert key","Change keying set"]
            new_keymap_modes=[CompactKeyframeInsertMenuInsert.bl_idname,CompactKeyframeInsertMenuChange.bl_idname]


            layout.label(text=label)


            for work_keymap_item,item_conflicts,work_label,new_keymap_mode in zip(work_keymap_items,work_conflicts,work_labels,new_keymap_modes):

                if work_keymap_item is not None:
                    for keymap_item in keymap_items:
                        if keymap_item.active and keymap_item.compare(work_keymap_item) and keymap_item!=work_keymap_item:
                            if keymap_item.type!='NONE' or keymap_item.key_modifier!='NONE' or any((keymap_item.any,keymap_item.ctrl,keymap_item.oskey,keymap_item.alt,keymap_item.shift)):

                                item_conflicts.append(keymap_item)


                # print(work_keymap_item,change_keymap_item)


                row=layout.row()
                row.label(text=work_label)
                if work_keymap_item is None:
                    row.context_pointer_set("keymap_items",keymap_items)
                    operator=row.operator(KeyMapOperator.bl_idname,text="Create mapping")
                    operator.mode='MAKE'
                    operator.new_keymap_mode=new_keymap_mode

                else:
                    row.prop(work_keymap_item,"value")
                    row.prop(work_keymap_item,"type",full_event=True,text="")


                    row.context_pointer_set("keymap_items",keymap_items)
                    operator=row.operator(KeyMapOperator.bl_idname,text="",icon='BACK')
                    operator.mode='RESTORE'
                    operator.id_to_resolve=work_keymap_item.id


                    row.context_pointer_set("keymap_items",keymap_items)
                    operator=row.operator(KeyMapOperator.bl_idname,text="",icon='X')
                    operator.mode='CLEAR'
                    operator.id_to_resolve=work_keymap_item.id



                    if len(item_conflicts)!=0:
                        layout.context_pointer_set("keymap",keymap)
                        operator=layout.operator(KeyMapOperator.bl_idname,text=f"Disable {len(item_conflicts)} conflicting mappings ")
                        operator.mode='RESOLVE'
                        operator.id_to_resolve=work_keymap_item.id

            layout.separator()


class CompactKeyframeInsertMenuInsert(bpy.types.Operator):

    bl_idname = "anim.compact_keyframe_insert_menu_insert"
    bl_label = "Insert keyframe"

    @classmethod
    def poll(self, context):
        return True
    def execute(self, context):
        return bpy.ops.anim.compact_keyframe_insert_menu('INVOKE_DEFAULT',mode='INSERT')

class CompactKeyframeInsertMenuChange(bpy.types.Operator):

    bl_idname = "anim.compact_keyframe_insert_menu_change"
    bl_label = "Change keying set"

    @classmethod
    def poll(self, context):
        return True

    # def invoke(self,context,event):
    #     return bpy.ops.anim.compact_keyframe_insert_menu('INVOKE_DEFAULT',mode='CHANGE')

    def execute(self, context):
        return bpy.ops.anim.compact_keyframe_insert_menu('INVOKE_DEFAULT',mode='CHANGE')




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
    new_keymap_mode:bpy.props.EnumProperty(name="Mode",
                                      items=[
                                          (CompactKeyframeInsertMenuInsert.bl_idname,"","",'NONE',0),
                                          (CompactKeyframeInsertMenuChange.bl_idname,"","",'NONE',1),
                                      ]
                                      )

    id_to_resolve: bpy.props.IntProperty()

    def execute(self, context):
        if self.mode=='MAKE':
            context.keymap_items.new(idname=self.new_keymap_mode,type='NONE',value='PRESS',head=True)

        if self.mode=='RESOLVE':
            keymap_item_to_resolve=context.keymap.keymap_items.from_id(self.id_to_resolve)
            for keymap_item in context.keymap.keymap_items:
                if keymap_item.active and keymap_item.compare(keymap_item_to_resolve) and keymap_item!=keymap_item_to_resolve:
                    keymap_item.active=False
        if self.mode=='CLEAR':
            context.keymap_items.remove(context.keymap_items.from_id(self.id_to_resolve))
        if self.mode=='RESTORE':
            # context.keymap.restore_item_to_default(context.keymap.keymap_items.from_id(self.id_to_resolve))
            keymap_item=context.keymap_items.from_id(self.id_to_resolve)
            keymap_item.type='NONE'
            keymap_item.key_modifier='NONE'
            keymap_item.any=False
            keymap_item.ctrl=False
            keymap_item.oskey=False
            keymap_item.alt=False
            keymap_item.shift=False








        return {'FINISHED'}







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
                split=self.layout.split()
                split.separator()
                split.prop(context.scene.compact_keyframe_insert_menu,"use_local_rotation",text="Local")
                split.separator()


            self.layout.separator()


            self.layout.prop(context.scene.compact_keyframe_insert_menu,"use_visual")

            if context.mode!='POSE':
                self.layout.prop(context.scene.compact_keyframe_insert_menu,"use_delta")

            if self.gv is not None:
                self.layout.prop(context.scene.compact_keyframe_insert_menu,"use_linked")





    # def modal(self,context,event):
    #     print("MODAL")
    #     # time.sleep(1)
    #     return {'FINISHED'}


class BUILTIN_KSI_transform(bpy.types.KeyingSetInfo):
    bl_label="Transform"
    bl_idname='TRANSFORM'
    # bl_options={'INSERTKEY_NEEDED','INSERTKEY_VISUAL'}

    # poll - test for whether Keying Set can be used at all



    def get_items(self,context):

        if  hasattr(bpy.types.Scene,"free_ik_gv"):gv=bpy.types.Scene.free_ik_gv
        else:gv=None

        items=set()
        if context.mode=='POSE':
            items=set(context.selected_pose_bones)

        if context.mode=='OBJECT':
            items=set(context.selected_objects)

        if gv is not None and context.scene.compact_keyframe_insert_menu.use_linked:
            selected_clusters=set()

            for node in gv.clustered_nodes:
                if node.is_selected and not node.is_unselected_active:
                    if not (node.is_bone and context.mode=='OBJECT'):
                        selected_clusters.add(node.cluster)

            for cluster in selected_clusters:
                for node in cluster.nodes:
                    items.add(node.source)

        return items


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
        for item in items:
            self.generate(context,ks,item)


    # generator - populate Keying Set with property paths to use
    def generate(self,context,ks,item):
        # print("GENERATOR")
        # print(self.use_insertkey_visual)


        if type(item)==bpy.types.PoseBone:
            base_path='pose.bones["{}"].'.format(item.name)
            fcurve_holder=item.id_data
        else:
            base_path=""
            fcurve_holder=item


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
            ks.paths.add(fcurve_holder,base_path+location_name)
        if context.scene.compact_keyframe_insert_menu.use_rotation:
            ks.paths.add(fcurve_holder,base_path+rotation_name)
        if context.scene.compact_keyframe_insert_menu.use_scale:
            ks.paths.add(fcurve_holder,base_path+scale_name)

        if  hasattr(bpy.types.Scene,"free_ik_gv"):gv=bpy.types.Scene.free_ik_gv
        else:gv=None

        if gv and context.scene.compact_keyframe_insert_menu.use_local_rotation:
            if item in gv.nodes_dictionary:
                if gv.nodes_dictionary[item].frame_parent is not None:
                    if item.rotation_mode=='QUATERNION':ks.paths.add(fcurve_holder,base_path+"free_ik_local_quaternion")
                    elif item.rotation_mode=='AXIS_ANGLE':ks.paths.add(fcurve_holder,base_path+"free_ik_local_axis_angle")
                    else:ks.paths.add(fcurve_holder,base_path+"free_ik_local_euler")



register_classes=[CompactKeyframeInsertMenu,Preferences,KeySettings,BUILTIN_KSI_transform,KeyMapOperator,CompactKeyframeInsertMenuInsert,CompactKeyframeInsertMenuChange]



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