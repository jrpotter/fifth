import os, sys
sys.path.insert(0, os.path.join('..', 'src'))

import plane
import ruleset as r
import configuration as c

class TestRuleset:
    """

    """
    def setUp(self):
        """

        """
        self.plane2d = plane.Plane((100, 100))
        self.config = c.Configuration(1, plane=self.plane2d, offsets={
            (-1, 0): 1,
            (-1, 1): 0,
            ( 0, 1): 1,
            ( 1, 1): 1,
        })

    def test_alwaysPassRuleset(self):
        """

        """
        # No configurations
        tmp_r = r.Ruleset(r.Ruleset.Method.ALWAYS_PASS)
        tmp_p = self.plane2d.bits.copy()
        tmp_r.apply_to(self.plane2d)
        assert tmp_p == self.plane2d.bits

        # One configuration
        tmp_r.configurations.append(self.config)
        tmp_r.apply_to(self.plane2d)
        assert tmp_p != self.plane2d.bits
        assert self.plane2d.bits.count() == 100 * 100

    def test_matchRuleset(self):
        """

        """
        # No configurations
        tmp_r = r.Ruleset(r.Ruleset.Method.MATCH)
        tmp_p = self.plane2d.bits.copy()
        tmp_r.apply_to(self.plane2d)
        assert tmp_p == self.plane2d.bits

        # One configuration
        tmp_r.configurations.append(self.config)
        tmp_r.apply_to(self.plane2d)
        assert tmp_p == self.plane2d.bits
        self.plane2d[[(-1, 0), (0, 1), (1, 1)]] = 1
        tmp_r.apply_to(self.plane2d)
        assert self.plane2d.bits.count() == 4

    def test_tolerateRuleset(self):
        """

        """
        # No configurations
        tmp_r = r.Ruleset(r.Ruleset.Method.TOLERATE)
        tmp_p = self.plane2d.bits.copy()
        tmp_r.apply_to(self.plane2d)
        assert tmp_p == self.plane2d.bits

        # One configuration
        tmp_r.configurations.append(self.config)
        tmp_r.apply_to(self.plane2d, 0.5)
        assert tmp_p == self.plane2d.bits

        self.plane2d[(-1, 0)] = 1
        tmp_r.apply_to(self.plane2d, 0.5)
        assert self.plane2d.bits.count() == 4

