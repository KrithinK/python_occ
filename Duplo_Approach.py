from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.SimpleGui import init_display
import OCC.Core.TopExp as TopExp
import OCC.Core.TopAbs as TopAbs
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh


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
    return xmax-xmin, ymax-ymin, zmax-zmin


step_reader = STEPControl_Reader()
status = step_reader.ReadFile("final_assembly.stp")
#if status == IFSelect_RetDone:
step_reader.TransferRoots()
shape = step_reader.Shape()



sub_assemblies = []
exp = TopExp.TopExp_Explorer(shape, TopAbs.TopAbs_SOLID)
while exp.More():
    current_shape = exp.Current()
    if current_shape.ShapeType() == TopAbs.TopAbs_SOLID:
        sub_assemblies.append(current_shape)
    exp.Next()

for sub_assembly in sub_assemblies:
    print("Box bounding box computation")
    bb1 = get_boundingbox(sub_assembly)
    print(bb1)


print("Box bounding box computation")
bb1 = get_boundingbox(shape)
print(bb1)






sub_assemblies_faces = []
exp = TopExp.TopExp_Explorer(sub_assemblies[0], TopAbs.TopAbs_FACE)
while exp.More():
    current_face = exp.Current()
    if current_face.ShapeType() == TopAbs.TopAbs_FACE:
        sub_assemblies_faces.append(current_face)
    exp.Next()

print(len(sub_assemblies_faces))
print(len(sub_assemblies))

display, start_display, add_menu, add_function_to_menu = init_display()
display.DisplayShape(sub_assemblies_faces[0], update=True)
start_display()