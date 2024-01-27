import multiprocessing as mp
import multiprocessing.connection as mpc
import pyqtgraph as pg
from PyQt6 import QtGui, QtCore

class RemotePlotter(mp.Process):
    def __init__(self, conn, framerate):
        mp.Process.__init__(self)

        self.dt = int(1000.0 / framerate) 
        self.conn = conn

    def run(self):
        print(">Starting remote plotter...")
        self.sc = pg.ScatterPlotItem()

        app = pg.mkQApp("NGC monitor")
        win = pg.GraphicsLayoutWidget(show=True, title="Max NGC Monitor")
        win.resize(1000,600)
        win.setWindowTitle('NGC Monitor')

        p0 = win.addPlot(title="mu0")
        p0.addItem(self.sc)
        p5 = win.addPlot(title="Scatter plot, axis labels, log scale")

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(self.dt)
        timer.setInterval(self.dt)
        win.show()
        app.exec()


    
    def update(self):
        self.conn : mpc.Connection
        if self.conn.poll():
            vec = self.conn.recv()
            # print(f"VEC:{vec}")
            self.sc.addPoints(vec[0], vec[1])
            n = 0
            while self.conn.poll():
                self.conn.recv()
                n += 1
            # print(f">Remote plotter received {vec}\n")
            # print(f">Remote plotter flushed {n} items")