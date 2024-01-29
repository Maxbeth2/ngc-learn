import multiprocessing as mp
import multiprocessing.connection as mpc
import pyqtgraph as pg
from PyQt6 import QtGui, QtCore, QtWidgets
import tensorflow as tf
import numpy as np
import pyqtgraph as pg
from tensorflow.keras.utils import img_to_array
from tensorflow.keras.utils import load_img
import math as m

_org_img= load_img('xInteractive/data/circles.png')
_img_array = img_to_array(_org_img)

#generate layout
class MultimodalMonitor(mp.Process):
    def __init__(self, inbox, outbox, commands, framerate):
        mp.Process.__init__(self)
        self.dt = int(1000.0 / framerate) 
        self.inbox = inbox
        self.outbox = outbox
        self.commands = commands
        self.package = {"pos": None, "color": None}
        self.colval = tf.zeros([1,3], dtype=tf.float32)
        
    def run(self):
        sz = 500
        # -----basic setup-----
        app = pg.mkQApp("Multimodal Monitor")
        win = pg.GraphicsLayoutWidget(show=True)
        win.resize(1200, 1200)
        win.setWindowTitle('Multimodal Monitor')
        samples_counter = pg.LabelItem(justify='left')
        label = pg.LabelItem(justify='right')
        layout = pg.LayoutWidget()
        layout.addWidget(win)
        layout.show()
        savecheck = QtWidgets.QCheckBox('save model')
        savecheck.setChecked(False)
        layout.addWidget(savecheck)
        win.addItem(samples_counter)
        win.addItem(label)
        # -----create and assign image element-----
        img = pg.ImageItem()
        img.setImage(_img_array)
        # -----create image display-----
        p0 = win.addPlot()
        p0.addItem(img)
        p0.setMaximumHeight(sz)
        p0.setMaximumWidth(sz)
        p0.setMinimumHeight(sz)
        p0.setMinimumWidth(sz)
        # -----crosshair-----
        vLine = pg.InfiniteLine(angle=90, movable=False)
        hLine = pg.InfiniteLine(angle=0, movable=False)
        p0.addItem(vLine, ignoreBounds=True)
        p0.addItem(hLine, ignoreBounds=True)
        vb = p0.vb
        # define event handlers
        def mouseMoved(evt):
            pos = evt
            if p0.sceneBoundingRect().contains(pos):
                mousePoint = vb.mapSceneToView(pos)
                vLine.setPos(mousePoint.x())
                hLine.setPos(mousePoint.y())
        def imageHoverEvent(event):
            """Show the position, pixel, and value under the mouse cursor.
            """
            if event.isExit():
                p0.setTitle("")
                return
            pos = event.pos()
            i, j = pos.y(), pos.x()
            i = int(np.clip(i, 0, _img_array.shape[0] - 1))
            j = int(np.clip(j, 0, _img_array.shape[1] - 1))
            val = _img_array[j, i]
            ppos = img.mapToParent(pos)
            x, y = ppos.x(), ppos.y()
            # print(x, y)
            self.package["pos"] = [x/sz,y/sz]
            self.package["col"] = [val[0]/255,val[1]/255,val[2]/255]
            self.outbox.send(self.package)
            p0.setTitle("pos: (%0.1f, %0.1f)  pixel: (%d, %d)  value: (%.3g, %.3g, %.3g)" % (x, y, i, j, val[0],val[1],val[2]))
        # assign event listeners
        p0.scene().sigMouseMoved.connect(mouseMoved)
        img.hoverEvent = imageHoverEvent

        # -----setup scatterplot-----
        preds = pg.ScatterPlotItem()
        z2 = pg.ScatterPlotItem()
        def update():
            self.inbox : mpc.Connection
            self.commands : mpc.Connection
            if savecheck.isChecked():
                self.commands.send(True)
                savecheck.setChecked(False)
            if self.inbox.poll():
                pkg = self.inbox.recv()
                pos_mu = pkg["pos_mu"]
                col_mu = pkg["col_mu"]
                r = int(col_mu[0] * 255)
                g = int(col_mu[1] * 255)
                b = int(col_mu[2] * 255)
                preds.addPoints(pos_mu[0], pos_mu[1], pen=(r,g,b))
                while self.inbox.poll():
                    self.inbox.recv()
        p1 = win.addPlot()
        p1.addItem(preds)
        p1.setMaximumHeight(500)
        p1.setMaximumWidth(500)
        p1.setMinimumHeight(500)
        p1.setMinimumWidth(500)
        # self.preds.addPoints([0.2, 0.5],[0.2, 0.8])






        timer = QtCore.QTimer()
        timer.timeout.connect(update)
        timer.start(self.dt)
        timer.setInterval(self.dt)

        app.exec()
    
    












