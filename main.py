import math
from graphics import *  # very basic graphics API #NOTE: Remember to do "pip install graphics.py"
# graphics.py documentation: https://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf

import sys, os, pygame, re, random
import numpy as np
from copy import copy, deepcopy

from scipy.spatial import KDTree

from entity import Entity, Spawner, VisualElement
from renderer import graphics_init, renderer_graphics, pygame_init, renderer_pygame

import datetime

# GLOBALS
SCREEN_HEIGHT = 448  # These are just the Touhou numbers adapted directly
SCREEN_WIDTH = 384

helpers = [] #FIXME: awful way of doing this.
void_center_visuals = []

#FIXME: Making globals here, very ugly fix this later.
creating_grid = False
grid_points = []

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

# custom KD-tree ?
# class KDNode:
#     def __init__(self, points, depth=0, depth_limit=2):
#         self.axis = depth % 2 #determines which axis to split along (0 = x, 1 = y)
#         self.left = None
#         self.right = None
#         self.point = None
#         self.points = None #only populated for non-leaf nodes
#         self.count = len(points)
#         self.bbox = self.compute_bbox(points)
    
#         if self.count <= 1 or depth >= depth_limit:
#             self.points = points
#             if points:
#                 self.point = points[0]
#             return
    
#         #Sort and split
#         if (depth <= depth_limit):
#             points.sort(key=lambda pt: pt[self.axis])
#             median_index = len(points) // 2
#             self.point = points[median_index] #split point

#             self.left = KDNode(points[:median_index], depth+1)
#             self.right = KDNode(points[median_index:], depth+1)
    
#     def compute_bbox(self, points):
#         arr = np.array(points)
#         min_corner = arr.min(axis=0)
#         max_corner = arr.max(axis=0)
#         return (min_corner, max_corner)
    
#     def intersects_box(self, min_corner, max_corner):
#         node_min, node_max = self.bbox
#         return np.all(max_corner >= node_min) and np.all(min_corner <= node_max)
    
#     def bbox_inside(self, min_corner, max_corner):
#         node_min, node_max = self.bbox
#         return np.all(node_min >= min_corner) and np.all(node_max <= max_corner)

#     def count_in_box(self, min_corner, max_corner):
#         if not self.intersects_box(min_corner, max_corner):
#             return 0

#         # Entire node is inside the box
#         if self.bbox_inside(min_corner, max_corner):
#             return self.count

#         # If leaf node, count matching points
#         if self.points is not None:
#             return sum(np.all((min_corner <= pt) & (pt <= max_corner)) for pt in self.points)

#         return self.left.count_in_box(min_corner, max_corner) if self.left != None else 0 + \
#                self.right.count_in_box(min_corner, max_corner) if self.right != None else 0
    



