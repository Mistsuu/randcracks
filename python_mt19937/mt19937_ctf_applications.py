import random
import gmpy2
import os
import mt19937_crack
import z3

def test_recover_random_primes():
    """
        Create a weird scenerio where, 
        you have a 50% chance of getting
        an array of [p, q] or [p * q].

        Idea taken from MetaCTF. Challenge name:
        Hide And Seek The Flag.
    """

    # ======================== SERVER ========================
    print(f'[i] Generate values from server...')
    values = []
    for _ in range(50):
        p = int(gmpy2.next_prime(random.getrandbits(1024)))
        q = int(gmpy2.next_prime(random.getrandbits(1024)))
        n = p * q

        # Just so that we're not interfere
        # with the random.
        if os.urandom(1)[0] >> 7 == 1:
            values.append(
                p.to_bytes(128, 'big') + 
                q.to_bytes(128, 'big')
            )
        else:
            values.append(
                n.to_bytes(256, 'big')
            )

    # ======================== CLIENT ========================
    print(f'[i] Solving values from client...')
    rndSolver = mt19937_crack.RandomSolver()
    for i in range(50):
        p = int.from_bytes(values[i][:128], 'big')
        q = int.from_bytes(values[i][128:], 'big')

        if gmpy2.is_prime(p) and gmpy2.is_prime(q):
            # Statistically, next_prime only changes at most
            # the last 32 bits, so we can only obtain the 
            # first 1024 - 32 bits
            z3_near_p = rndSolver.submit_bin_getrandbits(f'{p:01024b}'[:-32] + '?'*32)
            z3_near_q = rndSolver.submit_bin_getrandbits(f'{q:01024b}'[:-32] + '?'*32)
        else:
            # If p & q are not primes, we just skip
            _, z3_near_p = rndSolver.skip_getrandbits(1024)
            _, z3_near_q = rndSolver.skip_getrandbits(1024)

    rndSolver.solve()

    # Verify we've solve it correctly
    # by predicting newer outputs
    print(f'new_guess = {rndSolver.random()}, actual = {random.random()}')
    print(f'new_guess = {rndSolver.random()}, actual = {random.random()}')
    print(f'new_guess = {rndSolver.random()}, actual = {random.random()}')
    print(f'new_guess = {rndSolver.random()}, actual = {random.random()}')

if __name__ == '__main__':
    test_recover_random_primes()
    pass