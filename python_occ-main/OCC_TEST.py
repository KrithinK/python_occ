from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.BRepClass3d import BRepClass3d_SolidClassifier
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopAbs import TopAbs_ON, TopAbs_OUT, TopAbs_IN


def get_boundingbox(shape, tol=1e-6, use_mesh=True):
    """return the bounding box of the TopoDS_Shape `shape`
    Parameters
    ----------
    shape : TopoDS_Shape or a subclass such as TopoDS_Face
        the shape to compute the bounding box from
    tol: float
        tolerance of the computed boundingbox
    use_mesh : bool
        a flag that tells whether or not the shape has first to be meshed before the bbox
        computation. This produces more accurate results
    """
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
    return xmax, ymax, zmax


def point_in_solid(solid, pnt, tolerance=1e-5):
    """returns True if *pnt* lies in *solid*, False if not
    Args:
        solid   TopoDS_Solid
        pnt:    gp_Pnt
    Returns: bool
    """
    from OCC.Core.BRepClass3d import BRepClass3d_SolidClassifier
    from OCC.Core.TopAbs import TopAbs_ON, TopAbs_OUT, TopAbs_IN

    _in_solid = BRepClass3d_SolidClassifier(solid, pnt, tolerance)
    print("State", _in_solid.State())
    if _in_solid.State() == TopAbs_ON:
        return None, "on"
    if _in_solid.State() == TopAbs_OUT:
        return False, "out"
    if _in_solid.State() == TopAbs_IN:
        return True, "in"


print("debug")
step_reader = STEPControl_Reader()
status = step_reader.ReadFile(
    "E:\programming\python\Python_OCC\python_occ-main\Duplo_Approach\final_assembly.stp")
# if status == IFSelect_RetDone:
step_reader.TransferRoots()
shape = step_reader.Shape()

print("Box bounding box computation")
bb1 = get_boundingbox(shape)
print(bb1)

test_point = gp_Pnt(0, 0, 0)
answer = point_in_solid(shape, test_point)
print(answer)
