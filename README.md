# `randcracks`: Tools to crack random functions.

# Introduction
This repository will provide tools to crack random algorithm. It is made **100%** for educational purposes only *(and fun **:>**)*. 

<p align="center">
  <img src="img/hello-world-using-random.png">
  <p align="center">
    <i>Hehe :'3 a seed cracker in Python~</i>
  </p>
</p>

# Branches
There should be two main branches, updated side-by-side: 
- `release`  
- `unstable_cython`. 
  
The latter uses Cython code to boost speed to some mathematical operations, making it x10 times faster than its Python counterpart on the former branch. But as the name suggests, it is very unstable and may not be able to run on some machines.

# I don't know how to name this section...
And while there're already many repos that can do this, I also want to create some more relaxed, while systematic way to crack random algorithms, instead of having to transform outputs everytime to suit the other programmer's code **:>** *(but I hope I don't complicated things too much...)*

Some algorithms will be solved using **Python**'s `Z3` module, the others might involve some maths on it... 

If there are some math included, I also want to involve `sagemath` as little as possible, because you probably won't want to install a `9GB` package when CTF's time is just ***10 minutes away*** from being closed and you're so close to a solution but you can't because the download time is too slow and you're really really sad like me last week... so in some of the functions you might see my ugly `Cython` code trying to implement matrix multiplication in `GF(2)`...

## Supported algorithms
1. `mt19937` from `Python`'s `random` module.
2. `xorshift128+` used by `Node.js`'s `Math.random()`.
3. `rand()` used by `glibc` (which is not fully supported).