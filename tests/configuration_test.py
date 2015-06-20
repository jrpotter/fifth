import os, sys
sys.path.insert(0, os.path.join('..', 'src'))

import plane
import numpy as np
from configuration import Neighborhood
from configuration import Configuration


class TestConfiguration:
    """

    """
    def setUp(self):
        self.neighborhood = Neighborhood(0)

        self.plane2d = plane.Plane((10, 10))
        self.config2d = Configuration(0, plane=self.plane2d, offsets={
            (-1, -1): 1,
            (-1, 0): 1,
            (1, -1): 1,
            (0, 0): 1
        })

        self.plane3d = plane.Plane((100, 100, 100))
        self.config3d = Configuration(1, plane=self.plane3d, offsets={
            (-1, 0, 1): 1,
            (-2, 1, 1): 1,
            (-1, 0, 0): 0
        })

    def test_mooreNeighborhoodOffsets(self):
        """

        """
        assert len(Configuration.moore(self.plane2d)) == 8
        assert len(Configuration.moore(self.plane3d)) == 26

    def test_neumannNeighborhoodOffsets(self):
        """

        """
        assert len(Configuration.neumann(self.plane2d)) == 4
        assert len(Configuration.neumann(self.plane3d)) == 6

    def test_matchNeighborhood(self):
        """

        """
        assert not self.config2d.matches(self.plane2d, self.neighborhood)
        self.plane2d[[(-1, -1), (-1, 0), (1, -1), (0, 0)]] = 1
        assert self.config2d.matches(self.plane2d, self.neighborhood)

    def test_toleranceNeighborhood(self):
        """

        """
        assert not self.config2d.tolerates(self.plane2d, self.neighborhood, 0.5)
        self.plane2d[(-1, -1)] = 1
        assert not self.config2d.tolerates(self.plane2d, self.neighborhood, 0.5)
        self.plane2d[(-1, 0)] = 1
        assert self.config2d.tolerates(self.plane2d, self.neighborhood, 0.5)

