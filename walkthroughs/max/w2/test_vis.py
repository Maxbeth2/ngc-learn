"""
This example demonstrates many of the 2D plotting capabilities
in pyqtgraph. All of the plots may be panned/scaled by dragging with 
the left/right mouse buttons. Right click on any plot to show a context menu.
"""

import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

# app = pg.mkQApp("Plotting Example")
#mw = QtWidgets.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p5 = win.addPlot(title="Scatter plot, axis labels, log scale")
# x = np.random.normal(size=1000) * 1e-5
# y = x*1000 + 0.005 * np.random.normal(size=1000)
# y -= y.min()-1.0
# mask = x > 1e-15
# x = x[mask]
# y = y[mask]
# p5.plot(x, y, pen=None, symbol='o', symbolPen=None, symbolSize=10, symbolBrush=(100, 100, 255, 50))
p5.setLabel('left', "Y Axis", units='A')
p5.setLabel('bottom', "Y Axis", units='s')
p5.setLogMode(x=False, y=False)
x = np.random.normal(size=1000) * 1e-5
y = x*1000 + 0.005 * np.random.normal(size=1000)
y -= y.min()-1.0
mask = x > 1e-15
x = x[mask]
y = y[mask]
sc = pg.ScatterPlotItem(x,y, symbol='t')
p5.addItem(sc)
x = np.random.normal(size=1000) * 1e-5
y = x*1000 + 0.005 * np.random.normal(size=1000)
y -= y.min()-1.0
mask = x > 1e-15
x = x[mask]
y = y[mask]
sc.addPoints(x,y, symbol='o')





pg.exec()