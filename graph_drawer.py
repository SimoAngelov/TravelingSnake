
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from itertools import combinations
from IPython.display import HTML

import nav
from nav import Dir, Axis, Dmn

import hamilton_cycle_generator as hcg

plt.ioff()

def create_graph_edges(nodes, is_weighted):
    '''
    create_graph_edges - create edges for a graph with the given nodes

    Parameters
    ----------
    nodes : list
        nodes for which to create the edges

    is_weighted : bool
        do the edges have values(True) or not(False)

    Returns
    -------
    edges : list
        a list of edges
    '''
    node_count = len(nodes)
    # determine how many edges will emerge from each node
    combos = list(combinations(nodes, 2))
    edges = [combos[i] for i in range(node_count)]

    if is_weighted:
        for i in range(len(edges)):
            rand_weight = float("{:.2f}".format(np.random.rand()))
            edges[i] += (rand_weight,)
    return edges

def draw_graph_edges(G, edges, pos, is_directed, is_weighted,
                     width = 3, arrowstyle = "->", arrowsize = 20):
    '''
    draw the edges of the specified graph

    Parameters
    ----------
    G : graph
        graph for which to draw the edges

    edges : list
        edges to be drawn

    pos : list
        (x, y) positions of the edges

    is_directed : bool,
        are the edges directed(True) or not(False)

    is_weighted : bool
        do the edges have values(True) or not(False)

    width : integer, optional
        width of the edge in pixels, by default 3

    arrowstyle : string, optional
        style of the arrow, if the graph is directed, by default "->"

    arrowsize : integer, optional
        size of the arrow, if the graph is directed, by default 20
    '''
    def draw_edges(edge_list, alpha = None, edge_color="k", style="solid"):
        if is_directed:
            nx.draw_networkx_edges(G, pos, edgelist = edge_list, width = width,
                                   alpha = alpha, edge_color = edge_color, style = style,
                                   arrowstyle = arrowstyle, arrowsize = arrowsize)
        else:
            nx.draw_networkx_edges(G, pos, edgelist = edge_list, width = width,
                                  alpha = alpha, edge_color = edge_color, style = style)

    if is_weighted:
        large_edges = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]
        small_edges = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0.5]
        draw_edges(edge_list = large_edges)
        draw_edges(edge_list = small_edges, alpha = 0.5, edge_color = "b", style = "dashed")
        # edge weight labels
        edge_labels = nx.get_edge_attributes(G, "weight")
        nx.draw_networkx_edge_labels(G, pos, edge_labels)
    else:
        draw_edges(edge_list = edges)

def graph_example(title, is_directed = False, is_weighted = False, node_count = 6, dpi = 240, seed = 6):
    '''
    render a graph example

    Parameters
    ----------

    title : string
        title of the example graph

    is_directed : bool, optional
        is the graph directed(True) or undirected(False), by default False

    is_weighted : bool, optional
        is the graph weighted(True) or unweighed(False), by default False

    node_count : integer, optional
        number of nodes for the example graph, by default 6

    dpi : integer, optional
        dots per inch, by default 240

    seed : integer, optional
        position seed for reproducibility, by default 6
    '''
    G = nx.DiGraph() if is_directed else nx.Graph()
    G.graph['dpi'] = dpi
    # Label the nodes with letters
    nodes = [chr(ord('@') + i + 1) for i in range(node_count)]
    # Create edges between each pair of nodes
    edges = create_graph_edges(nodes, is_weighted)
    G.add_nodes_from(nodes)
    if is_weighted:
        G.add_weighted_edges_from(edges)
    else:
        G.add_edges_from(edges)

    pos = nx.spring_layout(G, seed = seed)

    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=700)
    # node labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")

    draw_graph_edges(G, edges, pos, is_directed, is_weighted)
    plt.title(title)
    plt.show()

def draw_grid_graph(title, m, n, edges_to_remove = [], node_color = "blue", node_size = 600):
    '''
    draw a grid graph with the specified size

    Parameters
    ----------
    title : string
        title of the graph

    m : integer
        number of rows

    n : integer
        number of colums

    edges_to_remove : list
        list of edges to be removed

    node_color : string, optional
        color of the node, by default "blue"

    node_size : integer, optional
        size of the node in pixels, by default 600
    '''
    G = nx.grid_2d_graph(m, n)

    plt.figure(figsize=(6,6))
    pos = {(x,y):(y,-x) for x,y in G.nodes()}
    if len(edges_to_remove) != 0:
        G.remove_edges_from(edges_to_remove)

    nx.draw(G, pos=pos,
            node_color=node_color,
            node_size=600)
    plt.title(title)
    plt.show()


