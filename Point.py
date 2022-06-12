class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def printLocation(self):
        print(str(self.x) + ", " + str(self.y) + ", " + str(self.z))
