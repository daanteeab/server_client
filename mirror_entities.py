from ursina import *

class cubeMirror(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.model="cube"
        self.color=color.red
        
        
