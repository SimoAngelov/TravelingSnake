#!/usr/bin/env python3

from game import SnakeGame
import arcade
import snake
from move_algo import Algo

SCREEN_TITLE = "Traveling Snake"

# Configuration parameters
NODE_SIZE = 30  # size of a node square in pixels
NODE_SHAPE = [16, 16]  # HxW - number of nodes in the height and width dimensions
FPS = 120  # application framerate
ALGO = Algo.TAKE_SHORTCUTS  # algorithm type the snake should follow, Algo.NONE means normal gameplay
SEED = 7  # seed for rng
IS_SHOW_PATH = False  # whether to show the hamilton path in a grid
IS_PAUSE_UPDATE = False  # whether to pause the update loop
IS_DRAW_FLAT_PATH = False  # whether to display the flat hamiltonian path below the grid

SIM_MODE = False  # run simulation using the provided parameters
SIM_PARAMS = {
    "seed_count": 10,
    "games_per_seed": 10,
    "node_shapes": [[6, 6], [17, 14]]
}

def main():
    """ Main function """
    if not SIM_MODE:
        snake_game = SnakeGame(SCREEN_TITLE, FPS, NODE_SHAPE, NODE_SIZE, ALGO, SEED, IS_SHOW_PATH,
                               IS_PAUSE_UPDATE, IS_DRAW_FLAT_PATH)
        snake_game.setup()
        arcade.run()
    else:
        snake.run_simulation(SIM_PARAMS, 'data/simulation.json')


if __name__ == "__main__":
    main()
