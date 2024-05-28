"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import arcade

import numpy as np

import hamilton_cycle_generator as hcg
from hamilton_cycle_generator import Dir


SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"
FPS = 5

SQUARE = 60
W = np.int64(SCREEN_WIDTH / SQUARE)
H = np.int64(SCREEN_HEIGHT / SQUARE)

curr_direction = np.zeros(2)

enum_dirs = {
    arcade.key.W : Dir.Up,
    arcade.key.S: Dir.Down,
    arcade.key.A: Dir.Left,
    arcade.key.D: Dir.Right
}

directions = {
    arcade.key.W : [0, 1],
    arcade.key.A: [-1, 0],
    arcade.key.S: [0, -1],
    arcade.key.D: [1, 0]
}

X = 0
Y = 1

food = 0



def get_direction(key_code):
    dir = directions.get(key_code)
    if dir == None:
        dir = [0, 0]
    return dir

def create_empty_snake():
    return np.empty(shape = 0, dtype = np.int64)

global_snake = create_empty_snake()
all_squares = np.array(np.arange(W * H))

def move(snake, dir, food, w = W, h = H):
    new_head = snake[0] + dir[X] + dir[Y] * w

    if (new_head == food):
        snake = np.append([food], snake)
        food = create_food(snake)
    elif (new_head in snake):
        snake = create_empty_snake()
        print(f'empty_snake: {snake}')
    else:
        snake = np.roll(snake, 1)
        snake[0] = new_head

    return snake, food

def create_food(snake, all = all_squares):
    rng = np.random.default_rng()
    free = np.setdiff1d(all, snake)
    if (free.size == 0):
        return -1
    return rng.choice(free)

def draw_square(square, color, square_size = SQUARE, w = W):
    offset = lambda t : np.int64(t) * square_size + square_size / 2
    x = offset(square % w)
    y = offset(square / w)
    arcade.draw_rectangle_filled(x, y, square_size - 10, square_size - 10, color)

def draw_snake(snake, square_size = SQUARE, w = W):
    for i in range(snake.size):
        j = snake.size - 1 - i
        color = arcade.color.AIR_SUPERIORITY_BLUE if j > 0 else arcade.color.RADICAL_RED
        draw_square(snake[j], color)

class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.BLACK)
        # If you have sprite lists, you should create them here,
        # and set them to None
        self.setup()
        self.set_update_rate(1/FPS)

        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        c = a + b
        print (f'a[{a}], b[{b}], c[{c}]')

        hcg.generate(W, H)

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        global global_snake, food, curr_direction
        food = 10#create_food(global_snake)
        global_snake = np.array([11, 1, 0])
        curr_direction = np.zeros(2)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below
        draw_snake(global_snake)
        draw_square(food, arcade.color.GREEN)


    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        global curr_direction, global_snake, food



    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        global curr_direction, global_snake, food
        curr_direction = get_direction(key)
        if curr_direction[X] != 0 or curr_direction[Y] != 0:
            global_snake, food = move(global_snake, curr_direction, food)
            print(f'curr_direction[{curr_direction}], UP[{Dir.Up.value}]')
            enum_dir = enum_dirs.get(key)
            local_dir = 0
            local_dir = hcg.set_dir(local_dir, Dir.Up)
            local_dir = hcg.set_dir(local_dir, Dir.Left)
            print(f'is enum_dir[{enum_dir}] in local_dir[{np.binary_repr(local_dir)}] -> {hcg.is_dir(local_dir, enum_dir)}')
            if (global_snake.size == 0):
                self.setup()


    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass


def main():
    """ Main function """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
