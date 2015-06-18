"""
B368/S245: Morley

@author: jrpotter
@date: June 02, 2015
"""
if __name__ == '__main__':

    import os, sys
    sys.path.append(os.path.abspath('src'))

    import cam
    import cam_parser

    c = cam.CAM(1, 100, 2)
    p = cam_parser.CAMParser('B368/S245', c)

    c.randomize()
    c.start(cam.CAM.Show.WINDOW, clock=50, rules=p.ruleset)
