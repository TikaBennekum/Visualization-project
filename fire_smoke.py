"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    Here the visualization of fire and smoke is generated.
"""

import vtk


def make_iso_actor(grid, theta_name, iso_value, color, opacity):
    """Makes iso actor."""
    contour = vtk.vtkContourFilter()
    contour.SetInputData(grid)
    contour.SetInputArrayToProcess(
        0,
        0,
        0,
        vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
        theta_name,
    )
    contour.SetValue(0, iso_value)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(contour.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetOpacity(opacity)
    actor.GetProperty().SetSpecular(0.2)
    actor.GetProperty().SetDiffuse(0.8)
    actor.GetProperty().SetAmbient(0.1)

    # Fix transparency rendering
    prop = actor.GetProperty()
    prop.BackfaceCullingOff()  # Prevent hiding fire when viewed from behind
    prop.FrontfaceCullingOff()  # Same for front faces

    return actor, contour


def compute_fire_levels(theta_min):
    """Defines at which level smoke is shown and at which level
    fire is shown."""
    low = theta_min + 2.0  # smoke (cool)
    mid = theta_min + 4.0  # smoke (warmer)
    hi = theta_min + 5.5  # fire (hot)
    higher = theta_min + 7.0  # fire (hotter)
    very_hi = theta_min + 25  # fire (very hot)

    print("Fire and smoke levels:", low, mid, hi, higher, very_hi)
    return low, mid, hi, higher, very_hi


def get_fire_colors():
    return {
        "low": (0.7, 0.7, 0.7),  # light gray
        "mid": (0.5, 0.5, 0.5),  # dark grey
        "hi": (1.0, 0.15, 0.0),  # red
        "higher": (1.0, 0.57, 0.05),  # orange
        "very_hi": (1.0, 0.85, 0.0),  # yellow
    }


def make_fire_smoke_actors(grid, theta_name, theta_min):
    """Creates fire and smoke actors."""
    low, mid, hi, higher, very_hi = compute_fire_levels(theta_min)
    colors = get_fire_colors()

    smoke_low, smoke_contour_low = make_iso_actor(
        grid, theta_name, low, colors["low"], 0.15
    )  # light gray
    smoke_mid, smoke_contour_mid = make_iso_actor(
        grid, theta_name, mid, colors["mid"], 0.30
    )  # dark grey
    fire_hi, fire_contour_hi = make_iso_actor(
        grid, theta_name, hi, colors["hi"], 0.60
    )  # red
    fire_higher, fire_contour_higher = make_iso_actor(
        grid, theta_name, higher, colors["higher"], 0.70
    )  # orange
    fire_very_hi, fire_contour_very_hi = make_iso_actor(
        grid, theta_name, very_hi, colors["very_hi"], 0.80
    )  # yellow

    return (
        (low, mid, hi, higher, very_hi),
        [
            smoke_low,
            smoke_mid,
            fire_hi,
            fire_higher,
            fire_very_hi,
        ],
        [
            smoke_contour_low,
            smoke_contour_mid,
            fire_contour_hi,
            fire_contour_higher,
            fire_contour_very_hi,
        ],
    )


def make_fire_legend(levels):
    """
    Build a discrete legend showing each isocontour level as a
    colored square with a text label.

    levels: list of 5 temperature values (low, mid, hi, higher, very_hi)

    Returns a list of (square_actor, text_actor).
    """
    legend_actors = []
    colors = get_fire_colors().values()

    # Position of top-most legend entry (NDC coordinates)
    x0 = 0.1  # horizontal position (left)
    y0 = 0.85  # start near the top
    dy = 0.05  # vertical spacing

    for i, (temp, col) in enumerate(zip(levels, colors)):
        y = y0 - i * dy

        # --- Colored square (vtkActor2D) ---
        square = vtk.vtkActor2D()
        square_mapper = vtk.vtkPolyDataMapper2D()

        # Create a square polygon
        pts = vtk.vtkPoints()
        polys = vtk.vtkCellArray()
        coords = [(0, 0), (30, 0), (30, 30), (0, 30)]
        for p in coords:
            pts.InsertNextPoint(p[0], p[1], 0)

        polys.InsertNextCell(4)
        polys.InsertCellPoint(0)
        polys.InsertCellPoint(1)
        polys.InsertCellPoint(2)
        polys.InsertCellPoint(3)

        square_poly = vtk.vtkPolyData()
        square_poly.SetPoints(pts)
        square_poly.SetPolys(polys)

        square_mapper.SetInputData(square_poly)
        square.SetMapper(square_mapper)

        square.GetProperty().SetColor(*col)

        # Position in normalized viewport coordinates
        square.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        square.SetPosition(x0, y)

        # --- Text label ---
        text = vtk.vtkTextActor()
        text.SetInput(f"{temp:.1f} K")
        text.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        text.SetPosition(x0 + 0.02, y - 0.001)
        tp = text.GetTextProperty()
        tp.SetColor(1, 1, 1)
        tp.SetFontSize(24)
        tp.SetBold(True)
        tp.SetFontFamilyToArial()

        legend_actors.append((square, text))

    return legend_actors
