import math
from graphics import *  # very basic graphics API #NOTE: Remember to do "pip install graphics.py"
# graphics.py documentation: https://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf

import sys, os, pygame, re, random
import numpy as np
from copy import copy, deepcopy

from entity import Entity, Spawner, VisualElement
from renderer import graphics_init, renderer_graphics, pygame_init, renderer_pygame

import datetime

# GLOBALS
SCREEN_HEIGHT = 448  # These are just the Touhou numbers adapted directly
SCREEN_WIDTH = 384

helpers = [] #FIXME: awful way of doing this.

def parse_input(Player):
    CMD_INPUT = input("ENTER COMMAND HERE: ")  # accept input until stop

    CMD_INPUT = CMD_INPUT.upper()  # make inputs uppercase

    # create dictionary that returns parsed values of input
    dictionary = {"REWIND": False, "TICKS": None, "PLAYER_MOVEMENT": (0, 0), "CONTROL_OVERRIDE": True}

    # simulate player movement
    if CMD_INPUT == "UP":
        dictionary["PLAYER_MOVEMENT"] = (0, -1)
    elif CMD_INPUT == "DOWN":
        dictionary["PLAYER_MOVEMENT"] = (0, 1)
    elif CMD_INPUT == "LEFT":
        dictionary["PLAYER_MOVEMENT"] = (-1, 0)
    elif CMD_INPUT == "RIGHT":
        dictionary["PLAYER_MOVEMENT"] = (1, 0)
    elif CMD_INPUT == "UPLEFT":
        dictionary["PLAYER_MOVEMENT"] = (-1, -1)
    elif CMD_INPUT == "UPRIGHT":
        dictionary["PLAYER_MOVEMENT"] = (1, -1)
    elif CMD_INPUT == "DOWNLEFT":
        dictionary["PLAYER_MOVEMENT"] = (-1, 1)
    elif CMD_INPUT == "DOWNRIGHT":
        dictionary["PLAYER_MOVEMENT"] = (1, 1)
    elif CMD_INPUT == "NONE":
        dictionary["PLAYER_MOVEMENT"] = (0, 0)
    else:
        dictionary["PLAYER_MOVEMENT"] = None
        dictionary["CONTROL_OVERRIDE"] = False


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
        # Player.rewind()

    return dictionary


def player_input(dictionary):
    # manual control for game
    # used only in pygame rendering mode

    # NOTE: this return dictionary should be in the exact same format as the one in parse_input().
    # dictionary = {"REWIND": False, "TICKS": None, "PLAYER_MOVEMENT": (0, 0)}
    dictionary["REWIND"] = False
    dictionary["TICKS"] = None

    x, y = 0, 0
    down = (0, 0)
    up = (0, 0)
    left = (0, 0)
    right = (0, 0)
    
    #For loop here is for keys that only get pressed once, or events that don't happen simultaneously.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN: #Only happen when key pressed down (once)
            if event.key == pygame.K_r:
                dictionary["CONTROL_OVERRIDE"] = not(dictionary["CONTROL_OVERRIDE"])
                if dictionary["CONTROL_OVERRIDE"] == True:
                    print("CONTROL OVERRIDEN")
                else:
                    print("CONTROL AUTOMATIC")
    keys = pygame.key.get_pressed()

    #Below is required to detect multiple key presses at once.
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

# Euclidean distance function
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

draw_void_center = []

