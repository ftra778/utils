import socket
import threading
import time
import json
from utils.colors import bcolors
try: 
    import queue
except ImportError:
    import Queue as queue

# General purpose connection manager that stores results in a queue property for asynchronous data processing
class Connection():
    def __init__(self, ip="127.0.0.1", port=7797, type='socket', max_retry=5):
        self.ip=ip
        self.port=port
        self.type=type
        self.max_retry=max_retry
        self.sock=None
        self.endpoint=None
        self.connected=False
        self.lock=threading.Lock()
        self.queue=queue.Queue()

        self.testingtime = 0.5

        if self.type in ['client', 'server']:
            self.connect()
        else:
            print("{}Connection type not set, setting client to \"None\" {}".format(bcolors.FAIL, bcolors.ENDC))
            self.sock=None
        

    def connect(self, type=None):
        if type is not None:
            self.type = type

        if self.type == 'client':
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while self.max_retry > 0:
                try:
                    self.sock.connect((self.ip,self.port))
                    print("\n{}Connected to: {}{}".format(bcolors.OKGREEN, (self.ip,self.port), bcolors.ENDC))
                    self.endpoint=self.sock
                    self.connected = True
                    return
                except ConnectionRefusedError:
                    self.max_retry -= 1
                    print("{}Connection failed, retrying {} times... {}".format(bcolors.WARNING, self.max_retry, bcolors.ENDC))
                    time.sleep(1)
                    continue
            print("{}Connection failed, setting client to \"None\" {}".format(bcolors.FAIL, bcolors.ENDC))

        elif self.type == 'server':
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.ip, self.port))
            print("{}Server listening on port {}... {}".format(bcolors.WARNING, self.port, bcolors.ENDC))
            self.sock.listen(1)
            self.endpoint, addr = self.sock.accept()
            self.connected = True
            print("\n{}Connected to {}\n{}".format(bcolors.OKGREEN, addr, bcolors.ENDC))



    def __send_handshake(self, data):
        self.endpoint.sendall(str(len(data)).encode())
        res = self.endpoint.recv(1024)
        if res != b'\\RDY\\':
            return False
        self.endpoint.sendall(data)
        return True
        
    def send(self, data):
        try:
            while data != b'':
                print((data))
                if len(data) < 4096:
                    res = self.__send_handshake(data)
                    break
                res = self.__send_handshake(data[:4096])
                data = data[4096:]
            
            res = self.__send_handshake(b'\\END\\')
            return True
        except socket.error:
            print("\n{}BrokenPipeError, disconnecting... {}".format(bcolors.FAIL, bcolors.ENDC))
            self.connected = False


    def __receive_handshake(self, size=1024):
        # Handle size
        size_b = self.endpoint.recv(1024)
        if size_b == b'':
            print("\n{}BrokenPipeError, disconnecting... {}".format(bcolors.FAIL, bcolors.ENDC))
            self.connected = False
            return False
        size = int(size_b)
        self.endpoint.sendall(b'\\RDY\\')
        
        # Send packet
        buf = bytearray()
        while len(buf) < size:
            packet = self.endpoint.recv(size - len(buf))
            if not packet:
                return False
            buf.extend(packet)
        # self.queue.put((buf))
        return buf
    

    def receive(self, size=1024, store=True):
        try:
            msg = []
            while True: 
                res = self.__receive_handshake()
                # if res is False:
                #     return False
                # res = self.queue.get()
                if res is False:
                    return False
                if res == b'\\END\\':
                    break
                msg.append(res)
            self.queue.put(bytearray().join(msg))
            return True
        except socket.error:
            print("\n{}BrokenPipeError, disconnecting... {}".format(bcolors.FAIL, bcolors.ENDC))
            self.connected = False
        
    def shut_down(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("\nClosed {}".format(self.label))