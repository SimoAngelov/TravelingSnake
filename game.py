
import arcade
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

    def __init__(self, title, fps, node_shape, node_size, seed):
        '''
        initialize the SnakeGame class

        Parameters
        ----------
        title : string
            The title of the game window

        fps - integer
            frames per second of the application

        node_shape : list
            node shape HxW

        node_size : integer
            size of the node in pixels

        seed : integer, optional
            used to seed the default rng, by default is none
        '''
        self.m_node_shape = nav.create_pos(node_shape[Dmn.H], node_shape[Dmn.W])
        self.m_node_size = node_size
        self.m_seed = seed

        screen_width = np.int64(self.m_node_shape[Dmn.W] * self.m_node_size)
        screen_height = np.int64(self.m_node_shape[Dmn.H] * self.m_node_size)
        super().__init__(screen_width, screen_height, title, update_rate=1/fps, vsync=True)

        arcade.set_background_color(arcade.color.BLACK)
        # If you have sprite lists, you should create them here,
        # and set them to None

        self.m_path = hcg.generate_path(self.m_node_shape, self.m_seed, True)
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
        self.m_food = snake.create_food(self.m_snake, self.m_all_nodes, self.m_seed)
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
                width = self.m_node_size
                arcade.draw_text(self.m_path[i], x - width / 2, y, font_size = 10, align="center", width=width)

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        algo = Algo.TAKE_SHORTCUTS
        self.algo_step(algo)


    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.N:
            self.algo_step(Algo.NONE)
            print(f'\n\n')

    def draw_square(self, square, color, square_size, w):
        '''
        draw a square on the screen

        Parameters
        ----------
        square - node id of the square to be draw.

        color : string
            color of the square

        square_size : integer
            the size of the square in pixels

        w : integer
            number of squares in the width dimension
        '''
        x = snake.offset_pos(square % w, square_size)
        y = self.height - snake.offset_pos(square / w, square_size)
        arcade.draw_rectangle_filled(x, y, square_size, square_size, color)

    def draw_snake(self, snake, square_size, w):
        '''
        draw a snake on the screen

        Parameters
        ----------
        snake : array
            array of node ids occupied by the snake

        square_size : integer
            the size of a square in pixels

        w : integer
            number of squares in the width dimension
        '''

        for i in range(snake.size):
            j = snake.size - 1 - i
            color = arcade.color.AIR_SUPERIORITY_BLUE if j > 0 else arcade.color.RADICAL_RED
            self.draw_square(snake[j], color, square_size, w)

    def algo_step(self, algo):
        dir = None

        if (algo is Algo.FOLLOW_PATH):
            dir = move_algo.find_next_dir(self.m_path, self.m_node_shape)
        elif algo is Algo.TAKE_SHORTCUTS:
            dir = move_algo.fint_next_shortcut_dir(self.m_snake, self.m_food, self.m_path, self.m_node_shape)

        if dir is not None:
            self.m_snake, self.m_food = snake.move(self.m_snake, dir, self.m_food, self.m_all_nodes,
                                                   self.m_seed, self.m_node_shape)
            if (self.m_snake.size == 0 or self.m_food == -1):
                self.setup()

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

    m_seed = None
    '''
    m_seed - used to seed the default rng
    '''