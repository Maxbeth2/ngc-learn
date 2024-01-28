from utils.construction_utils import SNodeBuilder, CableConnector
from ngclearn.engine.nodes.enode import ENode



def build_two_way():
    _bd = SNodeBuilder()
    latent_dim = 3
    col_dim = 3
    pos_dim = 2

    col = _bd.O0_build("col", dim=col_dim)
    col_e = ENode("col_e", dim=col_dim)
    col_mu = _bd.O0_build("col_mu", dim=col_dim)
    # lat_col = None
    latent_vec = _bd.O0_build("lat", dim=latent_dim)
    # lat_pos = None
    pos_mu = _bd.O0_build("pos_mu", dim=pos_dim)
    pos_e = ENode("pos_e", dim=pos_dim)
    pos = _bd.O0_build("pos", dim=pos_dim)

    cc = CableConnector()

    cc.O1_simple().O0_connect(col, col_e, to_comp=cc.EComps.PTARG)
    cc.O1_simple().O0_connect(col_mu, col_e, to_comp=cc.EComps.PMU)

    lat_cc = cc.O1_dense().Op1_with_update_rule(latent_vec, col_e).O0_connect(latent_vec, col_mu)
    cc.O1_mirror(lat_cc).O0_connect(col_e, latent_vec)
    lat_pc = cc.O1_dense().Op1_with_update_rule(latent_vec, pos_e).O0_connect(latent_vec, pos_mu)
    cc.O1_mirror(lat_pc).O0_connect(pos_e, latent_vec)

    cc.O1_simple().O0_connect(pos_mu, pos_e, to_comp=cc.EComps.PMU)
    cc.O1_simple().O0_connect(pos, pos_e, to_comp=cc.EComps.PTARG)

    from ngclearn.engine.ngc_graph import NGCGraph

    model = NGCGraph(K=20)
    model.set_cycle([latent_vec, col, pos])
    model.set_cycle([col_mu, pos_mu])
    model.set_cycle([col_e, pos_e])
    # model.set_cycle([col])

    model.compile(batch_size=1)

    from utils.vis import visualize_graph

    visualize_graph(model, output_dir="two_way")

    return model




def build_deep_two_way():
    _bd = SNodeBuilder()
    latent_dim = 3
    col_dim = 3
    pos_dim = 2

    col = _bd.O0_build("col", dim=col_dim)
    col_e = ENode("col_e", dim=col_dim)
    col_mu = _bd.O0_build("col_mu", dim=col_dim)
    lat_col = _bd.O0_build("lat_col", dim=latent_dim)
    lat_col_e = ENode("lc_e", dim=latent_dim)
    lat_col_mu = _bd.O0_build("lat_col_mu", dim=latent_dim)

    latent_vec = _bd.O0_build("lat", dim=latent_dim)

    lat_pos_mu = _bd.O0_build("lat_pos_mu", dim=latent_dim)
    lat_pos_e = ENode("lp_e", dim=latent_dim)
    lat_pos = _bd.O0_build("lat_pos", dim=latent_dim)

    pos_mu = _bd.O0_build("pos_mu", dim=pos_dim)
    pos_e = ENode("pos_e", dim=pos_dim)
    pos = _bd.O0_build("pos", dim=pos_dim)

    cc = CableConnector()

    lv_lpmu = cc.O1_dense().Op1_with_update_rule(latent_vec, lat_pos_e).O0_connect(latent_vec, lat_pos_mu)
    lpmu_lpe = cc.O1_simple().O0_connect(lat_pos_mu, lat_pos_e, to_comp=cc.EComps.PMU)
    lp_lpe = cc.O1_simple().O0_connect(lat_pos, lat_pos_e, to_comp=cc.EComps.PTARG)
    lpe_lv = cc.O1_mirror(lv_lpmu).O0_connect(lat_pos_e, latent_vec)

    lp_pmu = cc.O1_dense().Op1_with_update_rule(lat_pos, pos_e).O0_connect(lat_pos, pos_mu)
    pmu_pe = cc.O1_simple().O0_connect(pos_mu, pos_e, to_comp=cc.EComps.PMU)
    pos_pe = cc.O1_simple().O0_connect(pos, pos_e, to_comp=cc.EComps.PTARG)
    pe_lp = cc.O1_mirror(lp_pmu).O0_connect(pos_e, lat_pos)

    # ----

    lv_lcmu = cc.O1_dense().Op1_with_update_rule(latent_vec, lat_col_e).O0_connect(latent_vec, lat_col_mu)
    lcmu_lce = cc.O1_simple().O0_connect(lat_col_mu, lat_col_e, to_comp=cc.EComps.PMU)
    lc_lce = cc.O1_simple().O0_connect(lat_col, lat_col_e, to_comp=cc.EComps.PTARG)
    lce_lv = cc.O1_mirror(lv_lcmu).O0_connect(lat_col_e, latent_vec)

    lc_cmu = cc.O1_dense().Op1_with_update_rule(lat_col, col_e).O0_connect(lat_col, col_mu)
    cmu_ce = cc.O1_simple().O0_connect(col_mu, col_e, to_comp=cc.EComps.PMU)
    col_ce = cc.O1_simple().O0_connect(col, col_e, to_comp=cc.EComps.PTARG)
    ce_lc = cc.O1_mirror(lc_cmu).O0_connect(col_e, lat_col)




    from ngclearn.engine.ngc_graph import NGCGraph

    model = NGCGraph(K=20)
    model.set_cycle([latent_vec, lat_col, lat_pos, col, pos])
    model.set_cycle([lat_col_mu, lat_pos_mu, col_mu, pos_mu])
    model.set_cycle([lat_col_e, lat_pos_e, col_e, pos_e])
    # model.set_cycle([col])

    model.compile(batch_size=1)

    from utils.vis import visualize_graph

    visualize_graph(model, output_dir="two_way")

    return model