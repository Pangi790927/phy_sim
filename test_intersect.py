import sim
import numpy as np
from sim import Color
import intersect as isect

sim.init(width=800, height=800, scale=1)
s = sim.state.scale

A = [0, s]
B = [s, 0.1]
rad = 0.08

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

aabb = sim.ClickableCircle([0.1, -0.1], 0.03, color=Color.BLUE)
tria = sim.ClickableCircle([0.6, -0.1], 0.03, color=Color.BLUE)
para = sim.ClickableCircle([0.1, -0.6], 0.03, color=Color.BLUE)
circ = sim.ClickableCircle([0.6, -0.6], 0.03, color=Color.BLUE)

sim.clickable_add(c1)
sim.clickable_add(c2)
sim.clickable_add(l)

sim.clickable_add(aabb)
sim.clickable_add(tria)
sim.clickable_add(para)
sim.clickable_add(circ)

def draw_axis():
    sim.draw_line([0, 0], [s, 0], Color.RED)
    sim.draw_line([0, 0], [0, s], Color.BLUE)
    sim.draw_line([0, 0], [0,-s], Color.GREEN)
    sim.draw_line([0, 0], [-s,0], Color.BLACK)

def test_colinear_seg(A1, B1, A2, B2):
    sim.draw_line(A1, B1, Color.BLUE)
    sim.draw_line(A2, B2, Color.RED)
    int1 = isect.segment_segment(A1, B1, A2, B2)
    if int1:
        for p in int1:
            sim.draw_circle(p, 0.01)

    int2 = isect.segment_segment(A1, B1, l.pos, l.B)
    if int2:
        for p in int2:
            sim.draw_circle(p, 0.01)

    int3 = isect.segment_segment(A2, B2, l.pos, l.B)
    if int3:
        for p in int3:
            sim.draw_circle(p, 0.01)

def test_seg_seg_intersect():
    x_off = -1.
    A1, B1 = [0.3 + x_off, 0.0], [0.6 + x_off, -0.2]
    sim.draw_line(A1, B1)
    int1 = isect.segment_segment(A1, B1, l.pos, l.B)
    if int1:
        for p in int1:
            sim.draw_circle(p, 0.01)

    A2 , B2  = [0.3 + x_off, 0.2], [0.3 + x_off, 0.4]
    A2_, B2_ = [0.3 + x_off, 0.2], [0.3 + x_off, 0.4]
    test_colinear_seg(A2, B2, A2_, B2_)

    A3 , B3  = [0.4 + x_off, 0.3], [0.4 + x_off, 0.5]
    A3_, B3_ = [0.4 + x_off, 0.2], [0.4 + x_off, 0.4]
    test_colinear_seg(A3, B3, A3_, B3_)

    A4 , B4  = [0.5 + x_off, 0.1], [0.5 + x_off, 0.3]
    A4_, B4_ = [0.5 + x_off, 0.2], [0.5 + x_off, 0.4]
    test_colinear_seg(A4, B4, A4_, B4_)

    A5 , B5  = [0.6 + x_off, 0.5], [0.6 + x_off, 0.7]
    A5_, B5_ = [0.6 + x_off, 0.2], [0.6 + x_off, 0.4]
    test_colinear_seg(A5, B5, A5_, B5_)

def add_ints(ints, oth_ints):
    if oth_ints:
        for i in oth_ints:
            ints.append(i)

def test_shapes_intersect():
    AA, BB = [aabb.pos, aabb.pos + sim.Vec2(0.4, 0.4)]

    segs = isect._get_aabb_segs(AA, BB)
    for a, b in segs:
        sim.draw_line(a, b)

    O, N, M = [para.pos, sim.Vec2(0.2, -0.3), sim.Vec2(0.3, 0.3)]
    segs = isect._get_para_segs(O, N, M)
    for a, b in segs:
        sim.draw_line(a, b)

    E, F, G = [tria.pos, tria.pos + sim.Vec2(0.2, 0),
            tria.pos + sim.Vec2(0.1, 0.1)]
    segs = isect._get_tri_segs(E, F, G)
    for a, b in segs:
        sim.draw_line(a, b)

    C, r = [circ.pos, 0.2]
    sim.draw_circle(C, r)

    ints = []
    add_ints(ints, isect.circle_triangle(C, r, E, F, G))
    add_ints(ints, isect.circle_parallelogram(C, r, O, N, M))
    add_ints(ints, isect.aabb_circle(AA, BB, C, r))
    add_ints(ints, isect.aabb_parallelogram(AA, BB, O, N, M))
    add_ints(ints, isect.aabb_triangle(AA, BB, E, F, G))
    add_ints(ints, isect.parallelogram_triangle(O, N, M, E, F, G))

    for p in ints:
        sim.draw_circle(p, 0.01)

# will be called each frame, draw your stuff here
def draw_fn():
    draw_axis()
    sim.draw_aabb([0, 0], [0.5, 0.5])
    for i in np.linspace(0, 1, 30):
        sim.draw_dot([i, i])

    circle_intersect = isect.circle_circle(c1.pos, c1.radius, c2.pos, c2.radius)
    if circle_intersect:
        sim.draw_line(circle_intersect[0], circle_intersect[1], Color.GREEN)

    test_seg_seg_intersect()
    test_shapes_intersect()

sim.loop(draw_fn=draw_fn)
