"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    A single view of a visualization is generated here.
"""

#!/usr/bin/env vtkpython

import os
import sys

import vtk

from animation_singleview import create_frames, get_all_files
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


def create_singleview_visualisation(
    animation=True,
    terrain_type="mountain",
    fire_type="head",
    curvature=40,
    timestep=10000,
):
    """
    Creates a single-view visualization of the wildfire simulation.
    """
    # reading the VTS dataset
    if terrain_type == "valley":
        directory = f"{terrain_type}"
    else:
        directory = f"{terrain_type}_{fire_type}curve{curvature}"

    filename = f"{directory}/output.{timestep}.vts"

    # check if file exists before trying to read it
    if not os.path.isfile(filename):
        print(f"\nERROR: File not found: {filename}")
        print(f"Please ensure the timestep {timestep} exists for:")
        print(f"  Terrain: {terrain_type}")
        if terrain_type == "mountain":
            print(f"  Fire type: {fire_type}")
            print(f"  Curvature: {curvature}")
        sys.exit(1)

    reader = vtk.vtkXMLGenericDataObjectReader()
    reader.SetFileName(filename)
    reader.Update()
    grid = reader.GetOutput()

    renderer = make_renderer(visualisation_type="singleview")

    title, subtitle = make_title(terrain_type, fire_type, curvature)
    renderer.AddViewProp(title)
    renderer.AddViewProp(subtitle)

    timestamp_actor = make_timestep_text(timestep)
    renderer.AddViewProp(timestamp_actor)

    # adds vegetation to the visualization
    vegetation_actor, vegetation_lut, vegetation_contour = make_vegetation_actor(grid)
    renderer.AddActor(vegetation_actor)

    # creates black plane (burnt ground)
    ground_actor, ground_slice = create_plane(grid)
    renderer.AddActor(ground_actor)

    # adds wind streamlines
    stream_actor, stream_tracer, stream_calc, stream_tube = make_wind_streamlines(
        grid,
        num_seeds=15,
        tube_radius=4.0,
        color=(0.95, 0.95, 0.95),
        terrain=terrain_type,
    )
    if stream_actor is not None:
        renderer.AddActor(stream_actor)

    # adds fire and smoke to the visualization
    (levels, fire_smoke_actors, fire_contours) = make_fire_smoke_actors(grid)

    for actor in fire_smoke_actors:
        renderer.AddActor(actor)

    legend = make_fire_legend(levels, visualisation_type="singleview")

    for item in legend:
        if isinstance(item, tuple):
            square, text = item
            renderer.AddViewProp(square)
            renderer.AddViewProp(text)
        else:
            renderer.AddViewProp(item)  # background box or title

    # adds general wind arrow
    mean_u, mean_v, mean_w = compute_mean_wind_direction(grid)
    wind = make_wind_arrow(mean_u, mean_v, mean_w)
    wind_actor = wind[0]
    renderer.AddActor(wind_actor)

    setup_camera(renderer)
    render_window, interactor = make_window_and_interactor()
    render_window.AddRenderer(renderer)

    spd = wind_speed(mean_u, mean_v, mean_w)
    wind_label = make_wind_speed_follower(
        renderer, wind_actor, speed_value=spd, scale=27
    )

    if animation:
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
    else:
        render_window.Render()
        interactor.Initialize()
        interactor.Start()
