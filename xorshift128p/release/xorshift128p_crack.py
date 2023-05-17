import gmpy2
import struct

from matrixN import (
    identity_matN, zero_matN, set_entry_matN, bitstring_to_vecN, 
    solve_right, kernel_right
)
from matrix64 import add_mat64, mul_mat64
from matrix128 import add_mat128, mul_mat128, combine_4_mat64

# Debug imports
from matrixN import debug_matN, debug_vecN

####################################################################
#                          DEFAULT GENERATOR
####################################################################

class RandomGenerator:
    def xs128p(self):
        s1 = self.state0 & 0xFFFFFFFFFFFFFFFF
        s0 = self.state1 & 0xFFFFFFFFFFFFFFFF
        s1 ^= (s1 << 23) & 0xFFFFFFFFFFFFFFFF
        s1 ^= (s1 >> 17) & 0xFFFFFFFFFFFFFFFF
        s1 ^= s0 & 0xFFFFFFFFFFFFFFFF
        s1 ^= (s0 >> 26) & 0xFFFFFFFFFFFFFFFF
        self.state0 = s0
        self.state1 = s1 & 0xFFFFFFFFFFFFFFFF
        generated = self.state0 & 0xFFFFFFFFFFFFFFFF
        return generated

    def toDouble(self, value):
        double_bits = (value >> 12) | 0x3FF0000000000000
        return struct.unpack('d', struct.pack('<Q', double_bits))[0] - 1 

    def __init__(self, state0: int, state1: int, forward_pos: int = 0) -> None:
        self.state0 = state0
        self.state1 = state1
        self.batch = []
        for _ in range(forward_pos):
            self.randomInt64()

    def randomInt64(self):
        if len(self.batch) == 0:
            for _ in range(64):
                self.batch.append(self.state0)
                self.xs128p()
        return self.batch.pop()

    def random(self):
        return self.toDouble(self.randomInt64())
    

####################################################################
#            FUNCTIONS IN XORSHIFT++128 MODELED AS MATRICES
####################################################################

#
# The idea is to craft a vector 
# in the following form:
#     [ state0 | state1 ] => S
# where each entry of vector is a bit
# of state0, state1. (2 64-bit values)
#
# By doing this, we can use matrix multiplication
# to influence the bits from state0 to state1,
# or/and state1 to state0.
#
# (at first, I thought to arrange them
# as 2 rows/cols of a matrix, but then I 
# realized that it is impossible to
# use matrix multiplication so that
# bit from state0 can change to state1.)
#
def vec_to_states(v):
    bitstring = f'{v:0128b}'[::-1]
    state0, state1 = bitstring[:64], bitstring[64:]
    state0, state1 = int(state0, 2), int(state1, 2)
    return state0, state1

#
# Get matrix M so that M * S creates
# new vector [ state0 | state1 ] that is
# similar to what xs128p() produces.
#
# (you can cache M btw :>, because
# this matrix does not depend on S.)
#
# You can divide this matrix to 4 sections:
# ┌──────────────────────┬──────────────────────┐
# │      state0 bits     │      state1 bits     │
# │       influence      │       influence      │
# │        itself        │        state0        │
# ├──────────────────────┼──────────────────────┤
# │      state0 bits     │      state1 bits     │
# │       influence      │       influence      │
# │        state1        │        itself        │
# └──────────────────────┴──────────────────────┘
#
#  (btw vector S is in vertical form 
#  incase you're confused)
#
def generate_mat_xorshift128():
    Z64 = zero_matN(64)
    I64 = identity_matN(64)

    # This is basically swap state0 with state1.
    # s1 = state0 & 0xFFFFFFFFFFFFFFFF
    # s0 = state1 & 0xFFFFFFFFFFFFFFFF
    M1 = combine_4_mat64(
        Z64, I64,
        I64, Z64
    )

    # s1 ^= (s1 << 23) & 0xFFFFFFFFFFFFFFFF
    # This is just a shift left matrix :>
    # To be able to represent shift and self-XOR 
    # operation, we add I64 to this matrix.
    L23 = zero_matN(64)
    for i in range(64-23):
        set_entry_matN(L23, i, i+23, 1)
    M2 = combine_4_mat64(
        I64, Z64,
        Z64, add_mat64(I64, L23)
    )

    # s1 ^= (s1 >> 17) & 0xFFFFFFFFFFFFFFFF
    R17 = zero_matN(64)
    for i in range(64-17):
        set_entry_matN(R17, i+17, i, 1)
    M3 = combine_4_mat64(
        I64, Z64,
        Z64, add_mat64(I64, R17)
    )

    # s1 ^= s0 & 0xFFFFFFFFFFFFFFFF
    # s1 ^= (s0 >> 26) & 0xFFFFFFFFFFFFFFFF
    R26 = zero_matN(64)
    for i in range(64-26):
        set_entry_matN(R26, i+26, i, 1)
    M4 = combine_4_mat64(
        I64,                 Z64,
        add_mat64(I64, R26), I64
    )

    # Just for faster notation
    x = mul_mat128
    return x(M4, x(M3, x(M2, M1)))

xorshift128_mat = generate_mat_xorshift128()

####################################################################
#                              SOLVER
####################################################################

