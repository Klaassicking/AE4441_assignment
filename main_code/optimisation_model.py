"""Module for the optimisation model class."""

from gurobipy import GRB, Model, quicksum, tupledict
from icecream import ic

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

    # <editor-fold desc="Path finding constraints">
    def _create_constraint_1(self) -> None:
        """Create constraint ensuring exactly one starting node 's' at time step 1, and no starting nodes 's' at other time steps."""
        for tau in self.variables.time_steps:
            self.model.addConstr(
                quicksum(self.X["s", j, tau] for j in self.variables.nodes if ("s", j) in self.variables.arcs) == 1
                if tau == 1
                else quicksum(self.X["s", j, tau] for j in self.variables.nodes if ("s", j) in self.variables.arcs) == 0,
                name="Start_node_s",
            )

    def _create_constraint_2(self) -> None:
        """
        Create constraints ensuring incoming flow equals outgoing flow for intermediate nodes 'i'.

        This method iterates over each intermediate node 'i' (excluding 's' and 't') and for each time step 'tau'
        up to the second-to-last time step, it adds a constraint that ensures the incoming flow to node 'i'
        in the next time step (tau + 1) equals the outgoing flow from node 'i' in the current time step (tau).
        """
        for i in self.variables.nodes - {"s", "t"}:
            for tau in self.variables.time_steps[:-1]:
                self.model.addConstr(
                    quicksum(self.X[i, j, tau + 1] for j in self.variables.nodes if (i, j) in self.variables.arcs)
                    - quicksum(self.X[j, i, tau] for j in self.variables.nodes if (j, i) in self.variables.arcs)
                    == 0,
                    name="Incoming=outgoing",
                )

    def _create_constraint_3(self) -> None:
        """
        Create a constraint ensuring that there is exactly one path reaching the goal node 't'.

        This method adds a constraint that sums up the flow variables self.X[i, 't', tau] for each node 'i'
        (excluding 't') and each time step 'tau' where an arc (i, 't') exists in the network.
        """
        self.model.addConstr(
            quicksum(
                self.X[i, "t", tau] for i in (self.variables.nodes - {"t"}) for tau in self.variables.time_steps if (i, "t") in self.variables.arcs
            )
            == 1,
            name="goal_node_t",
        )

    # </editor-fold>

    # <editor-fold desc="Refueling constraints">
    def _create_constraint_4(self) -> None:
        """
        Create a constraint setting the initial fuel level to the specified fuel capacity.

        This method adds a constraint that sets the initial fuel level (`self.F[1]`) to the specified fuel capacity
        (`self.params.fuel_capacity`), ensuring that the optimization model starts with a predefined fuel amount.
        """
        self.model.addConstr(self.F[1] == self.params.fuel_capacity, name="InitialFuel")

    def _create_constraint_5(self) -> None:
        """
        Create a constraint modeling the evolution of fuel levels over consecutive time steps.

        This method adds constraints that model the evolution of fuel levels (`self.F[tau]`) over consecutive
        time steps (`tau`) in the optimization model.
        """
        for tau in self.variables.time_steps[1:]:
            self.model.addConstr(
                self.F[tau]
                <= self.F[tau - 1]
                - quicksum(self.variables.fij[i, j] * self.X[i, j, tau - 1] for i, j in self.variables.arcs if j in self.variables.nodes)
                + quicksum(self.params.fuel_capacity * self.X[i, j, tau - 1] for i, j in self.variables.arcs if j in self.variables.nodes_refuel),
                name=f"fuel_evolution_{tau}",
            )

    def _create_constraint_6(self) -> None:
        pass

    def _create_constraint_7(self) -> None:
        for tau in self.variables.time_steps[1:]:
            self.model.addConstr(
                self.F[tau] - quicksum(self.variables.fij[i, j] * self.X[i, j, tau] for i, j in self.variables.arcs) >= 0,
                name=f"fuel_non_negative_{tau}",
            )

    # </editor-fold>

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
        self._create_constraint_2()
        self._create_constraint_3()
        self._create_constraint_4()
        self._create_constraint_5()
        self._create_constraint_6()
        self._create_constraint_7()
        self._create_objective()
        self.model.optimize()

        # Check if the model is infeasible
        if self.model.status == GRB.Status.INFEASIBLE:
            msg = "Model is infeasible."
            raise ValueError(msg)

    def results(self) -> None:
        """Print the results of the optimisation model."""
        if self.model.status == GRB.Status.OPTIMAL:
            ic("Optimal objective value:", self.model.objVal)
            ic("Optimal solution:")
            nonzero_values = {var.VarName: var.X for var in self.model.getVars() if abs(var.X) != 0}
            sorted_nonzero_values = dict(
                sorted(nonzero_values.items(), key=lambda item: int(item[0].split(",")[2][:-1]) if "," in item[0] else float("inf"))
            )

            for var_name, value in sorted_nonzero_values.items():
                ic(f"{var_name}: {value}")
