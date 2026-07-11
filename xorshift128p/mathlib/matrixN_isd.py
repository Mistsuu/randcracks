import subprocess
import tempfile
import gmpy2
import os

from .matrixN import (
    rref, rand_perm_matN, mul_matN, transpose, kernel_left_basis, debug_vecN,
    solve_right
)

def check_parameters(n, k, w, p, l, l1):
    if k > n:
        raise ValueError(f'{k = } > {n = }')
    if w > n:
        raise ValueError(f'{w = } > {n = }')
    if p > w:
        raise ValueError(f'{p = } > {w = }')
    if l1 > l:
        raise ValueError(f'{l1 = } > {l = }')
    if l > n - k:
        raise ValueError(f'{l = } > {n - k = }')

    kl2               = (k+l)+2
    mid               = kl2 // 2 + (n-k-l)
    hs_mid            = mid - (n-k-l)
    hs_left_start_idx = 0
    hs_left_end_idx   = hs_mid
    num_left_cols     = hs_left_end_idx - hs_left_start_idx
    size_l1           = num_left_cols * (num_left_cols - 1) // 2
    bucket_l1         = 2**(l-l1)
    num_l1            = size_l1 // bucket_l1
    if num_l1 == 0:
        raise ValueError(f'{num_l1 = }')

