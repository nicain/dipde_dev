import IPython.display
from dipde.interfaces.zmq import RequestConnection, ReplyServerThread, ReplyServerBind
from dipde.internals import ExternalPopulation
import ipywidgets as ipw
import types

class WidgetReplyServerThread(ReplyServerThread):

    def __init__(self, widget, port=None, get_value=None):
        super(WidgetReplyServerThread, self).__init__(self.reply_function)
        self.daemon = True
        self.get_value = None
        self.widget = widget
        self.server = ReplyServerBind(self.reply_function, port=port)

    def reply_function(self, t):
        if not self.get_value is None:
            return self.get_value(self.widget, t)
        else:
            return self.widget.value


class ZMQIntSlider(ipw.IntSlider):

    def __init__(self,  port=None, display=True, **kwargs):

        self.display = display

        super(ZMQIntSlider, self).__init__(**kwargs)

        self.reply_server_thread = WidgetReplyServerThread(self, port=port)
        self.zmq_firing_rate_request_function = RequestConnection(self.port)


    @property
    def port(self):
        return self.reply_server_thread.port


    def start(self):
        self.reply_server_thread.start()
        if self.display == True:
            IPython.display.display(self)


    def shutdown(self):
        self.reply_server_thread.shutdown()

        if not self.zmq_firing_rate_request_function.socket.closed:
            self.zmq_firing_rate_request_function.shutdown()

def get_ExcitatoryPopulationZMQ(interactor, **kwargs):

    population = ExternalPopulation(interactor.zmq_firing_rate_request_function, **kwargs)

    # Monkey patch the start function onto the initialize function
    old_initialize = population.initialize
    def new_initialize(_self, ):
        interactor.start()
        old_initialize()
    population.initialize = types.MethodType(new_initialize, population)

    # Monkey patch the shutdown function
    old_shutdown = population.shutdown
    def new_shutdown(_self, ):
        interactor.shutdown()
        old_shutdown()
    population.shutdown = types.MethodType(new_shutdown, population)

    return population





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
