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
            package = self.conn.recv()
            # mu0 = self.conn.recv()
            # readouts = self.conn.recv()
            # mu0 = readouts[0][2].numpy()
            mu0 = package["mu0"]
            x = package["x"]
            # print(f"VEC:{vec}")
            self.sc.addPoints(mu0[0],mu0[1], pen='b')
            self.sc.addPoints(x[0], x[1], pen='r')
            n = 0
            while self.conn.poll():
                self.conn.recv()
                n += 1
            # print(f">Remote plotter received {vec}\n")
            # print(f">Remote plotter flushed {n} items")