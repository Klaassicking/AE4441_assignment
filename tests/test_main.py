import pytest
from gurobipy import GRB
from main_code.optimisation_model import OptimisationModel

@pytest.fixture
def setup_optimisation_model():
    optimisation_model = OptimisationModel()
    optimisation_model.solve()
    optimisation_model.results()
    return optimisation_model

def test_optimal_solution_found(setup_optimisation_model):
    optimisation_model = setup_optimisation_model
    assert optimisation_model.model.status == GRB.Status.OPTIMAL, "Model did not find an optimal solution"

def test_constraint_1(setup_optimisation_model):
    optimisation_model = setup_optimisation_model
    for tau in optimisation_model.variables.time_steps:
        if tau == 1:
            assert sum(optimisation_model.X['s', j, tau].X for j in optimisation_model.variables.nodes if ('s', j) in optimisation_model.variables.arcs) == 1, "Constraint 1 not satisfied"
        else:
            assert sum(optimisation_model.X['s', j, tau].X for j in optimisation_model.variables.nodes if ('s', j) in optimisation_model.variables.arcs) == 0, "Constraint 1 not satisfied"

def test_constraint_2(setup_optimisation_model):
    optimisation_model = setup_optimisation_model
    for i in optimisation_model.variables.nodes - {'s', 't'}:
        for tau in optimisation_model.variables.time_steps[:-1]:
            in_flow = sum(optimisation_model.X[i, j, tau + 1].X for j in optimisation_model.variables.nodes if (i, j) in optimisation_model.variables.arcs)
            out_flow = sum(optimisation_model.X[j, i, tau].X for j in optimisation_model.variables.nodes if (j, i) in optimisation_model.variables.arcs)
            assert in_flow - out_flow == 0, "Constraint 2 not satisfied"

def test_constraint_3(setup_optimisation_model):
    optimisation_model = setup_optimisation_model
    assert sum(optimisation_model.X[i, 't', tau].X for i in optimisation_model.variables.nodes if (i, 't') in optimisation_model.variables.arcs for tau in optimisation_model.variables.time_steps) == 1, "Constraint 3 not satisfied"

def test_constraint_4(setup_optimisation_model):
    optimisation_model = setup_optimisation_model
    assert optimisation_model.F[1].X == optimisation_model.params.fuel_capacity, "Constraint 4 not satisfied"

def test_constraint_5(setup_optimisation_model):
    optimisation_model = setup_optimisation_model
    for tau in optimisation_model.variables.time_steps[1:]:
        fuel_level = optimisation_model.F[tau].X
        prev_fuel_level = optimisation_model.F[tau - 1].X
        fuel_consumption = sum(optimisation_model.variables.fij[i, j] * optimisation_model.X[i, j, tau - 1].X for i, j in optimisation_model.variables.arcs if j in optimisation_model.variables.nodes)
        refuel = sum(optimisation_model.params.fuel_capacity * optimisation_model.X[i, j, tau - 1].X for i, j in optimisation_model.variables.arcs if j in optimisation_model.variables.nodes_refuel)
        assert fuel_level <= prev_fuel_level - fuel_consumption + refuel, "Constraint 5 not satisfied"

def test_constraint_6(setup_optimisation_model):
    optimisation_model = setup_optimisation_model
    for tau in optimisation_model.variables.time_steps[1:]:
        assert optimisation_model.F[tau].X <= optimisation_model.params.fuel_capacity, "Constraint 6 not satisfied"

def test_constraint_7(setup_optimisation_model):
    optimisation_model = setup_optimisation_model
    for tau in optimisation_model.variables.time_steps:
        fuel_level = optimisation_model.F[tau].X
        fuel_consumption = sum(optimisation_model.variables.fij[i, j] * optimisation_model.X[i, j, tau].X for i, j in optimisation_model.variables.arcs)
        assert fuel_level - fuel_consumption >= 0, "Constraint 7 not satisfied"

def test_constraint_8(setup_optimisation_model):
    optimisation_model = setup_optimisation_model
    for (i, j, tau) in optimisation_model.X.keys():
        assert optimisation_model.X[i, j, tau].X in {0, 1}, "Constraint 8 not satisfied"

def test_triangle_inequality(setup_optimisation_model):
    optimisation_model = setup_optimisation_model
    for i in range(1, optimisation_model.params.network_size - 2):
        if (i, i + 2) in optimisation_model.variables.fij and (i, i + 1) in optimisation_model.variables.fij and (i + 1, i + 2) in optimisation_model.variables.fij:
            fuel_direct = optimisation_model.variables.fij[i, i + 2]
            fuel_via = optimisation_model.variables.fij[i, i + 1] + optimisation_model.variables.fij[i + 1, i + 2]
            assert fuel_direct <= fuel_via, f"Triangle inequality does not hold for nodes {i}, {i+1}, {i+2}"

    pytest.main()
