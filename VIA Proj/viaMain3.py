import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
import itertools


class RideData:
    def __init__(self, data):
        self.grid_size_x = data["gridSizeX"]
        self.grid_size_y = data["gridSizeY"]
        self.a = data["a"]
        self.b = data["b"]
        self.van_vertex = data["vanVertex"]
        self.rides = data["rides"]
        self.non_connected_edges = data["nonConnectedEdges"]


def remove_edges_from_grid(grid_graph, non_connected_edges):
    edges_to_remove = []
    for non_con in non_connected_edges:
        vert1 = (non_con["startVertex"]["x"], non_con["startVertex"]["y"])
        vert2 = (non_con["endVertex"]["x"], non_con["endVertex"]["y"])
        edges_to_remove.append((vert1, vert2))
    grid_graph.remove_edges_from(edges_to_remove)


def get_rides(rides_data):
    ride_nodes = {}
    for ride in rides_data:
        pu_node = (ride["pickup"]["x"],ride["pickup"]["y"])
        do_node = (ride["dropoff"]["x"], ride["dropoff"]["y"])
        ride_nodes[pu_node] = do_node
    return ride_nodes


def set_nodes_and_edge_colors(gridG, ride_nodes):
    for ride_node in ride_nodes:
        gridG.add_node(ride_node, color = "red")
        gridG.add_node(ride_nodes[ride_node], color="blue")
        gridG.add_edge(ride_node,ride_nodes[ride_node], color="green")
    node_colors = []
    for node in gridG.nodes.data():
        if node[1].has_key("color"):
            node_colors.append(node[1]["color"])
        else:
            node_colors.append("gray")
    edge_colors = []
    for edge in gridG.edges.data():
        if edge[2].has_key("color"):
            edge_colors.append(edge[2]["color"])
        else:
            edge_colors.append("gray")
    return [node_colors,edge_colors]


def plot_grid_and_rides(gridG, gridpos, ride_nodes):
    [node_colors, edge_colors] = set_nodes_and_edge_colors(gridG, ride_nodes)
    plt.figure(figsize=(15, 15))
    nx.draw(gridG, gridpos, node_size=15, node_color=node_colors, edge_color=edge_colors)
    plt.show()
    for ride_node in ride_nodes: # Removing edges that were added for visualization (set_nodes_and_edge_colors function)
        gridG.remove_edge(ride_node, ride_nodes[ride_node])


def simple_graph_plotting(gridG, gridpos):
    plt.figure(figsize=(15, 15))
    nx.draw(gridG, gridpos, node_size=10, node_color='red')
    plt.show()


def load_nodes_to_travel_graph(travelG, gridG, ride_nodes, van_vertex, start=False):
    van_node = (van_vertex["x"],van_vertex["y"])
    travelG.add_node(van_node, color="green", name="van")
    pickup_nodes = []
    for node in ride_nodes:
        travelG.add_node(node, color="red", type="pickup")
        if not start:
            travelG.add_node(ride_nodes[node], color="blue", type="dropoff")
    for i, j in itertools.combinations(travelG.nodes, 2):
        travelG.add_edge(i, j, weight=nx.shortest_path_length(gridG, i, j))
    if start:
        return van_node

def get_edge_list_from_path(path):
    edges = []
    for step in xrange(len(path)-1):
        edges.append((path[step],path[step+1]))
    return edges


def final_graph_plotting(gridG, gridpos,ride_nodes, path):
    path_edge_list = get_edge_list_from_path(path)
    plt.figure(figsize=(15, 15))
    [node_colors, edge_colors] = set_nodes_and_edge_colors(gridG, ride_nodes)
    nx.draw(gridG, gridpos, node_size=15, node_color=node_colors, edge_color=edge_colors)
    nx.draw_networkx_edges(gridG,gridpos,path_edge_list,width=2,edge_color='red')
    for ride_node in ride_nodes:  # Removing edges that were added for visualization (set_nodes_and_edge_colors function)
        gridG.remove_edge(ride_node, ride_nodes[ride_node])
    plt.show()


def save_path_to_json_file(path, outfilename):
    jpath = {"vanRoute": [dict(zip(('x', 'y'), path_i)) for path_i in path]}
    with open(outfilename,'w') as outfile:
        json.dump(jpath, outfile)

