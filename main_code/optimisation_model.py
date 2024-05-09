"""Module for the optimisation model class."""

from gurobipy import GRB, Model, quicksum, tupledict

from main_code.model_variables import ModelVariables
from main_code.network import AcyclicNetworkGenerator
from main_code.set_params import NetworkParameters


class OptimisationModel:
    """Class to represent the optimisation model for refueling routing problem."""

    def __init__(self) -> None:
        self.model = Model()
        self.params = NetworkParameters()
        self.network = self._create_network
        self.variables = self._create_variables
        self.X, self.F = self._create_decision_variables

    @property
    def _create_network(self) -> AcyclicNetworkGenerator:
        return AcyclicNetworkGenerator(params=self.params)

    @property
    def _create_variables(self) -> ModelVariables:
        return ModelVariables(graph=self.network.G)

    @property
    def _create_decision_variables(self) -> tuple[tupledict, tupledict]:
        """
        Create decision variables 'x' and 'f' for the optimization model.

        Returns
        -------
        tuple[tupledict, tupledict]:
            Tuple containing decision variable 'x' (binary) and 'f' (continuous).
        """
        x = self.model.addVars(self.variables.arcs, self.variables.time_steps, vtype=GRB.BINARY, name="x")
        f = self.model.addVars(self.variables.time_steps, vtype=GRB.CONTINUOUS, name="F")
        return x, f

    def _create_constraint_1(self) -> None:
        for tau in self.variables.time_steps:
            self.model.addConstr(
                quicksum(self.X["s", j, tau] for j in self.variables.nodes if ("s", j) in self.variables.arcs) == 1
                if tau == 1
                else quicksum(self.X["s", j, tau] for j in self.variables.nodes if ("s", j) in self.variables.arcs) == 0,
                name="Start_node_s",
            )

    def _create_objective(self) -> None:
        cost = self.params.w1 * quicksum(
            self.variables.cij[i, j] * self.X[i, j, t] for (i, j) in self.variables.arcs for t in self.variables.time_steps
        )
        refueling_cost = self.params.w2 * quicksum(
            self.X[i, j, t] for (i, j) in self.variables.arcs if j in self.variables.nodes_refuel for t in self.variables.time_steps
        )
        self.model.setObjective(cost + refueling_cost, GRB.MINIMIZE)

    def solve(self) -> None:
        """Solve the optimisation model."""
        self._create_constraint_1()
        self._create_objective()
        self.model.optimize()


optimisation_model = OptimisationModel()
optimisation_model.solve()
