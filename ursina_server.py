from ursina import *
from server import server_base
import json
import select

class Handler(server_base):
    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.client_instances = {}
        self.server_instances = {}
        
    def update(self):
        ready = select.select([self.UDPServerSocket], [], [], 0.01)
        if ready[0]:

            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)

            message = json.loads(bytesAddressPair[0])
            address = bytesAddressPair[1]

            #print(message)
            
            if len(self.clients)==2 and time.time()-self.gametimer>10:
                pass
                server_init_mirror_message = {"class":"mushroomMirror","sender":"server","id":self.server_entity_id}
                self.server_entity_id += 1
                temp_msg = {"INIT_MIRROR":{"INIT_MIRROR":server_init_mirror_message}}
                bytesToSend = str.encode(json.dumps(temp_msg))
                for clients in self.clients_data:
                    self.UDPServerSocket.sendto(bytesToSend, self.clients_data[clients][clients])

            if address not in self.clients:
                self.clients.add(address)
                self.wp.content += Text(str(address)),
                self.wp.layout()

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
            
                elif list(message.keys())[0] == "INIT_SERVER_MIRROR":
                    module = __import__("mirror_entities")
                    class_ = getattr(module, message["INIT_SERVER_MIRROR"]["class"])
                    self.client_instances[str(tuple(message["INIT_SERVER_MIRROR"]["sender"]))] = class_()
                    
                else:
                    #the | operator merges two dicts
                    self.clients_data[str(address)] = {str(address):address} | message
                    #Animates position based on right click position in world space
                    self.client_instances[str(address)].animate_position(message["mouse right"], duration=distance(self.client_instances[str(address)].position, message["mouse right"])/self.client_instances[str(address)].speed, curve=curve.linear)

                    #Complements the message before sending out with actual server position to correct wrong client position
                    #the | operator merges two dicts
                    self.clients_data[str(address)] = self.clients_data[str(address)] | {"server position":list(self.client_instances[str(address)].position)}

                    #Sends out all client data to all clients
                    self.bytesToSend = str.encode(json.dumps(self.clients_data))
                    # Sending a reply to client

                    for clients in self.clients_data:
                        self.UDPServerSocket.sendto(self.bytesToSend, self.clients_data[clients][clients])
                        #print(f'sending{self.clients_data}')

class lobbyClient(Entity):
    def __init__(self):
        super().__init__()
        self.wp = WindowPanel(title='Connections', content=(), parent=camera.ui, position=(-0.7,0.48), scale=(0.3,0.025))
        self.add_script(Handler(wp=self.wp))

if __name__ == "__main__":
    app= Ursina()
    lobbyClient()

    plane = Entity(model="plane", texture="brick", scale=50, double_sided=True)
    EditorCamera()
    app.run()