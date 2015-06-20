from nose.plugins.skip import SkipTest

import os, sys
sys.path.insert(0, os.path.join('..', 'src'))

import plane
import numpy as np
from neighborhood import Neighborhood


class TestNeighborhood:
    """

    """
    def setUp(self):

        self.neigh2d = Neighborhood(0)
        self.offsets2d = [(-1, 0), (1, 0)]
        self.plane2d = plane.Plane((100, 100))
        self.neigh2d.populate(self.plane2d, self.offsets2d)

        self.neigh3d = Neighborhood(0)
        self.offsets3d = [(-1, 0, 0), (1, 0, 1)]
        self.plane3d = plane.Plane((100, 100, 100))
        self.neigh3d.populate(self.plane3d, self.offsets3d)

    def test_neighborhoodLength(self):
        """
        Neighborhood Length.
        """
        assert len(self.neigh2d.neighbors) == len(self.offsets2d)
        assert len(self.neigh3d.neighbors) == len(self.offsets3d)

    def test_neighborhoodValues(self):
        """
        Neighborhood Values.
        """
        self.plane2d[(1, 0)] = 1
        self.plane2d[(99, 0)] = 1
        self.neigh2d.neighbors = [1, 1]

        self.plane3d[(1, 0, 1)] = 1
        self.plane3d[(99, 0, 0)] = 1
        self.neigh3d.neighbors = [1, 1, 1]

    @SkipTest
    def test_neighborhoodTotal(self):
        """
        Neighborhood Total.
        """
        n1 = Neighborhood.get_neighborhoods(self.plane2d, self.offsets2d)
        n2 = Neighborhood.get_neighborhoods(self.plane3d, self.offsets3d)
        assert len(n1) == len(self.plane2d.bits)
        assert len(n2) == len(self.plane3d.bits)

    @SkipTest
    def test_neighboorhoodMembers(self):
        """
        Neighborhood Members.
        """
        n1 = Neighborhood.get_neighborhoods(self.plane2d, self.offsets2d)
        n2 = Neighborhood.get_neighborhoods(self.plane3d, self.offsets3d)
        for n in n1:
            assert len(n.neighbors) == len(self.offsets2d)
        for n in n2:
            assert len(n.neighbors) == len(self.offsets3d)

    def test_neighborhoodPlaneTotalInit(self):
        """
        Plane Total Initialization.
        """
        t1 = Neighborhood.get_totals(self.plane2d, self.offsets2d)
        t2 = Neighborhood.get_totals(self.plane3d, self.offsets3d)
        assert len(t1) == np.product(self.plane2d.shape)
        assert len(t2) == np.product(self.plane3d.shape)
        assert np.count_nonzero(np.array(t1)) == 0
        assert np.count_nonzero(np.array(t2)) == 0

    def test_neighborhoodPlaneTotalCount(self):
        """
        Plane Total Count.
        """
        self.plane2d[10] = 1;
        self.plane3d[10] = 1;
        t1 = Neighborhood.get_totals(self.plane2d, self.offsets2d)
        t2 = Neighborhood.get_totals(self.plane3d, self.offsets3d)
        assert np.count_nonzero(np.array(t1)) == 200
        assert np.count_nonzero(np.array(t2)) == 20000

