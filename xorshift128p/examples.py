import subprocess

from cracker import RandomSolver

CONST = 3456
exec_result = subprocess.run(
            ['node', '-e', 
             'for (let i = 0; i < 512; ++i)   '
            f'    console.log(Math.floor(Math.random() * {CONST}))  ' ], 
            capture_output=True).stdout

random_outputs = filter(lambda x: x, exec_result.split(b'\n'))
random_outputs = list(map(int, random_outputs))

solver = RandomSolver()
for x in random_outputs[:196]:
    solver.submit_random_mul_const(x, CONST)
solver.solve(timeout=1)

for i, answer in enumerate(solver.answers):
    print()
    print(f'[i] Guessing new values (universe {i}):')
    print(f"{'x':>7} {'y':>7}")
    print("-" * 15)
    for j in range(64):
        print(f"{int(answer.random() * CONST):>7d} {random_outputs[196 + j]:>7d}")

