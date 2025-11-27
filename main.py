"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    This is the main file.
    Here we create a dynamic visualization of a wildfire using VTK.
"""

#!/usr/bin/env vtkpython
import vtk

from vegetation import make_vegetation_actor, make_vegetation_scalar_bar
from fire_smoke import (
    make_fire_smoke_actors,
    make_temperature_lut,
    make_temperature_scalar_bar,
)
from geometry import make_outline_actor
from rendering import make_renderer, setup_camera, make_window_and_interactor

# Reading the VTS dataset
filename = "mountain_backcurve40/output.70000.vts"
reader = vtk.vtkXMLGenericDataObjectReader()
reader.SetFileName(filename)
reader.Update()
grid = reader.GetOutput()

# Get scalar field that represents potential temperature
theta_name = "theta"
theta = grid.GetPointData().GetArray(theta_name)
theta_min, theta_max = theta.GetRange()

# Initializes rendering
renderer = make_renderer()
outline_actor = make_outline_actor(grid)
renderer.AddActor(outline_actor)

# Adds fire and smoke to the visualization
(levels, fire_smoke_actors) = make_fire_smoke_actors(grid, theta_name, theta_min)
low, mid, hi, higher, very_hi = levels
fire_lut = make_temperature_lut(low, very_hi)
temp_bar = make_temperature_scalar_bar(fire_lut)

for actor in fire_smoke_actors:
    renderer.AddActor(actor)
renderer.AddViewProp(temp_bar)

# Adds vegetation to the visualization
vegetation_actor, vegetation_lut = make_vegetation_actor(grid)
vegetation_bar = make_vegetation_scalar_bar(vegetation_lut)
renderer.AddActor(vegetation_actor)
renderer.AddViewProp(vegetation_bar)

# Interactive rendering
setup_camera(renderer)
render_window, interactor = make_window_and_interactor(renderer)
render_window.Render()
interactor.Initialize()
interactor.Start()
