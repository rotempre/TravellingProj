import networkx as nx
import GraphUtils
import matplotlib.pyplot as plt


class GridG:
    def __init__(self, ride_data):
        self.ride_data = ride_data
        self.graph = nx.grid_graph([ride_data.grid_size_y, ride_data.grid_size_x])
        self.remove_edges_from_grid()  # Removes edges so it fits the real map
        self.node_colors = []
        self.positions = {}
        self.edge_colors = []
        self.pu_nodes = []
        self.do_nodes = []
        self.w_nodes = []

    def remove_edges_from_grid(self):
        non_connected_edges = self.ride_data.non_connected_edges
        edges_to_remove = []
        for non_con in non_connected_edges:
            vert1 = (non_con["startVertex"]["x"], non_con["startVertex"]["y"])
            vert2 = (non_con["endVertex"]["x"], non_con["endVertex"]["y"])
            edges_to_remove.append((vert1, vert2))
        self.graph.remove_edges_from(edges_to_remove)


    def plot_grid_and_rides(self, rides):
        '''
        plot the rides on the grid (insert and remove edges between ride pickup and drop-off points for visualization
        purposes)
        :param rides: list of ride objects
        :return:
        '''
        self.set_nodes_and_edge_colors()
        plt.figure(figsize=(15, 15))
        nx.draw(self.graph, self.positions, node_size=15, node_color=self.node_colors, edge_color=self.edge_colors)
        plt.show()
        for ride in rides:  # Removing edges that were added for visualization (set_nodes_and_edge_colors function)
            self.graph.remove_edge(ride.pickup.name, ride.dropoff.name)

    def set_nodes_and_edge_colors(self):
        [self.node_colors, self.positions, self.edge_colors] = GraphUtils.set_nodes_and_edge_colors(self.graph)

    def add_rides_to_graph(self, rides):
        for ride in rides:
            pu = GraphUtils.add_main_node(self.graph, ride.pickup.name, ride.pickup.pos, "pickup", self.ride_data)
            do = GraphUtils.add_main_node(self.graph, ride.dropoff.name, ride.dropoff.pos, "dropoff", self.ride_data)
            self.do_nodes.append(do[0])
            self.pu_nodes.append(pu[0])
            self.w_nodes.extend(pu[1:])
            self.w_nodes.extend(do[1:])
            self.add_edges_for_print(ride)

    def add_edges_for_print(self, ride):
        self.graph.add_edge(ride.pickup.name, ride.dropoff.name, color="green")

    def final_graph_plotting(self, path, rides):
        self.add_rides_to_graph(rides)
        self.add_van_node()
        path_edge_list = GraphUtils.get_edge_list_from_path(path)
        plt.figure(figsize=(15, 15))
        self.set_nodes_and_edge_colors()
        nx.draw(self.graph, self.positions, node_size=15, node_color=self.node_colors, edge_color=self.edge_colors)
        nx.draw_networkx_nodes(self.graph, self.positions, self.w_nodes, node_size=40, node_color='y')
        nx.draw_networkx_nodes(self.graph, self.positions, self.pu_nodes, node_size=40, node_color='r')
        nx.draw_networkx_nodes(self.graph, self.positions, self.do_nodes, node_size=40, node_color='b')
        nx.draw_networkx_nodes(self.graph, self.positions, ["van"], node_size=40, node_color='g')
        nx.draw_networkx_edges(self.graph, self.positions, path_edge_list, width=2, edge_color='red')
        plt.show()

    def add_van_node(self):
        van_pos = (self.ride_data.van_vertex["x"], self.ride_data.van_vertex["y"])
        GraphUtils.add_node(self.graph, "van", van_pos, "van", grid_graph=None, on_grid=True)
