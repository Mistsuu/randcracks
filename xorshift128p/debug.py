
import os
import gmpy2

from cracker import RandomGenerator, RandomSolver

rng = RandomGenerator(
        seed0 := int.from_bytes(os.urandom(8), 'big'),
        seed1 := int.from_bytes(os.urandom(8), 'big'),
      )

solver = RandomSolver()

CONST = 65537 
for t in range(100):
    solver.submit_random_mul_const(int(rng.random() * CONST), CONST)

from cracker import bitstring_to_vecN, approx_solve_right
from mathlib.matrixN import kernel_left_basis, mul_matN, transpose, debug_vecN, debug_matN

start_pos = 0
S         = list(map(lambda x: x.row,  solver.S[start_pos]))
bias_list = list(map(lambda x: x.bias, solver.S[start_pos]))

# debug_matN(S, len(S), 128)

# Solve original state vector w
v = bitstring_to_vecN(solver.known_bits_stack)
w = seed0 | (seed1 << 64)
debug_vecN(w, 128)

r = mul_matN(S, transpose([gmpy2.mpz(w)], 1, 128))
assert len(r) == len(S)
r = transpose(r, len(S), 1)[0]
r ^= v
# debug_vecN(r, len(S))

# Building inner of approx
H = kernel_left_basis(S, len(S), 128)
s = mul_matN(H, transpose([v], 1, len(S)))
s = transpose(s, len(H), 1)[0]

w = approx_solve_right(
    S, v,
    len(S), 128, 
    bias_list, 
    p=8, timeout=30,
)
debug_vecN(w, 128)

# solver.solve(timeout=1, p=3)

# debug_matN(list(map(lambda x: x.row, solver.S[0])), len(solver.S[0]), 128)

