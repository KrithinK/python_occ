from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.SimpleGui import init_display
import OCC.Core.TopExp as TopExp
import OCC.Core.TopAbs as TopAbs
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Display.SimpleGui import init_display
from OCC.Display.SimpleGui import *
from OCC.Core.gp import gp_Pnt, gp_Dir
from OCC.Core.Geom import Geom_Line
from OCC.Extend.ShapeFactory import make_edge
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse


def fuse(self, toFuse):
    """
    Fuse shapes together
    """

    fuse_op = BRepAlgoAPI_Fuse(self.wrapped, toFuse.wrapped)
    fuse_op.RefineEdges()
    fuse_op.FuseEdges()
    # fuse_op.SetFuzzyValue(TOLERANCE)
    fuse_op.Build()


step_reader = STEPControl_Reader()
status = step_reader.ReadFile("final_assembly.stp")
# if status == IFSelect_RetDone:
step_reader.TransferRoots()
shape = step_reader.Shape()


sub_assemblies = []
exp = TopExp.TopExp_Explorer(shape, TopAbs.TopAbs_SOLID)
while exp.More():
    current_shape = exp.Current()
    if current_shape.ShapeType() == TopAbs.TopAbs_SOLID:
        sub_assemblies.append(current_shape)
    exp.Next()

sub_assemblies[3] = BRepAlgoAPI_Fuse(
    sub_assemblies[3], sub_assemblies[1]).Shape()

display, start_display, add_menu, add_function_to_menu = init_display()
display.DisplayShape(sub_assemblies[3], update=True)
start_display()
