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
    Build a discrete legend showing each isocontour level as
    a colored square with a text label + a title + grey background box.

    Returns a list of actors.
    """
    legend_actors = []
    colors = list(get_fire_colors().values())

    # Legend layout (NDC coordinates)
    x0 = 0.1  # left position
    y0 = 0.85  # top position
    dy = 0.06  # vertical spacing
    sq_px = 24  # square size (pixels)

    # -------------------------
    #  Background box
    # -------------------------
    bg = vtk.vtkActor2D()
    bg_mapper = vtk.vtkPolyDataMapper2D()

    # Simple rectangle in pixel space
    bg_pts = vtk.vtkPoints()
    bg_polys = vtk.vtkCellArray()

    # Width/height of box in pixels
    box_w = 400
    box_h = int(60 + len(levels) * 85)

    bg_pts.InsertNextPoint(0, 0, 0)
    bg_pts.InsertNextPoint(box_w, 0, 0)
    bg_pts.InsertNextPoint(box_w, box_h, 0)
    bg_pts.InsertNextPoint(0, box_h, 0)

    bg_polys.InsertNextCell(4)
    for i in range(4):
        bg_polys.InsertCellPoint(i)

    bg_poly = vtk.vtkPolyData()
    bg_poly.SetPoints(bg_pts)
    bg_poly.SetPolys(bg_polys)

    bg_mapper.SetInputData(bg_poly)
    bg.SetMapper(bg_mapper)

    bg.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    bg.SetPosition(x0 - 0.02, y0 - (len(levels) - 1) * dy - 0.02)

    bg.GetProperty().SetColor(0.3, 0.3, 0.3)  # light gray
    bg.GetProperty().SetOpacity(0.6)

    legend_actors.append(bg)

    # -------------------------
    #  Title
    # -------------------------
    title = vtk.vtkTextActor()
    title.SetInput("Temperature")
    title.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    title.SetPosition(x0, y0 + 0.03)

    tp = title.GetTextProperty()
    tp.SetColor(1, 1, 1)
    tp.SetFontSize(28)
    tp.SetBold(True)
    tp.SetFontFamilyToArial()

    legend_actors.append(title)

    # -------------------------
    #  Squares + labels
    # -------------------------
    for i, (temp, col) in enumerate(zip(levels, colors)):
        y = y0 - i * dy

        # --- Colored square (2D polydata) ---
        square = vtk.vtkActor2D()
        square_mapper = vtk.vtkPolyDataMapper2D()

        pts = vtk.vtkPoints()
        polys = vtk.vtkCellArray()

        # Square geometry in pixel coordinates
        pts.InsertNextPoint(0, 0, 0)
        pts.InsertNextPoint(sq_px, 0, 0)
        pts.InsertNextPoint(sq_px, sq_px, 0)
        pts.InsertNextPoint(0, sq_px, 0)

        polys.InsertNextCell(4)
        for j in range(4):
            polys.InsertCellPoint(j)

        sq_poly = vtk.vtkPolyData()
        sq_poly.SetPoints(pts)
        sq_poly.SetPolys(polys)

        square_mapper.SetInputData(sq_poly)
        square.SetMapper(square_mapper)
        square.GetProperty().SetColor(*col)

        square.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        square.SetPosition(x0, y)

        legend_actors.append(square)

        # --- Label text ---
        text = vtk.vtkTextActor()
        text.SetInput(f"{temp:.1f} K")
        text.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        text.SetPosition(x0 + 0.04, y + 0.002)

        tp = text.GetTextProperty()
        tp.SetColor(1, 1, 1)
        tp.SetFontSize(24)
        tp.SetBold(True)
        tp.SetFontFamilyToArial()

        legend_actors.append(text)

    return legend_actors
