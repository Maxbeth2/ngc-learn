from processes.ngc_interactive import create_network
from ngclearn.engine.ngc_graph import NGCGraph
from processes.remote_plotter import RemotePlotter
from processes.ngc_interactive import GNCNProcess
from processes.sc_comm import SCComm
import multiprocessing as mp
import tensorflow as tf

import time as t

def help():
    print("RemotePlotter(rec, 30).start()")

if __name__ == '__main__':
    
    rec, snd = mp.Pipe()
    r_sc, s_sc = mp.Pipe()
    rp = RemotePlotter(rec, 40)
    ncn = GNCNProcess(snd, s_sc)
    synth = SCComm(r_sc)
    rp.start()
    ncn.start()
    synth.start()
