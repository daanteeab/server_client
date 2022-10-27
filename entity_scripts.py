from ursina import *
from numpy import arctan2
from numpy import degrees
from ursina.trigger import Trigger

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
            #self.entity.health = 0
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
        self.tower_aggro_radius.on_trigger_exit =  self._drop_target
        self.tower_aggro_radius.on_trigger_enter =  self._change_target
        #self.tower_aggro_radius.on_trigger_exit = print("exit")
        #self.tower_aggro_radius.on_trigger_enter = print("enter")
        #self.tower_aggro_radius.on_trigger_stay = print("stay")
        self.len_gtec = len(self.gtec.__dict__[self.enemy_team])
        self.update_rate = 6
        self.__i__ = 0
        self.target = None
        self.visible = False

    def _drop_target(self):
        if len(self.tower_aggro_radius.triggerers) == 0:
            print(f'dropped target')
            self.target = None

    def _change_target(self):
        if not self.target:
            print(f'switched target')
            self.target = self.tower_aggro_radius.triggerers[0]
         
    def update(self):
        if self.target:
            self.visible = True
            self.model.vertices[1] = self.target.position
            self.model.generate()
            if self.target.health<0:
                self.visible = False
                self.target = None
                #print(self.tower_aggro_radius.triggerers)
                if len(self.tower_aggro_radius.triggerers)>0:
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
        if keys == "left mouse down":
            if mouse.hovered_entity:
                self.select = mouse.hovered_entity

        if keys == "left mouse up":
            self.select = None
    def update(self):
        if self.select:
            if mouse.world_point:
                self.select.position = (mouse.world_point[0], 0, mouse.world_point[2])

class serverBehaviorMinions():
    def __init__(self, entity, actor, hostile, key_positions=None, **kwargs):
        self.actor = actor
        self.entity = entity
        self.key_positions = key_positions
        self.key_positions_index = 0
        self.tick_rate = 1
        self.last_tick = time.time()
        self.hostile = hostile
        self.is_attacking = 1
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.goal_vector = (Vec3(self.key_positions[self.key_positions_index])-self.entity.position).normalized()
        self.actor.loop("Walk")
        self.bite_front = self.actor.getAnimControl("Bite_Front")
        self.bite_front.setPlayRate(0.5)
        self.death = self.actor.getAnimControl("Death")
        self.death_flag = False

    def animate_next_key_positions(self):
        #print(f'if {time.time()-self.last_tick} > {self.tick_rate} and {self.key_positions_index != 5}')
        if time.time()-self.last_tick > self.tick_rate and self.key_positions_index != 10:
            self.goal_vector = (Vec3(self.key_positions[self.key_positions_index])-self.entity.position).normalized()
            self.last_tick = time.time()
            #print(f'if {distance(self.entity.position, self.key_positions[self.key_positions_index])}<{1}')
            if distance(self.entity.position, self.key_positions[self.key_positions_index])<1:
                self.key_positions_index += 1
                self.goal_vector = (Vec3(self.key_positions[self.key_positions_index])-self.entity.position).normalized()
                #print(f'animating to {self.key_positions[self.key_positions_index]}')
                #self.invoke_animate_position(ent=self.entity, pos=self.key_positions[self.key_positions_index])

    def check_collision(self):
        intersect_vector = Vec3(0,0,0)
        self.entity.collisions = self.entity.intersects(traverse_target=scene, ignore=(self,))
        #print(f'collisions: {self.entity.collisions.entities}')
        for v in self.entity.collisions.entities:
            intersect_vector += v.position-self.entity.position
            if hasattr(v, "team") and self.is_attacking != 0:
                if v.team != self.entity.team:
                    self.attacking = v
                    self.is_attacking = 0
        return intersect_vector
    
    def _is_attacking(self):
        if self.is_attacking == 0 and not self.bite_front.isPlaying() and not self.death.isPlaying():
            self.attacking.health -= 5
            self.actor.play("Bite_Front")
            if self.attacking.health < 0:
                self.is_attacking = 1
                self.attacking = None

    def _health_under_zero(self):
        if self.entity.health<=0 and not self.death.isPlaying() and self.death_flag is False:
            self.actor.play("Death")
            invoke(setattr, self.entity, "enabled", False, delay=2)
            #self.entity.fade_out(value=0, duration=.5)  
            self.death_flag = True

    def update(self):
        if self.death_flag is False:
            self._health_under_zero()
            self.animate_next_key_positions()
            vec = self.check_collision()
            self._is_attacking()
            resulting_vec = (-vec + self.goal_vector*self.is_attacking).normalized()
            resulting_rot_y = degrees(arctan2(resulting_vec[0], resulting_vec[2]))
            self.entity.position += resulting_vec*time.dt
            self.entity.rotation_y = lerp(self.entity.rotation_y, resulting_rot_y, t=0.01)





