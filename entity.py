import math
from graphics import *
import sys, os, pygame, re, random
import numpy as np
from copy import copy, deepcopy


# Entity includes the Player + Projectiles (Keep it simple)
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

        # Rect used for graphics.py rendering
        self.rect = Rectangle(
            Point(self.x1, self.y1), Point(self.x2, self.y2)
        )  # allows for drawing

        # Pygame rect: https://www.pygame.org/docs/ref/rect.html
        # Pygame.rect(left, top, width, height)
        self.pygame_rect = pygame.Rect(self.x1, self.y1, self.width, self.height)

        self.drawn = False

        # self.rect.setFill("red")
        if self.name == "player":  # set colors differently for players and bullets.
            self.rect.setFill("blue")
            self.pygame_color = pygame.Color("blue")
        else:
            self.rect.setFill("red")
            self.pygame_color = pygame.Color("red")
        # self.rect.draw(window)
        self.move_list = []  # cool ability to rewind!

    def draw_to(self, win):
        # print(self.name)
        # self.rect.draw(win)
        if self.drawn == False:
            self.rect.draw(win)
            self.drawn = True

    def aabb(self, other):
        # Circular instead of AABB
        # Maybe should add radius component?
        # print("WTF", math.sqrt(math.pow(self.x-other.x, 2) + math.pow(self.y-other.y, 2)))
        if (
            math.sqrt(math.pow(self.x - other.x, 2) + math.pow(self.y - other.y, 2))
            < self.height
        ):  # FIXME: circular distance isn't working
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
        # add functionality for rewinding
        if rewind == False:
            self.move_list.append((dx, dy))  # add to move list if not rewinding
        else:
            if self.move_list != []:  # if not empty
                dx, dy = self.move_list.pop(-1)  # pop end
                # reverse the movement
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
        # Move visual representation (graphics.py)
        self.rect.move(dx, dy)
        # print(dx, dy)

        # NOTE:  Below is strange. Because values being set aren't integers, the rendering is having trouble showing the results
        #       Possibly could lead to results where what is shown and said by the computer is different, which is bad. Just keep the float-integer issue in mind.
        self.pygame_rect.update((self.x1, self.y1), (self.width, self.height))
        # Because the movements (for the bullets) aren't just integers, the regular move_ip (move in-place) doesn't function properly with Pygame's renderer.
        # Most likely something to do with pixel coordinates?
        # self.pygame_rect.move_ip(dx, dy)

    def outside_of_area(self, height=448, width=384):
        if abs(height/2 - self.x) > height/2 + 100:
            return True
        if abs(width/2 - self.y) > width/2 + 100:
            return True
        return False

    
    """Simulates collision detection for future steps"""
    #args:
    #t -> steps
    #other -> the other type(Entity) to compare against
    def check_steps_ahead(self, t, other, velocity):
        
        potential_x, potential_y = velocity

        #if too far away from each other and will never meet anyways
        #then don't bother for-looping this
        if (abs(self.x-other.x) > (potential_x-other.velocity_x)*t and abs(self.y-other.y) > (potential_y-other.velocity_y)*t ):
            # print("instant return")
            return t

        #Create duplicate objects that are the same but just simulated ahead
        # self_copy = deepcopy(self)
        # other_copy = deepcopy(other)
        self_copy = collision_checker(self.x, self.y, self.height, self.width, potential_x, potential_y)
        other_copy = collision_checker(other.x, other.y, other.height, other.width, other.velocity_x, other.velocity_y)

        #simulate these copies for t-steps
        for t_ in range(t):
            #Move player and other by their velocity
            self_copy.movement(potential_x, potential_y)
            other_copy.movement(other_copy.velocity_x, other_copy.velocity_y)
            #Check to see if they collide
            # print(t_)

            # if going outside of area
            # if other.name == "player" and \
            #     (other.x >= 384 or other.x <= 0 or \
            #     other.y >= 448 or other.y <= 0):
            #     return t_-1
            if (self_copy.x > 384 or self_copy.x < 0 or \
                self_copy.y > 448 or self_copy.y < 0):
                return t_-1
            
            # if collision detected this frame
            if self_copy.aabb(other_copy) == True:
                # print("RETURN -1")
                return t_-1
        
        return t

    def rewind(self):
        self.movement(0, 0, rewind=True)  # rewind
        if len(self.move_list) == 0:
            return True

    def execute_command(self):
        pass

    def position(self):
        # if self.name == "player":
        #     print("PLAYER MOVE", [self.x, self.y])
        return [self.x, self.y]

