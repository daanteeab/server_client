from turtle import position
from ursina import *
from direct.actor.Actor import Actor
from panda3d.core import Material
from numpy import arctan2
from numpy import degrees
from entity_scripts import HealthBar
from entity_scripts import Tower
from entity_scripts import Draggable

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
        myMaterial.setAmbient((1, 1, 1, 1)) # Make this material blue
        self.actor.setMaterial(myMaterial)
        self.actor.setH(180)
        self.actor.reparent_to(self)
        #self.light = PointLight(parent=self, y=2, z=3, shadows=True)
        #self.light.attenuation = (0.2, 0.1, 0.1)
        self.speed = 1
        self.position = (-20,0,-20)
        self.team = "red"
        self.health = 50
        self.scale = 0.3

        #collider
        self.collision = True
        self.collider = SphereCollider(entity=self, radius=1)

        for k, v in kwargs.items():
            setattr(self, k, v)
        self.add_script(serverBehaviorMinions(entity=self, actor=self.actor, hostile="green", key_positions=[(-20,0,-20), (-10,0,-20), (0,0,-20), (10,0,-20), (20,0,-20), (23,0,-10), (20,0,0), (17,0,10), (20,0,20)]))
        self.add_script(HealthBar(entity=self, max_health=50, color=color.red))

