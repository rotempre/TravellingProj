import sys
import json
import networkx as nx
import matplotlib.pyplot as plt

import pdb
import GraphUtils
from RideData import RideData
from Ride import Ride
from TravelG import TravelG
from GridG import GridG


def main():
    outfilename = 'recomended_path.json'
    if len(sys.argv) != 2:
        print "program expected only one input argument, but got more. please try again."
        raise

    # Gets the data from the json file:
    try:
        with open(sys.argv[1]) as jf:
            data = json.load(jf)
    except:
        print "could not read json file properly!"
        raise
    ride_data = RideData(data)

    #  creates a grid graph for basic visualiztion:
    grid_g = GridG(ride_data)
    # Adding the pick-up and drop-off points:
    rides = get_rides(ride_data.rides)
    grid_g.add_rides_to_graph(rides)
    grid_g.plot_grid_and_rides(rides)

    sh_path_lens = {}
    for ride in rides:
        sh_path_lens[ride.pickup.name] = nx.shortest_path_length(grid_g.graph, ride.pickup.name, ride.dropoff.name)
    print sh_path_lens

    travel_g = TravelG(ride_data)
    travel_g.load_nodes(grid_g, rides, ride_data.van_vertex)

    travel_dist = 0
    detour_dist = 0
    walk_dist = 0
    path = []
    while travel_g.still_got_rides():  # as long as there are rides left to take or complete
        [nn, wght_cost, dist, detour, walk] = travel_g.find_weighted_nn()  # calculates the next destination parameters
        path = path + nx.shortest_path(grid_g.graph, travel_g.graph.node["van"]["position"], nn)
        travel_dist += dist
        walk_dist += walk
        # adds the path length to the detour of each dropoff node:
        travel_g.add_detour_to_nodes(dist)

        # if arrived to pickup point then adds its dropoff destinations nodes:
        if travel_g.is_pickup(nn):
            travel_g.add_drop_off_node(nn, rides, sh_path_lens,grid_g)

        # if arrived to dropoff point, keeps its detour value
        else:
            detour_dist += travel_g.graph.nodes[nn[0:3]]['detour']
        # remove the old van node and changes the arrived node to be the new van node:
        travel_g.remove_and_relabel(nn)

        # travel_g.plot_travelling_graph()

    print "The total Travel distance is: " + str(travel_dist)
    print "The total Detour distance is: " + str(detour_dist)
    print "The total Walk distance is: " + str(walk_dist)
    print "The total Cost is: " + str(travel_g.a * travel_dist + travel_g.b * detour_dist + travel_g.c * walk_dist)

    grid_g.final_graph_plotting(path, rides)
    save_path_to_json_file(path, outfilename, grid_g)

    print "lala"


def get_rides(rides_data):
    rides = []
    for ride in rides_data:
        rides.append(Ride(ride))
    return rides

# def simple_graph_plotting(gridG, gridpos):
#     plt.figure(figsize=(15, 15))
#     nx.draw(gridG, gridpos, node_size=10, node_color='red')
#     plt.show()


def save_path_to_json_file(path, outfilename, grid_g):
    ind_to_del = []
    for i in xrange(len(path)):
        if type(path[i])==str:
            path[i] = grid_g.graph.node[path[i]]["position"]
        if i>0 and path[i] == path[i-1]:
            ind_to_del.append(i)
    ind_to_del.reverse()
    for i in ind_to_del:
        del path[i]
    jpath = {"vanRoute": [dict(zip(('x', 'y'), path_i)) for path_i in path]}
    with open(outfilename,'w') as outfile:
        json.dump(jpath, outfile, indent=4)


if __name__ == "__main__":
    main()
    print "the end"
