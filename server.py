import socket
import json
import time
from ursina import *

class server_base():
    def __init__(self, **kwargs):
        self.localIP = "127.0.0.1"
        self.localPort = 20001
        self.bufferSize = 1024
        for keys, values in kwargs.items():
            setattr(self, keys, values)

        self.msgFromServer = "Hello UDP Client"
        self.bytesToSend = str.encode(json.dumps(self.msgFromServer))
        self.clients = set([])
        self.clients_data = {}
        self.temp_msg = "temp msg for keyword answers"
        # Create a datagram socket
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.setblocking(0)
        # Bind to address and ip
        self.UDPServerSocket.bind((self.localIP, self.localPort))
        self.message_keywords = set([])
        self.message_keywords.add("GET_ID")
        self.message_keywords.add("GET_CLIENTS")
        self.message_keywords.add("POST_MESSAGE")
        self.message_keywords.add("GET_MESSAGES")
        self.message_keywords.add("INIT_MIRROR")
        self.message_keywords.add("GET_MIRROR")
        print("UDP server up and listening")
        # Listen for incoming datagrams

        # Start game attributes
        self.gametimer = time.time()
        self.server_entity_id = 0

    def start(self):
        while(True):

            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)

            message = json.loads(bytesAddressPair[0])
            address = bytesAddressPair[1]

            #print(message)
            
            if len(self.clients)==2 and time.time()-self.gametimer>10:
                server_init_mirror_message = {"class":"mushroomMirror","sender":"server","id":self.server_entity_id}
                self.server_entity_id += 1
                temp_msg = {"INIT_MIRROR":{"INIT_MIRROR":server_init_mirror_message}}
                bytesToSend = str.encode(json.dumps(temp_msg))
                for clients in self.clients_data:
                    self.UDPServerSocket.sendto(bytesToSend, self.clients_data[clients][clients])

            if address not in self.clients:
                self.clients.add(address)
                
            if message == "GET_ID":
                self.temp_msg = {"GET_ID":address}
                self.bytesToSend = str.encode(json.dumps(self.temp_msg))
                self.UDPServerSocket.sendto(self.bytesToSend, address)
                print(f'sent GET ID to {address}')

            if message == "GET_CLIENTS":
                self.temp_msg = {"GET_CLIENTS":list(self.clients)}
                self.bytesToSend = str.encode(json.dumps(self.temp_msg))
                for x in list(self.clients):
                    self.UDPServerSocket.sendto(self.bytesToSend, x)
                    print(f'sent GET CLIENTS to {x}')
            
            if message == "GET_MIRROR":
                recv = [receivers for receivers in list(self.clients) if receivers != address]
                self.temp_msg = {"GET_MIRROR":address}
                self.bytesToSend = str.encode(json.dumps(self.temp_msg))
                for x in recv:
                    self.UDPServerSocket.sendto(self.bytesToSend, x)
                    print(f'sent GET MIRROR to {x}')

            if type(message) is dict:
                if list(message.keys())[0].split(" ")[0] == "INIT_MIRROR":
                    #TODO
                    message[list(message.keys())[0]]["sender"] = address
                    self.temp_msg = {"INIT_MIRROR":message}
                    self.bytesToSend = str.encode(json.dumps(self.temp_msg))
                    self.UDPServerSocket.sendto(self.bytesToSend, (message[list(message.keys())[0]]["receiver"][0],message[list(message.keys())[0]]["receiver"][1]))
                
            if str(message) not in self.message_keywords:
                self.clients_data[str(address)] = message
                self.clients_data[str(address)][str(address)] = address
                self.bytesToSend = str.encode(json.dumps(self.clients_data))
                # Sending a reply to client
                for clients in self.clients_data:
                    if clients not in self.message_keywords:
                        self.UDPServerSocket.sendto(self.bytesToSend, self.clients_data[clients][clients])
                        #print(f'sending{self.clients_data}')

if __name__ == "__main__":
    server_base().start()