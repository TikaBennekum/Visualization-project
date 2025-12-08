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

from fire_smoke import (
    make_fire_smoke_actors,
    make_temperature_lut,
    make_temperature_scalar_bar,
)
from geometry import create_plane
from labels import make_timestep_text, make_title
from rendering import make_renderer, make_window_and_interactor, setup_camera
from vegetation import make_vegetation_actor, make_vegetation_scalar_bar
from wind import (
    compute_mean_wind_direction,
    make_wind_arrow,
    make_wind_streamlines,
)

# --- 1. CONFIGURATION ---
STATIC_TIMESTEP = 10000

# Define the viewports for a 2x4 grid (8 slots total: 7 sims + 1 legend)
VIEWPORTS = [
    (0.0, 0.5, 0.25, 1.0),  # Slot 0: Sim 1
    (0.25, 0.5, 0.5, 1.0),  # Slot 1: Sim 2
    (0.5, 0.5, 0.75, 1.0),  # Slot 2: Sim 3
    (0.75, 0.5, 1.0, 1.0),  # Slot 3: Sim 4
    (0.0, 0.0, 0.25, 0.5),  # Slot 4: Sim 5
    (0.25, 0.0, 0.5, 0.5),  # Slot 5: Sim 6
    (0.5, 0.0, 0.75, 0.5),  # Slot 6: Sim 7
    (0.75, 0.0, 1.0, 0.5),  # Slot 7: Master Legend
]

# Define all 7 simulations (adjust the file paths as needed)
SIMULATION_PARAMS = [
    {
        "terrain": "mountain",
        "fire": "headcurve",
        "curvature": 40,
        "title": "Mnt C40 Head",
    },
    {
        "terrain": "mountain",
        "fire": "headcurve",
        "curvature": 80,
        "title": "Mnt C80 Head",
    },
    {
        "terrain": "mountain",
        "fire": "headcurve",
        "curvature": 320,
        "title": "Mnt C320 Head",
    },
    {"terrain": "valley", "fire": None, "curvature": None, "title": "Valley"},
    {
        "terrain": "mountain",
        "fire": "backcurve",
        "curvature": 40,
        "title": "Mnt C40 Back",
    },
    {
        "terrain": "mountain",
        "fire": "backcurve",
        "curvature": 80,
        "title": "Mnt C80 Back",
    },
    {
        "terrain": "mountain",
        "fire": "backcurve",
        "curvature": 320,
        "title": "Mnt C320 Back",
    },
]

# Global LUTs for synchronization
# These will be created once and shared by all scalar bars
global_fire_lut = None
global_veg_lut = None
all_renderers = []
all_grids = []

# --- 2. MULTI-VIEWPORT SETUP ---

# Create the main window and interactor once
render_window, interactor = make_window_and_interactor()  # Pass None initially

# 2a. Loop through all 7 simulations
for i, params in enumerate(SIMULATION_PARAMS):
    # Determine directory and filename for the VTS file
    if params["terrain"] == "valley":
        directory = f"{params['terrain']}"
    else:
        directory = f"{params['terrain']}_{params['fire']}{params['curvature']}"
    filename = f"{directory}/output.{STATIC_TIMESTEP}.vts"

    # Reading the VTS dataset
    reader = vtk.vtkXMLGenericDataObjectReader()
    reader.SetFileName(filename)
    reader.Update()
    grid = reader.GetOutput()
    all_grids.append(grid)  # Store grid for potential animation later

    # Create a new renderer and set its viewport
    renderer = make_renderer()
    renderer.SetViewport(VIEWPORTS[i])
    render_window.AddRenderer(renderer)
    all_renderers.append(renderer)

    # --- ACTOR GENERATION (Same logic as before, but per renderer) ---

    # Get scalar field info
    theta_name = "theta"
    theta = grid.GetPointData().GetArray(theta_name)
    theta_min, theta_max = theta.GetRange()

    # Title/Subtitle (Title is now the unique Sim name)
    subtitle = make_title(
        params["terrain"], fire_type=params["fire"], curvature=params["curvature"]
    )
    renderer.AddViewProp(subtitle)

    # Timestep text (unique to each view)
    timestamp_actor = make_timestep_text(STATIC_TIMESTEP)
    renderer.AddViewProp(timestamp_actor)

    # Vegetation Actor (and creating global LUTs)
    vegetation_actor, vegetation_lut, _ = make_vegetation_actor(grid)

    if global_veg_lut is None:
        global_veg_lut = vegetation_lut

    renderer.AddActor(vegetation_actor)

    # Ground Plane
    ground_actor, _ = create_plane(grid)
    renderer.AddActor(ground_actor)

    # Fire and Smoke Actors (and creating global LUTs)
    (levels, fire_smoke_actors, fire_contours) = make_fire_smoke_actors(
        grid, theta_name, theta_min
    )
    low, mid, hi, higher, very_hi = levels

    if global_fire_lut is None:
        global_fire_lut = make_temperature_lut(low, very_hi)

    for actor in fire_smoke_actors:
        # NOTE: If you are using LUTs inside make_fire_smoke_actors,
        # ensure they are all set to use the global_fire_lut here if you want uniform color scale.
        renderer.AddActor(actor)

    # Wind Arrow
    mean_u, mean_v, mean_w = compute_mean_wind_direction(grid)
    wind_actor, wind_transform, wind_tf_filter = make_wind_arrow(mean_u, mean_v, mean_w)
    renderer.AddActor(wind_actor)

    # Wind Streamlines
    stream_actor, _, _, _ = make_wind_streamlines(
        grid, num_seeds=20, tube_radius=2.0, seed_height_factor=0.1
    )
    if stream_actor is not None:
        renderer.AddActor(stream_actor)

    # Set up camera for this renderer (will be synchronized later)
    setup_camera(renderer)


# 2b. Setup the Master Legend Renderer (Slot 7)
legend_renderer = make_renderer()
legend_renderer.SetViewport(VIEWPORTS[7])
legend_renderer.SetBackground(0.05, 0.05, 0.05)  # Dark gray background
render_window.AddRenderer(legend_renderer)
all_renderers.append(legend_renderer)

# Add Temperature Scalar Bar
if global_fire_lut:
    temp_bar = make_temperature_scalar_bar(global_fire_lut)
    # Adjust position for the dedicated legend viewport
    temp_bar.SetPosition(0.05, 0.2)
    legend_renderer.AddViewProp(temp_bar)

# Add Vegetation Scalar Bar
if global_veg_lut:
    veg_bar = make_vegetation_scalar_bar(global_veg_lut)
    # Adjust position for the dedicated legend viewport
    veg_bar.SetPosition(0.5, 0.2)
    legend_renderer.AddViewProp(veg_bar)


# --- 3. SYNCHRONIZATION AND INTERACTION ---

# Synchronize Cameras
# Get the camera from the first simulation (Slot 0)
camera = all_renderers[0].GetActiveCamera()
all_renderers[0].ResetCamera()

# Apply this camera to all other simulation renderers (Slots 1-6)
for renderer in all_renderers[1:7]:
    renderer.SetActiveCamera(camera)

# The legend renderer (Slot 7) does not need a 3D camera

render_window.Render()
interactor.Initialize()
interactor.Start()
