import os
import sys

"""
    Matrices here are represented as
    lists of gmpy2.mpz(x)s.
"""

# ========================================================================
#                             CYTHON'S CODE
# ========================================================================

scriptDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(scriptDir)

import init_cmatrix
from cmatrix32 import (
    add_mat32, 
    mul_mat32,
    mul_vecl32
)