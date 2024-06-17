import numpy as np
from gurobipy import GRB
from icecream import ic


class ShowResults:
    def __init__(self, solved_model):
        self.model = solved_model
        self.nonzero_values = {var.VarName: var.X for var in self.model.getVars() if abs(var.X) != 0}
        self.x_var = [key for key in self.nonzero_values.keys() if key.startswith('x')]
        self.sorted_x_var = sorted(self.x_var, key=lambda x: int(x.split(',')[-1][:-1]))
        self.f_var = {key: value for key, value in self.nonzero_values.items() if key.startswith('F')}

    def show_results(self):
        """Print the results of the optimisation model."""
        if self.model.status == GRB.Status.OPTIMAL:
            ic("Optimal objective value:", self.model.objVal)
            ic("Optimal solution:")
            sorted_nonzero_values = dict(
                sorted(self.nonzero_values.items(), key=lambda item: int(item[0].split(",")[2][:-1]) if "," in item[0] else float("inf"))
            )
            for var_name, value in sorted_nonzero_values.items():
                ic(f"{var_name}: {value}")

    def get_route(self):
        route = []

        for name in self.sorted_x_var:
            components = [component.strip() for component in name[2:name.rfind(')')].split(',')]
            for component in components:
                try:
                    component = int(component)
                except ValueError:
                    component = str(component)
                if component not in route:
                    route.append(component)

        return route

# Example usage
# solved_model = <your_solved_model>
# Fmax = <maximum_fuel_capacity>
# fij = <fuel_consumption_matrix>
# NF = <nodes_with_fuel_stations>
# results = ShowResults(solved_model, Fmax, fij, NF)
# route, fuel, fuel_com, time_steps = results.get_route()
