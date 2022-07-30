from PIL import Image
import numpy
import glob

class BlocksArray:
    classBlocksNames = []
    def __init__(self) -> None:
        self.blocksPixels = self.blocksArray()
        self.blocksNames = self.classBlocksNames

    def rgbValues(self, imageName: str):
        im = Image.open("block/" + imageName, "r")
        pixelValues = list(im.getdata())
        blockRGBValues = numpy.array([], dtype = numpy.uint8)
        for rgba in pixelValues:
            blockRGBValues = numpy.append(blockRGBValues, rgba[0])
            blockRGBValues = numpy.append(blockRGBValues, rgba[1])
            blockRGBValues = numpy.append(blockRGBValues, rgba[2])
        return blockRGBValues

    def blocksArray(self):
        self.blocksNames = []
        blocks = numpy.empty((0, 0), dtype = numpy.uint8)

        directory = "./block"
        for filename in glob.iglob(f'{directory}/*'):
            if filename.endswith(".png"):
                self.classBlocksNames.append(filename[8:])
                values = self.rgbValues(filename[8:])
                blocks = numpy.append(blocks, values)
        return blocks