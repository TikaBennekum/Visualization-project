"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    Rendering of the scene of the visualization.
"""

import vtk


def make_renderer(background=(0.1, 0.1, 0.15)):
    """Initiliazes rendering."""
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(*background)
    renderer.SetUseDepthPeeling(1)
    renderer.SetMaximumNumberOfPeels(200)
    renderer.SetOcclusionRatio(0.1)
    return renderer


def setup_camera(renderer):
    """Creates the angle at which we view the grid."""
    camera = renderer.GetActiveCamera()
    camera.SetPosition(1180, -2348, 2500)
    camera.SetFocalPoint(101.0, -1.0, 450)
    camera.SetViewUp(-0.269, 0.614, 0.742)

    renderer.ResetCameraClippingRange()


def make_window_and_interactor(renderer, size=(2000, 1440)):
    """Makes window and interactor."""
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(*size)

    # transparency settings
    render_window.SetAlphaBitPlanes(1)
    render_window.SetMultiSamples(0)

    # background
    renderer.SetBackground(0.2, 0.2, 0.25)
    renderer.SetBackground2(0.5, 0.5, 0.6)
    renderer.GradientBackgroundOn()

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    return render_window, interactor
