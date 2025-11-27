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

def create_plane(grid):
    """ Creates black grid underneath forest that represents the burnt ground when all vegetation is gone. """
    # Colour the ground black
    slice0 = vtk.vtkExtractGrid()
    slice0.SetInputData(grid)
    slice0.SetVOI(0, 850, 0, 499, 0, 0)  # z = 0 -> ground layer
    slice0.Update()
    ground = slice0.GetOutput()

    black = vtk.vtkNamedColors().GetColor3d("Black")
    ground_mapper = vtk.vtkDataSetMapper()
    ground_mapper.SetInputData(ground)
    ground_mapper.SetScalarVisibility(False)

    ground_actor = vtk.vtkActor()
    ground_actor.SetMapper(ground_mapper)
    ground_actor.GetProperty().SetColor(black)

    return ground_actor
