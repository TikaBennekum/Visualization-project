"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    A multiview of the visualization is generated in this file.
"""

#!/usr/bin/env vtkpython

import os
import sys

import vtk

from animation_multiview import create_frames, get_all_files
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


def create_multiview_visualisation(
    animation=True,
    timestep_start=10000,
    timestep_end=15000,
):
    """
    Creates a multi-view visualization of the wildfire simulation.
    """
    # defines the viewports for a 2x3 grid
    VIEWPORTS = [
        (0.0, 0.5, 0.33, 1.0),  # Slot 0: Sim 1
        (0.33, 0.5, 0.66, 1.0),  # Slot 1: Sim 2
        (0.66, 0.5, 1.0, 1.0),  # Slot 2: Sim 3
        (0.0, 0.0, 0.33, 0.5),  # Slot 3: Sim 5
        (0.33, 0.0, 0.66, 0.5),  # Slot 4: Sim 6
        (0.66, 0.0, 1.0, 0.5),  # Slot 5: Sim 7
    ]

    # define all 6 simulations
    SIMULATION_PARAMS = [
        {
            "terrain": "mountain",
            "fire": "head",
            "curvature": 40,
        },
        {
            "terrain": "mountain",
            "fire": "head",
            "curvature": 80,
        },
        {
            "terrain": "mountain",
            "fire": "head",
            "curvature": 320,
        },
        {
            "terrain": "mountain",
            "fire": "back",
            "curvature": 40,
        },
        {
            "terrain": "mountain",
            "fire": "back",
            "curvature": 80,
        },
        {
            "terrain": "mountain",
            "fire": "back",
            "curvature": 320,
        },
    ]

    all_renderers = []
    filters = []
    timestamp_actors = []
    wind_arrows = []
    wind_labels = []
    wind_streams = []

    render_window, interactor = make_window_and_interactor(size=(2400, 1800))

    for i, params in enumerate(SIMULATION_PARAMS):
        if params["terrain"] == "valley":
            directory = f"{params['terrain']}"
        else:
            directory = (
                f"{params['terrain']}_{params['fire']}curve{params['curvature']}"
            )
        filename = f"{directory}/output.{timestep_start}.vts"

        # check if file exists before trying to read it
        if not os.path.isfile(filename):
            print(f"\nERROR: File not found: {filename}")
            print(f"Please ensure the timestep {timestep_start} exists for:")
            print(f"  Terrain: {params['terrain']}")
            print(f"  Fire type: {params['fire']}")
            print(f"  Curvature: {params['curvature']}")

            sys.exit(1)

        # reading the VTS dataset
        reader = vtk.vtkXMLGenericDataObjectReader()
        reader.SetFileName(filename)
        reader.Update()
        grid = reader.GetOutput()

        # create a new renderer and set its viewport
        renderer = make_renderer(visualisation_type="multiview")
        renderer.SetViewport(VIEWPORTS[i])
        render_window.AddRenderer(renderer)
        all_renderers.append(renderer)

        _, subtitle = make_title(
            params["terrain"], fire_type=params["fire"], curvature=params["curvature"]
        )
        renderer.AddViewProp(subtitle)
        timestamp_actor = make_timestep_text(timestep_start)
        renderer.AddViewProp(timestamp_actor)
        vegetation_actor, _, vegetation_contour = make_vegetation_actor(grid)
        renderer.AddActor(vegetation_actor)

        ground_actor, _ = create_plane(grid)
        renderer.AddActor(ground_actor)

        wind_stream = make_wind_streamlines(
            grid,
            num_seeds=15,
            tube_radius=4.0,
            color=(0.95, 0.95, 0.95),
            terrain=params["terrain"],
        )
        if wind_stream[0] is not None:
            renderer.AddActor(wind_stream[0])

        (levels, fire_smoke_actors, fire_contours) = make_fire_smoke_actors(grid)
        low, mid, hi, higher, very_hi = levels

        for actor in fire_smoke_actors:
            renderer.AddActor(actor)

        legend = make_fire_legend(levels, "multiview")

        for item in legend:
            if isinstance(item, tuple):
                square, text = item
                renderer.AddViewProp(square)
                renderer.AddViewProp(text)
            else:
                renderer.AddViewProp(item)  # background box or title

        mean_u, mean_v, mean_w = compute_mean_wind_direction(grid)
        wind_arrow = make_wind_arrow(mean_u, mean_v, mean_w)
        renderer.AddActor(wind_arrow[0])

        speed_value = wind_speed(mean_u, mean_v, mean_w)
        wind_label = make_wind_speed_follower(
            renderer, wind_arrow[0], speed_value, scale=35
        )

        setup_camera(renderer)
        filters.append(
            {
                "veg": vegetation_contour,
                "smoke_low": fire_contours[0],
                "smoke_mid": fire_contours[1],
                "fire_hi": fire_contours[2],
                "fire_higher": fire_contours[3],
                "fire_very_hi": fire_contours[4],
            }
        )
        timestamp_actors.append(timestamp_actor)
        wind_arrows.append(wind_arrow)
        wind_labels.append(wind_label)
        wind_streams.append(wind_stream)

    # synchronize Cameras
    camera = all_renderers[0].GetActiveCamera()
    all_renderers[0].ResetCamera()

    # apply this camera to all other simulation renderers
    for renderer in all_renderers[1:]:
        renderer.SetActiveCamera(camera)

    if animation:
        timesteps = list(range(timestep_start, timestep_end + 1, 1000))
        files = get_all_files(timesteps)

        create_frames(
            reader,
            render_window,
            filters,
            timestamp_actors,
            wind_arrows,
            wind_labels,
            wind_streams,
            files,
        )
    else:
        render_window.Render()
        interactor.Initialize()
        interactor.Start()
