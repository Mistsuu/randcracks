from gmpy2 cimport *
cdef extern from "gmp.h":
    void mpz_init (mpz_t x)
    void mpz_init_set (mpz_t rop, const mpz_t op)
    void mpz_init_set_ui (mpz_t rop, unsigned long int op)
    void mpz_xor (mpz_t rop, const mpz_t op1, const mpz_t op2)
    void mpz_clear (mpz_t x)
    int mpz_tstbit (const mpz_t op, unsigned long int bit_index)
import_gmpy2()   # needed to initialize the C-API

cdef _mpzs_to_GMPys(mpz_t[64] C_M):
    """
        Converts mpz_t -> gmpy2.mpz object    
    """
    M = [0] * 64
    for i in range(64):
        M[i] = GMPy_MPZ_From_mpz(C_M[i])
    return M

cdef _mpzs_clear(mpz_t[64] C_M):
    for i in range(64):
        mpz_clear(C_M[i])

def add_mat64(M, N):
    """
        add_mat64(): Adding 2 64x64 matrices.
    """
    cdef mpz_t C_R[64]
    for i in range(64):
        mpz_init(C_R[i])
        mpz_xor(
            C_R[i], 
            MPZ(M[i]), 
            MPZ(N[i])
        )
    R = _mpzs_to_GMPys(C_R)

    # Cleanup
    _mpzs_clear(C_R)

    # Return
    return R

def mul_mat64(M, N):
    """
        mul_mat64(): Multiply 2 64x64 matrices.
    """
    cdef mpz_t C_R[64]
    cdef mpz_t C_N[64]
    cdef mpz_t C_M_irow
    for i_row in range(64):
        C_N[i_row] = MPZ(N[i_row])

    for i_row in range(64):
        C_M_irow = MPZ(M[i_row])
        mpz_init_set_ui(C_R[i_row], 0)
        for i_col in range(64):
            if mpz_tstbit(C_M_irow, i_col):
                mpz_xor(
                    C_R[i_row], 
                    C_R[i_row], 
                    C_N[i_col]
                )
    R = _mpzs_to_GMPys(C_R)

    # Cleanup
    _mpzs_clear(C_R)

    # Return
    return R