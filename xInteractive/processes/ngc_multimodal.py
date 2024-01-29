import multiprocessing as mp
from multiprocessing.connection import Connection
from neural_forge.two_way import build_two_way, build_deep_two_way
import tensorflow as tf
import numpy as np
from ngclearn.utils import io_utils

from pynput.mouse import Controller

class InteractiveMultimodal(mp.Process):
    def __init__(self, send_pts, rec_mm, rec_comm):
        mp.Process.__init__(self)
        self.outbox = send_pts
        self.inbox = rec_mm
        self.rec_comm = rec_comm
        self.model = build_deep_two_way()
        self.mouse = Controller()
        self.pos = tf.zeros([1,2])
        self.col = tf.zeros([1,3])
        self.n_i = 0
        self.package = {"pos_mu": None, "col_mu": None, "n_i": self.n_i}

    def run(self):
        opt = tf.optimizers.Adam()
        ones = tf.ones([1,2])
        self.inbox : Connection
        self.rec_comm : Connection
        while True:
            if self.rec_comm.poll():
                c = self.rec_comm.recv()
                if c: 
                    self.save_model()
            if self.inbox.poll():
                pkg = self.inbox.recv()
                while self.inbox.poll():
                    self.inbox.recv()
                pos = pkg["pos"]
                col = pkg["col"]
                self.pos = tf.cast([np.array([pos[0], pos[1]])], dtype=tf.float32)
                self.col = tf.cast([col], dtype=tf.float32)

            
            readouts, delta = self.model.settle(
                clamped_vars=([("pos", "z", self.pos),("col", "z", self.col)]),
                readout_vars=([("pos_mu", "phi(z)"),("col_mu", "phi(z)")])
            )
            self.package_and_send(readouts=readouts)
            for p in range(len(delta)):
                delta[p] = delta[p] * (1.0/(ones.shape[0] * 1.0))
            opt.apply_gradients(zip(delta, self.model.theta))
            self.model.apply_constraints()
            self.model.clear()
            self.n_i += 1

    def package_and_send(self, readouts):
        pos_mu = readouts[0][2].numpy()
        col_mu = readouts[1][2].numpy()
        self.package["pos_mu"] = ([pos_mu[0][0]], [pos_mu[0][1]])
        self.package["col_mu"] = (col_mu[0][0], col_mu[0][1], col_mu[0][2])
        self.outbox : Connection
        self.outbox.send(self.package)

    def save_model(self):
        print(f"saved_model at {self.n_i} iterations")
        io_utils.serialize(fname=f'xInteractive/saved_models/mm{self.n_i}.ngc', object=self.model)

