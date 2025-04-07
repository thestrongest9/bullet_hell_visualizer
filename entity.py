import math
from graphics import *
import sys, os, pygame, re, random
import numpy as np
from copy import copy, deepcopy

#Entity includes the Player + Projectiles (Keep it simple)
class Entity:
    def __init__(self, name, x, y, height, width, color="red"):
        self.name = name
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.x1 = x - width / 2
        self.x2 = x + width / 2
        self.y1 = y - height / 2
        self.y2 = y + height / 2
        self.velocity_x = 0
        self.velocity_y = 0
        self.rect = Rectangle(Point(self.x1, self.y1), Point(self.x2, self.y2)) #allows for drawing
        
        self.drawn = False
        
        # self.rect.setFill("red")
        if self.name == "player": #set colors differently for players and bullets.
            self.rect.setFill("blue")
        else:
            self.rect.setFill("red")
        # self.rect.draw(window)
        self.move_list = [] #cool ability to rewind!

    def draw_to(self, win):
        print(self.name)
        # self.rect.draw(win)
        if self.drawn == False:
            self.rect.draw(win)
            self.drawn = True

    def aabb(self, other):

        #Circular instead of AABB
        #Maybe should add radius component?
        # print("WTF", math.sqrt(math.pow(self.x-other.x, 2) + math.pow(self.y-other.y, 2)))
        if math.sqrt(math.pow(self.x-other.x, 2) + math.pow(self.y-other.y, 2)) < self.height: #FIXME: circular distance isn't working
            print(f"Collision between {self.name} and {other.name}")
            return True
        else:
            return False


        # # Ensure both objects have the necessary attributes (bounding box coordinates)
        # if not all(hasattr(other, attr) for attr in ['x1', 'y1', 'x2', 'y2']):
        #     return None  # `other` doesn't have the necessary attributes for collision detection
        
        # # Check if there's an overlap on both the X and Y axes (AABB collision detection)
        # if (self.x2 >= other.x1 and self.x1 <= other.x2 and
        #     self.y2 >= other.y1 and self.y1 <= other.y2):
        #     # Collision detected
        #     print(f"Collision between {self.name} and {other.name}")
        #     return True
        # return False


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