import numpy as np
from tqdm import tqdm

class fillHoles:
    def __init__(self, model, bigFaces, blockFaces, snap, h):
        self.faces = model.getFaces()
        self.vertices = model.getVertices()
        self.textures = model.getTextures()
        self.dict = blockFaces
        self.snap = snap
        self.bigFaces = bigFaces
        self.height = h
    
    def fillHoles(self):   
        blockCoords = self.snap.tolist()
        for faceIndex in tqdm(range(len(self.bigFaces))):
            blocks = self.blocksInFace(self.bigFaces, faceIndex)
            for block in blocks:
                x = str(int(block[0]))
                y = str(int(block[1]))
                z = str(int(block[2]))
                faceInfo = [block[3], block[4], [block[5], block[6]]]
                # doing = instead of append to limit to one face per block for the block in big faces
                # some blocks might overlap two but I think its worth the time save
                self.dict[x + " " + y + " " + z] = faceInfo
                blockCoords.append(np.array([x, y, z]))
                
        blockCoords = np.unique(np.int_(np.array(blockCoords)), axis=0)
        
        mins = np.amin(blockCoords, axis=0)
        #blockCoords -= mins
    
        return self.dict, blockCoords
    
    def blocksInFace(self, bigFaces, fIndex):
        f = bigFaces[fIndex]
        # list of blocks that are touching this face and the face they are touching
        blockList = []
        # get vertex indices and shift to 0-based
        vIndices = f[:,0] - 1
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
        
        # get scaling factor for block length in this face
        faceSize = max(fVertices[:,0]) - min(fVertices[:,1])
        lengthScale = scaleFactor / faceSize
    
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
                    cutoff = np.sqrt(3) * scaleFactor / 2
                    if distance < cutoff:
                        faceInfo = np.append([fIndex, lengthScale], center)
                        block = np.append(block, faceInfo)
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
