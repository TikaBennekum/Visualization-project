#!/usr/bin/env vtkpython
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
theta = grid.GetPointData().GetArray(theta_name)

theta_min, theta_max = theta.GetRange()
print("theta range:", theta_min, theta_max)

# --------------------------------------------
# 2. Choose isovalues for smoke and fire bands
# --------------------------------------------
# You can tweak these as needed; these are relatively close to theta_min
# so you get a set of nested shells. If you know the range better, feel
# free to shift them.
low      = theta_min + 2.0    # smoke (cool)
mid      = theta_min + 4.0    # smoke (warmer)
hi       = theta_min + 6.0    # fire (hot)
very_hi  = theta_min + 8.0    # fire (very hot)

isovalues = [low, mid, hi, very_hi]

# -------------------------------------------------------
# 3. Helper: build one contour + actor for a single level
# -------------------------------------------------------
def make_iso_actor(grid, theta_name, iso_value, color, opacity):
    contour = vtk.vtkContourFilter()
    contour.SetInputData(grid)
    contour.SetInputArrayToProcess(
        0,  # idx
        0,  # port
        0,  # conn
        vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
        theta_name,
    )
    contour.SetValue(0, iso_value)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(contour.GetOutputPort())
    mapper.ScalarVisibilityOff()  # we are setting solid colors per actor

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetOpacity(opacity)
    actor.GetProperty().SetSpecular(0.2)
    actor.GetProperty().SetDiffuse(0.8)
    actor.GetProperty().SetAmbient(0.1)

    return actor

# ------------------------------------
# 4. Create smoke + fire iso-actors
# ------------------------------------
# Smoke: more translucent, grayish
smoke_actor_low = make_iso_actor(
    grid, theta_name, low,
    color=(0.7, 0.7, 0.7),   # light gray
    opacity=0.15             # very translucent
)

smoke_actor_mid = make_iso_actor(
    grid, theta_name, mid,
    color=(0.5, 0.5, 0.5),   # darker gray
    opacity=0.30             # slightly denser smoke
)

# Fire: more opaque, warm colors
fire_actor_hi = make_iso_actor(
    grid, theta_name, hi,
    color=(1.0, 0.15, 0.0),   # orange-red
    opacity=0.70             # fairly solid
)

fire_actor_very_hi = make_iso_actor(
    grid, theta_name, very_hi,
    color=(1.0, 0.6, 0.05),   # yellow
    opacity=0.95             # almost fully opaque
)

# --------------------------------
# 5. Add a simple domain outline
# --------------------------------
outline_filter = vtk.vtkStructuredGridOutlineFilter()
outline_filter.SetInputData(grid)

outline_mapper = vtk.vtkPolyDataMapper()
outline_mapper.SetInputConnection(outline_filter.GetOutputPort())

outline_actor = vtk.vtkActor()
outline_actor.SetMapper(outline_mapper)
outline_actor.GetProperty().SetColor(1.0, 1.0, 1.0)  # white outline
outline_actor.GetProperty().SetLineWidth(1.0)

# ------------------------------
# 6. Renderer / window / camera
# ------------------------------
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.1, 0.1, 0.15)

# Add actors in a sensible order (smoke behind fire visually)
renderer.AddActor(smoke_actor_low)
renderer.AddActor(smoke_actor_mid)
renderer.AddActor(fire_actor_hi)
renderer.AddActor(fire_actor_very_hi)
renderer.AddActor(outline_actor)

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(900, 700)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Optional: nicer camera
renderer.ResetCamera()
camera = renderer.GetActiveCamera()
camera.Azimuth(30)
camera.Elevation(20)
renderer.ResetCameraClippingRange()

# For better transparency rendering (optional but recommended)
render_window.SetAlphaBitPlanes(1)
renderer.SetUseDepthPeeling(1)
renderer.SetMaximumNumberOfPeels(100)
renderer.SetOcclusionRatio(0.1)

# ------------------------------
# 7. Start interactive rendering
# ------------------------------
render_window.Render()
interactor.Initialize()
interactor.Start()
