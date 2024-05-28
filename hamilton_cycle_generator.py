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

def get_next_pos(pos, dir : Dir):
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    offsets = {
        Dir.Up : np.array([0, 1]),
        Dir.Right: np.array([1, 0]),
        Dir.Down : np.array([0, -1]),
        Dir.Left : np.array([-1, 0])
    }
    next_pos = pos + offsets.get(dir, np.zeros(Axis.COUNT))
    return next_pos

def is_dir(mask : np.int8, dir : Dir):
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    return bool((mask >> dir.value) & 1)

def set_dir(mask : np.int8, dir : Dir):
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    return mask | 1 << dir.value

def get_square(pos, w : np.int64):
    return np.int64(pos[Axis.X] + pos[Axis.Y] * w)


def generate(w, h):
    hamilton_cycle = np.zeros(np.int64(w * h), dtype=np.int64)
    transitions = np.zeros(np.int64((w / 2) * (h / 2)), dtype=np.int8)
    transitions = generate_r([-1, -1], [0, 0], w / 2, h / 2, transitions)
    print(f'generate(w: {w}, h: {h}), transitions: {transitions}')
    return hamilton_cycle


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

def generate_hamilton_cycle():
    pass