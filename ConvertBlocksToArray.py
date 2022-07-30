from PIL import Image
import numpy
import glob
import os

def rgbValues(imageName: str):
    im = Image.open("block/" + imageName, "r")
    pixelValues = list(im.getdata())
    blockRGBValues = numpy.array([], dtype = numpy.uint8)
    for rgba in pixelValues:
        blockRGBValues = numpy.append(blockRGBValues, rgba[0])
        blockRGBValues = numpy.append(blockRGBValues, rgba[1])
        blockRGBValues = numpy.append(blockRGBValues, rgba[2])
    return blockRGBValues

def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)

blocks = numpy.empty((0, 0), dtype = numpy.uint8)

directory = "./block"
for filename in glob.iglob(f'{directory}/*'):
    if filename.endswith(".png"):
        values = rgbValues(filename[8:])
        blocks = numpy.append(blocks, values)

addToClipBoard(str(blocks))

class BlocksArray:
    def __init__(self):
        self.blocksArray = []