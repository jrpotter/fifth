"""

@author: jrpotter
@date: June 01, 2015
"""
if __name__ == '__main__':

    import os, sys
    sys.path.append(os.path.abspath('src'))

    import cam
    import ruleset as rs


    def game_of_life(f_index, f_grid, indices, states, *args):
        """
        Rules of the Game of Life.

        Note we ignore the second component of the neighbors tuples since
        life depends on all neighbors
        """
        total = sum(f_grid[indices])
        if f_grid[f_index]:
            if total < 2 or total > 3:
                return rs.Configuration.OFF
            else:
                return rs.Configuration.ON
        elif total == 3:
            return rs.Configuration.ON
        else:
            return rs.Configuration.OFF


    c = cam.CAM(1, 100, 2)
    c.randomize()

    r = rs.Ruleset(rs.Ruleset.Method.SATISFY)
    offsets = rs.Configuration.moore(c.master)
    r.addConfiguration(c.master, game_of_life, offsets)

    c.start_plot(100, r, lambda *args: True)
