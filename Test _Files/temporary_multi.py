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
import math
import time
from multiprocessing import Process
import os
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

start = time.time()
TOLERANCE = 0.0000001


class bcolors:
    OKGREEN = '\033[92m'
    OKBLUE = '\033[95m'
    OKCYAN = '\033[96m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def intersect_shape_by_line(topods_shape, line, low_parameter=0.0, hi_parameter=float("+inf")):
    """
    finds the intersection of a shape and a line
    :param shape: any TopoDS_*
    :param line: gp_Lin
    :param low_parameter:
    :param hi_parameter:
    :return: a list with a number of tuples that corresponds to the number
    of intersections found
    the tuple contains ( gp_Pnt, TopoDS_Face, u,v,w ), respectively the
    intersection point, the intersecting face
    and the u,v,w parameters of the intersection point
    :raise:
    """
    from OCC.Core.IntCurvesFace import IntCurvesFace_ShapeIntersector

    shape_inter = IntCurvesFace_ShapeIntersector()
    shape_inter.Load(topods_shape, TOLERANCE)
    shape_inter.PerformNearest(line, low_parameter, hi_parameter)

    try:
        return (
            shape_inter.Pnt(1),
            shape_inter.Face(1),
            shape_inter.UParameter(1),
            shape_inter.VParameter(1),
            shape_inter.WParameter(1),
        )
    except:
        return ("no intersection")


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


def positive_y(bb1, bb, temp, sub_assembly):
    pos = True
    box1 = temp     # main assembly
    box2 = sub_assembly  # sub assembly
    count = 0
    prev = 10000000000
    for i in range(math.ceil(bb[2]-bb1[3])):
        move = gp_Trsf()
        move.SetTranslation(gp_Vec(0, i, 0))
        box2 = BRepBuilderAPI_Transform(
            box2, move, True).Shape()

        # Create meshes for the proximity algorithm
        deflection = 1e-3
        mesher1 = BRepMesh_IncrementalMesh(box1, deflection)
        mesher2 = BRepMesh_IncrementalMesh(box2, deflection)
        mesher1.Perform()
        mesher2.Perform()

        # Perform shape proximity check
        tolerance = 0
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
        # print(i)
        # print(len(shape_1_faces))
        if (len(shape_1_faces) == 0):
            count += 1
        if (count == 2):
            break
        if (len(shape_1_faces) > prev):
            pos = False
            break
        prev = len(shape_1_faces)
    if (pos):
        print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
              "positive y " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
              "positive y " + bcolors.FAIL + "direction" + bcolors.ENDC)
    return pos


def negative_y(bb1, bb, temp, sub_assembly):
    pos = True
    box1 = temp     # main assembly
    box2 = sub_assembly  # sub assembly
    count = 0
    prev = 10000000000
    for i in range(-math.ceil(bb[3]-bb1[2])):
        move = gp_Trsf()
        move.SetTranslation(gp_Vec(0, -i, 0))
        box2 = BRepBuilderAPI_Transform(
            box2, move, True).Shape()

        # Create meshes for the proximity algorithm
        deflection = 1e-3
        mesher1 = BRepMesh_IncrementalMesh(box1, deflection)
        mesher2 = BRepMesh_IncrementalMesh(box2, deflection)
        mesher1.Perform()
        mesher2.Perform()

        # Perform shape proximity check
        tolerance = 0
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
        # print(i)
        # print(len(shape_1_faces))
        if (len(shape_1_faces) == 0):
            count += 1
        if (count == 2):
            break
        if (len(shape_1_faces) > prev):
            pos = False
            break
        prev = len(shape_1_faces)
    if (pos):
        print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
              "negative y " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
              "negative y " + bcolors.FAIL + "direction" + bcolors.ENDC)
    return pos


def positive_x(bb1, bb, temp, sub_assembly):
    pos = True
    box1 = temp     # main assembly
    box2 = sub_assembly  # sub assembly
    count = 0
    prev = 10000000000
    for i in range(math.ceil(bb[0]-bb1[1])):
        move = gp_Trsf()
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
        tolerance = 0
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
        # print(i)
        # print(len(shape_1_faces))
        if (len(shape_1_faces) == 0):
            count += 1
        if (count == 2):
            break
        if (len(shape_1_faces) > prev):
            pos = False
            break
        prev = len(shape_1_faces)
    if (pos):
        print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
              "positive x " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
              "positive x " + bcolors.FAIL + "direction" + bcolors.ENDC)
    return pos


def negative_x(bb1, bb, temp, sub_assembly):
    pos = True
    box1 = temp     # main assembly
    box2 = sub_assembly  # sub assembly
    count = 0
    prev = 10000000000
    for i in range(-math.ceil(bb[1]-bb1[0])):
        move = gp_Trsf()
        move.SetTranslation(gp_Vec(-i, 0, 0))
        box2 = BRepBuilderAPI_Transform(
            box2, move, True).Shape()

        # Create meshes for the proximity algorithm
        deflection = 1e-3
        mesher1 = BRepMesh_IncrementalMesh(box1, deflection)
        mesher2 = BRepMesh_IncrementalMesh(box2, deflection)
        mesher1.Perform()
        mesher2.Perform()

        # Perform shape proximity check
        tolerance = 0
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
        # print(i)
        # print(len(shape_1_faces))
        if (len(shape_1_faces) == 0):
            count += 1
        if (count == 2):
            break
        if (len(shape_1_faces) > prev):
            pos = False
            break
        prev = len(shape_1_faces)
    if (pos):
        print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
              "negative x " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
              "negative x " + bcolors.FAIL + "direction" + bcolors.ENDC)
    return pos


