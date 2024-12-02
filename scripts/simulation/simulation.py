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
        self.waiting_time = 0
        return

    def get_path(self) -> List[Direction]:
        """
        Finds path for car. Path is represented as directions at consecutive crossroads.
        If the list is empty car reached its destination

        Returns:
            List[Direction]: list of directions at crossroads
        """
        if self.origin[0] == self.destination[0]:
            return []
        else:
            return self.dest_to_path_map[(self.origin[0], self.destination[0])][:]

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
            self.processing_counter = 0
            car = self.queue.pop(0)
            car.waiting_time = 0
            return car

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
    type LightsTimes = Dict[Direction, float]
    type LightsOrder = List[Direction]

    def __init__(self) -> None:
        # Lights cycle tells witch lane has green light, None=yellow
        self.lights_order: Crossroad.LightsOrder = None
        self.lights_times: Crossroad.LightsTimes = None
        self.lights_cycle: List[Direction] = None
        self.in_lanes: Crossroad.LaneLocations = {}
        self.out_lanes: Crossroad.LaneLocations = {}
        self.add_in_lanes()
        self.add_out_lanes()

    def generate_cycle(self):
        cycle = []
        finish_time = 0
        for direction in self.lights_order:
            finish_time += self.lights_times[direction]
            cycle.append([direction, finish_time])
            finish_time += 5
            cycle.append([None, finish_time])
        return cycle

    def step(self, turn: int) -> int:
        """
        Runs one simulation step

        Args:
            time (int): turn in simulation

        Returns:
            int: score for this step
        """
        score = 0
        for cycle in self.lights_cycle:
            if cycle[1] >= turn:
                green_light_now = cycle[0]
                break
        else:
            green_light_now = None
        # if yellow light reset all counters

        if green_light_now == None:
            self.reset_lights_counters()
        else:
            # process cars in lane with green lights
            processed_car = self.in_lanes[green_light_now].process_cars()
            if processed_car is not None and processed_car.path != []:
                self.out_lanes[processed_car.path[0]].add_car(processed_car)
                processed_car.move()

        for in_lane in self.in_lanes.values():
            for car in in_lane.queue:
                score += car.waiting_time
                car.waiting_time += 1

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
    def __init__(self, turn_time=120, cycles=5) -> None:
        self.crossroad_network = CrossroadNetwork()
        self.turn_time = turn_time
        self.cycles = cycles
        self.car_adder = self.generate_add_car_lst()

    def run(self, solution) -> int:
        """
        Runs simulation and returns score.

        Returns:
            int: score
        """
        for crossroad in self.crossroad_network.crossroad_network:
            crossroad.reset_queues()
        for i, crossroad in enumerate(self.crossroad_network.crossroad_network):
            crossroad.lights_times = solution[i][0]
            crossroad.lights_order = solution[i][1]
            crossroad.lights_cycle = crossroad.generate_cycle()
        score = 0
        for _ in range(self.cycles):
            for t in range(self.turn_time):
                if not t % 4:
                    self.add_car(self.car_adder[t][0], self.car_adder[t][1])
                for crossroad in self.crossroad_network.crossroad_network:
                    score += crossroad.step(t)
        return score

    def init_corssroad_params(self, solution):
        for crossroad in self.crossroad_network.crossroad_network:
            crossroad.reset_queues()
        for i, crossroad in enumerate(self.crossroad_network.crossroad_network):
            crossroad.lights_times = solution[i][0]
            crossroad.lights_order = solution[i][1]
            crossroad.lights_cycle = crossroad.generate_cycle()

    def step(self, t: int) -> None:
        """
        Makes step in simulation. Used in graphic representation.

        Args:
            t (int): Turn in simulation
        """
        if t % 2:
            self.add_car(self.car_adder[t][0], self.car_adder[t][1])
        for crossroad in self.crossroad_network.crossroad_network:
            crossroad.step(t)

    def add_car(self, car_origin, car_destination):
        """
        Generates cars from outside world.
        """
        car = Car(car_origin, car_destination)
        self.crossroad_network.crossroad_network[car.origin[0]].\
            in_lanes[car.origin[1]].add_car(car)
        

    def generate_add_car_lst(self):
        possible_origins = [(0, Direction.WEST), (0, Direction.NORTH),
                            (1, Direction.EAST), (1, Direction.NORTH),
                            (2, Direction.WEST), (2, Direction.SOUTH),
                            (3, Direction.EAST), (3, Direction.SOUTH),]
        cars = []
        for _ in range(self.turn_time):
            car_origin = random.choices(possible_origins,
                                        weights=[1, 1,
                                                 1, 1,
                                                 1, 1,
                                                 1, 1],
                                        k=1)[0]
            car_destination = random.choices(possible_origins,
                                             weights=[1, 1,
                                                      1, 1,
                                                      1, 1,
                                                      1, 1],
                                             k=1)[0]
            cars.append((car_origin, car_destination))
        return cars





if __name__ == "__main__":

    sim = Simulation()
    sol = [
        [{Direction.SOUTH: 19.06458605473439, Direction.WEST: 23.081563712730155, Direction.NORTH: 38.80217131417088, Direction.EAST: 19.051678918364573},
            [Direction.NORTH, Direction.WEST, Direction.SOUTH, Direction.EAST]],
        [{Direction.SOUTH: 31.190325357371858, Direction.WEST: 30.637419871559267, Direction.NORTH: 25.585222426325853, Direction.EAST: 12.587032344743015},
            [Direction.SOUTH, Direction.WEST, Direction.NORTH, Direction.EAST]],
        [{Direction.SOUTH: 26.1720845381231, Direction.WEST: 10.811284569600645, Direction.NORTH: 28.352282624239628, Direction.EAST: 34.664348268036626},
         [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]],
        [{Direction.SOUTH: 27.094910679245277, Direction.WEST: 34.359840417504984, Direction.NORTH: 11.028910009813483, Direction.EAST: 27.516338893436256},
            [Direction.SOUTH, Direction.NORTH, Direction.EAST, Direction.WEST]]
    ]
    sol2 = [
        [{Direction.SOUTH: 9.06458605473439, Direction.WEST: 53.081563712730155, Direction.NORTH: 18.80217131417088, Direction.EAST: 19.051678918364573},
            [Direction.NORTH, Direction.WEST, Direction.SOUTH, Direction.EAST]],
        [{Direction.SOUTH: 31.190325357371858, Direction.WEST: 30.637419871559267, Direction.NORTH: 25.585222426325853, Direction.EAST: 12.587032344743015},
            [Direction.SOUTH, Direction.WEST, Direction.NORTH, Direction.EAST]],
        [{Direction.SOUTH: 26.1720845381231, Direction.WEST: 10.811284569600645, Direction.NORTH: 28.352282624239628, Direction.EAST: 34.664348268036626},
         [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]],
        [{Direction.SOUTH: 27.094910679245277, Direction.WEST: 34.359840417504984, Direction.NORTH: 11.028910009813483, Direction.EAST: 27.516338893436256},
            [Direction.SOUTH, Direction.NORTH, Direction.EAST, Direction.WEST]]
    ]
    print(sim.run(sol))
    print(sim.run(sol2))
