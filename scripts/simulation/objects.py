from typing import List
from collections import deque
from enum import Enum
import random


class Turn(Enum):
    LEFT = "L"
    RIGHT = "R"
    FORWARD = "F"

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return self.name


class Location(Enum):
    SOUTH = "S"
    WEST = "W"
    NORTH = "N"
    EAST = "E"

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return self.name


class Car:
    def __init__(self, location, turn) -> None:
        self.location: Location = location
        self.turn: Turn = turn

    def __str__(self) -> str:
        return f"Car from:{self.location}, turning {self.turn}"

    def __repr__(self) -> str:
        return f"<Car(location={self.location}, turn={self.turn})>"


class Lane:
    def __init__(self, location: Location, possible_turns: List[int], processing_time=2) -> None:
        self.location: Location = location
        self.possible_turns: List[Turn] = possible_turns
        self.collisions: List[Lane] = []
        self.green_light: bool = False
        self.queue: List[Car] = []
        self.processing_time = processing_time
        self.ticks_counter = 0

    def __str__(self) -> str:
        return f"Lane location: {self.location}, turns{self.possible_turns}"

    def __repr__(self) -> str:
        return self.__str__()

    def process_cars(self):
        if self.green_light and self.queue:
            self.ticks_counter += 1
            if self.ticks_counter >= self.processing_time:
                self.ticks_counter = 0
                return self.queue.pop(0)
        else:
            self.ticks_counter = 0
        return None

    def add_car_to_queue(self, car: Car):
        self.queue.append(car)


class Crossroad:
    def __init__(self) -> None:
        self.lanes: List[Lane] = []

    def step(self, ticks) -> None:
        print(f"Turn: {ticks}")
        for lane in self.lanes:
            print(f"{lane}, queue={len(lane.queue)}")
        self.process_cars()

    def process_cars(self):
        for lane in self.lanes:
            processed_car = lane.process_cars()
            if processed_car == None:
                continue

    def add_car(self, car: Car) -> None:
        correct_lanes = []
        for lane in self.lanes:
            if lane.location == car.location and car.turn in lane.possible_turns:
                correct_lanes.append((lane, len(lane.queue)))
        lane_with_shortest_queue = min(correct_lanes, key=lambda x: x[1])[0]
        lane_with_shortest_queue.add_car_to_queue(car)


class FourDirectionTwoLaneCrossroad(Crossroad):
    direction_map = {
        Location.NORTH: {Turn.LEFT: Location.EAST,
                         Turn.RIGHT: Location.WEST,
                         Turn.FORWARD: Location.SOUTH},
        Location.SOUTH: {Turn.LEFT: Location.WEST,
                         Turn.RIGHT: Location.EAST,
                         Turn.FORWARD: Location.NORTH},
        Location.EAST: {Turn.LEFT: Location.SOUTH,
                        Turn.RIGHT: Location.NORTH,
                        Turn.FORWARD: Location.WEST},
        Location.WEST: {Turn.LEFT: Location.NORTH,
                        Turn.RIGHT: Location.SOUTH,
                        Turn.FORWARD: Location.EAST}
    }

    def __init__(self) -> None:
        super().__init__()
        self.add_lanes()
        self.add_collisions()

    def add_lanes(self) -> None:
        self.lanes.append(Lane(Location.SOUTH,
                               [Turn.LEFT]))
        self.lanes.append(Lane(Location.SOUTH,
                               [Turn.FORWARD, Turn.RIGHT]))
        self.lanes.append(Lane(Location.WEST,
                               [Turn.LEFT]))
        self.lanes.append(Lane(Location.WEST,
                               [Turn.FORWARD, Turn.RIGHT]))
        self.lanes.append(Lane(Location.NORTH,
                               [Turn.LEFT]))
        self.lanes.append(Lane(Location.NORTH,
                               [Turn.FORWARD, Turn.RIGHT]))
        self.lanes.append(Lane(Location.EAST,
                               [Turn.LEFT]))
        self.lanes.append(Lane(Location.EAST,
                               [Turn.FORWARD, Turn.RIGHT]))

    def is_collision(self, lane_a: Lane, lane_b: Lane) -> None:
        is_collsion = False

        if lane_a.location == lane_b.location:
            return False

        if Turn.LEFT in lane_a.possible_turns:
            is_collsion = True
            if lane_b.location == self.direction_map[lane_a.location][Turn.RIGHT] and \
                    Turn.LEFT not in lane_b.possible_turns:
                is_collsion = False
            if lane_b.location == self.direction_map[lane_a.location][Turn.FORWARD] and \
                    Turn.FORWARD not in lane_b.possible_turns:
                is_collsion = False

        if Turn.FORWARD in lane_a.possible_turns:
            is_collsion = True
            if lane_b.location == self.direction_map[lane_a.location][Turn.LEFT] and \
                    Turn.FORWARD not in lane_b.possible_turns:
                is_collsion = False
            if lane_b.location == self.direction_map[lane_a.location][Turn.FORWARD] and \
                    Turn.LEFT not in lane_b.possible_turns:
                is_collsion = False

        if Turn.RIGHT in lane_a.possible_turns:
            if lane_b.location == self.direction_map[lane_a.location][Turn.LEFT] and \
                    Turn.FORWARD not in lane_b.possible_turns:
                is_collsion = True
        return is_collsion

    def add_collisions(self) -> None:
        for lane_a in self.lanes:
            for lane_b in self.lanes:
                if lane_a == lane_b:
                    continue
                if self.is_collision(lane_a, lane_b):
                    lane_a.collisions.append(lane_b)

    def step(self, ticks) -> None:
        super().step(ticks)
        self.accumulate_cars()

    def accumulate_cars(self):
        random_location = random.choice(list(Location))
        random_turn = random.choice(list(Turn))
        car = Car(random_location, random_turn)
        self.add_car(car)


class Simulation:
    def __init__(self, crossroad_cls: Crossroad, max_tics=81) -> None:
        self.ticks = 0
        self.max_tics = max_tics
        self.crossroad: Crossroad = crossroad_cls()

    def step(self):
        self.ticks = (self.ticks + 1) % self.max_tics
        self.swith_lights()
        self.crossroad.step(self.ticks)

    def run_simulation(self, end):
        for i in range(end):
            self.step()

    def swith_lights(self):
        if self.ticks == 20:
            direct = Location.SOUTH
            self.do_switch(direct)
        if self.ticks == 40:
            direct = Location.EAST
            self.do_switch(direct)
        if self.ticks == 60:
            direct = Location.NORTH
            self.do_switch(direct)
        if self.ticks == 80:
            direct = Location.WEST
            self.do_switch(direct)

    def do_switch(self, location):
        for lane in self.crossroad.lanes:
            lane.green_light = (lane.location == location)


if __name__ == "__main__":
    sim = Simulation(FourDirectionTwoLaneCrossroad)
    sim.run_simulation(100)
