import abc
import pygame, sys
import glm
import numpy as np
from pygame.locals import *
import pygame.freetype
import os

SIM_PKG_DIR = os.path.dirname(__file__)
sys.path.append(SIM_PKG_DIR)

import sim_utils
import intersect

# Defines:
# ==============================================================================

SIM_FONT_NAME = os.path.join(SIM_PKG_DIR, "font/static/FiraCode-Regular.ttf")
SIM_FONT_SIZE = 16

DEFAULT_VERTEX_SHADER = """
#version 330

in vec4 position;
in vec4 color;
in vec3 normal;
in vec2 tex_uv;

out vec4 vert_color;

void main() {
    gl_Position = position;
    vert_color = color;
}
"""

DEFAULT_FRAGMENT_SHADER = """
#version 330

in vec4 vert_color;
out vec4 frag_color;

void main() {
    frag_color = vert_color;
}
"""

# Utils:
# ==============================================================================

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def _none_fn(*args, **kwargs):
    pass

Vec2 = glm.vec2
Vec3 = glm.vec3
Vec4 = glm.vec4

Vert = sim_utils.Vert
Color = sim_utils.Color

SimFont = sim_utils.SimFont

def create_shader(vs_data, fs_data):
    gl = state.gl
    if not gl:
        raise Exception("Can't use this function without opengl")
    from OpenGL.GL import shaders
    import OpenGL
    try: 
        vs = shaders.compileShader(vs_data, gl.GL_VERTEX_SHADER)
        fs = shaders.compileShader(fs_data, gl.GL_FRAGMENT_SHADER)
    except OpenGL.GL.shaders.ShaderCompilationError as e:
        # TODO: nicer error somehow
        raise e
    return shaders.compileProgram(vs, fs)

# Screen and state:
# ==============================================================================

state = None
def init(width, height, scale=1, use_opengl=False, vsync=None):
    global state
    state = dotdict({
        'width':             width,
        'height':            height,
        'scale':             scale,
        'surface':           None,
        'alive':             True,
        'interactive':       None,
        'font':              None,
        'fonts':             {},
        'mouse_pos':         (0, 0),
        'prev_mouse_pos':    (0, 0),
        'gl':                None,
        'gl_triangle_batch': None,
        'gl_line_batch':     None,
        'gl_curr_shader':    None,
        'gl_def_shader':     None
    })

    pygame.init()
    state.font = load_font_size(SIM_FONT_SIZE)
    if state.width < state.height:
        print("WARNING: width can't be smaller than height, will clip height")
        state.height = state.width
    opt_args = {}
    if vsync is not None:
        opt_args["vsync"] = vsync
    if use_opengl:
        import OpenGL.GL as gl
        state.gl = gl
        state.surface = pygame.display.set_mode(
            (state.width, state.height),
            DOUBLEBUF | OPENGL,
            **opt_args
        )
        state.gl_def_shader = create_shader(
                DEFAULT_VERTEX_SHADER, DEFAULT_FRAGMENT_SHADER)
        gl.glUseProgram(state.gl_def_shader)
        state.gl_curr_shader = state.gl_def_shader
        state.gl_line_batch = sim_utils.LineBatch(state.gl_curr_shader, gl=gl)
        state.gl_triangle_batch = sim_utils.TriangleBatch(
                state.gl_curr_shader, gl=gl)
        gl.glClearColor(1, 1, 1, 0)
        gl.glDisable(gl.GL_CULL_FACE);
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA) 
    else:
        state.surface = pygame.display.set_mode(
                (state.width, state.height), 0, 32, **opt_args)
    _interactive_init()

def use_shader(new_shader):
    if not state.gl:
        raise Exception("can't change shaders if you don't use opengl")
    state.gl_line_batch.draw()
    state.gl_triangle_batch.draw()

    state.gl_line_batch.bind_shader(new_shader)
    state.gl_triangle_batch.bind_shader(new_shader)

    state.gl_curr_shader = new_shader
    state.gl.glUseProgram(new_shader)

