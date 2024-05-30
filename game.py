
import arcade
import numpy as np

import hamilton_cycle_generator as hcg
from hamilton_cycle_generator import Dir

import nav
from nav import Dir, Axis

import snake

def ai_find_next_dir(snake, food, path, shape):
    shape_size = np.int64(shape[Axis.X] * shape[Axis.Y])
    snake_size = len(snake)
    head = snake[0]
    tail = snake[-1]
    path_node = path[head]
    food_dist = nav.path_distance(path_node, food, shape)
    tail_dist = nav.path_distance(path_node, tail, shape)
    cutting_amount_available = tail_dist - snake_size - 3 # allow a small buffer
    empty_nodes = shape_size - snake_size - 1 # account for food

    # If we don't have much space (i.e. snake is 75% of board) then don't take any shortcuts
    if empty_nodes < shape_size / 2:
        cutting_amount_available = 0
    # Snake will eat the food on the way to the tail so take that into account
    elif food_dist < tail_dist:
        cutting_amount_available -= snake_size
        # Once the snake eats the food, it might end up with another food suddenly appearing in front of it
        # 25% chance of another path square appearing
        if (tail_dist - food_dist) * 4 > empty_nodes:
            cutting_amount_available -= 10

    cutting_amount_desired = food_dist
    if cutting_amount_desired < cutting_amount_available:
        cutting_amount_available = cutting_amount_desired
    if cutting_amount_available < 0:
        cutting_amount_available = 0
    # cutting_amount_available is now the maximum amout the snake can cut by

    def can_go(dir: Dir):
        next = nav.get_next_pos(head, dir)
        if next[Axis.X] < 0 or next[Axis.Y] < 0 or next[Axis.X] >= shape[Axis.X] or next[Axis.Y] > shape[Axis.Y]:
            return False
        next_node_id = nav.get_node_id(next, shape)
        if next_node_id in snake:
            return False
        return True

    dir_array = nav.get_dir_array()
    can_go_arr = np.zeros(len(dir_array), dtype = bool)
    best_dir = None
    best_dist = -1
    for i in range(len(dir_array)):
        dir = dir_array[i]
        can_go_arr[i] = can_go(dir)
        if can_go_arr[i]:
            next_node = nav.get_next_pos(head, dir)
            next_node_id = nav.get_node_id(next_node, shape)
            dist = nav.path_distance(path_node, next_node_id, shape)
            if (dist <= cutting_amount_available and dist > best_dist):
                best_dir = dir
                best_dist = dist

    if best_dist >= 0:
        return best_dir

    for dir in dir_array:
        if can_go(dir):
            return dir
    return None

class SnakeGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, title, fps, node_shape, node_size):
        self.m_node_shape = nav.create_pos(node_shape[Axis.X], node_shape[Axis.Y])
        self.m_node_size = node_size

        screen_width = np.int64(self.m_node_shape[Axis.X] * self.m_node_size)
        screen_height = np.int64(self.m_node_shape[Axis.Y] * self.m_node_size)
        super().__init__(screen_width, screen_height, title, update_rate=1/fps)

        arcade.set_background_color(arcade.color.BLACK)
        # If you have sprite lists, you should create them here,
        # and set them to None
        self.setup()

        self.m_path = hcg.generate_path(self.m_node_shape, True)
        row = ""
        for i in range(len(self.m_path)):
            row = f'{row}\t{self.m_path[i]}'
            if np.int64(i % self.m_node_shape[Axis.X]) == (self.m_node_shape[Axis.X] - 1):
                print(row)
                row = ""
        print(f'\n\npath:\n{self.m_path}')
        self.set_path_directions()

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        self.m_all_nodes = np.arange(self.m_node_shape[Axis.X] * self.m_node_shape[Axis.Y])
        self.m_snake = np.where(self.m_path == 0)[0]
        self.m_food = snake.create_food(self.m_snake, self.m_all_nodes)
        self.m_dir_vector = nav.create_pos()
        self.m_i = 0

    def on_draw(self):
        """
        Render the screen.
        """

        # dir = self.m_path_directions[self.m_i]
        # self.m_i = np.int64((self.m_i + 1) % len(self.m_path_directions))
        # if dir is not None:
        #     self.m_dir_vector = nav.get_next_pos(nav.create_pos(), dir)
        # else:
        #     self.m_dir_vector = nav.create_pos()

        # if self.m_dir_vector[Axis.X] != 0 or self.m_dir_vector[Axis.Y] != 0:
        #     self.m_snake, self.m_food = snake.move(self.m_snake, self.m_dir_vector,
        #                                             self.m_food, self.m_all_nodes, self.m_node_shape)
        #     if (self.m_snake.size == 0 or self.m_food == -1):
        #         self.setup()

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below
        self.draw_snake(self.m_snake, self.m_node_size, self.m_node_shape[Axis.X])
        self.draw_square(self.m_food, arcade.color.GREEN, self.m_node_size, self.m_node_shape[Axis.X])

        show_path = False
        if show_path:
            for i in range(self.m_path.size):
                x = snake.offset_pos(i % self.m_node_shape[Axis.X], self.m_node_size)
                y = self.height - snake.offset_pos(i / self.m_node_shape[Axis.X], self.m_node_size)
                arcade.draw_text(self.m_path[i], x, y)

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        dir = ai_find_next_dir(self.m_snake, self.m_food, self.m_path, self.m_node_shape)
        if dir is not None:
            self.m_dir_vector = nav.get_next_pos(nav.create_pos(), dir)
        else:
            self.m_dir_vector = nav.create_pos()

        if self.m_dir_vector[Axis.X] != 0 or self.m_dir_vector[Axis.Y] != 0:
            print(f'self.m_node_shape[{self.m_node_shape}], self.m_dir_vector[{self.m_dir_vector}], self.m_snake[{self.m_snake}]')
            self.m_snake, self.m_food = snake.move(self.m_snake, self.m_dir_vector,
                                                    self.m_food, self.m_all_nodes, self.m_node_shape)
            if (self.m_snake.size == 0 or self.m_food == -1):
                self.setup()


    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        # dir = self.m_directions.get(key)
        # if dir is not None:
        #     self.m_dir_vector = nav.get_next_pos(nav.create_pos(), dir)
        # else:
        #     self.m_dir_vector = nav.create_pos()

        # if self.m_dir_vector[Axis.X] != 0 or self.m_dir_vector[Axis.Y] != 0:
        #     print(f'self.m_node_shape[{self.m_node_shape}], self.m_dir_vector[{self.m_dir_vector}], self.m_snake[{self.m_snake}]')
        #     self.m_snake, self.m_food = snake.move(self.m_snake, self.m_dir_vector,
        #                                             self.m_food, self.m_all_nodes, self.m_node_shape)
        #     if (self.m_snake.size == 0 or self.m_food == -1):
        #         self.setup()

    def draw_square(self, square, color, square_size, w):
        x = snake.offset_pos(square % w, square_size)
        y = self.height - snake.offset_pos(square / w, square_size)
        arcade.draw_rectangle_filled(x, y, square_size, square_size, color)

    def draw_snake(self, snake, square_size, w):
        for i in range(snake.size):
            j = snake.size - 1 - i
            color = arcade.color.AIR_SUPERIORITY_BLUE if j > 0 else arcade.color.RADICAL_RED
            self.draw_square(snake[j], color, square_size, w)

    def set_path_directions(self):
        self.m_path_directions = np.zeros(shape = len(self.m_path), dtype=Dir)
        def get_node_id(val):
            return np.where(self.m_path == val)[0][0]
        initial_id = get_node_id(0)
        prev_node_id = initial_id
        for i in range(1, len(self.m_path)):
            node_id = get_node_id(i)
            dir = nav.get_dir_between(prev_node_id, node_id, self.m_node_shape)
            if dir is not None:
                self.m_path_directions[i - 1] = dir
            prev_node_id = node_id
        dir = nav.get_dir_between(prev_node_id, initial_id, self.m_node_shape)
        if dir is not None:
            self.m_path_directions[-1] = dir
        print (self.m_path_directions)


    m_node_shape = nav.create_pos()
    '''
    m_node_shape - shape of nodes WxH
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

    m_dir_vector = nav.create_pos()
    '''
    m_dir_vector - current snake vector
    '''

    m_food = -1
    '''
    m_food - current food position
    -1 means invalid food
    '''

    m_directions = {
        arcade.key.W : Dir.Up,
        arcade.key.A: Dir.Left,
        arcade.key.S: Dir.Down,
        arcade.key.D: Dir.Right
    }
    '''
    m_directions - map arcade keys to nav.Dir directions
    '''

    m_all_nodes = []
    '''
    m_all_nodes - all node ids on screen
    '''

    m_path_directions = []

    m_i = 0;