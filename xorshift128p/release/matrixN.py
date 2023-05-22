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

def find_pivot(row, ncols):
    for i_col in range(ncols):
        if gmpy2.bit_test(row, i_col):
            return i_col
    return -1

def rref(M, nrows, ncols):
    M = deepcopy(M)
    for i_row in range(nrows):
        # --- Step 1: Find row with pivot at lowest column index.
        min_pivot = ncols
        min_pivot_irow = -1
        for i_row2 in range(i_row, nrows):
            pivot = find_pivot(M[i_row2], min_pivot)
            if min_pivot > pivot and pivot != -1:
                min_pivot = pivot
                min_pivot_irow = i_row2     

        # If no row with pivot exists, 
        # that's mean RREF is done.
        if min_pivot_irow == -1:
            break

        # --- Step 2: Swap it with the top row
        tmp = M[min_pivot_irow]
        M[min_pivot_irow] = M[i_row]       
        M[i_row] = tmp

        # --- Step 3: Change every other row with the same pivot
        for i_row2 in range(nrows):
            if i_row2 != i_row and gmpy2.bit_test(M[i_row2], min_pivot):
                M[i_row2] ^= M[i_row]

    return M

def solve_right(M, v, nrows, ncols):
    """
        Solve vector `x` satisfying `M*x == v`.
    """
    R = deepcopy(M)
    v = deepcopy(v)

    # Create augmented matrix R = [M | v] 
    for i_row in range(nrows):
        if gmpy2.bit_test(v, i_row):
            R[i_row] = gmpy2.bit_set(R[i_row], ncols)

    # RRef the shit out of R
    R = rref(R, nrows, ncols+1)

    # Check if answer is actually solvable
    # if the system is over-determined?
    for i_row in range(ncols, nrows):
        if R[i_row] != 0:
            return None

    # Get answer.
    x = gmpy2.mpz(0)
    for row_R in R:
        pivot = find_pivot(row_R, ncols)
        if pivot == -1:
            break
        if gmpy2.bit_test(row_R, ncols):
            x = gmpy2.bit_set(x, pivot)
    return x

def transpose(M, nrows, ncols):
    R = [gmpy2.mpz(0) for i in range(ncols)]
    for i_row in range(nrows):
        for i_col in range(ncols):
            if gmpy2.bit_test(M[i_row], i_col):
                R[i_col] = gmpy2.bit_set(R[i_col], i_row)
    return R

def kernel_right(M, nrows, ncols):
    # Compute tranpose matrix M.T
    MT = transpose(M, nrows, ncols)

    # Augment it with an ncols x ncols identity matrix on the right
    for i_row in range(ncols):
        MT[i_row] = gmpy2.bit_set(MT[i_row], nrows + i_row)    

    # RREF it!
    MT = rref(MT, ncols, nrows)

    # Get the left side of the augmented matrix
    K = []
    for i_row in range(ncols):
        row_augR, row_augL = gmpy2.t_divmod_2exp(MT[i_row], nrows)
        if row_augL == 0 and row_augR != 0:
            K.append(row_augR)

    # Return unique
    return list(dict.fromkeys(K))