from enum import Enum
from ngclearn.engine.nodes.snode import SNode
from ngclearn.engine.nodes.enode import ENode
from ngclearn.engine.cables.dcable import DCable

class SNodeBuilder:
    """
    Defaults:
        act_fx = "identity"
        {"integrate_type": "euler", "use_dfx": False}
        leak = 0.001
        beta = 0.1
    """
    class PT(Enum):
        LAPLACE = "laplace"
        EXP = "exp"
        CAUCHY = "cauchy"
        GAUSS = "gaussian"

    class ACT_FX(Enum):
        RELU = "relu"
        ID = "identity"

    def __init__(self):
        self._icfg = {"integrate_type": "euler", "use_dfx": False}
        self._pcfg = None
        self._leak = 0.001
        self._beta = 0.1
        self._zeta = 1.0
        self._fx = "identity"

    def Op1_with_prior(self, pt=PT.LAPLACE, lbd=0.001):
        self._pcfg = {"prior_type": pt.value, "lambda": lbd}
        return self
    
    def reset(self):
        self._icfg = {"integrate_type": "euler", "use_dfx": True}
        self._pcfg = None
        return self

    def O1_set_numerals(self, beta=0.1, leak=0.01, zeta=1.0):
        self._beta = beta
        self._leak = leak
        self._zeta = zeta
        return self
    
    def O2_set_cats(self, use_dfx=False, act_fx=ACT_FX.ID):
        self._icfg["use_dfx"] = use_dfx
        self._fx = act_fx.value
        return self

    def O0_build(self, name, dim, reset=True):
        n = SNode(
                name=name, 
                dim=dim, 
                beta=self._beta,
                leak=self._leak,
                zeta=self._zeta,
                integrate_kernel=self._icfg,
                prior_kernel=self._pcfg,
                act_fx= self._fx
                )
        if reset:
            self.reset()
        return n
    



class ENodeBuilder:
    # class PT(Enum):
    #     LAPLACE = "laplace"
    #     EXP = "exp"
    #     CAUCHY = "cauchy"
    #     GAUSS = "gaussian"

    # class ACT_FX(Enum):
    #     RELU = "relu"
    #     ID = "identity"

    def __init__(self):
        self._ic = {"integrate_type": "euler", "use_dfx": True}
        self._pc = {"prior_type": "laplace", "lambda": 0.001}
        self._leak = 0.001
        self._beta = 0.1

    # def with_prior(self, pt=PT.LAPLACE, lbd=0.001):
    #     self._pc["prior_type"] = pt.value
    #     self._pc["lambda"] = lbd
    #     return self
    
    def reset(self):
        self._ic = {"integrate_type": "euler", "use_dfx": True}
        self._pc = {"prior_type": "laplace", "lambda": 0.001}
        return self

    def with_values(self, beta, leak):
        self._beta = beta
        self._leak = leak
        return self

    def build(self, name, dim, reset=True):
        n = SNode(
                name=name, 
                dim=dim, 
                beta=self._beta,
                leak=self._leak,
                integrate_kernel=self._ic,
                prior_kernel=self._pc
                )
        if reset:
            self.reset()
        return n





class CableConnector:
    """
    default setting:
        "type": "dense"
        "init_kernels": {"A_init": ("gaussian", 0.025)}
        "seed": 69
        "coeff": None
    """
    class SComps(Enum):
        BU = "dz_bu"
        TD = "dz_td"
        PHI = "phi(z)"
        Z = "z"
    class EComps(Enum):
        PMU = "pred_mu"
        PTARG = "pred_targ"
        PHI = "phi(z)"
        L = "L"
        Z = "z"
    class WDist(Enum):
        GAUSS = "gaussian"
    class Param(Enum):
        AT = "A^T"
        A = "A"
    class CType(Enum):
        NORM = "norm_clip"
    def __init__(self):
        self._ik = {"A_init": ("gaussian", 0.025)}
        self._cfg = {"type": "dense", "init_kernels": self._ik, "seed": 69, "coeff": None}
        self._mpk = None
        self._update_rule_dict = None
        self._constraint_dict = None
    def reset(self):
        self._ik = {"A_init": ("gaussian", 0.025)}
        self._cfg = {"type": "dense", "init_kernels": self._ik, "seed": 69, "coeff": None}
        self._update_rule_dict = None
        self._constraint_dict = None
        self._mpk = None
        # return self
    def O1_dense(self, dist=WDist.GAUSS, mu=0.025):
        """
        Gives a DCable with config
            {"type": "dense", "init_kernels": self._ik, "seed": 69, "coeff": None}
        where self._ik is
            {"A_init": ("gaussian", 0.025)}
        """
        self._ik["A_init"] = (dist, mu)
        self._cfg = {"type": "dense", "init_kernels": self._ik, "seed": 69, "coeff": None}
        self._mpk = None
        return self
    def O1_simple(self, coeff=1.0):
        self._cfg = {"type": "simple", "init_kernels": None, "seed": None, "coeff": coeff}
        self._mpk = None
        return self
    def O1_mirror(self, cable, mode=Param.AT):
        self._mpk = (cable, mode.value)
        self._cfg = None
        return self
    def O2_set_initial_A(self, dist=WDist.GAUSS, mu=0.025):
        self._ik["A_init"] = (dist, mu)
        self._cfg = {"type": "dense", "init_kernels": self._ik, "seed": 69, "coeff": None}
        self._mpk = None
        return self
    def Op1_with_update_rule(self, pre=SComps.PHI, post=SComps.PHI, param=Param.A):
        self._update_rule_dict = {"pre": pre.value, "post": post.value, "param": [param.value]}
        return self
    def Op1_disable_update(self):
        self._update_rule_dict = None
        return self
    def Op2_with_constraints(self, clip=CType.NORM, mag=1.0, axis=1):
        self._constraint_dict = {"clip_type": clip.value, "clip_mag": mag, "clip_axis": axis}
        return self
    def Op2_disable_constraints(self):
        self._constraint_dict = None
        return self
    def O0_connect(self, from_node, to_node, from_comp=SComps.PHI, to_comp=SComps.TD, reset=True):
        cable : DCable
        if self._cfg == None:
            type = "mirrored"
        else:
            type = self._cfg["type"]
        print(f"Connecting nodes {from_node.name}-{to_node.name} with -{type}- cable")
        cable = from_node.wire_to(
            to_node, 
            src_comp=from_comp.value, 
            dest_comp=to_comp.value,
            cable_kernel=self._cfg,
            mirror_path_kernel=self._mpk
            )
        if self._update_rule_dict is not None:
            cable.set_update_rule(
                preact=(from_node, self._update_rule_dict["pre"]),
                postact=(to_node, self._update_rule_dict["post"]),
                param=self._update_rule_dict["param"]
                )
        if self._constraint_dict is not None:
            cable.set_constraint(
                self._constraint_dict
            )
        if reset:
            self.reset()
        return cable



