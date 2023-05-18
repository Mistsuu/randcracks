def self_recover(states):
    while True:
        isRecoverMore = False
        for i in range(31, len(states)):
            if states[i] != None:
                if states[i-31] == None and states[i-3] != None:
                    states[i-31] = (states[i] - states[i-3]) % 2**32
                    isRecoverMore = True

                if states[i-31] != None and states[i-3] == None:
                    states[i-3] = (states[i] - states[i-31]) % 2**32
                    isRecoverMore = True

        for i in range(len(states) - 31):
            if states[i] != None:
                if states[i+31] == None and states[i+28] != None:
                    states[i+31] = (states[i] + states[i+28]) % 2**32
                    isRecoverMore = True

                if states[i+31] != None and states[i+28] == None:
                    states[i+28] = (states[i+31] - states[i]) % 2**32
                    isRecoverMore = True

        for i in range(28, len(states) - 3):
            if states[i] != None:
                if states[i+3] == None and states[i-28] != None:
                    states[i+3] = (states[i] + states[i-28]) % 2**32
                    isRecoverMore = True

                if states[i+3] != None and states[i-28] == None:
                    states[i-28] = (states[i+3] - states[i]) % 2**32
                    isRecoverMore = True

        if not isRecoverMore:
            break

def crack(outputs):
    states = []

    i = 0
    for i in range(len(outputs)):
        output = outputs[i]
        outputs.append(output)
        if (i >= 31 and 
            output        != None and
            outputs[i-31] != None and 
            outputs[i-3]  != None and 
            output != (outputs[i-31] + outputs[i-3]) % (2**31)
        ):
            states[i-31] = (outputs[i-31] << 1) + 1
            states[i-3]  = (outputs[i-3]  << 1) + 1
            states.append((output << 1) + 0)
        else:
            states.append(None)
        i += 1

    # Apply recovery rule to itself
    # again and again to recover
    # the states.
    self_recover(states)

    return states

def recover_seed(outputs):
    states = crack(outputs)
    init_states = [None] * 344
    for i in range(343, 2, -1):
        if i + 31 >= 344: state_i_31 = states[i + 31 - 344]
        else:             state_i_31 = init_states[i + 31]
        if i + 28 >= 344: state_i_28 = states[i + 28 - 344]
        else:             state_i_28 = init_states[i + 28]
        if state_i_31 != None and state_i_28 != None:
            init_states[i] = (state_i_31 - state_i_28) % 2**32

    for i in range(2, -1, -1):
        init_states[i] = init_states[i+31]

    # Find one in init_states[:31] that is not None
    the_one_i = None
    for i in range(31):
        if init_states[i] != None:
            the_one_i = i

    # If we can find one, recover the first 31 values there!
    if the_one_i != None:
        for i in range(31):
            if init_states[i] == None:
                init_states[i] = (
                    pow(16807, i - the_one_i, 2147483647) * 
                    init_states[the_one_i] % 2147483647
                )

    # Recursively recover itself (if possible)
    states_that_has_that_rule = init_states[3:] + states
    self_recover(states_that_has_that_rule)
    all_states = init_states[:3] + states_that_has_that_rule

    for i in range(2, -1, -1):
        init_states[i] = init_states[i+31]

    # Sanity check. You can't get
    # here with probability 2^-28.
    # Oh probably if it has many Nones.
    assert all(s == None or s < 2147483647 for s in all_states[1:31])

    print(f'[i] Not recovered: {all_states.count(None)}/{len(all_states)}')
    if all_states[0] != None:
        return all_states[0]