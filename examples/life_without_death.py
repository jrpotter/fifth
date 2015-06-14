"""
B3/S012345678: Life Without Death

@author: jrpotter
@date: June 02, 2015
"""
if __name__ == '__main__':

    import os, sys
    sys.path.append(os.path.abspath('src'))

    import cam
    import cam_parser

    c = cam.CAM(1, 100, 2)
    p = cam_parser.CAMParser('B3/S012345678', c)

    c.randomize()
    c.start_plot(50, p.ruleset)
