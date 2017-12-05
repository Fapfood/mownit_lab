from math import exp
from random import random


def should_choose_neighbour(current_energy, neighbour_energy, temperature):
    if neighbour_energy < current_energy:
        return True
    return exp((current_energy - neighbour_energy) / temperature) > random()


def exponential_multiplicative_cooling(temp, cooling_rate):
    return temp * (1 - cooling_rate)


def linear_additive_cooling(temp, cooling_rate):
    return temp - cooling_rate


def simulated_annealing(temperature_params, state_params, problem_params):
    temperature, cooling_schedule = temperature_params
    starting_state, neighbour_candidate_generator = state_params
    swapping_fun, energy_measurement, copying_fun, acceptable_energy = problem_params
    energy_memoization = []

    current_state = copying_fun(starting_state)
    current_energy = energy_measurement(current_state)
    best_state = copying_fun(current_state)
    best_energy = current_energy

    while temperature > 1:
        energy_memoization.append(current_energy)

        if current_energy <= acceptable_energy:
            break

        old, new = neighbour_candidate_generator(current_state)
        neighbour_state = swapping_fun(current_state, old, new)
        neighbour_energy = energy_measurement(neighbour_state)

        if should_choose_neighbour(current_energy, neighbour_energy, temperature):
            current_state = neighbour_state
            current_energy = neighbour_energy
        else:
            current_state = swapping_fun(neighbour_state, new, old)

        if current_energy < best_energy:
            best_state = copying_fun(current_state)
            best_energy = current_energy

        temperature = cooling_schedule(temperature)

    return best_state, energy_memoization
