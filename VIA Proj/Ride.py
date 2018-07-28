from MapPoint import MapPoint


class Ride:
    rides_counter = 0

    def __init__(self, ride):
        Ride.rides_counter += 1
        c = Ride.rides_counter
        self.number = c
        self.pickup = MapPoint("pu"+str(c), (ride["pickup"]["x"], ride["pickup"]["y"]))
        self.dropoff = MapPoint("do" + str(c), (ride["dropoff"]["x"], ride["dropoff"]["y"]))

