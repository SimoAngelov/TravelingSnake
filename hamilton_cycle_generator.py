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
        Dir.Up: create_pos(y = 1),
        Dir.Right: create_pos(x = 1),
        Dir.Down: create_pos(y = -1),
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

def get_square(pos, w: np.int64):
    return np.int64(pos[Axis.X] + pos[Axis.Y] * w)

def generate(w, h):
    transitions = np.zeros(np.int64((w / 2) * (h / 2)), dtype=np.int8)
    transitions = generate_r([-1, -1], [0, 0], w / 2, h / 2, transitions)
    print(f'generate(w: {w}, h: {h}), transitions: {transitions}')
    return generate_hamilton_cycle(w, h, transitions)

def create_pos(x = 0, y = 0):
    return np.array([x, y], dtype = np.int64)

def generate_r(prev_pos, pos, w, h, transitions):
    if pos[Axis.X] < 0 or pos[Axis.Y] < 0 or pos[Axis.X] >= w or pos[Axis.Y] >= h:
        return transitions
    square = get_square(pos, w)
    trans = transitions[square]

    if trans != 0:
        return transitions

    # Remove wall between fromX and fromY
    if prev_pos[Axis.X] != -1:
        if prev_pos[Axis.X] > pos[Axis.X]: trans = set_dir(trans, Dir.Left)
        if prev_pos[Axis.X] < pos[Axis.X]: trans = set_dir(trans, Dir.Right)
        if prev_pos[Axis.Y] > pos[Axis.Y]: trans = set_dir(trans, Dir.Down)
        if prev_pos[Axis.Y] < pos[Axis.Y]: trans = set_dir(trans, Dir.Up)
    transitions[square] = trans

    # We want to vist the fource connected nodes randomly,
    # so we just visit two randomly (maybe already visited)
    # then just visit them all non-randomly. It's okay to
    # visit the same node twice.
    directions_array = np.array(Dir)
    rng = np.random.default_rng()
    for i in range(Axis.COUNT):
        dir = rng.choice(directions_array)
        next_pos = get_next_pos(pos, dir)
        transitions = generate_r(pos, next_pos, w, h, transitions)

    for i in range(len(directions_array)):
        dir = directions_array[i]
        next_pos = get_next_pos(pos, dir)
        transitions = generate_r(pos, next_pos, w, h, transitions)

    return transitions

def generate_hamilton_cycle(w, h, transitions):
    hamilton_cycle = np.zeros(np.int64(w * h), dtype=np.int64)
    can_go = lambda dir, pos: is_dir(transitions[get_square(pos, w)], dir)
    start_pos = create_pos()
    pos = np.copy(start_pos)
    start_dir = Dir.Up if can_go(Dir.Down, pos) else Dir.Left
    dir = start_dir
    curr_square = 0

    while True:
        next_dir = dir # todo implement find_next_dir
        #todo set hamilton_cycle at current square
        curr_square += 1
        dir = next_dir
        pos = get_next_pos(pos, next_dir)

        pos_squared = pos ** 2


        # Terminate generator loop
        if curr_square >= hamilton_cycle.size:
            break