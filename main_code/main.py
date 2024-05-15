"""Module for main code."""
from icecream import ic
from main_code.network import AcyclicNetworkGenerator
from main_code.optimisation_model import OptimisationModel
from main_code.set_params import NetworkParameters

create_figure = True

if __name__ == "__main__":
    optimisation_model = OptimisationModel()
    optimisation_model.solve()
    ic(optimisation_model.network.create_cost_table)
    optimisation_model.results()

    if create_figure:
        network_params = NetworkParameters()
        network = AcyclicNetworkGenerator(params=network_params)
        network.visualize_network()