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
z1 = bd.O0_build("z1", dim=z1_dim)
mu0 = bd.O0_build("mu0", dim=x_dim)
e0 = ENode("e0", dim=x_dim)
z0 = bd.O0_build("z0", dim=x_dim)

cc.O1_dense().O0_connect(z2, mu1)
cc.O1_dense().O0_connect(z1, mu0)


circuit = NGCGraph(K=1)
circuit.set_cycle([z2, z1, z0])
circuit.set_cycle([mu1, mu0])
circuit.set_cycle([e1, e0])
circuit.compile(batch_size=1)

import ngclearn.utils.experimental.viz_graph_utils as viz

viz.visualize_graph(circuit) # generate the graph visual of