import random

import pisqpipe as pp
import re
from collections import defaultdict as ddict
from collections import Counter
import copy

MAXCHECK = 6
DIST = 1
BRANCH = 20
MAXDEPTH = 2
RATIO = 0.05
pattern_dict = {("WIN", (), ()): "11111",
                ("F4", (0, 5), ()): "011110",
                ("B4", (0), (5)): "011112",
                ("B4", (5), (0)): "211110",
                ("B4", (0), ()): "01111$",
                ("B4", (4), ()): "^11110",
                ("B4", (0, 2, 6), ()): "0101110",
                ("B4", (0, 3, 6), ()): "0110110",
                ("B4", (0, 4, 6), ()): "0111010",
                ("F3", (0, 4, 5), ()): "011100",
                ("F3", (0, 1, 5), ()): "001110",
                ("F3", (0, 2, 5), ()): "010110",
                ("F3", (0, 3, 5), ()): "011010",
                ("B3", (0, 1), (5)): "001112",
                ("B3", (0, 1), ()): "00111$",
                ("B3", (4, 5), (0)): "211100",
                ("B3", (4, 5), ()): "^11100",
                ("B3", (0, 2), (5)): "010112",
                ("B3", (0, 2), ()): "01011$",
                ("B3", (3, 5), (0)): "211010",
                ("B3", (3, 5), ()): "^110101",
                ("B3", (0, 3), (5)): "011012",
                ("B3", (0, 3), ()): "01101$",
                ("B3", (2, 5), (0)): "210110",
                ("B3", (2, 5), ()): "^10110",
                ("B3", (1, 2), ()): "10011",
                ("B3", (2, 3), ()): "11001",
                ("B3", (1, 3), ()): "10101",
                ("B3", (1, 5), (0, 6)): "2011102",
                ("B3", (1, 5), (0)): "201110$",
                ("B3", (1, 5), (6)): "^011102",
                ("F2", (0, 3, 4, 5), ()): "011000",
                ("F2", (0, 1, 4, 5), ()): "001100",
                ("F2", (0, 1, 2, 5), ()): "000110",
                ("F2", (0, 2, 4, 5), ()): "010100",
                ("F2", (0, 1, 3, 5), ()): "001010",
                ("F2", (0, 2, 3, 5), ()): "010010",
                ("B2", (0, 1, 2), (5)): "000112",
                ("B2", (0, 1, 2), ()): "00011$",
                ("B2", (3, 4, 5), (0)): "211000",
                ("B2", (3, 4, 5), ()): "^11000",
                ("B2", (0, 1, 3), (5)): "001012",
                ("B2", (0, 1, 3), ()): "00101$",
                ("B2", (2, 4, 5), (0)): "210100",
                ("B2", (2, 4, 5), ()): "^10100",
                ("B2", (0, 2, 3), (5)): "010012",
                ("B2", (0, 2, 3), ()): "01001$",
                ("B2", (2, 3, 5), (0)): "210010",
                ("B2", (2, 3, 5), ()): "^10010",
                ("B2", (1, 2, 3), ()): "10001",
                ("B2", (1, 3, 5), (0, 6)): "2010102",
                ("B2", (1, 3, 5), (0)): "201010$",
                ("B2", (1, 3, 5), (6)): "^010102",
                ("B2", (1, 4, 5), (0, 6)): "2011002",
                ("B2", (1, 4, 5), (0)): "201100$",
                ("B2", (1, 4, 5), (6)): "^011002",
                ("B2", (1, 2, 5), (0, 6)): "2001102",
                ("B2", (1, 2, 5), (0)): "200110$",
                ("B2", (1, 2, 5), (6)): "^001102",
                ("F1", (0, 2, 3, 4), ()): "01000",
                ("F1", (0, 1, 3, 4), ()): "00100",
                ("F1", (0, 1, 2, 4), ()): "00010",
                }
score_map = {"WIN": 10000000,
             "F4": 100000,
             "B4": 10000,
             "F3": 1000,
             "B3": 100,
             "F2": 100,
             "B2": 10,
             "F1": 10,
             "B1": 1
             }
direction_map = {"R": [1, 0],
                 "C": [0, 1],
                 "M": [1, 1],
                 "V": [1, -1]
                 }
STATE = dir()


class Zobrist:
    def __init__(self):
        self.table = [[[random.getrandbits(64) for _ in range(pp.width)] for _ in range(pp.height)] for _ in range(1, 3)]

    def do(self, x, y, player):
        self.code ^= self.table[1][x][y] if player == 1 else self.table[2][x][y]

    def withdraw(self, x, y, player):
        self.code ^= self.table[1][x][y] if player == 1 else self.table[2][x][y]


class Node:
    def __init__(self, player=1, depth=0, value=None, maxdepth=MAXDEPTH, move=None):
        self.value = value
        self.player = player
        self.depth = depth
        self.maxdepth = maxdepth
        self.move = move

    def isLeaf(self):
        return self.depth == self.maxdepth


