import os
from math import exp
from random import random

import matplotlib.pyplot as plt


class Cases:
    def __init__(self, cooling_schedules, neighbour_candidate_generators, starting_state_generators,
                 temperature, problem_params, plot):
        self._cooling_schedules = cooling_schedules
        self._neighbour_candidate_generators = neighbour_candidate_generators
        self._starting_state_generators = starting_state_generators
        self._temperature = temperature
        self._problem_params = problem_params
        self.plot = plot

    def __iter__(self):
        for cooling_schedule in self._cooling_schedules:
            for neighbour_candidate_generator in self._neighbour_candidate_generators:
                for starting_state_generator in self._starting_state_generators:
                    yield (self._temperature, cooling_schedule), (
                        starting_state_generator, neighbour_candidate_generator), self._problem_params


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


def test_cases(cases):
    if not os.path.exists('results'):
        os.mkdir('results')

    with open('results/common.txt', 'w', encoding='utf8') as file:
        file.write('starting_temperature:\n')
        file.write(str(cases._temperature) + '\n')
        file.write('problem_params:\n')
        file.write(str(cases._problem_params) + '\n')

    for i, case in enumerate(cases):
        temperature_params, state_params, problem_params = case
        cooling_schedule = temperature_params[1]
        starting_state_generator = state_params[0]
        neighbour_candidate_generator = state_params[1]
        starting_state = starting_state_generator()
        state_params = (starting_state, neighbour_candidate_generator)
        best_state, energy_memoization = simulated_annealing(temperature_params, state_params, problem_params)
        energy_measurement = problem_params[1]

        dir_path = 'results/{}'.format(i)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        with open(dir_path + '/results.txt', 'w', encoding='utf8') as file:
            file.write('cooling_schedule:\n')
            file.write(str(cooling_schedule) + '\n')
            file.write('starting_state_generator:\n')
            file.write(str(starting_state_generator) + '\n')
            file.write('neighbour_candidate_generator:\n')
            file.write(str(neighbour_candidate_generator) + '\n\n')

            file.write('starting_energy:\n')
            file.write(str(energy_measurement(starting_state)) + '\n')
            file.write('best_energy:\n')
            file.write(str(energy_measurement(best_state)) + '\n')

        cases.plot(starting_state, best_state, dir_path)

        plt.plot(energy_memoization)
        plt.savefig(dir_path + '/energy_memoization.png')
        plt.clf()
