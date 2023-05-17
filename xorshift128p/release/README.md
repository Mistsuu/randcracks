# `randcracks/xorshift128p`

Cracking the following pattern in modern V8 javascript engine.
```js
Math.floor(CONST * Math.random())
```

This project is based on the work of [v8_rand_buster](https://github.com/d0nutptr/v8_rand_buster) *(yes, I kinda copied the description from the original one too...)* Also it's inspired by the `fastrology` set of challenges I played in `plaidCTF` recently.

However, instead of using `z3` module in `Python`, this one utilized the power of linear-algebra with matrices in `GF(2)` implemented in `gmpy2` combined with the speed of `Cython` to achieve a much, much faster runtime. 

## Pros ✅ include:
- `< 1` **second** of solve time.
- Have some *(but a little bit of cumbersome)* way to enumerate through different solutions.
- Can work better with a much smaller `CONST`.
- No `sagemath` required.

## Cons ❌ include:
- `Cython` code might not work on some machines because I still haven't learned anything new from last time. *Maybe I'll plan to add a `xorshift128p_python` branch using pure Python so that it could work on other?*