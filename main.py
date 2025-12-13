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
from fire_smoke import make_fire_legend, make_fire_smoke_actors
from geometry import create_plane
from labels import make_timestep_text, make_title
from rendering import make_renderer, make_window_and_interactor, setup_camera
from vegetation import make_vegetation_actor
from wind import (
    compute_mean_wind_direction,
    make_wind_arrow,
    make_wind_speed_follower,
    make_wind_streamlines,
    wind_speed,
)

TERRAIN_TYPE = "mountain"  # "mountain" or "valley"
FIRE_TYPE = "back"  # "back" or "head" -- only used for mountain
CURVATURE = 40  # curvature value for mountain simulations -- 40, 80, or 320 -- only used for mountain

# Reading the VTS dataset
if TERRAIN_TYPE == "valley":
    directory = f"{TERRAIN_TYPE}"
else:
    directory = f"{TERRAIN_TYPE}_{FIRE_TYPE}curve{CURVATURE}"

filename = f"{directory}/output.1000.vts"


reader = vtk.vtkXMLGenericDataObjectReader()
reader.SetFileName(filename)
reader.Update()
grid = reader.GetOutput()

# Get scalar field that represents potential temperature
theta_name = "theta"
theta = grid.GetPointData().GetArray(theta_name)

# Initializes rendering
renderer = make_renderer()

# Adds title
title, subtitle = make_title(TERRAIN_TYPE, fire_type=FIRE_TYPE, curvature=CURVATURE)
renderer.AddViewProp(title)
renderer.AddViewProp(subtitle)

# Adds timestep text
timestamp_actor = make_timestep_text()
renderer.AddViewProp(timestamp_actor)

# Adds vegetation to the visualization
vegetation_actor, vegetation_lut, vegetation_contour = make_vegetation_actor(grid)
renderer.AddActor(vegetation_actor)

# Creates black plane (burnt ground)
ground_actor, ground_slice = create_plane(grid)
renderer.AddActor(ground_actor)

# Adds wind streamlines (detailed flow visualization)
stream_actor, stream_tracer, stream_calc, stream_tube = make_wind_streamlines(
    grid, num_seeds=17, tube_radius=4.0, color=(0.95, 0.95, 0.95), terrain=TERRAIN_TYPE
)
if stream_actor is not None:
    renderer.AddActor(stream_actor)

# Adds fire and smoke to the visualization
(levels, fire_smoke_actors, fire_contours) = make_fire_smoke_actors(grid, theta_name)

for actor in fire_smoke_actors:
    renderer.AddActor(actor)

legend = make_fire_legend(levels)

for item in legend:
    if isinstance(item, tuple):
        square, text = item
        renderer.AddViewProp(square)
        renderer.AddViewProp(text)
    else:
        renderer.AddViewProp(item)  # background box or title

# Adds general wind arrow
mean_u, mean_v, mean_w = compute_mean_wind_direction(grid)
wind = make_wind_arrow(
    mean_u, mean_v, mean_w
)  # <- keep as tuple (actor, transform, tf)
wind_actor = wind[0]
renderer.AddActor(wind_actor)

# Interactive rendering
setup_camera(renderer)
render_window, interactor = make_window_and_interactor(renderer)

# create a 3D follower speed label above the arrow (sticks in world space)
spd = wind_speed(mean_u, mean_v, mean_w)
wind_label = make_wind_speed_follower(
    renderer,
    wind_actor,
    speed_value=spd,
)

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
    wind,
    wind_label,
    (stream_actor, stream_tracer, stream_calc, stream_tube),
    files,
)
