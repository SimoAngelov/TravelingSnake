import numpy as np
import arcade
import nav
from nav import Dir, Axis, Dmn


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

def create_point_list(coords, offsets):
    '''
    create a point list

    Parameters
    ----------
    coords : tuple
        (x, y) pixel coordinates

    offsets : tuple
        tuple of (x, y) tuple offsets

    Returns
    -------
    point_list : PointList
        a point list from the specified coordinates and offsets
    '''
    point_list = ()
    for offset in offsets:
        point = tuple(map(sum, zip(offset, coords)))
        point_list += (point,)
    return point_list


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
    [x, y]: tuple
        (x, y) tuple of pixel coordinates
    '''
    x = offset_coord(node_id % shape_w, node_size)
    y = height - offset_coord(node_id / shape_w, node_size)
    return (x, y)

def create_snake_head(coords, dir: Dir, node_size, color):
    '''
    create a snake head shape

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

    Returns
    snake_head : Shape
        a snake head shape

    Raises
    ------
    TypeError
        if dir isn't of type Dir
    '''
    if not isinstance(dir, Dir):
        raise TypeError("dir: {dir} isn't of type Dir")
    half = node_size * 0.5
    quart = node_size * 0.25
    dir_offsets = {
        Dir.Up: ((-quart, -half), (0, half), (quart, -half)),
        Dir.Down : ((-quart, half), (0, -half), (quart, half)),
        Dir.Left: ((half, -quart), (-half, 0), (half, quart)),
        Dir.Right: ((-half, -quart), (half, 0), (-half, quart)),
    }
    offsets = dir_offsets.get(dir)
    point_list = create_point_list(coords, offsets)
    color_list = [color] * len(point_list)
    snake_head = arcade.create_triangles_filled_with_colors(point_list, color_list)
    return snake_head

def create_food(node_id, node_size, shape_w, height, color = arcade.color.RED_VIOLET):
    '''
    create a food shape

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

    color : tuple, optional
        (r, g, b) color of the circle, by default is RED_VIOLET

    Returns
    -------
    food : Shape
        a food circle
    '''
    coords = get_coords(node_id, node_size, shape_w, height)
    food = arcade.create_ellipse_filled(coords[Axis.X], coords[Axis.Y], node_size, node_size, color)
    return food

def create_snake_body_segment(coords, prev_dir: Dir, next_dir: Dir, node_size, color):
    '''
    create a snake body segment shape

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

    Returns:
    -------
    body_segment : Shape
        a snake body segment shape

    Raises
    ------
    TypeError
        if prev_dir or next_dir aren't of type Dir
    '''
    if not isinstance(prev_dir, Dir) or not isinstance(next_dir, Dir):
        raise TypeError("prev_dir: {prev_dir} or next_dir: {next_dir} are not of type Dir")
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
    body_segment = arcade.create_line_strip(points_list, color, node_size * 0.5)
    return body_segment

def create_snake_tail(coords, dir: Dir, node_size, color):
    '''
    create a snake tail shape

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

    Returns
    -------
    tail_segments : list of Shape objects
        a snake tail shape list

    Raises
    ------
    TypeError
        if dir isn't of type Dir
    '''
    if not isinstance(dir, Dir):
        raise TypeError("dir: {dir} isn't of type Dir")
    half = node_size * 0.5
    quart = node_size * 0.25
    dir_offsets = {
        Dir.Up: ((-quart, half), (-quart, -half,), (0, 0), (quart, -half), (quart, half)),
        Dir.Down: ((-quart, -half), (-quart, half), (0, 0), (quart, half), (quart, -half)),
        Dir.Left: ((-half, quart), (half, quart), (0, 0), (half, -quart), (-half, -quart)),
        Dir.Right: ((half, quart), (-half, quart), (0, 0), (-half, -quart), (half, -quart))
    }
    offsets = dir_offsets.get(dir)
    point_list = create_point_list(coords, offsets)
    tail = arcade.create_polygon(point_list, color)
    tr = arcade.create_triangles_filled_with_colors((point_list[1], point_list[2], point_list[3]),
                                                    [arcade.color.BLACK] * 3)
    tail_segments = [tail, tr]
    return [tail, tr]


def create_snake_list(snake_arr, snake_head_dir : Dir, node_size, node_shape, screen_height,
                      offset = None):
    '''
    create a snake shape element list

    Parameters
    ----------
    snake_arr : array
        array of node ids occupied by the snake

    snake_head_dir : Dir
        direction the snake head is pointing to

    node_size : integer
        with and height of a node in pixels

    node_shape : array
        node shape HxW - number of nodes in the height and width dimensions

    screen_height : integer
        the height of the screen in pixels

    offset : list, optional
        [x, y] offset the snake list in the X-Y axis, by default is None

    Returns
    -------
    snake_list : ShapeElementList
        a list of snake body shapes

    Raises
    ------
    TypeError
        if snake_head_dir isn't of type Dir
    '''
    if not isinstance(snake_head_dir, Dir):
        raise TypeError("snake_head_dir: {snake_head_dir} isn't of type Dir")
    snake_list = arcade.ShapeElementList()
    snake_len = len(snake_arr)
    for i in range(snake_len):
        j = snake_len - 1 - i
        square = snake_arr[j]
        coords = get_coords(square, node_size, node_shape[Dmn.W], screen_height)

        color = arcade.color.ALIZARIN_CRIMSON if j == 0 else arcade.color.UFO_GREEN
        segments = []
        if j == 0:
            segments = [create_snake_head(coords, snake_head_dir, node_size, color)]
        elif j == snake_len -1:
            dir = nav.get_dir_between(square, snake_arr[j-1], node_shape)
            segments = create_snake_tail(coords, dir, node_size, color)
        else:
            prev_dir = nav.get_dir_between(square, snake_arr[j-1], node_shape)
            next_dir = nav.get_dir_between(square, snake_arr[j+1], node_shape)
            segments = [create_snake_body_segment(coords, prev_dir, next_dir, node_size, color)]
        for segment in segments:
            snake_list.append(segment)
    if offset is not None:
        snake_list.move(offset[Axis.X], offset[Axis.Y])
    return snake_list

def create_path_lists(path, node_size, node_shape, screen_width, screen_height,
                      offset = None,
                      color = arcade.color.WHITE, font_size = None,
                      align = "center"):
    '''
    create path lists

    Parameters
    ----------
    path : array
        array of node ids that compromise the path

    node_size : integer
        with and height of a node in pixels

    node_shape : array
        node shape HxW - number of nodes in the height and width dimensions

    screen_width : integer
        the width of the screen in pixels

    screen_height : integer
        the height of the screen in pixels

    offset : list, optional
        [x, y] offset the lists in the X-Y axis, by default is None

    color : tuple, optional
        (r, g, b) color of the text and grid, by default is White

    font_size : integer, optional
        size of the text, by default is 10

    align : string, optional
        alignment of the text, by default is "center"

    Returns
    -------
    path_lists : tuple
        a tuple of the text sprite list and the grid shape list
    '''
    if font_size is None:
        font_size = node_size // 2

    path_sprite_list = arcade.SpriteList()
    for i in range(len(path)):
        coords = get_coords(i, node_size, node_shape[Dmn.W], screen_height)
        text_x = coords[Axis.X] - node_size * 0.5
        text_y = coords[Axis.Y] - node_size * 0.5
        sprite = arcade.create_text_sprite(f'{path[i]}', text_x, text_y, color, font_size,
                                           align=align, width=node_size)
        path_sprite_list.append(sprite)

    path_shape_list = arcade.ShapeElementList()
    for i in range(node_shape[Dmn.H] + 1):
        y = i * node_size
        shape = arcade.create_line(0, y, screen_width, y, arcade.color.WHITE)
        path_shape_list.append(shape)
    for i in range(node_shape[Dmn.W] + 1):
        x = i * node_size
        shape = arcade.create_line(x, 0, x, screen_height, arcade.color.WHITE)
        path_shape_list.append(shape)

    if offset is not None:
        path_sprite_list.move(offset[Axis.X], offset[Axis.Y])
        path_shape_list.move(offset[Axis.X], offset[Axis.Y])

    path_lists = (path_sprite_list, path_shape_list)
    return path_lists

def create_flat_snake_list(snake_arr, food, path, node_size,
                           node_shape, offset = None):
    '''
    create a snake shape element list

    Parameters
    ----------
    snake_arr : array
        array of node ids occupied by the snake

    snake_head_dir : Dir
        direction the snake head is pointing to

    food : integer
        food node id

    path : array
        flattened hamiltonian path on top of which to place
        the indvidual snake segments

    node_size : integer
        with and height of a node in pixels

    node_shape : array
        node shape HxW - number of nodes in the height and width dimensions

    offset : list, optional
        [x, y] offset the snake list in the X-Y axis, by default is None

    Returns
    -------
    snake_list : ShapeElementList
        a list of snake body shapes

    '''

    snake_list = arcade.ShapeElementList()
    snake_len = len(snake_arr)
    dir = Dir.Right
    get_pos = lambda path_node: tuple(nav.create_pos(x = path_node * node_size + node_size * 0.5, y = node_size * 0.5))
    for i in range(snake_len):
        j = snake_len - 1 - i
        square = path[snake_arr[j]]
        coords = get_pos(square)

        color = arcade.color.ALIZARIN_CRIMSON if j == 0 else arcade.color.UFO_GREEN
        segments = None
        if j == 0:
            segments = [create_snake_head(coords, dir, node_size, color)]
        elif j == snake_len -1:
            segments = create_snake_tail(coords, dir, node_size, color)
        else:
            segments = [create_snake_body_segment(coords, dir.Left, dir, node_size, color)]
        for segment in segments:
            snake_list.append(segment)

    food_pos = get_pos(path[food])
    food = arcade.create_ellipse_filled(food_pos[Axis.X], food_pos[Axis.Y], node_size, node_size, arcade.color.ALIZARIN_CRIMSON)
    snake_list.append(food)
    if offset is not None:
        snake_list.move(offset[Axis.X], offset[Axis.Y])
    return snake_list

def create_flat_path_lists(path, node_size, node_shape, offset = None,
                           color = arcade.color.WHITE, font_size = None,
                           align = "center"):
    '''
    create path lists flattened into a row

    Parameters
    ----------
    path : array
        array of node ids that compromise the path

    node_size : integer
        with and height of a node in pixels

    node_shape : array
        node shape HxW - number of nodes in the height and width dimensions

    offset : list, optional
        [x, y] offset the lists in the X-Y axis, by default is None

    color : tuple, optional
        (r, g, b) color of the text and grid, by default is White

    font_size : integer, optional
        size of the text, by default is 10

    align : string, optional
        alignment of the text, by default is "center"

    Returns
    -------
    path_lists : tuple
        a tuple of the text sprite list and the grid shape list
    '''
    if font_size is None:
        font_size = node_size // 2

    path_sprite_list = arcade.SpriteList()
    for i in range(len(path)):
        text_x = (i * node_size)
        text_y = 0
        sprite = arcade.create_text_sprite(f'{i}', text_x, text_y, color, font_size,
                                           align=align, width=node_size)
        path_sprite_list.append(sprite)

    path_shape_list = arcade.ShapeElementList()
    total_nodes = node_shape[Dmn.W] * node_shape[Dmn.H]
    for i in range(Axis.COUNT):
        y = i * node_size
        shape = arcade.create_line(0, y, total_nodes * node_size, y, arcade.color.WHITE)
        path_shape_list.append(shape)
    for i in range(total_nodes + 1):
        x = i * node_size
        shape = arcade.create_line(x, 0, x, node_size, arcade.color.WHITE)
        path_shape_list.append(shape)

    if offset is not None:
        path_sprite_list.move(offset[Axis.X], offset[Axis.Y])
        path_shape_list.move(offset[Axis.X], offset[Axis.Y])

    path_lists = (path_sprite_list, path_shape_list)
    return path_lists