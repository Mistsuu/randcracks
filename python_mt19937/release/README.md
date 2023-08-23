# `randcracks/python_mt19937`: Cracking Python's `random` module with the power of Z3.

Cracking Python's `random` module with the power of **Z3**. **This code is heavily inspired from the project of https://github.com/tna0y/Python-random-module-cracker.** Tested with **Python 3.10**.

The script `mt19937_crack.py` provides you class `RandomSolver`, allowing you to feed directly outputs of `random.getrandbits(nbits)`, `random.randbytes(nbytes)`, and `random.random()` in order to: 

- Predict newer values.
- Recover the seed value.

## Usages

### How to use `RandomSolver`

```python
randomSolver = RandomSolver()

# ... all of the randomSolver.submit_xx(), randomSolver.skip_xx(), ... must go between here ...

randomSolver.solve()

# ... all of the randomSolver prediction outputs
```

Between the creation of a `RandomSolver` object and the call to `RandomSolver.solve()` are the calls to the:

- **feed functions:** Ones that starts with `submit_`.
- **skip functions:** Ones that starts with `skips_`.
- **seed-finding initialization function**: `init_seed_finder`.

After the `RandomSolver.solve()` call, we can predict newer values by calling functions that we normally call in `random`, like `RandomSolver.random()`, or `RandomSolver.getrandbits(nbits)`, etc, the list of which can be found in the **Predict newer values** section. You can also choose NOT to call `RandomSolver.solve()` and call those functions instead, and the cracker will be able to detect and figure out the inner states before churning out any new outputs.

You can feed new outputs even after solved, and call `RandomSolver.solve(force_redo=True)` to force the cracker to re-solve the inner states.

You may also specify the endianess of the machine you're trying to crack using `RandomSolver(machine_byteorder="big")` or `RandomSolver(machine_byteorder="little")`. However, this mechanism is not tested yet in big-endian, only derived through code observations, so errors may occurs.

### Feeding outputs of `random.xxx()`

Using `RandomSolver.submit_xxx()` function, where the `xxx` suffix corresponds to the function names in the `random` module, in which we have:

- `RandomSolver.submit_randbytes(self, value: bytes)`
- `RandomSolver.submit_random(self, value: float)`
- `RandomSolver.submit_getrandbits(self, value: int, nbits: int)`
- `RandomSolver.submit_randbelow(self, value: int, nskips: int = 0)`
- `RandomSolver.submit_randrange(self, value: int, start: int, stop: int, nskips: int = 0)`
- `RandomSolver.submit_bin_getrandbits(self, binvalue: str)`

Since some functions calls an unpredictable amount of `random.getrandbits(nbits)` at their core, an `nskips` option is put so that we can specify if we know for sure how many `getrandbits` it could have called.

```python
randomSolver.submit_randbytes(random.randbytes(5))

# -- or -- 
randomSolver.submit_getrandbits(
    random.getrandbits(17),
    17
)

# -- or -- 
randomSolver.submit_random(random.random())

# -- or -- 
# (uses ONLY when you know exactly how many 
# random.getrandbits() have been used)
randomSolver.submit_randrange(69, 0, 100, nskips=3)

# -- or --
# This function returns a BitVecRef so you can use
# randomSolver.get_skipped_variable_answer(z3_output_var)
# to find out the missing '?' bits.
z3_output_var = randomSolver.submit_bin_getrandbits('01?01?01??01?01')
```

`RandomSolver` has no restrictions on the number of values that you feed in this random cracker. However, it is important to notice that if you feed less than **624 32-bit integer values**, or some equivalent number of values in terms of **bytes** or **bits**, the solver's predicted random inner states might differ from that of the actual `random` module. In the future, I might develop a way that allows you to enumerate between different solutions, but for now, for whatever inputs you give in to the cracker, it will try to find the best solution it can.

### Predict newer values

After solve, we can use the following functions to predict newer values:

```python
value = randomSolver.random()

# -- or -- 
value = randomSolver.getrandbits(32)

# -- or --
value = randomSolver.randrange(0, 100) # no skip implementation is in here yet :<

# -- or --
value = randomSolver.randbytes(8)

# -- or --
array = list(range(10))
randomSolver.shuffle(array)

# -- or --
array = list(range(10))
randomSolver.choice(array)
```

