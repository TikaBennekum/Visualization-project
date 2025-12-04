import numpy as np
import vtk


def compute_mean_wind_direction(u_array, v_array, w_array):
    """
    Compute average horizontal wind direction from u,v components.
    """
    mean_u = np.nanmean(u_array)
    mean_v = np.nanmean(v_array)
    mean_w = np.nanmean(w_array)

    print(f"Mean wind components: u={mean_u:.2f}, v={mean_v:.2f}, w={mean_w:.2f}")
    return mean_u, mean_v, mean_w


def make_wind_arrow(
    mean_u, mean_v, mean_w, start_pos=(-2, 2, 3), scale=20.0, color=(1, 1, 1)
):
    """
    Create a small 2D arrow showing mean wind direction.
    """
    # Normalize direction so we get just the angle

    vec = np.array([mean_u, mean_v, mean_w])
    mag = np.linalg.norm(vec)
    if mag < 1e-6:
        vec = np.array([1.0, 0.0, 0.0])
        mag = 1.0

    vec_normalized = vec / mag

    # Arrow geometry
    arrow = vtk.vtkArrowSource()
    arrow.SetTipResolution(20)
    arrow.SetShaftResolution(20)

    # Compute rotation to align X-axis (default arrow direction) to wind vector
    # Using vtkTransform with RotateWXYZ
    # Step 1: get cross product to find rotation axis
    x_axis = np.array([1.0, 0.0, 0.0])
    axis = np.cross(x_axis, vec_normalized)
    axis_mag = np.linalg.norm(axis)

    transform = vtk.vtkTransform()
    if axis_mag > 1e-6:
        axis /= axis_mag
        angle = np.degrees(np.arccos(np.dot(x_axis, vec_normalized)))
        transform.RotateWXYZ(angle, *axis)
    # else, arrow already aligned

    # Step 2: scale and translate
    transform.Scale(mag * scale, mag * scale, mag * scale)
    transform.Translate(start_pos)

    # Apply transform
    tf = vtk.vtkTransformPolyDataFilter()
    tf.SetInputConnection(arrow.GetOutputPort())
    tf.SetTransform(transform)
    tf.Update()

    # Mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tf.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)

    return actor
