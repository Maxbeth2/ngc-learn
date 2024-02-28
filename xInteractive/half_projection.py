from ngclearn.utils import io_utils as io
from ngclearn.engine.ngc_graph import NGCGraph

model : NGCGraph
model = io.deserialize('saved_models/mm3108_viktor.ngc')

print(model.nodes.keys())
print(model.theta)
print(model.K)
K = model.K
lat_lat_pos = model.cables["lat-to-lat_pos_mu_dense"]
lat_pos_pos = model.cables["lat_pos-to-pos_mu_dense"]

lat_lat_col = model.cables["lat-to-lat_col_mu_dense"]
lat_col_col = model.cables["lat_col-to-col_mu_dense"]



from utils.construction_utils import SNodeBuilder, CableConnector
from ngclearn.engine.nodes.enode import ENode
_bd = SNodeBuilder()
latent_dim = 3
col_dim = 3
pos_dim = 2

# col = _bd.O0_build("col", dim=col_dim)
# col_e = ENode("col_e", dim=col_dim)
col_F = _bd.O1_set_numerals(zeta=0.0, beta=1.0).O0_build("col_F", dim=col_dim)
# lat_col = _bd.O0_build("lat_col", dim=latent_dim)
# lat_col_e = ENode("lc_e", dim=latent_dim)
lat_col_F = _bd.O1_set_numerals(zeta=0.0, beta=1.0).O0_build("lat_col_F", dim=latent_dim)

latent_vec = _bd.O0_build("lat", dim=latent_dim)

lat_pos_mu = _bd.O0_build("lat_pos_mu", dim=latent_dim)
lat_pos_e = ENode("lp_e", dim=latent_dim)
lat_pos = _bd.O0_build("lat_pos", dim=latent_dim)

pos_mu = _bd.O0_build("pos_mu", dim=pos_dim)
pos_e = ENode("pos_e", dim=pos_dim)
pos = _bd.O0_build("pos", dim=pos_dim)

cc = CableConnector()

lv_lpmu = cc.O1_mirror(lat_lat_pos, mode=cc.Param.A).O0_connect(latent_vec, lat_pos_mu)
cc.O1_simple().O0_connect(lat_pos_mu, lat_pos_e, to_comp=cc.EComps.PMU)
cc.O1_simple().O0_connect(lat_pos, lat_pos_e, to_comp=cc.EComps.PTARG)
lpe_lv = cc.O1_mirror(lat_lat_pos, mode=cc.Param.AT).O0_connect(lat_pos_e, latent_vec)

lp_pmu = cc.O1_mirror(lat_pos_pos, mode=cc.Param.A).O0_connect(lat_pos, pos_mu)
cc.O1_simple().O0_connect(pos_mu, pos_e, to_comp=cc.EComps.PMU)
cc.O1_simple().O0_connect(pos, pos_e, to_comp=cc.EComps.PTARG)
pe_lp = cc.O1_mirror(lat_pos_pos, mode=cc.Param.AT).O0_connect(pos_e, lat_pos)

# ----

lv_lcmu = cc.O1_mirror(lat_lat_col, mode=cc.Param.A).O0_connect(latent_vec, lat_col_F)
# lcmu_lce = cc.O1_simple().O0_connect(lat_col_mu, lat_col_e, to_comp=cc.EComps.PMU)
# lc_lce = cc.O1_simple().O0_connect(lat_col, lat_col_e, to_comp=cc.EComps.PTARG)
# lce_lv = cc.O1_mirror(lv_lcmu).O0_connect(lat_col_e, latent_vec)

lc_cmu = cc.O1_mirror(lat_col_col, mode=cc.Param.A).O0_connect(lat_col_F, col_F)
# cmu_ce = cc.O1_simple().O0_connect(col_mu, col_e, to_comp=cc.EComps.PMU)
# col_ce = cc.O1_simple().O0_connect(col, col_e, to_comp=cc.EComps.PTARG)
# ce_lc = cc.O1_mirror(lc_cmu).O0_connect(col_e, lat_col)

blinded_model = NGCGraph(K=K)
blinded_model.set_cycle([latent_vec, lat_pos, pos])
blinded_model.set_cycle([lat_pos_mu, pos_mu, lat_col_F, col_F])
blinded_model.set_cycle([lat_pos_e, pos_e])
info = blinded_model.compile(batch_size=1)


#####

# import numpy as np
# import tensorflow as tf
# dim = 100
# pic = np.zeros((dim,dim,3))
# print(pic[:,:,0].shape)
# for iind, i in enumerate(np.linspace(0,1,dim)):
#     for jind, j in enumerate(np.linspace(0,1,dim)):
#         pos = np.array([[i, j]])
#         pos = tf.cast(pos, dtype=tf.float32)
#         rd, d = blinded_model.settle(
#             clamped_vars=[("pos", "z", pos)],
#             readout_vars=[("col_F", "phi(z)")]
#         )
#         # print(pic[int(i),int(j)])
#         pic[iind,jind,:] = rd[0][2].numpy()[0]
#         # print(rd[0,2,:].numpy()[0])
#         blinded_model.clear()

# import matplotlib.pyplot as plt
# print(pic)
# plt.imshow(pic)