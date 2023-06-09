from mt19937_crack import RandomSolver
import random

def counting_to_100_with_randrange():
    rndSolver = RandomSolver()
    for i in range(100):
        rndSolver.submit_randrange(i, 0, 100, random.randrange(0, 3))
    rndSolver.init_seed_finder(624 * 32)
    rndSolver.solve()
    print(f'seed = {rndSolver.get_seed()}')

def hello_world_with_randbytes():
    rndSolver = RandomSolver()
    rndSolver.submit_randbytes(b'Hello, world!')
    rndSolver.init_seed_finder(624 * 32)
    rndSolver.solve()
    print(f'seed = {rndSolver.get_seed()}')

if __name__ == '__main__':
    counting_to_100_with_randrange()
    # hello_world_with_randbytes()
    pass
