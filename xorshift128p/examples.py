import subprocess
import random

from cracker import RandomSolver

def test_int_outputs(CONST=27, N_SAMPLES=1024):
    WIDTH = len(str(CONST)) + 1
    LEN_PRERUN = random.randrange(0, 256)
    LEN_POSTRUN = 128

    exec_result = subprocess.run(
                ['/usr/bin/n', 'use', 'v26.4.0', '-e', 
                 f'for (let i = 0; i < {LEN_PRERUN}; ++i) Math.random();' +
                 f'for (let i = 0; i < {N_SAMPLES+LEN_POSTRUN}; ++i) console.log(Math.floor(Math.random() * {CONST}))' ],
                capture_output=True).stdout

    random_outputs = filter(lambda x: x, exec_result.split(b'\n'))
    random_outputs = list(map(int, random_outputs))
    actual_outputs = random_outputs[N_SAMPLES:]

    # A bias value of 13% is solvable by CU-BJMM.
    # You can try 17%, but it would be very very slow.
    solver = RandomSolver(max_relation_bias=0.10)
    for x in random_outputs[:N_SAMPLES]:
        solver.submit_random_mul_const(x, CONST)
    solver.solve(timeout=1)

    for i, answer in enumerate(solver.answers):
        guessed_outputs = [ int(answer.random() * CONST) for _ in range(LEN_POSTRUN) ]
        if guessed_outputs != actual_outputs:
            continue

        print()
        print(f'[i] Guessing new values (universe {i}):')
        print(f"{'x':>{WIDTH}} {'y':>{WIDTH}}")
        print("-" * (WIDTH*2+1))

        for j in range(LEN_POSTRUN):
            if guessed_outputs[j] != actual_outputs[j]:
                print('\033[31m', end='')
            else:
                print('\033[32m', end='')
            print(f"{guessed_outputs[j]:>{WIDTH}d} {actual_outputs[j]:>{WIDTH}d}\033[0m")

if __name__ == '__main__':
    test_int_outputs()

