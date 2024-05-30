"""Module for main code."""
from icecream import ic

from main_code.optimisation_model import OptimisationModel
show_cost_table = True
show_network_graph = True


if __name__ == "__main__":
    optimisation_model = OptimisationModel()
    optimisation_model.solve()
    ic(optimisation_model.network.create_cost_table) if show_cost_table else None
    optimisation_model.results()
