import numpy as np
import nav
from nav import Dir, Axis, Dmn


def generate_path(shape, seed = 0, is_print_mst = False):
    '''
    generate hamiltonian path

    Parameters
    ----------
    shape : array
        node shape HxW

    seed : integer, optional
        used to seed the default rng, by default is none

    is_print_mst : bool, optional
        whether to print the minimum spanning tree from Prim's MST algorithm, by default is False

    Returns
    -------
    array
        an array which is the hamiltonian path. The values are node ids.
        If the shape can't produce a valid hamiltonian path, an empty array is returned.

    Raises
    ------
    ValueError
        if neither of the shape's dimensions is even
    '''
    # The shape doesn't contain a valid hamiltonian cycle
    if shape[Dmn.W] * shape[Dmn.H] % 2 != 0 or shape[Dmn.W] == 1 or shape[Dmn.H] == 1:
        raise ValueError(f'failed to generate path! shape: {shape} is not even in any dimension!')
        return np.empty(shape = 0, dtype=np.int64)

    # The shape has an odd dimension, so Prim's MST can't be used in this case
    if shape[Dmn.W] % 2 != 0 or shape[Dmn.H] % 2 != 0:
        return generate_path_with_odd_dimension(shape)

    # Use Prim's MST to generate an mst and a hamiltonian cycle
    half_shape = nav.create_pos(shape[Dmn.H] / 2, shape[Dmn.W] / 2)
    mst, mst_edge_order = generate_prim_mst(shape, seed)

    if is_print_mst:
        print(f'mst: {mst}')
        dirs = nav.get_dir_array()
        for i in range(mst.size):
            res = ''
            for dir in dirs:
                if nav.is_dir(mst[i], dir):
                    res = f'{res}, {dir}'
            print(f'edge[{i}]: {res}')
        print(f'mst_edge_order:\n{mst_edge_order}')
    return generate_hamilton_cycle(mst, shape)

def generate_prim_mst(shape, seed = None):
    '''
    generate a minimum spanning tree (MST), using Prim's algorithm.
    Randomized choice is used to substitute the edge weights.
    The constructed MST is half the size of shape and is used as a
    guide to construct the Hamiltonian Cycle around the node grid.

    Parameters
    ----------
    shape : array
        node shape of the original grid for which to createHxW

    seed : integer, optional
        used to seed the default rng, by default is none

    Returns
    -------
    (mst, edge_order) : tuple
        a tuple of the generated mst and the order in which the edges were created.
        The MST or minimum spanning tree is an array for which the
        indices are nodes, values are direction masks,

    '''
    seed_seq = np.random.SeedSequence(entropy = seed)
    rng = np.random.default_rng(seed_seq)
    prim_shape = nav.create_pos(shape[Dmn.H] / 2, shape[Dmn.W] / 2)

    size = prim_shape[Dmn.W] * prim_shape[Dmn.H]
    # Initialize the MST as an array. The indices are node ids, the values are bit masks
    # that encode the directions to the node's neighbors.
    mst = np.zeros(size, dtype = np.int8)

    # Keep track of the order the edges were formed
    edge_order = np.zeros(shape = (size -1, Axis.COUNT), dtype = np.int64)

    # Create an adjacency list for each node in the grid
    # The indices of the array are node ids. The values of the array are dictionaries with
    # keys: neighbor node ids,
    # values: direction of the neighbor from the node.
    adjacency_arr = np.array([{} for _ in range(size)])
    dir_array = nav.get_dir_array()
    for node_id in range(size):
            for dir_id in range(len(dir_array)):
                dir = dir_array[dir_id]
                neighbor_id = nav.get_next_node_id(node_id, dir, prim_shape)
                if neighbor_id is not None:
                    adjacency_arr[node_id][neighbor_id] = dir

    # Choose a random node to be the start of the MST
    start = rng.integers(0, size)
    # Create a list of all fringe nodes that currently neighbor the MST.
    fringes = list(adjacency_arr[start].keys())
    # Create a list of all nodes that have already been visited and are part of the MST
    visited = [start]

    # Visit all nodes in the graph
    i = 0
    while (len(visited) < size):
        # Pick a random node from the fringes as a candidate to be added to the MST
        fringe = rng.choice(fringes)
        candidates = []
        new_fringes = []

        # Retrieve all the neighbors of the fringe node
        neighbors = adjacency_arr[fringe].keys()
        for neighbor in neighbors:
            # If the neighbor has already been visited and is part of the MST, add it as possible edge
            if neighbor in visited:
                candidates.append(neighbor)
            # If not, add it as a part of the new fringes, since it will neighbor the MST when the edge is formed
            elif neighbor not in fringes:
                new_fringes.append(neighbor)

        # Choose a random candidate from the available ones
        candidate = rng.choice(candidates)

        # Add the fringe node to the list of visited ones
        visited.append(fringe)

        # Update the MST with the connections between the two nodes
        mst[fringe] = nav.set_dir(mst[fringe], adjacency_arr[fringe][candidate])
        mst[candidate] = nav.set_dir(mst[candidate], adjacency_arr[candidate][fringe])
        edge_order[i, Axis.X] = fringe
        edge_order[i, Axis.Y] = candidate

        # Remove the fringe node from the fringes and add it to the new neighbors that border the MST
        fringes.remove(fringe)
        fringes += new_fringes
        i += 1

    return (mst, edge_order)

