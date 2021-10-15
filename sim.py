import abc
import pygame, sys
import glm
from pygame.locals import *

# Utils:
# ==============================================================================

class Color:
    BLACK = (  0,   0,   0)
    RED =   (255,   0,   0)
    GREEN = (  0, 255,   0)
    BLUE =  (  0,   0, 255)
    WHITE = (255, 255, 255)

class _dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def _none_fn(*args, **kwargs):
    pass

Vec2 = glm.vec2
Vec3 = glm.vec3
Vec4 = glm.vec4

# https://codereview.stackexchange.com/questions/86421/
#       line-segment-to-circle-collision-algorithm
def seg_circ_intersect(A, B, Q, rad):
    V = B - A
    a = glm.dot(V, V)
    b = 2 * glm.dot(V, A - Q)
    c = glm.dot(A, A) + glm.dot(Q, Q) - 2 * glm.dot(A, Q) - rad**2
    disc = b**2 - 4*a*c
    if disc < 0:
        return None, None
    t1 = (-b + disc ** 0.5) / (2 * a)
    t2 = (-b - disc ** 0.5) / (2 * a)
    I1 = A + V * t1 if 0 <= t1 <= 1 else None
    I2 = A + V * t2 if 0 <= t2 <= 1 else None
    return I1, I2

# Screen and state:
# ==============================================================================

state = None
def init(width, height, scale=1):
    global state
    state = _dotdict({
        'width': None,
        'height': None,
        'scale': None,
        'surface': None,
        'alive': False,
        'clickable': None,
    })
    state.width = width
    state.height = height
    state.scale = scale
    state.alive = True
    pygame.init()
    if state.width < state.height:
        print("WARNING: width can't be smaller than height, will clip height")
        state.height = state.width
    state.surface = pygame.display.set_mode((state.width, state.height), 0, 32)
    _clickable_init()

def _intern_exit(exit_fn=_none_fn):
    global state
    pygame.quit()
    exit_fn()
    state.alive = False

