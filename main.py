import math
from graphics import *  # very basic graphics API #NOTE: Remember to do "pip install graphics.py"
# graphics.py documentation: https://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf

import sys, os, pygame, re, random
import numpy as np
from copy import copy, deepcopy

from entity import Entity, Spawner
from renderer import graphics_init, renderer_graphics, pygame_init, renderer_pygame

# GLOBALS
SCREEN_HEIGHT = 448  # These are just the Touhou numbers adapted directly
SCREEN_WIDTH = 384


def parse_input(Player):
    CMD_INPUT = input("ENTER COMMAND HERE: ")  # accept input until stop

    CMD_INPUT = CMD_INPUT.upper()  # make inputs uppercase

    # create dictionary that returns parsed values of input
    dictionary = {"REWIND": False, "TICKS": None, "PLAYER_MOVEMENT": (0, 0)}

    # simulate player movement
    if CMD_INPUT == "UP":
        dictionary["PLAYER_MOVEMENT"] = (0, -1)
    if CMD_INPUT == "DOWN":
        dictionary["PLAYER_MOVEMENT"] = (0, 1)
    if CMD_INPUT == "LEFT":
        dictionary["PLAYER_MOVEMENT"] = (-1, 0)
    if CMD_INPUT == "RIGHT":
        dictionary["PLAYER_MOVEMENT"] = (1, 0)
    if CMD_INPUT == "UPLEFT":
        dictionary["PLAYER_MOVEMENT"] = (-1, -1)
    if CMD_INPUT == "UPRIGHT":
        dictionary["PLAYER_MOVEMENT"] = (1, -1)
    if CMD_INPUT == "DOWNLEFT":
        dictionary["PLAYER_MOVEMENT"] = (-1, 1)
    if CMD_INPUT == "DOWNRIGHT":
        dictionary["PLAYER_MOVEMENT"] = (1, 1)

    # Change ticks
    try:  # FIXME: Change this
        val = int(CMD_INPUT)
        # TICKS = val
        dictionary["TICKS"] = val
        print("Set tick rate to =", val)
    except:
        pass

    # Rewind actions
    if CMD_INPUT == "REWIND":
        dictionary["REWIND"] = True
        Player.rewind()

    return dictionary


def player_input():
    # manual control for game
    # used only in pygame rendering mode

    # NOTE: this return dictionary should be in the exact same format as the one in parse_input().
    dictionary = {"REWIND": False, "TICKS": None, "PLAYER_MOVEMENT": (0, 0)}

    x, y = 0, 0
    down = (0, 0)
    up = (0, 0)
    left = (0, 0)
    right = (0, 0)
    # FIXME: Input completely messed up. Need to fix this.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                x, y = (0, 1)
            if event.key == pygame.K_a:
                pass
            if event.key == pygame.K_s:
                x, y = (0, -1)
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
        down = (0, 1)
    else:
        down = (0, 0)

    if keys[pygame.K_RIGHT]:
        right = (1, 0)
    else:
        right = (0, 0)

    multiplier = 2
    if keys[pygame.K_LSHIFT]:
        multiplier = 1

    # print(up, left, right, down)
    dictionary["PLAYER_MOVEMENT"] = tuple(
        map(lambda i, j, k, l: (i + j + k + l) * multiplier, up, down, left, right)
    )

    return dictionary


