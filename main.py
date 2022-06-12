from Point import Point
from ObjReaderV1 import OBJReader

# example using new Point class
testPoint = Point(1.0, 1.5, 2.0)
testPoint.printLocation()

objReader = OBJReader
# i dont know if the dwayne.obj is the right thing to pass
objReader.readOBJ("dwayne.obj")