from random import randrange
from skimage import io
from functools import partial
from lab4.lab4 import exponential_multiplicative_cooling, simulated_annealing, linear_additive_cooling
import matplotlib.pyplot as plt


class MapException(BaseException):
    def __init__(self, message):
        self.message = message


class BinaryMap:
    def __init__(self, x, y, delta, neighbour_influence_matrix, new=True):
        self.x = x
        self.y = y
        if delta < 0 or delta > 1:
            raise MapException('wrong delta')
        self.delta = delta
        if len(neighbour_influence_matrix) % 2 == 0 or len(neighbour_influence_matrix[0]) % 2 == 0:
            raise MapException('wrong dimension of neighbour influence matrix')
        self.neighbour_influence_matrix = neighbour_influence_matrix
        self.board = None
        self.energy = None
        if new:
            self._init_board()
            self._init_energy()

    def __getitem__(self, item):
        y, x = item
        return self.board[y % self.y][x % self.x]

    def __setitem__(self, key, value):
        y, x = key
        self.board[y % self.y][x % self.x] = value

    def _init_board(self):
        if self.board is None:
            self.board = []
            for y in range(self.y):
                self.board.append([False] * self.x)
            for _ in range(round(self.x * self.y * self.delta)):
                while True:
                    x = randrange(self.x)
                    y = randrange(self.y)
                    if not self[y, x]:
                        self[y, x] = True
                        break

    def _init_energy(self):
        if self.energy is None:
            neighbour_x = len(self.neighbour_influence_matrix[0]) // 2
            neighbour_y = len(self.neighbour_influence_matrix) // 2
            energy = 0
            for x in range(self.x):
                for y in range(self.y):
                    for sx in range(-neighbour_x, neighbour_x + 1):
                        for sy in range(-neighbour_y, neighbour_y + 1):
                            if self[y, x] == self[y + sy, x + sx]:
                                energy += self.neighbour_influence_matrix[neighbour_y + sy][neighbour_x + sx]
            self.energy = energy

    def swap(self, old, new):
        if len(old) != len(new):
            raise MapException('wrong number of old and new')
        for o in old:
            x, y = o
            if not self[y, x]:
                raise MapException('old is False already')
        for n in new:
            x, y = n
            if self[y, x]:
                raise MapException('new is True already')

        neighbour_x = len(self.neighbour_influence_matrix[0]) // 2
        neighbour_y = len(self.neighbour_influence_matrix) // 2
        energy = 0
        for o in old:
            x, y = o
            for sx in range(-neighbour_x, neighbour_x + 1):
                for sy in range(-neighbour_y, neighbour_y + 1):
                    if self[y, x] == self[y + sy, x + sx]:
                        energy -= self.neighbour_influence_matrix[neighbour_y + sy][neighbour_x + sx]
                        energy -= self.neighbour_influence_matrix[neighbour_y - sy][neighbour_x - sx]
                    else:
                        energy += self.neighbour_influence_matrix[neighbour_y + sy][neighbour_x + sx]
                        energy += self.neighbour_influence_matrix[neighbour_y - sy][neighbour_x - sx]
            self[y, x] = False
        for n in new:
            x, y = n
            for sx in range(-neighbour_x, neighbour_x + 1):
                for sy in range(-neighbour_y, neighbour_y + 1):
                    if self[y, x] == self[y + sy, x + sx]:
                        energy -= self.neighbour_influence_matrix[neighbour_y + sy][neighbour_x + sx]
                        energy -= self.neighbour_influence_matrix[neighbour_y - sy][neighbour_x - sx]
                    else:
                        energy += self.neighbour_influence_matrix[neighbour_y + sy][neighbour_x + sx]
                        energy += self.neighbour_influence_matrix[neighbour_y - sy][neighbour_x - sx]
            self[y, x] = True
        self.energy += energy
        return self.energy

    def plot(self, suffix):
        """False is red, True is green"""
        matrix = []
        for row in self.board:
            matrix.append([(0, 255, 0) if i else (255, 0, 0) for i in row])
        io.imsave('binary_map' + suffix + '.png', matrix)

    def copy(self):
        new = BinaryMap(self.x, self.y, self.delta, self.neighbour_influence_matrix, False)
        board = []
        for row in self.board:
            board.append(row[:])
        new.board = board
        new.energy = self.energy
        return new


def arbitrary_pixel_swapping_candidate(_map, pixel_num=1):
    old = []
    for _ in range(pixel_num):
        while True:
            x = randrange(_map.x)
            y = randrange(_map.y)
            if _map[y, x]:
                old.append((x, y))
                break

    new = []
    for _ in range(pixel_num):
        while True:
            x = randrange(_map.x)
            y = randrange(_map.y)
            if not _map[y, x]:
                new.append((x, y))
                break

    return old, new


def map_swap(_map, old, new):
    _map.swap(old, new)
    return _map


def get_energy(current_map):
    return current_map.energy


def map_copy(_map):
    return _map.copy()


if __name__ == '__main__':
    neighbour_matrix = [
        [-2, 1, 2, 1, -2],
        [1, -3, -3, -3, 1],
        [2, -3, 0, -3, 2],
        [1, -3, -3, -3, 1],
        [-2, 1, 2, 1, -2],
    ]
    starting_map = BinaryMap(256, 256, 0.3, neighbour_matrix)
    t0 = 100
    fun = partial(exponential_multiplicative_cooling, cooling_rate=0.001)
    swapping_candidate = partial(arbitrary_pixel_swapping_candidate, pixel_num=1)
    best, energy_mem = simulated_annealing((t0, fun),
                                           (starting_map, swapping_candidate),
                                           (map_swap, get_energy, map_copy, float('-inf')))

    print(starting_map)
    print(get_energy(starting_map))
    print(best)
    print(get_energy(best))
    best.plot('_best')
    starting_map.plot('_start')

    plt.plot(energy_mem)
    plt.show()
