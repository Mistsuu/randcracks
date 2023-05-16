"""
    Matrices here are represented as
    lists of gmpy2.mpz(x)s.

    (I created 2 files because I'm lazy)
"""

# ========================================================================
#                             CYTHON'S CODE
# ========================================================================

import matrix_cython_initializer
from cmatrix64 import (
    add_mat64, 
    mul_mat64
)