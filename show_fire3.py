#!/usr/bin/env vtkpython
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
theta_name = "theta"
theta = grid.GetPointData().GetArray(theta_name)

theta_min, theta_max = theta.GetRange()
print("theta range:", theta_min, theta_max)

# --------------------------------------------
# 2. VEGETATION
# --------------------------------------------

# Name of the scalar field that represents vegetation
rhof_1_name = "rhof_1"
rhof_1 = grid.GetPointData().GetArray("rhof_1")

contour = vtk.vtkContourFilter()
contour.SetInputData(grid)
contour.SetInputArrayToProcess(
    0,  # idx
    0,  # port
    0,  # conn
    vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
    rhof_1_name,
)

# A few isovalues in the vegetation range.
rhof_1_min, rhof_1_max = rhof_1.GetRange()

isovalues = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

for i, value in enumerate(isovalues):
    contour.SetValue(i, value)

    vegetation_mapper = vtk.vtkPolyDataMapper()
vegetation_mapper.SetInputConnection(contour.GetOutputPort())

# Use rhof_1 for coloring
vegetation_mapper.SetScalarModeToUsePointFieldData()
vegetation_mapper.SelectColorArray(rhof_1_name)
vegetation_mapper.SetScalarRange(0, 0.6)  # color range restricted to vegetation

# Create a green lookup table for the contour mapper so we can show a colorbar
lut = vtk.vtkLookupTable()
lut.SetNumberOfTableValues(256)
lut.SetRange(rhof_1_min, rhof_1_max)

lut.SetHueRange(0.33, 0.33)  # pure green
lut.SetValueRange(1.0, 0.4)  # brightness: light -> dark (adjusted too)
lut.SetSaturationRange(0.6, 1.0)  # avoid pale/white low saturation
lut.Build()

vegetation_mapper.SetLookupTable(lut)
vegetation_mapper.SetUseLookupTableScalarRange(True)
vegetation_mapper.ScalarVisibilityOn()

vegetation_actor = vtk.vtkActor()
vegetation_actor.SetMapper(vegetation_mapper)

# --------------------------------------------
# 2. FIRE AND SMOKE values to colors
# --------------------------------------------
low = theta_min + 2.0  # smoke (cool)
mid = theta_min + 4.0  # smoke (warmer)
hi = theta_min + 5.5  # fire (hot)
higher = theta_min + 7.0  # fire (hotter)
very_hi = theta_min + 25  # fire (very hot)

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
# Create a color lookup table for the contour mapper so we can show a colorbar
fire_lut = vtk.vtkLookupTable()
fire_lut.SetNumberOfTableValues(4)
fire_lut.SetRange(low, very_hi)
fire_lut.Build()

# Assign colors to your levels: smoke low → smoke mid → fire → very hot
fire_colors = [
    (0.7, 0.7, 0.7),  # light gray
    (0.5, 0.5, 0.5),  # dark gray
    (1.0, 0.15, 0.0),  # orange-red
    (1.0, 0.6, 0.05),  # yellow
]

for i, color in enumerate(fire_colors):
    fire_lut.SetTableValue(i, *color, 1.0)  # RGB + alpha


# Smoke: more translucent, grayish
smoke_actor_low = make_iso_actor(
    grid,
    theta_name,
    low,
    color=(0.7, 0.7, 0.7),  # light gray
    opacity=0.15,  # very translucent
)

smoke_actor_mid = make_iso_actor(
    grid,
    theta_name,
    mid,
    color=(0.5, 0.5, 0.5),  # darker gray
    opacity=0.30,  # slightly denser smoke
)

# Fire: more opaque, warm colors
fire_actor_hi = make_iso_actor(
    grid,
    theta_name,
    hi,
    color=(1.0, 0.15, 0.0),  # red
    opacity=0.60,  # fairly solid
)

fire_actor_higher = make_iso_actor(
    grid,
    theta_name,
    higher,
    color=(1.0, 0.57, 0.05),  # orange
    opacity=0.70,  # fairly solid
)


fire_actor_very_hi = make_iso_actor(
    grid,
    theta_name,
    very_hi,
    color=(1.0, 0.85, 0.0),  # yellow
    opacity=0.80,  # almost fully opaque
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
renderer.AddActor(fire_actor_higher)
renderer.AddActor(fire_actor_very_hi)
renderer.AddActor(outline_actor)
renderer.AddActor(vegetation_actor)

# Add a scalar bar (color legend) for vegetation
scalar_bar = vtk.vtkScalarBarActor()
scalar_bar.SetLookupTable(lut)
scalar_bar.SetTitle("Vegetation density")
scalar_bar.SetNumberOfLabels(5)
scalar_bar.SetOrientationToVertical()
scalar_bar.SetPosition(0.88, 0.1)
scalar_bar.SetWidth(0.08)
scalar_bar.SetHeight(0.8)
scalar_bar.UnconstrainedFontSizeOn()

# Increase font sizes for better readability
title_prop = scalar_bar.GetTitleTextProperty()
title_prop.SetFontSize(24)  # increase font size
title_prop.SetBold(True)
title_prop.SetColor(1.0, 1.0, 1.0)  # white text (optional)
title_prop.SetFontFamilyToArial()

label_prop = scalar_bar.GetLabelTextProperty()
label_prop.SetFontFamilyToArial()
label_prop.SetBold(True)
label_prop.SetFontSize(24)  # larger labels
label_prop.SetColor(1, 1, 1)

renderer.AddViewProp(scalar_bar)

# Add a scalar bar (color legend) for temperature
temp_scalar_bar = vtk.vtkScalarBarActor()
temp_scalar_bar.SetLookupTable(fire_lut)
temp_scalar_bar.SetTitle("Temperature")
temp_scalar_bar.SetNumberOfLabels(4)
temp_scalar_bar.SetOrientationToVertical()
temp_scalar_bar.SetPosition(0.12, 0.1)
temp_scalar_bar.SetWidth(0.08)
temp_scalar_bar.SetHeight(0.8)
temp_scalar_bar.UnconstrainedFontSizeOn()

# Increase font sizes for better readability
title_prop = temp_scalar_bar.GetTitleTextProperty()
title_prop.SetFontSize(24)  # increase font size
title_prop.SetBold(True)
title_prop.SetColor(1.0, 1.0, 1.0)  # white text (optional)
title_prop.SetFontFamilyToArial()

label_prop = temp_scalar_bar.GetLabelTextProperty()
label_prop.SetFontFamilyToArial()
label_prop.SetBold(True)
label_prop.SetFontSize(24)  # larger labels
label_prop.SetColor(1, 1, 1)

renderer.AddViewProp(temp_scalar_bar)

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(900, 700)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Optional: set camera to a saved position (from user)
camera = renderer.GetActiveCamera()
# User-provided camera parameters
camera.SetPosition(1166.9393086976156, -2348.8726187497973, 2780.6186615624197)
camera.SetFocalPoint(101.0, -1.0, 449.6810739215296)
camera.SetViewUp(-0.26897888898416095, 0.6143246476336248, 0.741792143791419)
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
