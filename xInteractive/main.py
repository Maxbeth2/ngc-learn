# from processes.ngc_interactive import create_network
# from ngclearn.engine.ngc_graph import NGCGraph
# from processes.remote_plotter import RemotePlotter
from processes.multimodal_monitor import MultimodalMonitor
# from processes.ngc_interactive import GNCNProcess
from processes.ngc_multimodal import InteractiveMultimodal
from processes.sc_comm import SCComm
import multiprocessing as mp

def help():
    print("RemotePlotter(rec, 30).start()")

if __name__ == '__main__':    
    rec_pts, snd_pts = mp.Pipe()
    rec_sc, snd_sc = mp.Pipe()
    rec_mm, snd_mm = mp.Pipe()
    rec_comm, snd_comm = mp.Pipe()
    # rp = RemotePlotter(rec_pts, 40)
    rp = MultimodalMonitor(inbox=rec_pts, commands=snd_comm, outbox=snd_mm, framerate=40)
    # ncn = GNCNProcess(snd_pts)
    ncn = InteractiveMultimodal(send_pts=snd_pts, rec_mm=rec_mm, rec_comm=rec_comm)
    synth = SCComm(rec_sc)
    rp.start()
    ncn.start()
    synth.start()