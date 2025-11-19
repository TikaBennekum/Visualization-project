
# !/usr/bin/env vtkpython
import vtk

# -----------------------
# 1. Read the VTS dataset
# -----------------------
filename = "mountain_backcurve40/output.70000.vts"

reader = vtk.vtkXMLGenericDataObjectReader()
reader.SetFileName(filename)
reader.Update()

grid = reader.GetOutput()

print("Loaded:", grid.GetClassName())

# Name of the scalar field that represents potential temperature
theta_name = "theta"
theta = grid.GetPointData().GetArray("theta")


# --------------------------------------------
# 2. Build isosurfaces for "fire" temperature
#    (flame is roughly 400–800 K per the spec)
# --------------------------------------------
contour = vtk.vtkContourFilter()
contour.SetInputData(grid)
contour.SetInputArrayToProcess(
    0,  # idx
    0,  # port
    0,  # conn
    vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
    theta_name,
)

# A few isovalues in the flame range.
# You can tweak or add/remove values as you like.
theta_min, theta_max = theta.GetRange()

low = theta_min + 1.0       # barely above ambient (~301 K)
mid = theta_min + 5.0
hi  = theta_min + 20.0
very_hi = theta_min + 80.0

isovalues = [low, mid, hi, very_hi]

# isovalues = [450.0, 550.0, 650.0, 750.0, 800, 850, 900, 950, 1000]
for i, value in enumerate(isovalues):
    contour.SetValue(i, value)

# --------------------------
# 3. Mapper & actor for fire
# --------------------------
fire_mapper = vtk.vtkPolyDataMapper()
fire_mapper.SetInputConnection(contour.GetOutputPort())

# Use theta for coloring
fire_mapper.SetScalarModeToUsePointFieldData()
fire_mapper.SelectColorArray(theta_name)
fire_mapper.SetScalarRange(400.0, 800.0)  # color range restricted to flame temps

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
