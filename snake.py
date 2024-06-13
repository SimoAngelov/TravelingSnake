
import numpy as np
from enum import IntEnum
import json
import nav
from nav import Axis, Dir, Dmn
import move_algo
from move_algo import Algo
import hamilton_cycle_generator as hcg

class SnakeStatus(IntEnum):
    MOVING = 0
    ATE_FOOD = 1
    LOST = 2
    WON = 3

def create_empty_snake():
    '''
    create empty snake body

    Returns
    -------
    array
        the empty snake array
    '''
    return np.empty(shape = 0, dtype = np.int64)

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

def move(snake, dir : Dir, food, all_nodes, seed, node_shape):
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

    Raises
    ------
    TypeError
        if dir isn't of type Dir
    '''
    if not isinstance(dir, Dir):
        raise TypeError(f'dir: {dir} isn\'t of type Dir')
    new_head = nav.get_next_node_id(snake[0], dir, node_shape)
    if new_head is None:
        raise AssertionError(f'new_head is none! snake[0]: {snake[0]}, dir: {dir}, node_shape: {node_shape}')

    status = SnakeStatus.MOVING
    if (new_head == food):
        snake = np.append([food], snake)
        food = create_food(snake, all_nodes, seed)
        status = SnakeStatus.WON if food == -1 else SnakeStatus.ATE_FOOD
    elif (new_head in snake):
        snake = create_empty_snake()
        status = SnakeStatus.LOST
    else:
        snake = np.roll(snake, 1)
        snake[0] = new_head

    return snake, food, status

def run_test(node_shape, algo, seed):
    node_shape = nav.create_pos(node_shape[Dmn.H], node_shape[Dmn.W])
    hamilton = hcg.generate_path(node_shape, seed)
    all_nodes = np.arange(node_shape[Dmn.W] * node_shape[Dmn.H])
    snake = np.random.randint(len(all_nodes), size = 1)
    food = create_food(snake, all_nodes, seed)
    move_algo.set_path_dir_index(snake[0], hamilton)
    status = SnakeStatus.MOVING

    all_moves = np.zeros(shape = len(all_nodes) - 1, dtype = np.int64)
    curr_move = 0
    while status not in [SnakeStatus.WON, SnakeStatus.LOST]:
        dir = None
        if (algo is Algo.FOLLOW_PATH):
            dir = move_algo.find_next_dir(hamilton, node_shape)
        elif algo is Algo.TAKE_SHORTCUTS:
            dir = move_algo.fint_next_shortcut_dir(snake, food, hamilton, node_shape)

        if dir is None:
            break
        snake, food, status = move(snake, dir, food, all_nodes, seed, node_shape)

        all_moves[curr_move] += 1
        if status == SnakeStatus.ATE_FOOD:
            curr_move += 1
    return all_moves

def run_simulation(sim_params, save_path):

    seed_count = sim_params["seed_count"]
    games_per_seed = sim_params["games_per_seed"]
    shapes = sim_params["node_shapes"]

    seeds = np.arange(seed_count)
    results = {}
    results["params"] = sim_params
    results["params"]["seeds"] = seeds.tolist()
    results["data"] = {}
    for seed in seeds:
        for shape in shapes:
                shape_key = f'shape_{shape[Dmn.H]}x{shape[Dmn.W]}'
                results["data"][shape_key] = {}
                total_size = shape[Dmn.H] * shape[Dmn.W]
                for game in range(games_per_seed):
                    algos = [Algo.FOLLOW_PATH, Algo.TAKE_SHORTCUTS]
                    for algo in algos:
                        moves_key = f'seed_{seed}_algo_{algo}_game_{game}'
                        print(f'test shape_key[{shape_key}], moves_key[{moves_key}]')
                        moves = run_test(shape, algo, seed)
                        results["data"][shape_key][moves_key] = moves.tolist()
                        print(f'results -> shape_key[{shape_key}], moves_key[{moves_key}], moves: {moves}')

    # Save results to json file
    json_object = json.dumps(results, indent=4)
    with open(save_path, "w") as outfile:
        outfile.write(json_object)