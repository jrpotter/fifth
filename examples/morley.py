"""
B368/S245: Morley

@author: jrpotter
@date: June 02, 2015
"""
if __name__ == '__main__':

    import os, sys
    sys.path.append(os.path.abspath('src'))

    import cam
    import ruleset as rs


    def morley(f_index, f_grid, indices, states, *args):
        total = sum(f_grid[indices])
        if not f_grid[f_index]:
            if total == 3 or total == 6 or total == 8:
                return rs.Configuration.ON
        else:
            if total == 2 or total == 4 or total == 5:
                return rs.Configuration.ON

        return rs.Configuration.OFF


    c = cam.CAM(1, 100, 2)
    c.randomize()

    r = rs.Ruleset(rs.Ruleset.Method.SATISFY)
    offsets = rs.Configuration.moore(c.master)
    r.addConfiguration(c.master, morley, offsets)

    c.start_plot(100, r, lambda *args: True)
