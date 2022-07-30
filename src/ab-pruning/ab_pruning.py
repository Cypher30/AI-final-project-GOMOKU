import random
import copy
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG
from collections import defaultdict as ddict
from build import THRESHOLD, branch, DIST, RATIO, BRUNCH, DEPTH, CHECK_DIST

infotext = (
    'name="ab_pruning", '
    'author="DWB, ZZJ", '
    'country="China", '
    'school="FDU", '
    'www="https://github.com/DWB1115/Gomoku/blob/main/ab_pure.py"'
)

# f = open("C:/Users/Little_Zhang/Desktop/人工智能/finalpj/logtext.txt", 'w')

MAX_BOARD = 100
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
score = {
    'ONE': 10,
    'TWO': 100,
    'THREE': 1000,
    'FOUR': 100000,
    'FIVE': 10000000,
    'BLOCKED_ONE': 1,
    'BLOCKED_TWO': 10,
    'BLOCKED_THREE': 100,
    'BLOCKED_FOUR': 10000
}

# TODO: count to score 打表
# (左堵, 左段, 中心段, 右段, 右堵)
scoreDict = {
    # 无空点
    # 活一
    (0, 0, 1, 0, 0): score['ONE'],
    # 眠一
    (1, 0, 1, 0, 0): score['BLOCKED_ONE'],
    (0, 0, 1, 0, 1): score['BLOCKED_ONE'],
    # 活二
    (0, 0, 2, 0, 0): score['TWO'],
    # 眠二
    (1, 0, 2, 0, 0): score['BLOCKED_TWO'],
    (0, 0, 2, 0, 1): score['BLOCKED_TWO'],
    # 活三
    (0, 0, 3, 0, 0): score['THREE'],
    # 眠三
    (1, 0, 3, 0, 0): score['BLOCKED_THREE'],
    (0, 0, 3, 0, 1): score['BLOCKED_THREE'],
    # 活四
    (0, 0, 4, 0, 0): score['FOUR'],
    # 眠四
    (1, 0, 4, 0, 0): score['BLOCKED_FOUR'],
    (0, 0, 4, 0, 1): score['BLOCKED_FOUR'],

    # 一个空点, 无堵点
    # Question: 是否应该与活二等同?

    # 活二
    # count = 2
    (0, 1, 1, 0, 0): score['TWO'],
    (0, 0, 1, 1, 0): score['TWO'],
    # 活三
    # count = 3
    (0, 1, 2, 0, 0): score['THREE'],
    (0, 0, 2, 1, 0): score['THREE'],
    (0, 2, 1, 0, 0): score['THREE'],
    (0, 0, 1, 2, 0): score['THREE'],
    # 眠四
    # count = 4
    (0, 0, 3, 1, 0): score['BLOCKED_FOUR'],
    (0, 1, 3, 0, 0): score['BLOCKED_FOUR'],
    (0, 0, 1, 3, 0): score['BLOCKED_FOUR'],
    (0, 3, 1, 0, 0): score['BLOCKED_FOUR'],
    (0, 0, 2, 2, 0): score['BLOCKED_FOUR'],
    (0, 2, 2, 0, 0): score['BLOCKED_FOUR'],
    # count = 5
    (0, 0, 3, 2, 0): score['BLOCKED_FOUR'],
    (0, 2, 3, 0, 0): score['BLOCKED_FOUR'],
    (0, 0, 2, 3, 0): score['BLOCKED_FOUR'],
    (0, 3, 2, 0, 0): score['BLOCKED_FOUR'],
    # count = 6
    (0, 0, 3, 3, 0): score['BLOCKED_FOUR'],
    (0, 3, 3, 0, 0): score['BLOCKED_FOUR'],

    # 活四
    (0, 0, 4, 1, 0): score['FOUR'],
    (0, 1, 4, 0, 0): score['FOUR'],
    (0, 0, 4, 2, 0): score['FOUR'],
    (0, 2, 4, 0, 0): score['FOUR'],
    (0, 0, 4, 3, 0): score['FOUR'],
    (0, 3, 4, 0, 0): score['FOUR'],

    # 一个空点，一个堵点
    # 空点和堵点共侧
    # count = 2
    # 210[1]0
    (1, 1, 1, 0, 0): score['BLOCKED_TWO'],
    (0, 0, 1, 1, 1): score['BLOCKED_TWO'],
    # count = 3
    # 210[1]10, 21[1]01
    (1, 1, 2, 0, 0): score['BLOCKED_THREE'],
    (1, 2, 1, 0, 0): score['BLOCKED_THREE'],
    (0, 0, 2, 1, 1): score['BLOCKED_THREE'],
    (0, 0, 1, 2, 1): score['BLOCKED_THREE'],
    # count >= 4
    # 21101[1]0
    (1, 2, 2, 0, 0): score['BLOCKED_FOUR'],
    (0, 0, 2, 2, 1): score['BLOCKED_FOUR'],
    # 21110[1]0, 21011[1]0
    (1, 3, 1, 0, 0): score['BLOCKED_FOUR'],
    (1, 1, 3, 0, 0): score['BLOCKED_FOUR'],
    (1, 3, 2, 0, 0): score['BLOCKED_FOUR'],
    (1, 2, 3, 0, 0): score['BLOCKED_FOUR'],
    (0, 0, 1, 3, 1): score['BLOCKED_FOUR'],
    (0, 0, 3, 1, 1): score['BLOCKED_FOUR'],
    (0, 0, 2, 3, 1): score['BLOCKED_FOUR'],
    (0, 0, 3, 2, 1): score['BLOCKED_FOUR'],
    # 210[1]1110, 211110[1]0
    (1, 1, 4, 0, 0): score['FOUR'],
    (1, 4, 1, 0, 0): score['BLOCKED_FOUR'],
    (0, 0, 4, 1, 1): score['FOUR'],
    (0, 0, 1, 4, 1): score['BLOCKED_FOUR'],
    # 2110111[1]0, 2111101[1]0
    (1, 2, 4, 0, 0): score['FOUR'],
    (1, 4, 2, 0, 0): score['BLOCKED_FOUR'],
    (0, 0, 4, 2, 1): score['FOUR'],
    (0, 0, 2, 4, 1): score['BLOCKED_FOUR'],
    # 21110111[1]0, 21111011[1]0
    (1, 3, 4, 0, 0): score['FOUR'],
    (1, 4, 3, 0, 0): score['BLOCKED_FOUR'],
    (0, 0, 4, 3, 1): score['FOUR'],
    (0, 0, 3, 4, 1): score['BLOCKED_FOUR'],
    # 211110111[1]0
    (1, 4, 4, 0, 0): score['FOUR'],
    (0, 0, 4, 4, 1): score['FOUR'],

    # 一个空点，一个堵点
    # 空点和堵点异侧
    # count = 2
    # 2[1]010
    (1, 0, 1, 1, 0): score['BLOCKED_TWO'],
    (0, 1, 1, 0, 1): score['BLOCKED_TWO'],
    # count = 3
    # 2[1]1010, 2[1]0110
    (1, 0, 2, 1, 0): score['BLOCKED_THREE'],
    (1, 0, 1, 2, 0): score['BLOCKED_THREE'],
    (0, 1, 2, 0, 1): score['BLOCKED_THREE'],
    (0, 2, 1, 0, 1): score['BLOCKED_THREE'],
    # count >= 4
    # 21[1]0110
    (1, 0, 2, 2, 0): score['BLOCKED_FOUR'],
    (0, 2, 2, 0, 1): score['BLOCKED_FOUR'],
    # 211[1]010, 2[1]01110
    (1, 0, 1, 3, 0): score['BLOCKED_FOUR'],
    (1, 0, 3, 1, 0): score['BLOCKED_FOUR'],
    (1, 0, 2, 3, 0): score['BLOCKED_FOUR'],
    (1, 0, 3, 2, 0): score['BLOCKED_FOUR'],
    (0, 3, 1, 0, 1): score['BLOCKED_FOUR'],
    (0, 1, 3, 0, 1): score['BLOCKED_FOUR'],
    (0, 3, 2, 0, 1): score['BLOCKED_FOUR'],
    (0, 2, 3, 0, 1): score['BLOCKED_FOUR'],
    # 2[1]011110, 2[1]111010
    (1, 0, 4, 1, 0): score['BLOCKED_FOUR'],
    (1, 0, 1, 4, 0): score['BLOCKED_FOUR'],
    (0, 1, 4, 0, 1): score['BLOCKED_FOUR'],
    (0, 4, 1, 0, 1): score['BLOCKED_FOUR'],
    # 2110111[1]0, 2111101[1]0
    (1, 0, 4, 2, 0): score['BLOCKED_FOUR'],
    (1, 0, 2, 4, 0): score['BLOCKED_FOUR'],
    (0, 2, 4, 0, 1): score['BLOCKED_FOUR'],
    (0, 4, 2, 0, 1): score['BLOCKED_FOUR'],
    # 21110111[1]0, 21111011[1]0
    (1, 0, 4, 3, 0): score['BLOCKED_FOUR'],
    (1, 0, 3, 4, 0): score['BLOCKED_FOUR'],
    (0, 3, 4, 0, 1): score['BLOCKED_FOUR'],
    (0, 4, 3, 0, 1): score['BLOCKED_FOUR'],
    # 211110111[1]0
    (1, 0, 4, 4, 0): score['BLOCKED_FOUR'],
    (0, 4, 4, 0, 1): score['BLOCKED_FOUR'],

    # 一个空点，两个堵点。
    # 当且仅当 count>= 4时，返回眠四
    # Question: 两个堵点与一个堵点的得分一致, 这合理吗?

    # 21[1]0112
    (1, 0, 2, 2, 1): score['BLOCKED_FOUR'],
    (1, 2, 2, 0, 1): score['BLOCKED_FOUR'],
    # 211[1]012, 2[1]01112
    (1, 0, 1, 3, 1): score['BLOCKED_FOUR'],
    (1, 0, 3, 1, 1): score['BLOCKED_FOUR'],
    (1, 0, 2, 3, 1): score['BLOCKED_FOUR'],
    (1, 0, 3, 2, 1): score['BLOCKED_FOUR'],
    (1, 3, 1, 0, 1): score['BLOCKED_FOUR'],
    (1, 1, 3, 0, 1): score['BLOCKED_FOUR'],
    (1, 3, 2, 0, 1): score['BLOCKED_FOUR'],
    (1, 2, 3, 0, 1): score['BLOCKED_FOUR'],
    # 2[1]011110, 2[1]111010
    (1, 0, 4, 1, 1): score['BLOCKED_FOUR'],
    (1, 0, 1, 4, 1): score['BLOCKED_FOUR'],
    (1, 1, 4, 0, 1): score['BLOCKED_FOUR'],
    (1, 4, 1, 0, 1): score['BLOCKED_FOUR'],
    # 2110111[1]0, 2111101[1]0
    (1, 0, 4, 2, 1): score['BLOCKED_FOUR'],
    (1, 0, 2, 4, 1): score['BLOCKED_FOUR'],
    (1, 2, 4, 0, 1): score['BLOCKED_FOUR'],
    (1, 4, 2, 0, 1): score['BLOCKED_FOUR'],
    # 21110111[1]0, 21111011[1]0
    (1, 0, 4, 3, 1): score['BLOCKED_FOUR'],
    (1, 0, 3, 4, 1): score['BLOCKED_FOUR'],
    (1, 3, 4, 0, 1): score['BLOCKED_FOUR'],
    (1, 4, 3, 0, 1): score['BLOCKED_FOUR'],
    # 211110111[1]0
    (1, 0, 4, 4, 1): score['BLOCKED_FOUR'],
    (1, 4, 4, 0, 1): score['BLOCKED_FOUR'],

    # 两个空点
    # TODO: 1.采取 两侧相加 的策略 2.中心为四尚未考虑
    # 无堵点
    # 010[1]010
    (0, 1, 1, 1, 0): score['TWO'] * 2,
    (0, 1, 2, 1, 0): score['THREE'] * 2,
    (0, 1, 3, 1, 0): score['FOUR'],
    # 0110[1]010
    (0, 3, 1, 2, 0): score['BLOCKED_FOUR'] + score['THREE'],
    (0, 2, 1, 3, 0): score['BLOCKED_FOUR'] + score['THREE'],
    (0, 3, 1, 3, 0): score['FOUR'],

    (0, 2, 2, 1, 0): score['BLOCKED_FOUR'] + score['THREE'],
    (0, 1, 2, 2, 0): score['BLOCKED_FOUR'] + score['THREE'],
    (0, 2, 2, 2, 0): score['FOUR'],

    (0, 3, 2, 2, 0): score['FOUR'],
    (0, 2, 2, 3, 0): score['FOUR'],
    (0, 3, 2, 3, 0): score['FOUR'],
    (0, 1, 3, 2, 0): score['FOUR'],
    (0, 2, 3, 1, 0): score['FOUR'],
    (0, 2, 3, 2, 0): score['FOUR'],
    (0, 3, 3, 1, 0): score['FOUR'],
    (0, 1, 3, 3, 0): score['FOUR'],
    (0, 3, 3, 2, 0): score['FOUR'],
    (0, 2, 3, 3, 0): score['FOUR'],
    (0, 3, 3, 3, 0): score['FOUR'],

    # 一个堵点
    # 210[1]010
    (1, 1, 1, 1, 0): score['TWO'] + score['BLOCKED_TWO'],
    (1, 1, 2, 1, 0): score['THREE'] + score['BLOCKED_THREE'],
    (1, 1, 3, 1, 0): score['FOUR'],
    (0, 1, 1, 1, 1): score['TWO'] + score['BLOCKED_TWO'],
    (0, 1, 2, 1, 1): score['THREE'] + score['BLOCKED_THREE'],
    (0, 1, 3, 1, 1): score['FOUR'],

    # 2110[1]010
    (1, 3, 1, 2, 0): score['BLOCKED_FOUR'] + score['THREE'],
    (1, 2, 1, 3, 0): score['BLOCKED_FOUR'] + score['BLOCKED_THREE'],
    (1, 3, 1, 3, 0): score['FOUR'],
    (0, 2, 1, 3, 1): score['BLOCKED_FOUR'] + score['THREE'],
    (0, 3, 1, 2, 1): score['BLOCKED_FOUR'] + score['BLOCKED_THREE'],
    (0, 3, 1, 3, 1): score['FOUR'],

    # 21101[1]010
    (1, 2, 2, 1, 0): score['BLOCKED_FOUR'] + score['THREE'],
    (1, 1, 2, 2, 0): score['BLOCKED_FOUR'] + score['BLOCKED_THREE'],
    (1, 2, 2, 2, 0): score['FOUR'],
    (0, 1, 2, 2, 1): score['BLOCKED_FOUR'] + score['THREE'],
    (0, 2, 2, 1, 1): score['BLOCKED_FOUR'] + score['BLOCKED_THREE'],
    (0, 2, 2, 2, 1): score['FOUR'],

    (1, 3, 2, 2, 0): score['FOUR'],
    (1, 2, 2, 3, 0): score['FOUR'],
    (1, 3, 2, 3, 0): score['FOUR'],
    (1, 1, 3, 2, 0): score['FOUR'],
    (1, 2, 3, 1, 0): score['FOUR'],
    (1, 2, 3, 2, 0): score['FOUR'],
    (1, 3, 3, 1, 0): score['FOUR'],
    (1, 1, 3, 3, 0): score['FOUR'],
    (1, 3, 3, 2, 0): score['FOUR'],
    (1, 2, 3, 3, 0): score['FOUR'],
    (1, 3, 3, 3, 0): score['FOUR'],

    (0, 3, 2, 2, 1): score['FOUR'],
    (0, 2, 2, 3, 1): score['FOUR'],
    (0, 3, 2, 3, 1): score['FOUR'],
    (0, 1, 3, 2, 1): score['FOUR'],
    (0, 2, 3, 1, 1): score['FOUR'],
    (0, 2, 3, 2, 1): score['FOUR'],
    (0, 3, 3, 1, 1): score['FOUR'],
    (0, 1, 3, 3, 1): score['FOUR'],
    (0, 3, 3, 2, 1): score['FOUR'],
    (0, 2, 3, 3, 1): score['FOUR'],
    (0, 3, 3, 3, 1): score['FOUR'],

    # 两个堵点
    # 010[1]010
    (1, 1, 1, 1, 1): score['BLOCKED_TWO'] * 2,
    (1, 1, 2, 1, 1): score['BLOCKED_THREE'] * 2,
    (1, 1, 3, 1, 1): score['FOUR'],
    # 0110[1]010
    (1, 3, 1, 2, 1): score['BLOCKED_FOUR'] + score['BLOCKED_THREE'],
    (1, 2, 1, 3, 1): score['BLOCKED_FOUR'] + score['BLOCKED_THREE'],
    (1, 3, 1, 3, 1): score['FOUR'],

    (1, 2, 2, 1, 1): score['BLOCKED_FOUR'] + score['BLOCKED_THREE'],
    (1, 1, 2, 2, 1): score['BLOCKED_FOUR'] + score['BLOCKED_THREE'],
    (1, 2, 2, 2, 1): score['FOUR'],

    # 双方 count>=4
    (1, 3, 2, 2, 1): score['FOUR'],
    (1, 2, 2, 3, 1): score['FOUR'],
    (1, 3, 2, 3, 1): score['FOUR'],
    (1, 1, 3, 2, 1): score['FOUR'],
    (1, 2, 3, 1, 1): score['FOUR'],
    (1, 2, 3, 2, 1): score['FOUR'],
    (1, 3, 3, 1, 1): score['FOUR'],
    (1, 1, 3, 3, 1): score['FOUR'],
    (1, 3, 3, 2, 1): score['FOUR'],
    (1, 2, 3, 3, 1): score['FOUR'],
    (1, 3, 3, 3, 1): score['FOUR'],


}



