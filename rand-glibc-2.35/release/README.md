# `randcrack/rand-glibc-2.35`: I know, you can just brute force the seed, it's 32-bit, what the hell do you think you're trying to prove bla bla...

But because I'm really a noob so I decided to do this the pure `Python` way **:)** *(even no `Z3` is in here)* *(maybe I'll put it in the future, but not now :333)* The script is not really efficient, so in some case it will not work...

Btw, the details for the algorithm is in [this link](https://www.mscs.dal.ca/~selinger/random). I've been checking *(locally)* with my computer, and it matches the pattern described in that link perfectly.

## Usages (if you still care :o)
It basically gives you 2 functions: `crack(outputs)` and `recover_seed(outputs)`:
- `crack(outputs)`: Recover fully as much as many states as possible. Take in a list `outputs` of `rand()` outputs, return `states` array which corresponds to the inner states of the random generator corresponding to the `outputs` array. You can put a `None` in the `outputs` array if you're not sure what the value is.

- `recover_seed(outputs)`: Do the same thing as above but return `seed` instead.