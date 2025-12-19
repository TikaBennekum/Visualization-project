"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    File to inspect data attributes.
"""

import vtk

reader = vtk.vtkXMLStructuredGridReader()
reader.SetFileName("mountain_backcurve40/output.70000.vts")
reader.Update()

grid = reader.GetOutput()
theta = grid.GetPointData().GetArray("theta")

min_val = theta.GetRange()[0]
max_val = theta.GetRange()[1]

print("theta range:", min_val, max_val)
