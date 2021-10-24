import sys
import sim
import shapes
import interactive

use_opengl = 'ogl' in sys.argv

Color = sim.Color
sim.init(width=800, height=800, scale=2, use_opengl=use_opengl)
s = sim.state.scale

_shapes = [
    interactive.Movable(shapes.Circle, [0.5, 0.5], 0.2),
    interactive.Movable(shapes.Triangle,
            [0, 0.1], [-0.1, -0.1], [0.1, -0.1], Color.RED, filled=True),
    interactive.Movable(shapes.AABB, [-0.9, -0.9], [-0.5, -0.5]),
    interactive.Movable(shapes.Parallelogram,
            [-0.8, 0.0], [0.3, 0.1], [0.1, 0.3]),
    interactive.Movable(shapes.Segment, [0.2, -0.8], [0.5, -0.1])
]

# move the circle
def on_move_triangle(pos, old_pos):
    _shapes[0].shape.translate_origin(pos - old_pos)

# make the parallelogram reverse filled attribute
def on_click_aabb(pos, old_pos):
    _shapes[3].shape.filled = not _shapes[3].shape.filled

_shapes[1].on_move = on_move_triangle
_shapes[2].on_click = on_click_aabb

for shape in _shapes:
    sim.interactive_add(shape)

def draw_axis():
    sim.draw_line([0, 0], [s, 0], Color.RED)
    sim.draw_line([0, 0], [0, s], Color.BLUE)
    sim.draw_line([0, 0], [0,-s], Color.GREEN)
    sim.draw_line([0, 0], [-s,0], Color.BLACK)

def draw_fn():
    draw_axis()
    for s in _shapes:
        for u in _shapes:
            if u is not s:
                ints = s.shape.intersect(u.shape)
                if ints:
                    for i in ints:
                        shapes.Point(i, color=Color.GREEN/2, filled=True).draw()

sim.loop(draw_fn=draw_fn)
