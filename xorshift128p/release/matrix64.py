import gmpy2
from copy import deepcopy

"""
    Matrices here are represented as
    lists of gmpy2.mpz(x)s.

    (I created 2 files because I'm lazy)
"""

def add_mat64(M, N):
    """
        add_mat64(): Adding 2 64x64 matrices.
    """
    R = deepcopy(M)
    for i in range(64):
        R[i] ^= N[i]
    return R

def mul_mat64(M, N):
    """
        mul_mat64(): Multiply 2 64x64 matrices.
    """
    M = deepcopy(M)
    R = [gmpy2.mpz(0)] * 64
    for i_row in range(64):
        for i_col in range(64):
            if gmpy2.bit_test(M[i_row], 0):
                R[i_row] ^= N[i_col]
            M[i_row] >>= 1
    return R