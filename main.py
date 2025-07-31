import math
from graphics import *  # very basic graphics API #NOTE: Remember to do "pip install graphics.py"
# graphics.py documentation: https://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf

import sys, os, pygame, re, random
import numpy as np
from copy import copy, deepcopy

from scipy.spatial import KDTree

from entity import Entity, Spawner, VisualElement
from level import Level
from renderer import graphics_init, renderer_graphics, pygame_init, renderer_pygame
from data_visualization import Graph

import datetime
import time as TIME

# import threading
import multiprocessing

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

def macrododging_algo(player, objects, grid_resolution=30):
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
        # print("Grid creation should fire only once.")
        creating_grid = True

    # filter objects to exclude "Player" type objects so that player positions will not effect output
    vals = [(object.x,object.y) for object in objects if type(object) == Entity and object.type != "Player"]
    
    results = []
    tree = None
    # Create a KD-Tree with values for fast detection (README: Could probably use this for normal collision checking?)
    if (len(vals) == 0): #if this is empty then the screen has no bullets left on it.
        vals = grid_points
        result = grid_points
        tree = KDTree(vals)
    else:
        tree = KDTree(vals)
        results = []

    min_clumps = sys.maxsize
    # #Check radius (i.e. tree.query_ball_point) - How it works:
    # #1. square areas = (Area / num. grid points) -> ideally returns screen space divided into areas
    # #2. math.sqrt(square areas / PI) -> equation to return radius of circle given circle's area, given divided screen space area instead.
    # check_radius = math.sqrt( ((SCREEN_HEIGHT * SCREEN_WIDTH) / grid_resolution) / math.pi ) #SCREEN_HEIGHT / len(objects) #64
    check_radius = player.height #64 16

    for grid_point in grid_points:
        # Return number of objects around "grid_point" in radius "r"
        points_in_radius = len(tree.query_ball_point(grid_point, r=check_radius))
        # Prioritize going to areas that are empty
        if min_clumps > points_in_radius:
            results.clear()
            results.append(grid_point)
            min_clumps = points_in_radius
        elif min_clumps == points_in_radius:
            results.append(grid_point)

    # Create another K-D Tree, this time with the empty areas.
    # Get only the empty areas with the most amount of empty space near it
    # This way, the player does not go towards empty areas (blue) that do not have empty areas near it.
    # The areas the contain a lot of empty areas area (red) theoretically should be safter, as it's clumped with more empty areas.
    results1 = []
    tree1 = KDTree(results)
    max_count = -sys.maxsize
    for result in results:
        points_in_radius = len(tree1.query_ball_point(result, r=check_radius*2)) 
        if max_count < points_in_radius: #Get the area with the most amount of empty areas.
            results1.clear()
            results1.append(result)
            max_count = points_in_radius
        elif max_count == points_in_radius:
            results1.append(result)

    helpers.clear() #clear list
    for grid_point in results: #visualize empty grid points
        x, y = grid_point
        temp = VisualElement("Grid Point", x, y, 10, 10)
        temp.pygame_color = pygame.Color(125, 125, 255, 100)
        helpers.append(temp)

    for grid_point in results1: #visualize grid points enclosed within other empty grid points
        x, y = grid_point
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
        # ( 0 * multiplier,  0 * multiplier), #stand still
        # ( 0 * multiplier, -1 * multiplier), #up
        # (-1 * multiplier, -1 * multiplier), #upleft
        # ( 1 * multiplier, -1 * multiplier), #upright
        # ( 0 * multiplier,  1 * multiplier), #down
        # (-1 * multiplier,  1 * multiplier), #downleft
        # ( 1 * multiplier,  1 * multiplier), #downright
        # (-1 * multiplier,  0 * multiplier), #left
        # ( 1 * multiplier,  0 * multiplier), #right
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

    if player.strength == "weak":
        possible_velocities = [
            # ( 0 * multiplier,  0 * multiplier), #stand still
            # ( 0 * multiplier, -1 * multiplier), #up
            # ( 0 * multiplier,  1 * multiplier), #down
            # (-1 * multiplier,  0 * multiplier), #left
            # ( 1 * multiplier,  0 * multiplier), #right
            # ( 0 * multiplier,  0 * multiplier), #stand still
            #Without multiplier
            ( 0, -1), #up
            ( 0,  1), #down
            (-1,  0), #left
            ( 1,  0), #right
        ]
    
    CHECK_FRAMES = 16 #20 #amount of frames to check for collision

    #create a dictionary of smallest distance direction needs to go to collide with something
    dir_collision = dict()
    for each in possible_velocities:
        dir_collision[each] = CHECK_FRAMES
    
    #somehow also need to choose "best available" if no good decisions are available
    # safe_velocities = possible_velocities.copy()
    # max_t_velocity = possible_velocities[random.randint(0, len(possible_velocities)-1)]
    max_t_velocity = possible_velocities[0]

    # MAX_FRAMES = CHECK_FRAMES + 1
    MAX_FRAME_DIRS = []

    MAX_FRAMES = -1
    for v in possible_velocities:
        for ob in objects:
            if type(ob) is Entity:
                if ob.type != "Player":
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

    direction_scores = {}
    # Epsilon greedy
    if random.random() <= 0.05:
        max_t_velocity = random.choice(list(MAX_FRAME_DIRS))
    else:
        # Macrododging
        #1) Calculate void centers from inverse clustering 
        # void_centers, _ = macrododging_algo(player, objects)
        void_centers = macrododging_algo(player, objects)
        # void_centers = [(int(SCREEN_WIDTH/2), int(SCREEN_HEIGHT/2))]
        #2) Calculate whichever direction will move to closest void center
        # dist = float('inf')
        for dir in MAX_FRAME_DIRS:
            direction_scores[dir] = float('inf')
            dir_x, dir_y = dir
            for center in void_centers:
                center_x, center_y = center
                # if dist > euclidean_distance([player.x + dir_x, player.y + dir_y], [center_x, center_y]):
                    # max_t_velocity = dir
                    # dist = euclidean_distance([player.x + dir_x, player.y + dir_y], [center_x, center_y])
                score = euclidean_distance([player.x + dir_x, player.y + dir_y], [center_x, center_y])
                if (direction_scores[dir] > score):
                    direction_scores[dir] = score
        max_t_velocity = min(direction_scores, key=direction_scores.get)

    # Check for directions that have same value. NOTE: Can use this to add randomization?
    # for dir in MAX_FRAME_DIRS:
    #     if dir != max_t_velocity and (direction_scores[dir] == direction_scores[max_t_velocity]):
    #         print (f"Same distance for {max_t_velocity} {dir} for player {player.name}")
    # print ("Check values: ", direction_scores)
    # print ("Result: ", max_t_velocity)

    MAX_FRAMES = dir_collision[max_t_velocity]

    # print("MAX_FRAMES: ", MAX_FRAMES, void_centers, dir_collision)

    # MAX_FRAMES = 16

    dictionary = {"REWIND": False, "TICKS": None, "PLAYER_MOVEMENT": max_t_velocity, "MAX_FRAMES": MAX_FRAMES}
    return dictionary

