from typing import Tuple
import random
import pisqpipe as pp
from collections import defaultdict as ddict
import math

e = 0.5#乱下的概率
e_switch = 1#开启e_switch,加入随机性，避免局部最优
DIST = 1
branch = 16#分支因子
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

#1是我方2是敌方
class Node:#节点，用于构造树结构
    """MCTS树中的节点
    属性:
    parent:节点的父节点，也是一个node
    action_child_dict: ——< action:子节点(也是节点)>
    Visit_count:该节点被访问的次数
    每个节点保持自己的值Q，以及其开发-探索平衡常数
    """
    def __init__(self, parent, role):
        self.parent = parent
        self.action_child_dict = dict()  # 存子节点<key : value> = <action : nextboard(also a Node)> 
        self.visit_count = 0   # 该节点被访问次数
        self.Q = 0  # its own value，节点的当前胜率估计
        self.u = 0 #uct加号右半部分的值
        self.role = role
    
    def is_leaf(self):
        return len(self.action_child_dict) == 0

    def is_root(self):
        return self.parent is None

    def Select(self, c_puct):
        return max(self.action_child_dict.items(),
                   key=lambda x: x[1].get_value(c_puct))
        #返回的是一个键值对
        # self.action_child_dict is a dict
        # act_node[1].get_value will return the action with max Q+u and corresponding board
    
    def Expand(self, action):
        if action not in self.action_child_dict.keys():
            self.action_child_dict[action] = Node(self, 3 - self.role)
        # Expand all children that under this board
       
    def BackPropagation(self, leaf_value):
        # If it is not root, this node's parent should be updated first.
        if self.parent:
            self.parent.BackPropagation(1.0 - leaf_value)
        self.visit_count += 1
        # there is a simple equation: (v+n*Q)/(n+1) = Q + (v-Q)/(n+1)
        self.Q += (leaf_value - self.Q) / self.visit_count

    def get_total_count(self):
        if self.is_root():
            return self.visit_count
        return self.parent.get_total_count() #这个状态的总次数
    
    def get_value(self, c_puct):#计算ucb
        """计算节点的值。
        参数:
        C_puct: (0, inf)中的一个数字，控制勘探和开发的相对影响
        返回:
        一个元组(action, next_node)，最佳操作和相关节点
        """
        total_count = self.get_total_count()
        if self.visit_count == 0:
            self.u = 9999999
        else:
            self.u = c_puct * math.sqrt(2 * math.log(total_count)/self.visit_count)
        return self.Q + self.u

