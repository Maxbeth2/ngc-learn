import pyqtgraph.examples
pyqtgraph.examples.run()

# """
# Demonstrates use of GLScatterPlotItem with rapidly-updating plots.
# """

# import numpy as np

# import pyqtgraph as pg
# import pyqtgraph.opengl as gl
# from pyqtgraph import functions as fn
# from pyqtgraph.Qt import QtCore

# app = pg.mkQApp("GLScatterPlotItem Example")
# layout = pg.LayoutWidget()
# w = gl.GLViewWidget()

# w.show()
# w.orbit(90, 50)

# w.setWindowTitle('pyqtgraph example: GLScatterPlotItem')
# w.setCameraPosition(distance=20)

# g = gl.GLGridItem()
# w.addItem(g)


# ##
# ##  First example is a set of points with pxMode=False
# ##  These demonstrate the ability to have points with real size down to a very small scale 
# ## 
# pos = np.empty((53, 3))
# size = np.empty((53))
# color = np.empty((53, 4))
# pos[0] = (1,0,0); size[0] = 0.5;   color[0] = (1.0, 0.0, 0.0, 0.5)
# pos[1] = (0,1,0); size[1] = 0.2;   color[1] = (0.0, 0.0, 1.0, 0.5)
# pos[2] = (0,0,1); size[2] = 2./3.; color[2] = (0.0, 1.0, 0.0, 0.5)

# z = 0.5
# d = 6.0
# for i in range(3,53):
#     pos[i] = (0,0,z)
#     size[i] = 2./d
#     color[i] = (0.0, 1.0, 0.0, 0.5)
#     z *= 0.5
#     d *= 2.0
    
# sp1 = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
# sp1.translate(5,5,0)
# w.addItem(sp1)


# ##
# ##  Second example shows a volume of points with rapidly updating color
# ##  and pxMode=True
# ##

# pos = np.random.random(size=(100000,3))
# pos *= [10,-10,10]
# pos[0] = (0,0,0)
# color = np.ones((pos.shape[0], 4))
# d2 = (pos**2).sum(axis=1)**0.5
# size = np.random.random(size=pos.shape[0])*10
# sp2 = gl.GLScatterPlotItem(pos=pos, color=(1,1,1,1), size=size)
# phase = 0.

# w.addItem(sp2)


# ##
# ##  Third example shows a grid of points with rapidly updating position
# ##  and pxMode = False
# ##

# pos3 = np.zeros((100,100,3))
# pos3[:,:,:2] = np.mgrid[:100, :100].transpose(1,2,0) * [-0.1,0.1]
# pos3 = pos3.reshape(10000,3)
# d3 = (pos3**2).sum(axis=1)**0.5

# sp3 = gl.GLScatterPlotItem(pos=pos3, color=(1,1,1,.3), size=0.1, pxMode=False)

# w.addItem(sp3)


# def update():
#     ## update volume colors
#     global phase, sp2, d2
#     s = -np.cos(d2*2+phase)
#     color = np.empty((len(d2),4), dtype=np.float32)
#     color[:,3] = fn.clip_array(s * 0.1, 0., 1.)
#     color[:,0] = fn.clip_array(s * 3.0, 0., 1.)
#     color[:,1] = fn.clip_array(s * 1.0, 0., 1.)
#     color[:,2] = fn.clip_array(s ** 3, 0., 1.)
#     sp2.setData(color=color)
#     phase -= 0.1
    
#     ## update surface positions and colors
#     global sp3, d3, pos3
#     z = -np.cos(d3*2+phase)
#     pos3[:,2] = z
#     color = np.empty((len(d3),4), dtype=np.float32)
#     color[:,3] = 0.3
#     color[:,0] = np.clip(z * 3.0, 0, 1)
#     color[:,1] = np.clip(z * 1.0, 0, 1)
#     color[:,2] = np.clip(z ** 3, 0, 1)
#     sp3.setData(pos=pos3, color=color)
    
# t = QtCore.QTimer()
# t.timeout.connect(update)
# t.start(50)

if __name__ == '__main__':
    pg.exec()


# """
# This example demonstrates the use of RemoteGraphicsView to improve performance in
# applications with heavy load. It works by starting a second process to handle 
# all graphics rendering, thus freeing up the main process to do its work.

# In this example, the update() function is very expensive and is called frequently.
# After update() generates a new set of data, it can either plot directly to a local
# plot (bottom) or remotely via a RemoteGraphicsView (top), allowing speed comparison
# between the two cases. IF you have a multi-core CPU, it should be obvious that the 
# remote case is much faster.
# """

