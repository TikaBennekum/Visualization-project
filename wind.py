"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    Here the wind for the visualization is created.
"""

import numpy as np
import vtk


def compute_mean_wind_direction(grid):
    """
    Compute average wind direction from u,v,w components.
    """
    u_array = grid.GetPointData().GetArray("u")
    v_array = grid.GetPointData().GetArray("v")
    w_array = grid.GetPointData().GetArray("w")

    mean_u = np.nanmean(u_array)
    mean_v = np.nanmean(v_array)
    mean_w = np.nanmean(w_array)

    return mean_u, mean_v, mean_w


def make_wind_arrow(
    mean_u, mean_v, mean_w, start_pos=(-150, 150, 700), scale=200.0, color=(1, 1, 1)
):
    """
    Create a small 3D arrow indicating wind direction that stays in the same screen position.
    """

    # normalize direction
    vec_normalized = normalise_vector(np.array([mean_u, mean_v, mean_w]))

    # arrow geometry
    arrow = vtk.vtkArrowSource()
    arrow.SetTipResolution(20)
    arrow.SetShaftResolution(20)

    # rotation and scaling
    transform = vtk.vtkTransform()
    rotate(transform, vec_normalized)
    transform.Scale(scale, scale, scale)

    # transform
    tf = vtk.vtkTransformPolyDataFilter()
    tf.SetInputConnection(arrow.GetOutputPort())
    tf.SetTransform(transform)
    tf.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tf.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    actor.SetPosition(*start_pos)

    return actor, transform, tf


def wind_speed(mean_u, mean_v, mean_w):
    """Calulates wind speed."""
    return float(np.sqrt(mean_u**2 + mean_v**2 + mean_w**2))


def make_wind_speed_label(
    renderer,
    render_window,
    wind_actor,
    unit="m/s",
    color=(1, 1, 1),
    font_size=18,
    pixel_offset=(21, 15),
):
    """
    Creates wind speed label to put above arrow.
    """
    text = vtk.vtkTextActor()
    text.SetInput("")  # set later
    tp = text.GetTextProperty()
    tp.SetColor(*color)
    tp.SetFontSize(font_size)
    tp.BoldOn()
    tp.ShadowOn()

    renderer.AddActor2D(text)

    update_wind_speed_label(
        text,
        renderer,
        render_window,
        wind_actor,
        speed_value=0.0,
        unit=unit,
        pixel_offset=pixel_offset,
    )
    return text


def update_wind_speed_label(
    text_actor,
    renderer,
    render_window,
    wind_actor,
    speed_value,
    unit="m/s",
    pixel_offset=(21, 15),
):
    """
    Updates label text + positions it above the arrow based on the arrow's position.
    """
    text_actor.SetInput(f"{speed_value:.2f} {unit}")

    # changes arrow coordinations
    x, y, z = wind_actor.GetPosition()
    renderer.SetWorldPoint(x, y, z, 1.0)
    renderer.WorldToDisplay()
    dx, dy, _ = renderer.GetDisplayPoint()

    text_actor.SetDisplayPosition(int(dx + pixel_offset[0]), int(dy + pixel_offset[1]))

    # keep it inside the window bounds
    w, h = render_window.GetSize()
    pos = text_actor.GetPosition()
    clamped_x = max(0, min(int(pos[0]), max(0, w - 1)))
    clamped_y = max(0, min(int(pos[1]), max(0, h - 1)))
    text_actor.SetDisplayPosition(clamped_x, clamped_y)


# 3D follower-style label that sticks to the wind arrow in world space
def make_wind_speed_follower(
    renderer,
    wind_actor,
    speed_value=0.0,
    unit="m/s",
    color=(1, 1, 1),
    height_offset_factor=0.2,
    scale=20.0,
):
    # Use vtkFollower so the text always faces the camera and supports SetCamera
    vector_text = vtk.vtkVectorText()
    vector_text.SetText(f"{speed_value:.2f} {unit}")

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(vector_text.GetOutputPort())

    follower = vtk.vtkFollower()
    follower.SetMapper(mapper)
    follower.GetProperty().SetColor(*color)
    # VectorText units are small; scale up generously
    follower.SetScale(scale, scale, scale)

    # Position above the arrow
    update_wind_speed_follower(
        follower, renderer, wind_actor, speed_value, unit, height_offset_factor
    )
    follower.SetCamera(renderer.GetActiveCamera())
    renderer.AddActor(follower)
    return follower


def update_wind_speed_follower(
    text_actor,
    renderer,
    wind_actor,
    speed_value,
    unit="m/s",
    height_offset_factor=0.2,
):
    # Update text if mapper supports VectorText input; else ignore text update
    try:
        mapper = text_actor.GetMapper()
        src = mapper.GetInputConnection(0, 0).GetProducer()
        if isinstance(src, vtk.vtkVectorText):
            src.SetText(f"{speed_value:.2f} {unit}")
    except Exception:
        pass

    # Compute a position just above the arrow's top in world coordinates
    try:
        bx0, bx1, by0, by1, bz0, bz1 = wind_actor.GetBounds()
        cx = 0.5 * (bx0 + bx1)
        cy = 0.5 * (by0 + by1)
        z_offset = (bz1 - bz0) * height_offset_factor
        text_actor.SetPosition(cx, cy, bz1 + z_offset)
    except Exception:
        # fallback to actor position
        x, y, z = wind_actor.GetPosition()
        text_actor.SetPosition(x, y, z)

    # ensure it faces the camera
    try:
        text_actor.SetCamera(renderer.GetActiveCamera())
    except Exception:
        pass


def normalise_vector(vec):
    """
    Normalizes a 3D vector. If the vector has zero magnitude, returns a default unit vector.
    """
    mag = np.linalg.norm(vec)
    if mag < 1e-6:
        vec = np.array([1.0, 0.0, 0.0])
        mag = 1.0
    vec_normalized = vec / mag

    return vec_normalized


def rotate(transform, vec_normalized):
    """
    Rotates the transform to align the x-axis with the given normalized vector.
    """
    x_axis = np.array([1.0, 0.0, 0.0])
    axis = np.cross(x_axis, vec_normalized)
    axis_mag = np.linalg.norm(axis)

    if axis_mag < 1e-6:
        if np.dot(x_axis, vec_normalized) < 0:
            transform.RotateWXYZ(180, 0, 1, 0)
    else:
        axis /= axis_mag
        angle = np.degrees(
            np.arccos(np.clip(np.dot(x_axis, vec_normalized), -1.0, 1.0))
        )
        transform.RotateWXYZ(angle, *axis)


def update_wind_arrow(wind, mean_u, mean_v, mean_w, scale=200.0):
    """
    Updates the wind arrow actor to point in the direction of the new mean wind vector.
    wind_actor: vtkActor
    transform: vtkTransform
    tf_filter: vtkTransformPolyDataFilter
    """
    wind_actor, transform, tf_filter = wind

    # normalize direction
    vec_normalized = normalise_vector(np.array([mean_u, mean_v, mean_w]))

    # reset transform
    transform.Identity()

    # rotate
    rotate(transform, vec_normalized)

    # scale
    transform.Scale(scale, scale, scale)

    # update filter
    tf_filter.SetTransform(transform)
    tf_filter.Update()

    return wind_actor


def make_wind_streamlines(
    grid,
    num_seeds=10,
    tube_radius=1.0,
    color=(0.2, 0.8, 1.0),
    terrain="mountain",
):
    """
    Create streamlines along the top-left side of the domain slightly above the ground.
    Returns (actor, tracer, calculator, tube_filter).
    """

    # Build vector array 'velocity' from u,v,w
    calc = vtk.vtkArrayCalculator()
    calc.SetInputData(grid)
    calc.AddScalarVariable("u", "u")
    calc.AddScalarVariable("v", "v")
    calc.AddScalarVariable("w", "w")
    calc.SetFunction("u*iHat + v*jHat + w*kHat")
    calc.SetResultArrayName("velocity")
    calc.Update()

    # Get grid bounds
    bounds = grid.GetBounds()
    x_min, x_max, y_min, y_max, z_min, z_max = bounds

    # Place seeds along a horizontal line at the top-left corner (x_min, y_max)
    if terrain == "mountain":
        seed_z = z_min + 0.1 * (z_max - z_min)  # slightly above ground
    else:
        seed_z = z_min + 0.15 * (z_max - z_min)  # slightly above ground
    x_positions = np.linspace(x_min, x_min, num_seeds)  # constant x (left)
    y_positions = np.linspace(y_min, y_max, num_seeds)  # spread along y
    z_positions = np.full(num_seeds, seed_z)

    seeds = vtk.vtkPoints()
    for xi, yi, zi in zip(x_positions, y_positions, z_positions):
        seeds.InsertNextPoint(xi, yi, zi)

    seed_poly = vtk.vtkPolyData()
    seed_poly.SetPoints(seeds)

    # Stream tracer
    rk4 = vtk.vtkRungeKutta4()
    tracer = vtk.vtkStreamTracer()
    tracer.SetInputConnection(calc.GetOutputPort())
    tracer.SetSourceData(seed_poly)
    tracer.SetIntegrator(rk4)
    tracer.SetIntegrationDirectionToForward()
    tracer.SetMaximumPropagation(max(x_max - x_min, y_max - y_min, z_max - z_min) * 4.0)
    tracer.SetInitialIntegrationStep(0.1)
    tracer.SetMinimumIntegrationStep(0.01)
    tracer.SetComputeVorticity(False)
    tracer.SetInputArrayToProcess(
        0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, "velocity"
    )
    tracer.Update()

    # Tube filter for better visualization
    tube = vtk.vtkTubeFilter()
    tube.SetInputConnection(tracer.GetOutputPort())
    tube.SetNumberOfSides(20)
    tube.SetRadius(tube_radius)
    tube.CappingOn()
    tube.SetUseDefaultNormal(False)
    tube.SetVaryRadiusToVaryRadiusOff()
    tube.Update()

    # Mapper + actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tube.GetOutputPort())

    # Disable scalar coloring
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Set a constant gray color
    actor.GetProperty().SetColor(color)  # mid gray
    actor.GetProperty().SetOpacity(0.17)
    print(grid.GetBounds())

    # disable lighting so it doesn't look darker from some angles
    actor.GetProperty().LightingOff()

    return actor, tracer, calc, tube


def update_wind_streamlines(stream_tuple, grid):
    """Update the streamlines pipeline when a new `grid` is available.

    stream_tuple should be the (actor, tracer, calculator, tube_filter) returned
    by `make_wind_streamlines`.
    """
    if stream_tuple is None:
        return None
    actor, tracer, calc, tube = stream_tuple
    if calc is None or tracer is None:
        return actor
    try:
        # Replace calculator input and re-run the pipeline
        if hasattr(calc, "SetInputData"):
            calc.SetInputData(grid)
        else:
            # try connection-based
            tp = vtk.vtkTrivialProducer()
            tp.SetOutput(grid)
            if hasattr(calc, "SetInputConnection"):
                calc.SetInputConnection(tp.GetOutputPort())
        calc.Modified()
        calc.Update()

        tracer.Modified()
        tracer.Update()

        tube.Modified()
        tube.Update()
    except Exception:
        pass
    return actor
