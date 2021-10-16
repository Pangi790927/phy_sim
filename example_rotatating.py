import sim
import time
import numpy as np

Color = sim.Color

sim.init(width=800, height=800, scale=2)
s = sim.state.scale

def draw_axis():
    sim.draw_line([0, 0], [s, 0], Color.RED)
    sim.draw_line([0, 0], [0, s], Color.BLUE)
    sim.draw_line([0, 0], [0,-s], Color.GREEN)
    sim.draw_line([0, 0], [-s,0], Color.BLACK)

# will be called each frame, draw your stuff here
def draw_fn():
    draw_axis()
    t = time.time()
    sim.draw_circle([np.cos(t), np.sin(t)], 0.1)

sim.loop(draw_fn=draw_fn)
