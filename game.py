
import arcade
import numpy as np
import timeit

from enum import IntEnum
import hamilton_cycle_generator as hcg
import nav
from nav import Dir, Axis, Dmn
import snake
from snake import SnakeStatus
import move_algo
from move_algo import Algo

import draw_utils as du

class SnakeGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, title, fps, node_shape, node_size, seed = None,
                 is_show_path = False, is_pause_update = False,
                 is_draw_flat_path = False,
                 is_print_path = False):
        '''
        initialize the SnakeGame class

        Parameters
        ----------
        title : string
            The title of the game window

        fps - integer
            frames per second of the application

        node_shape : list
            node shape HxW - number of nodes in the height and width dimensions

        node_size : integer
            size of the node in pixels

        seed : integer, optional
            used to seed the default rng, by default is none

        is_show_path : bool, optional
            whether to show the hamiltonian path, by default is false

        is_pause_update : bool, optional
            whether to pause the update loop, by default is false

        is_draw_flat_path : bool, optional
            whether to draw the hamiltonian path flat below the grid
        '''
        self.m_node_shape = nav.create_pos(node_shape[Dmn.H], node_shape[Dmn.W])
        self.m_node_size = node_size
        self.m_seed = seed
        self.m_is_show_path = is_show_path
        self.m_is_pause_update = is_pause_update

        # Configure screen size
        self.m_grid_size[Dmn.W] = np.int64(self.m_node_shape[Dmn.W] * self.m_node_size)
        self.m_grid_size[Dmn.H] = np.int64(self.m_node_shape[Dmn.H] * self.m_node_size)

        screen_width = self.m_grid_size[Dmn.W]
        screen_height = self.m_grid_size[Dmn.H]
        if is_draw_flat_path:
            total_nodes = self.m_node_shape[Dmn.W] * self.m_node_shape[Dmn.H]
            screen_width = np.int64(total_nodes * self.m_node_size)
            screen_height = np.int64((self.m_node_shape[Dmn.H] + 2) * self.m_node_size)
            self.m_grid_offset = nav.create_pos(x = (screen_width - self.m_grid_size[Dmn.W]) * 0.5,
                                                y = screen_height - self.m_grid_size[Dmn.H])

        super().__init__(screen_width, screen_height, title, update_rate=1/fps)

        arcade.set_background_color(arcade.color.BLACK)
        # If you have sprite lists, you should create them here,
        # and set them to None

        self.m_path = hcg.generate_path(self.m_node_shape, self.m_seed, is_print_path)
        if is_print_path:
            row = ""
            for i in range(len(self.m_path)):
                row = f'{row}\t{self.m_path[i]}'
                if np.int64(i % self.m_node_shape[Dmn.W]) == (self.m_node_shape[Dmn.W] - 1):
                    print(row)
                    row = ""
            print(f'\n\npath:\n{self.m_path}')
        if is_show_path or is_draw_flat_path:
            self.m_path_lists = du.create_path_lists(self.m_path, self.m_node_size, self.m_node_shape,
                                                     self.m_grid_size[Dmn.W], self.m_grid_size[Dmn.H],
                                                     offset = self.m_grid_offset)
            if is_draw_flat_path:
                self.m_flat_path_lists = du.create_flat_path_lists(self.m_path, self.m_node_size, self.m_node_shape)
        self.setup()

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        self.m_all_nodes = np.arange(self.m_node_shape[Dmn.W] * self.m_node_shape[Dmn.H])
        self.m_snake = np.random.randint(len(self.m_all_nodes), size = 1)
        self.m_food = snake.create_food(self.m_snake, self.m_all_nodes, self.m_seed)
        move_algo.set_path_dir_index(self.m_snake[0], self.m_path)

        self.recreate_lists()

    def on_draw(self):
        #arcade.set_window(self._window)
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below
        self.m_snake_list.draw()

        # Draw the hamiltonian path
        if self.m_path_lists is not None:
            for list in self.m_path_lists:
                list.draw()

        # Draw flattened snake:
        if self.m_flat_snake_list is not None:
            self.m_flat_snake_list.draw()

        # Draw flattened path
        if self.m_flat_path_lists is not None:
            for list in self.m_flat_path_lists:
                list.draw()

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
            self.move_snake(dir)


    def algo_step(self, algo : Algo):
        '''
        make a step for the specified algorithm

        Parameters
        ----------
        algo : Algo
            algorithm type for which to make a step

        Returns
        -------
        status : SnakeStatus
            the current status of the snake
        '''
        dir = None

        if (algo is Algo.FOLLOW_PATH):
            dir = move_algo.find_next_dir(self.m_path, self.m_node_shape)
        elif algo is Algo.TAKE_SHORTCUTS:
            dir = move_algo.find_next_shortcut_dir(self.m_snake, self.m_food, self.m_path, self.m_node_shape)

        status = SnakeStatus.LOST
        if dir is not None:
            status = self.move_snake(dir)
        return status

    def move_snake(self, dir):
        '''
        move the snake in the specified direction

        Parameters
        ----------
        dir : Dir
            direction in which to move the snake

        Returns
        -------
        status : SnakeStatus
            the current status of the snake
        '''
        self.m_head_dir = dir
        self.m_snake, self.m_food, status = snake.move(self.m_snake, self.m_head_dir,
                                                       self.m_food, self.m_all_nodes,
                                                       self.m_seed, self.m_node_shape)
        self.recreate_lists()
        if status in [SnakeStatus.LOST, SnakeStatus.WON]:
            self.setup()
        return status

    def recreate_lists(self):
        '''
        recreate snake and food lists
        '''
        self.m_snake_list = du.create_snake_list(self.m_snake, self.m_head_dir, self.m_node_size,
                                                 self.m_node_shape, self.m_grid_size[Dmn.H],
                                                 offset = self.m_grid_offset)
        food_shape = du.create_food(self.m_food, self.m_node_size,
                                    self.m_node_shape[Dmn.W], self.m_grid_size[Dmn.H])
        self.m_snake_list.append(food_shape)

        if self.m_flat_path_lists is not None:
            self.m_flat_snake_list = du.create_flat_snake_list(self.m_snake, self.m_food, self.m_path,
                                                               self.m_node_size, self.m_node_shape)

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

    m_snake_list = None
    '''
    m_snake_list - snake segment shape list
    '''

    m_path_lists = None
    '''
    m_path_lists - text sprite and grid shape lists for m_path
    '''

    m_grid_size = nav.create_pos()
    '''
    m_grid_size - size of the grid in pixels
    '''

    m_grid_offset = None
    '''
    m_grid_offset - [x, y] grid offset from the bottom-right corner of the screen
    '''

    m_flat_snake_list = None
    '''
    m_flat_snake_list - contain the snake list as a flat row
    '''

    m_flat_path_lists = None
    '''
    m_flat_path_lists - contain the path lists as a flat row
    '''