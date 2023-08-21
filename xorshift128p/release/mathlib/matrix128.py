import os
import sys

"""
    Matrices here are represented as
    lists of gmpy2.mpz(x)s.
"""

def combine_4_mat64(
    M00, M01,
    M10, M11,
):
    R = []
    for i_row in range(64):
        R.append((M01[i_row] << 64) | M00[i_row])
    for i_row in range(64):
        R.append((M11[i_row] << 64) | M10[i_row])
    return R

# ========================================================================
#                             CYTHON'S CODE
# ========================================================================

scriptDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(scriptDir)

import init_cmatrix
from cmatrix128 import (
    add_mat128, 
    mul_mat128
)