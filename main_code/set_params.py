"""Module to store parameters for the network model."""

from dataclasses import dataclass


@dataclass
class NetworkParameters:
    """Parameters for the network model."""

    network_size: int = 20
    psi: float = 1600 / 18000
    initial_upper_bound: int = 6000
    fuel_capacity: int = 26000
    w1: int = 1
    w2: int = 100
    m: int = 5  # Lexicographic frequency
    e: float = 0.01  # Epsilon, optimality tolerance
    max_time: int = 3600  # Max CPU time in sec
    num_time_periods: int = 20  # Same as network_size
