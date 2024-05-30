#!/usr/bin/env python3

from game import SnakeGame
import arcade
import numpy as np

SCREEN_TITLE = "Traveling Snake"

NODE_SIZE = 20
NODE_SHAPE = [4, 4]
FPS = 20

def main():
    """ Main function """
    snake_game = SnakeGame(SCREEN_TITLE, FPS, NODE_SHAPE, NODE_SIZE)
    snake_game.setup()
    arcade.run()


if __name__ == "__main__":
    main()