def macrododging_algo(player, objects, num_voids=5, grid_resolution=50, min_separation=0.0):
    # xmin, xmax = 0, SCREEN_WIDTH
    # ymin, ymax = 0, SCREEN_HEIGHT
    xmin, xmax = SCREEN_WIDTH, 0
    ymin, ymax = SCREEN_HEIGHT, 0
    # xmin, xmax = 0, SCREEN_WIDTH
    # ymin, ymax = SCREEN_HEIGHT, 0

    grid_points = []
    for i in range(grid_resolution):
        x = xmin + i * (xmax - xmin) / (grid_resolution - 1)
        for j in range(grid_resolution):
            y = ymin + j * (ymax - ymin) / (grid_resolution - 1)
            grid_points.append((x, y))

    scored_points = []
    min_dist = float("inf")
    max_dist = float("-inf")
    for gp in grid_points:
        min_dist = float("inf")
        for pt in objects:
            if type(pt) is Entity and pt.name != "player":
                min_dist = min(min_dist, euclidean_distance(gp, pt.position()))
                max_dist = max(max_dist, euclidean_distance(gp, pt.position()))
        scored_points.append((min_dist, gp))

    scored_points.sort(reverse=True)

    void_centers = []
    for dist, gp in scored_points:
        if all(euclidean_distance(gp, existing) >= min_separation for existing in void_centers):
            void_centers.append(gp)
        if len(void_centers) >= num_voids:
            break

    helpers.clear() #clear list
    for center in void_centers: #visual all void centers
        x, y = center
        # print("CENTER", center)
        helpers.append(VisualElement("Void Center", x, y, 10, 10))

    for dist, gp in scored_points: #visualize all grid points
        x, y = gp
        # print("CNETER", center)
        temp = VisualElement("Void Center", x, y, 2, 2, "green")
        # print("dist", dist/max_dist)
        val = int(255 * (dist/max_dist))
        temp.pygame_color = pygame.Color(val, val, 255, 125)
        helpers.append(temp)

    return void_centers, scored_points


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
                        # print("num of frames", no_collision_frames)
                        if dir_collision[v] > no_collision_frames: #get the minimum amount of frames for that direction, based on collision detection with the obstacle
                            dir_collision[v] = no_collision_frames

    max_frames = 0

    # print("GREATEST", dir_collision)
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

        #FROM THE BEST VELOCITIES, CHOOSE ONE
        #NOTE: This is where the macrododging algorithm should go.

        #1) Macrododging
        void_centers, _ = macrododging_algo(player, objects)
        # print(void_centers)
        val = float('inf')
        for dir in safe_velocities[GREATEST_POSSIBLE_FRAMES]:
            dir_x, dir_y = dir
            for center in void_centers:
                center_x, center_y = center
                if val > euclidean_distance([player.x + dir_x, player.y + dir_y], [center_x, center_y]):
                    max_t_velocity = dir
                    val = euclidean_distance([player.x + dir_x, player.y + dir_y], [center_x, center_y])

        # #2) choose closest to center
        # for dir in safe_velocities[GREATEST_POSSIBLE_FRAMES]:
        #     dir_x, dir_y = dir
        #     #manhattan distance
        #     # y_axis * 2 => to emphasize y-axis movement more over x, otherwise when same good move appears, gets stuck beneath bullet and collides at bottom of screen.
        #     temp = abs(player.x + dir_x - 384/2) + abs(player.y + dir_y - 448/2) 
        #     if temp <= dist:
        #         max_t_velocity = dir
        #         dist = temp
        
        #3) pick randomly
        # max_t_velocity = safe_velocities[GREATEST_POSSIBLE_FRAMES][random.randint(0, len(safe_velocities[GREATEST_POSSIBLE_FRAMES])-1)]
    
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
            inputs["REWIND_LIMIT"] = player.rewind()
        else:
            x, y = inputs["PLAYER_MOVEMENT"] #Get player inputs

            # STOP player from moving outside of bounds
            if player.x + x >= 384 or player.x + x <= 0:
                x = 0
            if player.y + y >= 448 or player.y + y <= 0:
                y = 0
            player.movement(x, y)
            # if (player.x + x >= 384 or player.x + x <= 0 or \
            #     player.y + y >= 448 or player.y + y <= 0) == False:
            #     player.movement(x, y)

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
    temp_objects = []
    for object in objects:
        if type(object) is Entity and object.name != "player":
            object.aabb(player)
            if object.outside_of_area() == False: #NOTE: This will become an issue with the "rewind" functionality. Do something about that later.
                temp_objects.append(object)
        elif type(object) is Spawner:
            object.spawner_detect_collision(player)
    objects = temp_objects