def positive_z(bb1, bb, temp, sub_assembly):
    pos = True
    box1 = temp     # main assembly
    box2 = sub_assembly  # sub assembly
    count = 0
    prev = 10000000000
    for i in range(math.ceil(bb[4]-bb1[5])):
        move = gp_Trsf()
        move.SetTranslation(gp_Vec(0, 0, i))
        box2 = BRepBuilderAPI_Transform(
            box2, move, True).Shape()

        # Create meshes for the proximity algorithm
        deflection = 1e-3
        mesher1 = BRepMesh_IncrementalMesh(box1, deflection)
        mesher2 = BRepMesh_IncrementalMesh(box2, deflection)
        mesher1.Perform()
        mesher2.Perform()

        # Perform shape proximity check
        tolerance = 0
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
        # print(i)
        # print(len(shape_1_faces))
        if (len(shape_1_faces) == 0):
            count += 1
        if (count == 2):
            break
        if (len(shape_1_faces) >= prev):
            pos = False
            break
        prev = len(shape_1_faces)
    if (pos):
        print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
              "positive z " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
              "positive z " + bcolors.FAIL + "direction" + bcolors.ENDC)
    return pos


def negative_z(bb1, bb, temp, sub_assembly):
    pos = True
    box1 = temp     # main assembly
    box2 = sub_assembly  # sub assembly
    count = 0
    prev = 10000000000
    for i in range(-math.ceil(bb[5]-bb1[4])):
        move = gp_Trsf()
        move.SetTranslation(gp_Vec(0, 0, -i))
        box2 = BRepBuilderAPI_Transform(
            box2, move, True).Shape()

        # Create meshes for the proximity algorithm
        deflection = 1e-3
        mesher1 = BRepMesh_IncrementalMesh(box1, deflection)
        mesher2 = BRepMesh_IncrementalMesh(box2, deflection)
        mesher1.Perform()
        mesher2.Perform()

        # Perform shape proximity check
        tolerance = 0
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
        # print(i)
        # print(len(shape_1_faces))
        if (len(shape_1_faces) == 0):
            count += 1
        if (count == 2):
            break
        if (len(shape_1_faces) > prev):
            pos = False
            break
        prev = len(shape_1_faces)
    if (pos):
        print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
              "negative z " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
              "negative z " + bcolors.FAIL + "direction" + bcolors.ENDC)
    return pos


def end_time():
    end = time.time()
    print(end - start)


def allDirections(final, sub, i):
    print(bcolors.OKBLUE + "This is the arroach direction of block " +
          str(i) + bcolors.ENDC)
    bb1 = get_boundingbox(sub)
    bb = get_boundingbox(final)
    pos_posy = Process(target=positive_y, args=(
        bb1, bb, final, sub))
    pos_negy = Process(target=negative_y, args=(
        bb1, bb, final, sub))
    pos_posx = Process(target=positive_x, args=(
        bb1, bb, final, sub))
    pos_negx = Process(target=negative_x, args=(
        bb1, bb, final, sub))
    pos_posz = Process(target=positive_z, args=(
        bb1, bb, final, sub))
    pos_negz = Process(target=negative_z, args=(
        bb1, bb, final, sub))

    pos_posy.start()
    pos_negy.start()
    pos_posx.start()
    pos_negx.start()
    pos_posz.start()
    pos_negz.start()

    pos_posy.join()
    pos_negy.join()
    pos_posx.join()
    pos_negx.join()
    pos_posz.join()
    pos_negz.join()


if __name__ == '__main__':
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(
        os.getcwd()[:-12]+"/Assets/pick-up_classic_king-size.stp")
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

    temp = sub_assemblies[0]
    sub_assemblies_cummul = []
    sub_assemblies_reorder = []
    sub_assemblies_cummul.append(sub_assemblies[0])
    sub_assemblies_reorder.append(sub_assemblies[0])
    bb = get_boundingbox(temp)
    counter = 1
    Processes = []

    for i in [5, 6, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]:
        sub_assemblies_cummul.append(BRepAlgoAPI_Fuse(
            sub_assemblies_cummul[len(sub_assemblies_cummul)-1], sub_assemblies[i]).Shape())
        sub_assemblies_reorder.append(sub_assemblies[i])

    for i in range(len(sub_assemblies_cummul)):
        p = Process(target=allDirections, args=(
            sub_assemblies_cummul[i-1], sub_assemblies_reorder[i], counter))
        counter += 1
        p.start()
        Processes.append(p)

    for process in Processes:
        process.join()

    end_time()
