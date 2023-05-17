# `randcracks/xorshift128p`

Cracking the following pattern in modern V8 javascript engine.
```js
Math.floor(CONST * Math.random())
```

Based on the work of [v8_rand_buster](https://github.com/d0nutptr/v8_rand_buster) *(yes, I kinda copied the title of the original one too...)*. However, instead of using `z3` module in `Python`, this one utilized the power of linear-algebra implemented in `gmpy2` combined with the speed of `Cython` to achieve `< 1` second solve time!