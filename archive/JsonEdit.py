# This was for editing the java to bedrock json I'm saving it just in case

import json
import copy 
file = open('Data/block/jb.json')
data = json.load(file)
file.close()
keys = copy.copy(list(data.keys()))
prev_name = ""
for name in keys:
    if "[" in name:
        short_name = name.split("[")[0]
        if short_name != prev_name:
            val = data[name]
            data.pop(name)
            data[short_name] = val
            prev_name = short_name
file = open('Data/block/jb.json', 'w')
json.dump(data, file, indent=4)