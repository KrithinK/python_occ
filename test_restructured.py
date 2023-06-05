import math
import time
from multiprocessing import Process
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.SimpleGui import init_display
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_SOLID
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.gp import gp_Pnt, gp_Dir
from OCC.Core.Geom import Geom_Line
from OCC.Extend.ShapeFactory import make_edge
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse

# Set the tolerance for intersection calculations
TOLERANCE = 0.0000001

# Define color codes for console output
class bcolors:
    OKGREEN = '\033[92m'
    OKBLUE = '\033[95m'
    OKCYAN = '\033[96m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Class representing the main program
class BlockIntersectionChecker:
    def __init__(self):
        self.step_reader = STEPControl_Reader()
        self.sub_assemblies = []
        self.bb = None
        self.approach_directions = [(-1, "negative x"), (1, "positive x"), (-1, "negative y"), (1, "positive y"), (-1, "negative z"), (1, "positive z")]

    def load_step_file(self, file_path):
        # Read the STEP file
        status = self.step_reader.ReadFile(file_path)
        self.step_reader.TransferRoots()
        shape = self.step_reader.Shape()

        # Extract sub-assemblies from the shape
        exp = TopExp_Explorer(shape, TopAbs_SOLID)
        while exp.More():
            current_shape = exp.Current()
            if current_shape.ShapeType() == TopAbs_SOLID:
                self.sub_assemblies.append(current_shape)
            exp.Next()

    def get_bounding_box(self, shape, tol=1e-6, use_mesh=True):
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

    def intersect_shape_by_line(self, topods_shape, line, low_parameter=0.0, hi_parameter=float("+inf")):
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

    def check_intersection(self):
        self.bb = self.get_bounding_box(self.sub_assemblies[0])

        for i, direction in self.approach_directions:
            print(bcolors.OKBLUE + "This is the arroach direction of block " + str(i+1) + bcolors.ENDC)
            bb1 = self.get_bounding_box(self.sub_assemblies[i])

            # Create separate processes to check intersections in different directions
            processes = []
            for check_func in [self.check_positive_y, self.check_negative_y, self.check_positive_x, self.check_negative_x, self.check_positive_z, self.check_negative_z]:
                p = Process(target=check_func, args=(bb1,))
                processes.append(p)
                p.start()

            # Wait for all processes to finish
            for p in processes:
                p.join()

            # Fuse the current sub-assembly with the main assembly
            self.sub_assemblies[0] = BRepAlgoAPI_Fuse(self.sub_assemblies[0], self.sub_assemblies[i]).Shape()

    def check_positive_y(self, bb1):
        for j in range(math.floor(bb1[3]), math.ceil(self.bb1[2]), 1):
            p1 = gp_Pnt(math.floor(bb1[0]), j, math.ceil(bb1[5])+5)
            line_dir = gp_Dir(-math.floor(bb1[0]), j, math.ceil(bb1[5])+5)
            my_line = Geom_Line(p1, line_dir).Lin()
            inter = self.intersect_shape_by_line(self.sub_assemblies[0], my_line)
            if inter != "no intersection":
                print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN + "positive y " + bcolors.FAIL + "direction" + bcolors.ENDC)
                return False
        print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN + "positive y " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
        return True
    def check_negative_y(self, bb1):
        pos = True
        for j in range(math.floor(bb1[2]), math.ceil(bb1[3]), -1):
           p1 = gp_Pnt(math.floor(bb1[0]), j, math.ceil(bb1[5])+5)
           line_dir = gp_Dir(-math.floor(bb1[0]), j, math.ceil(bb1[5])+5)
           my_line = Geom_Line(p1, line_dir).Lin()
           inter = self.intersect_shape_by_line(self.sub_assemblies[3], my_line)
           if (inter != "no intersection"):
               pos = False
               break
        if (pos):
           print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
                 "negative y " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
        else:
           print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
                 "negative y " + bcolors.FAIL + "direction" + bcolors.ENDC)
        return pos
    
    
    def check_positive_x(self, bb1):
        pos = True
        for j in range(math.floor(bb1[1]), math.ceil(bb1[0]), 1):
            p1 = gp_Pnt(j, math.floor(bb1[2]), math.ceil(bb1[5])+5)
            line_dir = gp_Dir(j, -math.floor(bb1[2]), math.ceil(bb1[5])+5)
            my_line = Geom_Line(p1, line_dir).Lin()
            inter = self.intersect_shape_by_line(self.sub_assemblies[3], my_line)
            if (inter != "no intersection"):
                pos = False
                break
        if (pos):
            print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
                  "positive x " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
                  "positive x " + bcolors.FAIL + "direction" + bcolors.ENDC)
        return pos
    
    
    def check_negative_x(self, bb1):
        pos = True
        for j in range(math.floor(bb1[0]), math.ceil(bb1[1]), -1):
            p1 = gp_Pnt(j, math.floor(bb1[2]), math.ceil(bb1[5])+5)
            line_dir = gp_Dir(j, -math.floor(bb1[2]), math.ceil(bb1[5])+5)
            my_line = Geom_Line(p1, line_dir).Lin()
            inter = self.intersect_shape_by_line(self.sub_assemblies[3], my_line)
            if (inter != "no intersection"):
                pos = False
                break
        if (pos):
            print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
                  "negative x " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
                  "negative x " + bcolors.FAIL + "direction" + bcolors.ENDC)
        return pos
    
    
    def check_positive_z(self, bb1):
        pos = True
        for j in range(math.floor(bb1[5])+5, math.ceil(bb1[4]), 1):
            p1 = gp_Pnt(0, math.floor(bb1[2]), j)
            line_dir = gp_Dir(0, -math.floor(bb1[2]), j)
            my_line = Geom_Line(p1, line_dir).Lin()
            inter = self.intersect_shape_by_line(self.sub_assemblies[3], my_line)
            if (inter != "no intersection"):
                pos = False
                break
        if (pos):
            print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
                  "positive z " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
                  "positive z " + bcolors.FAIL + "direction" + bcolors.ENDC)
        return pos
    
    
    def check_negative_z(self, bb1):
        pos = True
        for j in range(math.floor(bb1[4]), math.ceil(bb1[5]), -1):
            p1 = gp_Pnt(0, math.floor(bb1[2]), j)
            line_dir = gp_Dir(0, -math.floor(bb1[2]), j)
            my_line = Geom_Line(p1, line_dir).Lin()
            inter = self.intersect_shape_by_line(self.sub_assemblies[3], my_line)
            if (inter != "no intersection"):
                pos = False
                break
        if (pos):
            print(bcolors.OKGREEN + "possible in " + bcolors.OKCYAN +
                  "negative z " + bcolors.OKGREEN + "direction" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "not possible in " + bcolors.OKCYAN +
                  "negative z " + bcolors.FAIL + "direction" + bcolors.ENDC)
        return pos

    # Define other check functions for different directions (negative_y, positive_x, negative_x, positive_z, negative_z)

    def run(self, file_path):
        start = time.time()
        self.load_step_file(file_path)
        self.check_intersection()
        end = time.time()
        print(end - start)


if __name__ == '__main__':
    checker = BlockIntersectionChecker()
    checker.run("pick-up_classic_king-size.stp")
