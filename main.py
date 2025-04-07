import math
from graphics import * #very basic graphics API #NOTE: Remember to do "pip install graphics.py"
#graphics.py documentation: https://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf

import sys, os, pygame, re, random
import numpy as np
from copy import copy, deepcopy
from entity import Entity, Spawner

#GLOBALS
SCREEN_HEIGHT = 448 #These are just the Touhou numbers adapted directly
SCREEN_WIDTH = 384

def parse_input(Player):
    CMD_INPUT = input("ENTER COMMAND HERE: ")  # accept input until stop

    CMD_INPUT = CMD_INPUT.upper() #make inputs uppercase

    #create dictionary that returns parsed values of input
    dictionary = {"REWIND":False, "TICKS":None, "PLAYER_MOVEMENT":(0, 0)}

    #simulate player movement
    if CMD_INPUT == "UP":
        dictionary["PLAYER_MOVEMENT"] = ( 0, -1)
    if CMD_INPUT == "DOWN":
        dictionary["PLAYER_MOVEMENT"] = ( 0,  1)
    if CMD_INPUT == "LEFT":
        dictionary["PLAYER_MOVEMENT"] = (-1,  0)
    if CMD_INPUT == "RIGHT":
        dictionary["PLAYER_MOVEMENT"] = ( 1,  0)
    if CMD_INPUT == "UPLEFT":
        dictionary["PLAYER_MOVEMENT"] = (-1, -1)
    if CMD_INPUT == "UPRIGHT":
        dictionary["PLAYER_MOVEMENT"] = ( 1, -1)
    if CMD_INPUT == "DOWNLEFT":
        dictionary["PLAYER_MOVEMENT"] = (-1,  1)
    if CMD_INPUT == "DOWNRIGHT":
        dictionary["PLAYER_MOVEMENT"] = ( 1,  1)


    #Change ticks
    try: #FIXME: Change this
        val = int(CMD_INPUT)
        # TICKS = val
        dictionary["TICKS"] = val
        print("Set tick rate to =", val)
    except:
        pass
    
    #Rewind actions
    if CMD_INPUT == "REWIND":
        dictionary["REWIND"] = True
        Player.rewind()

    return dictionary

def graphics_init():
    window = GraphWin("Bullet-hell Simulation", SCREEN_WIDTH, SCREEN_HEIGHT)
    return window

def renderer_graphics(player, objects, window):
    #graphics.py based rendering
    #used for automatic testing
    #Draw the Entity
    player.draw_to(window)
    for object in objects:
        if type(object) is Entity:
            object.draw_to(window)
    pass

def pygame_init():
    #function for initializing pygame functionality

    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()
    
    return surface, clock

def renderer_pygame(surface, clock, player, objects):
    #pygame renderer
    #used for human input
    surface.fill((0,0,0,0)) #Clear screen each frame

    if type(player) is Entity:
        pygame.draw.rect(surface, player.pygame_color, player.pygame_rect)

    for object in objects:
        if type(object) is Entity:
            pygame.draw.rect(surface, object.pygame_color, object.pygame_rect)
    
    clock.tick(30) #30 FPS
    pygame.display.update()


def player_input():
    #manual control for game
    #used only in pygame rendering mode

    #NOTE: this return dictionary should be in the exact same format as the one in parse_input().
    dictionary = {"REWIND":False, "TICKS":None, "PLAYER_MOVEMENT":(0, 0)}

    x, y = 0, 0
    down = (0,0)
    up = (0,0)
    left = (0,0)
    right = (0,0)
    #FIXME: Input completely messed up. Need to fix this.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()   
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                x,y = (0,1)
            if event.key == pygame.K_a:
                pass
            if event.key == pygame.K_s:
                x,y = (0,-1)
            if event.key == pygame.K_d:
                pass
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_UP]:
        up = (0, -1)
    else:
        up = (0, 0)

    if keys[pygame.K_LEFT]:
        left = (-1, 0)
    else:
        left = (0, 0)
    
    if keys[pygame.K_DOWN]:
        down = (0,  1)
    else:
        down = (0, 0)

    if keys[pygame.K_RIGHT]:
        right = (1,  0)
    else:
        right = (0, 0)

    multiplier = 2
    if keys[pygame.K_LSHIFT]:
        multiplier = 1

    # print(up, left, right, down)
    dictionary["PLAYER_MOVEMENT"] = tuple(map(lambda i, j, k, l: (i+j+k+l)*multiplier, up, down, left, right))
    
    return dictionary

