import numpy as np 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.simulationconfiguration import SimulationConfiguration
from dipde.internals.network import Network
from dipde.internals.simulation import Simulation
from dipde.internals.connection import Connection as Connection
import scipy.stats as sps
from dipde.interfaces.zmq import RequestConnection, ReplyServerThread
from dipde.interfaces.zmq import PublishCallbackConnect, CallbackSubscriberThread
from dipde.interfaces.zmq import context as zmq_context
import time
import logging
import os
logging.disable(logging.CRITICAL)


basic_steady_state = 5.110935325325733

def test_basic():
    logging.disable(logging.DEBUG)
    singlepop(basic_steady_state)
    
def test_tau_normal():
    mu = .02
    sigma = 0.004
    a = 0
    b = np.inf
    tau_m_dist = sps.truncnorm(float(a - mu) / sigma, float(b - mu)/sigma, loc=mu, scale=sigma)
    singlepop(4.7064469636898467, tau_m=(tau_m_dist,50))

def test_p0():
    p0 = sps.norm(0.01,.001)
    singlepop(5.4339562725381763, p0=p0)
    
def test_gmres():
    singlepop(5.0693643281797707, update_method='gmres', tol=1e-5)
    
def test_weight():
    weights = sps.norm(0.005,.001)
    singlepop(5.379652403431419, weights=weights)
    
def test_drive():
    bgfr = lambda t: 100
    singlepop(basic_steady_state, bgfr=bgfr)

def test_zmq_nsyn():
    reply_server_thread = ReplyServerThread(lambda: 1)
    reply_server_thread.start()
    singlepop(basic_steady_state, nsyn=RequestConnection(reply_server_thread.port))
    reply_server_thread.shutdown()
    
def test_zmq_drive_bind_server():

    reply_server_thread = ReplyServerThread(lambda t: 100)
    reply_server_thread.start()
    singlepop(basic_steady_state, bgfr=RequestConnection(reply_server_thread.port))
    reply_server_thread.shutdown()

def test_checkpoint_simulation():
    
    t0 = 0.
    dt = .001
    tf = .1
    checkpoint_file_name = './checkpoint_test.json'
    checkpoint_period = 1
    
    def network_update_callback(s):
        time.sleep(.03)

    class Canary(object):
        def __init__(self):
            self.called = False

        def checkpoint_callback(self, n):
            self.called = True

    canary = Canary()
    
    simulation_configuration = SimulationConfiguration(dt, tf, t0=t0, checkpoint_file_name=checkpoint_file_name, checkpoint_period=checkpoint_period)
#     logging.disable(logging.DEBUG)
    singlepop(basic_steady_state,
              simulation_configuration=simulation_configuration,
              network_update_callback=network_update_callback,
              checkpoint_callback = canary.checkpoint_callback)
    assert os.path.exists(checkpoint_file_name)
    os.remove(checkpoint_file_name)

    assert canary.called == True

def test_zmq_callback():

    # test_port = 5556
    
    # Start a thread that will listen to the callback:
    temp = CallbackSubscriberThread()
    temp.start()
    
    # Create callback, and wrap to make it publish:
    def network_update_callback(s):
        return [s.t]
    network_update_callback_pub = PublishCallbackConnect(temp.port, 'test', network_update_callback)
    
    # Run:
    singlepop(basic_steady_state, network_update_callback=network_update_callback_pub)
    


def singlepop(steady_state, tau_m=.02, p0=((0.,),(1.,)), weights={'distribution':'delta', 'loc':.005}, bgfr=100, network_update_callback=lambda s: None, update_method='approx', simulation_configuration=None, tol=None, checkpoint_callback=None, nsyn=1):
    
    # Settings:
    t0 = 0.
    dt = .001
    dv = .001
    v_min = -.01
    v_max = .02
    tf = .1
    
    # Create simulation:
    b1 = ExternalPopulation(bgfr)
    i1 = InternalPopulation(v_min=v_min, tau_m=tau_m, v_max=v_max, dv=dv, update_method=update_method, p0=p0, tol=tol)
    b1_i1 = Connection(b1, i1, nsyn, weights=weights)
    network = Network([b1, i1], [b1_i1], update_callback=network_update_callback)
    if simulation_configuration is None:
        simulation_configuration = SimulationConfiguration(dt, tf, t0=t0)
    simulation = Simulation(network=network, simulation_configuration=simulation_configuration, checkpoint_callback=checkpoint_callback)
    simulation.run()
    b1.plot()
    
    i1.plot_probability_distribution()
    i1.plot()
    assert i1.n_edges == i1.n_bins+1 

    # Test steady-state:
    np.testing.assert_almost_equal(i1.get_firing_rate(.05), steady_state, 12)



    
if __name__ == "__main__":          # pragma: no cover 
    test_zmq_callback()             # pragma: no cover
    test_basic()                    # pragma: no cover
    test_tau_normal()               # pragma: no cover
    test_p0()                       # pragma: no cover
    test_weight()                   # pragma: no cover
    test_drive()                    # pragma: no cover
    test_zmq_drive_bind_server()    # pragma: no cover
    test_zmq_nsyn()                 # pragma: no cover
    test_gmres()                    # pragma: no cover
    test_checkpoint_simulation()    # pragma: no cover


