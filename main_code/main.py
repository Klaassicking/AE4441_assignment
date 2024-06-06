"""Module for main code."""
from icecream import ic

from main_code.network import AcyclicNetworkGenerator
from main_code.optimisation_model import OptimisationModel
from main_code.set_params import SetUpParameters

# Global variables to control the display of cost table and network graph
show_cost_table = True
show_network_graph = True
solve = True


class Main:
    """Main class for the project."""

    def __init__(self) -> None:
        """Init method for the Main class."""
        # Initialize network parameters
        self.params: SetUpParameters = SetUpParameters()
        # Create the network
        self.network: AcyclicNetworkGenerator = self.create_network

    @property
    def create_network(self) -> AcyclicNetworkGenerator:
        """Create and return an acyclic network."""
        return AcyclicNetworkGenerator(params=self.params)

    def visualise_network(self) -> None:
        """Visualise the acyclic network."""
        self.network.visualize_network()

    def show_cost_table(self) -> None:
        """Show the cost table."""
        cost_table = self.network.create_cost_table
        ic(cost_table)

    def solve_optimisation_model(self) -> None:
        """Solve the optimisation model."""
        optimisation_model = OptimisationModel(network=self.network, params=self.params)
        optimisation_model.solve()
        optimisation_model.results()


if __name__ == "__main__":
    main = Main()
    # Show network graph if the flag is set
    if show_network_graph:
        main.visualise_network()
    # Show cost table if the flag is set
    if show_cost_table:
        main.show_cost_table()
    # Solve the optimisation model if the flag is set
    if solve:
        main.solve_optimisation_model()
