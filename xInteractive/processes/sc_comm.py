import multiprocessing as mp
import multiprocessing.connection as mpc
from supercollider import Server, Synth
from pynput.mouse import Controller

class SCComm(mp.Process):
    def __init__(self, rec_pos):
        mp.Process.__init__(self)
        self.rec_pos = rec_pos
    
    def run(self):
        server = Server()
        synth1 = Synth(server, "siner", {"freq": 440.0, "gain": -12.0})
        synth2 = Synth(server, "sinel", {"freq": 440.0, "gain": -12.0})
        mouse = Controller()
        self.rec_pos : mpc.Connection
        try:
            while True:
                posx, posy = mouse.position
                synth1.set("freq", posx)
                synth2.set("freq", posy)
        except KeyboardInterrupt:
            synth1.free()
            synth2.free()