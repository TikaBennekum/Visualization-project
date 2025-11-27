"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    Makes outline actor.
"""

import vtk


def make_outline_actor(grid):
    """set up of a basic enviroment by setting up a simple domain outline."""
    outline_filter = vtk.vtkStructuredGridOutlineFilter()
    outline_filter.SetInputData(grid)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(outline_filter.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(1.0, 1.0, 1.0)
    actor.GetProperty().SetLineWidth(1.0)

    return actor
