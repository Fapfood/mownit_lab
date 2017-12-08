import copy
import random
from functools import partial
from lab4 import exponential_multiplicative_cooling, simulated_annealing, linear_additive_cooling
import matplotlib.pyplot as plt


class Sudoku:
    def __init__(self, board, new=True):
        if new:
            self.board = self._init_board(board)
        else:
            self.board = board
        self.metadict = self._init_metadict(self.board)

    @staticmethod
    def _init_board(board):
        new_board = []
        for row in board:
            new_row = []
            for cell in row:
                if cell > 0:
                    new_row.append((True, cell))
                else:
                    new_row.append((False, cell))
            new_board.append(new_row)

        for i in range(9):
            y = i // 3 * 3
            x = i % 3 * 3
            s = set()
            for j in range(y, y + 3):
                for k in range(x, x + 3):
                    s.update({board[j][k]})
            s -= {0}
            s = {1, 2, 3, 4, 5, 6, 7, 8, 9} - s
            for j in range(y, y + 3):
                for k in range(x, x + 3):
                    if not new_board[j][k][0]:
                        elem = random.sample(s, 1)[0]
                        s -= {elem}
                        new_board[j][k] = (False, elem)
        return new_board

    @staticmethod
    def _init_metadict(board):
        metadict = {'r': {}, 'c': {}, 's': {}}
        for i in range(9):
            y = i // 3 * 3
            x = i % 3 * 3
            d_sqr = {k + 1: 0 for k in range(9)}
            for j in range(y, y + 3):
                for k in range(x, x + 3):
                    val_sqr = board[j][k][1]
                    d_sqr[val_sqr] += 1
            metadict['s'].update({i: d_sqr})
        for i in range(9):
            d_row = {k + 1: 0 for k in range(9)}
            d_col = {k + 1: 0 for k in range(9)}
            for j in range(9):
                val_row = board[i][j][1]
                val_col = board[j][i][1]
                d_row[val_row] += 1
                d_col[val_col] += 1
            metadict['r'].update({i: d_row})
            metadict['c'].update({i: d_col})
        return metadict

    def get_energy(self):
        energy = 0
        for d in self.metadict.values():
            for i in d.values():
                for j in i.values():
                    if j > 1:
                        energy += j - 1
        return energy

    def swap(self, old, new):
        o_y, o_x = old
        n_y, n_x = new
        o_val = self.board[o_y][o_x][1]
        n_val = self.board[n_y][n_x][1]

        self.metadict['r'][o_y][o_val] -= 1
        self.metadict['r'][n_y][n_val] -= 1
        self.metadict['r'][n_y][o_val] += 1
        self.metadict['r'][o_y][n_val] += 1

        self.metadict['c'][o_x][o_val] -= 1
        self.metadict['c'][n_x][n_val] -= 1
        self.metadict['c'][n_x][o_val] += 1
        self.metadict['c'][o_x][n_val] += 1

        o_s = o_y // 3 * 3 + o_x // 3
        n_s = n_y // 3 * 3 + n_x // 3
        self.metadict['s'][o_s][o_val] -= 1
        self.metadict['s'][n_s][n_val] -= 1
        self.metadict['s'][n_s][o_val] += 1
        self.metadict['s'][o_s][n_val] += 1

        self.board[o_y][o_x], self.board[n_y][n_x] = self.board[n_y][n_x], self.board[o_y][o_x]

    def plot(self):
        s = '|-----------------|\n'
        for y in range(9):
            s += '|'
            for x in range(9):
                s += str(self.board[y][x][1]) + '|'
            s += '\n|-----------------|\n'
        return s

    def copy(self):
        new = Sudoku(copy.deepcopy(self.board), False)
        return new


def arbitrary_swapping_candidate(sudoku):
    counter = 0
    breakpoint = 20
    while True:
        counter += 1
        _type = random.randrange(3)
        if _type == 0:
            i = random.randrange(9)
            y = i // 3 * 3
            x = i % 3 * 3
            j = random.randrange(y, y + 3)
            k = random.randrange(x, x + 3)
            b, val = sudoku.board[j][k]
            if not b and sudoku.metadict['s'][i][val] > 1:
                old = j, k
                break
        elif _type == 1:
            y = random.randrange(9)
            x = random.randrange(9)
            b, val = sudoku.board[y][x]
            if not b and sudoku.metadict['r'][y][val] > 1:
                old = y, x
                break
        else:
            y = random.randrange(9)
            x = random.randrange(9)
            b, val = sudoku.board[y][x]
            if not b and sudoku.metadict['c'][x][val] > 1:
                old = y, x
                break
        if counter > breakpoint:
            while True:
                y = random.randrange(9)
                x = random.randrange(9)
                if not sudoku.board[y][x][0]:
                    old = y, x
                    break
            break

    # new place
    counter = 0
    while True:
        counter += 1
        _type = random.randrange(3)
        if _type == 0:
            i = random.randrange(9)
            y = i // 3 * 3
            x = i % 3 * 3
            j = random.randrange(y, y + 3)
            k = random.randrange(x, x + 3)
            b, val = sudoku.board[j][k]
            if not b and sudoku.metadict['s'][i][val] > 1:
                new = j, k
                if old != new:
                    break
        elif _type == 1:
            y = random.randrange(9)
            x = random.randrange(9)
            b, val = sudoku.board[y][x]
            if not b and sudoku.metadict['r'][y][val] > 1:
                new = y, x
                if old != new:
                    break
        else:
            y = random.randrange(9)
            x = random.randrange(9)
            b, val = sudoku.board[y][x]
            if not b and sudoku.metadict['c'][x][val] > 1:
                new = y, x
                if old != new:
                    break
        if counter > breakpoint:
            while True:
                y = random.randrange(9)
                x = random.randrange(9)
                if not sudoku.board[y][x][0]:
                    new = y, x
                    if old != new:
                        break
            break

    return old, new


def sudoku_swap(sudoku, old, new):
    sudoku.swap(old, new)
    return sudoku


def get_energy(sudoku):
    return sudoku.get_energy()


def sudoku_copy(sudoku):
    return sudoku.copy()


if __name__ == '__main__':
    sudoku_board = [
        [0, 0, 3, 0, 2, 0, 6, 0, 0],
        [9, 0, 0, 3, 0, 5, 0, 0, 1],
        [0, 0, 1, 8, 0, 6, 4, 0, 0],
        [0, 0, 8, 1, 0, 2, 9, 0, 0],
        [7, 0, 0, 0, 0, 0, 0, 0, 8],
        [0, 0, 6, 7, 0, 8, 2, 0, 0],
        [0, 0, 2, 6, 0, 9, 5, 0, 0],
        [8, 0, 0, 2, 0, 3, 0, 0, 9],
        [0, 0, 5, 0, 1, 0, 3, 0, 0],
    ]
    starting_sudoku = Sudoku(sudoku_board)
    t0 = 10
    fun = partial(exponential_multiplicative_cooling, cooling_rate=0.00001)
    best, energy_mem = simulated_annealing((t0, fun),
                                           (starting_sudoku, arbitrary_swapping_candidate),
                                           (sudoku_swap, get_energy, sudoku_copy, 0))

    print(starting_sudoku)
    print(get_energy(starting_sudoku))
    print(starting_sudoku.plot())

    print(best)
    print(get_energy(best))
    print(best.plot())

    plt.plot(energy_mem)
    plt.show()
