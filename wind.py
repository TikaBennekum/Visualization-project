import numpy as np
import vtk


def compute_mean_wind_direction(grid):
    """
    Compute average horizontal wind direction from u,v components.
    """
    u_array = grid.GetPointData().GetArray("u")
    v_array = grid.GetPointData().GetArray("v")
    w_array = grid.GetPointData().GetArray("w")

    mean_u = np.nanmean(u_array)
    mean_v = np.nanmean(v_array)
    mean_w = np.nanmean(w_array)

    print(f"Mean wind components: u={mean_u:.2f}, v={mean_v:.2f}, w={mean_w:.2f}")
    return mean_u, mean_v, mean_w


def make_wind_arrow(
    mean_u, mean_v, mean_w, start_pos=(-150, 150, 700), scale=200.0, color=(1, 1, 1)
):
    """
    Create a small 3D arrow indicating wind direction that stays in the same screen position.
    start_pos is in normalized viewport coordinates (0..1) for X and Y, Z is ignored.
    """

    # 1. Normalize direction
    vec = np.array([mean_u, mean_v, mean_w])
    mag = np.linalg.norm(vec)
    if mag < 1e-6:
        vec = np.array([1.0, 0.0, 0.0])
        mag = 1.0
    vec_normalized = vec / mag

    # 2. Create arrow geometry
    arrow = vtk.vtkArrowSource()
    arrow.SetTipResolution(20)
    arrow.SetShaftResolution(20)

    # 3. Transform: rotate arrow from +X to wind direction
    x_axis = np.array([1.0, 0.0, 0.0])
    axis = np.cross(x_axis, vec_normalized)
    axis_mag = np.linalg.norm(axis)
    transform = vtk.vtkTransform()
    if axis_mag > 1e-6:
        axis /= axis_mag
        angle = np.degrees(
            np.arccos(np.clip(np.dot(x_axis, vec_normalized), -1.0, 1.0))
        )
        transform.RotateWXYZ(angle, *axis)

    # 4. Scale uniformly (optional: based on your choice)
    transform.Scale(scale, scale, scale)

    # 5. Position in screen (fixed)
    # We'll use vtkFollower or vtkActor2D with a coordinate transform
    tf = vtk.vtkTransformPolyDataFilter()
    tf.SetInputConnection(arrow.GetOutputPort())
    tf.SetTransform(transform)
    tf.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tf.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)

    # Force the arrow to stay in the same camera position:
    actor.SetPosition(start_pos)  # in world coords
    # Optional: you can attach this actor to a vtkCoordinate for normalized viewport later

    return actor, transform, tf


def update_wind_arrow(
    wind, mean_u, mean_v, mean_w, start_pos=(-2, 2, 3), scale=20.0, color=(1, 1, 1)
):
    """
    Updates the wind arrow actor to point in the direction of the new mean wind vector.
    """
    transform, tf_filter = wind

    vec = np.array([mean_u, mean_v, mean_w])
    mag = np.linalg.norm(vec)
    if mag < 1e-6:
        vec = np.array([1.0, 0.0, 0.0])
        mag = 1.0
    vec_normalized = vec / mag

    # Reset the transform
    transform.Identity()

    # Compute rotation
    x_axis = np.array([1.0, 0.0, 0.0])
    axis = np.cross(x_axis, vec_normalized)
    axis_mag = np.linalg.norm(axis)
    if axis_mag > 1e-6:
        axis /= axis_mag
        angle = np.degrees(np.arccos(np.dot(x_axis, vec_normalized)))
        transform.RotateWXYZ(angle, *axis)

    # Scale and translate
    transform.Scale(mag * scale, mag * scale, mag * scale)
    transform.Translate(start_pos)

    # Update the filter
    tf_filter.SetTransform(transform)
    tf_filter.Update()
