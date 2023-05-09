from OCC.Core.gp import gp_Pnt, gp_Dir
from OCC.Core.Geom import Geom_Line
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


p1 = gp_Pnt(0, 0, 0)
line_dir = gp_Dir(1, 1, 0)
my_line = Geom_Line(p1, line_dir).Lin()
my_line = BRepBuilderAPI_MakeEdge(my_line)
my_line.Build()
my_line = my_line.Shape()

display.DisplayShape(my_line, update=True)
start_display()
