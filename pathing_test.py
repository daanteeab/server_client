from ursina import *

app = Ursina()
camera.position = (0,50,0)
plane = Entity(model="plane", texture="brick", scale=50, collision=True, double_sided=True)
plane.collider = "mesh"
camera.look_at(plane)
cube = Entity(model="cube")
cube_2 = Entity(model="cube", x=5, color=color.green)

speed=1

def func(ent, pos, val):
    ent.animate_position(pos, curve=curve.linear, duration=val)

cube.animate_position(Vec3(-3,0,1), duration=distance(list(cube.position), Vec3(-5,0,-5)/speed), curve=curve.linear)

invoke(func, ent=cube, pos=(-5,0,-5), val=distance(cube.position, Vec3(-5,0,-5)/speed), delay=2)

def update():
    camera.z += (held_keys["w"]-held_keys["s"])*time.dt*20
    camera.x -= (held_keys["a"]-held_keys["d"])*time.dt*20
app.run()