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
        if gmpy2.bit_test(row, 0):
            return i_col
        row >>= 1
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
        R[i_row] |= ((v & 0x1) << ncols)
        v >>= 1

    # RRef the shit out of R
    R = rref(R, nrows, ncols+1)

    # Check if answer is actually solvable
    # if the system is over-determined?
    for i_row in range(ncols, nrows):
        assert R[i_row] == 0, \
            ValueError("This equation cannot be solved!")

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
    cdef int C_nrows = nrows
    cdef int C_ncols = ncols

    cdef mpz_t* C_M = <mpz_t*> malloc(C_nrows * sizeof(mpz_t))
    cdef mpz_t* C_R = <mpz_t*> malloc(C_ncols * sizeof(mpz_t))
    for i_row in range(C_nrows):
        C_M[i_row] = MPZ(M)
    for i_row in range(C_ncols):
        mpz_init_set_ui(C_R[i_row], 0)

    for i_row in range(C_nrows):
        for i_col in range(C_ncols):
            if mpz_tstbit(C_M[i_row], i_col):
                mpz_setbit(C_R[i_col], i_row)
    R = _mpzs_to_GMPys(C_R, C_ncols)

    # Cleanup
    _mpzs_clear(C_R, C_ncols)
    free(C_M)
    free(C_R)
    
    # Return
    return R

def kernel_right(M, nrows, ncols):
    cdef int C_nrows = nrows
    cdef int C_ncols = ncols

    # Compute tranpose matrix M.T
    cdef mpz_t* C_M  = <mpz_t*> malloc(C_nrows * sizeof(mpz_t))
    cdef mpz_t* C_MT = <mpz_t*> malloc(C_ncols * sizeof(mpz_t))
    for i_row in range(C_nrows):
        C_M[i_row] = MPZ(M[i_row])
    for i_row in range(C_ncols):
        mpz_init_set_ui(C_MT[i_row], 0)
    _transpose(C_M, C_MT, C_nrows, C_ncols)

    # Augment it with an ncols x ncols identity matrix on the right
    for i_row in range(C_ncols):
        mpz_setbit(C_MT[i_row], C_nrows + i_row)    

    # RREF it!
    _rref_inplace(C_MT, C_ncols, C_nrows)

    # Get the left side of the augmented matrix
    cdef mpz_t row_augL 
    cdef mpz_t row_augR
    mpz_init(row_augL)
    mpz_init(row_augR)

    K = []
    for i_row in range(C_ncols):
        mpz_fdiv_r_2exp(row_augL, C_MT[i_row], C_nrows)
        mpz_fdiv_q_2exp(row_augR, C_MT[i_row], C_nrows)
        if mpz_size(row_augL) == 0 and mpz_size(row_augR) != 0:
            K.append(GMPy_MPZ_From_mpz(row_augR))

    # Cleanup
    mpz_clear(row_augL)
    mpz_clear(row_augR)
    _mpzs_clear(C_MT, C_ncols)
    free(C_M)
    free(C_MT)

    # Return unique
    return list(dict.fromkeys(K))

if __name__ == '__main__':
    M = rand_matN(128)
    debug_matN(M, 128)

    N = kernel_right(M, 128, 128)
    for i in range(len(N)):
        debug_vecN(N[i], 128)