class score_graph:
    def __init__(self, board):
        self.board = board
        self.size = (pp.width, pp.height)
        self.score1 = ddict(lambda: 0)  # Our score
        self.score2 = ddict(lambda: 0)  # Enemy's score
        self.dirct_cache = {
            1: {
                "R": ddict(lambda: 0.0),
                "C": ddict(lambda: 0.0),
                "M": ddict(lambda: 0.0),
                "V": ddict(lambda: 0.0)
            },
            2: {
                "R": ddict(lambda: 0.0),
                "C": ddict(lambda: 0.0),
                "M": ddict(lambda: 0.0),
                "V": ddict(lambda: 0.0)
            }
        }
        self.init_score()

    def init_score(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.board[i][j] == 0:
                    self.score1[(i, j)] = self.point_score(i, j, 1)
                    self.score2[(i, j)] = self.point_score(i, j, 2)
                elif self.board[i][j] == 1:
                    self.score1[(i, j)] = self.point_score(i, j, 1)
                elif self.board[i][j] == 2:
                    self.score2[(i, j)] = self.point_score(i, j, 2)

    def point_score(self, x, y, player, direction=None):
        MAX = 5
        if direction == None:
            direct_list = list(direction_map.keys())
        else:
            direct_list = [direction]
        score = 0

        for direct in direct_list:
            vtemp = 0
            V = direction_map[direct]
            x1temp = x - V[0] * MAX
            y1temp = y - V[1] * MAX
            x2temp = x + V[0] * MAX
            y2temp = y + V[1] * MAX
            x1temp = max(0, x1temp) if x1temp < pp.width else pp.width
            y1temp = max(0, y1temp) if y1temp < pp.height else pp.height
            x2temp = max(0, x2temp) if x2temp < pp.width else pp.width
            y2temp = max(0, y2temp) if y2temp < pp.height else pp.height
            num = max(abs(x2temp - x1temp), abs(y2temp - y1temp))
            temp = [self.board[x1temp + i * V[0]][y1temp + i * V[1]] for i in range(num + 1)]
            if self.isFree(x, y):
                temp[max(abs(x - x1temp), abs(y - y1temp))] = player
            if player == 2:
                temp = [(3 - temp[i]) % 3 for i in range(len(temp))]
            work_str = "".join(map(str, temp))
            pattern_counter = Counter()
            for key in pattern_dict.keys():
                pattern_counter[key[0]] += len(re.findall(pattern_dict[key], work_str))
            for pattern, count in pattern_counter.items():
                vtemp = vtemp + score_map[pattern] * count
            self.dirct_cache[player][direct][(x, y)] = vtemp
            score = score + vtemp
        return score

    def update_point_score(self, x, y, player):
        R = 5
        for direct, V in direction_map.items():
            for r in [-1, 1]:
                flag = 0
                for k in range(1, R + 1):
                    i = x + V[0] * k * r
                    j = y + V[1] * k * r
                    if i < 0 or j < 0 or i > pp.width or j > pp.height:
                        break
                    else:
                        if self.board[i][j] != 0:
                            if not flag:
                                flag = self.board[i][j]
                            elif self.board[i][j] != flag:
                                break
                        self.quick_update(i, j, self.board[i][j], direct)
        self.update(x, y, player)

    def quick_update(self, x, y, player, direction):
        if player != 2:
            self.score1[(x, y)] -= self.dirct_cache[1][direction][(x, y)]
            self.score1[(x, y)] += self.point_score(x, y, 1, direction)
        if player != 1:
            self.score2[(x, y)] -= self.dirct_cache[2][direction][(x, y)]
            self.score2[(x, y)] += self.point_score(x, y, 2, direction)

    def update(self, x, y, player):
        if player == 0:
            self.score1[(x, y)] = self.point_score(x, y, 1)
            self.score2[(x, y)] = self.point_score(x, y, 2)

        elif player == 1:
            self.score2[(x, y)] = 0
            for direct in direction_map.keys():
                self.dirct_cache[2][direct][(x, y)] = 0
        else:
            self.score1[(x, y)] = 0
            for direct in direction_map.keys():
                self.dirct_cache[1][direct][(x, y)] = 0

    def isFree(self, x, y):
        return self.board[x][y] == 0

    def isOccupied(self, x, y):
        return self.board[x][y] != 0

    def has_neighbor(self, x, y, dist=DIST):
        for i in range(-dist if x - dist >= 0 else -x, dist + 1 if x + dist < pp.width else pp.width - x):
            for j in range(-dist if y - dist >= 0 else -y, dist + 1 if y + dist < pp.height else pp.height - y):
                if self.isOccupied(x + i, y + j):
                    return True
        return False

    def get_move(self, branch=BRANCH):
        nei = []
        for x in range(pp.width):
            for y in range(pp.height):
                if self.isFree(x, y):
                    if self.has_neighbor(x, y):
                        nei.append((x, y))
        nei.sort(key=lambda n: max(self.score1[n], self.score2[n]), reverse=True)
        return nei[0 : branch]

    def seek_must(self):
        moves = []
        for x in range(pp.width):
            for y in range(pp.height):
                if self.isFree(x, y):
                    if self.score1[(x, y)] >= score_map["F4"]:
                        return [x, y]
                    elif self.score2[(x, y)] >= score_map["F4"]:
                        moves.append([x, y])
        if moves:
            return random.choice(moves)
        return False

    def get_winner(self):
        for x in range(pp.width):
            for y in range(pp.height):
                if self.isOccupied(x, y):
                    if self.score1[(x, y)] >= score_map["WIN"]:
                        return 1
                    elif self.score2[(x, y)] >= score_map["WIN"]:
                        return 2
        return False

    def checkkill_MAX(self, depth=0, maxdepth=MAXCHECK):    # Our move
        if depth > maxdepth:
            return False
        if depth > 0:
            winner = self.get_winner()
            if winner:
                if winner == 1:
                    return True
                else:
                    return False

        moves = self.get_move()
        action = []
        for move in moves:
            x, y = move
            score = self.score1[(x, y)]
            score_opp = self.score2[(x, y)]
            if score_opp >= score_map["B4"]:
                self.board[x][y] = 1
                self.update_point_score(x, y, 1)
                action = self.checkkill_MIN(depth + 1)
                self.board[x][y] = 0
                self.update_point_score(x, y, 0)
                if action:
                    if depth == 0:
                        return [x, y]
                    else:
                        False
            if score >= 2 * score_map["F3"]:
                self.board[x][y] = 1
                self.update_point_score(x, y, 1)
                action = self.checkkill_MIN(depth + 1)
                self.board[x][y] = 0
                self.update_point_score(x, y, 0)
            if action:
                if depth == 0:
                    return [x, y]
                else:
                    return True
        return False

    def checkkill_MIN(self, depth, maxdepth=MAXCHECK):
        if depth > maxdepth:
            return False
        if depth > 1:
            winner = self.get_winner()
            if winner:
                if winner == 1:
                    return True
                else:
                    return False

        moves = self.get_move()
        action = []
        for move in moves:
            x, y = move
            score = self.score2[(x, y)]
            score_opp = self.score1[(x, y)]
            if score_opp >= score_map["B4"]:
                self.board[x][y] = 2
                self.update_point_score(x, y, 2)
                action = self.checkkill_MAX(depth + 1)
                self.board[x][y] = 0
                self.update_point_score(x, y, 0)
                if action:
                    return True
            if score >= 2 * score_map["F3"]:
                self.board[x][y] = 2
                self.update_point_score(x, y, 2)
                action = self.checkkill_MAX(depth + 1)
                self.board[x][y] = 0
                self.update_point_score(x, y, 0)
            if action:
                return True
        return False

    def evaluate(self, player):
        score1 = 0
        score2 = 0
        for x in range(pp.width):
            for y in range(pp.height):
                if self.board[x][y] == 1:
                    score1 += self.score1[(x, y)]
                elif self.board[x][y] == 2:
                    score2 += self.score2[(x, y)]
        r = 1 - RATIO if player == 1 else 1 + RATIO
        score = score1 - r * score2
        return score

    def get_value(self, node, alpha, beta):
        if node.move:
            x, y = node.move
            self.board[x][y] = 1 if node.player == 2 else 1
            self.update_point_score(x, y, self.board[x][y])
        if node.isLeaf():
            value, best_move = self.evaluate(node.player), None
        else:
            if node.player == 1:
                value, best_move = self.max_value(node, alpha, beta)
            else:
                value, best_move = self.min_value(node, alpha, beta)

        if node.move:
            x, y = node.move
            self.board[x][y] = 0
            self.update_point_score(x, y, 0)

        return value, best_move

    def max_value(self, node, alpha, beta):
        v = float("-inf")
        best_move = None
        moves = self.get_move(branch=8)
        new_depth = node.depth + 1

        for move in moves:
            x, y = move
            if self.score1[(x, y)] >= score_map["WIN"]:
                return float("+inf"), move
            new_node = Node(player=2 if node.player == 1 else 1, depth=new_depth, value=None, move=move)
            temp_v, temp_move = self.get_value(new_node, alpha, beta)[0], move
            if temp_v >= v:
                v, best_move = temp_v, temp_move
            if v >= beta:
                return v, best_move
            alpha = max(alpha, v)
        return v, best_move

    def min_value(self, node, alpha, beta):
        v = float("+inf")
        best_move = None
        moves = self.get_move(branch=8)
        new_depth = node.depth + 1

        for move in moves:
            x, y = move
            if self.score2[(x, y)] >= score_map["WIN"]:
                return float("-inf"), move
            new_node = Node(player=2 if node.player == 1 else 1, depth=new_depth, value=None, move=move)
            temp_v, temp_move = self.get_value(new_node, alpha, beta)[0], move
            if temp_v <= v:
                v, best_move = temp_v, temp_move
            if v <= alpha:
                return v, best_move
            beta = min(beta, v)
        return v, best_move


def abpruning_move(board):
    G = score_graph(board)
    if G.seek_must():
        move = G.seek_must()
        return move
    elif G.checkkill_MAX():
        move = G.checkkill_MAX()
        return move
    else:
        root = Node()
        _, move = G.get_value(node=root, alpha=float('-inf'), beta=float('+inf'))
        return move