def generate_hamilton_cycle(mst, shape):
    '''
    generate a hamiltonian cycle from the specified mst

    Parameters
    ----------
    mst : array
        mininum spanning tree from which to construct the hamiltonian cycle

    shape : array
        node shape HxW

    Returns
    -------
    array
        array which is the hamiltonian cycle from the specified mst. The values are indices in the path

    Raises
    ------
    ValueError
        if neither of the shape's dimensions is even
    '''
    hamilton_cycle = np.zeros(np.int64(shape[Dmn.W] * shape[Dmn.H]), dtype=np.int64)
    if len(hamilton_cycle) % 2 != 0:
        raise ValueError(f'failed to generate_hamilton_cycle! shape: {shape} is not even in any dimension!')

    def can_go(dir, pos):
        '''
        query whether we can move from the current position in the desired direction

        Parameters
        ----------
        dir : Dir
            direction in which we want to go

        pos : array
            current x, y position

        Returns
        -------
        bool
            True, if we can go from the current position in the desired direction
        '''
        node_id = nav.get_node_id(pos, shape / 2)
        if node_id >= mst.size:
            return False
        return nav.is_dir(mst[node_id], dir)

    pos = nav.create_pos()
    dir = Dir.Up if can_go(Dir.Down, pos) else Dir.Left
    curr_square = 0
    start_offsets = np.array([nav.create_pos(y = 1), nav.create_pos(), nav.create_pos(x = 1), nav.create_pos(1, 1)])

    while True:
        next_dir = find_next_dir(pos, dir, can_go)
        pos_double = pos * 2

        # set the current path square
        dir_array = nav.get_dir_array(dir)
        offsets = np.roll(start_offsets, -dir.value, Axis.X)
        offsets_len = len(offsets)

        set_path_square(hamilton_cycle, curr_square, pos_double + offsets[0], shape)
        curr_square += 1

        for i in range(1, offsets_len):
            indices = [j + i - 1 for j in range(offsets_len - i)]
            directions = dir_array[indices]
            if next_dir in directions:
                set_path_square(hamilton_cycle, curr_square, pos_double + offsets[i], shape)
                curr_square += 1

        dir = next_dir
        pos = nav.get_next_pos(pos, next_dir)

        # Terminate generator loop
        if curr_square >= hamilton_cycle.size:
            break
    return hamilton_cycle

