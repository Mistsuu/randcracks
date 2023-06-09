import random
from z3 import *
from z3wrapper import get_z3_answer

####################################################################
#            FUNCTIONS IN MERSENNE TWISTER MODELED IN Z3
####################################################################

# ----------------- functions used when update --------------------

w, n, m, r = 32, 624, 397, 31
a = 0x9908B0DF
f = 1812433253
def z3_sn(s_i, s_i1, s_m):
    s = (s_i & 0x80000000) | (s_i1 & 0x7fffffff)
    sA = LShR(s, 1)
    sA ^= a * (s_i1 & 1)
    return simplify(s_m ^ sA)

u, d = 11, 0xFFFFFFFF
s, b =  7, 0x9D2C5680
t, c = 15, 0xEFC60000
l    = 18
def z3_tamper(y):
    y = y ^ (LShR(y, u) & d)
    y = y ^ ((y << s) & b)
    y = y ^ ((y << t) & c)
    y = y ^ (LShR(y, l))
    return simplify(y)

# ----------------- functions used when initialize --------------------

def z3_init_genrand():
    z3_mt = [19650218] # hard-coded `seed` author picked. 
    for i in range(1, n):
        z3_mt.append((1812433253 * (z3_mt[-1] ^ (z3_mt[-1] >> 30)) + i) & 0xFFFFFFFF)
    for i in range(n):
        z3_mt[i] = BitVecVal(z3_mt[i], 32)
    return z3_mt

def z3_init_by_array(key_length: int):
    z3_mt       = z3_init_genrand()
    z3_init_key = [ BitVec(f'key_{i}', 32) for i in range(key_length) ] 
    i = 1
    j = 0
    for _ in range(max(n, key_length)):
        z3_mt[i] = (z3_mt[i] ^ ((z3_mt[i-1] ^ LShR(z3_mt[i-1], 30)) * 1664525))  \
                        + z3_init_key[j]                                         \
                        + j
        i += 1
        j += 1
        if i >= n:
            z3_mt[0] = z3_mt[n-1]
            i = 1
        if j >= key_length:
            j = 0

    for _ in range(n-1):
        z3_mt[i] = (z3_mt[i] ^ ((z3_mt[i-1] ^ LShR(z3_mt[i-1], 30)) * 1566083941)) \
                        - i
        i += 1
        if i >= n:
            z3_mt[0] = z3_mt[n-1]
            i = 1

    z3_mt[0] = BitVecVal(0x80000000, 32)
    for i in range(n):
        z3_mt[i] = simplify(z3_mt[i])
    return z3_mt, z3_init_key


