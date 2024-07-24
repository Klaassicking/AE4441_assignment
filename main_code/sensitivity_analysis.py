"""Module to perform sensitivity analysis on the network model."""
import random

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
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

    def plot_results(self, df: pd.DataFrame) -> None:
        """Plot the results of the sensitivity analysis.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing the results of the sensitivity analysis.
        """
        for param_name in df["param_name"].unique():
            param_df = df[df["param_name"] == param_name]
            fig, ax1 = plt.subplots(figsize=(10, 6))

            sns.lineplot(data=param_df, x="param_value", y="objective_value", marker="o", ax=ax1, color="b", label="Objective Value")
            ax1.set_xlabel(param_name)
            ax1.set_ylabel("Objective Value", color="b")
            ax1.tick_params(axis="y", labelcolor="b")

            ax2 = ax1.twinx()
            sns.lineplot(data=param_df, x="param_value", y="difference", marker="x", ax=ax2, color="r", label="Difference (%)")
            ax2.set_ylabel("Difference (%)", color="r")
            ax2.tick_params(axis="y", labelcolor="r")

            fig.suptitle(f"Sensitivity Analysis for {param_name}")
            fig.tight_layout()
            fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9), bbox_transform=ax1.transAxes)
            plt.grid(True)
            plt.show()
