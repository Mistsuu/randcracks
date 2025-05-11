import os
import sys

"""
    Matrices here are represented as
    lists of gmpy2.mpz(x)s.

    (I created 2 files because I'm lazy)
"""

# ========================================================================
#                             CYTHON'S CODE
# ========================================================================

scriptDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(scriptDir)

import init_cmatrix
from cmatrix64 import (
    add_mat64, 
    mul_mat64
)