from processes.ngc_interactive import create_network
from ngclearn.engine.ngc_graph import NGCGraph
from processes.remote_plotter import RemotePlotter
from processes.multimodal_monitor import MultimodalMonitor
from processes.ngc_interactive import GNCNProcess
from processes.ngc_multimodal import InteractiveMultimodal
from processes.sc_comm import SCComm
import multiprocessing as mp
import tensorflow as tf

import time as t

def help():
    print("RemotePlotter(rec, 30).start()")

if __name__ == '__main__':
    
    rec_pts, snd_pts = mp.Pipe()
    r_sc, s_sc = mp.Pipe()
    rec_mm, snd_mm = mp.Pipe()
    # rp = RemotePlotter(rec_pts, 40)
    rp = MultimodalMonitor(rec_pts, snd_mm, 40)
    # ncn = GNCNProcess(snd_pts)
    ncn = InteractiveMultimodal(snd_pts, rec_mm)
    synth = SCComm(r_sc)
    rp.start()
    ncn.start()
    synth.start()
