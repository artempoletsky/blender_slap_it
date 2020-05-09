import sys
import os
import bpy

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)

import slap_it
import imp
imp.reload(slap_it)
slap_it.register()
