import numpy as np
from enum import Enum, IntEnum

class Axis(IntEnum):
    ''' Enumerate axis '''

    X = 0
    ''' X axis '''

    Y = 1
    ''' Y Axis '''

    COUNT = 2
    ''' number of axes '''

class Dmn(IntEnum):
    ''' Enumerate dimensions '''
    H = 0
    ''' height '''

    W = 1
    ''' width '''

class Dir(Enum):
    '''  Enumerate directions '''
    Up = 0
    ''' Up direction '''
    Right = 1
    ''' Right direction '''
    Down = 2
    ''' Down direction '''
    Left = 3
    ''' Left direction '''

def get_next_pos(pos, dir: Dir):
    '''
    get_next_pos - move from the current position
    in the specified direction
    @param pos - current position
    @param dir - direction of the next position
    @return the next position in that direction
    '''
    if not isinstance(pos, np.ndarray):
        raise TypeError("pos is not array type")
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
    '''
    is_dir - query whether the mask contains the direction
    @param mask - mask to be queried
    @param dir - direction to be queried
    @return true, if the mask contains the direction
    '''
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    return bool((mask >> dir.value) & 1)

def set_dir(mask: np.int8, dir: Dir):
    '''
    set_dir - set the specified direction
    @param mask - mask to be set
    @param dir - direction to be set
    @return the newly set mask
    '''
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    return mask | 1 << dir.value

def get_dir_array(start: Dir = Dir.Up, offset = 0):
    '''
    get_dir_array - retrieve an array of directions
    @param start - first element of the array
    @param offset - how much to offset start,
    so a new direction is first
    @return an array of directions
    '''
    if not isinstance(start, Dir):
        raise TypeError("start is not type Dir")
    dir_array = np.array(Dir)
    dir_array = np.roll(dir_array, -start.value + offset)
    return dir_array

def create_pos(x = 0, y = 0):
    '''
    create_pos - create x, y position array
    @param x - x component
    @param y - y component
    @return an array with the x, y values
    '''
    return np.array([x, y], dtype = np.int64)

def get_node_pos(id, shape):
    '''
    get_node_pos - retrieve the position of the specified node
    @param id - id of the node ot be queried
    @param shape - node shape WxH
    @return a tuple of x, y node position in the shape grid
    '''
    x = np.int64(id % shape[Dmn.W])
    y = np.int64(id / shape[Dmn.W])
    return create_pos(x, y)

def get_node_id(pos, shape):
    '''
    get_node_id - retrieve the id of the node at the specified position
    @param pos - node x,y position
    @param shape - node shape WxH
    @return the id of the node at the specified position
    '''
    node_id = np.int64(pos[Axis.X] + pos[Axis.Y] * shape[Dmn.W])
    return node_id

def get_next_node_id(node_id, dir, shape):
    '''
    get_next_node_id - retrieve the next node id from the current one
    @param node_id - current node id
    @param dir - direction in which to move from node_id
    @param shape - node shape WxH
    @return the next node id in the direction of the current one
    '''
    curr_pos = get_node_pos(node_id, shape)
    next_pos = get_next_pos(curr_pos, dir)
    next_node_id = get_node_id(next_pos, shape)
    return next_node_id

def get_dir_between(start, end, node_shape):
    '''
    get_dir_between - retrieve the direction between two nodes.
    @param start - start node
    @param end - end node
    @param node_shape - node shape WxH
    @return the direction between start and end, if found.
    Otherwise return None
    '''
    start_pos = get_node_pos(start, node_shape)
    end_pos = get_node_pos(end, node_shape)

    dir = None
    if start_pos[Axis.X] != end_pos[Axis.X]:
        dir = Dir.Right if start_pos[Axis.X] - end_pos[Axis.X] < 0 else Dir.Left
    elif start_pos[Axis.Y] != end_pos[Axis.Y]:
        dir = Dir.Down if start_pos[Axis.Y] - end_pos[Axis.Y] < 0 else Dir.Up
    return dir

def path_distance(start_node, end_node, shape):
    '''
    path_distance - retrieve the path distance between two nodes
    @param start_node - id of the start node
    @param end_node - id of the end node
    @return the distance between the two nodes
    '''
    if (start_node < end_node):
        return end_node - start_node - 1
    return end_node - start_node - 1 + shape[Dmn.W] * shape[Dmn.H]

def is_out_of_bounds(pos, shape):
    '''
    is_out_of_bounds - query whether the position is out of the bounds of shape
    @param pos - x, y position to be queried.
    @param shape - node shape WxH
    @return true, if the position is out of the bounds of shape
    '''
    return pos[Axis.X] < 0 or pos[Axis.Y] < 0 or pos[Axis.X] >= shape[Dmn.W] or pos[Axis.Y] >= shape[Dmn.H]