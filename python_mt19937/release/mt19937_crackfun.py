from mt19937_crack import RandomSolver
import random
import sys
sys.set_int_max_str_digits(0)

def counting_to_100_with_randrange():
    rndSolver = RandomSolver()
    for i in range(100):
        rndSolver.submit_randrange(i, 0, 100, random.randrange(0, 3))
    rndSolver.init_seed_states()
    rndSolver.solve()

    # Solving seed states before
    # solving seed values helps
    # finding seed faster.
    z3_seed_states  = rndSolver.get_seed_states()
    out_seed_states = rndSolver.get_skipped_variable_answer(z3_seed_states)
    rndSolver.solver_constrants.extend([
        z3_seed_state == out_seed_state for z3_seed_state, out_seed_state in zip(z3_seed_states, out_seed_states)
    ])

    rndSolver.init_seed_finder(624 * 32)
    rndSolver.solve(force_redo=True)
    print(f'seed = {rndSolver.get_seed()}')

def hello_world_with_randbytes():
    rndSolver = RandomSolver()
    rndSolver.submit_randbytes(b'Hello, world!')
    rndSolver.init_seed_states()
    rndSolver.solve()

    # Solving seed states before
    # solving seed values helps
    # finding seed faster.
    z3_seed_states  = rndSolver.get_seed_states()
    out_seed_states = rndSolver.get_skipped_variable_answer(z3_seed_states)
    rndSolver.solver_constrants.extend([
        z3_seed_state == out_seed_state for z3_seed_state, out_seed_state in zip(z3_seed_states, out_seed_states)
    ])

    rndSolver.init_seed_finder(624 * 32)
    rndSolver.solve(force_redo=True)
    print(f'seed = {rndSolver.get_seed()}')

if __name__ == '__main__':
    counting_to_100_with_randrange()
    # hello_world_with_randbytes()
    pass