def cvoa_algo(player, objects):
    # Constrained Velocity Obstacle Algorithm (misnomer, but whatever)
    # To be used for micro-dodging

    #these possible velocities should take into account
    #player can move in 8 directions
    #FIXME: player can increase or decrease speed (pressing shift, x2)
    #player can stand still (do nothing)
    multiplier = 2
    #FIXME: Need to have (0, 0) option at top. or else starts moving. Need to fix somehow.
    possible_velocities = [
        ( 0 * multiplier,  0 * multiplier), #stand still
        ( 0 * multiplier, -1 * multiplier), #up
        (-1 * multiplier, -1 * multiplier), #upleft
        ( 1 * multiplier, -1 * multiplier), #upright
        ( 0 * multiplier,  1 * multiplier), #down
        (-1 * multiplier,  1 * multiplier), #downleft
        ( 1 * multiplier,  1 * multiplier), #downright
        (-1 * multiplier,  0 * multiplier), #left
        ( 1 * multiplier,  0 * multiplier), #right
        # ( 0 * multiplier,  0 * multiplier), #stand still
        #Without multiplier
        ( 0, -1), #up
        (-1, -1), #upleft
        ( 1, -1), #upright
        ( 0,  1), #down
        (-1,  1), #downleft
        ( 1,  1), #downright
        (-1,  0), #left
        ( 1,  0), #right
    ]
    
    #create a dictionary of smallest distance direction needs to go to collide with something
    dir_collision = dict()
    for each in possible_velocities:
        dir_collision[each] = float("inf")
    
    #somehow also need to choose "best available" if no good decisions are available
    # safe_velocities = possible_velocities.copy()
    max_t_velocity = possible_velocities[random.randint(0, len(possible_velocities)-1)]
    
    CHECK_FRAMES = 20 #amount of frames to check for collision

    #remove any velocity that would cause collision
    for ob in objects:
        if type(ob) is Entity:
            if ob.name != "player":
                #FIXME: When working on frame time divided version, need to set distance to very high number (need to take into account all bullets)
                if True:#ob.get_distance(player) <= 128.0: #only consider obstacles close enough
                # if ob.get_distance(player) <= 256:#128.0: #only consider obstacles close enough
                    for v in possible_velocities:
                        #get how many frames it is safe to move in direction (velocity) v.
                        # no_collision_frames = ob.check_steps_ahead(CHECK_FRAMES, player, v)
                        no_collision_frames = player.check_steps_ahead(CHECK_FRAMES, ob, v)
                        print("num of frames", no_collision_frames)
                        if dir_collision[v] > no_collision_frames: #get the minimum amount of frames for that direction, based on collision detection with the obstacle
                            dir_collision[v] = no_collision_frames

    max_frames = 0

    print("GREATEST", dir_collision)
    # safe_velocities = {}

    #choose from some safe velocities
    safe_velocities = {}
    GREATEST_POSSIBLE_FRAMES = None
    dist = float("inf")
    for direction, frames in dir_collision.items():
        if frames not in safe_velocities:
            safe_velocities[frames] = [direction]
        else:
            safe_velocities[frames].append(direction)
        
        #check if greatest number of frames possible from current set of directions
        if GREATEST_POSSIBLE_FRAMES == None:
            GREATEST_POSSIBLE_FRAMES = frames
        else:
            if frames > GREATEST_POSSIBLE_FRAMES:
                GREATEST_POSSIBLE_FRAMES = frames

    # print("GREATEST", dir_collision)
    if GREATEST_POSSIBLE_FRAMES != None:
        # print(len(safe_velocities))
        # max_t_velocity = safe_velocities[random.randint(0, len(safe_velocities)-1)]

        # #choose closest to center
        # for dir in safe_velocities[GREATEST_POSSIBLE_FRAMES]:
        #     dir_x, dir_y = dir
        #     #manhattan distance
        #     # y_axis * 2 => to emphasize y-axis movement more over x, otherwise when same good move appears, gets stuck beneath bullet and collides at bottom of screen.
        #     temp = abs(player.rect.x + dir_x - 320) + abs(player.rect.y + dir_y - 240) * 2 
        #     if temp <= dist:
        #         max_t_velocity = dir
        #         dist = temp
        
        #pick randomly
        max_t_velocity = safe_velocities[GREATEST_POSSIBLE_FRAMES][random.randint(0, len(safe_velocities[GREATEST_POSSIBLE_FRAMES])-1)]
    
    max_frames = dir_collision[max_t_velocity]

    # x, y = max_t_velocity #FIXME: Better way to do this?
    # print(max_t_velocity)

    if max_frames > CHECK_FRAMES: #this means that the max_Frames = infinity
        max_frames = 0
    # else:
    #     max_frames = GREATEST_POSSIBLE_FRAMES

    # return (x, y, max_frames) #return x, y, and frame count (frame count so that player AI can switch to different velocity after current one is no longer safe)

    dictionary = {"REWIND": False, "TICKS": None, "PLAYER_MOVEMENT": max_t_velocity, "MAX_FRAMES": max_frames}
    return dictionary



