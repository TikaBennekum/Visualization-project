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

from animation import create_frames, get_all_files
from fire_smoke import (
    make_fire_smoke_actors,
    make_temperature_lut,
    make_temperature_scalar_bar,
)
from geometry import create_plane, make_outline_actor
from labels import make_timestep_text, make_title
from rendering import make_renderer, make_window_and_interactor, setup_camera
from vegetation import make_vegetation_actor, make_vegetation_scalar_bar
from wind import (
    compute_mean_wind_direction,
    make_wind_arrow,
    make_wind_streamlines,
)

TERRAIN_TYPE = "mountain"  # "mountain" or "valley"
FIRE_TYPE = "backcurve"  # "backcurve" or "headcurve" -- only used for mountain
CURVATURE = 40  # curvature value for mountain simulations -- 40, 80, or 320 -- only used for mountain

# Reading the VTS dataset
if TERRAIN_TYPE == "valley":
    directory = f"{TERRAIN_TYPE}"
else:
    directory = f"{TERRAIN_TYPE}_{FIRE_TYPE}{CURVATURE}"

filename = f"{directory}/output.1000.vts"


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

# Adds title
title, subtitle = make_title(TERRAIN_TYPE, fire_type=FIRE_TYPE, curvature=CURVATURE)
renderer.AddViewProp(title)
renderer.AddViewProp(subtitle)

# Adds timestep text
timestamp_actor = make_timestep_text()
renderer.AddViewProp(timestamp_actor)

# Adds fire and smoke to the visualization
(levels, fire_smoke_actors, fire_contours) = make_fire_smoke_actors(
    grid, theta_name, theta_min
)
low, mid, hi, higher, very_hi = levels
fire_lut = make_temperature_lut(low, very_hi)
temp_bar = make_temperature_scalar_bar(fire_lut)

for actor in fire_smoke_actors:
    renderer.AddActor(actor)
renderer.AddViewProp(temp_bar)

# Adds general wind arrow
mean_u, mean_v, mean_w = compute_mean_wind_direction(grid)
wind_actor, wind_transform, wind_tf_filter = make_wind_arrow(mean_u, mean_v, mean_w)
renderer.AddActor(wind_actor)

# Adds wind streamlines (detailed flow visualization)
stream_actor, stream_tracer, stream_calc, stream_tube = make_wind_streamlines(
    grid, num_seeds=50, tube_radius=1.0, terrain=TERRAIN_TYPE
)
if stream_actor is not None:
    renderer.AddActor(stream_actor)

# Adds vegetation to the visualization
vegetation_actor, vegetation_lut, vegetation_contour = make_vegetation_actor(grid)
vegetation_bar = make_vegetation_scalar_bar(vegetation_lut)
renderer.AddActor(vegetation_actor)
renderer.AddViewProp(vegetation_bar)

# Creates black plane (burnt ground)
ground_actor, ground_slice = create_plane(grid)
renderer.AddActor(ground_actor)

# Interactive rendering
setup_camera(renderer)
render_window, interactor = make_window_and_interactor(renderer)
render_window.Render()
interactor.Initialize()
interactor.Start()

# Animation
filters = {
    "veg": vegetation_contour,
    "smoke_low": fire_contours[0],
    "smoke_mid": fire_contours[1],
    "fire_hi": fire_contours[2],
    "fire_higher": fire_contours[3],
    "fire_very_hi": fire_contours[4],
    "ground": ground_slice,
}

files = get_all_files(directory)

create_frames(
    reader,
    render_window,
    filters,
    timestamp_actor,
    (wind_actor, wind_transform, wind_tf_filter),
    (stream_actor, stream_tracer, stream_calc, stream_tube),
    files,
)
