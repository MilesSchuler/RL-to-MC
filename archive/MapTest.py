from ObjReader import OBJ
from PIL import Image, ImageDraw
import numpy as np

name = 'mountain'
model = OBJ(name)


coords = [1, 1, 1]


vertices = model.getVertices()
textures = model.getTextures()
faces = model.getFaces()
materials = model.getMaterials()

# assume there is only one material
mtl = materials[0]
# file name is a full path but we just want the name
mapName = mtl['map_Kd'].split("\\")[-1]
mapPath = "./Data/" + model.getName() + "/" + mapName
textmap = Image.open(mapPath)
pixels = textmap.load()
width, height = textmap.size


# testing on first face
vert_indices = faces[0, :, 0]
text_indices = faces[0, :, 1]

v_points = vertices[vert_indices - 1].T
t_points = np.append(textures[text_indices - 1].T, [[0, 0, 0]], axis=0)

v_inv = np.linalg.inv(v_points)

R = np.matmul(t_points, v_inv)

