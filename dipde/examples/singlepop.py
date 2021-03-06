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


import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.connection import Connection as Connection

def get_network(dv=.001, update_method='exact', tol=1e-14):

    # Create simulation:
    b1 = ExternalPopulation('100', record=True)
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, tol=tol)
    b1_i1 = Connection(b1, i1, 1, weights=.005, delays=0.0)
    network = Network([b1, i1], [b1_i1])

    return network

def example(show=False, save=False):

    # Settings:
    t0 = 0.
    dt = .0001
    dv = .0001
    tf = .1
    update_method = 'approx'
    tol = 1e-14
    
    # Run simulation:
    network = get_network(dv=dv, update_method=update_method, tol=tol)
    network.run(dt=dt, tf=tf, t0=t0)

    i1 = network.population_list[1]
    if show == True:                        # pragma: no cover


        # Visualize:


        fig, ax = plt.subplots(figsize=(3, 3))

        i1.plot(ax=ax)
        plt.xlim([0, tf])
        plt.ylim(ymin=0)
        plt.xlabel('Time (s)')
        plt.ylabel('Firing Rate (Hz)')
        fig.tight_layout()

        if save == True: plt.savefig('./singlepop.png')

        window = fig.canvas.manager.window  # pragma: no cover
        window.raise_()                     # pragma: no cover
        plt.show()                          # pragma: no cover
          

    return i1.t_record, i1.firing_rate_record
    
if __name__ == "__main__": example(show=True)        # pragma: no cover

