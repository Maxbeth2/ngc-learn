import multiprocessing as mp
import multiprocessing.connection as mpc
import pyqtgraph as pg
from PyQt6 import QtGui, QtCore
import tensorflow as tf


# class MultimodalMonitorQ(mp.Process):
#     def __init__(self, conn, framerate):
#         mp.Process.__init__(self)
#         self.dt = int(1000.0 / framerate) 
#         self.conn = conn
        
#     def run(self):
#         print(">Starting multimodal monitor...")
#         self.preds = pg.ScatterPlotItem()
#         self.latent1 = pg.ScatterPlotItem()

#         app = pg.mkQApp("Multimodal Monitor")
#         win = pg.GraphicsLayoutWidget(show=True, title="Multimodal Monitor")
#         win.resize(1000, 600)
#         p0 = win.addPlot(title="preds")

        
#         p0.addItem(self.preds)

#         vLine = pg.InfiniteLine(angle=90, movable=False)
#         hLine = pg.InfiniteLine(angle=0, movable=False)
#         p0.addItem(vLine, ignoreBounds=True)
#         p0.addItem(hLine, ignoreBounds=True)
#         vb = p0.vb
#         def mouseMoved(self, evt):
#             pos = evt
#             if p0.sceneBoundingRect().contains(pos):
#                 mousePoint = vb.mapSceneToView(pos)
#                 # index = int(mousePoint.x())
#                 # if index > 0 and index < len(data1):
#                 #     label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
#                 self.vLine.setPos(mousePoint.x())
#                 self.hLine.setPos(mousePoint.y())

#         p0.scene().sigMouseMoved.connect(mouseMoved)

        



       

#         timer = QtCore.QTimer()
#         timer.timeout.connect(self.update)
#         timer.start(self.dt)
#         timer.setInterval(self.dt)
#         win.show()
#         app.exec()
    
#     def update(self):
#         self.conn : mpc.Connection
#         # pkg = self.conn.recv()









import numpy as np

import pyqtgraph as pg

from tensorflow.keras.utils import img_to_array
from tensorflow.keras.utils import load_img

_org_img= load_img('xInteractive/data/circles.png')
_img_array = img_to_array(_org_img)

#generate layout
class MultimodalMonitor(mp.Process):
    def __init__(self, inbox, outbox, framerate):
        mp.Process.__init__(self)
        self.dt = int(1000.0 / framerate) 
        self.inbox = inbox
        self.outbox = outbox
        self.package = {"pos": None, "color": None}
        self.colval = tf.zeros([1,3], dtype=tf.float32)
        
    def run(self):
        app = pg.mkQApp("Multimodal Monitor")
        win = pg.GraphicsLayoutWidget(show=True)
        win.resize(1000, 600)
        win.setWindowTitle('Multimodal Monitor')
        label = pg.LabelItem(justify='right')
        win.addItem(label)
        p1 = win.addPlot()
        img = pg.ImageItem()
        p1.addItem(img) # <----------------
        img.setImage(_img_array)
        p1.setMaximumHeight(500)
        p1.setMaximumWidth(500)
        p1.setMinimumHeight(500)
        p1.setMinimumWidth(500)
        self.sc = pg.ScatterPlotItem()
        self.z2 = pg.ScatterPlotItem()
        p1.addItem(self.sc)

        vLine = pg.InfiniteLine(angle=90, movable=False)
        hLine = pg.InfiniteLine(angle=0, movable=False)
        p1.addItem(vLine, ignoreBounds=True)
        p1.addItem(hLine, ignoreBounds=True)
        vb = p1.vb
        self.outbox : mpc.Connection
        # def mouseMoved(evt):
        #     pos = evt
        #     if p1.sceneBoundingRect().contains(pos):
        #         mousePoint = vb.mapSceneToView(pos)
        #         vLine.setPos(mousePoint.x())
        #         hLine.setPos(mousePoint.y())
        #         self.package["pos"] = [mousePoint.x(), mousePoint.y()]
        #         self.outbox.send(self.package)
        
        def imageHoverEvent(event):
            """Show the position, pixel, and value under the mouse cursor.
            """
            if event.isExit():
                p1.setTitle("")
                return
            pos = event.pos()
            i, j = pos.y(), pos.x()
            i = int(np.clip(i, 0, _img_array.shape[0] - 1))
            j = int(np.clip(j, 0, _img_array.shape[1] - 1))
            val = _img_array[j, i]
            # print(val)
            ppos = img.mapToParent(pos)
            x, y = ppos.x(), ppos.y()

            self.package["pos"] = [x,y]
            self.package["col"] = [val[0],val[1],val[2]]
            self.outbox.send(self.package)

            p1.setTitle("pos: (%0.1f, %0.1f)  pixel: (%d, %d)  value: (%.3g, %.3g, %.3g)" % (x, y, i, j, val[0],val[1],val[2]))
        
        # p1.scene().sigMouseMoved.connect(mouseMoved)
        img.hoverEvent = imageHoverEvent

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(self.dt)
        timer.setInterval(self.dt)

        app.exec()
    
    def update(self):
        self.inbox : mpc.Connection
        if self.inbox.poll():
            pkg = self.inbox.recv()


            while self.inbox.poll():
                self.inbox.recv()














class RemotePlotter(mp.Process):
    def __init__(self, conn, framerate):
        mp.Process.__init__(self)

        self.dt = int(1000.0 / framerate) 
        self.conn = conn

    def run(self):
        print(">Starting remote plotter...")
        self.sc = pg.ScatterPlotItem()
        self.z2 = pg.ScatterPlotItem()

        app = pg.mkQApp("NGC monitor")
        win = pg.GraphicsLayoutWidget(show=True, title="Max NGC Monitor")
        win.resize(1000,600)
        win.setWindowTitle('NGC Monitor')

        p0 = win.addPlot(title="mu0")
        p0.addItem(self.sc)
        p1 = win.addPlot(title="Scatter plot, axis labels, log scale")
        p1.addItem(self.z2)

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(self.dt)
        timer.setInterval(self.dt)
        win.show()
        app.exec()


    
    def update(self):
        self.conn : mpc.Connection
        if self.conn.poll():
            pkg = self.conn.recv()
            # mu0 = self.conn.recv()
            # readouts = self.conn.recv()
            # mu0 = readouts[0][2].numpy()
            mu0 = pkg["mu0"]
            x = pkg["x"]
            z2 = pkg["z2"]
            # print(f"VEC:{vec}")
            self.sc.addPoints(mu0[0],mu0[1], pen='b')
            self.sc.addPoints(x[0], x[1], pen='r')
            self.z2.addPoints(z2[0], z2[1])
            n = 0
            while self.conn.poll():
                self.conn.recv()
                n += 1
            # print(f">Remote plotter received {vec}\n")
            # print(f">Remote plotter flushed {n} items")