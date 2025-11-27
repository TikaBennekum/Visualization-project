"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    Here the visualization of fire and smoke is generated.
"""

import vtk


def make_iso_actor(grid, theta_name, iso_value, color, opacity):
    """ Makes iso actor. """
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

    return actor


def compute_fire_levels(theta_min):
    """ Defines at which level smoke is shown and at which level 
    fire is shown. """
    low = theta_min + 2.0  # smoke (cool)
    mid = theta_min + 4.0  # smoke (warmer)
    hi = theta_min + 5.5  # fire (hot)
    higher = theta_min + 7.0  # fire (hotter)
    very_hi = theta_min + 25  # fire (very hot)
    return low, mid, hi, higher, very_hi


def make_fire_smoke_actors(grid, theta_name, theta_min):
    """ Creates fire and smoke actors. """
    low, mid, hi, higher, very_hi = compute_fire_levels(theta_min)

    smoke_low = make_iso_actor(
        grid, theta_name, low, (0.7, 0.7, 0.7), 0.15
    )  # light gray
    smoke_mid = make_iso_actor(
        grid, theta_name, mid, (0.5, 0.5, 0.5), 0.30
    )  # dark grey
    fire_hi = make_iso_actor(grid, theta_name, hi, (1.0, 0.15, 0.0), 0.60)  # red
    fire_higher = make_iso_actor(
        grid, theta_name, higher, (1.0, 0.57, 0.05), 0.70
    )  # orange
    fire_very_hi = make_iso_actor(
        grid, theta_name, very_hi, (1.0, 0.85, 0.0), 0.80
    )  # yellow

    return (low, mid, hi, higher, very_hi), [
        smoke_low,
        smoke_mid,
        fire_hi,
        fire_higher,
        fire_very_hi,
    ]


def make_temperature_lut(low, very_hi):
    """ Creates visualization of fire and smoke. """
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(5)
    lut.SetRange(low, very_hi)
    lut.Build()

    colors = [
        (0.7, 0.7, 0.7),
        (0.5, 0.5, 0.5),
        (1.0, 0.15, 0.0),
        (1.0, 0.57, 0.05),
        (1.0, 0.85, 0.0),
    ]
    for i, color in enumerate(colors):
        lut.SetTableValue(i, *color, 1.0)
    return lut


def make_temperature_scalar_bar(lut):
    """ Makes scalar bar showing levels of temperature. """
    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(lut)
    scalar_bar.SetTitle("Temperature")
    scalar_bar.SetNumberOfLabels(5)
    scalar_bar.SetOrientationToVertical()
    scalar_bar.SetPosition(0.12, 0.1)
    scalar_bar.SetWidth(0.08)
    scalar_bar.SetHeight(0.8)
    scalar_bar.UnconstrainedFontSizeOn()
    scalar_bar.SetLabelFormat("%.1f")

    title_prop = scalar_bar.GetTitleTextProperty()
    title_prop.SetFontSize(24)
    title_prop.SetBold(True)
    title_prop.SetColor(1.0, 1.0, 1.0)
    title_prop.SetFontFamilyToArial()

    label_prop = scalar_bar.GetLabelTextProperty()
    label_prop.SetFontFamilyToArial()
    label_prop.SetBold(True)
    label_prop.SetFontSize(24)
    label_prop.SetColor(1, 1, 1)
    return scalar_bar
