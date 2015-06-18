"""
B3/S23: Game of Life

@author: jrpotter
@date: June 01, 2015
"""
if __name__ == '__main__':

    import os, sys
    sys.path.append(os.path.abspath('src'))

    import cam
    import cam_parser

    c = cam.CAM(1, 100, 2)
    p = cam_parser.CAMParser('B3/S23', c)

    #c.randomize()

    # Glider Gun 9x36
    from bitarray import bitarray
    row = [1<<11
          ,1<<13|1<<11
          ,1<<23|1<<22|1<<15|1<<14|1<<1|1<<0
          ,1<<24|1<<20|1<<15|1<<14|1<<1|1<<0
          ,1<<35|1<<34|1<<25|1<<19|1<<15|1<<14
          ,1<<35|1<<34|1<<25|1<<21|1<<19|1<<18|1<<13|1<<11
          ,1<<25|1<<19|1<<11
          ,1<<24|1<<20
          ,1<<23|1<<22
          ]

    for i in range(9):
        c.master.grid[35+i][12:48] = bitarray(bin(row[i])[2:].zfill(36))

    c.start(cam.CAM.Show.CONSOLE, clock=50, rules=p.ruleset)
