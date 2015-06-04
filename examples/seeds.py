"""
B2/S: Seeds

@author: jrpotter
@date: June 02, 2015
"""
if __name__ == '__main__':

    import os, sys
    sys.path.append(os.path.abspath('src'))

    import cam
    import cam_util as u
    import ruleset as rs

    c = cam.CAM(1, 100, 2)
    p = u.CAMParser('B2/S', c)

    c.randomize()
    c.start_plot(100, p.ruleset)
