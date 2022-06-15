class TextureTesting:
    # figuring out how texture mapping works and how we want to use it
    # not even sure how we are going to call this class I just wanted a space to mess around


    def __init__(self, model):
        vertices = model.getVertices()
        textures = model.getTextures()
        faces = model.getFaces()
        materials = model.getMaterials()

        #print(materials)
        # ran out of time to actually do anything, will come back later