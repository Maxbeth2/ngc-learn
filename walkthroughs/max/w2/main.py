from ngc_interactive import create_network
from ngclearn.engine.ngc_graph import NGCGraph
from remote_plotter import RemotePlotter
from ngc_interactive import GNCNProcess
import multiprocessing as mp
import tensorflow as tf

import time as t


if __name__ == '__main__':
    
    rec, snd = mp.Pipe()
    rp = RemotePlotter(rec, 30)
    ncn = GNCNProcess(snd)
    rp.start()
    ncn.start()