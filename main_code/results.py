"""Module to show the results of the optimisation model."""
import re

import networkx as nx
from gurobipy import GRB, Model
from icecream import ic
from matplotlib import pyplot as plt

from main_code.model_variables import ModelVariables
from main_code.network import AcyclicNetworkGenerator
from main_code.set_params import SetUpParameters


class ShowResults:
    """Class to show the results of the optimisation model."""

    def __init__(self, solved_model: Model, params: SetUpParameters, network: AcyclicNetworkGenerator, model_variables: ModelVariables) -> None:
        self.model = solved_model
        self.params = params
        self.network = network
        self.model_variables = model_variables
        self.nonzero_values = {var.VarName: var.X for var in self.model.getVars() if abs(var.X) != 0}
        self.x_var = [key for key in self.nonzero_values if key.startswith("x")]
        self.sorted_x_var = sorted(self.x_var, key=lambda x: int(x.split(",")[-1][:-1]))
        self.f_var = {key: value for key, value in self.nonzero_values.items() if key.startswith("F")}

    def show_results(self) -> None:
        """Print the results of the optimisation model."""
        if self.model.status == GRB.Status.OPTIMAL:
            ic("Optimal objective value:", self.model.objVal)
            ic("Optimal solution:")
            sorted_nonzero_values = dict(
                sorted(self.nonzero_values.items(), key=lambda item: int(item[0].split(",")[2][:-1]) if "," in item[0] else float("inf"))
            )
            for var_name, value in sorted_nonzero_values.items():
                ic(f"{var_name}: {value}")

    def _get_route(self) -> list:
        route = []
        for point in self.sorted_x_var:
            current = point.split("[")[1].split(",")[0]
            match = re.search(r"\d+", current)
            if match:
                route.append(int(match.group()))
            else:
                route.append(current)
        route.append(self.sorted_x_var[-1].split(",")[1].split(",")[0])
        return route

    def _get_route_data(self) -> dict:
        nodes = self._get_route()
        route_data = {}
        for i in range(len(nodes) - 1):
            route_data[i] = self.network.G.get_edge_data(nodes[i], nodes[i + 1])
        return route_data

    @property
    def _get_take_off_fuel_levels(self) -> list[float]:
        route = self._get_route()
        take_off_fuel = [0.0] * len(route)
        take_off_fuel[0] = self.params.fuel_capacity
        for node in range(1, len(route)):
            if route[node] in self.model_variables.nodes_refuel:
                take_off_fuel[node] = self.params.fuel_capacity
            else:
                take_off_fuel[node] = take_off_fuel[node - 1] - self.model_variables.fij[route[node - 1], route[node]]
        return take_off_fuel

    @property
    def _get_landings_fuel_levels(self) -> list[float]:
        route = self._get_route()
        landings_fuel = [0.0] * len(route)
        landings_fuel[0] = self.params.fuel_capacity
        take_off_fuel = self._get_take_off_fuel_levels
        for node in range(1, len(route)):
            landings_fuel[node] = take_off_fuel[node - 1] - self.model_variables.fij[route[node - 1], route[node]]

        return landings_fuel

    def plot_route_data(self) -> None:
        """Plot the optimal route data."""
        nodes = self._get_route()
        ic(self.model_variables.nodes_refuel)
        costs = [self.model_variables.cij[nodes[i], nodes[i + 1]] for i in range(len(nodes) - 1)]
        time_steps = [i + 1 for i in range(len(nodes))]
        route_graph = nx.DiGraph()
        route_graph.add_nodes_from(nodes)
        edges = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]
        route_graph.add_edges_from(edges)

        # Create edge labels dictionary
        edge_labels = {(nodes[i], nodes[i + 1]): costs[i] for i in range(len(nodes) - 1)}
        pos = {node: (index + 1, self._get_take_off_fuel_levels[index]) for index, node in enumerate(nodes)}
        y_values = [val for pair in zip(self._get_landings_fuel_levels, self._get_take_off_fuel_levels) for val in pair]
        x_values = [item for item in time_steps for _ in range(2)]
        fig, ax = plt.subplots(figsize=(21, 8))
        plt.plot(x_values, y_values, marker="o", linestyle="-", color="steelblue")

        nx.draw(
            route_graph,
            pos,
            with_labels=True,
            font_weight="bold",
            node_size=2000,
            node_color="lightblue",
            font_size=12,
            font_color="black",
            arrowsize=20,
            ax=ax,
        )

        nx.draw_networkx_edge_labels(G=route_graph, pos=pos, edge_labels=edge_labels, font_color="red")
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        plt.xlabel("Time Steps")
        plt.ylabel("Fuel Levels [pounds]")
        plt.title("Optimal Route")
        plt.show()