#Potentially might be a good idea to separate collision component into separate object.
#This will just make checking future steps ahead easier.
class collision_checker:
    def __init__(self, x, y, height, width, velocity_x, velocity_y):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.x1 = x - width / 2
        self.x2 = x + width / 2
        self.y1 = y - height / 2
        self.y2 = y + height / 2
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def movement(self, dx, dy):
        # Move position (center)
        self.x += dx
        self.y += dy
        # Adjust collision boxes
        self.x1 = self.x - self.width / 2
        self.x2 = self.x + self.width / 2
        self.y1 = self.y - self.height / 2
        self.y2 = self.y + self.height / 2

    def aabb(self, other):
        # Circular instead of AABB
        # Maybe should add radius component?
        # print("WTF", math.sqrt(math.pow(self.x-other.x, 2) + math.pow(self.y-other.y, 2)))
        # print("AABB VALUE", math.sqrt(math.pow(self.x - other.x, 2.0) + math.pow(self.y - other.y, 2.0)), self.height)
        if (
            math.sqrt(math.pow(self.x - other.x, 2.0) + math.pow(self.y - other.y, 2.0))
            < self.height
        ):  # FIXME: circular distance isn't working
            # print(f"Collision between {self.name} and {other.name}")
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
        #     # print(f"Collision between {self.name} and {other.name}")
        #     return True
        # return False


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
        # list of spawned bullets
        spawned_bullets = []
        for i in range(num_bullets):
            # Calculate angle in radians
            angle = math.radians(i * angle_step)
            # Calculate the velocity components for the bullet in the x and y directions
            bullet_velocity_x = math.cos(angle) * speed
            bullet_velocity_y = math.sin(angle) * speed
            # Create a bullet entity at the center (self.x, self.y) with initial velocity
            bullet = Entity(
                "Bullet", self.x, self.y, self.width, self.height, color="blue"
            )  # Simple bullet size (5x5)
            bullet.velocity_x = bullet_velocity_x
            bullet.velocity_y = bullet_velocity_y
            # self.bullets.append(bullet)
            spawned_bullets.append(bullet)
            # print(
            #     f"Bullet spawned at angle {i * angle_step}° with velocity ({bullet_velocity_x}, {bullet_velocity_y})"
            # )
        return spawned_bullets

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
        # add functionality for rewinding
        if rewind == False:
            self.move_list.append((dx, dy))  # add to move list if not rewinding
        else:
            if self.move_list != []:  # if not empty
                dx, dy = self.move_list.pop(-1)  # pop end
                # reverse the movement
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
        self.movement(0, 0, rewind=True)  # rewind

    def execute_command(self):
        pass


class VisualElement:
    def __init__(self, name, x, y, height, width, color="yellow"):
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

        # Rect used for graphics.py rendering
        self.rect = Rectangle(
            Point(self.x1, self.y1), Point(self.x2, self.y2)
        )  # allows for drawing

        # Pygame rect: https://www.pygame.org/docs/ref/rect.html
        # Pygame.rect(left, top, width, height)
        self.pygame_rect = pygame.Rect(self.x1, self.y1, self.width, self.height)

        self.drawn = False

        
        self.rect.setFill(color)
        self.pygame_color = pygame.Color(color)
        
        
        # self.rect.draw(window)
        self.move_list = []  # cool ability to rewind!

    def draw_to(self, win):
        # print(self.name)
        # self.rect.draw(win)
        if self.drawn == False:
            self.rect.draw(win)
            self.drawn = True