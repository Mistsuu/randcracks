import random
import os
from mt19937_crack import RandomSolver

def test_recover_seed():
    print("============================ RECOVER SEED TEST ============================")

    seed = random.getrandbits(624)
    random.seed(seed)

    # Solve for outputs
    randomSolver = RandomSolver()
    for _ in range(624):
        randomSolver.submit_randbytes(random.randbytes(5))
    randomSolver.init_seed_finder(int(seed).bit_length())
    randomSolver.solve()

    # Check with Python's outputs
    def format_output_test(label, guesser_output, lib_output):
        print(f"[i] {label}:")
        print(f" L--- Guess: {guesser_output}")
        print(f" L--- Lib's: {lib_output}")
        print()

    format_output_test("Seed prediction",           randomSolver.get_seed(),         seed)
    format_output_test("random.random()",           randomSolver.random(),           random.random())
    format_output_test("random.random()",           randomSolver.random(),           random.random())
    format_output_test("random.getrandbits(170)",   randomSolver.getrandbits(170),   random.getrandbits(170))
    format_output_test("random.random()",           randomSolver.random(),           random.random())
    format_output_test("random.getrandbits(123)",   randomSolver.getrandbits(123),   random.getrandbits(123))
    format_output_test("random.random()",           randomSolver.random(),           random.random())
    format_output_test("random.random()",           randomSolver.random(),           random.random())
    format_output_test("random.randbytes(1).hex()", randomSolver.randbytes(1).hex(), random.randbytes(1).hex())
    format_output_test("random.random()",           randomSolver.random(),           random.random())
    format_output_test("random.random()",           randomSolver.random(),           random.random())

def test_skipping_outputs():
    print("============================ SKIPPING OUTPUTS TEST ============================")

    skipInfos = []

    # Solve for outputs
    randomSolver = RandomSolver()
    for _ in range(624 * 2):
        randomSolver.submit_getrandbits32(random.getrandbits(32))

        # Choosing from another source :)
        random_choice = os.urandom(1)[0] % 20
        match random_choice:
            case 0:
                _, z3_val = randomSolver.skip_random()
                skipInfos.append({
                    "z3_val": z3_val,
                    "type": "random.random()",
                    "actual": random.random()
                })

            case 1:
                nbits = os.urandom(1)[0] % 128 + 1
                _, z3_val = randomSolver.skip_getrandbits(nbits)
                skipInfos.append({
                    "z3_val": z3_val,
                    "type": f"random.getrandbits({nbits})",
                    "actual": random.getrandbits(nbits)
                })

            case 2:
                nbytes = os.urandom(1)[0] % 15 + 1
                _, z3_val = randomSolver.skip_randbytes(nbytes)
                skipInfos.append({
                    "z3_val": z3_val,
                    "type": f"random.randbytes({nbytes})",
                    "actual": random.randbytes(nbytes)
                })

            case _:
                """ Doesn't skip :) """

    randomSolver.solve()

    # Check with Python's outputs
    def format_output_test(type, guesser_val, lib_output):
        if "random.random" in type:
            guesser_output = randomSolver.get_skipped_variable_answer(guesser_val)

        if "random.getrandbits" in type:
            guesser_output = randomSolver.get_skipped_variable_answer(guesser_val)

        if "random.randbytes" in type:
            guesser_output = bytes(
                [randomSolver.get_skipped_variable_answer(val) for val in guesser_val]
            ).hex()
            lib_output = lib_output.hex()

        print(f"[i] {type}:")
        print(f" L--- Guess: {guesser_output}")
        print(f" L--- Lib's: {lib_output}")
        print()

    for skipInfo in skipInfos:
        format_output_test(
            skipInfo["type"], 
            skipInfo["z3_val"],
            skipInfo["actual"],
        )

def test_shuffle():
    randomSolver = RandomSolver()
    for _ in range(624):
        randomSolver.submit_getrandbits32(random.getrandbits(32))

    for i in range(20):
        arr1 = list(range(20))
        arr2 = list(range(20))
        random.shuffle(arr1, random=random.random)
        randomSolver.shuffle(arr2, random=randomSolver.random)

        print(f'[i] Shuffle test {i}...')
        print(f' L arr1 = {arr1}')
        print(f' L arr2 = {arr2}')

def test_simple_solve():
    randomSolver = RandomSolver()
    randomSolver.submit_getrandbits(random.getrandbits(32 * 624), 32 * 624)
    randomSolver.solve()

    for i in range(200):
        assert randomSolver.getrandbits32() == random.getrandbits(32)

if __name__ == '__main__':
    # test_recover_seed()
    # test_skipping_outputs()
    # test_shuffle()
    test_simple_solve()
    pass