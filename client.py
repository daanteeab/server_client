import socket
import json
import time
from ursina import *

class client_base(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.msgFromClient = {"position":(0,0,0),"rotation_y":0}
        self.bytesToSend = str.encode(json.dumps(self.msgFromClient))
        self.serverAddressPort = ("127.0.0.1", 20001)
        self.bufferSize = 1024
        for keys, values in kwargs.items():
            setattr(self, keys, values)
        
        # Create a UDP socket at client side
        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.time_var = 0
        self.msg = None
        #self.UDPClientSocket.sendto(self.bytesToSend, self.serverAddressPort)
        # Send to server using created UDP socket

    def start(self):
        while True:
            self.msgFromClient["position"][1] += 1

            bytesToSend = str.encode(json.dumps(self.msgFromClient))
            self.UDPClientSocket.sendto(bytesToSend, self.serverAddressPort)
            self.time_var = time.time()

            msgFromServer = self.UDPClientSocket.recvfrom(self.bufferSize)
            self.msg = json.loads(msgFromServer[0])
            for keys in self.msg:
                print(f'rcv msg in {time.time()-self.time_var} seconds {self.msg[keys]}')
    
    def start_ursina(self):
        bytesToSend = str.encode(json.dumps(self.msgFromClient))
        self.UDPClientSocket.sendto(bytesToSend, self.serverAddressPort)
        self.time_var = time.time()

        msgFromServer = self.UDPClientSocket.recvfrom(self.bufferSize)
        self.msg = json.loads(msgFromServer[0])
        for keys in self.msg:
            print(f'rcv msg in {time.time()-self.time_var} seconds {self.msg[keys]}')

if __name__ == "__main__":
    client_base().start()

