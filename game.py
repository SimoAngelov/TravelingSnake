
import arcade
import arcade.key
import numpy as np
from enum import IntEnum

import hamilton_cycle_generator as hcg

import nav
from nav import Dir, Axis, Dmn

import snake

import move_algo
from move_algo import Algo

class SnakeGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, title, fps, node_shape, node_size):
        self.m_node_shape = nav.create_pos(node_shape[Dmn.H], node_shape[Dmn.W])
        self.m_node_size = node_size

        screen_width = np.int64(self.m_node_shape[Dmn.W] * self.m_node_size)
        screen_height = np.int64(self.m_node_shape[Dmn.H] * self.m_node_size)
        super().__init__(screen_width, screen_height, title, update_rate=1/fps)

        arcade.set_background_color(arcade.color.BLACK)
        # If you have sprite lists, you should create them here,
        # and set them to None

        self.m_path = hcg.generate_path(self.m_node_shape, True)
        row = ""
        for i in range(len(self.m_path)):
            row = f'{row}\t{self.m_path[i]}'
            if np.int64(i % self.m_node_shape[Dmn.W]) == (self.m_node_shape[Dmn.W] - 1):
                print(row)
                row = ""
        print(f'\n\npath:\n{self.m_path}')
        self.setup()

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        self.m_all_nodes = np.arange(self.m_node_shape[Dmn.W] * self.m_node_shape[Dmn.H])
        self.m_snake = np.random.randint(self.m_node_shape[Dmn.W] * self.m_node_shape[Dmn.H], size = 1)
        self.m_food = snake.create_food(self.m_snake, self.m_all_nodes)
        move_algo.set_path_dir_index(self.m_snake[0], self.m_path)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below
        self.draw_snake(self.m_snake, self.m_node_size, self.m_node_shape[Dmn.W])
        self.draw_square(self.m_food, arcade.color.GREEN, self.m_node_size, self.m_node_shape[Dmn.W])

        show_path = False
        if show_path:
            for i in range(self.m_path.size):
                x = snake.offset_pos(i % self.m_node_shape[Dmn.W], self.m_node_size)
                y = self.height - snake.offset_pos(i / self.m_node_shape[Dmn.W], self.m_node_size)
                arcade.draw_text(self.m_path[i], x, y)

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        dir = None
        algo = Algo.TAKE_SHORTCUTS
        if (algo is Algo.FOLLOW_PATH):
            dir = move_algo.find_next_dir(self.m_path, self.m_node_shape)
        elif algo is Algo.TAKE_SHORTCUTS:
            dir = move_algo.fint_next_shortcut_dir(self.m_snake, self.m_food, self.m_path, self.m_node_shape)

        if dir is not None:
            self.m_snake, self.m_food = snake.move(self.m_snake, dir,
                                                    self.m_food, self.m_all_nodes, self.m_node_shape)
            if (self.m_snake.size == 0 or self.m_food == -1):
                self.setup()


    def on_key_press(self, key, key_modifiers):
        pass


    def draw_square(self, square, color, square_size, w):
        x = snake.offset_pos(square % w, square_size)
        y = self.height - snake.offset_pos(square / w, square_size)
        arcade.draw_rectangle_filled(x, y, square_size, square_size, color)

    def draw_snake(self, snake, square_size, w):
        for i in range(snake.size):
            j = snake.size - 1 - i
            color = arcade.color.AIR_SUPERIORITY_BLUE if j > 0 else arcade.color.RADICAL_RED
            self.draw_square(snake[j], color, square_size, w)

    m_node_shape = nav.create_pos()
    '''
    m_node_shape - shape of nodes HxW
    '''

    m_node_size = 0
    '''
    m_node_size - node size in pixels
    '''

    m_path = np.empty(shape = 0)
    '''
    m_path - current hamiltonian cycle
    '''

    m_snake = snake.create_empty_snake()
    '''
    m_snake - current hamiltonian cycle
    '''

    m_food = -1
    '''
    m_food - current food position
    -1 means invalid food
    '''

    m_all_nodes = []
    '''
    m_all_nodes - all node ids on screen
    '''