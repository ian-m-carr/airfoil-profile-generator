# Variable: bl_info
# Contains informations for Blender to recognize and categorize the addon.
bl_info = {
    "name": "Generate an airfoil profile mesh",
    "description": "Creates a mesh containing a single vertex path following a parameterized airfoil path",
    "author": "I.M Carr",
    "version": (1, 0, 0),
    "blender": (3, 4, 1),
    "category": "Object",
}

import bpy
import bmesh
from bpy_extras import object_utils
from bpy.props import FloatProperty, IntProperty, EnumProperty
from . import naca_mod


def add_box(width, height, depth):
    """
    This function takes inputs and returns vertex and face arrays.
    no actual mesh data creation is done here.
    """

    verts = [
        (+1.0, +1.0, -1.0),
        (+1.0, -1.0, -1.0),
        (-1.0, -1.0, -1.0),
        (-1.0, +1.0, -1.0),
        (+1.0, +1.0, +1.0),
        (+1.0, -1.0, +1.0),
        (-1.0, -1.0, +1.0),
        (-1.0, +1.0, +1.0),
    ]

    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (4, 0, 3, 7),
    ]

    # apply size
    for i, v in enumerate(verts):
        verts[i] = v[0] * width, v[1] * depth, v[2] * height

    return verts, faces


class AddNACA5Modified(bpy.types.Operator, object_utils.AddObjectHelper):
    """Add a NACA 5 digit (modified) parameterized airfoil mesh"""
    bl_idname = "mesh.airfoil_add"
    bl_label = "NACA 5 digit (modified) airfoil mesh"
    bl_options = {'REGISTER', 'UNDO'}

    num_points: IntProperty(
        name="Points per surface",
        description="Number of points to generate per surface",
        min=2, max=1000,
        default=40
    )
    point_spacing: EnumProperty(
        name="Point distribution algorithm",
        description="How to distribute the generated points",
        items=(
            ("1", "Equal spacing", "", 1),
            ("2", "Half Cosine With Smaller Increments Near Leading edge", "", 2),
            ("3", "Half Cosine With Smaller Increments Near 1", "", 3),
            ("4", "Full Cosine", "", 4)
        ),
        default=4
    )
    chord_length: FloatProperty(
        name="Chord length",
        description="The length of the airfoil chord to generate (meters)",
        min=0.0, max=10,
        default=1.0,
    )
    lift_coefficient: IntProperty(
        name="NACA5 Digit 1",
        description="Digit 1, Design lift coefficient * 20/3 (2 == 0.3 Cl)",
        min=0, max=20,
        default=2
    )
    max_camber_pos: IntProperty(
        name="NACA5 Digit 2",
        description="Digit 2, The position of maximum camber divided by .05 (3 == 0.15 or 15% of chord)",
        min=0, max=20,
        default=3
    )
    camber_curve_type: EnumProperty(
        name="NACA5 Digit 3",
        description="Digit 3, a single digit indicating whether the camber is simple (S = 0) or reflex (S = 1)",
        items=(
            ("0", "0: Simple", "", 0),
            ("1", "1: Reflex", "", 1)
        ),
        default=0
    )
    max_thickness_pct: IntProperty(
        name="NACA5 Digits 4/5",
        description="Digits 4/5, the maximum thickness in percent of chord",
        min=0, max=100,
        default=18
    )
    lead_edge_radius: IntProperty(
        name="NACA5 mod Digit 1",
        description="Modifier Digit 1, leading edge radius [6:default, 0:sharp, >6:larger radius]",
        min=0, max=10,
        default=6
    )
    max_thickness_pos: IntProperty(
        name="NACA5 mod Digit 2",
        description="Modifier Digit 1, position in 1/10 of chord of maximum thickness (from leading edge) default 30%",
        min=0, max=10,
        default=3
    )
    lead_edge_droop: FloatProperty(
        name="Leading Edge droop",
        description="Leading edge droop max",
        min=0.0, max=1.0,
        default=0.0,
    )
    lead_edge_droop_pos: FloatProperty(
        name="Leading Edge droop 0 distance",
        description="Position in 1/10 of chord where leading edge droop becomes 0 (from leading edge)",
        min=0.0, max=1.0,
        default=0.0,
    )

    def execute(self, context):
        # create the airfoil generator
        af = naca_5_mod.NACA5Modified(self.num_points)

        # and set it's spacing
        af.set_coord_spacing(int(self.point_spacing))

        # calculate the profile
        af.naca_five_modified(self.lift_coefficient, self.max_camber_pos, int(self.camber_curve_type),
                              self.max_thickness_pct, self.lead_edge_radius, self.max_thickness_pos,
                              self.lead_edge_droop, self.lead_edge_droop_pos)

        verts_loc, edges = af.get_profile_verts_and_edges(self.chord_length)

        mesh = bpy.data.meshes.new("Airfoil")

        bm = bmesh.new()

        for v_co in verts_loc:
            bm.verts.new(v_co)

        bm.verts.ensure_lookup_table()

        for edge in edges:
            bm.edges.new((bm.verts[edge[0]], bm.verts[edge[1]]))

        bm.to_mesh(mesh)
        mesh.update()

        # add the mesh as an object into the scene with this utility module
        object_utils.object_data_add(context, mesh, operator=self)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddNACA5Modified.bl_idname, icon='MESH_CUBE')


def register():
    bpy.utils.register_class(AddNACA5Modified)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)  # Adds the new operator to an existing menu.


def unregister():
    bpy.utils.unregister_class(AddNACA5Modified)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