class Zobrist:
    def __init__(self):
        self.table = [[[random.getrandbits(64) for _ in range(pp.height)] for _ in range(pp.width)] for _ in
                      range(0, 2)]
        self.code = random.getrandbits(64)

    def do(self, x, y, rule):
        self.code ^= self.table[0][x][y] if rule else self.table[1][x][y]
        return self.code

    def withdraw(self, x, y, rule):
        self.code ^= self.table[0][x][y] if rule else self.table[1][x][y]
        return self.code


class Node:
    def __init__(self, rule=True, depth=0, value=None, threshold=3, move=None):
        self.value = value
        # rule = True 表示 "max", 代表本方落子
        self.rule = rule
        self.depth = depth
        self.threshold = threshold
        self.move = move

    def isLeaf(self):
        return self.depth == self.threshold


class Estimator:
    def __init__(self, cur_board):
        self.board = cur_board
        self.size = (pp.width, pp.height)
        # self.alpha = -float('inf')
        # self.beta = float('inf')
        self.score_1 = ddict(lambda: 0.0)  # 自己得分
        self.score_2 = ddict(lambda: 0.0)  # 对方得分
        self.score_cache = {
            1: {
                'r': ddict(lambda: 0.0),
                'c': ddict(lambda: 0.0),
                'm': ddict(lambda: 0.0),
                'v': ddict(lambda: 0.0)
            },
            2: {
                'r': ddict(lambda: 0.0),
                'c': ddict(lambda: 0.0),
                'm': ddict(lambda: 0.0),
                'v': ddict(lambda: 0.0)
            }
        }
        # row, colomn, main diagonal, vice diagonal 四个方向；类似矩阵中的方向命名。
        self.direct_dict = {
            'r': [(1, 0), (-1, 0)],
            'c': [(0, 1), (0, -1)],
            'm': [(1, -1), (-1, 1)],
            'v': [(1, 1), (-1, -1)]
        }
        self.init_score()
        self.activeMoves = set()
        self.init_activeMoves()

    def init_score(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.board[i][j] == 0:
                    self.score_1[(i, j)] = self.get_point_score(i, j, 1)
                    self.score_2[(i, j)] = self.get_point_score(i, j, 2)
                elif self.board[i][j] == 1:
                    self.score_1[(i, j)] = self.get_point_score(i, j, 1)
                elif self.board[i][j] == 2:
                    self.score_2[(i, j)] = self.get_point_score(i, j, 2)

    def init_activeMoves(self):
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                if self.isFree_and_has_neighbor((x, y)):
                    self.activeMoves.add((x, y))

    def isFree_and_has_neighbor(self, move, dist=DIST):
        x, y = move
        if not self.nowFree(x, y):
            return False
        for i in range(-dist, dist + 1):
            for j in range(-dist, dist + 1):
                if self.nowOccupied(x + i, y + j):
                    return True
        return False

    def update_activeMoves(self, x, y, role, dist=DIST):
        #Ensure the board is updated before this method
        if self.board[x][y] != role:
            self.board[x][y] = role
        if role != 0:
            for i in range(-dist, dist + 1):
                for j in range(-dist, dist + 1):
                    if self.nowFree(x + i, y + j):
                        self.activeMoves.add((x + i, y + j))
            self.activeMoves.discard((x, y))

        else:
            for i in range(-dist, dist + 1):
                for j in range(-dist, dist + 1):
                    if not self.isFree_and_has_neighbor((x + i, y + j)):
                        self.activeMoves.discard((x + i, y + j))
            self.activeMoves.add((x, y))

    def nowFree(self, x, y):
        return x >= 0 and y >= 0 and x < pp.width and y < pp.height and self.board[x][y] == 0

    def nowOccupied(self, x, y):
        return self.board[x][y] != 0

    def now_has_neighbor(self, move, dist=DIST):
        x, y = move
        if not self.nowFree(x, y):
            return False
        for i in range(-dist, dist + 1):
            for j in range(-dist, dist + 1):
                if self.nowOccupied(x + i, y + j):
                    return True
        return False

    def get_moves(self, node):
        move_list = []
        if node.depth != node.threshold:
            for x in range(pp.width):
                for y in range(pp.height):
                    if self.now_has_neighbor((x, y)):
                        move_list.append((x, y))
        return move_list

    def get_successor(self, node, moves=None):
        result = []
        # 若未提供moves
        if not moves:
            moves = self.get_moves(node)

        # 若提供moves, 直接生成
        for move in moves:
            # x, y = move
            gennode = Node(not node.rule, depth=node.depth + 1, value=None,
                           threshold=node.threshold, move=move)
            result.append((move, gennode))
        return result

    def get_point_score(self, x, y, role, direction=None):
        # 完善打分模组
        enemy = 3 - role
        if direction is None:
            target_direct_list = list(self.direct_dict.keys())
        else:
            target_direct_list = [direction]

        ret = 0
        scale = self.size[0]
        for target_direct in target_direct_list:
            direct = self.direct_dict[target_direct]
            # 计数
            count = 0
            # 封堵
            block = [0, 0]
            # 中心连续棋子 # 非中心连续棋子
            cc = [[1, 0], [0, 0]]
            # 空点，两边最多可忍受的空点数目均为1
            empty = [0, 0]
            for k in range(len(direct)):
                i = x
                j = y
                while True:
                    i += direct[k][0]
                    j += direct[k][1]
                    t = self.board[i][j]
                    # 从中心向两边扫描
                    # 堵，退出
                    if i >= scale or j >= scale or i < 0 or j < 0 or t == enemy:
                        block[k] += 1
                        break

                    elif t == role:
                        count += 1
                        cc[empty[k]][k] += 1
                        continue

                    elif empty[k] == 0 and (0 < i < scale - 1 or not direct[k][0]) \
                            and (0 < j < scale - 1 or not direct[k][1]) and \
                            self.board[i + direct[k][0]][j + direct[k][1]] == role:
                        empty[k] = 1
                        continue

                    else:
                        break

            v = 0
            # 未将此情况包含在字典内
            if sum(cc[0]) >= 5:
                v = score['FIVE']
            elif sum(empty) == 2 and sum(cc[0]) == 4:
                v = score['FOUR']
            else:
                key = (block[0], cc[1][0], sum(cc[0]), cc[1][1], block[1])
                if key in scoreDict:
                    v = scoreDict[key]

            self.score_cache[role][target_direct][(x, y)] = v
            ret += v

        return ret

    def get_value(self, node, alpha, beta):
        # 更新
        # if not node.isLeaf():
        if node.move:
            x, y = node.move
            self.board[x][y] = 2 if node.rule else 1
            self.update_point_score(x, y, self.board[x][y])
            self.update_activeMoves(x, y, self.board[x][y])

        if node.isLeaf():
            # 叶节点没有对应着法
            value, best_move = self.evaluate(node.rule), None
        else:
            if node.rule:
                value, best_move = self.max_value(node, alpha, beta)
            else:
                value, best_move = self.min_value(node, alpha, beta)

        # if not node.isLeaf():
        if node.move:
            x, y = node.move
            self.board[x][y] = 0
            self.update_point_score(x, y, 0)
            self.update_activeMoves(x, y, 0)

        return value, best_move

    # MINIMAX
    def max_value(self, node, alpha, beta):
        v = float('-inf')
        best_move = None
        # moves = self.get_moves(node)
        # moves.sort(key=lambda t: max(self.score_1[t], self.score_2[t]), reverse=True)
        moves = self.get_candidates(brunch=20)

        # 新尝试：卡分+三循环：
        for move in moves:
            if max(self.score_1[move], self.score_2[move]) < score['FIVE']:
                break
            elif self.score_1[move] > score['FIVE']:
                return 20000000000, move

        for move in moves:
            if max(self.score_1[move], self.score_2[move]) < score['FIVE']:
                break
            elif self.score_2[move] > score['FIVE']:
                c = Node(not node.rule, depth=node.depth + 1, value=None,
                         threshold=node.threshold, move=move)
                return self.get_value(c, alpha, beta)[0], move

        for move in moves:
            if max(self.score_1[move], self.score_2[move]) < score['FOUR']:
                break
            elif self.score_1[move] > score['FOUR']:
                return 10000000000, move

        b = branch[node.depth]
        successors = self.get_successor(node, moves=moves[: b])

        for _, child in successors:
            tmp_v, tmp_m = self.get_value(child, alpha, beta)[0], child.move
            if tmp_v > v:
                v, best_move = tmp_v, tmp_m
            if v >= beta:
                return v, best_move
            alpha = max(alpha, v)
        return v, best_move

    def min_value(self, node, alpha, beta):
        v = float('inf')
        best_move = None
        # moves = self.get_moves(node)
        # moves.sort(key=lambda t: max(self.score_1[t], self.score_2[t]), reverse=True)
        moves = self.get_candidates(brunch=20)
        # 新尝试：卡分+三循环：
        for move in moves:
            if max(self.score_1[move], self.score_2[move]) < score['FIVE']:
                break
            elif self.score_2[move] > score['FIVE']:
                return -20000000000, move

        for move in moves:
            if max(self.score_1[move], self.score_2[move]) < score['FIVE']:
                break
            elif self.score_1[move] > score['FIVE']:
                c = Node(not node.rule, depth=node.depth + 1, value=None,
                         threshold=node.threshold, move=move)
                return self.get_value(c, alpha, beta)[0], move

        for move in moves:
            if max(self.score_1[move], self.score_2[move]) < score['FOUR']:
                break
            elif self.score_2[move] > score['FOUR']:
                return -10000000000, move

        b = branch[node.depth]
        successors = self.get_successor(node, moves=moves[: b])

        for _, child in successors:
            tmp_v, tmp_m = self.get_value(child, alpha, beta)[0], child.move
            if tmp_v < v:
                v, best_move = tmp_v, tmp_m
            if v <= alpha:
                return v, best_move
            beta = min(beta, v)
        return v, best_move

    def evaluate(self, rule):
        max_score_1 = 0
        max_score_2 = 0
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.board[i][j] == 1:
                    # TODO：能不能抛弃卡分函数
                    # max_score_1 += self.fix_evaluation(self.score_1[(i, j)], i, j, 1)
                    max_score_1 += self.score_1[(i, j)]
                elif self.board[i][j] == 2:
                    # max_score_2 += self.fix_evaluation(self.score_2[(i, j)], i, j, 2)
                    max_score_2 += self.score_2[(i, j)]
        ratio = 1 - RATIO if rule else 1 + RATIO
        result = max_score_1 - ratio * max_score_2
        return result

    def update_point_score(self, x, y, role, radius=6):
        scale = self.size[0]
        for target_direct in list(self.direct_dict.keys()):
            direct = self.direct_dict[target_direct][0]
            for w in (-1, 1):
                block_1 = block_2 = False
                for r in range(1, radius + 1):
                    i = x + direct[0] * w * r
                    j = y + direct[1] * w * r
                    if i < 0 or j < 0 or i >= scale or j >= scale:
                        break
                    if not block_1:
                        if self.board[i][j] == 2:
                            block_1 = True
                        else:
                            self.quick_update_function(i, j, board[i][j], target_direct)
                    if not block_2:
                        if self.board[i][j] == 1:
                            block_2 = True
                        else:
                            self.quick_update_function(i, j, board[i][j], target_direct)
        self.update_function(x, y, role)

    # BLU
    def quick_update_function(self, x, y, role, direction):
        if role != 2:
            self.score_1[(x, y)] -= self.score_cache[1][direction][(x, y)]
            self.score_1[(x, y)] += self.get_point_score(x, y, 1, direction)
        if role != 1:
            self.score_2[(x, y)] -= self.score_cache[2][direction][(x, y)]
            self.score_2[(x, y)] += self.get_point_score(x, y, 2, direction)

    def update_function(self, x, y, role):
        # direction是冗余的
        if role == 0:
            self.score_1[(x, y)] = self.get_point_score(x, y, 1)
            self.score_2[(x, y)] = self.get_point_score(x, y, 2)
        if role == 1:
            self.score_2[(x, y)] = 0
            # 这里可以直接在字典中取值？
            # self.score_1[(x, y)] = self.get_point_score(x, y, 1)
        if role == 2:
            self.score_1[(x, y)] = 0
            # self.score_2[(x, y)] = self.get_point_score(x, y, 2)

    def get_candidates(self, brunch = BRUNCH):
        moves = list(self.activeMoves)
        moves.sort()
        moves.sort(key=lambda t: max(self.score_1[t], self.score_2[t]), reverse=True)
        return moves[:brunch]

    def is_five(self, x, y, role):
        scale = self.size[0]
        directs = list(self.direct_dict.values())
        for direct in directs:
            count = 1
            for k in range(len(direct)):
                i = x + direct[k][0]
                j = y + direct[k][1]
                while True:
                    if i >= scale or j >= scale or i < 0 or j < 0 or self.board[i][j] != role:
                        break
                    else:
                        count += 1
                        i += direct[k][0]
                        j += direct[k][1]
            if count >= 5:
                return True
        return False

    def get_winner(self):
        for i in range(pp.width):
            for j in range(pp.height):
                role = self.board[i][j]
                if role and self.is_five(i, j, role):
                    return role
        return False

    # def checkmate(self, role, checkmate_depth):
    #     return self.checkmate_MAX(role, 0, checkmate_depth)
    #
    # def checkmate_MAX(self, role, depth, checkmate_depth):
    #     winner = self.get_winner()
    #     if winner == role:
    #         return True
    #     elif winner == 3 - role or depth > checkmate_depth:
    #         return False
    #     if depth == 0:
    #         if role == 1 and max(self.score_2.values()) >= score['FIVE']:
    #             return False
    #         elif role == 2 and max(self.score_1.values()) >= score['FIVE']:
    #             return False
    #
    #     moves = self.get_candidates()
    #     for move in moves:
    #         x, y = move
    #         point_role_score = self.score_1[(x, y)] if role == 1 else self.score_2[(x, y)]
    #         for i in range(pp.width):
    #             for j in range(pp.height):
    #                 if (role == 1 and self.score_2[(i,j)] >= score['FIVE']) or (role == 2 and self.score_1[(i,j)] >= score['FIVE']):
    #                     return False
    #         if point_role_score >= 2 * score['THREE']:
    #             self.board[x][y] = role
    #             self.update_point_score(x, y, role)
    #             self.update_activeMoves(x, y, role)
    #             m = self.checkmate_MIN(role, depth + 1, checkmate_depth)
    #             self.board[x][y] = 0
    #             self.update_point_score(x, y, 0)
    #             self.update_activeMoves(x, y, 0)
    #             if m:
    #                 if depth == 0:  # 可以斩杀
    #                     return move
    #                 else:
    #                     return True
    #     return False
    #
    # def checkmate_MIN(self, role, depth, checkmate_depth):
    #     winner = self.get_winner()
    #     if winner == role:
    #         return True
    #     elif winner == 3 - role or depth > checkmate_depth:
    #         return False
    #
    #     cand = []
    #     moves = self.get_candidates()
    #     for move in moves:
    #         x, y = move
    #         if self.score_2[(x, y)] + self.score_1[(x, y)] >= score['BLOCKED_FOUR']:
    #             self.board[x][y] = 3 - role  # opponent
    #             self.update_point_score(x, y, 3 - role)
    #             self.update_activeMoves(x, y, 3 - role)
    #             m = self.checkmate_MAX(role, depth + 1, checkmate_depth)
    #             self.board[x][y] = 0
    #             self.update_point_score(x, y, 0)
    #             self.update_activeMoves(x, y, 0)
    #             if m:
    #                 cand.append((x, y))
    #             else:
    #                 return False
    #     if cand:
    #         return random.choice(cand)
    #     else:
    #         return False

    def checkmate(self, role, rule=1, depth=0, threshold=DEPTH):
        # input : rule = 1代表对proof number取min,对disproof number取num,rule = 0则相反
        # output : p,dp:represent proof number and disproof number respectively
        # 先检查局面是否有人赢了
        winner = self.get_winner()
        if winner == 1:
            return [0, float('inf')]
        elif winner == 2:
            return [float('inf'), 0]

        # 当达到threshold时仍然没有分出胜负
        if (depth == threshold):
            return [1, 1]

        son_list = []
        move_list = []
        activeMoveList = self.get_candidates(brunch=BRUNCH)
        for move in activeMoveList:
            x, y = move
            point_role_score = self.score_1[(x, y)] if role == 1 else self.score_2[(x, y)]
            point_enemy_score = self.score_1[(x, y)] if role == 2 else self.score_2[(x, y)]
            # 先防守
            if point_enemy_score >= score['BLOCKED_FOUR']:
                self.board[x][y] = role
                self.update_point_score(x, y, role)
                self.update_activeMoves(x, y, role)

                m = self.checkmate(3 - role, 1 - rule, depth + 1, threshold)
                son_list.append(m)
                move_list.append(move)

                self.board[x][y] = 0
                self.update_point_score(x, y, 0)
                self.update_activeMoves(x, y, 0)

                continue

            # 进攻
            if point_role_score >= 2 * score['THREE']:
                self.board[x][y] = role
                self.update_point_score(x, y, role)
                self.update_activeMoves(x, y, role)

                m = self.checkmate(3 - role, 1 - rule, depth + 1, threshold)
                son_list.append(m)
                move_list.append(move)

                self.board[x][y] = 0
                self.update_point_score(x, y, 0)
                self.update_activeMoves(x, y, 0)

        def my_min(inputlist, i):
            minn = float('inf')
            for ele in inputlist:
                if ele[i] < minn:
                    minn = ele[i]
            return minn

        def my_sum(inputlist, i):
            summ = 0
            for ele in inputlist:
                summ = summ + ele[i]
            return summ

        if len(son_list) == 0:
            if depth == 0:
                return (None, 0)
            else:
                return [1, 1]
        else:
            ans = [1, 1]
            if rule == 1:
                ans[0] = my_min(son_list, 0)
                ans[1] = my_sum(son_list, 1)
            else:
                ans[0] = my_sum(son_list, 0)
                ans[1] = my_min(son_list, 1)
            if depth != 0:
                return ans
            else:
                # return_move_list存的是不一定被必杀的move
                must = 0
                # num 代表活路的个数
                num = 0
                return_move_list = []
                for idx, son in enumerate(son_list):
                    if son[1] > 0:
                        return_move_list.append(move_list[idx])
                        num = num + 1
                    if son[0] == 0:
                        return ([move_list[idx]], 1)
                if num == 1 and len(move_list) >= 2:
                    must = 1
                return (return_move_list, must)

def choose_move(cur_board):
    esti = Estimator(cur_board)    
    win_move, flag = esti.checkmate(role = 1, threshold = DEPTH)
    if flag:
        return win_move[0]
    best_move = [8, 6]
    root_node = Node(rule=True, depth=0, value=None, threshold=THRESHOLD)
    _, move = esti.get_value(node=root_node, alpha=-float('inf'), beta=float('inf'))
    if move:
        best_move = move
    return best_move

# def choose_move(cur_board):
#     root_node = Node(rule=True, depth=0, value=None, threshold=THRESHOLD)
#     # best_value = -float('inf')
#     best_move = [8, 6]
#     esti = Estimator(cur_board)
#     _, move = esti.get_value(node=root_node, alpha=-float('inf'), beta=float('inf'))
#     if move:
#         best_move = move
#     x, y = best_move
#     return x, y

