# !/usr/bin/env vtkpython
import vtk

# -----------------------
# 1. Read the VTS dataset
# -----------------------
filename = "mountain_backcurve40/output.50000.vts"

reader = vtk.vtkXMLGenericDataObjectReader()
reader.SetFileName(filename)
reader.Update()

grid = reader.GetOutput()

print("Loaded:", grid.GetClassName())

# Name of the scalar field that represents potential temperature
rhof_1_name = "rhof_1"
rhof_1 = grid.GetPointData().GetArray("rhof_1")

# --------------------------------------------
# 2. Build isosurfaces for "vegetation" density
#    (vegetation is roughly 0.1–0.6 per the spec)
# --------------------------------------------
contour = vtk.vtkContourFilter()
contour.SetInputData(grid)
contour.SetInputArrayToProcess(
    0,  # idx
    0,  # port
    0,  # conn
    vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
    rhof_1_name,
)

# A few isovalues in the flame range.
# You can tweak or add/remove values as you like.
rhof_1_min, rhof_1_max = rhof_1.GetRange()

isovalues = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

for i, value in enumerate(isovalues):
    contour.SetValue(i, value)

# --------------------------
# 3. Mapper & actor for fire
# --------------------------
fire_mapper = vtk.vtkPolyDataMapper()
fire_mapper.SetInputConnection(contour.GetOutputPort())

# Use rhof_1 for coloring
fire_mapper.SetScalarModeToUsePointFieldData()
fire_mapper.SelectColorArray(rhof_1_name)
fire_mapper.SetScalarRange(0, 0.6)  # color range restricted to vegetation

fire_actor = vtk.vtkActor()
fire_actor.SetMapper(fire_mapper)

# --------------------------------
# 4. Add a simple domain outline
# --------------------------------
outline_filter = vtk.vtkStructuredGridOutlineFilter()
outline_filter.SetInputData(grid)

outline_mapper = vtk.vtkPolyDataMapper()
outline_mapper.SetInputConnection(outline_filter.GetOutputPort())

outline_actor = vtk.vtkActor()
outline_actor.SetMapper(outline_mapper)
outline_actor.GetProperty().SetColor(1.0, 1.0, 1.0)  # white outline

# ------------------------------
# 5. Renderer / window / camera
# ------------------------------
renderer = vtk.vtkRenderer()
renderer.AddActor(fire_actor)
renderer.AddActor(outline_actor)
renderer.SetBackground(0.1, 0.1, 0.15)

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(900, 700)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Optional: a slightly nicer camera position
renderer.ResetCamera()
camera = renderer.GetActiveCamera()
camera.Azimuth(30)
camera.Elevation(20)
renderer.ResetCameraClippingRange()

# ------------------------------
# 6. Start interactive rendering
# ------------------------------
render_window.Render()
interactor.Initialize()
interactor.Start()
