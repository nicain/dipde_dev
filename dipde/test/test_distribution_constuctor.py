import json
import scipy.stats as sps
from dipde.internals.utilities import discretize_if_needed
import logging
logging.disable(logging.CRITICAL)
import numpy as np

def test_continuous_no_N():
    discretize_if_needed(sps.norm(loc=2, scale=1.5))
 
def test_continuous_N():
    discretize_if_needed((sps.norm(loc=2, scale=1.5),25))
    
def test_scalar():
    discretize_if_needed(.02)
 
def test_discrete_rv():
#     sps.rv_discrete(values=([.02],[1]), )
    discretize_if_needed(sps.rv_discrete(values=([.02],[1])))
 
def test_dist_specified():
    discretize_if_needed(((0,1,2,3),(.25,.25,.25,.25)))
    
def test_dist_xk_pk_off_by_one():
    discretize_if_needed(((0,1,2,3),(.5,.25,.25)))
    
def test_dist_dict_delta():
    discretize_if_needed({'distribution':'delta', 'loc':.5})
    
def test_dist_json_delta():
    discretize_if_needed(json.dumps({'distribution':'delta', 'loc':.5}))

def test_equvalent_discrete():
    import dipde

    test_list = [.001,
                 {'distribution': 'delta', 'loc': 0},
                 '{"distribution":"delta", "loc":0}',
                 ([0], [1]),
                 sps.rv_discrete(values=([0], [1]))]

    for p0 in test_list:
        print p0
        i1 = dipde.InternalPopulation(v_min=0, v_max=.02, dv=.001, p0=p0)
        b1 = dipde.ExternalPopulation('100')
        b1_i1 = dipde.Connection(b1, i1, 1, weights=.005)
        network = dipde.Network([b1, i1], [b1_i1])
        network.run(dt=.001, tf=.2)
        np.testing.assert_almost_equal(i1.firing_rate_record[-1], 5.39156805318, 10)

def test_equvalent_continuous():
    import dipde

    test_list = [dipde.InternalPopulation(v_min=0, v_max=.02, dv=.001, p0=sps.norm(scale=.003)),
                   dipde.InternalPopulation(v_min=0, v_max=.02, dv=.001, p0=sps.norm(loc=0, scale=.003)),
                   dipde.InternalPopulation(v_min=0, v_max=.02, dv=.001, p0=(sps.norm(loc=0, scale=.003), 25)),
                   dipde.InternalPopulation(v_min=0, v_max=.02, dv=.001,
                                            p0={"distribution": "norm", "loc": 0, "scale": 0.003}),
                   dipde.InternalPopulation(v_min=0, v_max=.02, dv=.001,
                                            p0={"distribution": "norm", "loc": 0, "scale": 0.003, "N": 25}),
                   dipde.InternalPopulation(v_min=0, v_max=.02, dv=.001,
                                            p0='{"distribution":"norm", "loc":0, "scale":0.003, "N":25}')]

    for i1 in test_list:
        b1 = dipde.ExternalPopulation('100')
        b1_i1 = dipde.Connection(b1, i1, 1, weights=.005)
        network = dipde.Network([b1, i1], [b1_i1])
        network.run(dt=.001, tf=.2)
        np.testing.assert_almost_equal(i1.firing_rate_record[-1], 5.3915680916372484, 10)

if __name__ == "__main__":                      # pragma: no cover
    test_continuous_no_N()                      # pragma: no cover
    test_continuous_N()                         # pragma: no cover
    test_scalar()                               # pragma: no cover
    test_discrete_rv()                          # pragma: no cover
    test_dist_specified()                       # pragma: no cover
    test_dist_xk_pk_off_by_one()                # pragma: no cover
    test_dist_dict_delta()                      # pragma: no cover
    test_dist_json_delta()                      # pragma: no cover
    test_equvalent_discrete()                   # pragma: no cover
    test_equvalent_continuous()                 # pragma: no cover