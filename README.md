# Bullet Hell Visualizer

Simulation Environment for creating *Conditionally Solvable Bullet Hell Levels*.


A simulation environment for a bullet hell game, so as to facilitate the generation of *conditionally solvable video game levels*.

Included components include a renderer, human input control, and basic collision detection.

## Quick Introduction

The Bullet Hell Visualizer project aims to create conditionally solvable levels for 'Bullet Hell' games, which are a subset of the Shoot'em Up (shmup) genre. Sets of levels are generated according to a genetic algorithm, then these generated levels are tested with "strong" and "weak" players.
- "Strong" players: Have 9 directions of movement.
- "Weak" players: Have 5 directions of movement.
The aim here is *conditionality*, that is, strong players should eventually be able to beat generated levels, while weak players cannot.

### Prerequisites

- **Python 3.8** or higher
- **Pygame**
- **graphics.py**
- **numpy**
- **scipy**
- **matplotlib**

### Running

Run the file **main.py** with **python main.py**.

### Usage



### Examples

## Structure

The Bullet Hell Visualizer's code is broken into components:
1. Evaluator
Levels are evaluated using a player model created based on strategies used by Bullet Hell gamers. There are many possible strategies that could have been chosen, however, only two are used here:
- Micrododging
“Micrododging” is a bullet hell concept that refers to a strategy where a player is [“precisely weaving your way through enemy projectiles, focusing on a small portion of the screen and threading yourself through the small openings in the pattern with delicate, subtle movements”](https://www.google.com/url?q=https://shmups.wiki/library/Help:Glossary%23Micrododging.2FMacrododging&sa=D&source=docs&ust=1756270386557237&usg=AOvVaw2KQ1ajQots4WoOJirbN4aP)
This strategy is implemented in this project through a greedy search algorithm called the ["Constrained Velocity Obstacle Algorithm"](https://github.com/Netdex/twinject?tab=readme-ov-file#constrained-velocity-obstacle-algorithm) or CVOA, a coin termed by Netdex (as far as I am aware) and used for the Touhou bot [Twinject](https://github.com/Netdex/twinject?tab=readme-ov-file).

- Macrododging
“Macrododging” is a bullet hell concept referring to a strategy where a player focuses [“on the entire screen in order to find larger openings or blind spots that allow them to avoid the bullet pattern entirely with large quick movements”](https://www.google.com/url?q=https://shmups.wiki/library/Help:Glossary%23Micrododging.2FMacrododging&sa=D&source=docs&ust=1756270386557237&usg=AOvVaw2KQ1ajQots4WoOJirbN4aP)
This strategy is implemented in this project through using a K-means clustering algorithm. How it works is that the algorithm first divides the screen into grid cells. Each grid cell is then checked to see if a bullet occupies it. Finally, the K-means clustering is run on all empty grid cell locations. Ideally, this will allow the returned cluster centers to point towards patterns of empty space, which are desirable goal positions our player should move towards, at least according to the macrododging strategy.

These two strategies, Micrododging and Macrododging are then combined into one cohesive player model by doing the following:
>The player goes through each best move. It checks the distance of the closest cluster center, given the player had performed that best move.
>If a given move has the smallest distance to a cluster center, then choose that move.
>If several different moves share the smallest distance, then randomly choose a move from the set of moves with the smallest distance.
To make our final player model.

2. Generator
Via the use of a genetic algorithm, levels are genereated


## Contributing

## License