def clustering(player, objects):
    # Cluster algorithm to help with macrododging
    pass


def lvl_generator():
    # Level generation component
    pass


# Simulate movement for all objects + player in game
# CHECK: If rewind functionality properly applied
def movement(inputs, player, objects):
    # inputs should be a dictionary value, returned from parse_input()
    # move player
    if type(player) is Entity:  # do player movement stuff
        if inputs["REWIND"]:  # rewind functionality
            player.rewind()
        else:
            x, y = inputs["PLAYER_MOVEMENT"]
            player.movement(x, y)
    # move all other objects
    for object in objects:
        if type(object) is Entity:  # bullets and misc
            if object.name == "player":  # skip player
                continue
            else:  # check everything else
                if inputs["REWIND"]:
                    object.rewind()
                else:
                    object.movement(object.velocity_x, object.velocity_y)
        elif type(object) is Spawner:  # spawners
            if inputs["REWIND"]:
                object.update(rewind=True)
            else:
                object.update()


def game_collision(player, objects):
    # collision detection for objects in the game
    for object in objects:
        if type(object) is Entity and object.name != "player":
            object.aabb(player)
        elif type(object) is Spawner:
            object.spawner_detect_collision(player)


def main():
    MODE = "INPUT"  # "GRAPHICS"

    # initialize render(s)
    if MODE == "GRAPHICS":
        window = graphics_init()  # graphics.py renderer
    if MODE == "INPUT":
        surface, clock = pygame_init(SCREEN_WIDTH, SCREEN_HEIGHT)  # pygame renderer

    # Make some method of visual output (not sure on this...)
    CMD_INPUT = ""

    # Example of how to use the Spawner to spawn circular bullets
    player_x = SCREEN_WIDTH / 2
    player_y = SCREEN_HEIGHT / 2
    # bullet_spawner = Spawner(player_x, player_y)
    bullet_spawner = Spawner(0, 0, 16, 16)

    # Example commands
    # bullet_spawner.spawn_circular_bullets(8, 1)  # Spawn 8 bullets at the spawner position, with speed of 2 units
    # bullet_spawner.update()  # Update all bullets' positions

    # game_objects should contain all bullets, spawners, player.
    game_objects = []  # checking all game objects
    game_objects.extend(bullet_spawner.spawn_circular_bullets(8, 1))

    Player = Entity("player", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 16, 16)

    game_objects.append(Player)
    game_objects.append(bullet_spawner)

    TICKS = 1

    CVOA_TICKS = -1

    command_dict = {}

    while CMD_INPUT != "END":  # game loop
        # Renderer

        if MODE == "GRAPHICS":
            renderer_graphics(Player, game_objects, window)
        if MODE == "INPUT":
            renderer_pygame(surface, clock, Player, game_objects)

        if MODE == "GRAPHICS":
            command_dict = parse_input(Player)
            if command_dict["TICKS"] != None:
                TICKS = command_dict["TICKS"]
                continue  # restart with new tick rate
        if MODE == "INPUT":
            # command_dict = player_input()
            if CVOA_TICKS == -1:
                command_dict = cvoa_algo(Player, game_objects)
            if "MAX_FRAMES" in command_dict:
                if CVOA_TICKS >= command_dict["MAX_FRAMES"]:
                    print("CVOA_TICKS", CVOA_TICKS)
                    command_dict = cvoa_algo(Player, game_objects)
                    CVOA_TICKS = 0
            CVOA_TICKS += 1
            

        # print(command_dict)

        # for tick in ticks: #simulate command for certain amount of ticks
        for tick in range(TICKS):
            movement(command_dict, Player, game_objects)
            # Simluate collision
            game_collision(Player, game_objects)

        # renderer_pygame(surface, clock, Player, game_objects)


# just organizational things.
if __name__ == "__main__":
    main()
