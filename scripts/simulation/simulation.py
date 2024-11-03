from typing import List, Dict, Tuple
from enum import Enum
import random


class Direction(Enum):
    SOUTH = "S"
    WEST = "W"
    NORTH = "N"
    EAST = "E"

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return self.name


class Turn(Enum):
    RIGHT = "R"
    FORWARD = "F"
    LEFT = "L"

    def __str__(self) -> str:
        return self.name


type Location = Tuple[int, Direction]


class Car:
    # hardcoding pathfindig
    dest_to_path_map = {(0, 1): [Direction.EAST],
                        (0, 2): [Direction.SOUTH],
                        (0, 3): [Direction.EAST, Direction.NORTH],
                        (1, 0): [Direction.WEST],
                        (1, 2): [Direction.NORTH, Direction.WEST],
                        (1, 3): [Direction.SOUTH],
                        (2, 0): [Direction.NORTH],
                        (2, 1): [Direction.NORTH, Direction.EAST],
                        (2, 3): [Direction.EAST],
                        (3, 0): [Direction.WEST, Direction.NORTH],
                        (3, 1): [Direction.NORTH],
                        (3, 2): [Direction.WEST]
                        }

    def __init__(self, origin: Location, destination: Location) -> None:
        """
        Creates car and its path

        Args:
            origin (Location): car spawn location
            destination (Location): car destination
        """
        self.origin: Location = origin
        self.destination: Location = destination
        self.path: List[Lane] = self.get_path()
        return

    def get_path(self) -> List[Direction]:
        """
        Finds path for car. Path is represented as directions at consecutive crossroads.
        If the list is empty car reached its destination

        Returns:
            List[Direction]: list of directions at crossroads
        """
        if self.origin[0] == self.destination[0]:
            return [self.destination[1]]
        else:
            return self.dest_to_path_map[(self.origin[0], self.destination[0])]

    def move(self) -> None:
        self.path.pop(0)


class Lane:
    def __init__(self, possible_turns, processing_time) -> None:
        self.possible_turns: List[Turn] = possible_turns
        self.queue: List[Car] = []
        self.processing_time = processing_time
        self.processing_counter = 0

    def process_cars(self) -> Car:
        """
        Process cars in lane if light is green. 

        Returns:
            Car: car that left the crossroad
        """
        if not self.queue:
            return None
        if self.processing_counter >= self.processing_time:
            return self.queue.pop(0)
        else:
            self.processing_counter += 1
            return None

    def add_car(self, car: Car) -> None:
        """
        Adds car to the end of queue

        Args:
            car (Car): car to add
        """
        self.queue.append(car)


class Crossroad:
    # This is how lanes at crossroad will be represented
    type LaneLocations = Dict[Direction, Lane]
    type LightsCycle = List[Direction]

    def __init__(self, lights_cycle=None) -> None:
        # Lights cycle tells witch lane has green light, None=yellow
        self.lights_cycle: Crossroad.LightsCycle = lights_cycle
        self.in_lanes: Crossroad.LaneLocations = {}
        self.out_lanes: Crossroad.LaneLocations = {}
        self.add_in_lanes()
        self.add_out_lanes()

    def step(self, turn: int) -> int:
        """
        Runs one simulation step

        Args:
            time (int): turn in simulation

        Returns:
            int: score for this step
        """
        score = 0
        green_light_now = self.lights_cycle[turn]
        # if yellow light reset all counters
        if green_light_now == None:
            self.reset_lights_counters()
        else:
            # process cars in lane with green lights
            processed_car = self.in_lanes[green_light_now].process_cars()
            if processed_car is not None:
                self.out_lanes[processed_car.path[0]].add_car(processed_car)

        for in_lane in self.in_lanes.values():
            score += len(in_lane.queue)

        return score

    def reset_lights_counters(self) -> None:
        """
        Resets processing counters for all lanes
        """
        for in_lane in self.in_lanes.values():
            in_lane.processing_counter = 0

    def add_car(self, car: 'Car') -> None:
        """
        Finds correct lane and appends car to queue.

        Args:
            car (Car): Car to add
        """
        self.in_lanes[car.origin[1]].add_car(car)

    def add_in_lanes(self) -> None:
        """
        Initialize crossroad with lanes going into, can change deepending on crossroad.
        """
        self.in_lanes[Direction.SOUTH] = Lane([Turn.LEFT, Turn.FORWARD, Turn.RIGHT],
                                              processing_time=2)
        self.in_lanes[Direction.WEST] = Lane([Turn.LEFT, Turn.FORWARD, Turn.RIGHT],
                                             processing_time=2)
        self.in_lanes[Direction.NORTH] = Lane([Turn.LEFT, Turn.FORWARD, Turn.RIGHT],
                                              processing_time=2)
        self.in_lanes[Direction.EAST] = Lane([Turn.LEFT, Turn.FORWARD, Turn.RIGHT],
                                             processing_time=2)

    def add_out_lanes(self) -> None:
        """
        Initialize crossroad with lanes going out, can change deepending on crossroad.
        """
        self.out_lanes[Direction.SOUTH] = Lane([],
                                               processing_time=2)
        self.out_lanes[Direction.WEST] = Lane([],
                                              processing_time=2)
        self.out_lanes[Direction.NORTH] = Lane([],
                                               processing_time=2)
        self.out_lanes[Direction.EAST] = Lane([],
                                              processing_time=2)

    def reset_queues(self) -> None:
        """
        Sets all queues to 0. Used when running new simulation on the same crossroad.
        """
        for in_lane in self.in_lanes.values():
            in_lane.queue = []


