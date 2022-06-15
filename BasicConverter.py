import numpy as np

class BasicConverter:
    def convertModel(vertices, textures, faces, height):
        
        ##Snapping vertices to cube lattice
        maxH = np.amax(vertices, axis = 0)[1]
        minH = np.amin(vertices, axis = 0)[1]
        
        scaleFactor = (maxH - minH) / height
        
        #Creates new array of the same shape as vertices filled with the scale factor
        constArr = np.full(np.shape(vertices), scaleFactor) 
        #Snapping each point to the top left corner of the cube
        snap = np.floor_divide(vertices, constArr)
        #Removes duplicates
        snap = np.unique(snap, axis = 1) 
        
        
        ##Converting to 3d blocks array
        mins = np.amin(snap, axis = 0) #Used to make all block positions non-negative
        maxes = np.amax(snap, axis = 0)
        #print(mins, maxes)
        
        #Creates array of zeros (False)
        blocks = np.full((int(maxes[0]) - int(mins[0]) + 1, int(maxes[1]) - int(mins[1]) + 1, int(maxes[2]) - int(mins[2]) + 1), 0) 
        for block in snap:
            x = int(block[0] - mins[0])
            y = int(block[1] - mins[1])
            z = int(block[2] - mins[2])

            blocks[x, y, z] = 1 #Will be replaced with block choice function
                    
        return blocks
        