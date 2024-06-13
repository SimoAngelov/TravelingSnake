import arcade.color
import numpy as np
import arcade
from nav import Dir, Axis

def offset_coord(t, node_size):
    '''
    offset draw coordinate

    Parameters
    ----------
    t : integer
        draw coordinate to be offset

    node_size : integer
        the node size in pixels

    Returns
    -------
    integer
        the offset coordinate
    '''
    return np.int64(t) * node_size + node_size / 2


def get_coords(node_id, node_size, shape_w, height):
    '''
    get x, y pixel coordinates

    Parameters
    ----------
    node_id : integer
        node id of the square for which to retrieve the coordinates

    node_size : integer
        width and height of a node in pixels

    shape_w : integer
        number of nodes in the width dimension

    height : integer
        height of the screen in pixels

    Returns
    -------
    [x, y]: list
        a tuple of x, y pixel coordinates
    '''
    x = offset_coord(node_id % shape_w, node_size)
    y = height - offset_coord(node_id / shape_w, node_size)
    return [x, y]

def get_triangle_coords(coords, dir: Dir, node_size):
    '''
    get_triangle_coords

    Parameters
    ----------
    coords : list
        [x, y] coordinates of the triangle to be drawn

    dir : Dir
        direction which the triangle is facing

    node_size : integer
        width and height of a node in pixels

    Returns
    -------
    tr_coords : list
        retrieve a list of x1, y1, x2, y2, x3, y3 coordinates of the triangle

    Raises
    ------
    TypeError
        if dir isn't of type Dir
    '''
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    half = node_size * 0.5
    quart = node_size * 0.25
    offsets = {
        Dir.Down : [-quart, half, 0, -half, quart, half],
        Dir.Up: [-quart, -half, 0, half, quart, -half],
        Dir.Right: [-half, -quart, half, 0, -half, quart],
        Dir.Left: [half, -quart, -half, 0, half, quart],
    }
    offset = offsets.get(dir)
    tr_coords = []
    for i in range(len(offset)):
        if i % 2 == 0:
            tr_coords.append(coords[Axis.X] + offset[i])
        else:
            tr_coords.append(coords[Axis.Y] + offset[i])
    return tr_coords

def draw_triangle(coords, dir: Dir, node_size, color):
    '''
    draw a triangle

    Parameters
    ----------
    coords : list
        [x, y] coordinates of the triangle to be drawn

    dir : Dir
        direction which the triangle is facing

    node_size : integer
        width and height of a node in pixels

    color : tuple
        (r, g, b) color of the string

    Raises
    ------
    TypeError
        if dir isn't of type Dir
    '''
    if not isinstance(dir, Dir):
        raise TypeError("dir is not type Dir")
    tr_coords = get_triangle_coords(coords, dir, node_size)
    arcade.draw_triangle_filled(tr_coords[0], tr_coords[1], tr_coords[2],
                                tr_coords[3], tr_coords[4], tr_coords[5], color)

def draw_square(coords, node_size, color):
    '''
    draw a square on the screen

    Parameters
    ----------
    coords : list
        [x, y] coordinates of the square to be drawn

    node_size : integer
        width and height of a square node in pixels

    color : tuple
        (r, g, b) color of the square
    '''
    arcade.draw_rectangle_filled(coords[Axis.X], coords[Axis.Y], node_size, node_size, color)

def draw_segment(coords, prev_dir: Dir, next_dir: Dir, node_size, color):
    '''
    draw line segment with a bend

    Parameters
    ----------
    coords : list
        [x, y] center coordinates

    prev_dir : Dir
        previous direction of the line segment

    next_dir : Dir
        next direction of the line segment

    node_size : integer
        width and height of a node in pixels

    color : tuple
        (r, g, b) color of the square
    '''
    def get_coords(dir: Dir):
        half = node_size * 0.5
        offsets = { Dir.Up : [0, half], Dir.Down : [0, -half], Dir.Left: [-half, 0], Dir.Right: [half, 0] }
        offset = offsets.get(dir, [0, 0])
        new_coords = [sum(x) for x in zip(coords, offset)]
        return new_coords
    prev_coords = get_coords(prev_dir)
    next_coords = get_coords(next_dir)
    points_list = ((prev_coords[Axis.X], prev_coords[Axis.Y]),
                   (coords[Axis.X], coords[Axis.Y]),
                   (next_coords[Axis.X], next_coords[Axis.Y]),
    )
    arcade.draw_line_strip(points_list, color, node_size * 0.5)

def draw_cirle(node_id, node_size, shape_w, height, color):
    '''
    draw a circle

    Parameters
    ----------
    node_id : integer
        node id of the square for which to retrieve the coordinates

    node_size : integer
        width and height of a node in pixels

    shape_w : integer
        number of nodes in the width dimension

    height : integer
        height of the screen in pixels

    color : tuple
        (r, g, b) color of the circle
    '''
    coords = get_coords(node_id, node_size, shape_w, height)
    arcade.draw_circle_filled(coords[Axis.X], coords[Axis.Y], node_size * 0.5, color)

def draw_tail(coords, dir: Dir, node_size, color):
    '''
    draw snake tail segment

    Parameters
    ----------
    coords : list
        [x, y] center coordinates

    dir : Dir
        direction which the tail is facing

    node_size : integer
        with and height of a node in pixels

    color : tuple
        (r, g, b) color of the tail
    '''
    half = node_size * 0.5
    quart = node_size * 0.25
    dir_offsets = {
        Dir.Up: ((-quart, half), (-quart, -half,), (0, 0), (quart, -half), (quart, half)),
        Dir.Down: ((-quart, -half), (-quart, half), (0, 0), (quart, half), (quart, -half)),
        Dir.Left: ((-half, quart), (half, quart), (0, 0), (half, -quart), (-half, -quart)),
        Dir.Right: ((half, quart), (-half, quart), (0, 0), (-half, -quart), (half, -quart))
    }
    offsets = dir_offsets.get(dir)
    coords = tuple(coords)
    tail_coords = ()
    for offset in offsets:
        tail_coord = tuple(map(sum, zip(offset, coords)))
        tail_coords += (tail_coord,)
    arcade.draw_polygon_filled(tail_coords, color)