"""Module for running a sensitivity analysis on the network model."""
from icecream import ic
from sensitivity_analysis import SensitivityAnalysis
from set_params import SetUpParameters

from main_code.main import Main

# Define the base parameters
base_params = SetUpParameters()

# Create an instance of the SensitivityAnalysis class
sensitivity_analysis = SensitivityAnalysis(base_run=Main(params=base_params))

# Define the parameter grids for sensitivity analysis
param_grids = {
    "network_size": [10, 15, 20, 30, 40],
    "psi": [1400 / 18000, 1500 / 18000, 1600 / 18000, 1700 / 18000, 1800 / 18000],
    "initial_upper_bound": [4000, 5000, 6000, 7000, 8000],
    "fuel_capacity": [20000, 25000, 30000, 35000, 40000],
    "w1": [1, 2, 3, 4, 5],
    "w2": [50, 75, 100, 125, 150],
    "m": [1, 2, 3, 4, 5],
    "e": [0.005, 0.01, 0.015, 0.02, 0.025],
    "max_time": [1800, 2400, 3600, 4800, 6000],
}


# Perform the sensitivity analysis
results_df = sensitivity_analysis.perform_analysis(param_grids)

# Save the results to a CSV file
results_df.to_csv("sensitivity_analysis_results.csv", index=False)

# Print the results
ic(results_df)

# Plot the results
sensitivity_analysis.plot_results(results_df)
