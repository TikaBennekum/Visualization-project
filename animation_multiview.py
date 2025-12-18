"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    Rendering of the scene of the visualization.
"""

import os
import re

import vtk

from labels import update_timestep_text
from wind import (
    compute_mean_wind_direction,
    update_wind_arrow,
    update_wind_speed_follower,
    update_wind_streamlines,
    wind_speed,
)


def setup_frame(render_window):
    """Sets up the frame for capturing screenshots."""
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(render_window)
    w2if.ReadFrontBufferOff()

    png = vtk.vtkPNGWriter()
    png.SetInputConnection(w2if.GetOutputPort())

    return w2if, png


def get_all_files(range):
    """Gets all VTS files in the dataset directory, sorted by time index."""
    files = []

    for i in range:
        one_step = []
        one_step.append(f"mountain_headcurve40/output.{i}.vts")
        one_step.append(f"mountain_headcurve80/output.{i}.vts")
        one_step.append(f"mountain_headcurve320/output.{i}.vts")
        one_step.append(f"mountain_backcurve40/output.{i}.vts")
        one_step.append(f"mountain_backcurve80/output.{i}.vts")
        one_step.append(f"mountain_backcurve320/output.{i}.vts")

        files.append(one_step)

    print("Found frames:", len(files))

    return files


def extract_number(path):
    # Extract the last integer in the filename
    nums = re.findall(r"\d+", path)
    return int(nums[-1])  # time index is usually the last number


def create_animation_directory():
    """Creates a directory for storing PNG frames if it doesn't exist."""
    os.makedirs("frames_multiview", exist_ok=True)


def create_frames(
    reader,
    render_window,
    filters,
    timestamp_actor,
    wind,
    wind_label,
    stream_tuple,
    files,
):
    create_animation_directory()
    w2if, png = setup_frame(render_window)

    for frame_id, step in enumerate(files):
        print(f"Frame {frame_id + 1}/{len(files)}")

        for i, fname in enumerate(step):
            print(f" → {fname}")
            reader.SetFileName(fname)
            reader.Update()
            grid = reader.GetOutput()

            # Update timestep text
            print(fname)
            if fname == "mountain_headcurve320/output.65000.vts":
                update_timestep_text(timestamp_actor[i], 64000)
            else:
                update_timestep_text(timestamp_actor[i], extract_number(fname))

            # Update wind arrow
            mean_u, mean_v, mean_w = compute_mean_wind_direction(grid)
            update_wind_arrow(
                wind[i],
                mean_u,
                mean_v,
                mean_w,
            )

            speed_value = wind_speed(mean_u, mean_v, mean_w)
            update_wind_speed_follower(
                wind_label[i],
                wind[i][0],
                speed_value,
            )

            # Update wind streamlines
            update_wind_streamlines(stream_tuple[i], grid)

            # Update all filters at once
            for f in filters[i].values():
                f.SetInputData(grid)
                f.Update()

        render_window.Render()
        w2if.Modified()

        png.SetFileName(f"frames_multiview/frame_{extract_number(fname)}.png")
        png.Write()

    print("\nDone writing PNG frames!")
