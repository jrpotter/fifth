"""

@author: jrpotter
@date: June 01, 2015
"""

def game_of_life(coordinate, grid, neighbors):
    """
    Rules of the Game of Life.

    Note we ignore the second component of the neighbors tuples since
    life depends on all neighbors
    """
    total = sum(map(lambda x: x[1], neighbors))
    if grid[coordinate]:
        if total < 2 or total > 3:
            return False
        else:
            return True
    elif total == 3:
        return True
    else:
        return False

if __name__ == '__main__':

    import os, sys
    sys.path.append(os.path.abspath('src'))

    import cam
    import ruleset as rs
    import neighborhood as nh

    c = cam.CAM(1, (100, 100))
    c.randomize()
    r = rs.Ruleset(rs.Rule.SATISFY)
    n = nh.Neighborhood.moore(c.master, True)
    c.start_plot(100, r, n, game_of_life)
