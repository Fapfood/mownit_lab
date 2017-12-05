from functools import partial
from random import randrange, shuffle
from lab4.lab4 import exponential_multiplicative_cooling, simulated_annealing, linear_additive_cooling
import matplotlib.pyplot as plt

MAP_DIMENSION = 200


class City:
    def __init__(self, x=None, y=None):
        self.x = x if x is not None else randrange(MAP_DIMENSION)
        self.y = y if y is not None else randrange(MAP_DIMENSION)

    def __repr__(self):
        return '({}, {})'.format(self.x, self.y)

    def distance_to(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** (1 / 2)


def test_city_init():
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


def plot(tour1, tour2):
    x1 = [city.x for city in tour1]
    y1 = [city.y for city in tour1]

    plt.plot(x1, y1, 'co')

    a_scale = float(max(x1)) / float(60)

    for i in range(len(x1)):
        plt.arrow(x1[i - 1], y1[i - 1], x1[i] - x1[i - 1], y1[i] - y1[i - 1],
                  head_width=a_scale, color='g', length_includes_head=True)

    x2 = [city.x for city in tour2]
    y2 = [city.y for city in tour2]

    for i in range(len(x2)):
        plt.arrow(x2[i - 1], y2[i - 1], x2[i] - x2[i - 1], y2[i] - y2[i - 1],
                  head_width=a_scale, color='r', length_includes_head=True)

    plt.xlim(min(x1) * 0.9, max(x1) * 1.1)
    plt.ylim(min(x1) * 0.9, max(y1) * 1.1)
    plt.show()


if __name__ == '__main__':
    starting_tour = clique_city_init(100, 3)
    t0 = 20
    fun1 = partial(exponential_multiplicative_cooling, cooling_rate=0.000005)
    fun2 = partial(linear_additive_cooling, cooling_rate=0.00001)
    best, energy_mem = simulated_annealing((t0, fun2),
                                           (starting_tour, arbitrary_city_swapping_candidate),
                                           (cities_swap, get_distance, cities_copy, 0))

    print(starting_tour)
    print(get_distance(starting_tour))
    print(best)
    print(get_distance(best))
    plot(starting_tour, best)

    plt.plot(energy_mem)
    plt.show()
