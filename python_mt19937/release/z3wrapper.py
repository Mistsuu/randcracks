from z3 import *

def get_z3_answers(constraints: list, variables_list: list):
    sat_solver = Solver()
    for constraint in constraints:
        sat_solver.add(constraint)

    while sat_solver.check() == sat:
        answer = sat_solver.model()
        yield answer
        
        sat_solver.add( 
            Or(*[variable != answer[variable] for variable in variables_list]) 
        )

def get_z3_answer(constraints: list, variables_list: list):
    sat_solver = Solver()
    for constraint in constraints:
        sat_solver.add(constraint)

    if sat_solver.check() == sat:
        return sat_solver.model()
    return None