### Seed recovery

Besides solving for the inner states, we can also find the seed that generates the outputs starting from the first one we submit. But to get it, we need to call `init_seed_finder()` before calling `solve()`. Then we can get the seed by calling `get_seed()` function that outputs an integer value having **(-32, +32)** bits to the specified number of bits.

```python
# Start seed finding process
randomSolver.init_seed_finder(32) # you can replace 32 for any number that is the number of bits in seed
randomSolver.solve()

# Get seed
seed = randomSolver.get_seed()
```

### Skip unknown outputs in the middle while submitting

In real world scenarios, we might don't have all of the outputs, or we may have a partial output. That's why the `skip_xx` functions are born.

Each `skip_xx` function returns an array containing `2` values of:
- `z3_state_var(s)`: **Z3** variable(s) representing the values in the state array involved in the generation of output value, which is represented as a **32-bit** `BitVec`.
- `z3_output_var(s)`: **Z3** variable(s) representing the output value of the function, which depends on the output of the function.

```python
# z3_output_var is a float64 Z3 variable.
z3_state_vars, z3_output_var = randomSolver.skip_random()

# z3_output_var is a Z3's nbits BitVec.
z3_state_vars, z3_output_var = randomSolver.skip_getrandbits(32)

# z3_output_vars is an array of nbytes Z3's 8bits BitVecs.
z3_state_vars, z3_output_vars = randomSolver.skip_randbytes(8)
```

The `RandomSolver` class has an attribute called `solver_constraints`, which is an array that contains all of the **Z3** constraints that allows you to solve the inner states. You can apply conditions to `z3_state_var(s)` and/or `z3_output_var(s)`, appending it to the `solver_constraints` array to create custom rules :)

```python
randomSolver.solver_constrants.append(
	z3_output_var >= 3
)
```

You can also use `RandomSolver.get_skipped_variable_answer` to obtain result of skipped values as well: 

```python
# For .skip_random(), .skip_getrandbits()
print(randomSolver.get_skipped_variable_answer(z3_output_var))

# For .skip_randbytes()
print(randomSolver.get_skipped_variable_answer(z3_output_vars[0])) # to get byte 0 - as int
print(randomSolver.get_skipped_variable_answer(z3_output_vars[1])) # to get byte 1 - as int
```

### More advanced uses

If you want to directly obtain the next inner state variables used for the next outputs, you can use:
```python
list(randomSolver.gen_state_rvars(nvars))
```
Since `gen_state_rvars` is a generator function, it is suggested to wrap it around a `list()`.

You don't have to worry about adding the default relationships between the inner states, as it is automatically detected and updated when you call this function. 

Each `gen_state_rvars(1)` call is equivalent to a `skip_getrandbits(32)`, without the `z3_output_var` return value.


## Examples

### Predict newer values given outputs of `random.random()`

A simple example that predicts newer values given **624 values** created by `random.random()`:

```python
randomSolver = RandomSolver()
for _ in range(624):
    randomSolver.submit_random(random.random())
randomSolver.solve()

# Predicts next random.random()s
assert randomSolver.random() == random.random()
assert randomSolver.random() == random.random()
assert randomSolver.random() == random.random()
```

### Counting with `random.randrange()`

You can also do some other wacky stuffs with this :) For example, finding the `seed` such that the first **100** values generated by `random.randrange(0, 100)` is just counting from **0** to **100**: *(in my laptop, the time taken to complete the code is around 4 minutes)*

```python
rndSolver = RandomSolver()
for i in range(100):
    rndSolver.submit_randrange(i, 0, 100, random.randrange(0, 3))
rndSolver.init_seed_finder(624 * 32)
rndSolver.solve()
print(f'seed = {rndSolver.get_seed()}')
```

### Hello, world using `random.randbytes()`

We can even say hello :)

```python
rndSolver = RandomSolver()
rndSolver.submit_randbytes(b'Hello, world!')
rndSolver.init_seed_finder(624 * 32)
rndSolver.solve()
print(f'seed = {rndSolver.get_seed()}')
```

