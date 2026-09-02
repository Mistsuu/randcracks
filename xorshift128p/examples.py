import subprocess

from cracker import RandomSolver

LEN_PRERUN = 0 # random.randrange(0, 256)
LEN_POSTRUN = 512

def test_int_outputs(CONST=27, N_SAMPLES=786):
    WIDTH = len(str(CONST)) + 1

    exec_result = subprocess.run(
                ['/usr/bin/n', 'use', 'v10.20.1', '-e', 
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


def test_float_outputs(N_SAMPLES=15):
    exec_result = subprocess.run(
                ['/usr/bin/n', 'use', 'v10.20.1', '-e', 
                 f'for (let i = 0; i < {LEN_PRERUN}; ++i) Math.random();' +
                 f'for (let i = 0; i < {N_SAMPLES+LEN_POSTRUN}; ++i) console.log(Math.random())' ],
                capture_output=True).stdout

    random_outputs = filter(lambda x: x, exec_result.split(b'\n'))
    random_outputs = list(map(float, random_outputs))
    actual_outputs = random_outputs[N_SAMPLES:]

    solver = RandomSolver(max_relation_bias=0.07)
    for x in random_outputs[:N_SAMPLES]:
        solver.submit_random(x)
    solver.solve(timeout=1)

    for i, answer in enumerate(solver.answers):
        guessed_outputs = [ answer.random() for _ in range(LEN_POSTRUN) ]
        if guessed_outputs != actual_outputs:
            continue

        print()
        print(f'[i] Guessing new values (universe {i}):')
        print(f"{'x':>11} {'y':>11}")
        print("-" * 23)

        for j in range(LEN_POSTRUN):
            if guessed_outputs[j] != actual_outputs[j]:
                print('\033[31m', end='')
            else:
                print('\033[32m', end='')
            print(f"{guessed_outputs[j]:>1.9f} {actual_outputs[j]:>1.9f}\033[0m")

if __name__ == '__main__':
    test_int_outputs()
    # test_float_outputs()

