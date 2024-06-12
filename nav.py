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
    move from the current position in the specified direction

    Parameters
    pos : array
        current position

    dir : Dir
        direction of the next position

    Returns
    -------
    next_pos : array
        the next position in that direction

    Raises
    ------
    TypeError
        if pos ins't an array type
        if dir isn't of type Dir
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
    query whether the mask contains the direction
    Parameters
    ----------
    mask : integer
        mask to be queried

    dir : Dir
        direction to be queried

    Returns
    -------
    bool
        true, if the mask contains the direction

    Raises
    ------
    TypeError
        If dir isn't of type Dir
    '''
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    return bool((mask >> dir.value) & 1)

def set_dir(mask: np.int8, dir: Dir):
    '''
    set the specified direction

    Parameters
    ----------
    mask : integer
        mask to be set

    dir : Dir
        direction to be set

    Returns
    -------
    integer
        the newly set mask

    Raises
    ------
    TypeError
        If dir isn't of type Dir
    '''
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    return mask | 1 << dir.value

def get_dir_array(start: Dir = Dir.Up, offset = 0):
    '''
    retrieve an array of directions

    Parameters
    ----------
    start : Dir, optional
        first element of the array, by default is Dir.Up

    offset : integer, optional,
        how much to offset start, so a new direction is first,
        by default is 0

    Returns
    -------
    dir_array : array
        an array of directions

    Raises
    ------
    TypeError
        If start isn't of type Dir
    '''
    if not isinstance(start, Dir):
        raise TypeError("start is not type Dir")
    dir_array = np.array(Dir)
    dir_array = np.roll(dir_array, -start.value + offset)
    return dir_array

def create_pos(x = 0, y = 0):
    '''
    create x, y position array

    Parameters
    ----------
    x component : integer, optional
        x component, default value is 0

    y : integer, optional
        y component, default value is 0

    Returns
    -------
    array
        an array with the x, y values
    '''
    return np.array([x, y], dtype = np.int64)

def create_random_pos(shape):
    x_rand = np.random.randint(shape[Dmn.W])
    y_rand = np.random.randint(shape[Dmn.H])
    return create_pos(x_rand, y_rand)

def get_node_pos(id, shape):
    '''
    retrieve the position of the specified node

    Parameters
    ----------
    id : integer
        id of the node ot be queried

    shape : array
        node shape WxH

    Returns
    -------
    array
        an of x, y node position in the shape grid
    '''
    x = np.int64(id % shape[Dmn.W])
    y = np.int64(id / shape[Dmn.W])
    return create_pos(x, y)

def get_node_id(pos, shape):
    '''
    retrieve the id of the node at the specified position

    Parameters
    ----------
    pos : array
        node x,y position

    shape : array
        node shape HxW

    Returns
    -------
    node_id : integer
        the id of the node at the specified position
        If pos is out of the bounds of shape, None is returned
    '''
    if pos[Axis.X] < 0 or pos[Axis.X] >= shape[Dmn.W] or pos[Axis.Y] < 0 or pos[Axis.Y] >= shape[Dmn.H]:
        return None

    node_id = np.int64(pos[Axis.X] + pos[Axis.Y] * shape[Dmn.W])
    return node_id

def get_next_node_id(node_id, dir, shape):
    '''
    retrieve the next node id from the current one

    Parameters
    ----------
    node_id : integer
        current node id

    dir : Dir
        direction in which to move from node_id

    shape : array
        node shape HxW

    Returns
    -------
    next_node_id : integer
        the next node id in the direction of the current one
        If next_pos is out of the bounds of shape, None is returned
    '''
    curr_pos = get_node_pos(node_id, shape)
    next_pos = get_next_pos(curr_pos, dir)
    next_node_id = get_node_id(next_pos, shape)
    return next_node_id

def get_dir_between(start, end, node_shape):
    '''
    retrieve the direction between two nodes

    Parameters
    ----------
    start : integer
        start node id

    end : integer
        end node ide
    node_shape : array
        node shape HxW

    Returns
    -------
    dir : Dir
        the direction between start and end, if found.
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
    retrieve the path distance between two nodes

    Parameters
    ----------
    start_node : integer
        id of the start node

    end_node : integer
        id of the end node

    shape : array
        node shape HxW

    Returns
    -------
    integer
        the distance between the two nodes
    '''
    if (start_node < end_node):
        return end_node - start_node - 1
    return end_node - start_node - 1 + shape[Dmn.W] * shape[Dmn.H]

def is_out_of_bounds(pos, shape):
    '''
    query whether the position is out of the bounds of shape

    Parameters
    ----------
    pos : array
        x, y position to be queried

    shape : array
        node shape HxW

    Returns
    -------
    bool
        true, if the position is out of the bounds of shape, false otherwise
    '''
    return pos[Axis.X] < 0 or pos[Axis.Y] < 0 or pos[Axis.X] >= shape[Dmn.W] or pos[Axis.Y] >= shape[Dmn.H]