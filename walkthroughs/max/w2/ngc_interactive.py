from construction_utils import SNodeBuilder, CableConnector
from ngclearn.engine.nodes.enode import ENode
from ngclearn.engine.ngc_graph import NGCGraph

def create_network():
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

    z2_mu1 = cc.O1_dense().Op1_with_update_rule(z2, e1).O0_connect(z2, mu1)
    z1_mu0 = cc.O1_dense().Op1_with_update_rule(z1, e0).O0_connect(z1, mu0)
    cc.O1_simple(1.0).O0_connect(mu1, e1, to_comp=cc.EComps.PMU)
    cc.O1_simple(1.0).O0_connect(z1, e1, to_comp=cc.EComps.PTARG)
    cc.O1_simple(1.0).O0_connect(mu0, e0, to_comp=cc.EComps.PMU)
    cc.O1_simple(1.0).O0_connect(z0, e0, to_comp=cc.EComps.PTARG)

    cc.O1_mirror(z2_mu1).O0_connect(e1, z2, to_comp=cc.SComps.BU)
    cc.O1_mirror(z1_mu0).O0_connect(e0, z1, to_comp=cc.SComps.BU)
    print("ONCE PLS")

    circuit = NGCGraph(K=20)
    circuit.set_cycle([z2, z1, z0])
    circuit.set_cycle([mu1, mu0])
    circuit.set_cycle([e1, e0])
    circuit.compile(batch_size=1)
    return circuit