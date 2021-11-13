import random
import pisqpipe as pp
from collections import defaultdict as ddict

MAXCHECK = 8   # The depth for checkkill
DIST = 1    # New moves distances
BRANCH = 32  # MAX Branch
CHECK_BRANCH = 16 # checkkill branch
branch_abpruning = [32, 16, 8, 4, 4, 4, 4] # abpruning branch
MAXDEPTH = 6    # Max depth for abpruning
RATIO = 0.1     # Evaluation rate
# Score map for each pattern
score_map = {'ONE': 10,
             'TWO': 100,
             'THREE': 1000,
             'FOUR': 100000,
             'FIVE': 10000000,
             'BLOCKED_ONE': 1,
             'BLOCKED_TWO': 10,
             'BLOCKED_THREE': 100,
             'BLOCKED_FOUR': 10000
             }
# Pattern dict
pattern_dict = {# No empty point
    # ONE
    (0, 0, 1, 0, 0): score_map['ONE'],
    # BLOCKED_ONE
    (1, 0, 1, 0, 0): score_map['BLOCKED_ONE'],
    (0, 0, 1, 0, 1): score_map['BLOCKED_ONE'],
    # TWO
    (0, 0, 2, 0, 0): score_map['TWO'],
    # BLOCKED_TWO
    (1, 0, 2, 0, 0): score_map['BLOCKED_TWO'],
    (0, 0, 2, 0, 1): score_map['BLOCKED_TWO'],
    # THREE
    (0, 0, 3, 0, 0): score_map['THREE'],
    # BLOCKED_THREE
    (1, 0, 3, 0, 0): score_map['BLOCKED_THREE'],
    (0, 0, 3, 0, 1): score_map['BLOCKED_THREE'],
    # FOUR
    (0, 0, 4, 0, 0): score_map['FOUR'],
    # BLOCKED_FOUR
    (1, 0, 4, 0, 0): score_map['BLOCKED_FOUR'],
    (0, 0, 4, 0, 1): score_map['BLOCKED_FOUR'],

    # One empty point, no block

    # TWO
    # count = 2
    (0, 1, 1, 0, 0): score_map['TWO'],
    (0, 0, 1, 1, 0): score_map['TWO'],
    # THREE
    # count = 3
    (0, 1, 2, 0, 0): score_map['THREE'],
    (0, 0, 2, 1, 0): score_map['THREE'],
    (0, 2, 1, 0, 0): score_map['THREE'],
    (0, 0, 1, 2, 0): score_map['THREE'],
    # BLOCKED_FOUR
    # count = 4
    (0, 0, 3, 1, 0): score_map['BLOCKED_FOUR'],
    (0, 1, 3, 0, 0): score_map['BLOCKED_FOUR'],
    (0, 0, 1, 3, 0): score_map['BLOCKED_FOUR'],
    (0, 3, 1, 0, 0): score_map['BLOCKED_FOUR'],
    (0, 0, 2, 2, 0): score_map['BLOCKED_FOUR'],
    (0, 2, 2, 0, 0): score_map['BLOCKED_FOUR'],
    # count = 5
    (0, 0, 3, 2, 0): score_map['BLOCKED_FOUR'],
    (0, 2, 3, 0, 0): score_map['BLOCKED_FOUR'],
    (0, 0, 2, 3, 0): score_map['BLOCKED_FOUR'],
    (0, 3, 2, 0, 0): score_map['BLOCKED_FOUR'],
    # count = 6
    (0, 0, 3, 3, 0): score_map['BLOCKED_FOUR'],
    (0, 3, 3, 0, 0): score_map['BLOCKED_FOUR'],

    # FOUR
    (0, 0, 4, 1, 0): score_map['FOUR'],
    (0, 1, 4, 0, 0): score_map['FOUR'],
    (0, 0, 4, 2, 0): score_map['FOUR'],
    (0, 2, 4, 0, 0): score_map['FOUR'],
    (0, 0, 4, 3, 0): score_map['FOUR'],
    (0, 3, 4, 0, 0): score_map['FOUR'],

    # One empty point & One block
    # Same side
    # count = 2
    # 210[1]0
    (1, 1, 1, 0, 0): score_map['BLOCKED_TWO'],
    (0, 0, 1, 1, 1): score_map['BLOCKED_TWO'],
    # count = 3
    # 210[1]10, 21[1]01
    (1, 1, 2, 0, 0): score_map['BLOCKED_THREE'],
    (1, 2, 1, 0, 0): score_map['BLOCKED_THREE'],
    (0, 0, 2, 1, 1): score_map['BLOCKED_THREE'],
    (0, 0, 1, 2, 1): score_map['BLOCKED_THREE'],
    # count >= 4
    # 21101[1]0
    (1, 2, 2, 0, 0): score_map['BLOCKED_FOUR'],
    (0, 0, 2, 2, 1): score_map['BLOCKED_FOUR'],
    # 21110[1]0, 21011[1]0
    (1, 3, 1, 0, 0): score_map['BLOCKED_FOUR'],
    (1, 1, 3, 0, 0): score_map['BLOCKED_FOUR'],
    (1, 3, 2, 0, 0): score_map['BLOCKED_FOUR'],
    (1, 2, 3, 0, 0): score_map['BLOCKED_FOUR'],
    (0, 0, 1, 3, 1): score_map['BLOCKED_FOUR'],
    (0, 0, 3, 1, 1): score_map['BLOCKED_FOUR'],
    (0, 0, 2, 3, 1): score_map['BLOCKED_FOUR'],
    (0, 0, 3, 2, 1): score_map['BLOCKED_FOUR'],
    # 210[1]1110, 211110[1]0
    (1, 1, 4, 0, 0): score_map['FOUR'],
    (1, 4, 1, 0, 0): score_map['BLOCKED_FOUR'],
    (0, 0, 4, 1, 1): score_map['FOUR'],
    (0, 0, 1, 4, 1): score_map['BLOCKED_FOUR'],
    # 2110111[1]0, 2111101[1]0
    (1, 2, 4, 0, 0): score_map['FOUR'],
    (1, 4, 2, 0, 0): score_map['BLOCKED_FOUR'],
    (0, 0, 4, 2, 1): score_map['FOUR'],
    (0, 0, 2, 4, 1): score_map['BLOCKED_FOUR'],
    # 21110111[1]0, 21111011[1]0
    (1, 3, 4, 0, 0): score_map['FOUR'],
    (1, 4, 3, 0, 0): score_map['BLOCKED_FOUR'],
    (0, 0, 4, 3, 1): score_map['FOUR'],
    (0, 0, 3, 4, 1): score_map['BLOCKED_FOUR'],
    # 211110111[1]0
    (1, 4, 4, 0, 0): score_map['FOUR'],
    (0, 0, 4, 4, 1): score_map['FOUR'],

    # One empty point & One block
    # Different sides
    # count = 2
    # 2[1]010
    (1, 0, 1, 1, 0): score_map['BLOCKED_TWO'],
    (0, 1, 1, 0, 1): score_map['BLOCKED_TWO'],
    # count = 3
    # 2[1]1010, 2[1]0110
    (1, 0, 2, 1, 0): score_map['BLOCKED_THREE'],
    (1, 0, 1, 2, 0): score_map['BLOCKED_THREE'],
    (0, 1, 2, 0, 1): score_map['BLOCKED_THREE'],
    (0, 2, 1, 0, 1): score_map['BLOCKED_THREE'],
    # count >= 4
    # 21[1]0110
    (1, 0, 2, 2, 0): score_map['BLOCKED_FOUR'],
    (0, 2, 2, 0, 1): score_map['BLOCKED_FOUR'],
    # 211[1]010, 2[1]01110
    (1, 0, 1, 3, 0): score_map['BLOCKED_FOUR'],
    (1, 0, 3, 1, 0): score_map['BLOCKED_FOUR'],
    (1, 0, 2, 3, 0): score_map['BLOCKED_FOUR'],
    (1, 0, 3, 2, 0): score_map['BLOCKED_FOUR'],
    (0, 3, 1, 0, 1): score_map['BLOCKED_FOUR'],
    (0, 1, 3, 0, 1): score_map['BLOCKED_FOUR'],
    (0, 3, 2, 0, 1): score_map['BLOCKED_FOUR'],
    (0, 2, 3, 0, 1): score_map['BLOCKED_FOUR'],
    # 2[1]011110, 2[1]111010
    (1, 0, 4, 1, 0): score_map['BLOCKED_FOUR'],
    (1, 0, 1, 4, 0): score_map['BLOCKED_FOUR'],
    (0, 1, 4, 0, 1): score_map['BLOCKED_FOUR'],
    (0, 4, 1, 0, 1): score_map['BLOCKED_FOUR'],
    # 2110111[1]0, 2111101[1]0
    (1, 0, 4, 2, 0): score_map['BLOCKED_FOUR'],
    (1, 0, 2, 4, 0): score_map['BLOCKED_FOUR'],
    (0, 2, 4, 0, 1): score_map['BLOCKED_FOUR'],
    (0, 4, 2, 0, 1): score_map['BLOCKED_FOUR'],
    # 21110111[1]0, 21111011[1]0
    (1, 0, 4, 3, 0): score_map['BLOCKED_FOUR'],
    (1, 0, 3, 4, 0): score_map['BLOCKED_FOUR'],
    (0, 3, 4, 0, 1): score_map['BLOCKED_FOUR'],
    (0, 4, 3, 0, 1): score_map['BLOCKED_FOUR'],
    # 211110111[1]0
    (1, 0, 4, 4, 0): score_map['BLOCKED_FOUR'],
    (0, 4, 4, 0, 1): score_map['BLOCKED_FOUR'],

    # One empty point & Two blocks
    # IFF count >= 4 return BLOCKED_FOUR

    # 21[1]0112
    (1, 0, 2, 2, 1): score_map['BLOCKED_FOUR'],
    (1, 2, 2, 0, 1): score_map['BLOCKED_FOUR'],
    # 211[1]012, 2[1]01112
    (1, 0, 1, 3, 1): score_map['BLOCKED_FOUR'],
    (1, 0, 3, 1, 1): score_map['BLOCKED_FOUR'],
    (1, 0, 2, 3, 1): score_map['BLOCKED_FOUR'],
    (1, 0, 3, 2, 1): score_map['BLOCKED_FOUR'],
    (1, 3, 1, 0, 1): score_map['BLOCKED_FOUR'],
    (1, 1, 3, 0, 1): score_map['BLOCKED_FOUR'],
    (1, 3, 2, 0, 1): score_map['BLOCKED_FOUR'],
    (1, 2, 3, 0, 1): score_map['BLOCKED_FOUR'],
    # 2[1]011110, 2[1]111010
    (1, 0, 4, 1, 1): score_map['BLOCKED_FOUR'],
    (1, 0, 1, 4, 1): score_map['BLOCKED_FOUR'],
    (1, 1, 4, 0, 1): score_map['BLOCKED_FOUR'],
    (1, 4, 1, 0, 1): score_map['BLOCKED_FOUR'],
    # 2110111[1]0, 2111101[1]0
    (1, 0, 4, 2, 1): score_map['BLOCKED_FOUR'],
    (1, 0, 2, 4, 1): score_map['BLOCKED_FOUR'],
    (1, 2, 4, 0, 1): score_map['BLOCKED_FOUR'],
    (1, 4, 2, 0, 1): score_map['BLOCKED_FOUR'],
    # 21110111[1]0, 21111011[1]0
    (1, 0, 4, 3, 1): score_map['BLOCKED_FOUR'],
    (1, 0, 3, 4, 1): score_map['BLOCKED_FOUR'],
    (1, 3, 4, 0, 1): score_map['BLOCKED_FOUR'],
    (1, 4, 3, 0, 1): score_map['BLOCKED_FOUR'],
    # 211110111[1]0
    (1, 0, 4, 4, 1): score_map['BLOCKED_FOUR'],
    (1, 4, 4, 0, 1): score_map['BLOCKED_FOUR'],

    # Two empty points & No block
    # 010[1]010
    (0, 1, 1, 1, 0): score_map['TWO'] * 2,
    (0, 1, 2, 1, 0): score_map['THREE'] * 2,
    (0, 1, 3, 1, 0): score_map['FOUR'],
    # 0110[1]010
    (0, 3, 1, 2, 0): score_map['BLOCKED_FOUR'] + score_map['THREE'],
    (0, 2, 1, 3, 0): score_map['BLOCKED_FOUR'] + score_map['THREE'],
    (0, 3, 1, 3, 0): score_map['FOUR'],

    (0, 2, 2, 1, 0): score_map['BLOCKED_FOUR'] + score_map['THREE'],
    (0, 1, 2, 2, 0): score_map['BLOCKED_FOUR'] + score_map['THREE'],
    (0, 2, 2, 2, 0): score_map['FOUR'],

    (0, 3, 2, 2, 0): score_map['FOUR'],
    (0, 2, 2, 3, 0): score_map['FOUR'],
    (0, 3, 2, 3, 0): score_map['FOUR'],
    (0, 1, 3, 2, 0): score_map['FOUR'],
    (0, 2, 3, 1, 0): score_map['FOUR'],
    (0, 2, 3, 2, 0): score_map['FOUR'],
    (0, 3, 3, 1, 0): score_map['FOUR'],
    (0, 1, 3, 3, 0): score_map['FOUR'],
    (0, 3, 3, 2, 0): score_map['FOUR'],
    (0, 2, 3, 3, 0): score_map['FOUR'],
    (0, 3, 3, 3, 0): score_map['FOUR'],

    # One block
    # 210[1]010
    (1, 1, 1, 1, 0): score_map['TWO'] + score_map['BLOCKED_TWO'],
    (1, 1, 2, 1, 0): score_map['THREE'] + score_map['BLOCKED_THREE'],
    (1, 1, 3, 1, 0): score_map['FOUR'],
    (0, 1, 1, 1, 1): score_map['TWO'] + score_map['BLOCKED_TWO'],
    (0, 1, 2, 1, 1): score_map['THREE'] + score_map['BLOCKED_THREE'],
    (0, 1, 3, 1, 1): score_map['FOUR'],

    # 2110[1]010
    (1, 3, 1, 2, 0): score_map['BLOCKED_FOUR'] + score_map['THREE'],
    (1, 2, 1, 3, 0): score_map['BLOCKED_FOUR'] + score_map['BLOCKED_THREE'],
    (1, 3, 1, 3, 0): score_map['FOUR'],
    (0, 2, 1, 3, 1): score_map['BLOCKED_FOUR'] + score_map['THREE'],
    (0, 3, 1, 2, 1): score_map['BLOCKED_FOUR'] + score_map['BLOCKED_THREE'],
    (0, 3, 1, 3, 1): score_map['FOUR'],

    # 21101[1]010
    (1, 2, 2, 1, 0): score_map['BLOCKED_FOUR'] + score_map['THREE'],
    (1, 1, 2, 2, 0): score_map['BLOCKED_FOUR'] + score_map['BLOCKED_THREE'],
    (1, 2, 2, 2, 0): score_map['FOUR'],
    (0, 1, 2, 2, 1): score_map['BLOCKED_FOUR'] + score_map['THREE'],
    (0, 2, 2, 1, 1): score_map['BLOCKED_FOUR'] + score_map['BLOCKED_THREE'],
    (0, 2, 2, 2, 1): score_map['FOUR'],

    (1, 3, 2, 2, 0): score_map['FOUR'],
    (1, 2, 2, 3, 0): score_map['FOUR'],
    (1, 3, 2, 3, 0): score_map['FOUR'],
    (1, 1, 3, 2, 0): score_map['FOUR'],
    (1, 2, 3, 1, 0): score_map['FOUR'],
    (1, 2, 3, 2, 0): score_map['FOUR'],
    (1, 3, 3, 1, 0): score_map['FOUR'],
    (1, 1, 3, 3, 0): score_map['FOUR'],
    (1, 3, 3, 2, 0): score_map['FOUR'],
    (1, 2, 3, 3, 0): score_map['FOUR'],
    (1, 3, 3, 3, 0): score_map['FOUR'],

    (0, 3, 2, 2, 1): score_map['FOUR'],
    (0, 2, 2, 3, 1): score_map['FOUR'],
    (0, 3, 2, 3, 1): score_map['FOUR'],
    (0, 1, 3, 2, 1): score_map['FOUR'],
    (0, 2, 3, 1, 1): score_map['FOUR'],
    (0, 2, 3, 2, 1): score_map['FOUR'],
    (0, 3, 3, 1, 1): score_map['FOUR'],
    (0, 1, 3, 3, 1): score_map['FOUR'],
    (0, 3, 3, 2, 1): score_map['FOUR'],
    (0, 2, 3, 3, 1): score_map['FOUR'],
    (0, 3, 3, 3, 1): score_map['FOUR'],

    # Two blocks
    # 010[1]010
    (1, 1, 1, 1, 1): score_map['BLOCKED_TWO'] * 2,
    (1, 1, 2, 1, 1): score_map['BLOCKED_THREE'] * 2,
    (1, 1, 3, 1, 1): score_map['FOUR'],
    # 0110[1]010
    (1, 3, 1, 2, 1): score_map['BLOCKED_FOUR'] + score_map['BLOCKED_THREE'],
    (1, 2, 1, 3, 1): score_map['BLOCKED_FOUR'] + score_map['BLOCKED_THREE'],
    (1, 3, 1, 3, 1): score_map['FOUR'],

    (1, 2, 2, 1, 1): score_map['BLOCKED_FOUR'] + score_map['BLOCKED_THREE'],
    (1, 1, 2, 2, 1): score_map['BLOCKED_FOUR'] + score_map['BLOCKED_THREE'],
    (1, 2, 2, 2, 1): score_map['FOUR'],

    # both players count>=4
    (1, 3, 2, 2, 1): score_map['FOUR'],
    (1, 2, 2, 3, 1): score_map['FOUR'],
    (1, 3, 2, 3, 1): score_map['FOUR'],
    (1, 1, 3, 2, 1): score_map['FOUR'],
    (1, 2, 3, 1, 1): score_map['FOUR'],
    (1, 2, 3, 2, 1): score_map['FOUR'],
    (1, 3, 3, 1, 1): score_map['FOUR'],
    (1, 1, 3, 3, 1): score_map['FOUR'],
    (1, 3, 3, 2, 1): score_map['FOUR'],
    (1, 2, 3, 3, 1): score_map['FOUR'],
    (1, 3, 3, 3, 1): score_map['FOUR'],
                }

