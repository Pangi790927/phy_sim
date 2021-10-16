import abc
import glm
import sim
import intersect

# obs1: those classes need sim to be initialized

# this is the size of a point on screen, this will decide if a point intersects
# a segment
POINT_RELATIVE_SIZE = 0.01

class Shape():
    def __init__(self, color=sim.Color.BLACK, filled=False):
        self.color = color
        self.filled = filled

    def draw(self):
        Exception("implement draw!")

    def intersect(self, oth_shape):
        Exception("implement intersect!")

class Circle(Shape):
    def __init__(self, center, radius, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.C = glm.vec2(center)
        self.r = radius

    def intersect(self, oth):
        if isinstance(oth, Circle):
            return intersect.circle_circle(self.C, self.r, oth.C, oth.r)
        if isinstance(oth, Segment):
            return oth.intersect(self)
        if isinstance(oth, Triangle):
            return oth.intersect(self)
        if isinstance(oth, AABB):
            return oth.intersect(self)
        if isinstance(oth, Parallelogram):
            return oth.intersect(self)
        if isinstance(oth, Point):
            return oth.intersect(self)
        Exception("No known way to intersect with shape!")

    def draw(self):
        sim.draw_circle(self.C, self.r, color=self.color, filled=self.filled)

class Segment(Shape):
    def __init__(self, A, B, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.A = glm.vec2(A)
        self.B = glm.vec2(B)

    def intersect(self, oth):
        if isinstance(oth, Circle):
            return intersect.segment_circle(self.A, self.B, oth.C, oth.r)
        if isinstance(oth, Segment):
            return intersect.segment_segment(self.A, self.B, oth.A, oth.B)
        if isinstance(oth, Triangle):
            return oth.intersect(self)
        if isinstance(oth, AABB):
            return oth.intersect(self)
        if isinstance(oth, Parallelogram):
            return oth.intersect(self)
        if isinstance(oth, Point):
            return oth.intersect(self)
        Exception("No known way to intersect with shape!")

    def draw(self):
        sim.draw_line(self.A, self.B, color=self.color)

class Triangle(Shape):
    def __init__(self, E, F, G, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.E = glm.vec2(E)
        self.F = glm.vec2(F)
        self.G = glm.vec2(G)

    def intersect(self, oth):
        if isinstance(oth, Circle):
            return intersect.circle_triangle(oth.C, oth.r,
                    self.E, self.F, self.G)
        if isinstance(oth, Segment):
            return intersect.segment_triangle(oth.A, oth.B,
                    self.E, self.F, self.G)
        if isinstance(oth, Triangle):
            return intersect.triangle_triangle(self.E, self.F, self.G,
                    oth.E, oth.F, oth.G)
        if isinstance(oth, AABB):
            return oth.intersect(self)
        if isinstance(oth, Parallelogram):
            return oth.intersect(self)
        if isinstance(oth, Point):
            return oth.intersect(self)
        Exception("No known way to intersect with shape!")

    def draw(self):
        sim.draw_triangle(self.E, self.F, self.G,
                color=self.color, filled=self.filled)

class AABB(Shape):
    def __init__(self, AA, BB, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.AA = glm.vec2(AA)
        self.BB = glm.vec2(BB)

    def intersect(self, oth):
        if isinstance(oth, Circle):
            return intersect.aabb_circle(self.AA, self.BB, oth.C, oth.r)
        if isinstance(oth, Segment):
            return intersect.aabb_segment(self.AA, self.BB, oth.A, oth.B)
        if isinstance(oth, Triangle):
            return intersect.aabb_triangle(self.AA, self.BB, oth.E, oth.F, oth.G)
        if isinstance(oth, AABB):
            return intersect.aabb_aabb(self.AA, self.BB, oth.AA, oth.BB)
        if isinstance(oth, Parallelogram):
            return oth.intersect(self)
        if isinstance(oth, Point):
            return oth.intersect(self)
        Exception("No known way to intersect with shape!")

    def draw(self):
        AA, BB = intersect._aabb_fix(self.AA, self.BB)
        AB = glm.vec2(BB.x, AA.y)
        BA = glm.vec2(AA.x, BB.y)
        sim.draw_quad(AA, AB, BB, BA, color=self.color, filled=self.filled)

class Parallelogram(Shape):
    def __init__(self, O, N, M, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.O = glm.vec2(O)
        self.N = glm.vec2(N)
        self.M = glm.vec2(M)

    def intersect(self, oth):
        if isinstance(oth, Circle):
            return intersect.circle_parallelogram(oth.C, oth.r,
                    self.O, self.N, self.M)
        if isinstance(oth, Segment):
            return intersect.segment_parallelogram(oth.A, oth.B,
                    self.O, self.N, self.M)
        if isinstance(oth, Triangle):
            return intersect.parallelogram_triangle(self.O, self.N, self.M,
                    oth.E, oth.F, oth.G)
        if isinstance(oth, AABB):
            return intersect.aabb_parallelogram(oth.AA, oth.BB,
                    self.O, self.N, self.M)
        if isinstance(oth, Parallelogram):
            return intersect.parallelogram_parallelogram(self.O, self.N, self.M,
                    oth.O, oth.N, oth.M)
        if isinstance(oth, Point):
            return oth.intersect(self)
        Exception("No known way to intersect with shape!")

    def draw(self):
        OO = self.O
        NN = OO + self.N
        MN = OO + self.N + self.M
        MM = OO + self.M
        sim.draw_quad(OO, NN, MN, MM, color=self.color, filled=self.filled)

class Point(Shape):
    def __init__(self, pos, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos = glm.vec2(pos)

    # for point and segment we will consider our point to be a circle because
    # it's not very practical to consider it a mathematical point for the rest
    # of the framework
    def intersect(self, oth):
        if isinstance(oth, Circle):
            return intersect.point_circle(self.pos, oth.C, oth.r)
        if isinstance(oth, Segment):
            r = POINT_RELATIVE_SIZE * sim.state.scale
            return intersect.segment_circle(self.pos, r, oth.A, oth.B)
        if isinstance(oth, Triangle):
            return intersect.point_triangle(self.pos, oth.E, oth.F, oth.G)
        if isinstance(oth, AABB):
            return intersect.point_aabb(self.pos, oth.AA, oth.BB)
        if isinstance(oth, Parallelogram):
            return intersect.point_parallelogram(self.pos, oth.O, oth.N, oth.M)
        if isinstance(oth, Point):
            r = POINT_RELATIVE_SIZE * sim.state.scale
            return intersect.point_circle(self.pos, oth.pos, r)
        Exception("No known way to intersect with shape!")

    def draw(self):
        r = POINT_RELATIVE_SIZE * sim.state.scale
        sim.draw_circle(self.pos, r, color=self.color, filled=self.filled)