# from time import perf_counter

# import numpy as np

# import pyqtgraph as pg
# from pyqtgraph.Qt import QtCore, QtWidgets

# app = pg.mkQApp()

# view = pg.widgets.RemoteGraphicsView.RemoteGraphicsView()
# pg.setConfigOptions(antialias=True)  ## this will be expensive for the local plot
# view.pg.setConfigOptions(antialias=True)  ## prettier plots at no cost to the main process! 
# view.setWindowTitle('pyqtgraph example: RemoteSpeedTest')

# app.aboutToQuit.connect(view.close)

# label = QtWidgets.QLabel()
# rcheck = QtWidgets.QCheckBox('plot remote')
# rcheck.setChecked(True)
# lcheck = QtWidgets.QCheckBox('plot local')
# lplt = pg.PlotWidget()
# layout = pg.LayoutWidget()
# layout.addWidget(rcheck)
# layout.addWidget(lcheck)
# layout.addWidget(label)
# layout.addWidget(view, row=1, col=0, colspan=3)
# layout.addWidget(lplt, row=2, col=0, colspan=3)
# layout.resize(800,800)
# layout.show()

# ## Create a PlotItem in the remote process that will be displayed locally
# rplt = view.pg.PlotItem()
# rplt._setProxyOptions(deferGetattr=True)  ## speeds up access to rplt.plot
# view.setCentralItem(rplt)

# lastUpdate = perf_counter()
# avgFps = 0.0

# def update():
#     global check, label, plt, lastUpdate, avgFps, rpltfunc
#     data = np.random.normal(size=(10000,50)).sum(axis=1)
#     data += 5 * np.sin(np.linspace(0, 10, data.shape[0]))
    
#     if rcheck.isChecked():
#         rplt.plot(data, clear=True, _callSync='off')  ## We do not expect a return value.
#                                                       ## By turning off callSync, we tell
#                                                       ## the proxy that it does not need to 
#                                                       ## wait for a reply from the remote
#                                                       ## process.
#     if lcheck.isChecked():
#         lplt.plot(data, clear=True)
        
#     now = perf_counter()
#     fps = 1.0 / (now - lastUpdate)
#     lastUpdate = now
#     avgFps = avgFps * 0.8 + fps * 0.2
#     label.setText("Generating %0.2f fps" % avgFps)
        
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(0)

# if __name__ == '__main__':
#     pg.exec()









# """
# Demonstrates common image analysis tools.

# Many of the features demonstrated here are already provided by the ImageView
# widget, but here we present a lower-level approach that provides finer control
# over the user interface.
# """

# import numpy as np

# import pyqtgraph as pg
# from pyqtgraph.Qt import QtGui

# # Interpret image data as row-major instead of col-major
# pg.setConfigOptions(imageAxisOrder='row-major')

# pg.mkQApp()
# win = pg.GraphicsLayoutWidget()
# win.setWindowTitle('pyqtgraph example: Image Analysis')

# # A plot area (ViewBox + axes) for displaying the image
# p1 = win.addPlot(title="")

# # Item for displaying image data
# img = pg.ImageItem()
# p1.addItem(img)

# # Custom ROI for selecting an image region
# roi = pg.ROI([-8, 14], [6, 5])
# roi.addScaleHandle([0.5, 1], [0.5, 0.5])
# roi.addScaleHandle([0, 0.5], [0.5, 0.5])
# p1.addItem(roi)
# roi.setZValue(10)  # make sure ROI is drawn above image

# # Isocurve drawing
# iso = pg.IsocurveItem(level=0.8, pen='g')
# iso.setParentItem(img)
# iso.setZValue(5)

# # Contrast/color control
# hist = pg.HistogramLUTItem()
# hist.setImageItem(img)
# win.addItem(hist)

# # Draggable line for setting isocurve level
# isoLine = pg.InfiniteLine(angle=0, movable=True, pen='g')
# hist.vb.addItem(isoLine)
# hist.vb.setMouseEnabled(y=False) # makes user interaction a little easier
# isoLine.setValue(0.8)
# isoLine.setZValue(1000) # bring iso line above contrast controls

# # Another plot area for displaying ROI data
# win.nextRow()
# p2 = win.addPlot(colspan=2)
# p2.setMaximumHeight(250)
# win.resize(800, 800)
# win.show()