def plot_travelling_graph(G):
    edge_labels = nx.get_edge_attributes(G, 'weight')
    node_labels = dict([(node, str(node)) for node in G.node])
    node_colors = [node[1]["color"] for node in G.nodes.data()]
    travel_pos = dict(zip(G.nodes(), G.nodes()))
    plt.figure(figsize=(15, 15))
    nx.draw_networkx_edge_labels(G, travel_pos, edge_labels=edge_labels, font_size=15)
    nx.draw_networkx_labels(G, travel_pos, labels=node_labels)
    nx.draw(G, travel_pos, node_size=25, node_color=node_colors)
    plt.show()

def find_weighted_nn(curG,van_node,a,b):
    def second_elmnt(elem):
        return elem[1]
    weight_list = []
    for i in xrange(len(curG[van_node].items())):
        wk_node = curG[van_node].items()[i]
        weight_list.append([wk_node[0], a*wk_node[1]['weight']])
        for node in curG.nodes.data():
            if node[1].has_key("detour") and node[0] != wk_node[0] and node[0] != van_node:
                detour = curG.edges[(node[0], wk_node[0])]['weight'] + curG.edges[(van_node, wk_node[0])]['weight'] - curG.edges[(node[0], van_node)]['weight']
                weight_list[i][1] += b*detour
    nwn = sorted(weight_list, key=second_elmnt)[0][0]
    return nwn


def main():
    PLOT = True
    outfilename = 'recomended_path.json'
    if len(sys.argv) != 2:
        print "program expected only one input argument, but got more. please try again."
        raise
    try:
        with open(sys.argv[1]) as jf:
            data = json.load(jf)
    except:
        print "could not read json file properly!"
        raise

    ride_data = RideData(data)
    gridG = nx.grid_graph([ride_data.grid_size_x, ride_data.grid_size_y])
    gridpos = dict(zip(gridG.nodes(), gridG.nodes()))
    remove_edges_from_grid(gridG, ride_data.non_connected_edges)
    # Adding the pick-up and drop-off points:
    ride_nodes = get_rides(ride_data.rides)
    plot_grid_and_rides(gridG, gridpos, ride_nodes)
    # simple_graph_plotting(gridG, gridpos)

    sh_path_lens = {}
    for ride_node in ride_nodes:
        sh_path_lens[ride_node] = (nx.shortest_path_length(gridG, ride_node, ride_nodes[ride_node]))
    print sh_path_lens

    travelG = nx.Graph()
    load_nodes_to_travel_graph(travelG, gridG, ride_nodes, ride_data.van_vertex)

    if PLOT:
        plot_travelling_graph(travelG)

    curG = nx.Graph()
    van_node = load_nodes_to_travel_graph(curG, gridG, ride_nodes, ride_data.van_vertex, start=True)
    travel_dist = 0
    detour_dist = 0
    path = []
    while curG.number_of_nodes() > 1:
        nearest_neighbor = find_weighted_nn(curG,van_node,ride_data.a,ride_data.b)
        path = path + nx.shortest_path(gridG, van_node, nearest_neighbor)
        cur_dist = curG.edges[(van_node, nearest_neighbor)]["weight"]
        travel_dist += cur_dist
        for node in curG.nodes.data():
            if node[1].has_key("detour"):
                node[1]["detour"] += cur_dist
        if curG.nodes[nearest_neighbor]['type'] == "pickup":
            new_node = ride_nodes[nearest_neighbor]
            curG.add_node(new_node, type="dropoff", color="blue", detour=-sh_path_lens[nearest_neighbor])
            for node in curG.nodes:
                if node != new_node and node != van_node:
                    curG.add_edge(new_node,node,weight=travelG.edges[(new_node,node)]["weight"])
        else:
            detour_dist += curG.nodes[nearest_neighbor]['detour']
        # detour_dist +=
        curG.remove_node(van_node)
        van_node = nearest_neighbor
        curG.nodes[van_node]['color'] = "green"

        # plot_travelling_graph(curG)


    print "The total travel distance is: " + str(travel_dist)
    print "the total Detour distance is: " + str(detour_dist)
    if PLOT:
        final_graph_plotting(gridG, gridpos, ride_nodes, path)
    save_path_to_json_file(path, outfilename)

    print "lala"


if __name__ == "__main__":
    main()
    print "the end"
