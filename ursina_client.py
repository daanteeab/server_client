from ursina import *
from client import client_base
import json
import select

class ursinaClientSide(client_base):
    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.__handshakes__ = set([])
        self.id = None

class Sender():
    def __init__(self, client, entity):
        self.entity = entity
        self.client = client
        self.init_msg = "GET_ID"
        bytesToSend = str.encode(json.dumps(self.init_msg))
        self.client.UDPClientSocket.sendto(bytesToSend, self.client.serverAddressPort)
    
    def movement(self):
        x_v = (held_keys["w"]-held_keys["s"])*time.dt*10
        y_v = (held_keys["a"]-held_keys["d"])*time.dt*10
        vector = Vec2(x_v, y_v)
        return vector

    def y_rot(self):
        ry_v = (held_keys["q"]-held_keys["e"])*time.dt*20
        return ry_v
    
    def update(self):
        #vector = self.movement()
        #rot_y = self.y_rot()
        #attrs_to_send = {"position":[self.entity.x+vector[0], self.entity.y, self.entity.z+vector[1]],"rotation_y":self.entity.rotation_y+rot_y,"time":time.time()}
        #bytesToSend = str.encode(json.dumps(attrs_to_send))
        #print(f'sending{attrs_to_send}')
        #self.client.UDPClientSocket.sendto(bytesToSend, self.client.serverAddressPort)
        if mouse.right:
            if mouse.world_point is not None:
                attrs_to_send = {"position":[mouse.world_point.x,mouse.world_point.y,mouse.world_point.z],"rotation_y":self.entity.rotation_y,"time":time.time()}
                bytesToSend = str.encode(json.dumps(attrs_to_send))
                print(f'sending{attrs_to_send}')
                self.client.UDPClientSocket.sendto(bytesToSend, self.client.serverAddressPort)

class Receiver():
    def __init__(self, client, entity):
        self.entity = entity
        self.client = client
        self.id = None
        self.message_keywords = set([])
        self.message_keywords.add("GET_ID")
        self.message_keywords.add("GET_CLIENTS")
        self.message_keywords.add("POST_MESSAGE")
        self.message_keywords.add("GET_MESSAGES")
        self.message_keywords.add("INIT_MIRROR")
        self.message_keywords.add("GET_MIRROR")
        self.rubber = {}
        self.msg_keywords = {"Entity"}
        self.rubber_var = 0.016
    
    def rubber(self, ip, attr):
        self.rubber[ip+attr] = []
    
    def _get_id(self, keys):
        if keys == "GET_ID":
            self.id = self.client.msg[keys]
            self.client.id = self.client.msg[keys]
            print(f'set id to {self.client.msg[keys]}')
        
    def _get_mirror(self, keys):
        if keys == "GET_MIRROR":
            attrs_to_send = {f'INIT_MIRROR FROM {self.client.id} TO {self.client.msg["GET_MIRROR"]}':{"class":"cubeMirror","receiver":self.client.msg["GET_MIRROR"]}}
            bytesToSend = str.encode(json.dumps(attrs_to_send))
            print(f'GET_MIRROR request: {attrs_to_send}')
            self.client.UDPClientSocket.sendto(bytesToSend, self.client.serverAddressPort)

    def pass_old_msg(self, keys):
        if "time" in set(self.client.msg[keys].keys()):
            if time.time()-self.client.msg[keys]["time"]>self.rubber_var:
                pass
 
    def update(self):
        ready = select.select([self.client.UDPClientSocket], [], [], 0.02)
        if ready[0]:
            msgFromServer = self.client.UDPClientSocket.recvfrom(self.client.bufferSize)
            #msgFromServer = self.client.UDPClientSocket.recvfrom(self.client.bufferSize)
            self.client.msg = json.loads(msgFromServer[0])
            for keys in self.client.msg:
                self._get_id(keys=keys)
                self._get_mirror(keys=keys)
                if keys not in self.message_keywords:
                    if self.client.msg[keys][keys] == self.id:
                        self.pass_old_msg(keys=keys)
                        [setattr(self.entity, i , self.client.msg[keys][i]) for i in self.client.msg[keys]]
                        
                        #'''LIST COMPREHENTION ABOVE REPLACES LOOP BELOW'''#

                        #for i in self.client.msg[keys]:
                            #if self.client.msg[keys][i] is float:
                                #self.rubber()
                            #setattr(self.entity, i , self.client.msg[keys][i])

                    if str(self.client.msg[keys][keys]) in self.client.instances:
                        print(f'setattrs for {self.client.instances[str(self.client.msg[keys][keys])]} with type {type(self.client.instances[str(self.client.msg[keys][keys])])}')
                        [setattr(self.client.instances[str(self.client.msg[keys][keys])], i , self.client.msg[keys][i]) for i in self.client.msg[keys]]

                        #'''LIST COMPREHENTION ABOVE REPLACES LOOP ABOVE, (does the same thing)'''#

