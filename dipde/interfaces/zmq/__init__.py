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


class RequestConnection(object):
    
    def __init__(self, port):
        
        self.port = port        
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:%s" % port)
        
    def __call__(self, *args):
        if len(args) == 0:
            self.socket.send(b'')
        else:
            self.socket.send_multipart(map(str,args))
        message = self.socket.recv_multipart()
        return float(message[0])

    def shutdown(self):
        self.socket.close()
        assert self.socket.closed
    
class ReplyServerBind(object):
    
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
            # print 'message:', message, type(message)
            if message == 'SHUTDOWN':
                break
            # print 'message'
            if message == '':
                requested_args = tuple()
            else:
                requested_args = tuple([float(message)])
            self.socket.send_multipart([b"%s" % self.reply_function(*requested_args)])
        self.socket.send('DOWN')
        self.socket.close()

class ReplyServerThread(threading.Thread):

    def __init__(self, reply_function, port=None):
        super(ReplyServerThread, self).__init__()
        self._stop = threading.Event()
        self.daemon = True
        self.reply_function = reply_function
        self.server = ReplyServerBind(self.reply_function, port=port)


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



