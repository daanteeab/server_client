import socket
import json

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

        # Bind to address and ip
        self.UDPServerSocket.bind((self.localIP, self.localPort))
        self.message_keywords = set([])
        self.message_keywords.add("GET_ID")
        self.message_keywords.add("GET_CLIENTS")
        self.message_keywords.add("POST_MESSAGE")
        self.message_keywords.add("GET_MESSAGES")
        self.message_keywords.add("INIT_MIRROR")
        print("UDP server up and listening")
        # Listen for incoming datagrams

    def start(self):
        while(True):

            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)

            message = json.loads(bytesAddressPair[0])
            address = bytesAddressPair[1]

            #print(message)

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
                    print(f'sent GET CLIENTS to {address}')
                
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