def macrododging_algo(player, objects, num_voids=5, grid_resolution=50, min_separation=0.0):
    #uses kd-trees to return positions far away from existing positions
    #should be relatively fast?
    global helpers
    
    global creating_grid #Set this to global
    global grid_points
    xmin, xmax = SCREEN_WIDTH, 0
    ymin, ymax = SCREEN_HEIGHT, 0
    if grid_points == []:
        for i in range(grid_resolution):
            x = xmin + i * (xmax - xmin) / (grid_resolution - 1)
            for j in range(grid_resolution):
                y = ymin + j * (ymax - ymin) / (grid_resolution - 1)
                grid_points.append((x, y))
        print("Grid creation should fire only once.")
        creating_grid = True

    vals = [(object.x,object.y) for object in objects if type(object) == Entity and object.name != "player"]
    
    results = []
    tree = None
    if (len(vals) == 0): #if this is empty then the screen has no bullets left on it.
        vals = grid_points
        result = grid_points
        tree = KDTree(vals)
    else:
        tree = KDTree(vals)
        # tree = KDNode(vals)
        results = []

    # print(grid_points)
    # min_dist = float("inf")
    min_dist = 32.0
    min_clumps = sys.maxsize
    max_dist = float("-inf")
    # #Check radius - How it works:
    # #1. square areas = (Area / num. grid points) -> ideally returns screen space divided into areas
    # #2. math.sqrt(square areas / PI) -> equation to return radius of circle given circle's area, given divided screen space area instead.
    # check_radius = math.sqrt( ((SCREEN_HEIGHT * SCREEN_WIDTH) / grid_resolution) / math.pi ) #SCREEN_HEIGHT / len(objects) #64
    check_radius = 64
    # print(check_radius)

    for grid_point in grid_points:
        # distance, _ = tree.query(grid_point)
        # if distance >= min_dist:
        #     results.clear()
        #     results.append(grid_point)
        #     # if distance >= max_dist:
        #     #     max_dist = distance
        #     distance = min_dist

        # Return number of objects around "grid_point" in radius "r"
        # points_in_radius = len(tree.query_ball_point(grid_point, r=player.height * 2))
        
        points_in_radius = len(tree.query_ball_point(grid_point, r=check_radius))
        # points_in_radius = len(np.all((tree.data >= [0, 0]) & (tree.data <= [100, 100]), axis=1))
        
        # x, y = grid_point
        # points_in_radius = tree.count_in_box(np.array([x-32, y-32]), np.array([x+32, y+32]))

        if min_clumps > points_in_radius:
            results.clear()
            results.append(grid_point)
            min_clumps = points_in_radius
        elif min_clumps == points_in_radius:
            results.append(grid_point)

    # Create another K-D Tree, this time with the empty areas.
    # Get only the empty areas with the most amount of empty areas near it
    # This way, the player does not go towards empty areas (blue) that do not have empty areas near it.
    # The areas the contain a lot of empty areas area (red) theoretically should be safter, as it's clumped with more empty areas.
    results1 = []
    tree1 = KDTree(results)
    max_count = -sys.maxsize
    for result in results:
        points_in_radius = len(tree1.query_ball_point(result, r=check_radius/2)) 
        if max_count < points_in_radius: #Get the area with the most amount of empty areas.
            results1.clear()
            results1.append(result)
            max_count = points_in_radius
        elif max_count == points_in_radius:
            results1.append(result)

    # print(results, "results")
    # print(len(results1), len(results))
    helpers.clear() #clear list
    for grid_point in results: #visual all void centers
        x, y = grid_point
        # print("Grid Point", grid_point)
        # temp = VisualElement("Void Center", x, y, 10, 10)
        # distance, _ = tree.query(grid_point)
        # val = int(255.0 * (distance/max_dist))
        # temp.pygame_color = pygame.Color(val, val, 255, 100)
        # helpers.append(temp)
        
        temp = VisualElement("Void Center", x, y, 10, 10)
        temp.pygame_color = pygame.Color(125, 125, 255, 100)
        # temp.pygame_color = pygame.Color(0, 255, 255, 200)
        helpers.append(temp)

    for grid_point in results1: #visual all void centers
        x, y = grid_point
        # print("Grid Point", grid_point)
        # temp = VisualElement("Void Center", x, y, 10, 10)
        # distance, _ = tree.query(grid_point)
        # val = int(255.0 * (distance/max_dist))
        # temp.pygame_color = pygame.Color(val, val, 255, 100)
        # helpers.append(temp)
        
        temp = VisualElement("Void Center", x, y, 10, 10)
        temp.pygame_color = pygame.Color(255, 0, 0, 100)
        helpers.append(temp)


    return results1



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
    # max_t_velocity = possible_velocities[random.randint(0, len(possible_velocities)-1)]
    max_t_velocity = possible_velocities[0]
    
    CHECK_FRAMES = 20 #amount of frames to check for collision

    # MAX_FRAMES = CHECK_FRAMES + 1
    MAX_FRAME_DIRS = []

    MAX_FRAMES = -1
    for v in possible_velocities:
        for ob in objects:
            if type(ob) is Entity:
                if ob.name != "player":
                    no_collision_frames = player.check_steps_ahead(CHECK_FRAMES, ob, v)
                    if dir_collision[v] > no_collision_frames: #get the minimum amount of frames for that direction, based on collision detection with the obstacle
                        dir_collision[v] = no_collision_frames
        #Check best directions
        if dir_collision[v] > MAX_FRAMES:
            MAX_FRAME_DIRS.clear()
            MAX_FRAME_DIRS.append(v)
            MAX_FRAMES = dir_collision[v]
        elif dir_collision[v] == MAX_FRAMES:
            MAX_FRAME_DIRS.append(v)

    # print(MAX_FRAME_DIRS, MAX_FRAMES)

    # Macrododging
    #1) Calculate void centers from inverse clustering 
    # void_centers, _ = macrododging_algo(player, objects)
    void_centers = macrododging_algo(player, objects)
    # void_centers = [(int(SCREEN_WIDTH/2), int(SCREEN_HEIGHT/2))]
    #2) Calculate whichever direction will move to closest void center
    dist = float('inf')
    for dir in MAX_FRAME_DIRS:
        dir_x, dir_y = dir
        for center in void_centers:
            center_x, center_y = center
            if dist > euclidean_distance([player.x + dir_x, player.y + dir_y], [center_x, center_y]):
                max_t_velocity = dir
                dist = euclidean_distance([player.x + dir_x, player.y + dir_y], [center_x, center_y])
        

    dictionary = {"REWIND": False, "TICKS": None, "PLAYER_MOVEMENT": max_t_velocity, "MAX_FRAMES": MAX_FRAMES}
    return dictionary



def clustering(player, objects):
    # Cluster algorithm to help with macrododging
    pass



