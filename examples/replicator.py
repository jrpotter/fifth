"""
B1357/S1357: Replicator

@author: jrpotter
@date: June 02, 2015
"""
if __name__ == '__main__':

    import os, sys
    sys.path.append(os.path.abspath('src'))

    import cam
    import cam_parser

    c = cam.CAM(1, 100, 2)
    p = cam_parser.CAMParser('B1357/S1357', c)

    for i in range(49, 52):
        c.master.grid[i][49:51] = 1

    c.start_plot(50, p.ruleset)