class CrossroadNetwork:
    def __init__(self) -> None:
        """
        Creates crossroad network represented as list of crossroads.
        """
        self.crossroad_network: List[Crossroad] = [
            Crossroad(), Crossroad(), Crossroad(), Crossroad()
        ]
        self.connect_crossroads()

    def connect_crossroads(self):
        """
        Setting some out_lanes of one crossroad to be in_lanes of other.
        """
        self.crossroad_network[0].out_lanes[Direction.EAST] =\
            self.crossroad_network[1].in_lanes[Direction.WEST]
        self.crossroad_network[0].out_lanes[Direction.SOUTH] =\
            self.crossroad_network[2].in_lanes[Direction.NORTH]

        self.crossroad_network[1].out_lanes[Direction.WEST] =\
            self.crossroad_network[0].in_lanes[Direction.EAST]
        self.crossroad_network[1].out_lanes[Direction.SOUTH] =\
            self.crossroad_network[3].in_lanes[Direction.NORTH]

        self.crossroad_network[2].out_lanes[Direction.EAST] =\
            self.crossroad_network[3].in_lanes[Direction.WEST]
        self.crossroad_network[2].out_lanes[Direction.NORTH] =\
            self.crossroad_network[0].in_lanes[Direction.SOUTH]

        self.crossroad_network[3].out_lanes[Direction.WEST] =\
            self.crossroad_network[2].in_lanes[Direction.EAST]
        self.crossroad_network[3].out_lanes[Direction.NORTH] =\
            self.crossroad_network[1].in_lanes[Direction.SOUTH]

    def add_car(self, car: Car):
        """
        Finds correct crossroad and adds car there.

        Args:
            car (Car): Car to add
        """
        self.crossroad_network[car.origin[0]].add_car(car)


class Simulation:
    def __init__(self, turn_time, cycles=0) -> None:
        self.crossroad_network = CrossroadNetwork()
        self.turn_time = turn_time
        self.cycles = cycles

    def run(self) -> int:
        """
        Runs simulation and returns score.

        Returns:
            int: score
        """
        score = 0
        for _ in range(self.cycles):
            for t in range(self.turn_time):
                self.add_car()
                for crossroad in self.crossroad_network.crossroad_network:
                    score += crossroad.step(t)

        for crossroad in self.crossroad_network.crossroad_network:
            crossroad.reset_queues()
        return score

    def step(self, t: int) -> None:
        """
        Makes step in simulation. Used in graphic representation.

        Args:
            t (int): Turn in simulation
        """
        self.add_car()
        for crossroad in self.crossroad_network.crossroad_network:
            crossroad.step(t)

    def add_car(self):
        """
        Generates cars from outside world.
        """
        possible_origins = [(0, Direction.WEST), (0, Direction.NORTH),
                            (1, Direction.EAST), (1, Direction.NORTH),
                            (2, Direction.WEST), (2, Direction.SOUTH),
                            (3, Direction.EAST), (3, Direction.SOUTH),]
        car_origin = random.choices(possible_origins,
                                    weights=[4, 1,
                                             1, 1,
                                             1, 1,
                                             1, 1],
                                    k=1)[0]
        car_destination = random.choices(possible_origins,
                                         weights=[1, 1,
                                                  2, 1,
                                                  1, 3,
                                                  1, 1],
                                         k=1)[0]
        car_to_add = Car(car_origin, car_destination)
        self.crossroad_network.crossroad_network[car_origin[0]].\
            in_lanes[car_origin[1]].add_car(car_to_add)
