"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    ...
"""

import vtk


def make_vegetation_actor(grid, rhof_1_name="rhof_1", isovalues=None):
    if isovalues is None:
        isovalues = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

    rhof_1 = grid.GetPointData().GetArray(rhof_1_name)
    rhof_1_min, rhof_1_max = rhof_1.GetRange()

    contour = vtk.vtkContourFilter()
    contour.SetInputData(grid)
    contour.SetInputArrayToProcess(
        0,
        0,
        0,
        vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
        rhof_1_name,
    )

    for i, value in enumerate(isovalues):
        contour.SetValue(i, value)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(contour.GetOutputPort())
    mapper.SetScalarModeToUsePointFieldData()
    mapper.SelectColorArray(rhof_1_name)
    mapper.SetScalarRange(0, 0.6)

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    lut.SetRange(rhof_1_min, rhof_1_max)
    lut.SetHueRange(0.33, 0.33)
    lut.SetValueRange(1.0, 0.4)
    lut.SetSaturationRange(0.6, 1.0)
    lut.Build()

    mapper.SetLookupTable(lut)
    mapper.SetUseLookupTableScalarRange(True)
    mapper.ScalarVisibilityOn()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor, lut


def make_vegetation_scalar_bar(lut):
    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(lut)
    scalar_bar.SetTitle("Vegetation density")
    scalar_bar.SetNumberOfLabels(5)
    scalar_bar.SetOrientationToVertical()
    scalar_bar.SetPosition(0.88, 0.1)
    scalar_bar.SetWidth(0.08)
    scalar_bar.SetHeight(0.8)
    scalar_bar.UnconstrainedFontSizeOn()

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
