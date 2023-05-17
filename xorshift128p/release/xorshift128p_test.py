from xorshift128p_crack import RandomSolver

if __name__ == '__main__':
    randSolver = RandomSolver()
    randSolver.submit_random(0.15589505829365424)
    randSolver.submit_random(0.4551868164930428)
    randSolver.submit_random(0.16771727497700617)
    randSolver.submit_random(0.10685554388753915)
    randSolver.submit_random(0.4275409415243707)

    randSolver.solve()
    print(f'[i] {randSolver.n_solutions} potential solutions exists.')
    for i in range(randSolver.n_solutions):
        JSRand = randSolver.answers[i]
        print(JSRand.random())
        print(JSRand.random())
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