def loop(draw_fn, event_fn=_none_fn, exit_fn=_none_fn):
    while state.alive:
        for event in pygame.event.get():
            if event.type == QUIT:
                _intern_exit(exit_fn)
                break
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    _intern_exit(exit_fn)
                    break

            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                _clickable_on_move(pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                _clickable_on_click(pos)

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                _clickable_on_release(pos)

            event_fn(event)
        if not state.alive:
            break
        state.surface.fill(Color.WHITE)
        draw_fn()
        _clickable_on_draw()
        pygame.display.update()


# Draw primitives:
# ==============================================================================

# this is how the coordinate system looks:
#        (0,s) ^ +y
#              |
#              |
# (-s,0)       |(0, 0)      +x
#    <---------o----------->
#   -x         |         (s,0)
#              |
#              |
#           -y v (0,-s)
# 
# where:
#   s - scale

# transforms position from coord space to space coords
def pos2screen(pos):
    x = pos[0] / state.scale
    y = pos[1] / state.scale
    screen_x = (x + 1) * state.height / 2 + (state.width - state.height) / 2
    screen_y = (1 - y) * state.height / 2
    return (int(screen_x), int(screen_y))

def screen2pos(pos):
    x = (pos[0] - (state.width - state.height) / 2) / state.height * 2 - 1
    y = -pos[1] / state.height * 2 + 1
    return (x * state.scale, y * state.scale)

def dist2screen(dist):
    return int(dist / state.scale * state.height / 2)

def draw_line(posA, posB, color=Color.BLACK):
    posA = pos2screen(posA)
    posB = pos2screen(posB)
    pygame.draw.line(state.surface, color, posA, posB)

def draw_dot(pos, color=Color.BLACK):
    pos = pos2screen(pos)
    state.surface.set_at(pos, color)

def draw_rect(posA, posB, color=Color.BLACK, filled=False):
    posA = pos2screen(posA)
    posB = pos2screen(posB)
    minx = min(posA[0], posB[0])
    miny = min(posA[1], posB[1])
    maxx = max(posA[0], posB[0])
    maxy = max(posA[1], posB[1])
    border = 1
    if filled:
        border = 0
    pygame.draw.rect(state.surface, color,
            pygame.Rect(minx, miny, maxx - minx, maxy - miny), border)

def draw_circle(pos, rad, color=Color.BLACK, filled=False):
    pos = pos2screen(pos)
    rad = dist2screen(rad)
    border = 1
    if filled:
        border = 0
    pygame.draw.circle(state.surface, color, pos, rad, border)

# Clickable objects:
# ==============================================================================

# desc:
# those will be allways drawn on the screen(default: on top of everything)

class Clickable:
    def __init__(self, pos, on_click_cbk=None, on_release_cbk=None,
            on_move_cbk=None):
        self.pos = Vec2(pos)
        self.is_clicked = False
        self.on_click_cbk = on_click_cbk
        self.on_release_cbk = on_release_cbk
        self.on_move_cbk = on_move_cbk

    def set_on_click(self, on_click_cbk):
        self.on_click_cbk = on_click_cbk

    def set_on_release(self, on_release_cbk):
        self.on_release_cbk = on_release_cbk

    def set_on_move(self, on_move_cbk):
        self.on_move_cbk = on_move_cbk

    def draw(*args, **kwargs):
        Exception('please implement a draw function inside child')

    def on_click(self, clicked: bool, pos):
        if clicked:
            self.is_clicked = True
            if self.on_click_cbk:
                self.on_click_cbk(pos)
        return False

    def on_release(self, pos):
        self.is_clicked = False
        if self.on_release_cbk:
            self.on_release_cbk(pos)

    def on_move(self, pos):
        if self.is_clicked:
            self.pos = self.pos + pos - state.clickable.old_pos
            if self.on_move_cbk:
                self.on_move_cbk(pos)

class ClickableCircle(Clickable):
    def __init__(self, pos, radius, color=Color.BLACK, on_click_cbk=None,
            on_release_cbk=None, on_move_cbk=None):
        super().__init__(pos, on_click_cbk=on_click_cbk,
                on_release_cbk=on_release_cbk, on_move_cbk=on_move_cbk)
        self.radius = radius
        self.color = color

    def draw(self):
        draw_circle(self.pos, self.radius, self.color, filled=not self.is_clicked)

    def on_click(self, pos):
        clicked = False
        if glm.length2(pos - self.pos) < self.radius * self.radius:
            clicked = True
        super().on_click(clicked, pos)
        return clicked

class ClickableLine(Clickable):
    def __init__(self, A, B, color=Color.BLACK, on_click_cbk=None,
            on_release_cbk=None, on_move_cbk=None):
        super().__init__(A, on_click_cbk=on_click_cbk,
                on_release_cbk=on_release_cbk, on_move_cbk=on_move_cbk)
        self.B = Vec2(B)
        self.color = color

    def draw(self):
        draw_line(self.pos, self.B, self.color)

    def on_click(self, pos):
        clicked = False
        rad = 0.01
        Q = pos
        A = self.pos
        B = self.B
        I1, I2 = seg_circ_intersect(A, B, Q, rad)
        if I1 or I2:
            clicked = True
        super().on_click(clicked, pos)
        return clicked

    def on_move(self, pos):
        super().on_move(pos)
        if self.is_clicked:
            self.B = self.B + pos - state.clickable.old_pos

def _clickable_init():
    state.clickable = _dotdict({
        'elements': [],
        'old_pos': Vec2(0, 0)
    })

def _clickable_on_click(pos):
    elem = None
    for e in state.clickable.elements:
        if e.on_click(Vec2(screen2pos(pos))):
            elem = e
            # we can only click one element
            break
    if elem:
        state.clickable.elements.remove(elem)
        state.clickable.elements.insert(0, elem)

def _clickable_on_release(pos):
    for e in state.clickable.elements:
        e.on_release(Vec2(screen2pos(pos)))

def _clickable_on_move(pos):
    for e in state.clickable.elements:
        e.on_move(Vec2(screen2pos(pos)))
    state.clickable.old_pos = Vec2(screen2pos(pos))

def _clickable_on_draw():
    for e in state.clickable.elements[::-1]:
        e.draw()

def clickable_add(clickable_obj):
    state.clickable.elements.append(clickable_obj)