#CHROMOSOME = [TIME] :: [PREFAB][POSITION][#BULLETS][SPEED]
#Prefab spawners
X = Spawner(0, 0, 16, 16)
Y = Spawner(0, 0, 16, 16)
def lvl_generator(time=1000, seed=TIME.time()):
    global X
    global Y

    # Create the dictionary for a level
    lvl = dict()
    # random.seed(10)
    # seed = TIME.time()
    # seed = 1751870909.2743487
    random.seed(seed)
    print(f"Seed used: {seed}")

    # max_bullets = 50 # FIXME: Need to somehow make better max limitation?  

    # Go through each timestep, and determine whether or not to spawn bullets
    for x in range(0, time+1):
        if random.random() >= 0.85: #0.85
            prefabs = [X,Y]
            # bullet_spawner = prefabs[random.randint(0, len(prefabs)-1)]
            bullet_spawner = Spawner(0, 0, 16, 16)
            bullet_spawner.x = random.randint(0, SCREEN_WIDTH)
                                                                    #randomly decide:
            bullet_spawner.num_bullets = random.randint(1, 8)       #1. Number of bullets per spawner
            bullet_spawner.bullet_speed = random.uniform(0.5, 2)    #2. The speed of bullet
            lvl[x] = bullet_spawner                                 #Then place bullet spawner at timestep (x)

            # max_bullets -= bullet_spawner.num_bullets

            # return bullet_spawner.spawn_circular_bullets(8, 1)
        # else:
        #     max_bullets += 5
    return lvl

def create_players(num_weak=1, num_strong=1):
    created_players = []
    for i in range(num_weak+num_strong):
        if i < num_weak:    # Create "weak" players
            extra_player = Entity(f"player{i}_WEAK", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 16, 16, type="Player")
            extra_player.strength = "weak"
            extra_player.pygame_color = pygame.Color("green")
        else:               # Create "strong" players
            extra_player = Entity(f"player{i}_STRONG", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 16, 16, type="Player")
            extra_player.strength = "strong"
            extra_player.pygame_color = pygame.Color("purple")
        created_players.append(extra_player)
    return created_players

