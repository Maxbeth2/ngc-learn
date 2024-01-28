import multiprocessing as mp
from multiprocessing.connection import Connection
from neural_forge.two_way import build_two_way
import tensorflow as tf
import numpy as np

from pynput.mouse import Controller

class InteractiveMultimodal(mp.Process):
    def __init__(self, send_pts, rec_mm):
        mp.Process.__init__(self)
        self.outbox = send_pts
        self.inbox = rec_mm
        self.model = build_two_way()
        self.mouse = Controller()
        self.package = {"pos_mu": None, "col_mu": None}
        self.pos = tf.zeros([1,2])
        self.col = tf.zeros([1,3])

    def run(self):
        self.inbox : Connection
        while True:
            if self.inbox.poll():
                pkg = self.inbox.recv()
                while self.inbox.poll():
                    self.inbox.recv()
                pos = pkg["pos"]
                col = pkg["col"]
                self.pos = tf.cast([np.array([pos[0], pos[1]])], dtype=tf.float32)
                self.col = tf.cast([col], dtype=tf.float32)

            
            self.model.settle(
                clamped_vars=([("pos", "z", self.pos),("col", "z", self.col)]),
                readout_vars=([("pos_mu", "phi(z)"),("col_mu", "phi(z)")])
            )

    def package_and_send(self, readouts, pos, col):
        self.send_pts : Connection
        self.send_pts.send(self.package)
