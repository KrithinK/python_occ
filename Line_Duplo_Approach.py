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

bb = get_boundingbox(shape)


for i in [1, 2, 0]:
    print(bcolors.OKBLUE + "This is the arroach direction of block " +
          str(i+1) + bcolors.ENDC)
    bb1 = get_boundingbox(sub_assemblies[i])
    pos = True
    for j in range(math.floor(bb1[3]), math.ceil(bb[2]), 1):
        p1 = gp_Pnt(math.floor(bb1[0]), j, math.ceil(bb1[5])+5)
        line_dir = gp_Dir(-math.floor(bb1[0]), j, math.ceil(bb1[5])+5)
        my_line = Geom_Line(p1, line_dir).Lin()
        inter = intersect_shape_by_line(sub_assemblies[3], my_line)
        if (inter != "no intersection"):
            pos = False
            break
    if (pos):
        print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
              "positive y " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
              "positive y " + bcolors.FAIL + "direction" + bcolors.ENDC)
    pos = True
    for j in range(math.floor(bb1[2]), math.ceil(bb[3]), -1):
        p1 = gp_Pnt(math.floor(bb1[0]), j, math.ceil(bb1[5])+5)
        line_dir = gp_Dir(-math.floor(bb1[0]), j, math.ceil(bb1[5])+5)
        my_line = Geom_Line(p1, line_dir).Lin()
        inter = intersect_shape_by_line(sub_assemblies[3], my_line)
        if (inter != "no intersection"):
            pos = False
            break
    if (pos):
        print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
              "negative y " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
              "negative y " + bcolors.FAIL + "direction" + bcolors.ENDC)

    pos = True
    for j in range(math.floor(bb1[1]), math.ceil(bb[0]), 1):
        p1 = gp_Pnt(j, math.floor(bb1[2]), math.ceil(bb1[5])+5)
        line_dir = gp_Dir(j, -math.floor(bb1[2]), math.ceil(bb1[5])+5)
        my_line = Geom_Line(p1, line_dir).Lin()
        inter = intersect_shape_by_line(sub_assemblies[3], my_line)
        if (inter != "no intersection"):
            pos = False
            break
    if (pos):
        print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
              "positive x " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
              "positive x " + bcolors.FAIL + "direction" + bcolors.ENDC)
    pos = True
    for j in range(math.floor(bb1[0]), math.ceil(bb[1]), -1):
        p1 = gp_Pnt(j, math.floor(bb1[2]), math.ceil(bb1[5])+5)
        line_dir = gp_Dir(j, -math.floor(bb1[2]), math.ceil(bb1[5])+5)
        my_line = Geom_Line(p1, line_dir).Lin()
        inter = intersect_shape_by_line(sub_assemblies[3], my_line)
        if (inter != "no intersection"):
            pos = False
            break
    if (pos):
        print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
              "negative x " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
              "negative x " + bcolors.FAIL + "direction" + bcolors.ENDC)

    sub_assemblies[3] = BRepAlgoAPI_Fuse(
        sub_assemblies[3], sub_assemblies[i]).Shape()

end = time.time()
print(end - start)
