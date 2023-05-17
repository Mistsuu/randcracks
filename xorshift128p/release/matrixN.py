import gmpy2
import random
from copy import deepcopy

"""
    Matrices here are represented as
    lists of gmpy2.mpz(x)s.

    Vectors are represented as a value
    of gmpy2.mpz(x).

    None of the functions here has a
    check condition code to optimize
    runtime.

    (This file is different, it's got
    different functions)
"""

# ========================================================================
#                             BASIC ARITHMETICS
# ========================================================================

def bitstring_to_vecN(bitstring):
    return gmpy2.mpz(int(bitstring[::-1], 2))

def identity_matN(N):
    I = []
    t = gmpy2.mpz(1)
    for i in range(N):
        I.append(t)
        t <<= 1
    return I

def zero_matN(N):
    return [gmpy2.mpz(0)] * N

def rand_matN(N):
    return [gmpy2.mpz(random.getrandbits(N)) for i in range(N)]

def debug_vecN(v, N):
    print(f'{v:0{N}b}'[::-1])
    print()

def debug_matN(M, nrows, ncols=None):
    if ncols == None:
        ncols = nrows
    for i in range(nrows):
        print(f'{M[i]:0{ncols}b}'[::-1])
    print()

def get_entry_matN(M, x, y):
    """
        get_entry_matN(M, x, y):
            Get value at M[x, y]
    """
    return int(gmpy2.bit_test(M[x], y))

def set_entry_matN(M, x, y, b):
    """
        set_entry_matN(M, x, y, b):
            Set M[x, y] = b.
    """
    if b == 0:
        M[x] = gmpy2.bit_clear(M[x], y)
    else:
        M[x] = gmpy2.bit_set(M[x], y)

# ========================================================================
#                          LINEAR ALGEBRA STUFFS
# ========================================================================

import matrix_cython_initializer
from cmatrixN import (
    rref, 
    find_pivot, 
    solve_right,
    transpose,
    kernel_right
)