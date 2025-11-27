#!/usr/bin/env vtkpython
import glob
import os

import vtk

# ============================================================
# 1. Locate all VTS files to animate
# ============================================================

# UPDATE THIS pattern:
files = sorted(glob.glob("mountain_backcurve40/output.*.vts"))
print("Found frames:", len(files))

# Directory for PNG frames
os.makedirs("frames", exist_ok=True)

# ============================================================
# 2. Read first file to build the pipeline
# ============================================================
reader = vtk.vtkXMLGenericDataObjectReader()
reader.SetFileName(files[0])
reader.Update()
grid = reader.GetOutput()
print("Loaded:", grid.GetClassName())

theta_name = "theta"
theta = grid.GetPointData().GetArray(theta_name)
theta_min, theta_max = theta.GetRange()

# --------------------------------------------
# VEGETATION
# --------------------------------------------
rhof_1_name = "rhof_1"
rhof_1 = grid.GetPointData().GetArray(rhof_1_name)
rhof_1_min, rhof_1_max = rhof_1.GetRange()

# Vegetation contour setup
veg_contour = vtk.vtkContourFilter()
veg_contour.SetInputData(grid)
veg_contour.SetInputArrayToProcess(
    0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, rhof_1_name
)
for i, value in enumerate([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]):
    veg_contour.SetValue(i, value)

veg_mapper = vtk.vtkPolyDataMapper()
veg_mapper.SetInputConnection(veg_contour.GetOutputPort())
veg_mapper.SetScalarModeToUsePointFieldData()
veg_mapper.SelectColorArray(rhof_1_name)
veg_mapper.SetScalarRange(0, 0.6)

# Green LUT
veg_lut = vtk.vtkLookupTable()
veg_lut.SetNumberOfTableValues(256)
veg_lut.SetRange(rhof_1_min, rhof_1_max)
veg_lut.SetHueRange(0.33, 0.33)
veg_lut.SetValueRange(1.0, 0.4)
veg_lut.SetSaturationRange(0.6, 1.0)
veg_lut.Build()
veg_mapper.SetLookupTable(veg_lut)

vegetation_actor = vtk.vtkActor()
vegetation_actor.SetMapper(veg_mapper)

# --------------------------------------------
# FIRE + SMOKE iso creators
# --------------------------------------------
low = theta_min + 2.0
mid = theta_min + 4.0
hi = theta_min + 5.5
higher = theta_min + 7.0
very_hi = theta_min + 25


def make_iso_actor(iso_value, color, opacity):
    contour = vtk.vtkContourFilter()
    contour.SetInputData(grid)
    contour.SetInputArrayToProcess(
        0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, theta_name
    )
    contour.SetValue(0, iso_value)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(contour.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetOpacity(opacity)
    return contour, actor


smoke_contour_low, smoke_actor_low = make_iso_actor(low, (0.7, 0.7, 0.7), 0.15)
smoke_contour_mid, smoke_actor_mid = make_iso_actor(mid, (0.5, 0.5, 0.5), 0.30)
fire_contour_hi, fire_actor_hi = make_iso_actor(hi, (1.0, 0.15, 0.0), 0.60)
fire_contour_higher, fire_actor_higher = make_iso_actor(higher, (1.0, 0.57, 0.05), 0.70)
fire_contour_vhi, fire_actor_vhi = make_iso_actor(very_hi, (1.0, 0.85, 0.0), 0.80)

# --------------------------------------------
# Ground plane
# --------------------------------------------
slice0 = vtk.vtkExtractGrid()
slice0.SetInputData(grid)
slice0.SetVOI(0, 850, 0, 499, 0, 0)
slice0.Update()
ground = slice0.GetOutput()

ground_mapper = vtk.vtkDataSetMapper()
ground_mapper.SetInputData(ground)
ground_mapper.SetScalarVisibility(False)

ground_actor = vtk.vtkActor()
ground_actor.SetMapper(ground_mapper)
ground_actor.GetProperty().SetColor(0, 0, 0)

# --------------------------------------------
# Outline
# --------------------------------------------
outline_filter = vtk.vtkStructuredGridOutlineFilter()
outline_filter.SetInputData(grid)

outline_mapper = vtk.vtkPolyDataMapper()
outline_mapper.SetInputConnection(outline_filter.GetOutputPort())

outline_actor = vtk.vtkActor()
outline_actor.SetMapper(outline_mapper)

# ============================================================
# 3. Renderer / window
# ============================================================
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.2, 0.2, 0.25)
renderer.SetBackground2(0.5, 0.5, 0.6)
renderer.GradientBackgroundOn()

renderer.AddActor(vegetation_actor)
renderer.AddActor(ground_actor)
renderer.AddActor(smoke_actor_low)
renderer.AddActor(smoke_actor_mid)
renderer.AddActor(fire_actor_hi)
renderer.AddActor(fire_actor_higher)
renderer.AddActor(fire_actor_vhi)
renderer.AddActor(outline_actor)

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(900, 700)

# Camera (your saved parameters)
camera = renderer.GetActiveCamera()
camera.SetPosition(1166.9393086976156, -2348.8726187497973, 2780.6186615624197)
camera.SetFocalPoint(101.0, -1.0, 449.6810739215296)
camera.SetViewUp(-0.26897888898416095, 0.6143246476336248, 0.741792143791419)
renderer.ResetCameraClippingRange()

# Transparency settings
render_window.SetAlphaBitPlanes(1)
renderer.SetUseDepthPeeling(1)
renderer.SetMaximumNumberOfPeels(100)
renderer.SetOcclusionRatio(0.1)

# ============================================================
# 4. PNG frame setup
# ============================================================
w2if = vtk.vtkWindowToImageFilter()
w2if.SetInput(render_window)
w2if.ReadFrontBufferOff()

png = vtk.vtkPNGWriter()
png.SetInputConnection(w2if.GetOutputPort())

# ============================================================
# 5. ANIMATION LOOP — update data + render + save PNG
# ============================================================
for frame_id, fname in enumerate(files):
    print(f"Frame {frame_id + 1}/{len(files)} → {fname}")

    reader.SetFileName(fname)
    reader.Update()
    grid = reader.GetOutput()

    # All contours must use the updated grid:
    veg_contour.SetInputData(grid)
    smoke_contour_low.SetInputData(grid)
    smoke_contour_mid.SetInputData(grid)
    fire_contour_hi.SetInputData(grid)
    fire_contour_higher.SetInputData(grid)
    fire_contour_vhi.SetInputData(grid)
    slice0.SetInputData(grid)

    render_window.Render()
    w2if.Modified()

    png.SetFileName(f"frames/frame_{frame_id:05d}.png")
    png.Write()

print("\nDone writing PNG frames!")
print("To create a video, run:")
print("ffmpeg -framerate 30 -i frames/frame_%05d.png -pix_fmt yuv420p output.mp4")
