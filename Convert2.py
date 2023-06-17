from tqdm import tqdm

from EuclideanDistance import EuclideanDistance
from ConvertBlocksToArray import BlocksArray
import numpy as np


class Convert2:
    def compute(self, snap, texture, blockPixels, blockTypes):
        # loop through faces
        for i in tqdm(range(len(self.faces))):
            f = self.faces[i]
            # indices from faces list
            vIndices = f[:,0]
            # put those into snap to get block coords for the corners of the face
            # this is actually unnecessary once we get blocksInFace working
            # but I'm keeping here because it is helpful for testing
            blocks = snap[vIndices]
            # find all blocks in the face and print
            blockList = self.blocksInFace(f, vIndices)
            # format looks like this [minecraft x, minecraft y, minecraft z, center x, center y]
            print(blockList)
            # So these should be the same (or the first one should have more
            # since it includes all the blocks not just the corners) but they are different
            # idk why its not working sorry
            print(blocks)
            # breaking after the first one
            break
            # this is where we would get the texture of each block and do the
            # euclidean distance calculations, etc
            # so we would use the matrix code in MapTest
            """
            
            img = texture.getImage(cube)

            ec = EuclideanDistance(blockPixels)
            neighborIndex = ec.find_closest_neighbor(img)

            blockName = blockTypes[neighborIndex]
            self.blocksList.append(blockName)
            """

    def __init__(self, model, snap, texture, height):
        self.blocksList = []
        blockPixels, blockTypes = BlocksArray().blockInfo
        self.vertices = model.getVertices()
        self.faces = model.getFaces()
        self.height = height
        self.compute(snap, texture, blockPixels, blockTypes)
        

    def blocksInFace(self, face, vIndices):
        # list of blocks that are touching this face and the face they are touching
        blockList = []
        # shift vertex indices to 0-based
        vIndices = vIndices - 1
        # get vertex coords for points in this face
        fVertices = self.vertices[vIndices]
        # define direction vectors u and v for plane made by face
        u = fVertices[1] - fVertices[0]
        v = fVertices[2] - fVertices[0]
    
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
                    distance, center = self.distToPlane(u, v, fVertices[0], coords)
                    # distance from center to corner is sqrt3 / 2
                    # so we use this cutoff to make sure the face goes through the block
                    cutoff = np.sqrt(3) * scaleFactor / 2
                    if distance < cutoff:
                        # including the center of the block obj coords bc that might be helpful
                        # But the way for getting the center is kinda bad - see below (sorry again)
                        block = np.append(block, center)
                        blockList.append(block)
        return blockList
    
    def distToPlane(self, u, v, p, coords):
        a = coords - p
        # get normal vector using cross product
        normal = np.cross(u, v)
        # distance = a dot normal / ||normal||
        mag = np.sqrt(np.dot(normal, normal))
        distance = np.dot(a, normal) / mag
        
        # calculate resulting vector when a is projected onto the normal
        unitNormal = normal / mag
        projection = distance * unitNormal
        # use that vector to find point where coords is closest to plane,
        # aka where the center of the block would project to
        center = a - projection
        
        
        # NOTE I do not understand this comment so I've just been ignoring it
        # OLD COMMENT:
        # currently have it in x y z plane but need it in terms of u and v
        # only need two of the three dimensions to solve equation
        # but two of the three can be zero which breaks the np.linalg.solve so we try/except to account for that
        # i tried ifs but that didn't work cuz there are so many possibilities
        # TODO better way?
        coeff = np.array([[u[0], v[0]], [u[1], v[1]]])
        result = np.array([center[0], center[1]])
        try:
            center = np.linalg.solve(coeff, result)
        except:
            coeff = np.array([[u[1], v[1]], [u[2], v[2]]])
            result = np.array([center[1], center[2]])
            try:
                center = np.linalg.solve(coeff, result)
            except:
                coeff = np.array([[u[0], v[0]], [u[2], v[2]]])
                result = np.array([center[0], center[2]])
                try:
                    center = np.linalg.solve(coeff, result)
                except:
                    print(coeff, u, v)
        return distance, center