class cactusMirror(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        
        #Actor and relevant actor attrs
        self.actor = Actor("assets/models/Cactus.gltf")
        myMaterial = Material()
        myMaterial.setShininess(1.0) # Make this material shiny
        myMaterial.setAmbient((1, 1, 1, 1)) # Make this material blue
        self.actor.setMaterial(myMaterial)
        self.actor.setH(0)
        self.actor.reparent_to(self)
        #self.light = PointLight(parent=self, y=2, z=3, shadows=True)
        #self.light.attenuation = (1, 0.1, 0.1)
        self.speed = 1
        self.position = (20,0,20)
        self.team = "green"
        self.health = 50
        self.scale = 0.3

        #collider
        self.collision = True
        self.collider = SphereCollider(entity=self, radius=1)

        for k, v in kwargs.items():
            setattr(self, k, v)
        self.add_script(serverBehaviorMinions(entity=self, actor=self.actor, hostile="red", key_positions=[(20,0,20), (20,0,10), (20,0,0), (20,0,-10), (20,0,-20), (10,0,-23), (0,0,-20), (-10,0,-17), (-20,0,-20)]))
        self.add_script(HealthBar(entity=self, max_health=50, color=color.green))

class boidContainer(Entity):
    def __init__(self, gtec, **kwargs):
        super().__init__()
        self.mirror_type = "red"
        self.boids = {}
        self.id = 0
        self.center = Vec3(0,0,0)
        self.gtec = gtec
        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.mirror_type == "red":
            #print("creating red boids")
            for x in range(6):
                self.boids[self.id] = mushroomMirror(position=(-20+random.random(),0,-20+random.random()))
                self.gtec.red += self.boids[self.id],
        if self.mirror_type == "green":
            #print("creating green boids")
            for x in range(6):
                self.boids[self.id] = cactusMirror(position=(20+random.random(),0,20+random.random()))
                self.gtec.green += self.boids[self.id],
                self.id += 1

    def update(self):
        x_hat = Vec3(0,0,0)
        for x, y  in self.boids.items():
            x_hat += y.position
        self.center = x_hat/6
        for i, j  in self.boids.items():
            j.position += (self.center-j.position)*time.dt*0.1

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
        if self.entity.health<0 and not self.death.isPlaying() and self.death_flag is False:
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

class actorMirror(Entity):
    def __init__(self, actor, gtec = None, tower = None, **kwargs):
        super().__init__()
        #Actor and relevant actor attrs
        self.model = actor
        #self.actor = Actor("self.actor")
        myMaterial = Material()
        myMaterial.setShininess(1.0) # Make this material shiny
        myMaterial.setAmbient((0, 0, 0, 0)) # Make this material blue
        self.model.setMaterial(myMaterial)
        self.model.setH(180)
        self.model.reparent_to(self)
        self.collision = True
        self.light = PointLight(parent=self, y=2, z=3, shadows=False)
        self.collider = SphereCollider(entity=self)
        self.gtec = gtec
        self.tower = tower
        for k, v in kwargs.items():
            setattr(self, k, v)
        
        if hasattr(self, "health"):
            self.add_script(HealthBar(entity=self, max_health=500, color=color.yellow))

        if self.tower:
            self.add_script(Tower(enemy_team=self.enemy_team, tower_model_position=self.position, gtec=self.gtec, parent_ent=self))

    def update(self):
        if hasattr(self, "health"):
            if self.health < 0:
                self.enabled=False

class globalTeamEntityContainer():
    def __init__(self):
        self.red = ()
        self.green = ()

if __name__ == "__main__":
    app= Ursina()
    #some light
    pivot = Entity()
    alight = AmbientLight(parent=pivot, y=2, z=3, shadows=False)
    alight.attenuation = (0.05, 0.2, 0.2)
    alight.setColor((1, 1, 1, 1))
    #camera.position = (0,50,0)
    plane = Entity(model="plane", texture="brick", scale=50, double_sided=True)
    #camera.look_at(plane)
    gtec = globalTeamEntityContainer()
    structs = []
    structs.append(actorMirror(actor="assets/models/OBJ/WatchTower_FirstAge_Level3.obj", position = (17,0,10), team="green", health=500, tower=True, gtec=gtec, enemy_team="red"))
    structs.append(actorMirror(actor="assets/models/OBJ/WatchTower_FirstAge_Level3.obj", position = (10,0,17), team="green", health=500, tower=True, gtec=gtec, enemy_team="red"))
    structs.append(actorMirror(actor="assets/models/OBJ/WatchTower_FirstAge_Level2.obj", position = (-23,0,10), team="red", health=500, tower=True, gtec=gtec, enemy_team="green"))
    structs.append(actorMirror(actor="assets/models/OBJ/WatchTower_FirstAge_Level2.obj", position = (23,0,-10), team="green", health=500, tower=True, gtec=gtec, enemy_team="red"))
    structs.append(actorMirror(actor="assets/models/OBJ/WatchTower_FirstAge_Level3.obj", position = (-17,0,-10), team="red", health=500, tower=True, gtec=gtec, enemy_team="green"))
    structs.append(actorMirror(actor="assets/models/OBJ/WatchTower_FirstAge_Level2.obj", position = (-10,0,23), team="green", health=500, tower=True, gtec=gtec, enemy_team="red"))
    structs.append(actorMirror(actor="assets/models/OBJ/WatchTower_FirstAge_Level3.obj", position = (-10,0,-17), team="red", health=500, tower=True, gtec=gtec, enemy_team="green"))
    structs.append(actorMirror(actor="assets/models/OBJ/WatchTower_FirstAge_Level2.obj", position = (10,0,-23), team="red", health=500, tower=True, gtec=gtec, enemy_team="green"))

    structs.append(actorMirror(actor="assets/models/OBJ/Temple_FirstAge_Level1.obj", position = (-23,0,-23), team="red", health=5000, tower=True, gtec=gtec, enemy_team="green"))
    structs.append(actorMirror(actor="assets/models/OBJ/Temple_FirstAge_Level1.obj", position = (23,0,23), team="green", health=5000, tower=True, gtec=gtec, enemy_team="red"))

    #actorMirror(actor="assets\models\OBJ\Mountain_Single.obj", position = (0,0,0), scale=2)
    actorMirror(actor="assets\models\OBJ\Mountain_Group_1.obj", position = (0,0,0), scale=(4,2,4))
    #actorMirror(actor="assets\models\OBJ\Mountain_Group_2.obj", position = (-10,0,0), scale=4)
    #actorMirror(actor="assets\models\OBJ\MountainLarge_Single.obj", position = (0,0,10), scale=2)
    mine = actorMirror(actor="assets\models\OBJ\Mine.obj", position = (-25,0,25), scale=2)
    actorMirror(actor="assets\models\OBJ\Farm_SecondAge_Level3_Wheat", position = (25,0,-25), scale=2)
    #mine.add_script(Draggable(entity=mine))
    for x in structs:
        setattr(x, "scale", 2)

    EditorCamera()

    boidContainer(mirror_type="red", gtec=gtec)
    boidContainer(mirror_type="green", gtec=gtec)
    global_time = [time.time()]
    def update():
        if time.time() - global_time[0] > 10:
            boidContainer(mirror_type="red", gtec=gtec)
            boidContainer(mirror_type="green", gtec=gtec)
            global_time[0] = time.time()
    app.run()