from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.SimpleGui import init_display
import OCC.Core.TopExp as TopExp
import OCC.Core.TopAbs as TopAbs
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


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
    return xmax-xmin, ymax-ymin, zmax-zmin, xmax+xmin, ymax+ymin, zmax+zmin


step_reader = STEPControl_Reader()
status = step_reader.ReadFile("final_assembly.stp")
#if status == IFSelect_RetDone:
step_reader.TransferRoots()
shape = step_reader.Shape()



sub_assemblies = []
sub_assemblies_GeomCent = []
exp = TopExp.TopExp_Explorer(shape, TopAbs.TopAbs_SOLID)
while exp.More():
    current_shape = exp.Current()
    if current_shape.ShapeType() == TopAbs.TopAbs_SOLID:
        sub_assemblies.append(current_shape)
    exp.Next()

for i, sub_assembly in enumerate(sub_assemblies):
    print("Box bounding box computation")
    bb1 = get_boundingbox(sub_assembly)
    print(bb1)
    sub_assemblies_GeomCent.append([bb1[3]/2, bb1[4]/2, bb1[5]/2])

print(sub_assemblies_GeomCent)

display.DisplayShape(shape, update=True)
start_display()
