from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.SimpleGui import init_display
import OCC.Core.TopExp as TopExp
import OCC.Core.TopAbs as TopAbs
from OCC.Display.SimpleGui import init_display
from OCC.Display.SimpleGui import *
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepBndLib import brepbndlib_Add


def get_boundingbox(shape, tol=1e-6, use_mesh=True):
    bbox = Bnd_Box()
    bbox.SetGap(tol)
    if use_mesh:
        mesh = BRepMesh_IncrementalMesh()
        mesh.SetParallelDefault(True)
        mesh.SetShape(shape)
        mesh.Perform()
        if not mesh.IsDone():
            raise AssertionError("Mesh not done.")
    brepbndlib_Add(shape, bbox, use_mesh)

    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    return xmax, xmin, ymax, ymin, zmax, zmin


step_reader = STEPControl_Reader()
status = step_reader.ReadFile(
    "E:\programming\python\Python_OCC\python_occ\Assets\pick-up_classic_king-size.stp")
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

print(len(sub_assemblies))

temp = BRepAlgoAPI_Fuse(
    sub_assemblies[0], sub_assemblies[5]).Shape()

print(get_boundingbox(sub_assemblies[0]))
print(get_boundingbox(temp))

# for sub_assembly in sub_assemblies:
# display, start_display, add_menu, add_function_to_menu = init_display()
# display.DisplayShape(temp, update=True)
# start_display()
