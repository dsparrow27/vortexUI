from Qt import QtCore


TOP = 0
BOTTOM = 1
LEFT = 2
RIGHT = 3
CENTER = 4
X = 5
Y = 6


def avgPosX(items):
    avg = 0.0
    for i in items:
        avg += i.x()
    return avg / len(items)


def avgPosY(items):
    avg = 0.0
    for i in items:
        avg += i.y()
    return avg / len(items)


def minPosX(items):
    return min([i.x() for i in items])


def minPosY(items):
    return min([i.y() for i in items])


def maxPosX(items):
    return max([i.x() for i in items])


def maxPosY(items):
    return max([i.y() for i in items])


def nodesAlignX(items, direction):
    if direction == CENTER:
        avg = avgPosX(items)
        for i in items:
            i.setPos(QtCore.QPointF(avg, i.y()))
    elif direction == RIGHT:
        maxX = maxPosX(items)
        for i in items:
            i.setPos(QtCore.QPointF(maxX, i.y()))
    elif direction == LEFT:
        minX = minPosX(items)
        for i in items:
            i.setPos(QtCore.QPointF(minX, i.y()))


def nodesAlignY(items, direction):
    if direction == CENTER:
        avg = avgPosY(items)
        for i in items:
            i.setPos(QtCore.QPointF(i.x(), avg))
    elif direction == TOP:
        maxY = minPosY(items)
        for i in items:
            i.setPos(QtCore.QPointF(i.x(), maxY))
    elif direction == BOTTOM:
        minY = maxPosY(items)
        for i in items:
            i.setPos(QtCore.QPointF(i.x(), minY))
