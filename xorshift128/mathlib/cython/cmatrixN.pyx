from gmpy2 cimport *
from libc.stdlib cimport malloc, free
cdef extern from "gmp.h":
    void mpz_init (mpz_t x)
    void mpz_init_set (mpz_t rop, const mpz_t op)
    void mpz_init_set_ui (mpz_t rop, unsigned long int op)
    void mpz_set_ui (mpz_t rop, unsigned long int op)
    void mpz_xor (mpz_t rop, const mpz_t op1, const mpz_t op2)
    void mpz_clear (mpz_t x)
    int mpz_tstbit (const mpz_t op, unsigned long int bit_index)
    void mpz_setbit (mpz_t rop, unsigned long int bit_index)
    size_t mpz_size (const mpz_t op)
    void mpz_swap (mpz_t rop1, mpz_t rop2)
    void mpz_fdiv_q_2exp (mpz_t q, const mpz_t n, unsigned long int b)
    void mpz_fdiv_r_2exp (mpz_t r, const mpz_t n, unsigned long int b)
import_gmpy2()   # needed to initialize the C-API

# =============================================================
#                          C's functions
# =============================================================

cdef _mpzs_to_GMPys(mpz_t* C_M, int C_nrows):
    """
        Converts mpz_t -> gmpy2.mpz object    
    """
    M = [0] * C_nrows
    for i in range(C_nrows):
        M[i] = GMPy_MPZ_From_mpz(C_M[i])
    return M

cdef void _mpzs_clear(mpz_t* C_M, int C_nrows):
    for i in range(C_nrows):
        mpz_clear(C_M[i])

cdef int _find_pivot(mpz_t row, int C_ncols):
    for i_col in range(C_ncols):
        if mpz_tstbit(row, i_col):
            return i_col
    return -1

cdef void _rref_inplace(mpz_t* C_M, int C_nrows, int C_ncols):
    cdef int min_pivot
    cdef int min_pivot_irow 
    for i_row in range(C_nrows):
        # --- Step 1: Find row with pivot at lowest column index.
        min_pivot = C_ncols
        min_pivot_irow = -1
        for i_row2 in range(i_row, C_nrows):
            pivot = _find_pivot(C_M[i_row2], min_pivot)
            if min_pivot > pivot and pivot != -1:
                min_pivot = pivot
                min_pivot_irow = i_row2     

        # If no row with pivot exists, 
        # that's mean RREF is done.
        if min_pivot_irow == -1:
            break

        # --- Step 2: Swap it with the top row
        mpz_swap(C_M[min_pivot_irow], C_M[i_row])

        # --- Step 3: Change every other row with the same pivot
        for i_row2 in range(C_nrows):
            if i_row2 != i_row and mpz_tstbit(C_M[i_row2], min_pivot):
                mpz_xor(C_M[i_row2], C_M[i_row2], C_M[i_row])

cdef void _transpose(mpz_t* C_M, mpz_t* C_R, int C_nrows, int C_ncols):
    """
        Compute R = M^T.
    """
    for i_row in range(C_nrows):
        for i_col in range(C_ncols):
            if mpz_tstbit(C_M[i_row], i_col):
                mpz_setbit(C_R[i_col], i_row)

# =============================================================
#                       Python's functions
# =============================================================

def find_pivot(row, ncols):
    for i_col in range(ncols):
        if mpz_tstbit(MPZ(row), i_col):
            return i_col
    return -1

def rref(M, nrows, ncols):
    cdef int C_nrows = nrows
    cdef int C_ncols = ncols
    cdef mpz_t* C_M = <mpz_t*> malloc(C_nrows * sizeof(mpz_t))
    if not C_M:
        return None
    for i_row in range(C_nrows):
        mpz_init_set(C_M[i_row], MPZ(M[i_row]))

    # I've already written a Cython function
    # so just reuse it :)
    _rref_inplace(C_M, C_nrows, C_ncols)
    M = _mpzs_to_GMPys(C_M, C_nrows)

    # Cleanup
    _mpzs_clear(C_M, C_nrows)
    free(C_M)

    # Return
    return M

def solve_right(M, v, nrows, ncols):
    """
        Solve vector `x` satisfying `M*x == v`.
    """
    cdef int C_nrows = nrows
    cdef int C_ncols = ncols
    cdef mpz_t  C_v
    cdef mpz_t* C_R = <mpz_t*> malloc(C_nrows * sizeof(mpz_t))
    if not C_R:
        return None
    for i_row in range(C_nrows):
        mpz_init_set(C_R[i_row], MPZ(M[i_row]))
    mpz_init_set(C_v, MPZ(v))

    # Create augmented matrix R = [M | v] 
    for i_row in range(C_nrows):
        if mpz_tstbit(C_v, i_row):
            mpz_setbit(C_R[i_row], C_ncols)

    # RRef the shit out of R
    _rref_inplace(C_R, C_nrows, C_ncols + 1)

    # Check if answer is actually solvable
    # if the system is over-determined?
    for i_row in range(C_ncols, C_nrows):
        if mpz_size(C_R[i_row]) != 0:
            # Cleanup
            _mpzs_clear(C_R, C_nrows)
            mpz_clear(C_v)
            free(C_R)

            # Return
            return None

    # Get answer.
    cdef mpz_t C_x
    mpz_init_set_ui(C_x, 0)
    for i_row in range(C_nrows):
        pivot = _find_pivot(C_R[i_row], C_ncols)
        if pivot == -1:
            break
        if mpz_tstbit(C_R[i_row], C_ncols):
            mpz_setbit(C_x, pivot)

    # Convert back to vector
    x = GMPy_MPZ_From_mpz(C_x)

    # Cleanup
    _mpzs_clear(C_R, C_nrows)
    mpz_clear(C_v)
    mpz_clear(C_x)
    free(C_R)
    
    # Return
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

def kernel_right_basis(M, nrows, ncols):
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