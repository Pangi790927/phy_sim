import sys
import sim
import shapes

use_opengl = 'ogl' in sys.argv

Color = sim.Color
sim.init(width=800, height=800, scale=2, use_opengl=use_opengl)
s = sim.state.scale

_shapes = [
    shapes.Circle([0.5, 0.5], 0.2),
    shapes.Triangle([0, 0.1], [-0.1, -0.1], [0.1, -0.1], Color.RED, filled=True),
    shapes.AABB([-0.9, -0.9], [-0.5, -0.5]),
    shapes.Parallelogram([-0.8, 0.0], [0.3, 0.1], [0.1, 0.3]),
    shapes.Segment([0.2, -0.8], [0.5, -0.1])
]

def draw_axis():
    sim.draw_line([0, 0], [s, 0], Color.RED)
    sim.draw_line([0, 0], [0, s], Color.BLUE)
    sim.draw_line([0, 0], [0,-s], Color.GREEN)
    sim.draw_line([0, 0], [-s,0], Color.BLACK)

def draw_fn():
    draw_axis()
    for s in _shapes:
        s.draw()

sim.loop(draw_fn=draw_fn)
