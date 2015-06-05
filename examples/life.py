"""
B3/S23: Game of Life

@author: jrpotter
@date: June 01, 2015
"""
if __name__ == '__main__':

    import os, sys
    sys.path.append(os.path.abspath('src'))

    import cam
    import util as u
    import ruleset as rs

    c = cam.CAM(1, 100, 2)
    p = u.CAMParser('B3/S23', c)

    c.randomize()
    c.start_plot(400, p.ruleset)
