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
import pyqtgraph.opengl as gl
import random as r



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
        self.n_lat = 0
        
    def run(self):
        _org_img= load_img('xInteractive/data/circles_noisy.png')
        _img_array = img_to_array(_org_img)
        sz = 500
        # -----basic setup-----
        app = pg.mkQApp("Multimodal Monitor")
        win = pg.GraphicsLayoutWidget(show=True)
        win.resize(1200, 600)
        win.setWindowTitle('Multimodal Monitor')
        #GL 3D window
        glw = gl.GLViewWidget()
        g = gl.GLGridItem()
        glw.addItem(g)
        glw.show()
        # 2d plot layout
        layout = pg.LayoutWidget()
        layout.addWidget(win)
        layout.show()
        random_sample = QtWidgets.QCheckBox('r_samp')
        random_sample.setChecked(True)
        savecheck = QtWidgets.QCheckBox('save ncn')
        savecheck.setChecked(False)
        layout.addWidget(savecheck)
        layout.addWidget(random_sample)
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
            if random_sample.isChecked():
                return
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
        # -----setup scatterplot-----¨
        lats = np.empty((300,3))
        pos_lats = np.empty((300,3))
        col_lats = np.empty((300,3))
        preds = pg.ScatterPlotItem()
        p3d = gl.GLScatterPlotItem(color=[1.0,1.0,1.0,0.2])
        p3dc = gl.GLScatterPlotItem(color=[0.0,1.0,0.0,0.2])
        p3dp = gl.GLScatterPlotItem(color=[1.0,0.0,0.0,0.2])
        # z2 = pg.ScatterPlotItem()
        p1 = win.addPlot()
        rand = r
        def update():
            if random_sample.isChecked():
                i = rand.randint(0,sz-1)
                j = rand.randint(0,sz-1)
                val = _img_array[i, j]
                # print(x, y)
                self.package["pos"] = [i/sz,j/sz]
                self.package["col"] = [val[0]/255,val[1]/255,val[2]/255]
                self.outbox.send(self.package)
            glw.orbit(azim=1, elev=0)
            self.inbox : mpc.Connection
            self.commands : mpc.Connection
            if savecheck.isChecked():
                self.commands.send(True)
                savecheck.setChecked(False)
            if self.inbox == None:
                return
            if self.inbox.poll():
                pkg = self.inbox.recv()
                n_i = pkg["n_i"]
                p1.setTitle(f"samples seen: {n_i}")
                pos_mu = pkg["pos_mu"]
                col_mu = pkg["col_mu"]
                lat = pkg["lat"]
                col_lat = pkg["lat_col"]
                pos_lat = pkg["lat_pos"]
                self.n_lat %= 299
                lats[self.n_lat] = lat
                col_lats[self.n_lat] = col_lat
                pos_lats[self.n_lat] = pos_lat
                self.n_lat += 1
                p3d.setData(pos=lats)
                p3dc.setData(pos=col_lats)
                p3dc.setData(pos=col_lats)
                p3dp.setData(pos=pos_lats)
                r = int(col_mu[0] * 255)
                g = int(col_mu[1] * 255)
                b = int(col_mu[2] * 255)
                preds.addPoints(pos_mu[0], pos_mu[1], pen=(r,g,b))
                while self.inbox.poll():
                    self.inbox.recv()
        
        
        glw.addItem(p3d)
        glw.addItem(p3dc)
        glw.addItem(p3dp)
        
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
    
    







if __name__ == '__main__':
    import matplotlib.pyplot as plt

    _org_img= load_img('xInteractive/data/circles.png')
    _img_array = img_to_array(_org_img)
    white_px = np.array([255,255,255])
    for i in range(_img_array.shape[0]):
        for j in range(_img_array.shape[1]):
            if np.array_equal(_img_array[i, j], [255, 255, 255]):
                # Replace [255, 255, 255] with noise (you can use np.random for noise)
                _img_array[i, j] = np.random.randint(0, 256, size=3)
    _img_array = _img_array / 255.0
    plt.imsave(fname="xInteractive\data\circles_noisy.png", arr=_img_array)
# Now, arr has been modified with noise replacing [255, 255, 255]
    # print(_img_array)






