# Copyright 2013 Allen Institute
# This file is part of dipde
# dipde is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# dipde is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with dipde.  If not, see <http://www.gnu.org/licenses/>.


# Imports
from dipde.internals.utilities import descretize
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as sps
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.connection import Connection as Connection
import logging
logging.disable(logging.CRITICAL)

def get_network(dv=.001, update_method='exact', approx_order=None, tol=1e-8, tau_m=.02):

    # Create simulation:
    b1 = ExternalPopulation('100', record=True)
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol, tau_m=tau_m)
    b1_i1 = Connection(b1, i1, 1, weights=.005, delays=0.0)
    network = Network([b1, i1], [b1_i1])

    return network

def example(show=False, save=False):

    # Settings:
    t0 = 0.
    dt = .0001
    dv = .0001
    tf = .1
    update_method = 'gmres'
    tol = 1e-14
    
    # Run simulation:
    mu = .02
    sigma = 0.004
    b = np.inf
    a = 0
    tau_m_dist = sps.truncnorm(float(a - mu) / sigma, float(b - mu) / sigma, loc=mu, scale=sigma)

    total = 0
    vals, probs = descretize(tau_m_dist, 100)
    for ii, (val, prob) in enumerate(zip(vals, probs)):
        print ii
        network = get_network(dv=dv, update_method=update_method,  tol=tol, tau_m=val)
        network.run(dt=dt, tf=tf, t0=t0)
        i1 = network.population_list[1]
        total += i1.firing_rate_record[-1]*prob

    print total
     

    # # Visualize:
    # i1 = network.population_list[1]
    #
    # fig, ax = plt.subplots(figsize=(3,3))
    #
    # i1.plot(ax=ax)
    # plt.xlim([0,tf])
    # plt.ylim(ymin=0)
    # plt.xlabel('Time (s)')
    # plt.ylabel('Firing Rate (Hz)')
    # fig.tight_layout()
    # if save == True: plt.savefig('./singlepop.png')
    #
    #
    #
    # if show == True:                        # pragma: no cover
    #     fig = plt.gcf()                     # pragma: no cover
    #     window = fig.canvas.manager.window  # pragma: no cover
    #     window.raise_()                     # pragma: no cover
    #     plotting.show()
          

    return i1.t_record, i1.firing_rate_record
    
if __name__ == "__main__": example(show=True)        # pragma: no cover

