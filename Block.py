class Block:
    def __init__(self, x, y, z, t):
        self.x = x
        self.y = y
        self.z = z
        self.type = t
    def printLocation(self):
        print(str(self.x) + ", " + str(self.y) + ", " + str(self.z))
