# AE4441_assignment

This project focuses on optimizing aircraft routing by constructing and verifying a Mixed Integer Linear Programming (MILP) model. The goal is to determine the optimal path for an aircraft from a starting node to a destination node, incorporating refueling constraints as described in the paper by Kannon et al. \cite{kannon2016aircraft}. The model ensures that sufficient fuel is onboard to complete the journey and optimizes the route through a network of nodes and arcs.

## Running the Code

### Installation

1. Install the required dependencies:
   ```bash
   pip install -r ./requirements.txt
    ```
   
2. Run the code:
run the main.py file to get the results of the model.
3. Run the run_sensitivity_analysis.py file to get the sensitivity analysis of the model.


### Development commands
```bash
pre-commit run --all-files
pytest
```

