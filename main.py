#!/usr/bin/env python3

from game import SnakeGame
import arcade
import numpy as np

SCREEN_TITLE = "Traveling Snake"

NODE_SIZE = 20
NODE_SHAPE = [10, 10]
FPS = 120
SEED = 7
IS_SHOW_PATH = False
IS_PAUSE_UPDATE = False

def main():
    """ Main function """
    snake_game = SnakeGame(SCREEN_TITLE, FPS, NODE_SHAPE, NODE_SIZE, SEED, IS_SHOW_PATH,
                           IS_PAUSE_UPDATE)
    snake_game.setup()
    arcade.run()


if __name__ == "__main__":
    main()