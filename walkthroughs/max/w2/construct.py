from construction_utils import CableConnector, SNodeBuilder
from ngclearn.engine.nodes.enode import ENode

bd = SNodeBuilder()
cc = CableConnector()

a = bd.set_values(beta=0.05, leak=0.001).build("a", dim=20)
b = bd.set_values(beta=0.05, leak=0.002).build("b", dim=10)
e = ENode("e", dim=10)

a_e = cc.with_update_rule().with_constraints().connect(a, e, to_comp=cc.EComps.PMU, reset=True)
b_e = cc._1_simple().connect(b, e, from_comp=cc.SComps.Z, to_comp=cc.EComps.PTARG)

cc._1_mirror(a_e).connect(e, a, to_comp=cc.SComps.BU)
cc._1_simple(-1.0).connect(e, b)