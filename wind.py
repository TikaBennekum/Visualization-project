"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    Here the 3D array that points in the wind direction is computed,
    and a small 3D arrow indicating the wind direction is created.
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

    print(
        f"Mean wind components: u={mean_u:.2f}, v={mean_v:.2f}, w={mean_w:.2f}"
    )  # TODO: remove print, only for debugging
    return mean_u, mean_v, mean_w


def make_wind_arrow(
    mean_u, mean_v, mean_w, start_pos=(-150, 150, 700), scale=200.0, color=(1, 1, 1)
):
    """
    Create a small 3D arrow indicating wind direction that stays in the same screen position.
    start_pos is in world coordinates.
    """

    # 1. Normalize direction
    vec_normalized = normalise_vector(np.array([mean_u, mean_v, mean_w]))

    # 2. Arrow geometry
    arrow = vtk.vtkArrowSource()
    arrow.SetTipResolution(20)
    arrow.SetShaftResolution(20)

    # 3. Rotate
    transform = vtk.vtkTransform()
    rotate(transform, vec_normalized)

    # 4. Scale arrow
    transform.Scale(scale, scale, scale)

    # 5. Apply transform
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

    # 1. Normalize direction
    vec_normalized = normalise_vector(np.array([mean_u, mean_v, mean_w]))

    # 2. Reset transform
    transform.Identity()

    # 3. Rotate
    rotate(transform, vec_normalized)

    # 4. Scale only
    transform.Scale(scale, scale, scale)

    # 5. Update the filter
    tf_filter.SetTransform(transform)
    tf_filter.Update()

    return wind_actor


def make_wind_streamlines(
    grid,
    num_seeds=50,
    tube_radius=1.0,
    color=(0.2, 0.8, 1.0),
    terrain="mountain",
):
    """
    Create streamlines along the top-left side of the domain slightly above the ground.
    Returns (actor, tracer, calculator, tube_filter).
    """

    # 1) Build vector array 'velocity' from u,v,w
    calc = vtk.vtkArrayCalculator()
    calc.SetInputData(grid)
    calc.AddScalarVariable("u", "u")
    calc.AddScalarVariable("v", "v")
    calc.AddScalarVariable("w", "w")
    calc.SetFunction("u*iHat + v*jHat + w*kHat")
    calc.SetResultArrayName("velocity")
    calc.Update()

    # 2) Get grid bounds
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

    # 3) Stream tracer
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

    # 4) Tube filter for better visualization
    tube = vtk.vtkTubeFilter()
    tube.SetInputConnection(tracer.GetOutputPort())
    tube.SetNumberOfSides(8)
    tube.SetRadius(tube_radius)
    tube.CappingOn()
    tube.Update()

    # 5) Mapper + actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tube.GetOutputPort())
    mapper.SetScalarModeToUsePointFieldData()
    mapper.SelectColorArray("velocity")

    # Create grayscale lookup table
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    lut.Build()

    for i in range(256):
        gray = i / 255.0
        lut.SetTableValue(i, gray, gray, gray, 1.0)  # r,g,b,a

    mapper.SetLookupTable(lut)
    mapper.SetUseLookupTableScalarRange(True)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    # actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetOpacity(0.5)

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
