import numpy as np
import collections
from tqdm import tqdm


class FindBlocks:

    def __init__(self, model, height):
        self.faces = model.getFaces()
        self.vertices = model.getVertices()
        self.textures = model.getTextures()
        self.height = height
        

    def convertModel(self):
        dict = collections.defaultdict(list)
        blockCoords = []
        for faceIndex in tqdm(range(len(self.faces))):
            blocks = self.blocksInFace(faceIndex)
            for block in blocks:
                x = str(block[0])
                y = str(block[1])
                z = str(block[2])
                inFace = block[3]
                dict[x + " " + y + " " + z].append(inFace)
                blockCoords.append(np.array([x, y, z]))
                
        blockCoords = np.unique(np.int_(np.array(blockCoords)), axis=0)
        
        mins = np.amin(blockCoords, axis=0)
        blockCoords -= mins

        return dict, blockCoords, mins
    
    def blocksInFace(self, fIndex):
        f = self.faces[fIndex]
        # list of blocks that are touching this face and the face they are touching
        # this should go in the defaultdict so idk if we want to do it here or elsewhere
        blockList = []
        # get vertex indices and shift to 0-based
        vIndices = f[:,0] - 1
        # get vertex coords for points in this face
        fVertices = self.vertices[vIndices]
        # define direction vectors u and v for plane made by face
        u = fVertices[1] - fVertices[0]
        v = fVertices[2] - fVertices[1]

        # get corners of face bounding box (rectangular prism)
        box = [min(fVertices[:,0]), min(fVertices[:,1]), min(fVertices[:,2]), max(fVertices[:,0]), max(fVertices[:,1]), max(fVertices[:,2])]
        
        # max and min of vertices
        maxH = np.amax(self.vertices, axis=0)[1]
        minH = np.amin(self.vertices, axis=0)[1]
        # scaling factor, also the length of a block
        scaleFactor = (maxH - minH) / self.height

        # convert vertex coords into scaled int coords that are minecraft block coords,
        # for both corners
        p1 = np.int_(box[:3] // scaleFactor)
        p2 = np.int_(box[3:] // scaleFactor)
        
        # loop through all blocks in the bounding box
        for z in range(p1[2], p2[2] + 1):
            for y in range(p1[1], p2[1] + 1):
                for x in range(p1[0], p2[0] + 1):
                    block = np.array([x, y, z])
                    # turn the block coords back into the vertex coords and then shift from top corner to middle
                    coords = block * scaleFactor + (scaleFactor / 2)
                    # get the distance between the middle of our block and the plane
                    # we need to pass in a point on the plane, so we just use a vertex
                    # TODO in theory this could be done all at once using matrices instead of having to go through each block
                    distance = self.distToPlane(u, v, fVertices[0], coords)
                    # distance from center to corner is sqrt3 / 2
                    cutoff = np.sqrt(3) * scaleFactor / 2
                    if distance < cutoff:
                        block = np.append(block, fIndex)
                        blockList.append(block)
        return blockList
    
    def distToPlane(self, u, v, p, coords):
        a = coords - p
        # get normal vector using cross product
        normal = np.cross(u, v)
        # distance = a dot normal  / ||normal||
        distance = np.dot(a, normal) / np.sqrt(np.dot(normal, normal))
        return distance
