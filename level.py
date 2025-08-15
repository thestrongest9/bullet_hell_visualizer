import time as TIME
import random
import copy
from entity import Spawner

def clamp(val, min_val, max_val):
    if val <= min_val:
        return min_val
    elif val >= max_val:
        return max_val
    else:
        return val

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
        self.total_survival_ratio = 1

        # Log how many collided + how many in total
        self.total_weak = 0
        self.total_strg = 0
        self.weak_dead = 0
        self.strg_dead = 0

        # Stats
        self.weak_time_avg = 0
        self.strg_time_avg = 0
        # Previous values
        self.prev_weak_time_avg = None
        self.prev_strg_time_avg = None

        self.length = 1000

        self.spawner_cnt = 0

        self.SCREEN_WIDTH = 384 # Size of screen
        self.SCREEN_HEIGHT = 448

        self.level_history = []

        # Check if level has been tested
        self.tested = False

    def calc_stats(self):
        # Sets the avg + other stats if necessary
        self.weak_time_avg = sum(self.weak_times) / self.total_weak
        self.strg_time_avg = sum(self.strg_times) / self.total_strg

        # Calculate ratio of weak to strong dead/alive
        self.ratio_weak_alive = (self.total_weak - self.weak_dead) / self.total_weak
        self.ratio_strg_alive = (self.total_strg - self.strg_dead) / self.total_strg

        # Calculate total survival ratio
        self.total_survival_ratio = (self.ratio_strg_alive + self.ratio_weak_alive) / 2

    def generate(self):
        self.seed = TIME.time() # Set random seed
        random.seed(self.seed)
        self.level_history = [f"Created {self.seed}"]

        bullet_cnt = []

        previous_spawner = None

        for t in range(0, self.length+1):

            
            
            if random.random() >= 0.85: # 0.85
                self.spawner_cnt += 1
                
                if random.random() >= 0.85 or previous_spawner == None:
                    x = random.randint(0, self.SCREEN_WIDTH)
                    num_bullets = random.randint(1, 8)
                    speed = random.uniform(0.5, 2)
                else:
                    x = previous_spawner.x + random.randint(-10, 10)
                    
                    num_bullets = previous_spawner.num_bullets + random.randint(-1, 1)
                    num_bullets = clamp(num_bullets, 1, 8)

                    speed = previous_spawner.bullet_speed
                bullet_spawner = Spawner(x, 0, 16, 16)
                bullet_spawner.num_bullets = num_bullets
                bullet_spawner.bullet_speed = speed
                self.dict[t] = bullet_spawner

                previous_spawner = bullet_spawner

    def get_new_key(self):
        idx = random.randint(0, self.length)
        while idx in self.dict.keys():
            idx = random.randint(0, self.length)
        return idx

    def add_spawner(self, key=None):
        # random.seed(self.seed) # Set to same seed so that results are consistent.

        idx = 0
        if self.spawner_cnt < 1000:
            if key == None:
                idx = self.get_new_key()
            else:
                idx = key

            x = random.randint(0, self.SCREEN_WIDTH)
            bullet_spawner = Spawner(x, 0, 16, 16)
            bullet_spawner.num_bullets = random.randint(1, 8)
            bullet_spawner.bullet_speed = random.uniform(0.5, 2)
            self.spawner_cnt += 1
            self.dict[idx] = bullet_spawner

    def rmv_spawners(self):
        # key_len_before = 0
        # key_len_after = 0
        if self.spawner_cnt > 0:
            keys = list(self.dict.keys())
            # key_len_before = len(keys)
            idx = random.choice(keys)
            del self.dict[idx]
            # keys.remove(idx)
            self.spawner_cnt -= 1

        # key_len_after = len(list(self.dict.keys()))
        # print(f"KEY COUNT BEFORE: {key_len_before}, AFTER: {key_len_after}")

    def mutate(self, diff, elites, SCREEN_WIDTH=384):
        # random.seed(self.seed) # Set to same seed so that results are consistent.

        target_spawner_cnt = sum([elite.spawner_cnt for elite in elites]) / len(elites)

        # Mutation
        # Changes that can be made during mutation:
        # 1. Add/Remove spawner entries
        #   Do this by obtaining some "ideal" spawner count, and comparing the current level's spawner count to it
        #   from the difference between this level's spawner count and the ideal count, randomly pick some integer
        #   if value is negative, then remove that amount of spawners from the level
        #   else, then add that amount of spawners to the level
        # 2. Change values in spawner entry
        #   Depending on the fitness of this level, tweak values of randomly selected spawner entries.
        lvl = Level()
        lvl.dict = copy.deepcopy(self.dict)
        lvl.spawner_cnt = self.spawner_cnt
        lvl.seed = TIME.time() # Set random seed
        # Randomly get values of a range determined by diff.
        # Negative to Positve, detemrines if spawners will
        # be added or removed.
        if int(abs(self.spawner_cnt - target_spawner_cnt)) <= 1:
            val = 1
        else:
            val = random.randint(1, int(abs(self.spawner_cnt - target_spawner_cnt)))
        # val = random.randint(1, diff)

        # if self.ratio_strg_alive > self.ratio_weak_alive:
        #     pass
        # else:
        #     val *= -1
        # if random.random() >= 0.0:
        #     for _ in range(val):
        #         lvl.rmv_spawners()
        # else:
        #     for _ in range(val):
        #         lvl.add_spawner(SCREEN_WIDTH)

        if lvl.spawner_cnt > target_spawner_cnt:
            for _ in range(val):
                lvl.rmv_spawners()
        else:
            for _ in range(val):
                lvl.add_spawner(SCREEN_WIDTH)

        # temp = self.level_history[:]
        lvl.level_history = self.level_history[:]
        lvl.level_history.append(f"MUTATED {self.seed}")
        lvl.seed = TIME.time()
        lvl.prev_weak_time_avg = self.weak_time_avg
        lvl.prev_strg_time_avg = self.strg_time_avg
        # print("Mutate", temp)
        return lvl

    def selection(self):
        raise NotImplementedError
    
    def improvement(self):
        # lvl.prev_weak_time_avg = self.weak_time_avg
        # lvl.prev_strg_time_avg = self.strg_time_avg
        if self.prev_strg_time_avg == None or self.prev_weak_time_avg == None:
            return True
        diff_new = self.strg_time_avg - self.weak_time_avg
        diff_old = self.prev_strg_time_avg - self.prev_weak_time_avg
        if diff_new > diff_old:
            return True
        else:
            return False

    def crossover(self, othr, length=1000):
        # random.seed(self.seed) # Set to same seed so that results are consistent.

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

            # If for this "key" there is no equivalent then:
            # Randomly decide if this entry will be added to crossover child
            # The percent chance is determined by the amount of spawners already added vs the avg between two levels being crossovered
            # Additionally this value is adjusted more (the max the value can be is 0.95), this leaves 5% chnace for addition, allowing
            # the algorithm to explore a little.
            if random.random() >= (spawner_cnt / target_cnt) + 0.05 * random.uniform(-1, 1):
                if key == None:
                    continue
                elif key in ownr_keys or key in othr_keys: # key existed in both levels.
                    # spawner_cnt += 1
                    if random.random() >= 0.5: # randomly choose a spawner from a level
                        cross_lvl[key] = self.dict[key]
                    else:
                        cross_lvl[key] = othr.dict[key]
                else:
                    # spawner_cnt += 1
                    cross_lvl[key] = ref.dict[key]
                spawner_cnt += 1


            # if key == None:
            #     continue
            # elif key in ownr_keys or key in othr_keys: # key existed in both levels.
            #     spawner_cnt += 1
            #     if random.random() >= 0.5: # randomly choose a spawner from a level
            #         cross_lvl[key] = self.dict[key]
            #     else:
            #         cross_lvl[key] = othr.dict[key]
            # else:
            #     # If for this "key" there is no equivalent then:
            #     # Randomly decide if this entry will be added to crossover child
            #     # The percent chance is determined by the amount of spawners already added vs the avg between two levels being crossovered
            #     # Additionally this value is adjusted more (the max the value can be is 0.95), this leaves 5% chnace for addition, allowing
            #     # the algorithm to explore a little.
            #     if random.random() >= (spawner_cnt / target_cnt) * 0.95:
            #         spawner_cnt += 1
            #         cross_lvl[key] = ref.dict[key]
            

        # print(othr)
        lvl = Level(cross_lvl)
        lvl.spawner_cnt = spawner_cnt
        # Add to history of this new level
        # hist_seed = self.seed if len(self.level_history) > len(othr.level_history) else othr.seed
        lvl.level_history = self.level_history[:] if len(self.level_history) > len(othr.level_history) else othr.level_history[:]
        # temp = [f"Change in {hist_seed}" for _ in range(hist_len)]
        # lvl.level_history = [f"Change in {hist_seed}" for _ in range(hist_len)]
        lvl.level_history.append(f"CROSSOVER {self.seed} {othr.seed}")
        # print("Crossover", temp)
        # lvl.level_history = [f"CROSSOVER {self.seed} {othr.seed}"]
        lvl.seed = TIME.time()
        lvl.prev_weak_time_avg = self.weak_time_avg
        lvl.prev_strg_time_avg = self.strg_time_avg
        return lvl