import vtk

reader = vtk.vtkXMLStructuredGridReader()
reader.SetFileName("mountain_backcurve40/output.30000.vts")
reader.Update()

grid = reader.GetOutput()
theta = grid.GetPointData().GetArray("theta")
rhof_1 = grid.GetPointData().GetArray("rhof_1")

min_val = theta.GetRange()[0]
max_val = theta.GetRange()[1]

print("theta range:", min_val, max_val)
print("rhof_1 range:", rhof_1.GetRange())
