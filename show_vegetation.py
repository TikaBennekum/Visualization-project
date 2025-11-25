# !/usr/bin/env vtkpython

import math
import os

import vtk

# -----------------------
# 1. Read the VTS dataset
# -----------------------
filename = "mountain_backcurve40/output.10000.vts"

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


# Key handler to print current camera parameters (position, focal point, view up)
# and derived azimuth/elevation relative to the focal point. Press 'p' while
# the interactor has focus to print values to the console.
def print_camera_params(obj, event):
    key = obj.GetKeySym()
    if key != "p":
        return
    cam = renderer.GetActiveCamera()
    pos = cam.GetPosition()
    fp = cam.GetFocalPoint()
    vu = cam.GetViewUp()
    dx = pos[0] - fp[0]
    dy = pos[1] - fp[1]
    dz = pos[2] - fp[2]
    horiz_dist = math.hypot(dx, dy)
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
    # Azimuth: angle in XY plane from +X toward +Y
    azimuth = math.degrees(math.atan2(dy, dx))
    # Elevation: angle above the XY plane
    elevation = math.degrees(math.atan2(dz, horiz_dist))
    print("\nCamera parameters:")
    print(f"  Position: {pos}")
    print(f"  FocalPoint: {fp}")
    print(f"  ViewUp: {vu}")
    print(f"  Distance: {dist:.3f}")
    print(f"  Azimuth (deg): {azimuth:.3f}")
    print(f"  Elevation (deg): {elevation:.3f}\n")


interactor.AddObserver("KeyPressEvent", print_camera_params)

# Optional: set camera to a saved position (from user)
camera = renderer.GetActiveCamera()
# User-provided camera parameters
camera.SetPosition(1166.9393086976156, -2348.8726187497973, 2780.6186615624197)
camera.SetFocalPoint(101.0, -1.0, 449.6810739215296)
camera.SetViewUp(-0.26897888898416095, 0.6143246476336248, 0.741792143791419)
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
