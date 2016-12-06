import IPython.display
from dipde.interfaces.zmq import RequestConnection, ReplyServerThread, ReplyServerBind
from dipde.internals import ExternalPopulation, Connection
import ipywidgets as ipw
import types
import time

# class WidgetReplyServerThread(ReplyServerThread):
#
#     def __init__(self, widget, port=None, get_value=None):
#         super(WidgetReplyServerThread, self).__init__(self.reply_function)
#         self.daemon = True
#         self.get_value = None
#         self.widget = widget
#         self.server = ReplyServerBind(self.reply_function, port=port)
#
#     def reply_function(self, *args):
#         if not self.get_value is None:
#             return self.get_value(self.widget, *args)
#         else:
#             return self.widget.value
#
#
# class ZMQIntSlider(ipw.IntSlider):
#
#     def __init__(self,  port=None, display=True, **kwargs):
#
#         self.display = display
#
#         super(ZMQIntSlider, self).__init__(**kwargs)
#
#         self.reply_server_thread = WidgetReplyServerThread(self, port=port)
#         self.zmq_firing_rate_request_function = RequestConnection(self.port)
#
#         # Start up server:
#         self.reply_server_thread.start()
#         if self.display == True:
#             IPython.display.display(self)
#
#
#     @property
#     def port(self):
#         return self.reply_server_thread.port
#
#     def shutdown(self):
#         self.reply_server_thread.shutdown()
#
#         if not self.zmq_firing_rate_request_function.socket.closed:
#             self.zmq_firing_rate_request_function.shutdown()
#
#
# def wrap_widget(obj_to_wrap, widget_to_wrap, property_to_wrap):
#     reassign_dict = {'nsyn': 'nsyn_input',
#                      'external_firing_rate':'closure'}
#
#     setattr(obj_to_wrap, reassign_dict[property_to_wrap], widget_to_wrap.zmq_firing_rate_request_function)
#
#     # Monkey patch the shutdown function
#     old_shutdown = obj_to_wrap.shutdown
#
#     def new_shutdown(_self, ):
#         widget_to_wrap.shutdown()
#         old_shutdown()
#
#     obj_to_wrap.shutdown = types.MethodType(new_shutdown, obj_to_wrap)
#
#     return obj_to_wrap



class ProgressBar(object):
    def __init__(self, display = True, stop_button = True):
        self.progress_bar = ipw.FloatProgress()
        if stop_button == True:
            self.stop_button = ipw.Button(description='Stop')

        else:
            self.stop_button = None
        self.display = display

    def initialize(self):
        self.progress_bar.min = 0
        self.progress_bar.max = int((self.network.tf - self.network.t0) / self.network.dt)
        self.progress_bar.value = 0

        if not self.stop_button is None:
            self.stop_button._network = self.network
            def f(stop_button):
                stop_button._network.kill_signal = True
            self.stop_button.on_click(f)

        if self.display == True and self.stop_button is None:
            IPython.display.display(self.progress_bar)
        elif self.display == True and not self.stop_button is None:
            IPython.display.display(ipw.HBox([self.progress_bar, self.stop_button]))
        else:
            pass





    def update(self):
        self.progress_bar.value += 1

    def set_network(self, network):
        self.network = network


class Slider(ipw.IntSlider):
    def __init__(self, port=None, display=True, **kwargs):
        self.display = display
        super(Slider, self).__init__(**kwargs)

        if self.display == True:
            IPython.display.display(self)

        self.observe(self.update, names='value')

    def update(self, change):
        self.value = change['new']

    def set_target(self, target, key):
        self.target = target
        reassign_dict = {'nsyn': 'nsyn_input',
                         'external_firing_rate': 'closure'}

        setattr(self.target, reassign_dict[key], self.get_value)

    def get_value(self, *args):
        return self.value


# p = ExternalPopulation()
# slider = Slider(display=True, value=100, min=0, max=200, continuous_update=False)
# slider.set_target(p, 'external_firing_rate')