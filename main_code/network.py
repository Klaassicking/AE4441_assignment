"""Module for generating and manipulating acyclic networks."""

import random

import matplotlib.pyplot as plt
import networkx as nx
from icecream import ic
from prettytable import PrettyTable

from main_code.set_params import NetworkParameters


class AcyclicNetworkGenerator:
    """
    Class for generating and manipulating acyclic networks.

    Parameters
    ----------
        size (int): The size of the network.
        psi (float): A parameter used in edge cost calculation.
        u (int): Upper limit for fuel distribution.
        m (int): Refueling point interval.

    Attributes
    ----------
        G (nx.DiGraph): The generated acyclic network graph.
    """

    def __init__(self, params: NetworkParameters) -> None:
        """Init method for the AcyclicNetworkGenerator class."""
        self.params = params
        self.G: nx.DiGraph = self.generate_acyclic_network()

    def generate_acyclic_network(self) -> nx.DiGraph:
        """
        Generate an acyclic network graph based on specified parameters.

        Returns
        -------
            nx.DiGraph: The generated acyclic network graph.
        """
        network = nx.DiGraph()

        # Add nodes
        nodes = ["s", *range(1, self.params.network_size - 2), self.params.network_size - 2, "t"]
        network.add_nodes_from(nodes)

        # Add edges with rounded fuel parameters
        for i in range(self.params.network_size):
            if i % self.params.m == 0:
                network.nodes[nodes[i]]["refueling_point"] = True
            else:
                network.nodes[nodes[i]]["refueling_point"] = False
            for j in range(i + 1, self.params.network_size):
                if i == 0 or j == self.params.network_size - 1 or i < j:
                    k = j - i
                    fuel_param = self.generate_fuel_distribution(k)
                    cost_param = round(random.uniform(a=0.95, b=1.05) * self.params.psi * fuel_param)
                    network.add_edge(nodes[i], nodes[j], fuel=fuel_param, cost=cost_param)

        return network

    def generate_fuel_distribution(self, k: int) -> int:
        """
        Generate a random fuel distribution parameter for a given distance.

        Parameters
        ----------
        k : int
            The distance for which the fuel distribution is generated.

        Returns
        -------
        int
            The generated fuel distribution parameter.
        """
        if k < 1:
            msg = "k must be greater than or equal to 1"
            raise ValueError(msg)

        initial_fuel_consumption_rate = 0.9 * self.params.initial_upper_bound
        lower_bound = initial_fuel_consumption_rate
        upper_bound = initial_fuel_consumption_rate
        for _ in range(1, k):
            upper_bound = initial_fuel_consumption_rate + lower_bound
            lower_bound = 0.9 * upper_bound

        return round(random.uniform(lower_bound, upper_bound))

    def visualize_network(self) -> None:
        """Visualize the generated acyclic network graph."""
        pos = nx.spring_layout(self.G)
        edge_labels = {(u, v): f"{self.G[u][v]['cost']}\n {self.G[u][v]['fuel']}" for u, v in self.G.edges()}
        refueling_point_color_map = ["seagreen" if self.G.nodes[node].get("refueling_point", False) else "tomato" for node in self.G.nodes]
        nx.draw(self.G, pos, with_labels=True, font_weight="bold", node_size=700, node_color=refueling_point_color_map, font_size=8)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_color="powderblue", font_size=7)
        plt.show()

    def create_cost_table(self) -> PrettyTable:
        """
        Create a cost table representation of the acyclic network graph.

        Returns
        -------
            PrettyTable: The cost table representation.
        """
        nodes = list(self.G.nodes)
        cost_table = PrettyTable()

        node_table_names = [
            str(node) + " (Refueling point)" if attributes.get("refueling_point", False) else str(node)
            for node, attributes in self.G.nodes(data=True)
        ]

        cost_table.field_names = ["", *node_table_names]

        for node in nodes:
            row_data = [node]
            for successor in nodes:
                if self.G.has_edge(node, successor):
                    cost = self.G[node][successor]["cost"]
                    fuel = self.G[node][successor]["fuel"]
                    string = f"{cost}, {fuel}"
                    row_data.append(string)
                else:
                    row_data.append("-")

            cost_table.add_row(row_data)

        return cost_table


generator = AcyclicNetworkGenerator(params=NetworkParameters())
generator.visualize_network()
cost_table = generator.create_cost_table()
ic(cost_table)
