
import numpy as np
import nav
from nav import Axis

def create_empty_snake():
    '''
    create empty snake body

    Returns
    -------
    array
        the empty snake array
    '''
    return np.empty(shape = 0, dtype = np.int64)

def move(snake, dir, food, all_nodes, node_shape):
    '''
    move the snake and check for collisions

    Parameters
    ----------
    snake - array
        snake to be moved, contains node ids it occupies on the board

    dir : Dir
        direction to move snake next

    food : integer
        node id of the food

    all_nodes : array
        all node ids on the board

    node_shape : array
        node shape WxH

    Returns
    -------
    Tuple
        a tuple of the modified snake and food
    '''
    new_head = nav.get_next_node_id(snake[0], dir, node_shape)

    if (new_head == food):
        snake = np.append([food], snake)
        food = create_food(snake, all_nodes)
    elif (new_head in snake):
        snake = create_empty_snake()
    else:
        snake = np.roll(snake, 1)
        snake[0] = new_head

    return snake, food

def create_food(snake, all_nodes):
    '''
    create food

    Parameters
    ----------

    snake : array
        contains all node ids the snake occupies on the board

    all_nodes : array
        all node ids on the board

    Returns
    -------
    integer
        a node id of the newly created food
    '''
    rng = np.random.default_rng()
    free = np.setdiff1d(all_nodes, snake)
    if (len(free) == 0):
        return -1
    return rng.choice(free)

def offset_pos(t, node_size):
    '''
    offset draw position

    Parameters
    ----------
    t : integer
        draw component to be offset

    node_size : integer
        the node size in pixels

    Returns
    -------
    integer
        the offset component
    '''
    return np.int64(t) * node_size + node_size / 2


