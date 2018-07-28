def add_main_node(graph, name, position, type, ride_data, grid_graph=None, on_grid=True):
    '''
    adds main node of types: pickup or dropoff and creates the needed walk_nodes
    :param G: the graph contains all the nodes
    :param name: name of main node to be created
    :param position: location of node (x,y)
    :param type: type of main node (pickup or dropoff
    :return: none
    '''
    if grid_graph is None:
        grid_graph = graph
    wn_dict = {"aa original": {"name": name, "position": (position[0], position[1]), "type": type}}

    if position[1] + 1 < ride_data.grid_size_y:
        wn_dict["north"] = {"name": name + "n", "position": (position[0], position[1] + 1), "type": "walk_node"}
    if position[1] - 1 >= 0:
        wn_dict["south"] = {"name": name + "s", "position": (position[0], position[1] - 1), "type": "walk_node"}
    if position[0] - 1 >= 0:
        wn_dict["west"] = {"name": name + "w", "position": (position[0] - 1, position[1]), "type": "walk_node"}
    if position[0] + 1 < ride_data.grid_size_x:
        wn_dict["east"] = {"name": name + "e", "position": (position[0] + 1, position[1]), "type": "walk_node"}

    all_cluster = [wn_dict[key]["name"] for key in wn_dict.keys()]
    while len(all_cluster) < 5:
        all_cluster.append(None)

    for key in wn_dict.keys():
        node_name = wn_dict[key]["name"]
        add_node(graph, node_name, wn_dict[key]["position"], wn_dict[key]["type"], cluster=all_cluster, grid_graph=grid_graph, on_grid=on_grid)
    return [wn_dict[key]["name"] for key in wn_dict.keys()]


def add_node(graph, name, position, type, cluster=None, grid_graph=None, on_grid=True):
    if grid_graph is None:
        grid_graph = graph
    tp_clr_dict = {"van": "green", "pickup": "red", "dropoff": "blue", "walk_node": "yellow"}
    if type == "van":
        graph.add_node(name, position=position, type=type, color=tp_clr_dict[type])
    else:
        graph.add_node(name, position=position, type=type, color=tp_clr_dict[type], wnode=cluster)
    if on_grid:
        for key in grid_graph[position].keys():
            graph.add_edge(key, name)


def set_nodes_and_edge_colors(graph):
    node_colors = []
    positions = {}
    edge_colors = []
    for node in graph.nodes.data():
        if node[1].has_key("color"):
            node_colors.append(node[1]["color"])
            positions[node[0]] = node[1]["position"]
        else:
            node_colors.append("gray")
            positions[node[0]] = node[0]
    for edge in graph.edges.data():
        if edge[2].has_key("color"):
            edge_colors.append(edge[2]["color"])
        else:
            edge_colors.append("gray")
    return [node_colors, positions, edge_colors]


def get_edge_list_from_path(path):
    edges = []
    for step in xrange(len(path) - 1):
        edges.append((path[step], path[step + 1]))
    return edges