class MCTS:#MCTS方法with utc
    def __init__(self, board, c, simulation_times):
        self.size = (pp.width, pp.height)
        self.board = board
        self.root = Node(parent=None, role = 1)
        self.c_puct = c
        self.Simulation_times = simulation_times# times of tree search
        # root node do not have parent ,and sure with prior probability 1
        self.score1 = ddict(lambda: 0)  # Our score
        self.score2 = ddict(lambda: 0)  # Enemy's score
        self.direct_dict = {
            'R': [(1, 0), (-1, 0)],
            'C': [(0, 1), (0, -1)],
            'M': [(1, -1), (-1, 1)],
            'V': [(1, 1), (-1, -1)]
        }
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
        self.init_score()
        self.activemoves = self.get_moves()

    #为了减小expand的空间，采取较大的评分点
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
                    if i >= scale or j >= scale or i < 0 or j < 0:
                        block[k] += 1
                        break
                    t = self.board[i][j]
                    if t == enemy:
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

    def update_point_score(self, x, y, player, radius=6):#更改点需要调用
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

    def quick_update(self, x, y, player, direction):#for update_point_score
        #Quick update for one direction
        if player != 2:
            self.score1[(x, y)] -= self.direct_cache[1][direction][(x, y)]
            self.score1[(x, y)] += self.point_score(x, y, 1, direction)
        if player != 1:
            self.score2[(x, y)] -= self.direct_cache[2][direction][(x, y)]
            self.score2[(x, y)] += self.point_score(x, y, 2, direction)

    def update(self, x, y, player):#更改自己
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

    def has_neighbor(self, x, y, dist=DIST):
        for i in range(-dist if x - dist >= 0 else -x, dist + 1 if x + dist < self.size[0] else self.size[0] - x):
            for j in range(-dist if y - dist >= 0 else -y, dist + 1 if y + dist < self.size[1] else self.size[1] - y):
                if self.isOccupied(x + i, y + j):
                    return True
        return False
        
    def get_moves(self): #获得较近的合理下点, 取评分前branch个
        action = []
        x_list = [0 for i in range(self.size[0])]
        for x in range(self.size[0]):
            x_list[x] = 1 if sum(self.board[x]) != 0 else 0    
        for i in range(self.size[0]):
            if x_list[i] == 0:
                if x_list[i-1] == 1 and i-1 >= 0:
                    x_list[i] += 1
                elif x_list[i+1] == 1 and i+1 < self.size[0]:
                    x_list[i] += 1
        for x in range(self.size[0]):
            if x_list[x] != 0:
                for y in range(self.size[1]):
                    if self.isFree(x, y):
                        if self.has_neighbor(x, y):
                            action.append((x, y))
        action.sort(key=lambda n: max(self.score1[n], self.score2[n]), reverse=True)
        return action[:branch]

    def seek_must(self):#找必要走的棋子
        moves1 = []
        moves2 = []
        moves3 = []
        for action in self.activemoves:
            x, y = action
            if self.isFree(x, y):
                if self.score1[(x, y)] >= score_map["FIVE"]:
                        return (x, y)
                elif self.score2[(x, y)] >= score_map["FIVE"]:
                        moves1.append((x, y))
                elif self.score1[(x, y)] >= score_map["FOUR"]:
                        moves2.append((x, y))
                elif self.score2[(x, y)] >= score_map["FOUR"]:
                        moves3.append((x, y))
        # Choose the move with biggest score1
        if moves1:
            return max(moves1, key=lambda n: self.score2[(n[0], n[1])])
        elif moves2:
            return max(moves2, key=lambda n: self.score1[(n[0], n[1])])
        elif moves3:
            return max(moves3, key=lambda n: self.score2[(n[0], n[1])])
        return False

    def isFree(self, x, y):#是不是空的
        return self.board[x][y] == 0

    def isOccupied(self, x, y):#是不是有位置了
        return self.board[x][y] != 0

    def get_winner(self):#有胜者则找到胜者
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                if self.isOccupied(x, y):
                    if self.score1[(x, y)] >= score_map["FIVE"]:
                        return 1
                    elif self.score2[(x, y)] >= score_map["FIVE"]:
                        return 2
        return False

    def make_move(self): #获得最终的落子点
        move = self.seek_must() 
        if move:
            return move
        else:#没有必须下的点就用uct找
            moves = self.activemoves #我们只用棋型评估找出初始的选择范围，而不是选哪个，选哪个是贪心时根据ucb值决定或者随机决定
            while self.root.visit_count<=self.Simulation_times:
                for move in moves:
                    self.root.Expand(move)
                action, node = self.Treepolicy()
                self.Simulation(state = node, move = action)
            return self.root.Select(self.c_puct)[0] if moves else None

    def is_full(self):#场上下满了吗，判断平局
        if len(self.activemoves):
            return False
        return True

    def is_teriminal(self):#结束了吗？胜负平
        winner = self.get_winner()
        if winner:
            return winner    
        else:
            return -1 if self.is_full() else False

    def add_move(self, move, role, radius = 5):#加一颗子改变board、改存值、维护activemoves 
        x, y = move
        self.board[x][y] = role
        self.activemoves.remove((x, y))
        self.update_point_score(x, y, role)#改存值
        scale = self.size[0]#维护activemoves, 旧的activemoves其实是当前节点的子节点
        for target_direct in list(self.direct_dict.keys()):
            direct = self.direct_dict[target_direct][0]
            for w in (-1, 1):
                flag = 0
                for r in range(1, radius + 1):#radius是5，扩展5个
                    i = x + direct[0] * w * r
                    j = y + direct[1] * w * r
                    if i < 0 or j < 0 or i >= scale or j >= scale:
                        break
                    if self.board[i][j] != role:#有异色子隔绝了影响，就break换方向
                        break
                    elif self.board[i][j] == 0:
                        flag += 1
                        if flag > 2:#第二个空格之后值不更新了，也就不算进activemove里面去了
                            break
                        self.activemoves.append((i,j))         
        self.activemoves.sort(key=lambda n: max(self.score1[n], self.score2[n]), reverse=True)
        self.activemoves = self.activemoves[:branch]
    
    def Treepolicy(self):
        for i in self.root.action_child_dict.items():
            if len(i[1].action_child_dict.items()) == 0:
                return i
        else:
            return self.root.Select(self.c_puct)

    def Simulation(self, state, move): #e-greedy
        self.add_move(move, 3 - state.role)#加一步形成state
        if not state.is_leaf():#不是叶节点说明它已经有子节点了
            new_move, new_state = state.Select(self.c_puct)
        else:#是叶节点，先判断结束了吗
            flage = self.is_teriminal()
            if flage:
                if flage == -1:#平局
                    state.BackPropagation(0.5)
                elif flage == state.role:#下输了+0
                    state.BackPropagation(1)
                else:
                    state.BackPropagation(0)#下赢了+1
                self.withdraw_move(move, state)
                return None
            #没结束，说明可以拓展
            must = self.seek_must() 
            if must:
                state.Expand(must)
                new_state = state.action_child_dict[must]
                new_move = must
            else:
                moves = self.activemoves
                for i in moves:
                    state.Expand(i)
                if e_switch:#e-greedy
                    a = random.uniform(0, 1) 
                    if a <= 1-e:#有1-e的概率贪心
                        new_move, new_state = state.Select(self.c_puct)
                    else:#e的概率随机
                        new_move = self.activemoves[random.randint(0, len(self.activemoves)-1)]
                        new_state = state.action_child_dict[new_move]
                else:#greedy
                    new_move, new_state = state.Select(self.c_puct)
        self.Simulation(new_state, new_move)
        self.withdraw_move(move, state)
        return None

    def withdraw_move(self, move, state):#撤销形成state的一步
        x, y = move
        self.board[x][y] = 0
        self.activemoves = list(state.parent.action_child_dict.keys())
        self.update_point_score(x, y, 0)


def take_action(board): #选择落点函数，调用类
    mct = MCTS(board, c=math.sqrt(2), simulation_times=160)
    move = mct.make_move()
    return move
