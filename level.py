import time as TIME
import random
from entity import Spawner

class Level:
    # NOTE: Stagnation avoidance tactics
    # Dynamic Mutation Rate
    # Novelty Search
    # Age-based replacement
    # Re-seeding (If no improvement for N generations.)

    def __init__(self, lvl=dict()):
        self.seed = None # Seed based on current time? 
        self.tested = False # Is this level tested?
        self.dict = lvl # Dictionary containing level data
        
        # Log surivival time of weak and strong players
        self.weak_times = []
        self.strg_times = []

        # Log how many collided + how many in total
        self.total_weak = 0
        self.total_strg = 0
        self.weak_dead = 0
        self.strg_dead = 0

        # Stats
        self.weak_time_avg = 0
        self.strg_time_avg = 0

        self.length = 1000

    def calc_stats(self):
        # Sets the avg + other stats if necessary
        self.weak_time_avg = sum(self.weak_times) / self.total_weak
        self.strg_time_avg = sum(self.strg_times) / self.total_strg

    def generate(self, SCREEN_WIDTH=384):
        self.seed = TIME.time() # Set random seed
        random.seed(self.seed)

        for t in range(0, self.length+1):
            if random.random() >= 0.85: # 0.85
                x = random.randint(0, SCREEN_WIDTH)
                bullet_spawner = Spawner(x, 0, 16, 16)

                bullet_spawner.num_bullets = random.randint(1, 8)
                bullet_spawner.bullet_speed = random.uniform(0.5, 2)
                self.dict[t] = bullet_spawner

    def crossover(self, othr, length=1000):
        random.seed(TIME.time())
        cross_lvl = dict()

        ownr_keys = list(self.dict.keys())
        othr_keys = list(othr.dict.keys())

        while len(ownr_keys) > 0 and len(othr_keys) > 0:
            key = None
            ref = self
            if len(ownr_keys) > 0:
                key = random.choice(ownr_keys)
                ownr_keys.remove(key)
                ref = self
            elif len(othr_keys) > 0:
                key = random.choice(othr_keys)
                othr_keys.remove(key)
                ref = othr
            
            if key == None:
                continue
            elif key in ownr_keys or key in othr_keys:
                if random.random() >= 0.5:
                    cross_lvl[key] = self.dict[key]
                else:
                    cross_lvl[key] = othr.dict[key]
            else:
                if random.random() >= 0.5:
                    cross_lvl[key] = ref.dict[key]
            


        return Level(cross_lvl)

        # for t in range(0, length+1):
        #     obj1 = None
        #     if t in self.dict.keys():
        #         obj1 = self.dict[t]
        #     obj2 = None
        #     if t in othr.dict.keys():
        #         obj1 = othr.dict[t]
            
        #     if obj1 == None and obj2 == None:
        #         continue
        #     else:
        #         if random.random() >= 0.5:
        #             if obj1 != None:
        #                 cross_lvl[t] = obj1
        #         else:
        #             if obj2 != None:
        #                 cross_lvl[t] = obj2
        
        # return Level(cross_lvl) # Return new level with crossed over data