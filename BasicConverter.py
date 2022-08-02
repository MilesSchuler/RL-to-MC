import numpy as np


def snapVertices(self, model, height):

    vertices = model.getVertices()
    textures = model.getTextures()
    faces = model.getFaces()

    ## Snapping vertices to cube lattice

    maxH = np.amax(vertices, axis = 0)[1]
    minH = np.amin(vertices, axis = 0)[1]

    scaleFactor = (maxH - minH) / height

    # Creates new array of the same shape as vertices filled with the scale factor
    constArr = np.full(np.shape(vertices), scaleFactor)
    # Snapping each point to the top left corner of the cube
    snap = np.floor_divide(vertices, constArr)


    # Used to make all block positions non-negative
    mins = np.amin(snap, axis=0)
    maxes = np.amax(snap, axis=0)

    for i in range(len(snap)):

        coords = snap[i]
        x = int(coords[0] - mins[0])
        y = int(coords[1] - mins[1])
        z = int(coords[2] - mins[2])

        snap[i] = [x, y, z]

    uSnap = np.unique(snap, axis=0)

    # add one to each element because this is the max and... 0-based counting idk
    shape = np.int_(maxes - mins) + [1, 1, 1]

    return shape, snap, uSnap
        