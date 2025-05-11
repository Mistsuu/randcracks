from mt19937_crack import RandomSolver
import random
import sys
sys.set_int_max_str_digits(0)

def counting_to_100_with_randrange():
    rndSolver = RandomSolver()
    for i in range(100):
        rndSolver.submit_randrange(i, 0, 100, random.randrange(0, 3))
    rndSolver.init_seed_states()                    # Solving seed states before
    rndSolver.accumulate_solve()                    # solving seed values helps
    rndSolver.init_seed_finder(624 * 32)            # finding seed faster.
    rndSolver.solve(force_redo=True)
    print(f'seed = {rndSolver.get_seed()}')

def hello_world_with_randbytes():
    rndSolver = RandomSolver()
    rndSolver.submit_randbytes(b'Hello, world!')
    rndSolver.init_seed_states()                    # Solving seed states before
    rndSolver.accumulate_solve()                    # solving seed values helps
    rndSolver.init_seed_finder(624 * 32)            # finding seed faster.
    rndSolver.solve(force_redo=True)
    print(f'seed = {rndSolver.get_seed()}')

if __name__ == '__main__':
    counting_to_100_with_randrange()
    # hello_world_with_randbytes()
    pass
