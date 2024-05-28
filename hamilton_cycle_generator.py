import numpy as np
from enum import Enum

X = 0
Y = 1

class Dir(Enum):
    Up = 0
    Down = 1
    Left = 2
    Right = 3

def get_next_pos(x, y, dir : Dir):
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    offsets = {
        Dir.Up : (0, 1),
        Dir.Down : (0, -1),
        Dir.Left : (-1, 0),
        Dir.Right: (1, 0)
    }
    offset_x, offset_y = offsets.get(dir, (0, 0))
    return x + offset_x, y + offset_y

def is_dir(mask : np.int8, dir : Dir):
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    return bool((mask >> dir.value) & 1)

def set_dir(mask : np.int8, dir : Dir):
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    return mask | 1 << dir.value

def get_square(x : np.int64, y : np.int64, w : np.int64):
    return np.int64(x + y * w)

hamilton_cycle = np.empty(shape = 0, dtype=np.int8)
transitions = np.empty(shape = 0, dtype=np.int8)


def generate(w, h):
    w /= 2
    h /= 2
    size = np.int64(w * h)
    hamilton_cycle = np.zeros(size)
    transitions = np.zeros(size, dtype=np.int8)
    transitions = generate_r(-1, -1, 0, 0, w, h, transitions)
    print(f'generate(w: {w}, h: {h}), transitions: {transitions}')


def generate_r(fromX : np.int64, fromY : np.int64, x : np.int64, y : np.int64,
                w : np.int64, h : np.int64, transitions):
    if x < 0 or y < 0 or x >= w or y >= h:
        return transitions
    square = get_square(x, y, w)
    trans = transitions[square]

    if trans != 0:
        return transitions

    # Remove wall between fromX and fromY
    if fromX != -1:
        if fromX > x: trans = set_dir(trans, Dir.Left)
        if fromX < x: trans = set_dir(trans, Dir.Right)
        if fromY > y: trans = set_dir(trans, Dir.Down)
        if fromY < y: trans = set_dir(trans, Dir.Up)
    transitions[square] = trans


    # We want to vist the fource connected nodes randomly,
    # so we just visit two randomly (maybe already visited)
    # then just visit them all non-randomly. It's okay to
    # visit the same node twice.
    directions_array = np.array(Dir)
    rng = np.random.default_rng()
    for i in range(2):
        dir = rng.choice(directions_array)
        next_x, next_y = get_next_pos(x, y, dir)
        transitions = generate_r(x, y, next_x, next_y, w, h, transitions)

    for i in range(len(directions_array)):
        dir = directions_array[i]
        next_x, next_y = get_next_pos(x, y, dir)
        transitions = generate_r(x, y, next_x, next_y, w, h, transitions)

    return transitions
