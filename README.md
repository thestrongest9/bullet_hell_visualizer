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
- Macrododging


1. Generator
Via the use of a genetic algorithm, levels are genereated

2. Evaluator

## Contributing

## License