def load_font_size(size):
    if size in state.fonts:
        return state.fonts[size]
    else:
        state.fonts[size] = SimFont(SIM_FONT_NAME, size)
        return state.fonts[size]

def _intern_exit(exit_fn=_none_fn):
    global state
    pygame.quit()
    exit_fn()
    state.alive = False

def draw_batch():
    gl = state.gl
    if gl:
        state.gl_line_batch.draw()
        state.gl_triangle_batch.draw()

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
                state.prev_mouse_pos = state.mouse_pos
                state.mouse_pos = pos
                _interactive_on_move(pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                _interactive_on_click(pos)

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                _interactive_on_release(pos)

            event_fn(event)

        if not state.alive:
            break
        gl = state.gl
        if gl:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT|gl.GL_DEPTH_BUFFER_BIT)
        else:
            state.surface.fill(Color.WHITE)
        _interactive_on_draw()
        draw_batch()
        draw_fn()
        draw_batch()
        if gl:
            pygame.display.flip()
        else:
            pygame.display.update()

# Input functions
# ==============================================================================

def get_mouse_pos_px():
    return state.mouse_pos

def get_prev_mouse_pos_px():
    return state.prev_mouse_pos

def get_mouse_pos():
    return Vec2(screen2pos(get_mouse_pos_px()))

def get_prev_mouse_pos():
    return Vec2(screen2pos(get_prev_mouse_pos_px()))

# Coord functions:
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

def dist2px(dist):
    return int(dist / state.scale * state.height / 2)

def px2dist(dist):
    return dist * state.scale / state.height * 2

# Drawing primitives:
# ==============================================================================

def draw_line(posA, posB, color=Color.BLACK):
    if state.gl:
        posA = Vec4(posA[0], posA[1], 0, state.scale) / state.scale
        posB = Vec4(posB[0], posB[1], 0, state.scale) / state.scale
        state.gl_line_batch.add_line(
                Vert(posA, color), Vert(posB, color))
    else:
        posA = pos2screen(posA)
        posB = pos2screen(posB)
        pygame.draw.line(state.surface, color, posA, posB)

def draw_dot(pos, color=Color.BLACK):
    dot_size = state.scale / 4
    up = vec2(0, dot_size)
    down = vec2(0, -dot_size)
    left = vec2(-dot_size, 0)
    right = vec2(dot_size, 0)
    pos = Vec2(pos)
    draw_line(pos, pos + up, color)
    draw_line(pos, pos + down, color)
    draw_line(pos, pos + left, color)
    draw_line(pos, pos + right, color)

def draw_surf(pos_px, surface):
    draw_batch()
    if state.gl:
        gl = state.gl
        old_prog = state.gl_curr_shader
        # it's a pain to do anything in the new opengl so we will draw text
        # with the old pipeline
        gl.glUseProgram(0)
        data = pygame.image.tostring(surface, "RGBA", True)
        pos = (pos_px[0], pos_px[1] + surface.get_height())
        pos = Vec2(screen2pos(pos)) / state.scale
        was_blend_enabled = gl.glIsEnabled(gl.GL_BLEND)
        gl.glEnable(gl.GL_BLEND)
        gl.glRasterPos3d(pos[0], pos[1], 0);
        gl.glDrawPixels(surface.get_width(), surface.get_height(),
                gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data)
        if old_prog != 0:
            gl.glUseProgram(old_prog)
        if not was_blend_enabled:
            gl.glDisable(gl.GL_BLEND)
    else:
        state.surface.blit(surface, pos_px)