#CHROMOSOME = [TIME][PREFAB][POSITION][#BULLETS][SPEED]
#Prefab spawners
X = Spawner(0, 0, 16, 16)
Y = Spawner(0, 0, 16, 16)
def lvl_generator(time=1000, init_random=True):
    global X
    global Y

    lvl = dict()

    random.seed(10)

    max_bullets = 50 # FIXME: Need to somehow make better max limitation? 
    # bullets_spawned = 

    for x in range(0, time+1):
        if random.random() >= 0.9:
            prefabs = [X,Y]
            # bullet_spawner = prefabs[random.randint(0, len(prefabs)-1)]
            bullet_spawner = Spawner(0, 0, 16, 16)
            bullet_spawner.x = random.randint(0, SCREEN_WIDTH)
            
            # print(bullet_spawner.x)

            bullet_spawner.y = SCREEN_HEIGHT if random.random() >= 0.5 else 0
            
            
            bullet_spawner.num_bullets = random.randint(1, 8)
            bullet_spawner.bullet_speed = random.uniform(0.5, 2) 
            lvl[x] = bullet_spawner

            max_bullets -= bullet_spawner.num_bullets

            # return bullet_spawner.spawn_circular_bullets(8, 1)
        else:
            max_bullets += 5
    return lvl

    # Level generation component
    if init_random:
        if random.random() >= 0.5:
            prefabs = [X,Y]
            bullet_spawner = prefabs[random.randint(0, len(prefabs)-1)]
            bullet_spawner.x = random.randint(0, SCREEN_WIDTH)
            bullet_spawner.y = SCREEN_HEIGHT if random.random() >= 0.5 else 0
            return bullet_spawner.spawn_circular_bullets(8, 1)
    else:
        return []
        
    return []

def play_lvl():
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
            #FIXME: Make this variable
            if player.x + x >= 384 or player.x + x <= 0:
                x = 0
            if player.y + y >= 448 or player.y + y <= 0:
                y = 0
            player.movement(x, y)
            # if (player.x + x >= 384 or player.x + x <= 0 or \
            #     player.y + y >= 448 or player.y + y <= 0) == False:
            #     player.movement(x, y)

    cnt = 0
    obj_len = len(objects)
    while cnt < obj_len:
        object = objects.pop(0)
        if type(object) is Entity:  # bullets and misc
            if object.name == "player":  # skip player
                objects.append(object)
                # continue
            else:  # check everything else
                if inputs["REWIND"]:
                    object.rewind()
                    objects.append(object)
                else:
                    object.movement(object.velocity_x, object.velocity_y)
                    if object.check_outside_play_area() == False:
                        objects.append(object)
        elif type(object) is Spawner:  # spawners
            if inputs["REWIND"]:
                object.update(rewind=True)
            else:
                object.update()
            objects.append(object)
        cnt += 1
    # # move all other objects
    # for object in objects:
    #     if type(object) is Entity:  # bullets and misc
    #         if object.name == "player":  # skip player
    #             continue
    #         else:  # check everything else
    #             if inputs["REWIND"]:
    #                 object.rewind()
    #             else:
    #                 object.movement(object.velocity_x, object.velocity_y)
    #     elif type(object) is Spawner:  # spawners
    #         if inputs["REWIND"]:
    #             object.update(rewind=True)
    #         else:
    #             object.update()


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

    lvl = lvl_generator(1000)

    TICKS = 1

    TOTAL_TICKS = 0

    CVOA_TICKS = -1 # Determines when new direction should be returned by CVOA. Without this output is chaotic.

    command_dict = {}
    command_dict["CONTROL_OVERRIDE"] = True

    cvoa_return_dict = {}

    prev_time = datetime.datetime.now()

    while CMD_INPUT != "END":  # game loop
        # if (datetime.datetime.now() - prev_time).total_seconds() > 1.0:
        #     # bullet_spawner.x = random.randint(0, SCREEN_WIDTH)
        #     # bullet_spawner.y = SCREEN_HEIGHT if random.random() >= 0.5 else 0
        #     # game_objects.extend(bullet_spawner.spawn_circular_bullets(8, 1))
            
        #     # game_objects.extend(lvl_generator())

        #     prev_time = datetime.datetime.now()
        #     # print("NEW TIME")        

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
            
        if (TOTAL_TICKS in lvl.keys()):
            print(TOTAL_TICKS)
            temp_spawner = lvl[TOTAL_TICKS]
            game_objects.extend(temp_spawner.spawn_circular_bullets(temp_spawner.num_bullets, temp_spawner.bullet_speed))
        # TOTAL_TICKS += 1

        # print(command_dict)

        # for tick in ticks: #simulate command for certain amount of ticks
        for tick in range(TICKS):
            TOTAL_TICKS += 1

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