def play_lvl(queue, lvl=None):
    # Setup all players and game objects
    total_weak = 4
    total_strong = 4

    players = create_players(4, 4)
    all_players = copy(players)
    game_objects = copy(players)

    #Use pygame renderer
    surface, clock = pygame_init(SCREEN_WIDTH, SCREEN_HEIGHT)
    # renderer_pygame(surface, clock, players, game_objects, helpers)
    
    # Generate the level
    # seed = TIME.time()
    # lvl_length = 1000
    # if lvl == None:
    #     lvl = lvl_generator(lvl_length, seed)
    
    lvl_length = 1000
    if lvl == None:
        lvl = Level()
        lvl.generate()

    TOTAL_TICKS = 0 # Total number of ticks over simulation

    command_dict = {}

    only_players = False # Are there only players left on screen?

    running = True
    while running: # In simulation!

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # print(TOTAL_TICKS)
        renderer_pygame(surface, clock, players, game_objects, helpers)

        if TOTAL_TICKS in lvl.dict.keys():
            temp_spawner = lvl.dict[TOTAL_TICKS] # Get spawner(s) at this specific tick
            game_objects.extend(temp_spawner.spawn_circular_bullets(temp_spawner.num_bullets, temp_spawner.bullet_speed)) # Use the spawners
        
        no_players_left = True

        for player in players: # For each player
            if player in game_objects:
                if player.CVOA_TICKS == -1: # Initialize CVOA timer check
                    player.cvoa_return_dict = cvoa_algo(player, game_objects)
                if "MAX_FRAMES" in player.cvoa_return_dict: # if CVOA timer already exists for player
                    if player.CVOA_TICKS >= player.cvoa_return_dict["MAX_FRAMES"]: # if player's tick count (timer) has elapsed
                        player.cvoa_return_dict = cvoa_algo(player, game_objects) # redo CVOA algorithm
                        player.CVOA_TICKS = 0 # Reset timer
                player.CVOA_TICKS += 1 # count timer
                player.TIME_ALIVE += 1 # Increment time alive
                no_players_left = False

        # if no players are left then just break
        if no_players_left == True:
            break
        
        # Simulate movement of all objects and players
        movement(players, game_objects)
        # Simulate collision
        only_players = game_collision(players, game_objects)
        
        if TOTAL_TICKS >= lvl_length and only_players:
            break
        
        TOTAL_TICKS += 1 #increment simulation ticks

    pygame.quit() 
    
    # When simulation is finished (i.e. no other objects other than players)
    # Analyze results:
    # data = dict()

    # data["weak_times"] = []
    # data["strong_times"] = []
    # data["weak_dead"] = 0
    # data["strong_dead"] = 0
    # data["seed"] = seed # FIXME: Need to do this to something else.
    # data["total_weak"] = total_weak
    # data["total_strong"] = total_strong
    lvl.total_strg = total_strong
    lvl.total_weak = total_weak
    # if "lvl" not in data.keys():
    #     data["lvl"] = lvl
    #FIXME: Need some way of storing level data?

    for player in all_players:
        if player.strength == "weak":
            lvl.weak_times.append(player.TIME_ALIVE)
            if player not in players:
                lvl.weak_dead += 1
        elif player.strength == "strong":
            lvl.strg_times.append(player.TIME_ALIVE)
            if player not in players:
                lvl.strg_dead += 1

    # return data
    try:
        lvl.tested = True
        queue.put_nowait(lvl)
    except:
        print("ERROR IN PUT IN QUEUE")

# Simulate movement for all objects + player in game
# CHECK: If rewind functionality properly applied
def movement(players, objects):
    for player in players:
        if type(player) is Entity:  # do player movement stuff
            x, y = player.cvoa_return_dict["PLAYER_MOVEMENT"] #Get player inputs

            # print(f"{x}, {y}, {player.name}")

            # STOP player from moving outside of bounds
            #FIXME: Make this variable
            if player.x + x >= 384 or player.x + x <= 0:
                x = 0
            if player.y + y >= 448 or player.y + y <= 0:
                y = 0
            player.movement(x, y)

    cnt = 0
    obj_len = len(objects)
    while cnt < obj_len:
        object = objects.pop(0)
        if type(object) is Entity:  # bullets and misc
            if object.type == "Player":  # skip player
                objects.append(object)
                # continue
            else:  # check everything else
                object.movement(object.velocity_x, object.velocity_y)
                if object.check_outside_play_area() == False:
                    objects.append(object)
        elif type(object) is Spawner:  # spawners
            object.update()
            objects.append(object)
        cnt += 1


