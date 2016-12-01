import time
import zmq
import threading

context = zmq.Context()

class PublishCallback(object):
    
    def __init__(self, port, topic, message_callback):
        
        self.port = port
        self.topic = topic
        self.message_callback = message_callback        
        self.socket = context.socket(zmq.PUB)
        
    def __call__(self, obj):
        message_to_send = list(self.message_callback(obj))
        message_to_send.insert(0,"%s" % self.topic)
        self.socket.send_multipart(map(str, message_to_send))
        
class PublishCallbackConnect(PublishCallback):
    
    def __init__(self, port, topic, message_callback):
        super(self.__class__, self).__init__(port, topic, message_callback)
        self.socket.connect("tcp://localhost:%s" % self.port)
        

# class PublishCallbackBind(PublishCallback):
#     
#     def __init__(self, port, topic, message_callback):
#         super(self.__class__, self).__init__(port, topic, message_callback)
#         self.socket.bind("tcp://*:%s" % self.port)
        
class CallbackSubscriber(object): 
    
    def __init__(self, port=None, receive_callback=None):

        self.socket = context.socket(zmq.SUB)
        if port is None:
            self.port = self.socket.bind_to_random_port('tcp://*', min_port=6001, max_port=6004, max_tries=100)

        else:
            self.socket.bind("tcp://*:%s" % port)
            self.port = port

        self.socket.setsockopt(zmq.SUBSCRIBE, 'test')
        
        if receive_callback is None:
            def receive_callback(received_message):
                print received_message
        self.receive_callback = receive_callback 

    def run(self):     
        while True: 
            received_message_multipart = self.socket.recv_multipart() 
            topic = received_message_multipart[0]
            received_message = received_message_multipart[1:]
            self.receive_callback(received_message)

class CallbackSubscriberThread(threading.Thread): 
    def __init__(self, port=None):
        super(self.__class__, self).__init__()
        self.subscriber = CallbackSubscriber(port)
        self.daemon = True

    def run(self, port=None):

        self.subscriber.run()

    @property
    def port(self):
        return self.subscriber.port


class RequestFiringRate(object):
    
    def __init__(self, port):
        
        self.port = port        
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:%s" % port)
        
    def __call__(self, t):
        self.socket.send('%s' % t)
        message = self.socket.recv_multipart()
        return float(message[0])

    def shutdown(self):
        self.socket.close()
        assert self.socket.closed
    
class ReplyFiringRateServer(object):
    
    def __init__(self, reply_function, port=None):

        self.socket = context.socket(zmq.REP)
        if port is None:
            self.port = self.socket.bind_to_random_port('tcp://*', min_port=6001, max_port=6004, max_tries=100)

        else:
            self.socket.bind("tcp://*:%s" % port)
            self.port = port

        self.reply_function = reply_function

    def run(self):
        
        while True:
            message = self.socket.recv()
            if message == 'SHUTDOWN':
                break
            requested_t = float(message)
            self.socket.send_multipart([b"%s" % self.reply_function(requested_t)])
        self.socket.send('DOWN')
        self.socket.close()

class ReplyServerThread(threading.Thread):

    def __init__(self, reply_function, port=None):
        super(ReplyServerThread, self).__init__()
        self._stop = threading.Event()
        self.daemon = True
        self.reply_function = reply_function
        self.server = ReplyFiringRateServer(self.reply_function, port=port)


    def run(self, port=None):
        self.server.run()

    def shutdown(self):
        shutdown_socket = context.socket(zmq.REQ)
        shutdown_socket.connect("tcp://localhost:%s" % self.port)
        shutdown_socket.send('SHUTDOWN')
        message = shutdown_socket.recv()
        assert message == 'DOWN'
        self.stop()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    @property
    def port(self):
        return self.server.port

class WidgetReplyServerThread(ReplyServerThread):

    def __init__(self, widget, port=None, get_value=None):
        super(WidgetReplyServerThread, self).__init__(self.reply_function)
        self.daemon = True
        self.get_value = None
        self.widget = widget
        self.server = ReplyFiringRateServer(self.reply_function, port=port)

    def reply_function(self, t):
        if not self.get_value is None:
            return self.get_value(self.widget, t)
        else:
            return self.widget.value

# class WidgetPublisher(object):
#     def __init__(self, widget, port):
#         self.widget = widget
#         self.reply_server = ReplyFiringRateServer(port, self.reply_function)
#
#     def start(self):
#         self.reply_server.run()
#         for ii in range(100):
#             time.sleep(.1)
#
#     def reply_function(self):
#         return self.widget.value
