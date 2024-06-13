
import arcade
import arcade.key
import arcade.key
import arcade.key
import arcade.key
import arcade.key
import arcade.key
import numpy as np
from enum import IntEnum

import hamilton_cycle_generator as hcg

import nav
from nav import Dir, Axis, Dmn

import snake

import move_algo
from move_algo import Algo

import draw_utils as du

class SnakeGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, title, fps, node_shape, node_size, seed = None,
                 is_show_path = False, is_pause_update = False):
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

        is_show_path : bool, optional
            whether to show the hamiltonian path, by default is false

        is_pause_update : bool, optional
            whether to pause the update loop, by default is false
        '''
        self.m_node_shape = nav.create_pos(node_shape[Dmn.H], node_shape[Dmn.W])
        self.m_node_size = node_size
        self.m_seed = seed
        self.m_is_show_path = is_show_path
        self.m_is_pause_update = is_pause_update

        screen_width = np.int64(self.m_node_shape[Dmn.W] * self.m_node_size)
        screen_height = np.int64(self.m_node_shape[Dmn.H] * self.m_node_size)
        super().__init__(screen_width, screen_height, title, update_rate=1/fps)

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
        #arcade.set_window(self._window)
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below
        self.draw_snake(self.m_snake, self.m_node_size, self.m_node_shape[Dmn.W])
        du.draw_cirle(self.m_food, self.m_node_size, self.m_node_shape[Dmn.W], self.height, arcade.color.RED_VIOLET)

        # Draw the hamiltonian path
        if self.m_is_show_path:
            for i in range(self.m_path.size):
                coords = du.get_coords(i, self.m_node_size, self.m_node_shape[Dmn.W], self.height)
                width = self.m_node_size
                arcade.draw_text(self.m_path[i], coords[Axis.X] - width * 0.5, coords[Axis.Y], font_size = 10, align="center", width=width)

            for i in range(self.m_node_shape[Dmn.H] + 1):
                y = i * self.m_node_size
                arcade.draw_line(0, y, self.width, y, arcade.color.WHITE)
            for i in range(self.m_node_shape[Dmn.W] + 1):
                x = i * self.m_node_size
                arcade.draw_line(x, 0, x, self.height, arcade.color.WHITE)

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        if self.m_is_pause_update:
            return
        algo = Algo.TAKE_SHORTCUTS
        self.algo_step(algo)


    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.P:
            self.m_is_pause_update = not self.m_is_pause_update

        if key == arcade.key.N:
            self.algo_step(Algo.TAKE_SHORTCUTS)

        if key == arcade.key.G:
            image = arcade.draw_commands.get_image(x=0, y=0, width=None, height=None)
            image.save('screenshot.png', 'PNG')

        dirs = {
             arcade.key.W : Dir.Up,
             arcade.key.A: Dir.Left,
             arcade.key.S: Dir.Down,
             arcade.key.D: Dir.Right
        }
        dir = dirs.get(key)
        if dir is not None:
            self.m_head_dir = dir
            self.m_snake, self.m_food = snake.move(self.m_snake, self.m_head_dir, self.m_food, self.m_all_nodes,
                                        self.m_seed, self.m_node_shape)
            if (self.m_snake.size == 0 or self.m_food == -1):
                self.setup()

    def draw_snake(self, snake_arr, square_size, w):
        '''
        draw a snake on the screen

        Parameters
        ----------
        snake_arr : array
            array of node ids occupied by the snake

        square_size : integer
            the size of a square in pixels

        w : integer
            number of squares in the width dimension
        '''

        snake_len = len(snake_arr)
        shape = self.m_node_shape
        for i in range(snake_len):
            j = snake_len - 1 - i
            square = snake_arr[j]
            coords = du.get_coords(square, square_size, w, self.height)

            color = arcade.color.ALIZARIN_CRIMSON if j == 0 else arcade.color.UFO_GREEN
            if j == 0:
                du.draw_triangle(coords, self.m_head_dir, square_size, color)
            elif j == snake_len -1:
                dir = nav.get_dir_between(square, snake_arr[j-1], shape)
                du.draw_tail(coords, dir, square_size, color)
            else:
                prev_dir = nav.get_dir_between(square, snake_arr[j-1], shape)
                next_dir = nav.get_dir_between(square, snake_arr[j+1], shape)
                du.draw_segment(coords, prev_dir, next_dir, square_size, color)


    def algo_step(self, algo):
        dir = None

        if (algo is Algo.FOLLOW_PATH):
            dir = move_algo.find_next_dir(self.m_path, self.m_node_shape)
        elif algo is Algo.TAKE_SHORTCUTS:
            dir = move_algo.fint_next_shortcut_dir(self.m_snake, self.m_food, self.m_path, self.m_node_shape)

        if dir is not None:
            self.m_head_dir = dir
            self.m_snake, self.m_food = snake.move(self.m_snake, self.m_head_dir, self.m_food, self.m_all_nodes,
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

    m_head_dir = Dir.Up
    '''
    m_head_dir - snake head direction
    '''

    m_is_pause_update = False
    '''
    m_is_pause_update - flag for pausing the update loop
    '''

    m_is_show_path = False
    '''
    m_is_show_path - should the hamiltonian path be shown
    '''