from xorshift128p_crack import RandomSolver, RandomGenerator, RandomGeneratorVariant

def sumbit_random_test():
    randSolver = RandomSolver()
    randSolver.submit_random(0.15589505829365424)
    randSolver.submit_random(0.4551868164930428)
    randSolver.submit_random(0.16771727497700617)
    randSolver.submit_random(0.10685554388753915)
    randSolver.submit_random(0.4275409415243707)

    randSolver.solve()
    print(f'[i] {len(randSolver.answers)} potential solutions exists.')
    for answer in randSolver.answers:
        print(answer.random())
        print(answer.random())
        print('--------')

    """
    > Math.random()
    0.15589505829365424
    > Math.random()
    0.4551868164930428
    > Math.random()
    0.16771727497700617
    > Math.random()
    0.10685554388753915
    > Math.random()
    0.4275409415243707
    > Math.random()
    0.14465836581416336
    > Math.random()
    0.7161265607850553
    > Math.random()
    0.9930565861959089
    > Math.random()
    0.5910911402852297
    > Math.random()
    0.6067497666127513
    > Math.random()
    0.9498573537777268
    """

# Example using outputs from test/serial-gen14.js
def submit_random_mul_const_test():
    # ------ Generate for later validation.
    import math
    def generate_new_serial(random_fn):
        serial = ''
        for i in range(32):
            if i == 4 or i == 8 or i == 12 or i == 24:
                serial += '-'
            serial += hex(math.floor(random_fn() * 14))[2:]
        return serial

    # ------ List of outputs from script.
    old_serials = [
        "67a1-1d47-cb35-748ddc6ca763-0cb27a5d",
        "1b68-2917-0434-c4b7d09dc895-10197c33",
        "0a74-0653-dd09-dd19541666c1-9ca0bcbc",
        "5167-a8a6-d975-dab44159d1dc-a14a6d6c",
    ]
    new_serials = [
        "cb49-565d-9a9c-897c171bb8db-8481b44a",
        "1c5a-9973-8ac5-6967258a57c2-dc8ca105",
    ]

    # ------ Convert to list of output numbers
    def convert_serial_to_list_of_outputs(serial: str):
        serial = serial.replace('-', '')
        return list(map(lambda x: int(x, 16), serial))

    random_outputs = []
    for serial in old_serials:
        random_outputs.extend(
            convert_serial_to_list_of_outputs(serial)
        )

    randSolver = RandomSolver()
    for random_output in random_outputs:
        randSolver.submit_random_mul_const(random_output, 14)
    randSolver.solve()

    print(f'[i] {len(randSolver.answers)} potential solutions exists.')
    print(f' L predict next serial:', generate_new_serial(randSolver.answers[0].random))
    print(f' L predict next serial:', generate_new_serial(randSolver.answers[0].random))

#
# Example using outputs from `test/serial-gen.js`
# In this case, we have less outputs and therefore,
# multiple solutions may occur.
#
# RandomSolver.answers will contain either RandomGenerator
# or RandomGeneratorVariant objects.
#
def submit_random_mul_const_test_underdetermined_system():
    # ------ Generate for later validation.
    import math
    def generate_new_serial(random_fn):
        serial = ''
        for i in range(32):
            if i == 4 or i == 8 or i == 12 or i == 24:
                serial += '-'
            serial += hex(math.floor(random_fn() * 16))[2:]
        return serial

    # ------ List of outputs from script.
    old_serials = [
        "a61b-454f-7206-41f5127c90bd-b3919692",
    ]
    new_serials = [
        "1b41-e83d-91c9-e67d26711a35-dc72f582",
        "fe6d-e87e-ef9e-72f0b977fd66-e5433f8f",
        "9660-7735-5a60-f965eef335b0-170deba4",
        "db90-ff8e-18a7-a94ee6c84e02-5eb905a0",
        "8b92-196e-de9d-3af97a6cd316-4f74c655",
    ]

    # ------ Convert to list of output numbers
    def convert_serial_to_list_of_outputs(serial: str):
        serial = serial.replace('-', '')
        return list(map(lambda x: int(x, 16), serial))

    random_outputs = []
    for serial in old_serials:
        random_outputs.extend(
            convert_serial_to_list_of_outputs(serial)
        )

    randSolver = RandomSolver()
    for random_output in random_outputs:
        randSolver.submit_random_mul_const(random_output, 16)
    randSolver.solve()

    print(f'[i] {len(randSolver.answers)} potential solutions exists.')
    correct_answer = None
    for answer in randSolver.answers:
        # We run through all solutions to arrive
        # at the correct solution.
        next_serial = generate_new_serial(answer.random)
        if next_serial == new_serials[0]:
            correct_answer = answer

        # Of course, we can submit all,
        # But we're assuming that we only
        # know first output.
        if correct_answer != None:
            print(f'[i] Found an answer that matches the next serial!')
            break

    print(f' L predict next serial:', generate_new_serial(correct_answer.random))
    print(f' L predict next serial:', generate_new_serial(correct_answer.random))
    print(f' L predict next serial:', generate_new_serial(correct_answer.random))
    print(f' L predict next serial:', generate_new_serial(correct_answer.random))

if __name__ == '__main__':
    sumbit_random_test()
    # submit_random_mul_const_test()
    # submit_random_mul_const_test_underdetermined_system()