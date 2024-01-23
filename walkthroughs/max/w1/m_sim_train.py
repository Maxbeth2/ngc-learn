from ngclearn.utils.data_utils import DataLoader

from ngclearn.utils.config import Config
import ngclearn.utils.transform_utils as transform
import ngclearn.utils.metric_utils as metric
import ngclearn.utils.io_utils as io_tools

from ngclearn.museum.gncn_t1 import GNCN_t1
from ngclearn.museum.gncn_t1_sigma import GNCN_t1_Sigma
from ngclearn.museum.gncn_pdh import GNCN_PDH
import tensorflow as tf

def calc_ToD(agent):
    """Measures the total discrepancy (ToD) of a given NGC model"""
    L2 = agent.ngc_model.extract(node_name="e2", node_var_name="L")
    L1 = agent.ngc_model.extract(node_name="e1", node_var_name="L")
    L0 = agent.ngc_model.extract(node_name="e0", node_var_name="L")
    ToD = -(L0 + L1 + L2)
    return float(ToD)

def eval_model(agent, dataset, calcToD=calc_ToD, verbose=False):
    """Evaluates performance of agent on this fixed-point data sample"""
    ToD = 0.0
    Lx = 0.0
    N = 0.0
    for batch in dataset:
        x_name, x = batch[0]
        N += x.shape[0]
        x_hat = agent.settle(x) # conduct iterative inferece
        # update tracked fixed point losses
        Lx = tf.reduce_sum( metric.bce(x_hat, x) ) + Lx
        ToD = calc_ToD(agent) + ToD
        agent.clear()
        if verbose:
            print(f"\r ToD {(ToD/(N * 1.0))}, Lx {(Lx/(N*1.0))}, over {N} samples...", end="")
    if verbose:
        print()
    Lx = Lx / N
    ToD = ToD / N
    return ToD, Lx

# create a training loop

ToD, Lx = eval_model(agent, train_set, calc_ToD, verbose=True)
vToD, vLx = eval_model(agent, dev_set, calc_ToD, verbose=True)
print(f"{-1} | ToD = {ToD} Lx = {Lx} ; vToD = {vToD} vLx = {vLx}")

import time
sim_start_time = time.time()
for i in range(num_iter=3): # for each training / iteration epoch
    ToD = 0.0
    Lx = 0.0
    n_s = 0
    # run singe epoch/pass/iteration through dataset
    ################################################
    for batch in train_set:
        n_s = batch[0][1].shape[0]
        x_name, x = batch[0]
        x_hat = agent.settle(x)
        ToD_t = calc_ToD(agent)
        Lx = tf.reduce_sum( metric.bce(x_hat, x) ) + Lx
        # update synaptic parameters given current model internal state
        delta = agent.calc_updates()
        opt.applty_gradients(zip(delta, agent.ngc_model.theta))
        agent.ngc_model.apply_constraints()
        agent.clear()

        ToD = ToD_t + ToD
        print(f"\r train.ToD {(ToD/(n_s * 1.0))} Lx {(Lx/(n_s * 1.0))} with {n_s} samples seen...", end="")
        ################################################
        print()
        ToD = ToD/(n_s * 1.0)
        Lx = Lx/(n_s * 1.0)
        # evaluate generalization ability on dev set
        vToD, vLx = eval_model(agent, dev_set, calc_ToD)
        print(f"{i} | ToD = {ToD} Lx = {Lx} ; vToD = {vToD} vLx = {vLx}")