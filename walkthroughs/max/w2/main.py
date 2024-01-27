from ngc_interactive import create_network
from ngclearn.engine.ngc_graph import NGCGraph
from remote_plotter import RemotePlotter
import multiprocessing as mp
import tensorflow as tf


import time as t


if __name__ == '__main__':
    opt = tf.optimizers.Adam()
    ones = tf.ones([1,2])
    model = create_network()
    model : NGCGraph

    rec, snd = mp.Pipe()
    rp = RemotePlotter(rec, 30)
    rp.start()
    print("Blocking...")
    t.sleep(5)
    for i in range(1000):
        readouts, delta = model.settle(
            clamped_vars=[("z0", "z", ones)],
            readout_vars=[("mu0", "phi(z)")]
        )
        mu0 = readouts[0][2].numpy()
        snd.send([[mu0[0][0]], [mu0[0][1]]])
        for p in range(len(delta)):
            delta[p] = delta[p] * (1.0/(ones.shape[0] * 1.0))
        opt.apply_gradients(zip(delta, model.theta))
        model.apply_constraints()
        model.clear()
        # t.sleep(0.2)