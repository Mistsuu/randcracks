# `randcracks/xorshift128p`

Cracking the following pattern in modern V8 javascript engine.
```js
Math.floor(CONST * Math.random())
```

This project is based on the work of [v8_rand_buster](https://github.com/d0nutptr/v8_rand_buster) *(yes, I kinda copied the description from the original one too...)* However, instead of using `z3` module in `Python`, this one utilized the power of linear-algebra with matrices in `GF(2)` implemented in `gmpy2` combined with the speed of `Cython` to achieve a much, much faster runtime. The method is inspired by the `fastrology` challenge set I played in `plaidCTF` recently.

## Pros ✅ include:
- `< 1` **second** of solve time *(if you don't stuff too much (like 10000) inputs to the solver)*.
- Have some *(but a little bit cumbersome)* way to enumerate through different solutions.
- Can work better with a much smaller `CONST`.
- No `sagemath` required.

## Cons ❌ include:
- `Cython` code might not work on some machines because I still haven't learned anything new from last time. *Maybe I'll plan to add a `xorshift128p_python` branch using pure Python so that it could work on other?*

## Install

If you're in Ubuntu, run:
```
sudo apt-get install -y libmpc-dev
python3 -m pip install -r requirements.txt

# You can omit this and import 
# xorshift12p_crack directly to 
# compile Cython's files, however
# the script will exit after it
# finished compiling.
python3 init_cmatrix.py  
```

If you're currently on other distros, step `2+` is the same, but step 1, install `gmp` somehow you can **:3**