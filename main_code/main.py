"""Module for main code."""
from icecream import ic

from main_code.optimisation_model import OptimisationModel

if __name__ == "__main__":
    optimisation_model = OptimisationModel()
    optimisation_model.solve()
    ic(optimisation_model.network.create_cost_table())
    optimisation_model.results()