def cvoa_algo(player, objects):
    #Constrained Velocity Obstacle Algorithm (misnomer, but whatever)
    #To be used for micro-dodging
    pass

def clustering(player, objects):
    #Cluster algorithm to help with macrododging
    pass

def lvl_generator():
    #Level generation component
    pass

#Simulate movement for all objects + player in game
#CHECK: If rewind functionality properly applied
def movement(inputs, player, objects):
    #inputs should be a dictionary value, returned from parse_input()
    #move player
    if type(player) is Entity: #do player movement stuff
        if inputs["REWIND"]: #rewind functionality
            player.rewind()
        else:
            x, y = inputs["PLAYER_MOVEMENT"]
            player.movement(x, y)
    #move all other objects
    for object in objects:
        if type(object) is Entity: #bullets and misc
            if object.name == "player": #skip player
                continue
            else: #check everything else
                if inputs["REWIND"]:
                    object.rewind()
                else:
                    object.movement(object.velocity_x, object.velocity_y)
        elif type(object) is Spawner: #spawners
            if inputs["REWIND"]:
                object.update(rewind=True)
            else:
                object.update()

def game_collision(player, objects):
    #collision detection for objects in the game
    for object in objects:
        if type(object) is Entity and object.name != "player":
            object.aabb(player)
        elif type(object) is Spawner:
            object.spawner_detect_collision(player)


def main():

    MODE = "INPUT" #"GRAPHICS"

    #initialize render(s)
    if MODE == "GRAPHICS":
        window = graphics_init() #graphics.py renderer
    if MODE == "INPUT":
        surface, clock = pygame_init() #pygame renderer

    #Make some method of visual output (not sure on this...)
    CMD_INPUT = ""

    # Example of how to use the Spawner to spawn circular bullets
    player_x = SCREEN_WIDTH / 2
    player_y = SCREEN_HEIGHT / 2
    # bullet_spawner = Spawner(player_x, player_y)
    bullet_spawner = Spawner(0, 0, 16, 16)

    # Example commands
    # bullet_spawner.spawn_circular_bullets(8, 1)  # Spawn 8 bullets at the spawner position, with speed of 2 units
    # bullet_spawner.update()  # Update all bullets' positions

    #game_objects should contain all bullets, spawners, player.
    game_objects = [] #checking all game objects
    game_objects.extend(bullet_spawner.spawn_circular_bullets(8, 1))

    Player = Entity("player", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 16, 16)

    game_objects.append(Player)
    game_objects.append(bullet_spawner)

    TICKS = 1

    while CMD_INPUT != "END": #game loop
        #Renderer 
        
        if MODE == "GRAPHICS":
            renderer_graphics(Player, game_objects, window)
        if MODE == "INPUT":
            renderer_pygame(surface, clock, Player, game_objects)
        
        if MODE == "GRAPHICS":
            command_dict = parse_input(Player)
            if command_dict["TICKS"] != None:
                TICKS = command_dict["TICKS"]
                continue #restart with new tick rate
        if MODE == "INPUT":
            command_dict = player_input()

        # print(command_dict)

        #for tick in ticks: #simulate command for certain amount of ticks
        for tick in range(TICKS):
            movement(command_dict, Player, game_objects)
            #Simluate collision
            game_collision(Player, game_objects)

        # renderer_pygame(surface, clock, Player, game_objects)

#just organizational things.
if __name__ == '__main__':
    main()