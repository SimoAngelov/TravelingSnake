
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

def move(snake, dir, food, all_nodes, seed, node_shape):
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

    seed : integer
        used to seed the default rng

    Returns
    -------
    Tuple
        a tuple of the modified snake and food
    '''
    new_head = nav.get_next_node_id(snake[0], dir, node_shape)

    if (new_head == food):
        snake = np.append([food], snake)
        food = create_food(snake, all_nodes, seed)
    elif (new_head in snake):
        snake = create_empty_snake()
    else:
        snake = np.roll(snake, 1)
        snake[0] = new_head

    return snake, food

def create_food(snake, all_nodes, seed):
    '''
    create a food on the board

    Parameters
    ----------

    snake : array
        contains all node ids the snake occupies on the board

    all_nodes : array
        all node ids on the board

    seed : integer
        used to seed the default rng

    Returns
    -------
    integer
        a node id of the newly created food
    '''
    free = np.setdiff1d(all_nodes, snake)
    if (len(free) == 0):
        return -1
    seed_seq = np.random.SeedSequence(entropy = seed)
    rng = np.random.default_rng(seed_seq)
    return rng.choice(free)