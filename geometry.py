"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    ...
"""

import vtk


def make_outline_actor(grid):
    outline_filter = vtk.vtkStructuredGridOutlineFilter()
    outline_filter.SetInputData(grid)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(outline_filter.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(1.0, 1.0, 1.0)
    actor.GetProperty().SetLineWidth(1.0)

    return actor