def draw_aabb(posA, posB, color=Color.BLACK, filled=False):
    if state.gl:
        minx = min(posA[0], posB[0])
        miny = min(posA[1], posB[1])
        maxx = max(posA[0], posB[0])
        maxy = max(posA[1], posB[1])
        AA = (minx, miny)
        AB = (maxx, miny)
        BB = (maxx, maxy)
        BA = (minx, maxy)
        if not filled:
            draw_line(AA, AB, color)
            draw_line(AB, BB, color)
            draw_line(BB, BA, color)
            draw_line(BA, AA, color)
        else:
            draw_triangle(AA, AB, BB, color, True)
            draw_triangle(BB, BA, AA, color, True)
    else:
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
    if state.gl:
        pos = glm.vec2(pos)
        n = 30
        a_inc = 2 * np.pi / n
        if filled:
            for i in range(n):
                a = a_inc * i
                v1 = pos + glm.vec2(np.cos(a), np.sin(a)) * rad
                v2 = pos + glm.vec2(np.cos(a + a_inc), np.sin(a + a_inc)) * rad
                draw_triangle(pos, v1, v2, color, True)
        else:
            for i in range(n):
                a = a_inc * i
                v1 = pos + glm.vec2(np.cos(a), np.sin(a)) * rad
                v2 = pos + glm.vec2(np.cos(a + a_inc), np.sin(a + a_inc)) * rad
                draw_line(v1, v2, color)
    else:
        pos = pos2screen(pos)
        rad = dist2px(rad)
        border = 1
        if filled:
            border = 0
        pygame.draw.circle(state.surface, color, pos, rad, border)

def draw_triangle(posA, posB, posC, color=Color.BLACK, filled=False):
    if state.gl:
        if filled:
            posA = Vec4(posA[0], posA[1], 0, state.scale) / state.scale
            posB = Vec4(posB[0], posB[1], 0, state.scale) / state.scale
            posC = Vec4(posC[0], posC[1], 0, state.scale) / state.scale
            state.gl_triangle_batch.add_triangle(
                    Vert(posA, color), Vert(posB, color), Vert(posC, color))
        else:
            draw_line(posA, posB, color)
            draw_line(posB, posC, color)
            draw_line(posC, posA, color)
    else:
        posA = pos2screen(posA)
        posB = pos2screen(posB)
        posC = pos2screen(posC)
        border = 1
        if filled:
            border = 0
        pygame.draw.polygon(state.surface, color, [posA, posB, posC], border)

def draw_quad(posA, posB, posC, posD, color=Color.BLACK, filled=False):
    if state.gl:
        if not filled:
            draw_line(posA, posB, color)
            draw_line(posB, posC, color)
            draw_line(posC, posD, color)
            draw_line(posD, posA, color)
        else:
            draw_triangle(posA, posB, posC, color, True)
            draw_triangle(posC, posD, posA, color, True)
    else:
        posA = pos2screen(posA)
        posB = pos2screen(posB)
        posC = pos2screen(posC)
        posD = pos2screen(posD)
        border = 1
        if filled:
            border = 0
        pygame.draw.polygon(state.surface, color,
                [posA, posB, posC, posD], border)

# Interactive objects:
# ==============================================================================

def _interactive_init():
    state.interactive = dotdict({
        'elements': [],
        'old_pos': Vec2(0, 0)
    })

def _interactive_on_click(pos):
    pos = Vec2(screen2pos(pos))
    elem = None
    for e in state.interactive.elements:
        if e.on_click_fn(pos, state.interactive.old_pos):
            elem = e
            # we can only click one element
            break
    if elem:
        state.interactive.elements.remove(elem)
        state.interactive.elements.insert(0, elem)
    state.interactive.old_pos = pos

def _interactive_on_release(pos):
    pos = Vec2(screen2pos(pos))
    for e in state.interactive.elements:
        e.on_release_fn(pos, state.interactive.old_pos)
    state.interactive.old_pos = pos

def _interactive_on_move(pos):
    pos = Vec2(screen2pos(pos))
    for e in state.interactive.elements:
        e.on_move_fn(pos, state.interactive.old_pos)
    state.interactive.old_pos = pos

def _interactive_on_draw():
    for e in state.interactive.elements[::-1]:
        e.draw()

def interactive_add(interactive_obj):
    state.interactive.elements.append(interactive_obj)
