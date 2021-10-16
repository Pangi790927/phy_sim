import sim
import time
import numpy as np
from pygame.locals import *

Color = sim.Color

TIME_STEP = 0.01
time_state = sim.dotdict({
    'time': 0,
    'paused': True
})

sim.init(width=800, height=800, scale=1)
s = sim.state.scale

def increment_time():
    time_state.time += TIME_STEP

def draw_axis():
    sim.draw_line([0, 0], [s, 0], Color.RED)
    sim.draw_line([0, 0], [0, s], Color.BLUE)
    sim.draw_line([0, 0], [0,-s], Color.GREEN)
    sim.draw_line([0, 0], [-s,0], Color.BLACK)

def event_fn(event):
    # http://www.pygame.org/docs/ref/key.html 
    if event.type == KEYDOWN:
        if event.key == K_p:
            time_state.paused = not time_state.paused
        if time_state.paused and event.key == K_n:
            increment_time()

def draw_fn():
    if not time_state.paused:
        increment_time()
    draw_axis()
    t = time_state.time
    sim.draw_circle([np.cos(t) / 2, np.sin(t) / 2], 0.1)

sim.loop(draw_fn=draw_fn, event_fn=event_fn)
