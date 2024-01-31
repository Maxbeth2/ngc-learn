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
        # self.model = build_deep_two_way()
        self.model = io_utils.deserialize("xInteractive\saved_models\mm10770_noisy_rand.ngc")
        self.mouse = Controller()
        self.pos = tf.zeros([1,2])
        self.col = tf.zeros([1,3])
        self.n_i = 0
        self.package = {"pos_mu": None, "col_mu": None, "lat": None, "lat_col": None, "lat_pos": None, "n_i": self.n_i}



    def run(self):
        self.opt = tf.optimizers.Adam()
        self.ones = tf.ones([1,2])
        self.inbox : Connection
        self.rec_comm : Connection
        while True:
            self.check_GUI_commands()
            # receive inputs
            if self.inbox.poll():
                pkg = self.inbox.recv()
                pos = pkg["pos"]
                col = pkg["col"]
                self.pos = tf.cast([np.array([pos[0], pos[1]])], dtype=tf.float32)
                self.col = tf.cast([col], dtype=tf.float32)
                self.flush_residual_inputs()
            # model makes predictions
                readouts, delta = self.model.settle(
                    clamped_vars=([("pos", "z", self.pos),("col", "z", self.col)]),
                    readout_vars=([("pos_mu", "phi(z)"),("col_mu", "phi(z)"), ("lat", "phi(z)"), ("lat_col", "phi(z)"), ("lat_pos", "phi(z)")])
                )
                self.package_and_send_points(readouts=readouts)
                self.update_model(delta=delta)
                self.n_i += 1



    def package_and_send_points(self, readouts):
        pos_mu = readouts[0][2].numpy()
        col_mu = readouts[1][2].numpy()
        lats = readouts[2][2].numpy()
        col_lats = readouts[3][2].numpy()
        pos_lats = readouts[4][2].numpy()
        self.package["pos_mu"] = ([pos_mu[0][0]], [pos_mu[0][1]])
        self.package["col_mu"] = (col_mu[0][0], col_mu[0][1], col_mu[0][2])
        self.package["lat"] = (lats[0][0], lats[0][1], lats[0][2])
        self.package["lat_col"] = (col_lats[0][0], col_lats[0][1], col_lats[0][2])
        self.package["lat_pos"] = (pos_lats[0][0], pos_lats[0][1], pos_lats[0][2])
        self.package["n_i"] = self.n_i
        self.outbox : Connection
        self.outbox.send(self.package)
    
    def flush_residual_inputs(self):
        while self.inbox.poll():
            self.inbox.recv()

    def update_model(self, delta):
        for p in range(len(delta)):
                delta[p] = delta[p] * (1.0/(self.ones.shape[0] * 1.0))
        self.opt.apply_gradients(zip(delta, self.model.theta))
        self.model.apply_constraints()
        self.model.clear()

    def check_GUI_commands(self):
        if self.rec_comm.poll():
            c = self.rec_comm.recv()
            if c: 
                self.save_model()

    def save_model(self):
        print(f"saved_model at {self.n_i} iterations")
        io_utils.serialize(fname=f'xInteractive/saved_models/mm{self.n_i}.ngc', object=self.model)

