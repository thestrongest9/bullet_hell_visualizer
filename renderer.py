import math
from graphics import *  # very basic graphics API #NOTE: Remember to do "pip install graphics.py"
# graphics.py documentation: https://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf

import sys, os, pygame, re, random
import numpy as np
from copy import copy, deepcopy

from entity import Entity, Spawner

def graphics_init(SCREEN_WIDTH, SCREEN_HEIGHT):
    window = GraphWin("Bullet-hell Simulation", SCREEN_WIDTH, SCREEN_HEIGHT)
    return window


def renderer_graphics(player, objects, window):
    # graphics.py based rendering
    # used for automatic testing
    # Draw the Entity
    player.draw_to(window)
    for object in objects:
        if type(object) is Entity:
            object.draw_to(window)
    pass


def pygame_init(SCREEN_WIDTH, SCREEN_HEIGHT):
    # function for initializing pygame functionality

    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()

    return surface, clock


def renderer_pygame(surface, clock, player, objects):
    # pygame renderer
    # used for human input
    surface.fill((0, 0, 0, 0))  # Clear screen each frame

    if type(player) is Entity:
        pygame.draw.rect(surface, player.pygame_color, player.pygame_rect)

    for object in objects:
        if type(object) is Entity:
            pygame.draw.rect(surface, object.pygame_color, object.pygame_rect)

    clock.tick(30)  # 30 FPS
    pygame.display.update()