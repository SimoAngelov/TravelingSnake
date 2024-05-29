import numpy as np
from enum import Enum, IntEnum

class Axis(IntEnum):
    X = 0
    Y = 1
    COUNT = 2

class Dir(Enum):
    Up = 0
    Right = 1
    Down = 2
    Left = 3

def get_next_pos(pos, dir: Dir):
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    offsets = {
        Dir.Up: create_pos(y = -1),
        Dir.Right: create_pos(x = 1),
        Dir.Down: create_pos(y = 1),
        Dir.Left: create_pos(x = -1)
    }
    next_pos = pos + offsets.get(dir, create_pos())
    return next_pos

def is_dir(mask: np.int8, dir: Dir):
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    return bool((mask >> dir.value) & 1)

def set_dir(mask: np.int8, dir: Dir):
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    return mask | 1 << dir.value

def get_dir_array(start: Dir = Dir.Up, offset = 0):
    if not isinstance(start, Dir):
        raise TypeError("start is not type Dir")
    dir_array = np.array(Dir)
    dir_array = np.roll(dir_array, -start.value + offset)
    return dir_array

def get_square(pos, w: np.int64):
    square = np.int64(pos[Axis.X] + pos[Axis.Y] * w)
    return square

def generate(w, h):
    half_w = np.int64(w / 2)
    half_h = np.int64(h / 2)
    edges = np.zeros(half_w * half_h, dtype=np.int8)
    visited = np.zeros(len(edges), dtype=bool)
    edges = generate_edges(create_pos(-1, -1), create_pos(),
                            half_w, half_h, edges, visited)
    print(f'generate(w: {w}, h: {h}), edges: {edges}')

    dirs = get_dir_array()
    for i in range(edges.size):
        res = ''
        for dir in dirs:
            if is_dir(edges[i], dir):
                res = f'{res}, {dir}'
        print(f'edge[{i}]: {res}')
    return generate_hamilton_cycle(w, h, edges)

def create_pos(x = 0, y = 0):
    return np.array([x, y], dtype = np.int64)

def find_next_dir(pos, dir: Dir, can_go):
    # start the array by rolling it one position, so it starts
    # from left neighbor of dir
    next_dir_array = get_dir_array(dir, 1)
    for i in range(next_dir_array.size - 1):
        # check if we can go in any of the first 3 directions
        next_dir = next_dir_array[i]
        if can_go(next_dir, pos):
            return next_dir
    # return the inverted dir
    return next_dir_array[-1]

def get_path_square(path, pos, w):
    square = get_square(pos, w)
    return path[square]

def set_path_square(path, path_square, pos, w):
    square = get_square(pos, w)
    if (path[square] == 0):
        path[square] = path_square

def generate_edges(prev_pos, pos, w, h, edges, visited):
    if pos[Axis.X] < 0 or pos[Axis.Y] < 0 or pos[Axis.X] >= w or pos[Axis.Y] >= h:
        return

    curr_square = get_square(pos, w)

    if visited[curr_square]:
        return
    visited[curr_square] = True

    # Remove wall between fromX and fromY
    if prev_pos[Axis.X] != -1:
        prev_square = get_square(prev_pos, w)
        if prev_pos[Axis.X] < pos[Axis.X]:
            edges[prev_square] = set_dir(edges[prev_square], Dir.Right)
            edges[curr_square] = set_dir(edges[curr_square], Dir.Left)
        elif prev_pos[Axis.X] > pos[Axis.X]:
            edges[prev_square] = set_dir(edges[prev_square], Dir.Left)
            edges[curr_square] = set_dir(edges[curr_square], Dir.Right)
        elif prev_pos[Axis.Y] < pos[Axis.Y]:
            edges[prev_square] = set_dir(edges[prev_square], Dir.Down)
            edges[curr_square] = set_dir(edges[curr_square], Dir.Up)
        elif prev_pos[Axis.Y] > pos[Axis.Y]:
            edges[prev_square] = set_dir(edges[prev_square], Dir.Up)
            edges[curr_square] = set_dir(edges[curr_square], Dir.Down)


    # We want to vist the four connected nodes randomly,
    # so we just visit two randomly (maybe already visited)
    # then just visit them all non-randomly. It's okay to
    # visit the same node twice.
    directions_array = np.array(Dir)
    rng = np.random.default_rng()

    for i in range(Axis.COUNT):
        dir = rng.choice(directions_array)
        next_pos = get_next_pos(pos, dir)
        generate_edges(pos, next_pos, w, h, edges, visited)

    for i in range(len(directions_array)):
        dir = directions_array[i]
        next_pos = get_next_pos(pos, dir)
        generate_edges(pos, next_pos, w, h, edges, visited)

    return edges

def generate_hamilton_cycle(w, h, edges):
    hamilton_cycle = np.zeros(np.int64(w * h), dtype=np.int64)
    def can_go(dir, pos):
        square = get_square(pos, w / 2)
        if square >= edges.size:
            return False
        return is_dir(edges[square], dir)

    pos = create_pos()
    dir = Dir.Up if can_go(Dir.Down, pos) else Dir.Left
    curr_square = 0
    start_offsets = np.array([create_pos(y = 1), create_pos(), create_pos(x = 1), create_pos(1, 1)])

    while True:
        next_dir = find_next_dir(pos, dir, can_go)
        pos_double = pos * 2

        # set the current path square
        dir_array = get_dir_array(dir)
        offsets = np.roll(start_offsets, -dir.value, Axis.X)
        offsets_len = len(offsets)

        set_path_square(hamilton_cycle, curr_square, pos_double + offsets[0], w)
        curr_square += 1

        for i in range(1, offsets_len):
            indices = [j + i - 1 for j in range(offsets_len - i)]
            directions = dir_array[indices]
            if next_dir in directions:
                set_path_square(hamilton_cycle, curr_square, pos_double + offsets[i], w)
                curr_square += 1

        dir = next_dir
        pos = get_next_pos(pos, next_dir)

        # Terminate generator loop
        if curr_square >= hamilton_cycle.size:
            break

    return hamilton_cycle