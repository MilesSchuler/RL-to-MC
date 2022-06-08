# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 11:59:00 2022

@author: shirl
"""

import pyvista

image = open("image.gltf")

pl = pyvista.Plotter()
pl.import_gltf(image)
pl.camera.zoom(1.7)
pl.show()

