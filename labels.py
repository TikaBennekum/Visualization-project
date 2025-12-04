"""
Text overlays for titles and timestep display.
"""

import vtk


def make_title(
    terrain_type,
    fire_type=None,
    curvature=None,
):
    """Creates a static title actor for all frames."""
    title = vtk.vtkTextActor()
    title.SetInput("Fire Spread Simulation")

    tp = title.GetTextProperty()
    tp.SetFontSize(32)
    tp.SetBold(True)
    tp.SetColor(1, 1, 1)
    tp.SetFontFamilyToArial()
    tp.SetJustificationToCentered()

    title.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    title.SetPosition(0.5, 0.95)  # centered at top

    terrain = terrain_type.lower()

    if terrain == "valley":
        text = "Los Alamos Los Conchas Valley"
    elif terrain == "mountain":
        if fire_type is None:
            raise ValueError("Mountain simulations require fire_type.")
        if curvature is None:
            raise ValueError("Mountain simulations require curvature.")
        text = f"Mountain — {fire_type.capitalize()} (Curvature {curvature})"
    else:
        raise ValueError("terrain_type must be 'mountain' or 'valley'")

    subtitle = vtk.vtkTextActor()
    subtitle.SetInput(text)
    sub_prop = subtitle.GetTextProperty()
    sub_prop.SetFontFamilyToArial()
    sub_prop.SetFontSize(28)
    sub_prop.SetColor(1, 1, 1)
    sub_prop.SetBold(False)
    sub_prop.SetJustificationToCentered()

    subtitle.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    subtitle.SetPosition(0.5, 0.92)

    return title, subtitle


def make_timestep_text():
    """Creates a text actor that will display the timestep."""
    txt = vtk.vtkTextActor()
    txt.SetInput("Time step: 0")

    tp = txt.GetTextProperty()
    tp.SetFontSize(28)
    tp.SetBold(True)
    tp.SetColor(1.0, 1.0, 1.0)
    tp.SetFontFamilyToArial()
    tp.SetJustificationToCentered()

    txt.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    txt.SetPosition(0.5, 0.89)

    return txt


def update_timestep_text(actor, timestep):
    """Updates the text content according to timestep."""
    actor.SetInput(f"Time step: {timestep}")
