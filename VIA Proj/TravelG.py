import networkx as nx
import GraphUtils
import itertools
import matplotlib.pyplot as plt


class TravelG:
    def __init__(self, ride_data):
        self.ride_data = ride_data
        self.graph = nx.Graph()
        self.node_colors = []
        self.positions = {}
        self.edge_colors = []
        self.a = ride_data.a
        self.b = ride_data.b
        self.c = ride_data.c

    def load_nodes(self, gridG, rides, van_vertex, for_final_plot=False):
        van_pos = (van_vertex["x"],van_vertex["y"])
        GraphUtils.add_node(self.graph, "van", van_pos, "van", grid_graph=gridG.graph, on_grid=False)
        for ride in rides:
            GraphUtils.add_main_node(self.graph, ride.pickup.name, ride.pickup.pos, "pickup", self.ride_data, grid_graph=gridG.graph, on_grid=False)
            if for_final_plot:
                GraphUtils.add_main_node(self.graph, ride.dropoff.name, ride.dropoff.pos, "dropoff", self.ride_data, grid_graph=gridG.graph, on_grid=False)
                self.graph.add_edge(ride.pickup.name, ride.dropoff.name, color="green")
        else:
            for i, j in itertools.combinations(self.graph.nodes, 2):
                if i == "van" or j == "van" or j not in self.graph.node[i]["wnode"]:
                    self.graph.add_edge(i, j, weight=nx.shortest_path_length(gridG.graph, self.graph.node[i]["position"],
                                                                             self.graph.node[j]["position"]))

    def set_nodes_and_edge_colors(self):
        [self.node_colors, self.positions, self.edge_colors] = GraphUtils.set_nodes_and_edge_colors(self.graph)

    def find_weighted_nn(self):

        def second_elmnt(elem):
            return elem[1]

        weight_list = []
        for i in xrange(len(self.graph["van"].items())):  # runs through all possible destinations
            wk_node = self.graph["van"].items()[i]  # define current neighbor and gets its weight

            dist = wk_node[1]["weight"]

            walk = 0
            if self.graph.node[wk_node[0]]["type"] == "walk_node":
                walk = 1

            detour = 0
            for node in self.graph.nodes.data():   # runs through all other possible destinations and calculates their detour
                if node[1]["type"] == "dropoff" and node[0] not in self.graph.node[wk_node[0]]["wnode"]:
                    detour += self.graph.edges[(node[0], wk_node[0])]['weight'] + \
                              self.graph.edges[("van", wk_node[0])]['weight'] - \
                              self.graph.edges[(node[0], "van")]['weight']

            weighted_cost = self.a*dist + self.b*detour + self.c*walk
            weight_list.append([wk_node[0], weighted_cost, dist, detour, walk])

        nwn = sorted(weight_list, key=second_elmnt)[0]
        return nwn

    def still_got_rides(self):
        return self.graph.number_of_nodes() > 1

    def add_detour_to_nodes(self, dist):
        for node in self.graph.nodes.data():
            if node[1]["type"] == "dropoff":
                node[1]["detour"] += dist

    def is_pickup(self, nn):
        if 'pu' in nn:
            return True
        else:
            return False

    def add_drop_off_node(self, nn, rides, sh_path_lens, grid_g):
        cur_node_dict = self.graph.nodes[nn]
        ride_num = int(nn[2])
        ride = rides[ride_num - 1]
        new_nodes = GraphUtils.add_main_node(self.graph, ride.dropoff.name, ride.dropoff.pos, "dropoff", self.ride_data,
                                             grid_graph=grid_g.graph, on_grid=False)
        # adds the "detour" attribute to the node attributes dictionary
        self.graph.nodes[ride.dropoff.name]["detour"] = -sh_path_lens[ride.pickup.name]
        #  Creates weighted edges for the new nodes with the exist nodes
        for new_node in new_nodes:
            for node in self.graph.nodes:
                if all([node not in self.graph.node[new_node]["wnode"], node != "van"]):
                    self.graph.add_edge(new_node, node,
                                            weight=nx.shortest_path_length(grid_g.graph, new_node, node))

    def remove_and_relabel(self, nn):
        nodes_to_remove = self.graph.node[nn]["wnode"]
        self.graph.remove_node("van")
        mapping = {nn: "van"}
        self.graph = nx.relabel_nodes(self.graph, mapping, copy=False)
        self.graph.node["van"]["type"] = "van"
        self.graph.node["van"]["color"] = "green"
        del self.graph.node["van"]["wnode"]
        # remove related nodes of local nodes
        self.graph.remove_nodes_from(nodes_to_remove)

    def plot_travelling_graph(self):
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        node_labels = dict([(node, str(node)) for node in self.graph.node])
        node_colors = [node[1]["color"] for node in self.graph.nodes.data()]
        travel_pos = dict(zip(self.graph.nodes(), [node[1]["position"] for node in self.graph.nodes.data()]))
        plt.figure(figsize=(15, 15))
        nx.draw_networkx_edge_labels(self.graph, travel_pos, edge_labels=edge_labels, font_size=15)
        nx.draw_networkx_labels(self.graph, travel_pos, labels=node_labels)
        nx.draw(self.graph, travel_pos, node_size=25, node_color=node_colors)
        plt.show()

