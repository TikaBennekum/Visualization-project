# !/usr/bin/env vtkpython
import vtk

# -----------------------
# 1. Read the VTS dataset
# -----------------------
filename = "mountain_backcurve40/output.30000.vts"

reader = vtk.vtkXMLGenericDataObjectReader()
reader.SetFileName(filename)
reader.Update()

grid = reader.GetOutput()

print("Loaded:", grid.GetClassName())

# Name of the scalar field that represents potential temperature
rhof_1_name = "rhof_1"


# --------------------------------------------
# 2. Build isosurfaces for "fire" temperature
#    (flame is roughly 400–800 K per the spec)
# --------------------------------------------
# Instead of drawing a few isosurfaces, extract the dataset surface
# and color it continuously by the `rhof_1` scalar.
surface = vtk.vtkDataSetSurfaceFilter()
surface.SetInputData(grid)
surface.Update()

# --------------------------
# 3. Mapper & actor for vegetation (continuous color)
# --------------------------
veg_mapper = vtk.vtkPolyDataMapper()
veg_mapper.SetInputConnection(surface.GetOutputPort())

# Use rhof_1 for coloring
veg_mapper.SetScalarModeToUsePointFieldData()
veg_mapper.SelectColorArray(rhof_1_name)

# Determine scalar range from the data if possible, otherwise fall back
veg_range = (0.0, 0.6)
pd = grid.GetPointData()
if pd and pd.GetArray(rhof_1_name):
    try:
        veg_range = pd.GetArray(rhof_1_name).GetRange()
    except Exception:
        veg_range = veg_range

veg_mapper.SetScalarRange(veg_range)

# Build a green lookup table for continuous surface coloring.
# Make scalar == 0 (air) transparent by setting alpha=0 for those table entries.
lut = vtk.vtkLookupTable()
num_entries = 256
lut.SetNumberOfTableValues(num_entries)
lut.Build()

# Small epsilon to treat values as zero (air)
eps_zero = 1e-8
for i in range(num_entries):
    t = float(i) / (num_entries - 1)
    scalar_val = veg_range[0] + t * (veg_range[1] - veg_range[0])
    # green ramp (dark -> bright)
    r = 0.05 + 0.15 * t
    g = 0.35 + 0.6 * t
    b = 0.05
    # treat very small values as air -> transparent
    alpha = 0.0 if scalar_val <= eps_zero else 1.0
    lut.SetTableValue(i, r, g, b, alpha)

veg_mapper.SetLookupTable(lut)
veg_mapper.SetUseLookupTableScalarRange(True)
veg_mapper.ScalarVisibilityOn()

veg_actor = vtk.vtkActor()
veg_actor.SetMapper(veg_mapper)
veg_actor.GetProperty().SetInterpolationToPhong()

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
renderer.AddActor(veg_actor)
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
