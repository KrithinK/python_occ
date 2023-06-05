from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.SimpleGui import init_display
import OCC.Core.TopExp as TopExp
import OCC.Core.TopAbs as TopAbs
from OCC.Display.SimpleGui import init_display
from OCC.Display.SimpleGui import *




step_reader = STEPControl_Reader()
status = step_reader.ReadFile("pick-up_classic_king-size.stp")
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

for sub_assembly in sub_assemblies:
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.DisplayShape(sub_assembly, update=True)
    start_display()


