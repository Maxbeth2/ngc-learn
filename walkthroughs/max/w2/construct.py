from construction_utils import SNodeBuilder, CableConnector
from ngclearn.engine.nodes.enode import ENode
from ngclearn.engine.ngc_graph import NGCGraph

x_dim = 2
z1_dim = 16
z2_dim = 3
bd = SNodeBuilder()
cc = CableConnector()

z2 = bd.O0_build("z2", dim=z2_dim)
mu1 = bd.O0_build("mu1", dim=z1_dim)
e1 = ENode("e1", dim=z1_dim)
z1 = bd.Op1_with_prior().O0_build("z1", dim=z1_dim)
mu0 = bd.O0_build("mu0", dim=x_dim)
# mu0b = bd.O0_build("mu0b", dim=x_dim)
e0 = ENode("e0", dim=x_dim)
# e0b = ENode("e0b", dim=x_dim)
z0 = bd.O0_build("z0", dim=x_dim)
# z0b = bd.O0_build("z0b", dim=x_dim)

z2_mu1 = cc.O1_dense().O0_connect(z2, mu1)
z1_mu0 = cc.O1_dense().O0_connect(z1, mu0)
cc.O1_simple(1.0).O0_connect(mu1, e1, to_comp=cc.EComps.PMU)
cc.O1_simple(1.0).O0_connect(z1, e1, to_comp=cc.EComps.PTARG)
cc.O1_simple(1.0).O0_connect(mu0, e0, to_comp=cc.EComps.PMU)
cc.O1_simple(1.0).O0_connect(z0, e0, to_comp=cc.EComps.PTARG)

cc.O1_mirror(z2_mu1).O0_connect(e1, z2, to_comp=cc.SComps.BU)
cc.O1_mirror(z1_mu0).O0_connect(e0, z1, to_comp=cc.SComps.BU)



circuit = NGCGraph(K=40)
circuit.set_cycle([z2, z1, z0])
circuit.set_cycle([mu1, mu0])
circuit.set_cycle([e1, e0])
circuit.compile(batch_size=1)

from vis import visualize_graph

visualize_graph(circuit, output_dir="vis_net", width='1000px') # generate the graph visual of


from pynput.mouse import Button, Controller
from supercollider import Server, Synth
import tensorflow as tf
import numpy as np
import threading
from queue import Queue

# server = Server()
# synth1 = Synth(server, "siner", {"freq": 440.0, "gain": -12.0})
# synth2 = Synth(server, "sinel", {"freq": 440.0, "gain": -12.0})
mouse = Controller()

# Create a Queue for communication between threads
data_queue = Queue()


# def update_synths():
#     try:
#         while True:
#             synth1.set("freq", (mouse.position[0] / 3.0) + 80.0)
#             synth2.set("freq", (mouse.position[1] / 3.0) + 80.0)

#     except KeyboardInterrupt:
#         synth1.free()
#         synth2.free()

# # Start the Synth operations in a separate thread
# update_synths_thread = threading.Thread(target=update_synths)
# update_synths_thread.start()

try:
    while True:
        x = tf.cast(np.array([mouse.position]), dtype=tf.float32)
        reads, deltas = circuit.settle(
            clamped_vars=[("z0", "z", x)],
            readout_vars=[("mu0", "phi(z)")])
        x, y = mouse.position
        print(f"{x} , {y}")
        print(reads[0][2].numpy())

except KeyboardInterrupt:
    # update_synths_thread.join()
    while not data_queue.empty():
        print(data_queue.get)