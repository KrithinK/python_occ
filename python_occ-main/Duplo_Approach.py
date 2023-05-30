from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.SimpleGui import init_display
import OCC.Core.TopExp as TopExp
import OCC.Core.TopAbs as TopAbs
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.gp import gp_Pnt, gp_Dir
from OCC.Core.GC import GC_MakeSegment
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_Line

TOLERANCE = 1e-6


class assert_isdone(object):
    def __init__(self, to_check, error_statement):
        self.to_check = to_check
        self.error_statement = error_statement

    def __enter__(
        self,
    ):
        if self.to_check.IsDone():
            pass
        else:
            raise AssertionError(self.error_statement)

    def __exit__(self, assertion_type, value, traceback):
        pass


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
    return xmax-xmin, ymax-ymin, zmax-zmin, xmax, xmin, ymax, ymin, zmax, zmin


def intersect_shape_by_line(
    topods_shape, line, low_parameter=0.0, hi_parameter=float("+inf")
):
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
        return("no intersection")


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

"""for sub_assembly in sub_assemblies:
    print("Box bounding box computation")
    bb1 = get_boundingbox(sub_assembly)
    print(bb1)"""

print("Box bounding box computation")
bb1 = get_boundingbox(sub_assemblies[3])
print(bb1)

for i in range(0, 100, 1):
    temp = i*(63.416-31.683)/100 + 31.683
    p1 = gp_Pnt(15.866, temp, 19.2)
    line_dir = gp_Dir(-15.866, temp, 20)
    my_line = Geom_Line(p1, line_dir).Lin()
    print(i)
    temp_shape = intersect_shape_by_line(sub_assemblies[3], my_line)
    print(temp_shape)


display, start_display, add_menu, add_function_to_menu = init_display()
display.DisplayShape(temp_shape.Face(1), update=True)
start_display()
