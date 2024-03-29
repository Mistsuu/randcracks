# `randcracks/xorshift128p`

Cracking the following pattern in modern V8 javascript engine.
```js
Math.floor(CONST * Math.random())
```

This project is based on the work of [v8_rand_buster](https://github.com/d0nutptr/v8_rand_buster) *(yes, I kinda copied the description from the original one too...)* However, instead of using `z3` module in `Python`, this one utilized the power of linear-algebra with matrices in `GF(2)` implemented in `gmpy2` combined with the speed of `Cython` to achieve a much, much faster runtime. The method is inspired by the `fastrology` challenge set I played in `plaidCTF` recently.

## Pros ✅ include:
- Have some *(but a little bit cumbersome)* way to enumerate through different solutions.
- Can work better with a much smaller `CONST`.
- No `sagemath` required.
- No crazy `Cython` install stuffs.

## Cons ❌ include:
- Slower 10x than it's `unstable_cython` counterpart. A full recovery with enough inputs should take you around 10 seconds to solve.
  
## Install

If you're in Ubuntu, just run:
```bash
python3 -m pip install -r requirements.txt
```

## Usages

### Object creation
First, you create the `RandomSolver()` object.
```py
randSolver = RandomSolver()
```

### Submit/Skip outputs
Afterwards, you can feed different types of outputs to the solver. This includes two types of outputs:
1. `Math.random()` by using:
```py
randSolver.submit_random(x) 
```

2. `Math.floor(CONST * Math.random())` where `CONST` is an integer in the range `[2, 2**52]` by using:
```py
randSolver.submit_random_mul_const(x, CONST)
```

You can also skip an output if you don't know what's the value is:
```py
randSolver.skip_random()
```

### Solve
Then, you just need to call:
```py
randSolver.solve()
```

to get the result. When you're finished, you can access `randSolver.answers` to get `RandomGenerator` objects. *(if your inputs are not enough, there might be multiple solutions)*

Those objects are created during accessing the `[]` operator of the `randSolver.answers` object, so no need to worry about memory usages too much. You can use `len(randSolver.answers)` to get the total numbers of possible `RandomGenerator` objects given your inputs to the solver.

### Generate new outputs
You can do it by using the returned `RandomGenerator` object:

```py
# Get the number of solutions
print(f'[i] There are {len(randSolver.answers)} potential solutions.')

generator = randSolver.answers[0]
print(generator.random())       # Simulates the next Math.random() outputs
print(generator.random())       
print(generator.random())
print(generator.random())
print(generator.random())
```

You can also iterate through the `randSolver.answers` object like this:
```py
for answer in randSolver.answers:
    print(answer.random())
```

### Examples
You can find some of the examples from `xorshift128p_examples.py` file.