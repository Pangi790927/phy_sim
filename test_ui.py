import sys
import sim
import ui
import time
import glm
import interactive
import shapes
import utils
import pygame.freetype

use_opengl = 'ogl' in sys.argv

Color = sim.Color
sim.init(width=800, height=800, scale=2, use_opengl=use_opengl)
s = sim.state.scale

fps = utils.FpsCounter()

text = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor 
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident,
sunt in culpa qui officia deserunt mollit anim id est laborum."""

def draw_axis():
    sim.draw_line([0, 0], [s, 0], Color.RED)
    sim.draw_line([0, 0], [0, s], Color.BLUE)
    sim.draw_line([0, 0], [0,-s], Color.GREEN)
    sim.draw_line([0, 0], [-s,0], Color.BLACK)

curr_color = Color.WHITE / 1.2
def on_click(*args):
    print("clicked btn")
    btn.shape.color = Color.WHITE / 2

def on_release(*args):
    print("released btn")
    btn.shape.color = curr_color

def on_hover(pos, opos, entered, exited):
    global curr_color
    if entered:
        curr_color = Color.WHITE / 1.6
    if exited:
        curr_color = Color.WHITE / 1.2
    if not btn.is_clicked:
        btn.shape.color = curr_color

btn = ui.Button("Click me!", [0, 0], [0.5, 0.5], Color.WHITE / 1.2, filled=True)
print(btn.shape.AA, btn.shape.AA)
btn.on_click = on_click
btn.on_release = on_release
btn.on_hover = on_hover

sim.interactive_add(btn)

def rot_text(text, pos, align):
    sim.draw_circle(pos, 0.005 * s, filled=True)
    rotated=True
    ui.TextLine(text, pos=pos, align=align, rotated=rotated).draw()

def draw_rotated_text():
    rot_text(text = "xlyt", pos=(s*1/4, -s*1/4), align=(ui.XLEFT,   ui.YTOP))
    rot_text(text = "xlyc", pos=(s*2/4, -s*1/4), align=(ui.XLEFT,   ui.YCENTER))
    rot_text(text = "xlyb", pos=(s*3/4, -s*1/4), align=(ui.XLEFT,   ui.YBOTTOM))
    rot_text(text = "xcyt", pos=(s*1/4, -s*2/4), align=(ui.XCENTER, ui.YTOP))
    rot_text(text = "xcyc", pos=(s*2/4, -s*2/4), align=(ui.XCENTER, ui.YCENTER))
    rot_text(text = "xcyb", pos=(s*3/4, -s*2/4), align=(ui.XCENTER, ui.YBOTTOM))
    rot_text(text = "xryt", pos=(s*1/4, -s*3/4), align=(ui.XRIGHT,  ui.YTOP))
    rot_text(text = "xryc", pos=(s*2/4, -s*3/4), align=(ui.XRIGHT,  ui.YCENTER))
    rot_text(text = "xryb", pos=(s*3/4, -s*3/4), align=(ui.XRIGHT,  ui.YBOTTOM))

def draw_fn():
    fps.update()

    draw_axis()
    tb = ui.TextBlock(text, pos=(-s+0.01, 0), limits_px=(400, 400))
    tb.draw()

    sim.draw_circle([1, 1], 0.3, filled=True)

    mouse_pos_px = sim.get_mouse_pos_px()
    mouse_pos = sim.get_mouse_pos()
    metadata = '\n'.join([
        "fps %d" % fps.get_fps(),
        "mouse_x_px %d, mouse_y_px %d" % (mouse_pos_px[0], mouse_pos_px[1]),
        "mouse_x %.3f, mouse_y %.3f" % (mouse_pos[0], mouse_pos[1]),
        "ana are mere",
        "inca o fraza",
        "Mp"
    ])
    tb = ui.TextBlock(metadata, pos=(-s, s-0.01),
            limits_px=(400, 400), xalign=ui.XCENTER)
    tb.draw()
    draw_rotated_text()

sim.loop(draw_fn=draw_fn)
