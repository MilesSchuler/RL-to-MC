from tokenize import String
import numpy as np


class OBJ:
    # Reads obj file as text document and organizes the contents
    # into self.vertices, self.textures, and self.faces
    
    def __init__(self, name):
        # name is the name of the folder and the obj file, so path is
        # bird/bird.obj, for example
        path = name + "/"
        filename = name + ".obj"
        file = open(path + filename)

        self.vertices = []
        self.textures = []
        self.faces = []
        # Each line can start with one of these
        # or a '#' to mean comment, or other random stuff
        possible_starts = ['v', 'vp', 'vn', 'vt', 'f', 'l']
        for line in file:
            # remove new lines at end of lines
            if '\n' in line:
                line = line[:-1]
            # convert to list
            nums = line.split(" ")
            # some lines are empty just for formatting
            if len(nums) <= 1:
                continue
            
            # sometimes there are extra spaces, whicih lead to empty strings in the list
            nums = [num for num in nums if num != ""]

            # character(s) at the beginning of the line tell us 
            # what the line is
            dataType = nums[0]

            # vertex (v x y z)
            if dataType == 'v':
                coords = [float(i) for i in nums[1:]]
                self.vertices.append(coords)
            # texture (maps material to self.vertices, I think)
            # (vt u v w), v and w are optional
            elif dataType == 'vt':
                texture = [float(i) for i in nums[1:]]
                self.textures.append(texture)
            # face (f v1/vt1 v2/vt2 v3/vt3)
            # can have more than 3, vts are optional and can include
            # vn, which is a normal vector
            elif dataType == 'f':
                points = nums[1:]
                # this splits up each point in the face into the vertex
                # and the vertex texture
                for i in range(len(points)):
                    p = points[i]
                    info = p.split("/")
                    points[i] = [int(i) for i in info]
                self.faces.append(points)

            # material library information, stored in a separate file and
            # tells the obj file what the texture and color is
            elif dataType == "mtllib":
                # file name comes right after the string mtllib in that line
                mtlFile = line[len("mtllib "):]
                material = open(path + mtlFile)

                # file can contain multiple different materials
                self.mtlDicts = []
                mtlData = []
                for mtlLine in material:
                    # if its not a comment
                    if mtlLine[0] != '#':
                        if "\t" in mtlLine:
                            mtlLine = mtlLine[1:]
                        if "\n" in mtlLine:
                            mtlLine = mtlLine[:-1]
                        if mtlLine != "":
                            mtlData.append(mtlLine)
                
                # loop through each line
                first = True
                curMtl = {}
                for mtlLine in mtlData:
                    info = mtlLine.split(" ")
                    # take out empty strings
                    info = [i for i in info if i != ""]
                    # new materials are defined with lines like this: newmtl MaterialName
                    if info[0] == "newmtl":
                        # if this is the start of material number 2, add material 1 to the list
                        if first:
                            first = False
                        else:
                            self.mtlDicts.append(curMtl)
                        
                        # add the name to the dict
                        curMtl["name"] = info[1]

                    # other lines give various material information, with a format similar to obj,
                    # e.g. Kd 1.0 1.0 1.0
                    else:
                        # maps will have strings, others will have floats
                        if mtlLine[:3] == "map":
                            curMtl[info[0]] = info[1]
                        else:
                            curMtl[info[0]] = [float(i) for i in info[1:]]
                self.mtlDicts.append(curMtl)

            elif dataType == "usemtl":
                # not sure what we need here yet
                continue
        file.close()
        
    def getVertices(self):
        return np.array(self.vertices)
    
    def getTextures(self):
        return np.array(self.textures)
    
    def getFaces(self):
        return np.array(self.faces)
    
    def getMaterials(self):
        return self.mtlDicts