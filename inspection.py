import vtk

reader = vtk.vtkXMLStructuredGridReader()
reader.SetFileName("output.70000.vts")
reader.Update()

grid = reader.GetOutput()
theta = grid.GetPointData().GetArray("theta")

min_val = theta.GetRange()[0]
max_val = theta.GetRange()[1]

print("theta range:", min_val, max_val)
