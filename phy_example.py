import sim
import numpy as np
from sim import Color

sim.init(width=800, height=800, scale=1)
s = sim.state.scale

A = [0, s]
B = [s, 0.1]
rad = 0.04

c1 = sim.ClickableCircle(A, rad)
c2 = sim.ClickableCircle(B, rad, color=Color.BLUE)
l = sim.ClickableLine(A, B, color=Color.RED)

def move_A(pos):
    l.pos = c1.pos

def move_B(pos):
    l.B = c2.pos

def move_AB(pos):
    c1.pos = l.pos
    c2.pos = l.B

c1.set_on_move(move_A)
c2.set_on_move(move_B)
l.set_on_move(move_AB)

sim.clickable_add(c1)
sim.clickable_add(c2)
sim.clickable_add(l)

def draw_axis():
    sim.draw_line([0, 0], [s, 0], Color.RED)
    sim.draw_line([0, 0], [0, s], Color.BLUE)
    sim.draw_line([0, 0], [0,-s], Color.GREEN)
    sim.draw_line([0, 0], [-s,0], Color.BLACK)

# will be called each frame, draw your stuff here
def draw_fn():
    draw_axis()
    sim.draw_rect([0, 0], [0.5, 0.5])
    for i in np.linspace(0, 1, 30):
        sim.draw_dot([i, i])
    sim.draw_circle([-0.5, -0.5], 0.5)

sim.loop(draw_fn=draw_fn)
