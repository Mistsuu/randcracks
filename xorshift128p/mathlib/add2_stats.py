"""
Modelling the probability of carrying at
i-th digit of a 2-term sum.


How it works:
If we model any multi-term addition as:
digit ^ digit ^ digit ^ ... ^ carry

where each digit in [0, 1]
and   each carry in [0, inf]

then we can compute the probability of
each carry.
 
(denote A[i] be the i-th binary digit of A)

If we want to check (x1 + x2 + ... + xn)[i] = x1[i] ^ x2[i] ^ ... ^ xn[i],
We can check if carry[i] is divisible by 2 (0, 2, 4, ...)
else, it's not :)

  332               <== carry
   111              <== digit
+  111              <== digit
   111              <== digit
   111              <== digit
--------
 11100

This script has been optimized to work with 2-term summation.
"""

def digit0_carry_probability() -> list[float]:
    return [float(1), float(0)]

def next_digit_carry_probability(
    curr_digit_carry_prob: list[float],
    current_digit: int | None = None
) -> tuple[float, float]:
    next_digit_carry_prob = [float(0), float(0)]

    for digits in ((0,0),(0,1),(1,0),(1,1)):
        sum_digits = sum(digits)
        for carry in (0,1):
            result = sum_digits + carry
            if current_digit is not None and result & 0x1 != current_digit:
                continue
            next_digit_carry_prob[result >> 1] += 0.25 * curr_digit_carry_prob[carry]

    # in conditional cases, the sum probability is not 1.
    sum_carry_prob = next_digit_carry_prob[0] + next_digit_carry_prob[1]
    return (
        next_digit_carry_prob[0] / sum_carry_prob,
        next_digit_carry_prob[1] / sum_carry_prob,
    )

def build_carry_probabilities(known_digits: list[int|None]) -> list[tuple[float,float]]:
    """
    Calculate the probability carry[i], bit-i of carry operand is 0/1
    for given input digits.
    
    :param known_digits: list of int and None, the binary digits of the result.
    :type known_digits: list[int|None]
    :return: The list of list[2] floats, where:\n
              - list[2][0] denotes probability where carry[i] = 0 and\n
              - list[2][1] denotes probability where carry[i] = 1.
    :rtype: list[tuple[float,float]]
    """

    prob_carry_i = digit0_carry_probability()
    prob_list = [prob_carry_i]

    for i in range(len(known_digits)):
        prob_carry_i = next_digit_carry_probability(prob_carry_i, known_digits[i])
        prob_list.append(prob_carry_i)

    return prob_list

if __name__ == "__main__":
    import sys
    from rich import print

    n_digits = int(sys.argv[1])
    pattern = eval(sys.argv[2])
    assert isinstance(pattern, str)

    known_digits = {}
    for i, b in enumerate(pattern):
        known_digits[len(pattern) - i - 1] = int(b) if b in '01' else None

    d = digit0_carry_probability()

    for i in range(n_digits):
        print(f'[i] {i = }, {d = }')
        print(f' --> P(carry[{i}] == 0) = {d[0]}')  # not carry
        print(f' --> P(carry[{i}] == 1) = {d[1]}')  # carry
        print()
        d = next_digit_carry_probability(d, known_digits.get(i, None))

