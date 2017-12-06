from functools import partial
from random import randrange, shuffle

import matplotlib.pyplot as plt

from lab4 import exponential_multiplicative_cooling, linear_additive_cooling, Cases, test_cases

MAP_DIMENSION = 200


class City:
    def __init__(self, x=None, y=None):
        self.x = x if x is not None else randrange(MAP_DIMENSION)
        self.y = y if y is not None else randrange(MAP_DIMENSION)

    def __repr__(self):
        return '({}, {})'.format(self.x, self.y)

    def distance_to(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** (1 / 2)


def example_city_init():
    tour = [City(60, 200),
            City(180, 200),
            City(80, 180),
            City(140, 180),
            City(20, 160),
            City(100, 160),
            City(200, 160),
            City(140, 140),
            City(40, 120),
            City(100, 120),
            City(180, 100),
            City(60, 80),
            City(120, 80),
            City(180, 60),
            City(20, 40),
            City(100, 40),
            City(200, 40),
            City(20, 20),
            City(60, 20),
            City(160, 20),
            ]
    shuffle(tour)
    return tour


def clique_city_init(n, k):
    cities = []
    part = 5000
    margin = 2000
    for i in range(k):
        for j in range(k):
            for _ in range(n // (k * k)):
                x = randrange(part - 2 * margin) + part * i + margin
                y = randrange(part - 2 * margin) + part * j + margin
                c = City(x, y)
                cities.append(c)
    shuffle(cities)
    return cities


def get_distance(tour):
    distance = 0
    for i, city in enumerate(tour):
        distance += city.distance_to(tour[i - 1])
    return distance


def arbitrary_city_swapping_candidate(tour):
    p1 = randrange(len(tour))
    p2 = randrange(len(tour))
    return p1, p2


def consecutive_city_swapping_candidate(tour):
    p = randrange(len(tour))
    return p, (p + 1) % len(tour)


def cities_swap(tour, old, new):
    tour[old], tour[new] = tour[new], tour[old]
    return tour


def cities_copy(tour):
    return tour.copy()


def plot(tour1, tour2, dir_path):
    x1 = [city.x for city in tour1]
    y1 = [city.y for city in tour1]

    plt.plot(x1, y1, 'co')

    a_scale = max(x1) / 100

    for i in range(len(x1)):
        plt.arrow(x1[i - 1], y1[i - 1], x1[i] - x1[i - 1], y1[i] - y1[i - 1],
                  head_width=a_scale, color='g', length_includes_head=True)

    x2 = [city.x for city in tour2]
    y2 = [city.y for city in tour2]

    for i in range(len(x2)):
        plt.arrow(x2[i - 1], y2[i - 1], x2[i] - x2[i - 1], y2[i] - y2[i - 1],
                  head_width=a_scale, color='r', length_includes_head=True)

    margin = a_scale
    plt.xlim(min(x1) - margin, max(x1) + margin)
    plt.ylim(min(y1) - margin, max(y1) + margin)
    plt.savefig(dir_path + '/start_vs_best.png')
    plt.clf()


if __name__ == '__main__':
    starting_tour_generator_1 = partial(clique_city_init, n=100, k=1)
    starting_tour_generator_2 = partial(clique_city_init, n=100, k=2)
    starting_tour_generator_3 = partial(clique_city_init, n=100, k=3)
    starting_tour_generators = [starting_tour_generator_1, starting_tour_generator_2, starting_tour_generator_3]

    t0 = 100
    cooling_schedule_1 = partial(exponential_multiplicative_cooling, cooling_rate=0.000001)
    cooling_schedule_2 = partial(linear_additive_cooling, cooling_rate=0.00001)
    cooling_schedules = [cooling_schedule_1, cooling_schedule_2]

    neighbour_candidate_generators = [arbitrary_city_swapping_candidate, consecutive_city_swapping_candidate]
    problem_params = (cities_swap, get_distance, cities_copy, 0)

    cases = Cases(cooling_schedules, neighbour_candidate_generators, starting_tour_generators, t0, problem_params, plot)
    test_cases(cases)
