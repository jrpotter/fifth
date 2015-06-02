"""
B3/S012345678: Life Without Death

@author: jrpotter
@date: June 02, 2015
"""
if __name__ == '__main__':

    import os, sys
    sys.path.append(os.path.abspath('src'))

    import cam
    import ruleset as rs


    def lwd(f_index, f_grid, indices, states, *args):
        total = sum(f_grid[indices])
        if not f_grid[f_index] and total == 3:
            return rs.Configuration.ON
        else:
            return f_grid[f_index]


    c = cam.CAM(1, 100, 2)
    c.randomize()

    r = rs.Ruleset(rs.Ruleset.Method.SATISFY)
    offsets = rs.Configuration.moore(c.master)
    r.addConfiguration(c.master, lwd, offsets)

    c.start_plot(100, r, lambda *args: True)
