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
        raise Exception("implement draw!")

    def intersect(self, oth_shape):
        raise Exception("implement intersect!")

    def get_origin(self):
        raise Exception("implement get origin")

    def set_origin(self, pos):
        raise Exception("implement set origin")

    def translate_origin(self, diff):
        raise Exception("implement translate origin")

    # this function is the main reason for having a Point Shape
    def intersect_point(self, pos):
        p = Point(pos)
        return p.intersect(self)

class Circle(Shape):
    def __init__(self, center, radius, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.C = glm.vec2(center)
        self.r = radius
        self.origin = self.C

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
        raise Exception("No known way to intersect with shape!")

    def draw(self):
        sim.draw_circle(self.C, self.r, color=self.color, filled=self.filled)

    def get_origin(self):
        return self.C

    def set_origin(self, pos):
        self.C = glm.vec2(pos)

    def translate_origin(self, diff):
        self.C += glm.vec2(diff)

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
        raise Exception("No known way to intersect with shape!")

    def draw(self):
        sim.draw_line(self.A, self.B, color=self.color)

    def get_origin(self):
        return self.A

    def set_origin(self, pos):
        diff = self.B - self.A
        self.A = glm.vec2(pos)
        self.B = self.A + diff

    def translate_origin(self, diff):
        self.A += glm.vec2(diff)
        self.B += glm.vec2(diff)

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
        raise Exception("No known way to intersect with shape!")

    def draw(self):
        sim.draw_triangle(self.E, self.F, self.G,
                color=self.color, filled=self.filled)

    def get_origin(self):
        return self.E

    def set_origin(self, pos):
        diffF = self.F - self.E
        diffG = self.G - self.E
        self.E = glm.vec2(pos)
        self.F = self.F + diffF
        self.G = self.G + diffG

    def translate_origin(self, diff):
        self.E += glm.vec2(diff)
        self.F += glm.vec2(diff)
        self.G += glm.vec2(diff)

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
        raise Exception("No known way to intersect with shape!")

    def draw(self):
        AA, BB = intersect._aabb_fix(self.AA, self.BB)
        AB = glm.vec2(BB.x, AA.y)
        BA = glm.vec2(AA.x, BB.y)
        sim.draw_quad(AA, AB, BB, BA, color=self.color, filled=self.filled)

    def get_origin(self):
        return self.AA

    def set_origin(self, pos):
        diff = self.BB - self.AA
        self.AA = glm.vec2(pos)
        self.BB = self.AA + diff

    def translate_origin(self, diff):
        self.AA += glm.vec2(diff)
        self.BB += glm.vec2(diff)


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
        raise Exception("No known way to intersect with shape!")

    def draw(self):
        OO = self.O
        NN = OO + self.N
        MN = OO + self.N + self.M
        MM = OO + self.M
        sim.draw_quad(OO, NN, MN, MM, color=self.color, filled=self.filled)

    def get_origin(self):
        return self.O

    def set_origin(self, pos):
        self.O = glm.vec2(pos)

    def translate_origin(self, diff):
        self.O += glm.vec2(diff)


class Point(Shape):
    def __init__(self, P, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.P = glm.vec2(P)

    # for point and segment we will consider our point to be a circle because
    # it's not very practical to consider it a mathematical point for the rest
    # of the framework
    def intersect(self, oth):
        if isinstance(oth, Circle):
            return intersect.point_circle(self.P, oth.C, oth.r)
        if isinstance(oth, Segment):
            r = POINT_RELATIVE_SIZE * sim.state.scale
            return intersect.segment_circle(oth.A, oth.B, self.P, r)
        if isinstance(oth, Triangle):
            return intersect.point_triangle(self.P, oth.E, oth.F, oth.G)
        if isinstance(oth, AABB):
            return intersect.point_aabb(self.P, oth.AA, oth.BB)
        if isinstance(oth, Parallelogram):
            return intersect.point_parallelogram(self.P, oth.O, oth.N, oth.M)
        if isinstance(oth, Point):
            r = POINT_RELATIVE_SIZE * sim.state.scale
            return intersect.point_circle(self.P, oth.P, r)
        raise Exception("No known way to intersect with shape!")

    def draw(self):
        r = POINT_RELATIVE_SIZE * sim.state.scale
        sim.draw_circle(self.P, r, color=self.color, filled=self.filled)

    def get_origin(self):
        return self.P

    def set_origin(self, pos):
        self.P = glm.vec2(pos)

    def translate_origin(self, diff):
        self.P += glm.vec2(diff)
