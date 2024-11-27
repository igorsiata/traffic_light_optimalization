import unittest
from scripts.simulation.simulation import *


class TestCarProcessing(unittest.TestCase):
    def test_car_passing(self):
        cn = CrossroadNetwork()
        cn.crossroad_network[0].out_lanes[Direction.SOUTH].add_car(1)
        cn.crossroad_network[0].out_lanes[Direction.SOUTH].add_car(3)
        self.assertEqual(
            cn.crossroad_network[2].in_lanes[Direction.NORTH].queue, [1, 3])


if __name__ == "__main__":
    unittest.main()
