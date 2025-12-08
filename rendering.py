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
    renderer.SetMaximumNumberOfPeels(50)
    renderer.SetOcclusionRatio(0.1)
    return renderer


def setup_camera(renderer):
    """Creates the angle at which we view the grid."""
    camera = renderer.GetActiveCamera()
    camera.SetPosition(1166, -2348, 2780)
    camera.SetFocalPoint(101.0, -1.0, 449)
    camera.SetViewUp(-0.269, 0.614, 0.742)
    renderer.ResetCameraClippingRange()


def make_window_and_interactor(size=(2560, 1440)):
    """
    Makes window and interactor.

    NOTE: This function no longer accepts a renderer argument.
    Renderers must be added to the returned render_window
    by the caller (main script) after setting their viewports.
    """
    render_window = vtk.vtkRenderWindow()
    # render_window.AddRenderer(renderer) <-- REMOVE THIS LINE

    # Set the size for the entire display window
    render_window.SetSize(*size)

    # General transparency settings (needed for Depth Peeling)
    render_window.SetAlphaBitPlanes(1)
    render_window.SetMultiSamples(0)

    # Gradient background is usually set per-renderer, but if you want
    # it for the entire window *before* renderers are added, you can leave it.
    # However, since you're setting background in make_renderer,
    # we can remove the background settings here to avoid confusion.
    # renderer.SetBackground(0.2, 0.2, 0.25) <-- REMOVE
    # renderer.SetBackground2(0.5, 0.5, 0.6) <-- REMOVE
    # renderer.GradientBackgroundOn() <-- REMOVE

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # 🌟 We can return the size here for use in 2D positioning if needed
    return render_window, interactor
