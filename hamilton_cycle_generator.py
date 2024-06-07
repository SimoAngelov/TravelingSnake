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
    '''
    # The shape doesn't contain a valid hamiltonian cycle
    if shape[Dmn.W] * shape[Dmn.H] % 2 != 0 or shape[Dmn.W] == 1 or shape[Dmn.H] == 1:
        return np.empty(shape = 0, dtype=np.int64)

    # The shape has an odd dimension, so Prim's MST can't be used in this case
    if shape[Dmn.W] % 2 != 0 or shape[Dmn.H] % 2 != 0:
        return generate_path_with_odd_dimension(shape)

    # Use Prim's MST to generate an mst and a hamiltonian cycle
    half_shape = nav.create_pos(shape[Dmn.H] / 2, shape[Dmn.W] / 2)
    mst, visited, prim_path = generate_prim_mst(nav.create_pos(-1, -1), nav.create_pos(), half_shape, seed)

    if is_print_mst:
        print(f'mst: {mst},\nprim_path: {prim_path}')
        dirs = nav.get_dir_array()
        for i in range(mst.size):
            res = ''
            for dir in dirs:
                if nav.is_dir(mst[i], dir):
                    res = f'{res}, {dir}'
            print(f'edge[{i}]: {res}')
    return generate_hamilton_cycle(mst, shape)

def generate_prim_mst(prev_pos, pos, shape, seed, mst = None, visited = None, prim_path = None):
    '''
    recursively defined method to generate a minimum spanning tree, using Prim's algorithm

    Parameters
    ----------
    prev_pos : array
        previous mst node position from which to connect an edge

    pos : array
        current node position to be added to the mst and connect and edge to

    shape : array
        node shape HxW

    seed : integer, optional
        used to seed the default rng, by default is none

    mst : array, optional
        minimum spanning tree for which to add a node,
        indices are nodes, values are direction masks,
        default is None

    visited : array, optional
        keep trach of which node was visited, by default is None

    prim_path : list, optional
        contains the path constructed by the mst, by default is None

    Returns
    -------
    Tuple
        a tuple of the current mst, he visited nodes and the prim path
    '''
    if mst is None:
        mst = np.zeros(shape[Dmn.W] * shape[Dmn.H], dtype = np.int8)

    if visited is None:
        visited = np.zeros(len(mst), dtype = bool)

    if pos[Axis.X] < 0 or pos[Axis.Y] < 0 or pos[Axis.X] >= shape[Dmn.W] or pos[Axis.Y] >= shape[Dmn.H]:
        return (mst, visited, prim_path)

    curr_node_id = nav.get_node_id(pos, shape)

    if visited[curr_node_id]:
        return (mst, visited, prim_path)
    visited[curr_node_id] = True

    # Remove wall between fromX and fromY
    if prev_pos[Axis.X] != -1:
        prev_node_id = nav.get_node_id(prev_pos, shape)
        if prev_pos[Axis.X] < pos[Axis.X]:
            mst[prev_node_id] = nav.set_dir(mst[prev_node_id], Dir.Right)
            mst[curr_node_id] = nav.set_dir(mst[curr_node_id], Dir.Left)
        elif prev_pos[Axis.X] > pos[Axis.X]:
            mst[prev_node_id] = nav.set_dir(mst[prev_node_id], Dir.Left)
            mst[curr_node_id] = nav.set_dir(mst[curr_node_id], Dir.Right)
        elif prev_pos[Axis.Y] < pos[Axis.Y]:
            mst[prev_node_id] = nav.set_dir(mst[prev_node_id], Dir.Down)
            mst[curr_node_id] = nav.set_dir(mst[curr_node_id], Dir.Up)
        elif prev_pos[Axis.Y] > pos[Axis.Y]:
            mst[prev_node_id] = nav.set_dir(mst[prev_node_id], Dir.Up)
            mst[curr_node_id] = nav.set_dir(mst[curr_node_id], Dir.Down)
        if prim_path is None:
            prim_path = [prev_node_id]
        prim_path.append(curr_node_id)

    # We want to vist the four connected nodes randomly,
    # so we just visit two randomly (maybe already visited)
    # then just visit them all non-randomly. It's okay to
    # visit the same node twice.
    dir_array = nav.get_dir_array()
    seed_seq = np.random.SeedSequence(entropy = seed)
    rng = np.random.default_rng(seed_seq)

    for i in range(Axis.COUNT):
        dir = rng.choice(dir_array)
        next_pos = nav.get_next_pos(pos, dir)
        mst, visited, prim_path = generate_prim_mst(pos, next_pos, shape, seed, mst, visited, prim_path)

    for i in range(len(dir_array)):
        dir = dir_array[i]
        next_pos = nav.get_next_pos(pos, dir)
        mst, visited, prim_path = generate_prim_mst(pos, next_pos, shape, seed, mst, visited, prim_path)

    return (mst, visited, prim_path)

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
    '''
    hamilton_cycle = np.zeros(np.int64(shape[Dmn.W] * shape[Dmn.H]), dtype=np.int64)
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

        print(f'i -> {i}, y1: {y1}, y2: {y2}, id_1: {get_id(i, y1)}, id_2: {get_id(i, y2)}')
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

    print(f'turning_points: {turning_points}')
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