class Zobrist:
    def __init__(self, code=None):
        self.table = [[[random.getrandbits(64) for _ in range(pp.width)] for _ in range(pp.height)] for _ in range(1, 3)]
        if not code:
            self.code = random.getrandbits(64)
        else:
            self.code = code
    def do(self, x, y, player):
        self.code ^= self.table[1][x][y] if player == 1 else self.table[2][x][y]

    def withdraw(self, x, y, player):
        self.code ^= self.table[1][x][y] if player == 1 else self.table[2][x][y]


# Class of node for abpruning MINMAX search
class Node:
    def __init__(self, player=1, depth=0, value=None, maxdepth=MAXDEPTH, move=None):
        self.value = value
        self.player = player
        self.depth = depth
        self.maxdepth = maxdepth
        self.move = move

    def isLeaf(self):
        return self.depth == self.maxdepth


# Class of score_graph
class score_graph:
    def __init__(self, board):
        self.board = board
        self.size = (pp.width, pp.height)
        self.score1 = ddict(lambda: 0)  # Our score
        self.score2 = ddict(lambda: 0)  # Enemy's score
        self.direct_cache = {
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
        }   # Direct_cache for quick update

        self.direct_dict = {
            'R': [(1, 0), (-1, 0)],
            'C': [(0, 1), (0, -1)],
            'M': [(1, -1), (-1, 1)],
            'V': [(1, 1), (-1, -1)]
        }   # Direct_dict for direction vector
        self.init_score()
        self.activemoves = self.get_move()  # Active moves for current board

    def init_score(self):
        # Initializing the score for each point
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
        enemy = 3 - player
        if direction is None:
            target_direct_list = list(self.direct_dict.keys())
        else:
            target_direct_list = [direction]

        ret = 0
        scale = self.size[0]
        for target_direct in target_direct_list:
            direct = self.direct_dict[target_direct]
            # count
            count = 0
            # blocks
            block = [0, 0]
            # central continuous chess pieces # None continuous chess pieces
            cc = [[1, 0], [0, 0]]
            # empty point (at most 1 for each side
            empty = [0, 0]
            for k in range(len(direct)):
                i = x
                j = y
                while True:
                    i += direct[k][0]
                    j += direct[k][1]
                    t = self.board[i][j]
                    # scan from central point
                    # block, return
                    if i >= scale or j >= scale or i < 0 or j < 0 or t == enemy:
                        block[k] += 1
                        break

                    elif t == player:
                        count += 1
                        cc[empty[k]][k] += 1
                        continue

                    elif empty[k] == 0 and (0 < i < scale - 1 or not direct[k][0]) \
                            and (0 < j < scale - 1 or not direct[k][1]) and \
                            self.board[i + direct[k][0]][j + direct[k][1]] == player:
                        empty[k] = 1
                        continue

                    else:
                        break

            v = 0
            # Not in pattern_dict
            if sum(cc[0]) >= 5:
                v = score_map['FIVE']
            elif sum(empty) == 2 and sum(cc[0]) == 4:
                v = score_map['FOUR']
            else:
                key = (block[0], cc[1][0], sum(cc[0]), cc[1][1], block[1])
                if key in pattern_dict:
                    v = pattern_dict[key]

            self.direct_cache[player][target_direct][(x, y)] = v
            ret += v

        return ret

    def update_point_score(self, x, y, player, radius=6):
        # Update
        scale = self.size[0]
        for target_direct in list(self.direct_dict.keys()):
            direct = self.direct_dict[target_direct][0]
            for w in (-1, 1):
                block_1 = block_2 = False   # If block just return
                for r in range(1, radius + 1):
                    i = x + direct[0] * w * r
                    j = y + direct[1] * w * r
                    if i < 0 or j < 0 or i >= scale or j >= scale:
                        break
                    if not block_1:
                        if self.board[i][j] == 2:
                            block_1 = True
                        else:
                            self.quick_update(i, j, self.board[i][j], target_direct)
                    if not block_2:
                        if self.board[i][j] == 1:
                            block_2 = True
                        else:
                            self.quick_update(i, j, self.board[i][j], target_direct)
        self.update(x, y, player)

    def quick_update(self, x, y, player, direction):
        #Quick update for one direction
        if player != 2:
            self.score1[(x, y)] -= self.direct_cache[1][direction][(x, y)]
            self.score1[(x, y)] += self.point_score(x, y, 1, direction)
        if player != 1:
            self.score2[(x, y)] -= self.direct_cache[2][direction][(x, y)]
            self.score2[(x, y)] += self.point_score(x, y, 2, direction)

    def update(self, x, y, player):
        # Self updating for changed point
        if player == 0:
            self.score1[(x, y)] = self.point_score(x, y, 1)
            self.score2[(x, y)] = self.point_score(x, y, 2)

        elif player == 1:
            self.score2[(x, y)] = 0
            for direct in self.direct_dict.keys():
                self.direct_cache[2][direct][(x, y)] = 0
        else:
            self.score1[(x, y)] = 0
            for direct in self.direct_dict.keys():
                self.direct_cache[1][direct][(x, y)] = 0

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
        # Get active move for current board
        nei = []
        for x in range(pp.width):
            for y in range(pp.height):
                if self.isFree(x, y):
                    if self.has_neighbor(x, y):
                        nei.append((x, y))
        nei.sort(key=lambda n: max(self.score1[n], self.score2[n]), reverse=True)
        return nei[:branch]

    def seek_must(self):
        # Check must point
        # If we have win point, simply make that move
        # else if opponent has win point, we should take it
        # else if we have point for live four, we make that move
        # else if opponent has live four point, we should take it
        moves1 = []
        moves2 = []
        moves3 = []
        for x in range(pp.width):
            for y in range(pp.height):
                if self.isFree(x, y):
                    if self.score1[(x, y)] >= score_map["FIVE"]:
                        return [x, y]
                    elif self.score2[(x, y)] >= score_map["FIVE"]:
                        moves1.append([x, y])
                    elif self.score1[(x, y)] >= score_map["FOUR"]:
                        moves2.append([x, y])
                    elif self.score2[(x, y)] >= score_map["FOUR"]:
                        moves3.append([x, y])
        # Choose the move with biggest score1
        if moves1:
            return max(moves1, key=lambda n: self.score1[(n[0], n[1])])
        elif moves2:
            return max(moves2, key=lambda n: self.score1[(n[0], n[1])])
        elif moves3:
            return max(moves3, key=lambda n: self.score1[(n[0], n[1])])
        return False

    def get_winner(self):
        # Find if we have winner on the board
        for x in range(pp.width):
            for y in range(pp.height):
                if self.isOccupied(x, y):
                    if self.score1[(x, y)] >= score_map["FIVE"]:
                        return 1
                    elif self.score2[(x, y)] >= score_map["FIVE"]:
                        return 2
        return False

    def checkkill_MAX(self, depth=0, maxdepth=MAXCHECK):
        # Check kill for us
        # If depth > 0 get winner first and if there's a winner return corresponding result
        # Attack first using point larger than double live three
        # If such a point cannot be used to attack, we think about defensive move,
        # which take moves that could stop opponent from making at least BLOCKED_FOUR
        if depth > maxdepth:
            return False
        if depth > 0:
            winner = self.get_winner()
            if winner:
                if winner == 1:
                    return True
                else:
                    return False

        moves = self.activemoves[:CHECK_BRANCH]
        for move in moves:
            x, y = move
            score = self.score1[(x, y)]
            score_opp = self.score2[(x, y)]
            if score >= 2 * score_map["THREE"]:
                self.board[x][y] = 1
                self.update_point_score(x, y, 1)
                self.activemoves = self.get_move()
                action = self.checkkill_MIN(depth + 1)
                self.board[x][y] = 0
                self.update_point_score(x, y, 0)
                self.activemoves = self.get_move()
                if action:
                    if depth == 0:
                        return [x, y]
                    else:
                        return True
            if score_opp >= score_map["BLOCKED_FOUR"]:
                self.board[x][y] = 1
                self.update_point_score(x, y, 1)
                self.activemoves = self.get_move()
                action = self.checkkill_MIN(depth + 1)
                self.board[x][y] = 0
                self.update_point_score(x, y, 0)
                self.activemoves = self.get_move()
                if action:
                    if depth == 0:
                        return [x, y]
                    else:
                        return True
        return False

    def checkkill_MIN(self, depth, maxdepth=MAXCHECK):
        # Check kill for opponent
        # The actions of opponent just the same as we do in checkkill_MAX
        if depth > maxdepth:
            return False
        if depth > 1:
            winner = self.get_winner()
            if winner:
                if winner == 1:
                    return True
                else:
                    return False

        moves = self.activemoves[:CHECK_BRANCH]
        action = []
        for move in moves:
            x, y = move
            score = self.score2[(x, y)]
            score_opp = self.score1[(x, y)]
            if score >= 2 * score_map["THREE"]:
                self.board[x][y] = 2
                self.update_point_score(x, y, 2)
                self.activemoves = self.get_move()
                action = self.checkkill_MAX(depth + 1)
                self.board[x][y] = 0
                self.update_point_score(x, y, 0)
                self.activemoves = self.get_move()
                if action:
                    return True
            if score_opp >= score_map["BLOCKED_FOUR"]:
                self.board[x][y] = 2
                self.update_point_score(x, y, 2)
                self.activemoves = self.get_move()
                action = self.checkkill_MAX(depth + 1)
                self.board[x][y] = 0
                self.update_point_score(x, y, 0)
                self.activemoves = self.get_move()
                if action:
                    return True
        return False

    def evaluate(self, player):
        # Evaluate the board score by adding the occupied points score for player 1 and player 2
        # and subtract r * score2 from score1 (r depends on whether we are taking moves or waiting
        # in the current situation)
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
        # MINMAX search
        if node.move:
            x, y = node.move
            self.board[x][y] = 1 if node.player == 2 else 1
            self.update_point_score(x, y, self.board[x][y])
            self.activemoves = self.get_move()
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
            self.activemoves = self.get_move()

        return value, best_move

    def max_value(self, node, alpha, beta):
        # MAX step: our move
        v = float("-inf")
        best_move = None
        new_depth = node.depth + 1
        moves = self.activemoves[:branch_abpruning[new_depth]]

        for move in moves:
            x, y = move
            if self.score1[(x, y)] >= score_map["FIVE"]:
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
        # MIN step: opponent's move
        v = float("+inf")
        best_move = None
        new_depth = node.depth + 1
        moves = self.activemoves[:branch_abpruning[new_depth]]

        for move in moves:
            x, y = move
            if self.score2[(x, y)] >= score_map["FIVE"]:
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
    move = G.seek_must()
    if move:
        # f = open(file="D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning/test.txt", mode="a")
        # print("Use seek_must!", file=f)
        # f.close()
        return move
    move = G.checkkill_MAX()
    if move:
        # f = open(file="D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning/test.txt",
        #          mode="a")
        # print("Use checkkill!", file=f)
        # f.close()
        return move
    # f = open(file="D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning/test.txt", mode="a")
    # print("Use abpurning!", file=f)
    # f.close()
    root = Node()
    _, move = G.get_value(node=root, alpha=float('-inf'), beta=float('+inf'))
    return move

