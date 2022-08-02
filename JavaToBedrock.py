import json


class JavaToBedrock:
    def __init__(self):
        file = open('./data/block/java2bedrock.json')
        self.data = json.load(file)
        file.close()

    def convertBlocks(self, javaPalette):
        bedrockPalette = []
        blockStates = []
        for block in javaPalette:
            try:
                blockData = self.data[block]
                bedrockPalette.append(blockData['bedrock_identifier'])
                if 'bedrock_states' in blockData.keys():
                    blockStates.append(blockData['bedrock_states'])
                else:
                    blockStates.append({})
            except:
                print('Block not found: ' + block)
                break
        return bedrockPalette, blockStates
