import numpy as np
import nav
from nav import Dir, Axis

def generate_path(shape, is_print_edges = False):
    '''
    generate_path - generate hamiltonian path
    @param shape - node shape WxH
    @return an array which is the hamiltonian path. The values are node ids
    '''
    half_shape = nav.create_pos(shape[Axis.X] / 2, shape[Axis.Y] / 2)
    edges = np.zeros(half_shape[Axis.X] * half_shape[Axis.Y], dtype=np.int8)
    visited = np.zeros(len(edges), dtype=bool)
    edges = generate_edges(nav.create_pos(-1, -1), nav.create_pos(),
                            half_shape, edges, visited)

    if is_print_edges:
        dirs = nav.get_dir_array()
        for i in range(edges.size):
            res = ''
            for dir in dirs:
                if nav.is_dir(edges[i], dir):
                    res = f'{res}, {dir}'
            print(f'edge[{i}]: {res}')
    return generate_hamilton_cycle(edges, shape)

def generate_edges(prev_pos, pos, shape, edges, visited):
    '''
    generate_edges - recursively defined method to generate node edges
    @param prev_pos - previous position from which to connect an edge
    @param pos - current position to which to connect an edge
    @param shape - node shape WxH
    @param edges - output parameter. Edges to be set at the specified positions
    @param visited - output parameter. Keep trach of which node was visited
    '''
    if pos[Axis.X] < 0 or pos[Axis.Y] < 0 or pos[Axis.X] >= shape[Axis.X] or pos[Axis.Y] >= shape[Axis.Y]:
        return

    curr_node_id = nav.get_node_id(pos, shape)

    if visited[curr_node_id]:
        return
    visited[curr_node_id] = True

    # Remove wall between fromX and fromY
    if prev_pos[Axis.X] != -1:
        prev_node_id = nav.get_node_id(prev_pos, shape)
        if prev_pos[Axis.X] < pos[Axis.X]:
            edges[prev_node_id] = nav.set_dir(edges[prev_node_id], Dir.Right)
            edges[curr_node_id] = nav.set_dir(edges[curr_node_id], Dir.Left)
        elif prev_pos[Axis.X] > pos[Axis.X]:
            edges[prev_node_id] = nav.set_dir(edges[prev_node_id], Dir.Left)
            edges[curr_node_id] = nav.set_dir(edges[curr_node_id], Dir.Right)
        elif prev_pos[Axis.Y] < pos[Axis.Y]:
            edges[prev_node_id] = nav.set_dir(edges[prev_node_id], Dir.Down)
            edges[curr_node_id] = nav.set_dir(edges[curr_node_id], Dir.Up)
        elif prev_pos[Axis.Y] > pos[Axis.Y]:
            edges[prev_node_id] = nav.set_dir(edges[prev_node_id], Dir.Up)
            edges[curr_node_id] = nav.set_dir(edges[curr_node_id], Dir.Down)


    # We want to vist the four connected nodes randomly,
    # so we just visit two randomly (maybe already visited)
    # then just visit them all non-randomly. It's okay to
    # visit the same node twice.
    dir_array = nav.get_dir_array()
    rng = np.random.default_rng()

    for i in range(Axis.COUNT):
        dir = rng.choice(dir_array)
        next_pos = nav.get_next_pos(pos, dir)
        generate_edges(pos, next_pos, shape, edges, visited)

    for i in range(len(dir_array)):
        dir = dir_array[i]
        next_pos = nav.get_next_pos(pos, dir)
        generate_edges(pos, next_pos, shape, edges, visited)
    return edges

def generate_hamilton_cycle(edges, shape):
    '''
    generate_hamilton_cycle - generate a hamiltonian cycle from the specified edges
    @param edges - valid edges between nodes
    @param shape - node shape WxH
    @return an array which is the hamiltonian cycle from the specified edges. The values are edges
    '''
    hamilton_cycle = np.zeros(np.int64(shape[Axis.X] * shape[Axis.Y]), dtype=np.int64)
    def can_go(dir, pos):
        node_id = nav.get_node_id(pos, shape / 2)
        if node_id >= edges.size:
            return False
        return nav.is_dir(edges[node_id], dir)

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
    find_next_dir - find the next direction we can
    go from the current position
    @param pos - current position
    @param dir - direction we're currently facing
    @param can_go - predicate to determine, if we can
    go in a certain position
    @return the next direction we should go from the
    current position
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
    set_path_square - set a path square at the specified position
    @param path - output parameter. Path for which to set the square
    @param path_square - square to be set
    @param pos - node position at which to set the square
    @param shape - node shape WxH
    '''
    node_id = nav.get_node_id(pos, shape)
    if (path[node_id] == 0):
        path[node_id] = path_square