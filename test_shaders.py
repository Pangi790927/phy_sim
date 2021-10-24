import sys
import sim
import ui
import time
import glm
import interactive
import shapes
import utils
import pygame.freetype

Color = sim.Color
sim.init(width=800, height=800, scale=10, use_opengl=True)
s = sim.state.scale

VERTEX_SHADER = """
#version 330

in vec4 position;
in vec4 color;
in vec3 normal;
in vec2 tex_uv;

out vec4 vert_color;
out vec4 vert_pos;

void main() {
    gl_Position = position;
    vert_color = color;
    vert_pos = position;
}
"""

FRAGMENT_SHADER = """
#version 330

in vec4 vert_pos;
in vec4 vert_color;
out vec4 frag_color;

uniform float scale;
uniform vec2 mouse_pos;

void main() {
    float x = vert_pos.x * scale;
    float y = vert_pos.y * scale;
    vec2 mdir = vec2(x, y) - mouse_pos;
    vec2 mdir_norm = normalize(mdir);
    float grid_size = 2;
    float nx = round(x * grid_size) / grid_size;
    float ny = round(y * grid_size) / grid_size;
    vec3 dir = vec3(nx, ny, 0) - vec3(x, y, 0);
    vec3 dst_dir = vec3(mdir_norm.x, mdir_norm.y, 0);
    float l = length(dir);
    bool done = false;
    do {
        if (l < 1. / grid_size * 0.1) {
            frag_color = vec4(1, 0, 0, 1);
            break;
        }

        if (l < 1. / grid_size * 0.8) {
            if (dot(normalize(dir), normalize(dst_dir)) > 0.99) {
                frag_color = vec4(0, 0, 1, 1);
                break;
            }
        }

        frag_color = vec4(0, 0, 1, 1) / length(mdir);
    } while (false);
}
"""

gl = sim.state.gl

test_shader = sim.create_shader(VERTEX_SHADER, FRAGMENT_SHADER)
fps = utils.FpsCounter()

def draw_axis():
    fps.update()
    sim.draw_line([0, 0], [s, 0], Color.RED)
    sim.draw_line([0, 0], [0, s], Color.BLUE)
    sim.draw_line([0, 0], [0,-s], Color.GREEN)
    sim.draw_line([0, 0], [-s,0], Color.BLACK)

def set_uniform(shader, fn, name, *vals):
    uniform_loc = gl.glGetUniformLocation(shader, name)
    fn(uniform_loc, *vals)

def draw_fn():
    draw_axis()
    sim.use_shader(test_shader)
    set_uniform(test_shader, gl.glUniform1f, 'scale', s)
    mp = sim.get_mouse_pos()
    set_uniform(test_shader, gl.glUniform2f, 'mouse_pos', mp.x, mp.y)
    sim.draw_aabb([-s, -s], [s, s], Color.WHITE, filled=True)

sim.loop(draw_fn=draw_fn)
exit(0)


# WIP

# https://github.com/Rabbid76/graphics-snippets/blob/master/example/python/dsa_spirv_cube/example_python_dsa_spirv.md

import pygame as pg
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from pyshader import python2shader, vec3, vec4, mat4

import numpy as np

@python2shader
def vertex_shader(
    vertex_pos=("input", 0, vec3),
    transform=("uniform", (0, 0), mat4),
    out_pos=("output", "Position", vec4),
):
    out_pos = transform * vec4(vertex_pos, 1.0)

@python2shader
def fragment_shader_flat(
    color=("uniform", (0, 1), vec3), out_color=("output", 0, vec4),
):
    out_color = vec4(0, 1, 0, 1.0)  # noqa

cubeVertices = ((1,1,1),(1,1,-1),(1,-1,-1),(1,-1,1),(-1,1,1),(-1,-1,-1),(-1,-1,1),(-1,1,-1))
cubeEdges = ((0,1),(0,3),(0,4),(1,2),(1,7),(2,5),(2,3),(3,6),(4,6),(4,7),(5,6),(5,7))
cubeQuads = ((0,3,6,4),(2,5,6,3),(1,2,5,7),(1,0,4,7),(7,4,6,5),(2,3,0,1))

def wireCube():
    glBegin(GL_LINES)
    for cubeEdge in cubeEdges:
        for cubeVertex in cubeEdge:
            glVertex3fv(cubeVertices[cubeVertex])
    glEnd()

def solidCube():
    glBegin(GL_QUADS)
    for cubeQuad in cubeQuads:
        for cubeVertex in cubeQuad:
            glVertex3fv(cubeVertices[cubeVertex])
    glEnd()

def create_shader(shader_code, shader_type):
    if not sim.gl:
        raise Exception("Can't use this function without opengl")
    sh_code = shader_code.to_spirv()
    
    sh_obj = glCreateShader(shader_type)
    sho = np.array([sh_obj], dtype=np.uint32)
    glShaderBinary(1, sho, GL_SHADER_BINARY_FORMAT_SPIR_V, sh_code, len(sh_code))
    glSpecializeShader(sh_obj, 'main', 0, None, None)

    result = glGetShaderiv(sh_obj, GL_COMPILE_STATUS)
    if not result:
        print(glGetShaderInfoLog(sh_obj))
    return sh_obj

def create_program(sh_objects):
    program = glCreateProgram()
    for sh_obj in sh_objects:
        glAttachShader(program, sh_obj)

    # programs has to be declare separable for the use
    # with program pipeline - this is crucial!
    glProgramParameteri(program, GL_PROGRAM_SEPARABLE, GL_TRUE)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        print('link error:')
        print(glGetProgramInfoLog(program))
    for sh_obj in sh_objects:
        glDeleteShader(sh_obj)
    return program


def main():
    pg.init()
    display = (800, 800)
    surface = pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    vs = create_shader(vertex_shader, GL_VERTEX_SHADER)
    fs = create_shader(fragment_shader_flat, GL_FRAGMENT_SHADER)
    prog = create_program([vs, fs])

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    _vbo = OpenGL.arrays.vbo.VBO(
        np.array([
            [  0, 1, 0 ],
            [ -1,-1, 0 ],
            [  1,-1, 0 ],
            [  2,-1, 0 ],
            [  4,-1, 0 ],
            [  4, 1, 0 ],
            [  2,-1, 0 ],
            [  4, 1, 0 ],
            [  2, 1, 0 ],
        ],'f')
    )

    glUseProgram(prog)
    tr_loc = glGetUniformLocation(prog, 'transform')
    print(tr_loc)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        glRotatef(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        _vbo.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointerf(_vbo)
        glDrawArrays(GL_TRIANGLES, 0, 9)
        _vbo.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        # solidCube()
        # wireCube()
        pg.display.flip()
        # pg.time.wait(10)

if __name__ == "__main__":
    main()