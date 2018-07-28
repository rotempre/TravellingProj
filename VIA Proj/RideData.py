class RideData:
    def __init__(self, data):
        self.grid_size_x = data["gridSizeX"]
        self.grid_size_y = data["gridSizeY"]
        self.a = data["a"]
        self.b = data["b"]
        self.c = data["c"]
        self.van_vertex = data["vanVertex"]
        self.rides = data["rides"]
        self.non_connected_edges = data["nonConnectedEdges"]
