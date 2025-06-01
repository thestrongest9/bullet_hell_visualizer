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


def renderer_graphics(player, objects, window, helpers=[]):
    # graphics.py based rendering
    # used for automatic testing
    # Draw the Entity
    player.draw_to(window)
    for object in objects:
        if type(object) is Entity:
            object.draw_to(window)
    
    for helper in helpers:
        helper.draw_to(window)


def pygame_init(SCREEN_WIDTH, SCREEN_HEIGHT):
    # function for initializing pygame functionality

    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()

    return surface, clock

background_surface = None
draw_surface = None

def renderer_pygame(surface, clock, players, objects, helpers=[]):
    # pygame renderer
    # used for human input
    global background_surface
    global draw_surface
    if background_surface == None and draw_surface == None:
        background_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
        # draw_surface = pygame.Surface((800, 600))
    
    background_surface.fill(pygame.Color(255, 255, 255, 0))
    # draw_surface.fill(pygame.Color('#000000'))
    surface.fill(pygame.Color('#000000'))

    for player in players:
        if type(player) is Entity:
            pygame.draw.rect(surface, player.pygame_color, player.pygame_rect)

    for object in objects:
        if type(object) is Entity:
            pygame.draw.rect(surface, object.pygame_color, object.pygame_rect)

    for helper in helpers:
        # print(helper.pygame_color)
        pygame.draw.rect(background_surface, helper.pygame_color, helper.pygame_rect)

    clock.tick(30)  # 30 FPS
    
    # surface.blit(background_surface, (0, 0))
    # surface.blit(draw_surface, (0, 0))
    surface.blit(background_surface, (0, 0))


    pygame.display.update()