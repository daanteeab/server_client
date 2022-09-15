from ursina import *

class HealthBar():
    def __init__(self, entity, max_health, color):
        self.color = color
        self.entity = entity
        self.max_health = max_health
        self.bar = Entity(parent = self.entity, position = (0,2,0))
        self.bar_entity = Entity(model = "quad", parent = self.bar, scale = (self.entity.health/self.max_health, 0.2), billboard = True, position = (-1 + self.entity.health/self.max_health, 0, 0), color = self.color)

    def update(self):
        if self.entity.health > self.max_health:
            self.entity.health = self.max_health
        if self.entity.health < 0:
            self.entity.health = 0
            self.bar.disable()

        self.bar_entity.scale = (self.entity.health/self.max_health, 0.2)
        self.bar_entity.position = (-1 + self.entity.health/self.max_health, 0, 0)

class Tower(Entity):
    def __init__(self, enemy_team, tower_model_position, gtec, parent_ent):
        super().__init__()
        self.parent_ent = parent_ent
        self.gtec = gtec
        self.tower_model_position = tower_model_position + (0,3,0)
        self.enemy_team = enemy_team
        self.model = Mesh(vertices=[self.tower_model_position, Vec3(1,0,0)], mode='line', thickness=2)
        self.color = color.red
        self.tower_aggro_radius = Trigger(trigger_targets=(*self.gtec.__dict__[self.enemy_team], ), radius=5, color=hsv(90,1,1,0.5), position=self.parent_ent.position)
        #self.tower_aggro_radius.on_trigger_exit =  self._drop_target
        self.tower_aggro_radius.on_trigger_enter =  self._change_target
        self.len_gtec = len(self.gtec.__dict__[self.enemy_team])
        self.update_rate = 65678
        self.__i__ = 0
        self.target = None

        self.visible = False

    def _drop_target(self):
        self.target = None

    def _change_target(self):
        if not self.target:
            self.target = self.tower_aggro_radius.triggerers[0]
        
    def update(self):
        if self.target:
            self.visible = True
            self.model.vertices[1] = self.target.position
            self.model.generate()
            if self.target.health<0:
                self.visible = False
                self.target = None
                if any in self.tower_aggro_radius.triggerers:
                    print(f'switched target')
                    self._change_target()

        self.__i__ += 1
        if self.__i__ < self.update_rate:
            return

        self._i = 0

        if self.target:
            self.target.health -= 1

        if self.len_gtec != len(self.gtec.__dict__[self.enemy_team]):
            self.tower_aggro_radius.trigger_targets = (*self.gtec.__dict__[self.enemy_team], )
            self.len_gtec = len(self.gtec.__dict__[self.enemy_team])

class Draggable():
    def __init__(self, entity):
        self.entity = entity
        self.select = None
    
    def input(self, keys):
        if keys == "mouse left down":
            if mouse.hovered_entity:
                self.select = mouse.hovered_entity

        if keys == "mouse left up":
            self.select = None
    def update(self):
        if self.select:
            if mouse.world_point:
                self.select.position = (mouse.world_point[0], 0, mouse.world_point[2])

        