####################################################################
#                              SOLVER
####################################################################
class RandomSolver():
    def __init__(self, machine_byteorder="little") -> None:
        assert machine_byteorder == "big" or machine_byteorder == "little", \
            ValueError("machine_byteorder option can only be \"big\" or \"little\".")

        self.solver_constrants = []
        self.key_variables = []
        self.variables = {}

        self.lindex = -1
        self.rindex = 0
        self.answer = None

        self.started_finding_seed = False
        self.machine_byteorder = machine_byteorder

    def init_seed_finder(self, seed_nbits: int) -> None:
        assert not self.started_finding_seed, \
            ValueError("Seed finding process is already started!")

        # The mt_init_states is actually just -n values to the left
        # of our current state values.
        key_length = (seed_nbits - 1) // 32 + 1
        if seed_nbits == 0:
            key_length = 1
        mt_init_states, self.key_variables = z3_init_by_array(key_length)
        
        # Generate n variables to the left
        z3_state_vars = list(self.gen_state_lvars(n))
        for i in range(n):
            self.solver_constrants.append(
                mt_init_states[i] == z3_state_vars[i]
            )

        # Don't start it again...
        self.started_finding_seed = True

    # =============================== SOLVERS ===============================

    def gen_state_lvars(self, n_vars: int):
        assert not self.started_finding_seed, \
            ValueError("Cannot add values to the left if the solver is already in the state of finding seed!")

        i = self.lindex
        for j in range(0, -n_vars, -1):
            self.variables[i+j] = BitVec(f'state_{i+j}', 32)
            self.lindex -= 1

            if (
                i+j+1 in self.variables and
                i+j+m in self.variables and
                i+j+n in self.variables
            ):
                self.solver_constrants.append(
                    z3_sn(
                        self.variables[i+j],
                        self.variables[i+j+1],
                        self.variables[i+j+m]
                    ) == self.variables[i+j+n]
                )

        for j in range(-n_vars + 1, 1):
            yield self.variables[i+j]

    def gen_state_rvars(self, n_vars: int):
        i = self.rindex
        for j in range(n_vars):
            self.variables[i+j] = BitVec(f'state_{i+j}', 32)
            self.rindex += 1

            if (
                i+j-n   in self.variables and
                i+j-n+1 in self.variables and
                i+j-n+m in self.variables
            ):
                self.solver_constrants.append(
                    z3_sn(
                        self.variables[i+j-n],
                        self.variables[i+j-n+1],
                        self.variables[i+j-n+m]
                    ) == self.variables[i+j]
                )

            # For user
            yield self.variables[i+j]

    # ------------------------ submit_xx() sub-functions -----------------------

    def submit_getrandbits32(self, value: int) -> None:
        """
            Submit an output of `value = random.getrandbits(32)` to the solver.
        """

        # Sanity check
        assert 0 <= value < 2**32, ValueError("You should submit a 32-bit value.")

        # Create variables
        z3_state_var, = list(self.gen_state_rvars(1))

        # Add constraints
        self.solver_constrants.extend([
            z3_tamper(z3_state_var) == value
        ])

    def submit_getrandbits(self, value: int, nbits: int) -> None:
        """
            Submit an output of `value = random.getrandbits(nbits)` to the solver.
        """

        # Sanity check
        assert 0 <= value < 2**nbits, ValueError(f"You should submit a {nbits}-bit value.")

        for remaining_bits in range(nbits, 0, -32):
            # Extracting 32-bits from lsb to msb
            lsb_value = value & 0xFFFFFFFF
            value >>= 32
            if remaining_bits >= 32:
                self.submit_getrandbits32(lsb_value)
                continue
            
            # Create variables -- for cases where bits < 32
            z3_state_var, = list(self.gen_state_rvars(1))

            # Add constraints
            self.solver_constrants.extend([
                LShR(z3_tamper(z3_state_var), 32 - remaining_bits) == lsb_value
            ])

    def submit_randbytes(self, value: bytes) -> None:
        """
            Submit an output of `value = random.randbytes(nbytes)` to the solver.
        """

        self.submit_getrandbits(
            int.from_bytes(value, 'little'), 
            len(value) * 8
        )

    def submit_random(self, value: float) -> None:
        """
            Submit an output of `value = random.random()` to the solver.
        """

        # Sanity check
        assert 0 <= value <= 1.0, ValueError("The output of random.random() limits to [0, 1) only.")

        # Get truncated outputs of random.getrandbits(32)
        tampered = int(value * 2**53)
        tampered0, tampered1 = tampered >> 26, tampered & ((1<<26) - 1)
        
        # Create variables
        z3_state_var0, z3_state_var1 = list(self.gen_state_rvars(2))

        # Add constraint
        self.solver_constrants.extend([
            LShR(z3_tamper(z3_state_var0), 5) == tampered0,
            LShR(z3_tamper(z3_state_var1), 6) == tampered1,
        ])

    def submit_randbelow(self, value: int, n: int, nskips: int = 0) -> list:
        """
            Submit an output of `value = random.random()` to the solver.

            If you're trying to accurately recover the states, you should use 
            this function only when you know exactly how many 
            `random.getrandbits()` are skipped, which can be specified in
            `nskips` option.
        """
        assert 0 <= value < n, ValueError(f"You should submit a value in range [0, {n})")
        k = n.bit_length()
        for _ in range(nskips):
            _, z3_output_var = self.skip_getrandbits(k)
            self.solver_constrants.append(
                UGE(z3_output_var, n) # same as z3_output_var >= n but for unsigned values.
            )
        self.submit_getrandbits(value, k)

    def submit_randrange(self, value: int, start: int, stop: int, nskips: int = 0) -> list:
        """
            Submit an output of `value = random.randrange(start, stop)` to the solver.

            If you're trying to accurately recover the states, you should use 
            this function only when you know exactly how many 
            `random.getrandbits()` are skipped, which can be specified in
            `nskips` option.
        """

        assert start <= value < stop, ValueError(f"You should submit a value in range [{start}, {stop})")
        self.submit_randbelow(
            value - start, 
            stop - start, 
            nskips = nskips
        )

    # ------------------------ skip_xx() sub-functions -----------------------
    #               in-case we missed some values in the middle :)
    #       (but only works if we know the exact number of missing values)
    #                   ( so please use it with care :> )
    #
    def skip_getrandbits32(self) -> list:
        """
            Skips a `random.getrandbits(32)` call in the process.

            Returns `[z3_state_var, z3_output_var]` where:
                - `z3_state_var` is a z3 variable that controls 
                   the state involved in this function.
                - `z3_output_var` is the z3 variable represents the output
                   of `random.getrandbits(32)`.

            The purpose is that we can apply further conditions
            onto `z3_state_var` or `z3_output_var`, or get a result
            from it after solved.
        """
        # Create variables for output
        z3_output_var = BitVec(f'value_getrandbits32_{self.rindex}', 32)
        
        # Create state variables
        z3_state_var, = list(self.gen_state_rvars(1))

        # Add constraints
        self.solver_constrants.append(
            z3_tamper(z3_state_var) == z3_output_var
        )

        return z3_state_var, z3_output_var

    def skip_getrandbits(self, nbits: int) -> list:
        """
            Skips a `random.getrandbits(nbits)` call in the process.

            Returns `[z3_state_vars, z3_output_var]` where:
                - `z3_state_vars` is a list of z3 variables that controls 
                   the state involved in this function.
                - `z3_output_var` is the z3 variable represents the output
                   of `random.getrandbits(nbits)`.

            The purpose is that we can apply further conditions
            onto `z3_state_vars` or `z3_output_var`, or get a result from it after
            solved.
        """
        # Create variables for output
        z3_output_var = BitVec(f'value_getrandbits{nbits}_{self.rindex}', nbits)
        
        # List of states variables
        z3_state_vars = []
        z3_output_pieces = []

        shift = 0
        for remaining_bits in range(nbits, 0, -32):
            # I'd want to reuse skip_getrandbits(32)
            # but it'll probably create some more
            # variables
            z3_state_var,           = list(self.gen_state_rvars(1))
            z3_output_getrandbits32 = z3_tamper(z3_state_var)
            if remaining_bits < 32:
                z3_output_getrandbits32 = (
                    Extract(
                        31,
                        32 - remaining_bits,
                        z3_output_getrandbits32
                    )
                )

            # Update
            shift += 32
            z3_state_vars.append(z3_state_var)
            z3_output_pieces.append(z3_output_getrandbits32)

        # Add constraints
        self.solver_constrants.append(
            z3_output_var == Concat(*z3_output_pieces[::-1])
                if len(z3_output_pieces) > 1
                else
            z3_output_var == z3_output_pieces[0]
        )

        return z3_state_vars, z3_output_var

    def skip_randbytes(self, nbytes: int) -> list:
        """
            Skips a `random.randbytes(nbytes)` call in the process.

            Returns `[z3_state_vars, z3_output_vars]` where:
                - `z3_state_vars` is a list of z3 variables that controls 
                   the state involved in this function.
                - `z3_output_vars` is the array of z3 variables representing
                   the result of `random.randbytes(nbytes)`, each variable 
                   in array represents an output byte.

            The purpose is that we can apply further conditions
            onto `z3_state_vars` or `z3_output_vars`, or get a result from it after
            solved.
        """
        # Create variables for output
        z3_output_vars = [BitVec(f'value_randbyte{i}_{self.rindex}', 8) for i in range(nbytes)]
        
        # Just reuse skip_getrandbits() 
        z3_state_vars, z3_output_getrandbits = self.skip_getrandbits(
            nbytes * 8
        )

        # Add constraints
        self.solver_constrants.append(
            Concat(*z3_output_vars[::-1]) == z3_output_getrandbits
                if len(z3_output_vars) > 1
                else 
            z3_output_vars[0] == z3_output_getrandbits
        )

        return z3_state_vars, z3_output_vars

    def skip_random(self) -> list:
        """
            Skips a `random.random()` call in the process.

            Returns `[z3_state_vars, z3_output_var]` where:
                - `z3_state_vars` is a list of z3 variables that controls 
                   the state involved in this function.
                - `z3_output_var` is the floating-point z3 variable representing
                   the output of `random.random()`.

            The purpose is that we can apply further conditions
            onto `z3_state_vars` or `z3_output_var`, or get a result 
            from it after solved.
        """
                
        # Create variables for output
        z3_out_bitvec = BitVec(f'value_random_bitvec_{self.rindex}', 64)
        z3_output_var = FP(f'value_random_float_{self.rindex}', Float64())

        # Create variables
        z3_state_var0, z3_state_var1 = list(self.gen_state_rvars(2))
        tampered0 = LShR(z3_tamper(z3_state_var0), 5)
        tampered1 = LShR(z3_tamper(z3_state_var1), 6)

        # Add constraint
        self.solver_constrants.extend([
            Extract(25, 0, tampered0) == Extract(51, 26, z3_out_bitvec), # first-half of mantissa
            Extract(25, 0, tampered1) == Extract(25, 0,  z3_out_bitvec), # last-half of mantissa
            Extract(63, 52, z3_out_bitvec) == 1022,                      # sign_bit = 0 | exponent = 2^(1022-1) = 2^(-1)
            If(Extract(26, 26, tampered0) == 1,
               fpBVToFP(z3_out_bitvec, Float64()),
               fpBVToFP(z3_out_bitvec, Float64()) - 0.5,
            ) == z3_output_var
        ])

        return [z3_state_var0, z3_state_var1], z3_output_var

    # --------------------------------  solve():  -------------------------------
    #                     retrieve state array / seed recovering 
        
    def solve(self, force_redo=False):
        # If it's already solved, just don't care 
        # unless we tell them to :)
        if self.answer != None and not force_redo:
            return

        # Get answer from Z3 :)
        self.answer = get_z3_answer(self.solver_constrants, [])
        assert self.answer, "Cannot untwist this twister!"
        
        # Get current state
        self.state = [self.answer[self.variables[self.rindex - i]].as_long() for i in range(n, 0, -1)]
        assert len(self.state) == n, "Not enough states are recovered!"

        # Advance n times
        for _ in range(n):
            self.advance()

    def get_seed(self):
        assert self.started_finding_seed, \
            ValueError("You need to initiate the seed finding process first.")

        # Attempt to solve if not solved
        if self.answer == None:
            self.solve()
        
        # Get key in it's unsigned-char form.
        key = b''
        for key_variable in self.key_variables:
            key += self.answer[key_variable].as_long().to_bytes(4, self.machine_byteorder)
        return int.from_bytes(key, 'little')
    
    def get_skipped_variable_answer(self, variable: BitVecRef | FPRef) -> int | float:
        # Attempt to solve if not solved
        if self.answer == None:
            self.solve()

        try:
            if type(variable) == BitVecRef:
                return self.answer[variable].as_long()
            elif type(variable) == FPRef:
                # It's always 64-bit value, so
                # we don't have to worry about
                # precision here.
                sign        = self.answer[variable].sign()
                significand = self.answer[variable].significand_as_long()
                exponent    = self.answer[variable].exponent_as_long()
                return (
                    (-1 if sign else 1) 
                            *
                    (significand / 2**52 + 1)
                            *
                    2**(exponent-1023)
                )
        except:
            raise ValueError("This variable does not exist in the constraint system!")
        
        raise ValueError(f"Not implemented for this type of variable ({type(variable)})")

    # =============================== GENERATE NEW VALUES ===============================

    def advance(self):
        if self.answer == None:
            self.solve()

        s = (self.state[0] & 0x80000000) | (self.state[1] & 0x7fffffff)
        sA = s >> 1
        if s & 0x1 == 0x1:
            sA ^= a

        sn = self.state[m] ^ sA
        self.state = self.state[1:] + [sn]

    def getrandbits32(self) -> int:
        if self.answer == None:
            self.solve()

        y = self.state[0]
        y = y ^ ((y >> u) & d)
        y = y ^ ((y << s) & b)
        y = y ^ ((y << t) & c)
        y = y ^ ((y >> l))
        self.advance()

        return y

    def getrandbits(self, nbits: int) -> int:
        shift = 0
        value = 0
        for remaining_bits in range(nbits, 0, -32):
            random32 = self.getrandbits32()
            if remaining_bits < 32:
                random32 >>= 32 - remaining_bits
            value |= random32 << shift
            shift += 32
        return value

    def randbytes(self, nbytes: int) -> bytes:
        return self.getrandbits(nbytes * 8).to_bytes(nbytes, 'little')

    def random(self) -> float:
        a = self.getrandbits32() >> 5
        b = self.getrandbits32() >> 6
        return ((a<<26) + b) / (2**53)

    def randbelow(self, n: int) -> int:
        # I just copied from the source
        if not n:
            return 0
        
        k = n.bit_length()       # don't use (n-1) here because n can be 1
        r = self.getrandbits(k)  # 0 <= r < 2**k
        while r >= n:
            r = self.getrandbits(k)
        return r
    
    def randrange(self, start: int, stop: int) -> int:
        return self.randbelow(stop - start) + start