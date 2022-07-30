import numpy as np
from Block import Block

class BasicConverter:
    def convertModel(vertices, textures, faces, height):
        
        ## Snapping vertices to cube lattice
        maxH = np.amax(vertices, axis = 0)[1]
        minH = np.amin(vertices, axis = 0)[1]
        
        scaleFactor = (maxH - minH) / height
        
        # Creates new array of the same shape as vertices filled with the scale factor
        constArr = np.full(np.shape(vertices), scaleFactor) 
        # Snapping each point to the top left corner of the cube
        snap = np.floor_divide(vertices, constArr)
        

        ## Converting to Block class
        
        # Used to make all block positions non-negative
        mins = np.amin(snap, axis = 0) 
        maxes = np.amax(snap, axis = 0)
                
        blocks = set()

        for coords in snap:
           x = int(coords[0] - mins[0])
           y = int(coords[1] - mins[1])
           z = int(coords[2] - mins[2])

           blockType = "foo" # Will be changed to block choice eventually
            
           # Creating instance of Block class
           block = Block(x, y, z, blockType)
           
           blocks.add(block)

        # add one to each element because this is the max and... 0-based counting idk
        shape = np.int_(maxes - mins) + [1, 1, 1]

        return blocks, shape, snap
        