def find_next_dir(pos, dir: Dir, can_go):
    '''
    find the next direction we can go from the current position

    Parameters
    ----------
    pos : array
        current position

    dir : Dir
        direction we're currently facing

    can_go : function
        predicate to determine, if we can go in a certain direction

    Returns
    -------
    Dir
        the next direction we should go from the current position
    '''
    # start the array by rolling it one position, so it starts
    # from left neighbor of dir
    next_dir_array = nav.get_dir_array(dir, 1)
    for i in range(next_dir_array.size - 1):
        # check if we can go in any of the first 3 directions
        next_dir = next_dir_array[i]
        if can_go(next_dir, pos):
            return next_dir
    # return the inverted dir
    return next_dir_array[-1]

def set_path_square(path, path_square, pos, shape):
    '''
    set a path square at the specified position

    Parameters
    ----------
    path : array, output parameter
        Path for which to set the square

    path_square : integer
        square to be set

    pos : array
        node position at which to set the square

    shape : array
        node shape HxW
    '''
    node_id = nav.get_node_id(pos, shape)
    if (path[node_id] == 0):
        path[node_id] = path_square

def get_turning_points_odd_w(w, h, get_id):
    '''
    retrieve a dictionary of turning points where the path has an odd width

    Parameters
    ----------
    w : integer
        width of the grid

    h : integer
        height of the grid

    get_id : function
        a callback to retrieve a node id from x, y coordinates

    Returns
    -------
        turning_points : dict
        a dictionary of turning mode ids and directions they turn
    '''
    turning_points = {get_id(x = w - 1) : Dir.Down}
    switch = False
    for i in range(1, h):
        x1 = 1 if i % 2 == 0 else w - 1
        x2 = w - 1 if i % 2 == 0 else 1
        turning_points[get_id(x1, i)] = Dir.Right if switch else Dir.Left
        switch = not switch
        if i < h - 1:
            turning_points[get_id(x2, i)] = Dir.Down

    turning_points[get_id(y = h - 1)] = Dir.Up
    return turning_points


def get_turning_points_odd_h(w, h, get_id):
    '''
    retrieve a dictionary of turning points where the path has an odd height

    Parameters
    ----------
    w : integer
        width of the grid

    h : integer
        height of the grid

    get_id : function
        a callback to retrieve a node id from x, y coordinates

    Returns
    -------
        turning_points : dict
        a dictionary of turning mode ids and directions they turn
    '''
    turning_points = {get_id(x = w - 1) : Dir.Down}
    switch = False
    for i in range(w - 1, -1, -1):
        y1 = 1 if i % 2 == 0 else h - 1
        y2 = h - 1 if i % 2 == 0 else 1
        if i > 0:
            turning_points[get_id(i, y1)] = Dir.Left
        if i < w - 1:
            turning_points[get_id(i, y2)] = Dir.Down if switch else Dir.Up
            switch = not switch
    return turning_points


def generate_path_with_odd_dimension(shape):
    '''
    generate a hamiltonian path where one of the dimensions is odd

    Parameters
    ----------
    shape : array
        node shape HxW

    Returns
    -------
    path : array
        array which is the hamiltonian cycle. The values are indices in the path
    '''
    w = shape[Dmn.W]
    h = shape[Dmn.H]
    get_id = lambda x = 0, y = 0: nav.get_node_id(nav.create_pos(x, y), shape)

    path = np.zeros(shape = w * h, dtype = np.int64)
    turning_points = {}
    if h % 2 != 0:
        turning_points = get_turning_points_odd_h(w, h, get_id)
    elif w % 2 != 0:
        turning_points = get_turning_points_odd_w(w, h, get_id)

    dir = Dir.Right
    pos = nav.create_pos()
    for i in range(len(path)):
        curr_id = nav.get_node_id(pos, shape)
        path[curr_id] = i
        curr_dir = turning_points.get(curr_id)
        if curr_dir is not None:
            dir = curr_dir
        pos = nav.get_next_pos(pos, dir)

    return path