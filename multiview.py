"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    This is the main file.
    Here we create a dynamic visualization of a wildfire using VTK.
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
    Parameters:
        animation (bool): Whether to create an animation or just a static view.
        timesteps (list of int): Timesteps to load for static visualization in case length=1, or for animation in case length>1.
    Returns:
        None
    """
    # Define the viewports for a 2x3 grid (6 slots total: 6 sims)
    VIEWPORTS = [
        (0.0, 0.5, 0.33, 1.0),  # Slot 0: Sim 1
        (0.33, 0.5, 0.66, 1.0),  # Slot 1: Sim 2
        (0.66, 0.5, 1.0, 1.0),  # Slot 2: Sim 3
        (0.0, 0.0, 0.33, 0.5),  # Slot 3: Sim 5
        (0.33, 0.0, 0.66, 0.5),  # Slot 4: Sim 6
        (0.66, 0.0, 1.0, 0.5),  # Slot 5: Sim 7
    ]

    # Define all 7 simulations (adjust the file paths as needed)
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

    # These will be created once and shared by all scalar bars
    all_renderers = []
    filters = []
    timestamp_actors = []
    wind_arrows = []
    wind_labels = []
    wind_streams = []

    # --- 2. MULTI-VIEWPORT SETUP ---

    # Create the main window and interactor once
    render_window, interactor = make_window_and_interactor(size=(2400, 1800))

    # 2a. Loop through all 6 simulations
    for i, params in enumerate(SIMULATION_PARAMS):
        # Determine directory and filename for the VTS file
        if params["terrain"] == "valley":
            directory = f"{params['terrain']}"
        else:
            directory = (
                f"{params['terrain']}_{params['fire']}curve{params['curvature']}"
            )
        filename = f"{directory}/output.{timestep_start}.vts"

        # Check if file exists before trying to read it
        if not os.path.isfile(filename):
            print(f"\nERROR: File not found: {filename}")
            print(f"Please ensure the timestep {timestep_start} exists for:")
            print(f"  Terrain: {params['terrain']}")
            print(f"  Fire type: {params['fire']}")
            print(f"  Curvature: {params['curvature']}")

            sys.exit(1)

        # Reading the VTS dataset
        reader = vtk.vtkXMLGenericDataObjectReader()
        reader.SetFileName(filename)
        reader.Update()
        grid = reader.GetOutput()

        # Create a new renderer and set its viewport
        renderer = make_renderer()
        renderer.SetViewport(VIEWPORTS[i])
        render_window.AddRenderer(renderer)
        all_renderers.append(renderer)

        # --- ACTOR GENERATION ---
        # Subtitle
        _, subtitle = make_title(
            params["terrain"], fire_type=params["fire"], curvature=params["curvature"]
        )
        renderer.AddViewProp(subtitle)

        # Timestep text (unique to each view)
        timestamp_actor = make_timestep_text(timestep_start)
        renderer.AddViewProp(timestamp_actor)

        # Vegetation Actor (and creating global LUTs)
        vegetation_actor, _, vegetation_contour = make_vegetation_actor(grid)

        renderer.AddActor(vegetation_actor)

        # Ground Plane
        ground_actor, _ = create_plane(grid)
        renderer.AddActor(ground_actor)

        # Wind Streamlines
        wind_stream = make_wind_streamlines(
            grid,
            num_seeds=15,
            tube_radius=4.0,
            color=(0.95, 0.95, 0.95),
            terrain=params["terrain"],
        )
        if wind_stream[0] is not None:
            renderer.AddActor(wind_stream[0])

        # Fire and Smoke Actors (and creating global LUTs)
        (levels, fire_smoke_actors, fire_contours) = make_fire_smoke_actors(grid)
        low, mid, hi, higher, very_hi = levels

        for actor in fire_smoke_actors:
            renderer.AddActor(actor)

        # Fire Legend
        legend = make_fire_legend(levels)

        for item in legend:
            if isinstance(item, tuple):
                square, text = item
                renderer.AddViewProp(square)
                renderer.AddViewProp(text)
            else:
                renderer.AddViewProp(item)  # background box or title

        # Wind Arrow
        mean_u, mean_v, mean_w = compute_mean_wind_direction(grid)
        wind_arrow = make_wind_arrow(mean_u, mean_v, mean_w)
        renderer.AddActor(wind_arrow[0])

        # Wind Speed Label
        speed_value = wind_speed(mean_u, mean_v, mean_w)
        wind_label = make_wind_speed_follower(
            renderer, wind_arrow[0], speed_value, scale=35
        )

        # Set up camera for this renderer (will be synchronized later)
        setup_camera(renderer)

        # Store filters for animation
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

    # --- 3. SYNCHRONIZATION AND INTERACTION ---

    # Synchronize Cameras
    # Get the camera from the first simulation (Slot 0)
    camera = all_renderers[0].GetActiveCamera()
    all_renderers[0].ResetCamera()

    # Apply this camera to all other simulation renderers (Slots 1-6)
    for renderer in all_renderers[1:]:
        renderer.SetActiveCamera(camera)

    # Animation
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
