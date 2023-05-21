import gmpy2
from copy import deepcopy

"""
    Matrices here are represented as
    lists of gmpy2.mpz(x)s.
"""

def add_mat128(M, N):
    """
        add_mat128(): Adding 2 128x128 matrices.
    """
    R = deepcopy(M)
    for i in range(128):
        R[i] ^= N[i]
    return R

def mul_mat128(M, N):
    """
        mul_mat128(): Multiply 2 128x128 matrices.
    """
    M = deepcopy(M)
    R = [gmpy2.mpz(0)] * 128
    for i_row in range(128):
        for i_col in range(128):
            if gmpy2.bit_test(M[i_row], 0):
                R[i_row] ^= N[i_col]
            M[i_row] >>= 1
    return R

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

if __name__ == '__main__':
    from matrixN import rand_matN, debug_matN, rref

    M = rand_matN(128)
    debug_matN(M, 128)

    N = rref(M, 128, 128)
    debug_matN(N, 128)

