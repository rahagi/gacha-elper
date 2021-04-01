from random import randint
from scipy import spatial


class Coordinate:
    """
    Represent a coordinate on screen.
    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        coord1 = self.x, self.y
        coord2 = other.x, other.y
        return spatial.distance.euclidean(coord1, coord2) < 10

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def randomize(self, radius=3):
        """
        Return new `Coordinate` with randomized x and y value within `radius`.
        """
        x = self.x + randint(-radius, radius)
        y = self.y + randint(-radius, radius)
        return Coordinate(x, y)