def main():
    RENDER_MODE = "INPUT"  # "GRAPHICS"
    # RENDER_MODE = "GRAPHICS"
    # INPUT_MODE = "TERMINAL" #"TERMINAL" #KEYS
    INPUT_MODE = "KEYS"

    # initialize render(s)
    if RENDER_MODE == "GRAPHICS":
        window = graphics_init(SCREEN_WIDTH, SCREEN_HEIGHT)  # graphics.py renderer
    if RENDER_MODE == "INPUT":
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

    CVOA_TICKS = -1 # Determines when new direction should be returned by CVOA. Without this output is chaotic.

    command_dict = {}
    command_dict["CONTROL_OVERRIDE"] = True

    cvoa_return_dict = {}

    prev_time = datetime.datetime.now()

    while CMD_INPUT != "END":  # game loop
        if (datetime.datetime.now() - prev_time).total_seconds() > 5:
            bullet_spawner.x = random.randint(0, SCREEN_WIDTH)
            game_objects.extend(bullet_spawner.spawn_circular_bullets(8, 1))
            prev_time = datetime.datetime.now()
            # print("NEW TIME")

        # Renderer

        if RENDER_MODE == "GRAPHICS":
            renderer_graphics(Player, game_objects, window, helpers)
        if RENDER_MODE == "INPUT":
            renderer_pygame(surface, clock, Player, game_objects,  helpers)

        if INPUT_MODE == "TERMINAL":
            command_dict = parse_input(Player)
            if command_dict["TICKS"] != None:
                TICKS = command_dict["TICKS"]
                CVOA_TICKS = -1
                continue  # restart with new tick rate
        if INPUT_MODE == "KEYS":
            # command_dict = player_input()
            player_input(command_dict)
        # if INPUT_MODE == "NONE":
        #     try:
        #         TICKS = int(input())
        #     except:
        #         TICKS = 1
            # if CVOA_TICKS == -1:
            #     command_dict = cvoa_algo(Player, game_objects)
            # if "MAX_FRAMES" in command_dict:
            #     if CVOA_TICKS >= command_dict["MAX_FRAMES"]:
            #         print("CVOA_TICKS", CVOA_TICKS)
            #         command_dict = cvoa_algo(Player, game_objects)
            #         CVOA_TICKS = 0
            # CVOA_TICKS += 1
            

        # print(command_dict)

        # for tick in ticks: #simulate command for certain amount of ticks
        for tick in range(TICKS):

            if "REWIND_LIMIT" in command_dict:
                if command_dict["REWIND_LIMIT"] == True:
                    break

            CVOA_ACTIVE = True
            # print(command_dict["PLAYER_MOVEMENT"])
            if "CONTROL_OVERRIDE" in command_dict and command_dict["CONTROL_OVERRIDE"] == False:
                if (CVOA_ACTIVE):
                    if CVOA_TICKS == -1: #Initialize CVOA timer check
                        cvoa_return_dict = cvoa_algo(Player, game_objects)
                    if "MAX_FRAMES" in command_dict:
                        if CVOA_TICKS >= command_dict["MAX_FRAMES"]:
                            # print("CVOA_TICKS", CVOA_TICKS)
                            cvoa_return_dict = cvoa_algo(Player, game_objects)
                            CVOA_TICKS = 0
                    command_dict["MAX_FRAMES"] = cvoa_return_dict["MAX_FRAMES"]
                    command_dict["PLAYER_MOVEMENT"] = cvoa_return_dict["PLAYER_MOVEMENT"]
                    CVOA_TICKS += 1

            movement(command_dict, Player, game_objects)
            # Simluate collision
            game_collision(Player, game_objects)

        # renderer_pygame(surface, clock, Player, game_objects)

    if RENDER_MODE == "INPUT":
        pygame.quit()
    sys.exit()

    

# just organizational things.
if __name__ == "__main__":
    main()
