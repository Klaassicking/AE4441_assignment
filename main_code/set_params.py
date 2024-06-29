"""Module to store parameters for the network model."""

from dataclasses import dataclass


@dataclass
class SetUpParameters:
    """Parameters for the network model."""

    network_size: int = 26
    psi: float = 1600 / 18000
    initial_upper_bound: int = 6000
    fuel_capacity: int = 30000
    w1: int = 1  # Weight for cost
    w2: int = 100  # Weight for refueling cost
    m: int = 4  # Lexicographic frequency
    e: float = 0.01  # Epsilon, optimality tolerance
    max_time: int = 3600  # Max CPU time in seconds
