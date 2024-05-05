from typing import Tuple, Optional
# Author:   Daryl Damman (daryld@iastate.edu)
# Date:     2024-02-05

# Measurements are all in inches.
HOLE_DIAM = 0.1
HOLE_RADIUS = HOLE_DIAM / 2
BREADBOARD_HEIGHT = 2.125
BREADBOARD_WIDTH = 6.5

SCREW_TOLERANCE = 5 / 8
CENTER_DISTANCE = 0.3125
PAD_BOTH_SIDES = True

XORIGIN: float
YORIGIN: float

def calculateHole(x: float, y: float, yoffset: Optional[bool] = False)\
    -> Tuple[Tuple[float, float], Tuple[float, float]]:
    xcenter, ycenter = (x, y)

    if x > XORIGIN:
        xcenter -= CENTER_DISTANCE
    else:
        xcenter += CENTER_DISTANCE

    if not yoffset:
        if y > YORIGIN:
            ycenter -= CENTER_DISTANCE
        else:
            ycenter += CENTER_DISTANCE

    xedge, yedge = (xcenter - HOLE_RADIUS, ycenter)
    return (xcenter, ycenter), (xedge, yedge)

def calculateCenterHole(xval: float, height: float, count: int, yoffset: float) -> None:
    yadjust = height / (count - 1)
    for i in range(1, count - 1):
        (centerPoint, edgePoint) = calculateHole(xval, yadjust * i + yoffset, True)
        print(f"\n{centerPoint[0]},{centerPoint[1]}\n{edgePoint[0]},{edgePoint[1]}")

if __name__=='__main__':
    import sys
    if (len(sys.argv) < 4):
        print("Include arguments: <name> <breadboard up> <breadboard right> [yoffset] [xoffset]")
        exit()

    name: str = sys.argv[1]
    try:
        vertCount = int(sys.argv[2])
        horzCount = int(sys.argv[3])
    except TypeError:
        print("Whole numbers for breadboard measurements only.")
        exit()

    xoffset, yoffset = (0, 0)
    if (len(sys.argv) >= 5):
        yoffset = float(sys.argv[4])
    if (len(sys.argv) >= 6):
        xoffset = float(sys.argv[5])

    print(name, vertCount, horzCount)

    XORIGIN, YORIGIN = (xoffset, yoffset)
    xfinal, yfinal = (XORIGIN + BREADBOARD_WIDTH * horzCount, YORIGIN + BREADBOARD_HEIGHT * vertCount)

    if (PAD_BOTH_SIDES):
        xfinal += 2 * SCREW_TOLERANCE
    else:
        xfinal += SCREW_TOLERANCE

    print(f"rect\n{XORIGIN},{YORIGIN}\n{xfinal},{yfinal}")

    # Calculate holes now!
    (centerPoint, edgePoint) = calculateHole(XORIGIN, YORIGIN)
    print(f"circle\n{centerPoint[0]},{centerPoint[1]}\n{edgePoint[0]},{edgePoint[1]}")

    #! Mid-point holes
    if (vertCount > 2):
        calculateCenterHole(XORIGIN, yfinal - YORIGIN, vertCount, YORIGIN)

    (centerPoint, edgePoint) = calculateHole(XORIGIN, yfinal)
    print(f"\n{centerPoint[0]},{centerPoint[1]}\n{edgePoint[0]},{edgePoint[1]}")

    (centerPoint, edgePoint) = calculateHole(xfinal, YORIGIN)
    print(f"\n{centerPoint[0]},{centerPoint[1]}\n{edgePoint[0]},{edgePoint[1]}")

    #! Mid-point holes
    if (vertCount > 2):
        calculateCenterHole(xfinal, yfinal - YORIGIN, vertCount, YORIGIN)

    (centerPoint, edgePoint) = calculateHole(xfinal, yfinal)
    print(f"\n{centerPoint[0]},{centerPoint[1]}\n{edgePoint[0]},{edgePoint[1]}")
    print()