class Getter():
    def __init__(self, client, entity):
        self.entity = entity
        self.client = client
        self.init_msg = "GET_CLIENTS"
        bytesToSend = str.encode(json.dumps(self.init_msg))
        self.client.UDPClientSocket.sendto(bytesToSend, self.client.serverAddressPort)

    def new_client_to___handshakes___(self, keys):
        [self.client.__handshakes__.add(str(self.client.msg[keys][x])) for x in range(len(self.client.msg[keys])) if str(self.client.msg[keys][x]) != str(self.client.id)]
        [print(f'__handshakes__ updated to {self.client.__handshakes__} with new client {self.client.msg[keys][x]}') for x in range(len(self.client.msg[keys])) if str(self.client.msg[keys][x]) != str(self.client.id)]

    def update(self):
        [self.new_client_to___handshakes___(keys) for keys in self.client.msg if keys == "GET_CLIENTS" and str(self.client.msg[keys]) not in self.client.__handshakes__]
        '''LIST COMPREHENTION ABOVE REPLACES THIS CODE BELOW'''
        
        #for keys in self.client.msg:
            #if keys == "GET_CLIENTS":
                #if str(self.client.msg[keys]) not in self.client.__handshakes__:
                    #List comprehention to loo
                    #[self.client.__handshakes__.add(str(self.client.msg[keys][x])) for x in range(len(self.client.msg[keys])) if str(self.client.msg[keys][x]) != str(self.client.id)]
                    #[print(f'__handshakes__ updated to {self.client.__handshakes__} with new client {self.client.msg[keys][x]}') for x in range(len(self.client.msg[keys])) if str(self.client.msg[keys][x]) != str(self.client.id)]

class RequestMirror():
    def __init__(self, client, entity):
        self.client = client
        self.entity = entity
        self.has_mirrors = set([])
    
    def new_mirror_condition(self):
        for x in list(self.client.__handshakes__):
            if x not in self.has_mirrors:
                init_msg = "GET_MIRROR"
                bytesToSend = str.encode(json.dumps(init_msg))
                self.client.UDPClientSocket.sendto(bytesToSend, self.client.serverAddressPort)
                self.has_mirrors.add(x)
    
    def update(self):
        self.new_mirror_condition()

class InitiateMirror():
    def __init__(self, client, entity):
        self.client = client
        self.entity = entity
        self.client.instances = {}
    
    def parse_client_msg(self):
        if type(self.client.msg) is dict:
            if list(self.client.msg.keys())[0] == "INIT_MIRROR":
                module = __import__("mirror_entities")
                class_ = getattr(module, self.client.msg["INIT_MIRROR"][list(self.client.msg["INIT_MIRROR"].keys())[0]]["class"])
                self.client.instances[str(self.client.msg["INIT_MIRROR"][list(self.client.msg["INIT_MIRROR"].keys())[0]]["sender"])] = class_()

    def update(self):
        self.parse_client_msg()

class lobbyClient(Entity):
    def __init__(self):
        super().__init__()
        self.ipf_ip_text = Text(text="IP", position=(-0.25,0.15),)
        self.ipf_ip = InputField(default_value="127.0.0.1", position=(0,0.1))
        self.ipf_ip_port = Text(text="Port", position=(-0.25,0))
        self.ipf_port = InputField(default_value="20001", position=(0,-0.05))
        self.connect_btn = Button(text="Connect", position=(0.32, -0.05), scale=(0.1,0.05), color=color.green)
        self.disconnect_btn = Button(text="DC", position=(0.7,0.475), scale=(0.07,0.025), color=color.red, enabled=False)
        self.ui_elements = [self.ipf_ip, self.ipf_port, self.ipf_ip_text, self.ipf_ip_port, self.connect_btn]
        self.player_base = None
        self.ursina_client_side = None

    def connect_to_server(self):
        self.ursina_client_side = ursinaClientSide(serverAddressPort=(self.ipf_ip.text, int(self.ipf_port.text)))
        self.player_base = playerBase()
        self.player_base.add_script(Sender(client=self.ursina_client_side, entity=self.player_base))
        self.player_base.add_script(Receiver(client=self.ursina_client_side, entity=self.player_base))
        self.player_base.add_script(Getter(client=self.ursina_client_side, entity=self.player_base))
        self.player_base.add_script(RequestMirror(client=self.ursina_client_side, entity=self.player_base))
        self.player_base.add_script(InitiateMirror(client=self.ursina_client_side, entity=self.player_base))
        self.disconnect_btn.enabled=True
        #self.add_script(Sender(client=self.ursina_client_side, entity=self.player_base))
        #self.add_script(Receiver(client=self.ursina_client_side, entity=self.player_base))
        [x.disable() for x in self.ui_elements]
    
    def disconnect_from_server(self):
        self.ursina_client_side.UDPClientSocket.close()
        self.ursina_client_side.disable()
        self.player_base.disable()
        [x.enable() for x in self.ui_elements]
        self.disconnect_btn.enabled=False

class playerBase(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.tag = Text(parent=self, text=self.name)
        self.model="cube"
        self.client_message = None
        self.position = (0,0,0)
        
        for k, v in kwargs.items():
            setattr(self, k, v)

if __name__ == "__main__":
    app = Ursina()
    camera.position = (-20,0,0)
    plane = Entity(model="plane", texture="brick", scale=5, collision=True, rotation_z=90, double_sided=True)
    plane.collider = "mesh"
    camera.look_at(plane)

    lc = lobbyClient()
    lc.connect_btn.on_click = lc.connect_to_server
    lc.disconnect_btn.on_click = lc.disconnect_from_server
    app.run()
