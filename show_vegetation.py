# !/usr/bin/env vtkpython

import os

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

# -----------------------------
# Animation: cycle through frames
# -----------------------------
# Build a list of filenames to animate between (inclusive). Adjust start/end/step.
anim_start = 10000
anim_end = 20000
anim_step = 1000
anim_folder = os.path.dirname(filename)
frame_files = []
for t in range(anim_start, anim_end + 1, anim_step):
    fn = os.path.join(anim_folder, f"output.{t}.vts")
    if os.path.exists(fn):
        frame_files.append(fn)

if len(frame_files) == 0:
    print("No animation frames found; running single-frame view.")
    interactor.Start()
else:
    print(f"Animating {len(frame_files)} frames:", frame_files)

    state = {"i": 0, "running": True}

    def timer_callback(obj, event):
        if not state["running"]:
            return
        i = state["i"]
        fn = frame_files[i]
        print("Loading frame:", fn)
        reader.SetFileName(fn)
        reader.Update()
        contour.SetInputData(reader.GetOutput())
        contour.Modified()
        render_window.Render()
        state["i"] = (i + 1) % len(frame_files)

    def keypress(obj, event):
        key = obj.GetKeySym()
        if key == "space":
            state["running"] = not state["running"]
            print("Animation running=" + str(state["running"]))
        if key == "q":
            interactor.DestroyTimer(timer_id)
            interactor.TerminateApp()

    interactor.AddObserver("KeyPressEvent", keypress)
    timer_id = interactor.CreateRepeatingTimer(600)
    interactor.AddObserver("TimerEvent", timer_callback)
    interactor.Start()
