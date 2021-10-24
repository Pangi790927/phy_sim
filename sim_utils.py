import glm
import pygame
import numpy as np
import ctypes

SIM_GEOMETRY_PER_BATCH = 65536

# sizeof(float) * (color + pos + normal + texcoords)
SIM_VERT_SIZE = 4 * (4 + 4 + 3 + 2)
SIM_TRIANGLE_SIZE = SIM_VERT_SIZE * 3
SIM_LINE_SIZE = SIM_VERT_SIZE * 2

class Color:
    BLACK = glm.vec4(  0,   0,   0, 255)
    RED =   glm.vec4(255,   0,   0, 255)
    GREEN = glm.vec4(  0, 255,   0, 255)
    BLUE =  glm.vec4(  0,   0, 255, 255)
    WHITE = glm.vec4(255, 255, 255, 255)

class Vert:
    def __init__(self, p, c=Color.BLACK, n=glm.vec3(), t=glm.vec2()):
        self.p = glm.vec4(p)
        self.c = glm.vec4(c) / 256
        self.n = glm.vec3(n)
        self.t = glm.vec2(t)

# In TriangleBatch objects we will add triangles and draw them later on loop
# update or on shader change
class MeshBatch:
    def __init__(self, shader, geometry_size, gl=None):
        if not gl:
            raise Exception("Can't use mesh batch without opengl")
        self.gl = gl

        self.vbo = gl.glGenBuffers(1)
        self.count = 0
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            SIM_GEOMETRY_PER_BATCH * geometry_size,
            None,
            gl.GL_DYNAMIC_DRAW
        )
        self.bind_shader(shader)

    def bind_shader(self, shader):
        gl = self.gl
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        self.shader = shader
        position = gl.glGetAttribLocation(shader, 'position')
        if position >= 0:
            gl.glVertexAttribPointer(position, 4, gl.GL_FLOAT, False,
                    SIM_VERT_SIZE, ctypes.c_void_p(0))
            gl.glEnableVertexAttribArray(position)

        color = gl.glGetAttribLocation(shader, 'color')
        if color >= 0:
            gl.glVertexAttribPointer(color, 4, gl.GL_FLOAT, False,
                    SIM_VERT_SIZE, ctypes.c_void_p(16))
            gl.glEnableVertexAttribArray(color)

        normal = gl.glGetAttribLocation(shader, 'normal')
        if normal >= 0:
            gl.glVertexAttribPointer(normal, 3, gl.GL_FLOAT, False,
                    SIM_VERT_SIZE, ctypes.c_void_p(32))
            gl.glEnableVertexAttribArray(normal)

        tex_uv = gl.glGetAttribLocation(shader, 'tex_uv')
        if tex_uv >= 0:
            gl.glVertexAttribPointer(tex_uv, 2, gl.GL_FLOAT, False,
                    SIM_VERT_SIZE, ctypes.c_void_p(44))
            gl.glEnableVertexAttribArray(tex_uv)

class TriangleBatch(MeshBatch):
    def __init__(self, shader, **kwargs):
        super().__init__(shader, SIM_TRIANGLE_SIZE, **kwargs)

    def add_triangle(self, vE: Vert, vF: Vert, vG: Vert):
        gl = self.gl
        if self.count == SIM_GEOMETRY_PER_BATCH:
            self.draw()

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        triangle = [
            vE.p.x, vE.p.y, vE.p.z, vE.p.w, vE.c.r, vE.c.g, vE.c.b, vE.c.a,
            vE.n.x, vE.n.y, vE.n.z, vE.t.x, vE.t.y,
            vF.p.x, vF.p.y, vF.p.z, vF.p.w, vF.c.r, vF.c.g, vF.c.b, vF.c.a,
            vF.n.x, vF.n.y, vF.n.z, vF.t.x, vF.t.y,
            vG.p.x, vG.p.y, vG.p.z, vG.p.w, vG.c.r, vG.c.g, vG.c.b, vG.c.a,
            vG.n.x, vG.n.y, vG.n.z, vG.t.x, vG.t.y
        ]

        triangle = np.array(triangle, dtype=np.float32)

        gl.glBufferSubData(
            gl.GL_ARRAY_BUFFER,
            SIM_TRIANGLE_SIZE * self.count,
            triangle.nbytes,
            triangle)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        self.count += 1

    def draw(self):
        if self.count > 0:
            gl = self.gl
            self.bind_shader(self.shader)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3 * self.count)
            self.count = 0

class LineBatch(MeshBatch):
    def __init__(self, shader, **kwargs):
        super().__init__(shader, SIM_LINE_SIZE, **kwargs)

    def add_line(self, vE: Vert, vF: Vert):
        gl = self.gl
        if self.count == SIM_GEOMETRY_PER_BATCH:
            self.draw()

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        line = [
            vE.p.x, vE.p.y, vE.p.z, vE.p.w, vE.c.r, vE.c.g, vE.c.b, vE.c.a,
            vE.n.x, vE.n.y, vE.n.z, vE.t.x, vE.t.y,
            vF.p.x, vF.p.y, vF.p.z, vF.p.w, vF.c.r, vF.c.g, vF.c.b, vF.c.a,
            vF.n.x, vF.n.y, vF.n.z, vF.t.x, vF.t.y
        ]

        line = np.array(line, dtype=np.float32)

        gl.glBufferSubData(
            gl.GL_ARRAY_BUFFER,
            SIM_LINE_SIZE * self.count,
            line.nbytes,
            line)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        self.count += 1

    def draw(self):
        if self.count > 0:
            gl = self.gl
            self.bind_shader(self.shader)
            gl.glDrawArrays(gl.GL_LINES, 0, 2 * self.count)
            self.count = 0

# font must be a monospace font, we don't support other types of fonts
class SimFont:
    def __init__(self, font_name, font_size):
        self.font_name = font_name
        self.font_size = font_size
        self.font = pygame.freetype.Font(font_name, font_size)

    def char_width_px(self):
        return self.font.get_rect(' ').width

    def char_height_px(self):
        return self.font.get_sized_height()

    def char_width(self):
        return px2dist(self.char_width_px())

    def char_height(self):
        return px2dist(self.char_height_px())
