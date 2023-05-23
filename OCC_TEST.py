from OCC.Display.SimpleGui import init_display
from OCC.Core.STEPControl import STEPControl_Reader


display, start_display, add_menu, add_function_to_menu = init_display()

step_reader = STEPControl_Reader()
status = step_reader.ReadFile("final_assembly.stp")
# if status == IFSelect_RetDone:
step_reader.TransferRoots()
shape = step_reader.Shape()


display.DisplayShape(shape, update=True)
start_display()