class RandomGeneratorVariant:
    def __init__(self, w: gmpy2.mpz, K: list, forward_pos: int) -> None:
        self.w = w
        self.K = K
        self.cache = {}
        self.n_variants = pow(2, len(K))
        self.forward_pos = forward_pos

    def __getitem__(self, key: int) -> RandomGenerator:
        assert 0 <= key < self.n_variants, \
            ValueError(f"key should be in [0, {self.n_variants}) only.")
        
        if key not in self.cache:
            w = self.w
            K = self.K
            l = len(K)
            for ibit, bit in enumerate(f'{key:0{l}b}'):
                if bit == '1':
                    w ^= K[ibit]

            # Cache for later usages...
            state0, state1 = vec_to_states(w)
            self.cache[key] = RandomGenerator(
                                state0, state1, 
                                self.forward_pos
                              )
            
        return self.cache[key]
    
    def random(self):
        raise ValueError(f"This is not a RandomGenerator object. This is RandomGeneratorVariant, which generates variants of RandomGenerator based on the solutions of RandomSolver. To access a RandomGenerator object, use [] operator. The argument should be in the range of [0, {self.n_variants}).")

class RandomSolver:
    def __init__(self) -> None:
        self.M = xorshift128_mat
        self.T = identity_matN(128)

        # Keep track of known bits of the XORShift++128
        self.known_bits_stack = ''
        
        # Solve matrices for different start positions
        self.S           = [[]   for i in range(64)]
        self.current_pos = [63-i for i in range(64)]
        self.forward_pos = [i    for i in range(64)]
        self.answers     = None
        self.n_solutions = 0

        # Cache for every value of M^x
        self.cache_pow_M = []

    # ------------------------- some crazy inner stuffs  ----------------------
    #                  ( not really crazy, I just want to sleep )

    def update_cache_pow_M(self):
        for _ in range(64):
            self.cache_pow_M.append(self.T)
            self.T = mul_mat128(self.M, self.T)

    def get_M_pow_i(self, i):
        while i >= len(self.cache_pow_M):
            self.update_cache_pow_M()
        return self.cache_pow_M[i]
    
    def update_inner_states(self):
        for start_pos in range(64):
            if self.current_pos[start_pos] % 64 == 0:
                self.current_pos[start_pos] += 128
            self.current_pos[start_pos] -= 1
            self.forward_pos[start_pos] += 1
    
    # ------------------------ submit_xx() sub-functions -----------------------

    def submit_state_bits(self, state_partial_bits: str, ibit_l: int, ibit_r: int) -> None:
        """
            Submit bits of position [`ibit_l`, `ibit_r`] of the current state.
        """
        assert ibit_r - ibit_l + 1 <= 64 and 0 <= ibit_r < 64 and 0 <= ibit_l < 64, \
            ValueError("XORShift128++ only has 64-bit states!")
        assert ibit_r >= ibit_l, \
            ValueError(f"ibit_r ({ibit_r}) must be >= than ibit_l ({ibit_l})!")
        assert len(state_partial_bits) == ibit_r - ibit_l + 1, \
            ValueError(f"Sanity check: You must submit a bitstring of len={ibit_r - ibit_l + 1}!")

        self.known_bits_stack += state_partial_bits

        # Iterate through every possible start positions
        # to update the matrices in a corresponding way.
        for start_pos in range(64):
            T = self.get_M_pow_i(self.current_pos[start_pos])
            for ibit in range(ibit_l, ibit_r + 1):
                self.S[start_pos].append(T[ibit])

        self.update_inner_states()

    def submit_random(self, value: float) -> None:
        """
            Add result of `Math.random()`.
        """
        assert value >= 0 and value < 1, \
            ValueError("You must submit values in [0, 1)!")

        # You could use unpack() or some crazy stuffs, 
        # but this is probably enough.
        double_bits = f'{int(value * 2**52):052b}' 
        self.submit_state_bits(double_bits, 0, 51)

    def submit_random_mul_const(self, value: float, const: int) -> None:
        """
            Add result of `Math.random() * CONST | 0`.
            (not done yet...)
        """
        pass

    # ------------------------ skip_xx() sub-functions -----------------------
    #                      (although there's just skip_random())
    def skip_random(self):
        """
            Probably will be able to return "ticket"
            to a skipped value?
        """

        # Yeah... Just do nothing.
        self.update_inner_states()

    # --------------------------------  solve():  -------------------------------
    #                             retrieve state array 

    def solve(self, force_redo=False, debug=False) -> None:
        # If it's already solved, just don't care 
        # unless we tell them to :)
        if self.answers != None and not force_redo:
            return
        
        # This could happen during the fact that
        # submit_random_mul_const() sometimes will 
        # not add any bits to the array...
        assert len(self.known_bits_stack) > 0, \
            ValueError("Can't solve with an empty stomach man! Please call submit_xx() functions to give me something to gobble :)")
        
        # Find answer using some linear algrebra
        # magics.
        self.answers = []
        self.n_solutions = 0
        for start_pos in range(64):
            # Solve original state vectors
            v = bitstring_to_vecN(self.known_bits_stack)
            w = solve_right(
                self.S[start_pos], v,
                len(self.S[start_pos]), 128
            )
            K = kernel_right(
                self.S[start_pos],
                len(self.S[start_pos]), 128
            )

            # Update number of solutions
            if w != None:
                self.n_solutions += 2**len(K)

                # Create object holding potential
                # variants of the solutions
                # (not generate all of it in an array
                # because n_solutions scale with O(2^N))
                if len(K) > 0:
                    self.answers.append(
                        RandomGeneratorVariant(w, K, self.forward_pos[start_pos])
                    )
                else:
                    self.answers.append(
                        RandomGeneratorVariant(w, K, self.forward_pos[start_pos])[0]
                    )

        # Almost forgot to let user know
        # that the solution might not be possible...
        if self.n_solutions == 0:
            self.answers = None
            raise ValueError("Can't solve this shift!")