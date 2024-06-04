import numpy as np
from enum import IntEnum

import nav
from nav import Axis, Dmn, Dir

class Algo(IntEnum):
    FOLLOW_PATH = 0
    TAKE_SHORTCUTS = 1
    NONE = 2

directions = None
'''
directions - path directions for Algo.FOLLOW_PATH
'''

dir_index = np.int64(0)
'''
dir_index - current index in the directions array for Algo.FOLLOW_PATH
'''

def find_next_dir(path, shape):
    if directions is None:
        directions = create_path_directions(path, shape)
    while True:
        yield directions[dir_index]
        dir_index = np.int64((dir_index + 1) % len(directions))


def fint_next_shortcut_dir(snake, food, path, shape):
    '''
    find_next_shortcut_dir - find the next direction the snake should take
    so it reaches the food
    @param snake - snake array
    @param food - food node id
    @param path - hamilton path the snake should follow
    @param shape - node shape HxW
    @return the next direction the snake should take
    '''
    shape_size = np.int64(shape[Dmn.W] * shape[Dmn.H])
    snake_size = len(snake)
    head_pos = nav.get_node_pos(snake[0], shape)
    tail = snake[-1]
    path_node = path[snake[0]]
    food_dist = nav.path_distance(path_node, path[food], shape)
    tail_dist = nav.path_distance(path_node, path[tail], shape)
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
        next = nav.get_next_pos(head_pos, dir)
        if nav.is_out_of_bounds(next, shape):
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
            next_node = nav.get_next_pos(head_pos, dir)
            next_node_id = nav.get_node_id(next_node, shape)
            dist = nav.path_distance(path_node, path[next_node_id], shape)
            if (dist <= cutting_amount_available and dist > best_dist):
                best_dir = dir
                best_dist = dist

    if best_dist >= 0:
        return best_dir

    for dir in dir_array:
        if can_go(dir):
            return dir
    return None


# Utility functions
def create_path_directions(path, shape):
    '''
    create_path_directions - create an array of directions the snake should follow
    @param path - path the snake should follow
    @param shape - node shape HxW
    @return an array of path directions the snake should follow
    '''
    path_directions = np.zeros(shape = len(path), dtype=Dir)
    def get_node_id(val):
        return np.where(path == val)[0][0]
    initial_id = get_node_id(0)
    prev_node_id = initial_id
    for i in range(1, len(path)):
        node_id = get_node_id(i)
        dir = nav.get_dir_between(prev_node_id, node_id, shape)
        if dir is not None:
            path_directions[i - 1] = dir
        prev_node_id = node_id
    dir = nav.get_dir_between(prev_node_id, initial_id, shape)
    if dir is not None:
        path_directions[-1] = dir
    return path_directions

def set_path_dir_index(snake_head, path):
    '''
    set_path_dir_index - set the path direction index based on the
    head of the snake
    @param snake_head - snake head node id
    @param path - path the snake should follow
    '''
    dir_index = path[snake_head]