def find_e(H: list[gmpy2.mpz], s: gmpy2.mpz, n, k, w, p=8, l=16, l1=8, timeout:float=10):
    """
    Find e such that: He = s,
    where weight(e) <= w
    """
    check_parameters(n, k, w, p, l, l1)
    assert len(H) == n-k

    MASK = gmpy2.bit_mask(n-k)
    MASK_N = gmpy2.bit_mask(n)

    def generate_solve_matrices():
        for _ in range(1000):
            P = rand_perm_matN(n)
            HP = mul_matN(H, P)

            Hs = []
            for i_row in range(n-k):
                Hs_row = gmpy2.mpz(HP[i_row])
                if gmpy2.bit_test(s, i_row):
                    Hs_row = gmpy2.bit_set(Hs_row, n)
                Hs.append(Hs_row)

            Hs = rref(Hs, n-k, n+1)

            found = True
            for i_row, Hs_row in enumerate(Hs):
                if Hs_row & MASK != gmpy2.mpz(1<<i_row):
                    found = False
                    break

            if found:
                HH = []
                ss = gmpy2.mpz(0) 

                for i_row, Hs_row in enumerate(Hs):
                    HH.append(Hs_row & MASK_N)
                    if gmpy2.bit_test(Hs_row, n):
                        ss = gmpy2.bit_set(ss, i_row)

                return P, HP, HH, ss 

        return None, None, None, None

    P, HP, HH, ss = generate_solve_matrices()
    if P is None:
        raise ValueError("unsolvable ISD")

    def make_temp_challenge_file():
        ftemp = tempfile.NamedTemporaryFile()
        ftemp.write(b"# n\n")
        ftemp.write(f'{n}\n'.encode())
        ftemp.write(b"# k\n")
        ftemp.write(f'{k}\n'.encode())
        ftemp.write(b"# w\n")
        ftemp.write(f'{w}\n'.encode())
        ftemp.write(b"# H^T (H truncated last k columns)\n")
        for i_col in range(n-k, n):
            for i_row in range(n-k):
                if gmpy2.bit_test(HH[i_row], i_col):
                    ftemp.write(b'1')
                else:
                    ftemp.write(b'0')
            ftemp.write(b'\n')
        ftemp.write(b"# s^T\n")
        for i in range(n-k):
            if gmpy2.bit_test(ss, i):
                ftemp.write(b'1')
            else:
                ftemp.write(b'0')
        ftemp.write(b'\n')
        ftemp.flush()
        return ftemp

    CUR_DIR = os.path.dirname(__file__)
    BUILD_CACHE_FILE = os.path.join(CUR_DIR, "CU_BJMM/.build-cache")

    def solve_runner_is_built() -> bool:
        try:
            cache_file = open(BUILD_CACHE_FILE, "r")
            return cache_file.read() == f'{n},{k},{w},{p},{l},{l1}'
        except FileNotFoundError:
            return False

    def build_solve_runner():
        os.chdir(os.path.join(os.path.dirname(__file__), "CU_BJMM/cuBJMM+"))
        subprocess.run(['make', 'clean'], capture_output=True)

        make_arg0 = "EXTRA_FLAGS="
        make_arg0 +=  f"-DBJMM_N={n}"
        make_arg0 += f" -DBJMM_K={k}"
        make_arg0 += f" -DBJMM_W={w}"
        make_arg0 += f" -DBJMM_P={p}"
        make_arg0 += f" -DBJMM_L1={l1}"
        make_arg0 += f" -DBJMM_L2={l-l1}"
        make_arg0 += ""

        result = subprocess.run(['make', make_arg0], capture_output=True)
        os.chdir(os.path.dirname(__file__))

        try:
            cache_file = open(BUILD_CACHE_FILE, "w")
            cache_file.write(f'{n},{k},{w},{p},{l},{l1}')
            cache_file.flush()
            cache_file.close()
        except PermissionError:
            pass

        result.check_returncode()

    challenge_file = make_temp_challenge_file()

    if not solve_runner_is_built():
        build_solve_runner()

    try:
        result = subprocess.run(
            ['CU_BJMM/cuBJMM+/bjmm.out', challenge_file.name, '16'], 
            capture_output=True, 
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        result = None

    # input(f'Read the file at {challenge_file.name}')
    challenge_file.close()

    if not result or result.returncode != 0 or not result.stdout:
        return None

    e = list(map(gmpy2.mpz, result.stdout.strip().split(b' ')[-1].decode())) 
    Pe = mul_matN(P, e)
    Pe = transpose(Pe, n, 1)[0]

    return Pe

if __name__ == '__main__':
    from sage.all import random_matrix, GF, vector, shuffle
    from matrixN import debug_vecN

    n = 431
    k = 345
    w = 10
    H = random_matrix(GF(2), n-k, n)
    e = [1]*w + [0]*(n-w)
    shuffle(e)
    e = vector(GF(2), e)
    s = H*e
    print('e  =', ''.join(map(str, e)))

    Hgmpy2 = []
    for row in H:
        row = int(''.join(map(str, row))[::-1], 2)
        row = gmpy2.mpz(row)
        Hgmpy2.append(row)

    sgmpy2 = gmpy2.mpz(0)
    for i_col, col in enumerate(s):
        if col:
            sgmpy2 |= gmpy2.bit_set(gmpy2.mpz(0), i_col)

    Pe = find_e(Hgmpy2, sgmpy2, n, k, w, l=28, l1=16)
    print('e\' =', end=' ')
    debug_vecN(Pe, n)

def check_isd_solver_installed():
    CUR_DIR = os.path.dirname(__file__)
    ENV = os.environ
    ENV["CUR_DIR"] = CUR_DIR

    result = subprocess.run(
                [os.path.join(CUR_DIR, "check.sh")],
                env=ENV
             )
    result.check_returncode()


def approx_solve_right(
    M: list[gmpy2.mpz], v: gmpy2.mpz,
    nrows: int, ncols: int, 
    bias_list: list[float],
    **kwargs
):
    assert len(M) == len(bias_list), \
        ValueError(f"{len(M) = } != {len(bias_list) = }")

    # Can't solve this yet :)
    if nrows < ncols:
        return None

    check_isd_solver_installed()

    # error_rate = sum(bias_list) / len(bias_list) * 1.1
    error_rate = max(bias_list)

    H = kernel_left_basis(M, nrows, ncols)
    s = mul_matN(H, transpose([v], 1, nrows))
    s = transpose(s, len(H), 1)[0]
    w = int(nrows * error_rate)
    e = find_e(H, s, nrows, nrows - len(H), w, **kwargs)
    if e is None:
        return None

    return solve_right(M, v^e, nrows, ncols)

