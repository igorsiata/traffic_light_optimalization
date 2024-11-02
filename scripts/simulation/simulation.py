from typing import List
from enum import Enum
import random


class Location(Enum):
    SOUTH = "S"
    WEST = "W"
    NORTH = "N"
    EAST = "E"

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return self.name


class Simulation:
    def __init__(self, lights_cycle, turns=0) -> None:
        self.lights_cycle = lights_cycle
        self.turn_time = len(lights_cycle)
        self.turns = turns
        print(list(Location))
        self.car_add_from = random.choices(list(Location),
                                           weights=[20, 20, 20, 20], k=len(lights_cycle))

    def run(self, lights_cycle) -> int:
        self.crossroad = Crossroad(lights_cycle)
        score = 0
        for _ in range(self.turns):
            for t in range(self.turn_time):
                self.add_car(t)
                score += self.crossroad.step(t)
        return score

    def step(self, t) -> None:
        self.add_car(t)
        self.crossroad.step(t)

    def add_car(self, t):
        location = random.choices(list(Location),
                                  weights=[20, 5, 20, 10], k=1)[0]
        # location = self.car_add_from[t]
        direction_list = list(Location)
        direction_list.remove(location)
        direction = random.choice(direction_list)
        car_to_add = Car(location, direction)
        self.crossroad.add_car(car_to_add)


class Crossroad:
    def __init__(self, lights_cycle) -> None:
        self.lights_cycle: List[bool] = lights_cycle  # direction (N,E,S,W)
        self.in_lanes: List[Lane] = []
        self.out_lanes: List[Lane] = []
        self.add_in_lanes()
        self.add_out_lanes()

    def step(self, time) -> int:
        score = 0
        green_light_now = self.lights_cycle[time]
        # yellow light so reset all counters
        if green_light_now == None:
            self.reset_lights_counters()
        # process cars in lane with green lights
        for in_lane in self.in_lanes:
            score += len(in_lane.queue)
            if in_lane.location == green_light_now:
                in_lane.process_cars()

        return score

    def reset_lights_counters(self) -> None:
        for in_lane in self.in_lanes:
            in_lane.processing_counter = 0

    def add_car(self, car: 'Car') -> None:
        for in_lane in self.in_lanes:
            if in_lane.location == car.location:
                in_lane.add_car(car)

    def add_in_lanes(self) -> None:
        self.in_lanes.append(Lane(Location.SOUTH,
                                  [Location.WEST, Location.NORTH,
                                   Location.EAST, Location.SOUTH],
                                  processing_time=2))
        self.in_lanes.append(Lane(Location.WEST,
                                  [Location.WEST, Location.NORTH,
                                   Location.EAST, Location.SOUTH],
                                  processing_time=2))
        self.in_lanes.append(Lane(Location.NORTH,
                                  [Location.WEST, Location.NORTH,
                                   Location.EAST, Location.SOUTH],
                                  processing_time=2))
        self.in_lanes.append(Lane(Location.EAST,
                                  [Location.WEST, Location.NORTH,
                                   Location.EAST, Location.SOUTH],
                                  processing_time=2))

    def add_out_lanes(self) -> None:
        self.out_lanes.append(Lane(Location.SOUTH,
                                   [], None))
        self.out_lanes.append(Lane(Location.WEST,
                                   [], None))
        self.out_lanes.append(Lane(Location.NORTH,
                                   [], None))
        self.out_lanes.append(Lane(Location.EAST,
                                   [], None))


class Car:
    def __init__(self, location, destination) -> None:
        self.location: Lane = location
        self.destination: Lane = destination
        self.path: List[Lane] = self.get_path()

    def get_path(self):
        return [self.destination]

    def move(self) -> None:
        new_lane = self.path.pop(0)
        if self.path == []:
            pass
        else:
            new_lane.add_car(self)

    def __str__(self) -> str:
        return f"Car from:{self.location}, turning {self.turn}"


class Lane:

    def __init__(self, location, out_conections, processing_time) -> None:
        self.out_connections: List['Location'] = out_conections
        self.queue: List[Car] = []
        self.location: Location = location
        self.processing_time = processing_time
        self.processing_counter = 0

    def process_cars(self) -> None:
        if not self.queue:
            return
        if self.processing_counter >= self.processing_time:
            car = self.queue.pop(0)
            car.move()
        else:
            self.processing_counter += 1

    def add_car(self, car: Car) -> None:
        self.queue.append(car)
