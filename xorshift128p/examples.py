import os

from cracker import RandomGenerator, RandomSolver

rng = RandomGenerator(
        int.from_bytes(os.urandom(8), 'big'),
        int.from_bytes(os.urandom(8), 'big'),
      )

solver = RandomSolver()

CONST = 65537 
for t in range(100):
    solver.submit_random_mul_const(int(rng.random() * CONST), CONST)

solver.solve(timeout=10)

# from mathlib.matrixN import debug_matN
# print(solver.known_bits_stack)
# debug_matN(list(map(lambda x: x.row, solver.S[0])), len(solver.S[0]), 128)

