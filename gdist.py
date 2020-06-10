import ctypes

import numpy as np

lib = ctypes.CDLL('./gdist_c_api.so')
# build numpy arrays etc
print(lib.computeGdist(1, 1, 1, 1))
