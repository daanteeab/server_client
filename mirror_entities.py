from ursina import *
from direct.actor.Actor import Actor
from panda3d.core import Material

class cubeMirror(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.model="cube"
        self.speed = 1
        self.color=color.red

class mushroomMirror(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        
        #Actor and relevant actor attrs

        self.actor = Actor("assets/models/Mushroom.gltf")
        myMaterial = Material()
        myMaterial.setShininess(1.0) # Make this material shiny
        myMaterial.setAmbient((0, 0, 0, 0)) # Make this material blue
        self.actor.setMaterial(myMaterial)
        self.actor.setH(180)
        self.actor.reparent_to(self)
        PointLight(parent=self, y=2, z=3, shadows=False)
        self.speed = 1
        self.position = (-20,0,-20)
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.add_script(serverBehaviorMinions(entity=self))

class cactusMirror(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        
        #Actor and relevant actor attrs
        self.actor = Actor("assets/models/Cactus.gltf")
        myMaterial = Material()
        myMaterial.setShininess(1.0) # Make this material shiny
        myMaterial.setAmbient((0, 0, 0, 0)) # Make this material blue
        self.actor.setMaterial(myMaterial)
        self.actor.setH(180)
        self.actor.reparent_to(self)
        PointLight(parent=self, y=2, z=3, shadows=False)
        self.speed = 1
        self.position = (20,0,20)

        #collider
        self.collision = True
        self.collider = SphereCollider(entity=self, radius=1)
        self.intersects.ignore = (self,)

        for k, v in kwargs.items():
            setattr(self, k, v)
        
class serverBehaviorMinions():
    def __init__(self, entity, key_positions=None, **kwargs):
        self.entity = entity
        self.key_positions = key_positions
        self.key_positions = [(-20,0,-20), (-10,0,-20), (0,0,-20), (10,0,-20), (20,0,-20)]
        self.key_positions_index = 0
        self.tick_rate = 1
        self.last_tick = time.time()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def invoke_animate_position(self, ent, pos):
        #THIS FUNCTION EXISTS BECAUSE <invoke()> DOESNT RECOGNIZE <animate_someattr()> AS A FUNCTION
        #Calculates duration of movement based on distance/velocity
        dist_over_vel = distance(ent.position, pos)/ent.speed
        #Animates position
        ent.animate_position(pos, curve=curve.linear, duration=dist_over_vel)

    def animate_next_key_positions(self):
        if time.time()-self.last_tick > self.tick_rate and self.key_positions_index != 5:
            print(self.entity.intersects, self.entity.name)
            self.last_tick = time.time()
            if distance(self.entity.position, self.key_positions[self.key_positions_index])<1:
                self.key_positions_index += 1
                self.invoke_animate_position(ent=self.entity, pos=self.key_positions[self.key_positions_index])

    def update(self):
        self.animate_next_key_positions()

if __name__ == "__main__":
    app= Ursina()
    #some light
    pivot = Entity()
    DirectionalLight(parent=pivot, y=2, z=3, shadows=False)
    alight = AmbientLight(parent=pivot, y=2, z=3, shadows=False)
    alight.attenuation = (1, 0, 1)
    alight.setColor((0.05, 0.05, 0.05, 1))
    camera.position = (0,50,0)
    plane = Entity(model="plane", texture="brick", scale=50, double_sided=True)
    camera.look_at(plane)
    ents = {}
    for x in range(3):
        #mushroom rest instance
        ents["mush"+str(x)]= mushroomMirror(position=(-20+x,0,-20))

    def update():
        camera.z += (held_keys["w"]-held_keys["s"])*time.dt*20
        camera.x -= (held_keys["a"]-held_keys["d"])*time.dt*20

    app.run()