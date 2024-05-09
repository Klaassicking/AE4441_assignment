"""Module for storing the variables for the optimization model."""

from typing import Any

import networkx as nx


class ModelVariables:
    """Class to represent model variables for an acyclic network optimization problem."""

    def __init__(self, graph: nx.DiGraph) -> None:
        """Initialize the network model with a given acyclic network graph."""
        self.graph = graph
        self.nodes_refuel, self.nodes_not_refuel = self._classify_nodes()
        self.nodes = self.nodes_refuel | self.nodes_not_refuel
        self.arcs = set(graph.edges())
        self.cij = self._calculate_edge_costs()
        self.fij = self._extract_fuel_parameters()
        self.time_steps = self._set_time_periods()

    def _classify_nodes(self) -> tuple[set[Any], set[Any]]:
        """
        Classify nodes into refueling points (NF) and non-refueling points (NNF).

        Returns
        -------
        Tuple[Set[Any], Set[Any]]
            Tuple containing refueling point nodes (NF) and non-refueling point nodes (NNF).
        """
        nf = {node for node, attrs in self.graph.nodes(data=True) if attrs.get("refueling_point", False)}
        nnf = {node for node in self.graph.nodes() if node not in nf}
        return nf, nnf

    def _calculate_edge_costs(self) -> dict[tuple[Any, Any], float]:
        """
        Extract edge costs (cij) from the graph.

        Returns
        -------
        Dict[Tuple[Any, Any], float]
            Dictionary mapping each edge (u, v) to its cost.
        """
        return {(u, v): attrs["cost"] for u, v, attrs in self.graph.edges(data=True)}

    def _extract_fuel_parameters(self) -> dict[tuple[Any, Any], int]:
        """
        Extract fuel parameters (fij) from the graph.

        Returns
        -------
        Dict[Tuple[Any, Any], int]
            Dictionary mapping each edge (u, v) to its fuel parameter.
        """
        return {(u, v): attrs["fuel"] for u, v, attrs in self.graph.edges(data=True)}

    def _set_time_periods(self) -> range:
        """Set the time periods for the optimization model."""
        return range(1, len(self.nodes) + 1)
