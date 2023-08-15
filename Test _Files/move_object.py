from math import atan, cos, sin, pi

from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_Transform,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
)
from OCC.Core.BRepFeat import BRepFeat_MakeCylindricalHole
from OCC.Core.BRepPrimAPI import (
    BRepPrimAPI_MakeSphere,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeTorus,
    BRepPrimAPI_MakeRevol,
)
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Ax1, gp_Trsf, gp_Vec

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


def boolean_cut(base):
    # Create a cylinder
    cylinder_radius = 0.25
    cylinder_height = 2.0
    cylinder_origin = gp_Ax2(
        gp_Pnt(0.0, 0.0, -cylinder_height / 2.0), gp_Dir(0.0, 0.0, 1.0)
    )
    cylinder = BRepPrimAPI_MakeCylinder(
        cylinder_origin, cylinder_radius, cylinder_height
    )

    # Repeatedly move and subtract it from the input shape
    move = gp_Trsf()
    boolean_result = base
    clone_radius = 0.5

    for clone in range(8):
        angle = clone * pi / 4.0
        # Move the cylinder
        move.SetTranslation(
            gp_Vec(cos(angle) * clone_radius, sin(angle) * clone_radius, 0.0)
        )
        moved_cylinder = BRepBuilderAPI_Transform(
            cylinder.Shape(), move, True).Shape()
        # Subtract the moved cylinder from the drilled sphere
        boolean_result = BRepAlgoAPI_Cut(
            boolean_result, moved_cylinder).Shape()
    return boolean_result


shape = boolean_cut(BRepPrimAPI_MakeSphere(1.0).Shape())
display.DisplayShape(shape, update=True)
start_display()
