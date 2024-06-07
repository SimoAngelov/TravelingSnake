#!/usr/bin/env python3

from game import SnakeGame
import arcade
import numpy as np

SCREEN_TITLE = "Traveling Snake"

NODE_SIZE = 20
NODE_SHAPE = [20, 20]
FPS = 60
SEED = 6

def main():
    """ Main function """
    snake_game = SnakeGame(SCREEN_TITLE, FPS, NODE_SHAPE, NODE_SIZE, SEED)
    snake_game.setup()
    arcade.run()


if __name__ == "__main__":
    main()