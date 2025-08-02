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
        self.ratio_weak_alive = 0
        self.ratio_strg_alive = 0
        self.bad_ratio = 0

        # Log how many collided + how many in total
        self.total_weak = 0
        self.total_strg = 0
        self.weak_dead = 0
        self.strg_dead = 0

        # Stats
        self.weak_time_avg = 0
        self.strg_time_avg = 0

        self.length = 1000

        self.spawner_cnt = 0

    def calc_stats(self):
        # Sets the avg + other stats if necessary
        self.weak_time_avg = sum(self.weak_times) / self.total_weak
        self.strg_time_avg = sum(self.strg_times) / self.total_strg

        # Calculate ratio of weak to strong dead/alive
        self.ratio_weak_alive = (self.total_weak - self.weak_dead) / self.total_weak
        self.ratio_strg_alive = (self.total_strg - self.strg_dead) / self.total_strg

        # Calculate replacement ratio
        if self.ratio_weak_alive > self.ratio_strg_alive:
            self.bad_ratio = 1.0
        else:
            self.bad_ratio = self.ratio_weak_alive

    def generate(self, SCREEN_WIDTH=384):
        self.seed = TIME.time() # Set random seed
        random.seed(self.seed)

        for t in range(0, self.length+1):
            if random.random() >= 0.85: # 0.85
                self.spawner_cnt += 1
                x = random.randint(0, SCREEN_WIDTH)
                bullet_spawner = Spawner(x, 0, 16, 16)

                bullet_spawner.num_bullets = random.randint(1, 8)
                bullet_spawner.bullet_speed = random.uniform(0.5, 2)
                self.dict[t] = bullet_spawner

    def mutate(self):
        # Mutation
        # Changes that can be made during mutation:
        # 1. Add/Remove spawner entries
        #   Do this by obtaining some "ideal" spawner count, and comparing the current level's spawner count to it
        #   from the difference between this level's spawner count and the ideal count, randomly pick some integer
        #   if value is negative, then remove that amount of spawners from the level
        #   else, then add that amount of spawners to the level
        # 2. Change values in spawner entry
        #   Depending on the fitness of this level, tweak values of randomly selected spawner entries.
        pass

        self.calc_stats()

        # raise NotImplementedError

    def selection(self):
        raise NotImplementedError

    def crossover(self, othr, length=1000):
        random.seed(TIME.time())
        cross_lvl = dict()
        spawner_cnt = 0
        target_cnt = (self.spawner_cnt + othr.spawner_cnt) / 2

        ownr_keys = list(self.dict.keys())
        othr_keys = list(othr.dict.keys())

        while len(ownr_keys) > 0 and len(othr_keys) > 0:
            key = None
            ref = self
            # Obtain a key from a level.
            # It should be randomly picked (to avoid frontloading levels by going through it chronologically.)
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
            elif key in ownr_keys or key in othr_keys: # key existed in both levels.
                spawner_cnt += 1
                if random.random() >= 0.5: # randomly choose a spawner from a level
                    cross_lvl[key] = self.dict[key]
                else:
                    cross_lvl[key] = othr.dict[key]
            else:
                # If for this "key" there is no equivalent then:
                # Randomly decide if this entry will be added to crossover child
                # The percent chance is determined by the amount of spawners already added vs the avg between two levels being crossovered
                # Additionally this value is adjusted more (the max the value can be is 0.95), this leaves 5% chnace for addition, allowing
                # the algorithm to explore a little.
                if random.random() >= (spawner_cnt / target_cnt) * 0.95:
                    spawner_cnt += 1
                    cross_lvl[key] = ref.dict[key]
            

        lvl = Level(cross_lvl)
        lvl.spawner_cnt = spawner_cnt
        return lvl

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