import os
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepExtrema import BRepExtrema_ShapeProximity
from OCC.Display.SimpleGui import init_display
from OCC.Core.STEPControl import STEPControl_Reader
import OCC.Core.TopExp as TopExp
import OCC.Core.TopAbs as TopAbs
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_Transform,
)

step_reader = STEPControl_Reader()
status = step_reader.ReadFile(os.getcwd()[:-12]+"/Assets/final_assembly.stp")
print(os.getcwd()[:-12]+"/Assets/final_assembly.stp")
# if status == IFSelect_RetDone:
step_reader.TransferRoots()
shape = step_reader.Shape()

move = gp_Trsf()

sub_assemblies = []
exp = TopExp.TopExp_Explorer(shape, TopAbs.TopAbs_SOLID)
while exp.More():
    current_shape = exp.Current()
    if current_shape.ShapeType() == TopAbs.TopAbs_SOLID:
        sub_assemblies.append(current_shape)
    exp.Next()


# create two boxes that intersect
box1 = sub_assemblies[3]
box2 = sub_assemblies[0]

for i in range(1):
    move.SetTranslation(gp_Vec(i, 0, 0))
    box2 = BRepBuilderAPI_Transform(
        box2, move, True).Shape()

    # Create meshes for the proximity algorithm
    deflection = 1e-3
    mesher1 = BRepMesh_IncrementalMesh(box1, deflection)
    mesher2 = BRepMesh_IncrementalMesh(box2, deflection)
    mesher1.Perform()
    mesher2.Perform()

    # Perform shape proximity check
    tolerance = 0.0001
    isect_test = BRepExtrema_ShapeProximity(box1, box2, tolerance)
    isect_test.Perform()

    # Get intersecting faces from Shape1
    overlaps1 = isect_test.OverlapSubShapes1()
    face_indices1 = overlaps1.Keys()
    shape_1_faces = []
    for ind in face_indices1:
        face = isect_test.GetSubShape1(ind)
        shape_1_faces.append(face)

    # Get intersecting faces from Shape2
    overlaps2 = isect_test.OverlapSubShapes2()
    face_indices2 = overlaps2.Keys()
    shape_2_faces = []
    for ind in face_indices2:
        face = isect_test.GetSubShape2(ind)
        shape_2_faces.append(face)
    print(i)
    print(len(shape_1_faces))

    display, start_display, add_menu, add_function_to_menu = init_display()
    display.DisplayShape(box1, transparency=0.5)
    display.DisplayShape(box2, transparency=0.5)
    display.DisplayShape(shape_1_faces + shape_2_faces, color="RED")

    display.FitAll()
    start_display()
