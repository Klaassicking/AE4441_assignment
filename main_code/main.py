"""Module for main code."""
from gurobipy import Model
from icecream import ic

from main_code.network import AcyclicNetworkGenerator
from main_code.optimisation_model import OptimisationModel
from main_code.results import ShowResults
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
        self.optimisation_model: OptimisationModel = self.set_up_optimisation_model
        self.model_variables = self.optimisation_model.variables

    @property
    def create_network(self) -> AcyclicNetworkGenerator:
        """Create and return an acyclic network."""
        return AcyclicNetworkGenerator(params=self.params)

    @property
    def set_up_optimisation_model(self) -> OptimisationModel:
        """Set up the optimisation model."""
        return OptimisationModel(network=self.network, params=self.params)

    def visualise_network(self) -> None:
        """Visualise the acyclic network."""
        self.network.visualize_network()

    def show_cost_table(self) -> None:
        """Show the cost table."""
        cost_table = self.network.create_cost_table
        ic(cost_table)

    def solve_optimisation_model(self) -> Model:
        """Solve the optimisation model."""
        return self.optimisation_model.solve()

    def get_results(self) -> ShowResults:
        """Get the results of the optimisation model."""
        return ShowResults(
            solved_model=self.solve_optimisation_model(), params=self.params, network=self.network, model_variables=self.model_variables
        )


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
        results = main.get_results()
        results.show_results()
        results.plot_route_data()
