# Real Life to Minecraft
This project is designed to convert 3D files to Minecraft structures

Currently in progress, progress updates below:

- 6/10/22: basic file parser
- 6/12/22: ~~implemented **Point** class~~
- 6/14/22: created basic converter
  - inputs: vertices of obj file, intended height in Minecraft blocks
  - ~~outputs: 3d scaled array **blocks** with blocks[x, y, z] = 1 if a vertex is present in the corresponding block and 0 if no vertex is present~~
- 6/15/22: Added material file reader; changed ~~Point~~ class to **Block** class; converter now returns set of **Block** instances
  - **Block** class includes coordinates: self.x, self.y, and self.z, as well as self.type (block type)      
- 6/17/22: First steps into nbt file creation!
- 6/24/22: Began work on Bedrock nbt
- 7/28/22: First texture image reader
- 7/30/22: Massive progress!!
  - Added Minecraft block data
  - Block classifier using minimum Euclidean distance
  - More efficient texture image reader
  - Tweaked NBT makers
- 7/31/22: Troubleshooted **Texture** code
- 8/1/22: Made block classification more efficient, worked on NBT makers

Ultimate goal: User inputs a .obj file (possibility of adding additional filetypes in the future), program outputs a downloadable Minecraft structure file.

*Disclaimer: This program and its creators are not endorsed by, directly affiliated with, maintained, authorized, or sponsored by Mojang Studios or Minecraft. All product and company names are the registered trademarks of their original owners. The use of any trade name or trademark is for identification and reference purposes only and does not imply any association with the trademark holder of their product brand.*
