import math
from graphics import *  # very basic graphics API #NOTE: Remember to do "pip install graphics.py"
# graphics.py documentation: https://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf

import sys, os, pygame, re, random
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Suppress Pygame init message
import numpy as np
from copy import copy, deepcopy

from scipy.spatial import KDTree
from scipy.cluster.vq import kmeans

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
grid_tree = None

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
    global grid_tree
    global grid_points
    xmin, xmax = SCREEN_WIDTH, 0
    ymin, ymax = SCREEN_HEIGHT, 0
    if grid_points == []:
        for i in range(grid_resolution):
            x = xmin + i * (xmax - xmin) / (grid_resolution - 1)
            for j in range(grid_resolution):
                y = ymin + j * (ymax - ymin) / (grid_resolution - 1)
                grid_points.append((x, y))
        grid_tree = KDTree(grid_points)
        # print("Grid creation should fire only once.")
        creating_grid = True

    # filter objects to exclude "Player" type objects so that player positions will not effect output
    vals = [(object.x,object.y) for object in objects if type(object) == Entity and object.type != "Player"]

    object_tree = None
    result = []
    if (len(vals) == 0): #if this is empty then the screen has no bullets left on it.
        # If there are no bullets (i.e. other collidable objs), then just return centroids based on grid
        centroids, _ = kmeans(grid_points, 9)
        return centroids
    else:
        object_tree = KDTree(vals)

    check_radius = player.height #64 16

    helpers.clear() #clear list
    low_cnt = float('inf')
    # Get grid point with lowest value (ideally this would be 0)
    # Collect grid points with that same low value and return that as result
    # The reason for doing it this way is that sometimes ALL the grid points have bullets near them
    # So only checking for len() == 0 would cause an error.
    for grid_point in grid_points:
        obj_cnt = len(object_tree.query_ball_point(grid_point, r=check_radius*2))
        x, y = grid_point
        if obj_cnt < low_cnt:
            helpers.clear()
            result.clear()
            temp = VisualElement("Grid Tile", x, y, 10, 10)
            temp.pygame_color = pygame.Color(125, 125, 255, 100)
            helpers.append(temp)
            result.append(grid_point)
            low_cnt = obj_cnt
        elif obj_cnt == low_cnt:
            temp = VisualElement("Grid Tile", x, y, 10, 10)
            temp.pygame_color = pygame.Color(125, 125, 255, 100)
            helpers.append(temp)
            result.append(grid_point)

    centers = 9
    if len(result) < centers:
        centers = len(result)
    centroids, _ = kmeans(result, centers)
    # centroids = []
    # distortion_val = float('inf')
    # for num in range(1, 10):
    #     temp, distortion = kmeans(result, num)
    #     if distortion_val > distortion:
    #         centroids = temp
    #         distortion_val = distortion

    for grid_point in centroids:
        x, y = grid_point
        helpers.append(VisualElement("Center", x, y, 10, 10))

    return centroids

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
        ( 0,  1), #down
        (-1,  0), #left
        ( 1,  0), #right
        (-1, -1), #upleft
        ( 1, -1), #upright
        (-1,  1), #downleft
        ( 1,  1), #downright
    ]

    if player.strength == "weak":
        possible_velocities = [
            ( 0 * multiplier,  0 * multiplier), #stand still
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
            # (-1, -1), #upleft
            # ( 1, -1), #upright
            # (-1,  1), #downleft
            # ( 1,  1), #downright
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

    # suboptimal_move_chance = 0.05 if player.strength == "strong" else 0.5

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
        
        dist = float('inf')
        dirs = []
        for key, value in direction_scores.items():
            if value < dist:
                dirs.clear()
                dirs.append(key)
                dist = value
            elif value == dist:
                # print("SAME DIST?")
                dirs.append(key)
        
        max_t_velocity = random.choice(dirs)
        # max_t_velocity = min(direction_scores, key=direction_scores.get)
        # print("direction_scores", direction_scores, max_t_velocity)

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

        # Spawn bullets
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
        lvl.calc_stats()
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
    elite_num = int(len(data_set) * 0.25) # Save top 25% as elites
    elites = []
    lvl_set = []
    set_size = len(data_set)
    # print("set size: ", set_size)

    # for each in lvl_set:
    #     print(each["seed"], end=" ")

    # Fitness Function:
    data_set = sorted(data_set, key=lambda lvl: lvl.strg_time_avg - lvl.weak_time_avg)
    # data_set = sorted(data_set, key=lambda lvl: lvl["weak_dead"] - lvl["strong_dead"])
    # data_set = sorted(data_set, key=lambda lvl: lvl["strong_time_avg"])

    # Remove bottom 25%
    for _ in range(drop_num):
        data_set.pop(0)

    for _ in range(elite_num):
        elite = data_set.pop()
        lvl_set.append(elite)
        elites.append(elite)

    random.seed(TIME.time())

    # 25% -> Elites
    # 75% -> Elite crossovers + Mutated level + New levels

    print("set size: ", set_size)

    # 1. Crossover
    if len(data_set) == 0 or len(elites) == 0:
        raise IndexError
    else:
        while len(lvl_set) < set_size:
            lvl = random.choice(data_set)
            if random.random() >= lvl.bad_ratio: # Determine via repalacement ratio
                # 1. Crossover
                # Crossover level with randomly chosen elite
                elite = random.choice(elites)
                cross_lvl = elite.crossover(lvl)
                lvl_set.append(cross_lvl)
            else:
                elite = random.choice(elites)
                if random.random() >= 0.5:
                    # 2. Mutation
                    lvl = elite.mutate(50)
                else:
                    # 3. Generation
                    # Create new Level
                    lvl = Level()
                    lvl.generate()
                    lvl_set.append(lvl)

    return lvl_set



def main():
    data_set = []
    queue = multiprocessing.Queue()
    processes = []
    running_processes = []
    
    levels_per_iteration = 8    # Number of levels per iteration
    num_run_procs = 4           # Max number of levels being simultaneously at any time

    data_graph = Graph()
    total_ratio_weak = []
    total_ratio_strg = []

    alive_time_graph = Graph()
    total_time_strg = []
    total_time_weak = []

    iteration = 0

    for _ in range(levels_per_iteration):
        process = multiprocessing.Process(target=play_lvl, args=(queue,))
        # process.start()
        processes.append(process)
        # TIME.sleep(1)
    # TIME.sleep(1)
    goal = False
    while goal == False:
        # print("HERE?")

        # Start new processes if capacity exists.
        running_procs = False
        if len(processes) > 0 or len(running_processes) > 0:
            running_procs = True
            if len(running_processes) < num_run_procs and len(processes) > 0:
                process = processes.pop()
                process.start()
                running_processes.append(process)

        #     if len(running_processes) > 0:
        #         process = running_processes.pop(0)
        #         if process.is_alive():
        #             running_processes.append(process)
        # elif len(processes) == 0 and len(running_processes) == 0: #NOTE: In practice this should never happen
        #     print("ERROR: Both processes and running processes empty?")
        #     break;

        # Check running processes.
        still_running = []
        for process in running_processes:
            if process.is_alive():
                still_running.append(process) # This process is still working.
            else:
                process.join(timeout=0.1) # Cleanup finishes process otherwise.
        running_processes = still_running # Preserve processes that are still alive.

        # GET from queue
        try:
            data = queue.get_nowait()
            data_set.append(data)

            ratio_weak = (data.total_weak - data.weak_dead) / data.total_weak
            ratio_strg = (data.total_strg - data.strg_dead) / data.total_strg

            total_ratio_strg.append(ratio_strg)
            total_ratio_weak.append(ratio_weak)

            data_graph.update(iteration, total_ratio_weak, total_ratio_strg)

            total_time_strg.append(data.strg_time_avg)
            total_time_weak.append(data.weak_time_avg)
            # print("TOTAL TIME STRG: ", total_time_strg)

            alive_time_graph.update(iteration, total_time_weak, total_time_strg)

            print(f"Weak stats: {ratio_weak}, Strong stats: {ratio_strg}")

            # FIXME: Need to save all results to some JSON file.
        except:
            if len(running_processes) == 0:
                print("ERROR: Nothing returned, nothing running")
            pass

        
        if running_procs == False:
            data_graph.update(iteration, total_ratio_weak, total_ratio_strg)
            alive_time_graph.update(iteration, total_time_weak, total_time_strg)
            iteration += 1

            # Reset round graphs
            total_ratio_strg = []
            total_ratio_weak = []

            total_time_strg = []
            total_time_weak = []

            lvl_set = genetic_algo(data_set)
            data_set.clear()
            # break
            for lvl in lvl_set:
                if lvl.tested == False:
                    process = multiprocessing.Process(target=play_lvl, args=(queue,lvl))
                    # process.start()
                    processes.append(process)
                else:
                    total_ratio_strg.append(lvl.ratio_strg_alive)
                    total_ratio_weak.append(lvl.ratio_weak_alive)
                    total_time_strg.append(lvl.strg_time_avg)
                    total_time_weak.append(lvl.weak_time_avg)

                    data_set.append(lvl)


    

# just organizational things.
if __name__ == "__main__":
    main()