# # Generate image data
# data = np.random.normal(size=(200, 100))
# data[20:80, 20:80] += 2.
# data = pg.gaussianFilter(data, (3, 3))
# data += np.random.normal(size=(200, 100)) * 0.1
# img.setImage(data)
# hist.setLevels(data.min(), data.max())

# # build isocurves from smoothed data
# iso.setData(pg.gaussianFilter(data, (2, 2)))

# # set position and scale of image
# tr = QtGui.QTransform()
# img.setTransform(tr.scale(0.2, 0.2).translate(-50, 0))

# # zoom to fit imageo
# p1.autoRange()  


# # Callbacks for handling user interaction
# def updatePlot():
#     global img, roi, data, p2
#     selected = roi.getArrayRegion(data, img)
#     p2.plot(selected.mean(axis=0), clear=True)

# roi.sigRegionChanged.connect(updatePlot)
# updatePlot()

# def updateIsocurve():
#     global isoLine, iso
#     iso.setLevel(isoLine.value())

# isoLine.sigDragged.connect(updateIsocurve)

# def imageHoverEvent(event):
#     """Show the position, pixel, and value under the mouse cursor.
#     """
#     if event.isExit():
#         p1.setTitle("")
#         return
#     pos = event.pos()
#     i, j = pos.y(), pos.x()
#     i = int(np.clip(i, 0, data.shape[0] - 1))
#     j = int(np.clip(j, 0, data.shape[1] - 1))
#     val = data[i, j]
#     ppos = img.mapToParent(pos)
#     x, y = ppos.x(), ppos.y()
#     p1.setTitle("pos: (%0.1f, %0.1f)  pixel: (%d, %d)  value: %.3g" % (x, y, i, j, val))

# # Monkey-patch the image to use our custom hover function. 
# # This is generally discouraged (you should subclass ImageItem instead),
# # but it works for a very simple use like this. 
# img.hoverEvent = imageHoverEvent

# if __name__ == '__main__':
#     pg.exec()








































# """
# Demonstrates some customized mouse interaction by drawing a crosshair that follows 
# the mouse.
# """

# import numpy as np

# import pyqtgraph as pg

# #generate layout
# app = pg.mkQApp("Crosshair Example")
# win = pg.GraphicsLayoutWidget(show=True)
# win.setWindowTitle('pyqtgraph example: crosshair')
# label = pg.LabelItem(justify='right')
# win.addItem(label)
# p1 = win.addPlot(row=1, col=0)
# # customize the averaged curve that can be activated from the context menu:
# p1.avgPen = pg.mkPen('#FFFFFF')
# p1.avgShadowPen = pg.mkPen('#8080DD', width=10)

# p2 = win.addPlot(row=2, col=0)

# region = pg.LinearRegionItem()
# region.setZValue(10)
# # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this 
# # item when doing auto-range calculations.
# p2.addItem(region, ignoreBounds=True)

# #pg.dbg()
# p1.setAutoVisible(y=True)


# #create numpy arrays
# #make the numbers large to show that the range shows data from 10000 to all the way 0
# data1 = 10000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)
# data2 = 15000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)

# p1.plot(data1, pen="r")
# p1.plot(data2, pen="g")

# p2d = p2.plot(data1, pen="w")
# # bound the LinearRegionItem to the plotted data
# region.setClipItem(p2d)

# def update():
#     region.setZValue(10)
#     minX, maxX = region.getRegion()
#     p1.setXRange(minX, maxX, padding=0)    

# region.sigRegionChanged.connect(update)

# def updateRegion(window, viewRange):
#     rgn = viewRange[0]
#     region.setRegion(rgn)

# p1.sigRangeChanged.connect(updateRegion)

# region.setRegion([1000, 2000])

# #cross hair
# vLine = pg.InfiniteLine(angle=90, movable=False)
# hLine = pg.InfiniteLine(angle=0, movable=False)
# p1.addItem(vLine, ignoreBounds=True)
# p1.addItem(hLine, ignoreBounds=True)


# vb = p1.vb

# def mouseMoved(evt):
#     pos = evt
#     if p1.sceneBoundingRect().contains(pos):
#         mousePoint = vb.mapSceneToView(pos)
#         index = int(mousePoint.x())
#         if index > 0 and index < len(data1):
#             label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
#         vLine.setPos(mousePoint.x())
#         hLine.setPos(mousePoint.y())



# p1.scene().sigMouseMoved.connect(mouseMoved)


# if __name__ == '__main__':
#     pg.exec()