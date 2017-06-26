import numpy as np
from dipde.profiling import profile_network, extract_value
from dipde.examples.singlepop import get_network
import re



def test_profile_singlepop():
    
    dv = .0001
    update_method = 'approx'
    tol = 1e-14
    
    run_dict = {'dt':.0001, 't0':0, 'tf':.2}

    simulation = get_network(dv=dv, update_method=update_method, tol=tol)
    profile_result = profile_network(simulation, run_dict)

    run_time = extract_value(profile_result, 'network.py', 'run')
    
    
if __name__ == "__main__":                      # pragma: no cover
    test_profile_singlepop()                    # pragma: no cover