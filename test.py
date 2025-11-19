#!/usr/bin/env pvpython

from paraview.simple import *

# Load the .vts file
grid = XMLStructuredGridReader(FileName=["output.1000.vts"])

# Show the data
view = CreateRenderView()

display = Show(grid, view)
ColorBy(display, ('POINTS', 'theta'))

# Adjust color range for flame region
display.RescaleTransferFunctionToDataRange(False, False)
display.LookupTable.RGBPoints = [400, 0.0, 0.0, 1.0,   800, 1.0, 0.0, 0.0]

# Add contour of the fire (isosurface)
contour = Contour(Input=grid)
contour.ContourBy = ('POINTS', 'theta')
contour.Isosurfaces = [450, 550, 650, 750]

contourDisplay = Show(contour, view)
ColorBy(contourDisplay, ('POINTS', 'theta'))

Render()