def game_collision(players, objects):
    # collision detection for objects in the game

    only_players = True

    for player in players:
        idx = 0
        length = len(objects)
        if length == 0:
            continue
        while idx < length:
            object = objects.pop(0)
            if type(object) is Entity and object.type == "Bullet":
                only_players = False
                if object.aabb(player):
                    #
                    player.pygame_color = pygame.Color("white")
                    #add remove player functonality?
                    if player in players:
                        # print(f"Player: {player.name} end at {player.TIME_ALIVE}")
                        players.remove(player)
                elif object.outside_of_area():
                    idx += 1
                    continue
            objects.append(object)
            idx += 1
    return only_players
    
def genetic_algo(data_set):
    # data["weak_times"] = []
    # data["strong_times"] = []
    # data["weak_dead"] = 0
    # data["strong_dead"] = 0
    # data["seed"] = seed
    # data["total_weak"] = total_weak
    # data["total_strong"] = total_strong
    # data["lvl"] = lvl

    # total_lvls = len(data_set)
    # for lvl in data_set:
    #     lvl["weak_time_avg"] = sum(lvl["weak_times"]) / len(lvl["weak_times"])
    #     lvl["strong_time_avg"] = sum(lvl["strong_times"]) / len(lvl["strong_times"])
    for lvl in data_set:
        lvl.calc_stats()

    # Determine fitness
    drop_num = int(len(data_set) * 0.25) # Drop lowest 25%

    # for each in lvl_set:
    #     print(each["seed"], end=" ")

    # Fitness Function:
    data_set = sorted(data_set, key=lambda lvl: lvl.strg_time_avg - lvl.weak_time_avg)
    # data_set = sorted(data_set, key=lambda lvl: lvl["weak_dead"] - lvl["strong_dead"])
    # data_set = sorted(data_set, key=lambda lvl: lvl["strong_time_avg"])

    # Remove bottom 25%
    for _ in range(drop_num):
        data_set.pop(0)

    random.seed(TIME.time())

    lvl_set = []

    while len(lvl_set) <= len(data_set):
        lvl1 = random.choice(data_set)      # Mix randomly between "good" generations
        data_set.remove(lvl1)
        # lvl1 = data_set.pop(-1)           # Mix only strongest
        lvl2 = random.choice(data_set)
        while lvl2 == lvl1:
            lvl2 = random.choice(data_set)
        data_set.append(lvl1)
        # lvl1 = lvl1["lvl"]
        # lvl2 = lvl2["lvl"]
        cross_lvl = lvl1.crossover(lvl2)
        # cross_lvl = crossover(lvl1, lvl2)
        lvl_set.append(cross_lvl)

    # print("\n")
    # for each in lvl_set:
    #     print(each["seed"], end=" ")
    # print("\n")

    # Crossover

    # Mutation

    return lvl_set



def main():
    data_set = []
    queue = multiprocessing.Queue()
    processes = []

    data_graph = Graph()
    total_ratio_weak = []
    total_ratio_strg = []
    turn = 0

    for _ in range(4):
        process = multiprocessing.Process(target=play_lvl, args=(queue,))
        process.start()
        processes.append(process)
        # TIME.sleep(1)
    # TIME.sleep(1)
    goal = False
    while goal == False:
        # print("HERE?")
        running_procs = False
        for process in processes[::]:
            if process.is_alive():
                running_procs = True
            else:
                if process in processes:
                    processes.remove(process)

        # GET from queue
        try:
            data = queue.get_nowait()
            data_set.append(data)
            # print(data)

            # for key in data.keys():
            #     temp = ""
            #     if key != "lvl":
            #         temp += f"{key} : {data[key]} "
            #     print(temp)
            
            # Ratio of "Alive:Total"
            # ratio_weak = (data["total_weak"] - data["weak_dead"])/data["total_weak"]
            # ratio_strong = (data["total_strong"] - data["strong_dead"])/data["total_strong"]

            ratio_weak = (data.total_weak - data.weak_dead) / data.total_weak
            ratio_strg = (data.total_strg - data.strg_dead) / data.total_strg

            total_ratio_strg.append(ratio_strg)
            total_ratio_weak.append(ratio_weak)

            data_graph.update(turn, total_ratio_weak, total_ratio_strg)

            print(f"Weak stats: {ratio_weak}, Strong stats: {ratio_strg}")

            # FIXME: Need to save all results to some JSON file.
        except:
            pass

        
        if running_procs == False:

            data_graph.update(turn, total_ratio_weak, total_ratio_strg)
            turn += 1

            lvl_set = genetic_algo(data_set)
            data_set.clear()
            # break
            for lvl in lvl_set:
                process = multiprocessing.Process(target=play_lvl, args=(queue,lvl))
                process.start()
                processes.append(process)
            pass


    

# just organizational things.
if __name__ == "__main__":
    main()
