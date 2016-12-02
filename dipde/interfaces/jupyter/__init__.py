import IPython.display
from dipde.interfaces.zmq import RequestFiringRate, WidgetReplyServerThread
from dipde.internals import ExternalPopulation
import ipywidgets as ipw
import types

class IntSliderInput(object):
    def __init__(self, port=None, display=True, **kwargs):

        self.display = display

        self.int_slider = ipw.IntSlider(**kwargs)
        self.reply_server_thread = WidgetReplyServerThread(self.int_slider, port=port)
        self.zmq_firing_rate_request_function = RequestFiringRate(self.port)
        self.population = ExternalPopulation(self.zmq_firing_rate_request_function)

        # Monkey patch the start function onto the initialize function
        old_initialize = self.population.initialize
        def new_initialize(_self, ):
            self.start()
            old_initialize()
        self.population.initialize= types.MethodType(new_initialize, self.population)

        # Monkey patch the shutdown function
        old_shutdown= self.population.shutdown
        def new_shutdown(_self, ):
            self.shutdown()
            old_shutdown()
        self.population.shutdown = types.MethodType(new_shutdown, self.population)

    @property
    def port(self):
        return self.reply_server_thread.port

    def start(self):
        self.reply_server_thread.start()
        if self.display == True:
            IPython.display.display(self.int_slider)

    def shutdown(self):
        self.reply_server_thread.shutdown()

        if not self.zmq_firing_rate_request_function.socket.closed:
            self.zmq_firing_rate_request_function.shutdown()


class ProgressBar(object):
    def __init__(self):
        self.progress_bar = ipw.FloatProgress()

    def initialize(self):
        self.progress_bar.min = 0
        self.progress_bar.max = int((self.network.tf - self.network.t0) / self.network.dt)
        self.progress_bar.value = 0
        IPython.display.display(self.progress_bar)

    def update(self):
        self.progress_bar.value += 1

    def set_network(self, network):
        self.network = network
