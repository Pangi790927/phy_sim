import pygame, sys
import numpy as np
import time
from pygame.locals import *

class Color:
    BLACK = (  0,   0,   0)
    RED =   (255,   0,   0)
    GREEN = (  0, 255,   0)
    BLUE =  (  0,   0, 255)
    WHITE = (255, 255, 255)

width = 800
height = 800
s = 10

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

def draw_axis():
    draw_line([0, 0], [s, 0], Color.RED)
    draw_line([0, 0], [0, s], Color.BLUE)
    draw_line([0, 0], [0,-s], Color.GREEN)
    draw_line([0, 0], [-s,0], Color.BLACK)

# will be called each frame, draw your stuff here
def draw_fn():
	draw_axis()
	t = time.time()
	draw_circle([np.cos(t), np.sin(t)], 0.1)

# Ignore bellow
# ==============================================================================

pygame.init()
if width < height:
    width = height
display = pygame.display.set_mode((width, height), 0, 32)

# transforms position from coord space to space coords
def pos2screen(pos):
    x = pos[0] / s
    y = pos[1] / s
    screen_x = (x + 1) * height / 2 + (width - height) / 2
    screen_y = (1 - y) * height / 2
    return (int(screen_x), int(screen_y))

def dist2screen(dist):
    return int(dist / s * height / 2)

def draw_line(posA, posB, color=Color.BLACK):
    posA = pos2screen(posA)
    posB = pos2screen(posB)
    pygame.draw.line(display, color, posA, posB)

def draw_dot(pos, color=Color.BLACK):
    pos = pos2screen(pos)
    display.set_at(pos, color)

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
    pygame.draw.rect(display, color,
            pygame.Rect(minx, miny, maxx - minx, maxy - miny), border)

def draw_circle(pos, rad, color=Color.BLACK, filled=False):
    pos = pos2screen(pos)
    rad = dist2screen(rad)
    border = 1
    if filled:
        border = 0
    pygame.draw.circle(display, color, pos, rad, border)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
    display.fill(Color.WHITE)
    draw_fn()
    pygame.display.update()

