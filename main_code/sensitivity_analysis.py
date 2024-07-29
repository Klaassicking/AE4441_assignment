"""Module to perform sensitivity analysis on the network model."""
import random

import matplotlib.pyplot as plt
import pandas as pd
from gurobipy import GRB
from icecream import ic
from main import Main
from set_params import SetUpParameters

# ruff: noqa: TRY300


class SensitivityAnalysis:
    """Class to perform sensitivity analysis on the network model.

    Attributes
    ----------
    base_params : SetUpParameters
        The base parameters for the optimization model as defined in set_params.py.
    base_objective_value : float
        The objective value of the optimization model with the base parameters.
    """

    def __init__(self, base_run: Main) -> None:
        """Initialize the SensitivityAnalysis class with base parameters.

        Parameters
        ----------
        base_params : SetUpParameters
            The base parameters for the optimization model as defined in set_params.py.
        """
        self.base_params = base_run.params
        self.base_objective_value = self.run_optimization(self.base_params)
        self.base_network = base_run.network

    def modify_params(self, **kwargs) -> SetUpParameters:
        """Modify parameters based on the provided keyword arguments.

        Parameters
        ----------
        **kwargs : dict
            Arbitrary keyword arguments representing the parameters to modify.

        Returns
        -------
        SetUpParameters
            The modified parameters object.
        """
        return SetUpParameters(**{**self.base_params.__dict__, **kwargs})

    def run_optimization(self, modified_params: SetUpParameters) -> float | None:
        """Run the optimization model with the given parameters and return the objective value or None if infeasible.

        Parameters
        ----------
        modified_params : SetUpParameters
            The modified parameters for the optimization model.

        Returns
        -------
        float
            The objective value of the optimization model if solved optimally, otherwise None.
        """
        random.seed(42)
        main = Main(params=modified_params)
        try:
            results = main.get_results()
            solved_model = results.model
            if solved_model.status == GRB.OPTIMAL:
                ic(solved_model.objVal)
                return solved_model.objVal
            if solved_model.status == GRB.INFEASIBLE:
                ic(f"Optimization infeasible for parameters: {modified_params}")
                return None
            ic(f"Optimization resulted in status {solved_model.status} for parameters: {modified_params}")
            return None
        except AttributeError as e:
            ic(f"Optimization failed due to missing attribute: {e}")
            return None
        except Exception as e:
            ic(f"Optimization failed: {e}")
            return None

    def calculate_percentual_change(self, obj_val: float | None) -> float | None:
        """Calculate the percentual change in the objective value."""
        if obj_val is not None and self.base_objective_value is not None:
            return (obj_val - self.base_objective_value) / self.base_objective_value * 100
        return None

    def perform_analysis(self, param_grids: dict) -> pd.DataFrame:
        """Perform sensitivity analysis on all given parameters based on their grids.

        Parameters
        ----------
        param_grids : dict
            Dictionary where keys are parameter names and values are lists of values to test for sensitivity analysis.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the results of the sensitivity analysis.
        """
        results = []
        for param_name, values in param_grids.items():
            for value in values:
                ic(f"New sensitivity analysis for {param_name}: {value}")
                modified_params = self.modify_params(**{param_name: value})
                obj_val = self.run_optimization(modified_params)
                percentual_change = (
                    ((obj_val - self.base_objective_value) / self.base_objective_value * 100)
                    if obj_val is not None and self.base_objective_value is not None
                    else None
                )

                results.append({"param_name": param_name, "param_value": value, "objective_value": obj_val, "difference": percentual_change})
        return pd.DataFrame(results)

    @staticmethod
    def _plot_multiple_data(data_list: list[tuple[float, float, float]]) -> None:
        """Plot multiple data on the same plot."""
        fig, ax1 = plt.subplots(figsize=(10, 6))

        colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]
        ax = ax1

        for i, data in enumerate(data_list):
            dataframe = pd.DataFrame(data)

            if i == 0:
                # Primary x-axis
                ax1.set_xlabel(f"{dataframe['param_name'].iloc[0]} param_value")
                ax1.set_ylabel("objective_value", color=colors[i % len(colors)])
                ax1.plot(
                    dataframe["param_value"],
                    dataframe["objective_value"],
                    marker="o",
                    label=f"Objective Value ({dataframe['param_name'].iloc[0]})",
                    color=colors[i % len(colors)],
                )
                ax1.tick_params(axis="y", labelcolor=colors[i % len(colors)])
                ax1.legend(loc="upper left")

                ax2 = ax1.twinx()
                color = "tab:red"
                ax2.set_ylabel("difference", color=color)
                ax2.tick_params(axis="y", labelcolor=color)
                ax2.legend(loc="upper right")

            else:
                # Secondary x-axis
                ax = ax1.twiny()
                ax.spines["top"].set_position(("outward", 60 * i))
                ax.set_xlabel(f"{dataframe['param_name'].iloc[0]} param_value", color=colors[i % len(colors)])
                ax.plot(
                    dataframe["param_value"],
                    dataframe["objective_value"],
                    marker="o",
                    label=f"Objective Value ({dataframe['param_name'].iloc[0]})",
                    color=colors[i % len(colors)],
                )
                ax.tick_params(axis="x", labelcolor=colors[i % len(colors)])
                ax.legend(loc="upper right")

                ax2 = ax1.twinx()
                color = "tab:red"
                ax2.set_ylabel("difference", color=color)
                ax2.tick_params(axis="y", labelcolor=color)
                ax2.legend(loc="upper right")

        fig.tight_layout()
        plt.title("Param Value vs. Objective Value for multiple parameters")
        plt.show()

    def plot_results(self, df: pd.DataFrame, exclude_params: list[str] | None = None) -> None:
        """Plot the results of the sensitivity analysis.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing the results of the sensitivity analysis.
        exclude_params : list, optional
            List of parameters to exclude from the plot, by default None.
        """
        if exclude_params is None:
            exclude_params = []
        data_list = []
        for param_name in df["param_name"].unique():
            if param_name not in exclude_params:
                data_list.append(df[df["param_name"] == param_name])
            max_length = 3
            if len(data_list) == max_length:
                self._plot_multiple_data(data_list)
                data_list = []
