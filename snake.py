
import numpy as np
import nav
from nav import Axis

def create_empty_snake():
    '''
    create_empty_snake - create empty snake body
    @return the empty snake array
    '''
    return np.empty(shape = 0, dtype = np.int64)

def move(snake, dir, food, all_nodes, node_shape):
    '''
    move - move the snake and check for collisions
    @param snake - snake to be moved
    @param dir - direction to move snake next
    @param food - node id of the food
    @param all_nodes - all node ids
    @param node_shape - node shape WxH
    '''
    new_head = nav.get_next_node_id(snake[0], dir, node_shape)

    if (new_head == food):
        snake = np.append([food], snake)
        food = create_food(snake, all_nodes)
    elif (new_head in snake):
        snake = create_empty_snake()
        print(f'empty_snake: {snake}')
    else:
        snake = np.roll(snake, 1)
        snake[0] = new_head

    return snake, food

def create_food(snake, all_nodes):
    rng = np.random.default_rng()
    free = np.setdiff1d(all_nodes, snake)
    if (len(free) == 0):
        return -1
    return rng.choice(free)

def offset_pos(t, node_size):
    return np.int64(t) * node_size + node_size / 2


