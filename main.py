import math
from graphics import * #very basic graphics API #NOTE: Remember to do "pip install graphics.py"
#graphics.py documentation: https://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf

import sys, os, pygame, re, random
import numpy as np
from copy import copy, deepcopy
from entity import Entity


#GLOBALS
SCREEN_HEIGHT = 448 #These are just the Touhou numbers adapted directly
SCREEN_WIDTH = 384
window = GraphWin("Bullet-hell Simulation", SCREEN_WIDTH, SCREEN_HEIGHT);

#Current Goal: Decouple rendering and input from base game logic.
#Make it so that the final rendering part is a separate modular component.



# This spawns bullet -- for now just have a very simple spawning pattern
class Spawner:
    def __init__(self, x, y, width=5, height=5):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bullets = []  # List to hold all the bullets
        
    def spawn_circular_bullets(self, num_bullets, speed):
        angle_step = 360 / num_bullets
        for i in range(num_bullets):
            # Calculate angle in radians
            angle = math.radians(i * angle_step)
            # Calculate the velocity components for the bullet in the x and y directions
            bullet_velocity_x = math.cos(angle) * speed
            bullet_velocity_y = math.sin(angle) * speed
            # Create a bullet entity at the center (self.x, self.y) with initial velocity
            bullet = Entity("Bullet", self.x, self.y, self.width, self.height, color="blue")  # Simple bullet size (5x5)
            bullet.velocity_x = bullet_velocity_x
            bullet.velocity_y = bullet_velocity_y
            self.bullets.append(bullet)
            print(f"Bullet spawned at angle {i * angle_step}° with velocity ({bullet_velocity_x}, {bullet_velocity_y})")

    def update(self, rewind=False):
        # Update each bullet's position based on its velocity
        if rewind == False:
            for bullet in self.bullets:
                bullet.movement(bullet.velocity_x, bullet.velocity_y)
        else:
            for bullet in self.bullets:
                bullet.rewind()

    def spawner_detect_collision(self, other):
        # Check colision for each bullet
        for bullet in self.bullets:
            bullet.aabb(other)

    def movement(self, dx, dy, rewind=False):
        #add functionality for rewinding
        if rewind == False:
            self.move_list.append((dx, dy)) #add to move list if not rewinding
        else:
            if self.move_list != []: #if not empty
                dx, dy = self.move_list.pop(-1) #pop end
                #reverse the movement
                dx = -dx
                dy = -dy
            else:
                dx, dy = (0, 0)

        # Move position (center)
        self.x += dx
        self.y += dy
        # Adjust collision boxes
        self.x1 = self.x - self.width / 2
        self.x2 = self.x + self.width / 2
        self.y1 = self.y - self.height / 2
        self.y2 = self.y + self.height / 2
        # Move visual representation
        self.rect.move(dx, dy)

    def rewind(self):
        self.movement(0, 0, rewind=True) #rewind

    def execute_command(self):
        pass


def parse_input(CMD_INPUT, Player):
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


def render(objects):
    #rendering loop for all objects
    #should change depending on current modules used
    pass

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

def game_collision(player, objects):
    #collision detection for objects in the game
    pass


def main():
    #Make some method of visual output (not sure on this...)
    CMD_INPUT = ""

    # Example of how to use the Spawner to spawn circular bullets
    player_x = SCREEN_WIDTH / 2
    player_y = SCREEN_HEIGHT / 2
    # bullet_spawner = Spawner(player_x, player_y)
    bullet_spawner = Spawner(0, 0, 16, 16)

    # Example commands
    bullet_spawner.spawn_circular_bullets(8, 1)  # Spawn 8 bullets at the spawner position, with speed of 2 units
    bullet_spawner.update()  # Update all bullets' positions

    game_objects = [] #checking all game objects

    Player = Entity("player", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 16, 16)

    game_objects.append(Player)
    game_objects.append(bullet_spawner)

    REWIND = False

    TICKS = 20

    while CMD_INPUT != "END":
        REWIND = False
        CMD_INPUT = input("ENTER COMMAND HERE: ")  # accept input until stop
        
        command_dict = parse_input(CMD_INPUT, Player)
        REWIND = command_dict["REWIND"]
        if command_dict["TICKS"] != None:
            TICKS = command_dict["TICKS"]
            continue #restart with new tick rate

        #for tick in ticks: #simulate command for certain amount of ticks
        for tick in range(TICKS):
            for game_object in game_objects:
                if type(game_object) is Entity:
                    #Draw the Entity
                    game_object.draw(window)
                    #Simulate movement
                    if game_object != Player:
                        if REWIND == False: #Check if rewinding
                            game_object.movement(self.velocity_x, self.velocity_y)
                        else:
                            game_object.rewind()
                    else: #move player
                        if REWIND == False:
                            dx, dy = command_dict["PLAYER_MOVEMENT"]
                            game_object.movement(dx, dy)
                        else:
                            game_object.rewind()
                elif type(game_object) is Spawner: #if spawner
                    if REWIND == False: #if rewinding
                        game_object.update()  # Update all bullets on each command
                    else:
                        game_object.update(rewind=True)  # Update all bullets on each command (and rewind simulation)

            #Simluate collision
            for game_object in game_objects: 
                if game_object != Player:
                    if type(game_object) is Entity:
                        #simulate collision
                        game_object.aabb(Player)
                    elif type(game_object) is Spawner:
                        #simulate collision with all bullets of spawner
                        game_object.spawner_detect_collision(Player)

#just organizational things.
if __name__ == '__main__':
    main()