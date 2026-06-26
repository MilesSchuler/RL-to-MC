import numpy as np


def snapVertices(model, height):

    vertices = model.getVertices()

    ## Snapping vertices to cube lattice

    maxH = np.amax(vertices, axis=0)[1]
    minH = np.amin(vertices, axis=0)[1]

    scaleFactor = (maxH - minH) / height

    # Creates new array of the same shape as vertices filled with the scale factor
    constArr = np.full(np.shape(vertices), scaleFactor)
    # Snapping each point to the top left corner of the cube
    snap = np.int_(np.floor_divide(vertices, constArr))

    # Used to make all block positions non-negative
    mins = np.amin(snap, axis=0)
    maxes = np.amax(snap, axis=0)

    snap -= mins

    uSnap = np.unique(snap, axis=0)

    # add one to each element because the number of integers from m to n in n-m+1
    shape = np.int_(maxes - mins + np.array([1, 1, 1]))

    return shape, snap, uSnap
        