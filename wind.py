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
