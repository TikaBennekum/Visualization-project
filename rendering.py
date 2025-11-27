"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    ...
"""

import vtk


def make_renderer(background=(0.1, 0.1, 0.15)):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(*background)
    return renderer


def setup_camera(renderer):
    camera = renderer.GetActiveCamera()
    camera.SetPosition(1166.9393086976156, -2348.8726187497973, 2780.6186615624197)
    camera.SetFocalPoint(101.0, -1.0, 449.6810739215296)
    camera.SetViewUp(-0.26897888898416095, 0.6143246476336248, 0.741792143791419)
    renderer.ResetCameraClippingRange()


def make_window_and_interactor(renderer, size=(900, 700)):
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(*size)

    # transparency settings
    render_window.SetAlphaBitPlanes(1)
    renderer.SetUseDepthPeeling(1)
    renderer.SetMaximumNumberOfPeels(100)
    renderer.SetOcclusionRatio(0.1)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    return render_window, interactor
