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
        
        