def draw_diracs_theorem():
    '''
    draw an example of Dirac's theorem
    '''
    G = nx.Graph()
    nodes = np.arange(6)
    G.add_nodes_from(nodes)

    edges = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 5), (2, 3), (2, 4), (2, 5), (4, 5)]
    G.add_edges_from(edges)
    pos = {0: (1, 2), 1: (2, 2), 2: (3, 1), 3: (2, 0), 4: (1, 0), 5: (0, 1)}

    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=2800)
    # node labels
    labels = {i : f'Degree: {G.degree[i]}' for i in range(len(nodes))}
    nx.draw_networkx_labels(G, pos, labels = labels, font_size=10, font_family="sans-serif")
    draw_graph_edges(G, edges, pos, is_directed = False, is_weighted = False)
    plt.title(f'Dirac\'s Theorem\nVertices: {len(nodes)}')
    plt.show()

def draw_ores_theorem():
    '''
    draw an example of Ore's theorem
    '''
    G = nx.Graph()
    nodes = np.arange(5)
    G.add_nodes_from(nodes)

    edges = [(0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]
    G.add_edges_from(edges)
    pos = {0: (0, 2), 1: (1, 2), 2: (2, 1), 3: (1, 0), 4: (0, 0)}

    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=2800)
    # node labels
    labels = {i : f'Degree: {G.degree[i]}' for i in range(len(nodes))}
    nx.draw_networkx_labels(G, pos, labels = labels, font_size=10, font_family="sans-serif")
    draw_graph_edges(G, edges, pos, is_directed = False, is_weighted = False)
    plt.title(f'Ore\'s Theorem\nVertices: {len(nodes)}')
    plt.show()

def draw_hamilton_example():
    '''
    draw a hamilton example
    '''
    edges_to_remove = []
    m = 5
    n = 6
    for i in range(1, n - 1):
        edges_to_remove.append([(0, i), (1, i)])
    for j in range(1, m):
        for i in range(n - 1):
            if (j == 1 and i % 2 != 0) or (j == m - 1 and i % 2 == 0):
                pass
            else:
                edges_to_remove.append([(j, i), (j, i + 1)])
    draw_grid_graph("Hamiltonian Cycle with one even dimension", m, n, edges_to_remove, node_size = 300)

def animate_prim_mst(shape, seed, is_html = False, node_size = 100):
    half_shape = nav.create_pos(shape[Dmn.H] / 2, shape[Dmn.W] / 2)
    mst, visited, prim_path = hcg.generate_prim_mst(nav.create_pos(-1, -1), nav.create_random_pos(half_shape), half_shape, seed)
    hamilton_path = hcg.generate_hamilton_cycle(mst, shape)

    fig = plt.figure(figsize=[4, 4])

    offset = node_size * 10

    frames = len(prim_path)

    h_graph = nx.Graph()
    h_nodes = [x for x in range(len(hamilton_path))]
    h_graph.add_nodes_from(h_nodes)
    h_pos = {}

    G = nx.Graph()
    prim_pos = {}

    G.add_nodes_from(prim_path)

    p_i = 0
    for node in h_nodes:
        node_pos = nav.get_node_pos(node, shape)
        h_pos[node] = (node_pos[Axis.X] * offset, node_pos[Axis.Y] * offset)
        if node_pos[Axis.X] % 2 == 0 and node_pos[Axis.Y] % 2 == 0:
            prim_pos[p_i] = (h_pos[node][Axis.X] + offset * 0.5, h_pos[node][Axis.Y] + offset * 0.5)
            p_i += 1

    print(f'prim_pos: {prim_pos}')
    def draw_prim():
        ax = fig.gca()
        x_lim = (shape[Dmn.W]) * offset
        y_lim = (shape[Dmn.H]) * offset
        ax.set(xlim=[0, x_lim], ylim=[y_lim, 0])

        left, right = ax.get_xlim()
        bottom, top = ax.get_ylim()


        xs = [left, left, right, right, left]
        ys = [top, bottom, bottom, top, top]


        plt.scatter(xs, ys)

        nx.draw(G, pos=prim_pos,
            node_color="blue",
            with_labels = True,
            node_size=node_size,
            font_color="white")

        #nx.draw(h_graph, pos = h_pos, node_color = "cyan", with_labels = True, node_size = node_size, font_color = "black")

    def animate(frame):
        fig.clear()
        if frame > 0:
            G.add_edge(prim_path[frame - 1], prim_path[frame])
        draw_prim()
        return G

    anim = animation.FuncAnimation(fig, animate, frames=frames, interval=1000, repeat=False)
    if not is_html:
        plt.show()
    return HTML(anim.to_jshtml())
