import random
import pisqpipe as pp
import win32api

# 棋形
win, flex4, block4, flex3, block3, flex2, block2 = 7, 6, 5, 4, 3, 2, 1
max_size = 20  # 棋盘最大尺寸
max_branch = 8  # 最大分支数
hash_size = 1 << 22  # 哈希表大小
pvs_size = 1 << 20  # pvs置换表大小
max_depth = 6  # 最大搜索深度
min_depth = 2  # 最小搜索深度
offen_coef = 1.2  # 进攻系数

hash_exact = 0
hash_alpha = 1
hash_beta = 2
unknown = -20000

# 点的状态，取0,1方便异或操作
White = 0
Black = 1
Empty = 2
Outsider = 3

# 四个方向
dx = [1, 0, 1, 1]
dy = [0, 1, 1, -1]


# 类定义
class Point:
    """点的位置和分值"""

    def __init__(self, val=0):
        self.pos = [0, 0]
        self.val = val


class Unit:
    """棋盘上的点的状态"""

    def __init__(self):
        self.role = 0
        self.nei = 0  # 邻居数量(两格)
        self.pattern = [[0 for _ in range(4)] for _ in range(2)]


class PV:
    """principal variation 主变量"""

    def __init__(self):
        self.key = 0
        self.best = [0, 0]


class Path:
    """下棋路径"""

    def __init__(self):
        self.n = 0
        self.moves = [[0, 0] for _ in range(max_depth)]


class MoveList:
    """可能的走法"""

    def __init__(self):
        self.phase = 0  # 谁下的
        self.n = 0
        self.index = 0
        self.first = False  # 是否是第一个
        self.hash_move = [0, 0]
        self.moves = [[0, 0] for _ in range(64)]


step = 0  # 行棋数
zobristkey = 0  # 当前zobrist键值
board = [[Unit() for _ in range(max_size + 8)] for _ in range(max_size + 8)]  # 将每一点变为Unit，并拓展棋盘
moved = [[0, 0] for _ in range(max_size * max_size)]  # 记录已下位置
cand = [Point() for _ in range(400)]  # 候选点
my = Black
opp = White
root_move = [Point() for _ in range(64)]  # 根节点走法
root_count = 0  # 根节点走法总数


def get_time():
    """返回已用的时间"""
    return win32api.GetTickCount() - pp.start_time


def stop_time():
    """返回每步可用的时间"""
    return min(pp.info_timeout_turn, pp.info_time_left / 7)


# zobrist置换表
class Hash:
    """哈希表"""

    def __init__(self, key=0, depth=0, hashf=0, val=0):
        self.key = key
        self.depth = depth
        self.hashf = hashf
        self.val = val


def search_hash(depth, alpha, beta):
    """查询zobrist置换表"""
    global hashtable, zobristkey
    hash_ele: Hash = hashtable[zobristkey & (hash_size - 1)]
    if hash_ele:
        if hash_ele.key == zobristkey:
            if hash_ele.depth >= depth:
                if hash_ele.hashf == hash_exact:
                    return hash_ele.val
                elif hash_ele.hashf == hash_alpha and hash_ele.val <= alpha:
                    return hash_ele.val
                elif hash_ele.hashf == hash_beta and hash_ele.val >= beta:
                    return hash_ele.val
    return unknown


def write_hash(depth, val, hashf):
    """写入zobrist置换表"""
    global hashtable, zobristkey
    hash_ele = Hash(zobristkey, depth, hashf, val)
    hashtable[zobristkey & (hash_size - 1)] = hash_ele


# 初始化一些变量
def init_zobrist():
    """初始化zobrist置换表"""
    zobrist = [[[0 for _ in range(max_size + 4)] for _ in range(max_size + 4)] for _ in range(2)]
    for i in range(max_size + 4):
        for j in range(max_size + 4):
            zobrist[0][i][j] = random.getrandbits(64)
            zobrist[1][i][j] = random.getrandbits(64)
    return zobrist


def evaluate_assist(length, dist, count, block):
    """
    通过提取的数据判断属于哪种棋形
    @param length: 总长度
    @param dist: 自己的距离
    @param count: 连续长度
    @param block: 是否堵
    @return: value: 对应的棋形
    """
    if length >= 5 and count > 1:
        if count == 5:
            return win
        if length > 5 and dist < 5 and block == 0:
            if count == 2:
                return flex2
            if count == 3:
                return flex3
            if count == 4:
                return flex4
        else:
            if count == 2:
                return block2
            if count == 3:
                return block3
            if count == 4:
                return block4
    return 0


def create_evalute_table():
    """打成表，快速判断"""
    evalute_table = [[[[0 for _ in range(3)] for _ in range(6)] for _ in range(6)] for _ in range(10)]
    for i in range(10):
        for j in range(6):
            for k in range(6):
                for l in range(3):
                    evalute_table[i][j][k][l] = evaluate_assist(i, j, k, l)
    return evalute_table


def short_path(path):
    """在一个方向上提取特征"""
    empty = block = 0
    length = dist = count = 1
    my = path[4]
    for k in range(5, 9):
        if path[k] == my:
            if empty + count > 4:
                break
            count += 1
            length += 1
            dist = empty + count
        elif path[k] == Empty:
            length += 1
            empty += 1
        else:
            if path[k - 1] == my:
                block += 1
            break
    empty = dist - count
    for k in range(3, -1, -1):
        if path[k] == my:
            if empty + count > 4:
                break
            count += 1
            length += 1
            dist = empty + count
        elif path[k] == Empty:
            length += 1
            empty += 1
        else:
            if path[k + 1] == my:
                block += 1
            break
    return evalute_table[length][dist][count][block]


def path_type(role, key):
    """判断key的棋形"""
    path_left = [0] * 9
    path_right = [0] * 9

    for i in range(9):
        if i == 4:
            path_left[i] = role
            path_right[i] = role
        else:
            path_left[i] = key & 3
            path_right[8 - i] = key & 3
            key >>= 2

    #  两边的棋形
    p1 = short_path(path_left)
    p2 = short_path(path_right)

    #  如果都是眠三，有可能合起来是双三，重新检测
    if p1 == block3 and p2 == block3:
        for i in range(9):
            if path_left[i] == Empty:
                path_left[i] = role

                five = count_five(path_left, role)

                path_left[i] = Empty
                if five >= 2:
                    return flex3
        return block3
    #  如果都是眠四，有可能是活四，重新检测
    elif p1 == block4 and p2 == block4:
        five = count_five(path_left, role)
        return flex4 if five >= 2 else block4

    #  返回最大值
    else:
        return p1 if p1 > p2 else p2


def count_five(path, role):
    five = 0
    for i in range(9):
        if path[i] == Empty:
            count = 0
            j = i - 1
            while j >= 0 and path[j] == role:
                count += 1
                j -= 1
            j = i + 1
            while j <= 8 and path[j] == role:
                count += 1
                j += 1
            if count >= 4:
                five += 1
    return five


def create_pattern_table():
    """棋形表"""
    pattern_table = [[0 for _ in range(2)] for _ in range(65536)]
    for i in range(65536):
        pattern_table[i][0] = path_type(0, i)  # 自己的
        pattern_table[i][1] = path_type(1, i)
    return pattern_table


def get_pval(a, b, c, d):
    """走法评分"""
    type = [0] * 8
    # 四个方向上的情况
    type[a] += 1
    type[b] += 1
    type[c] += 1
    type[d] += 1

    # 必胜点
    if type[win] > 0:
        return 5000
    # 活四或双冲四
    if type[flex4] > 0 or type[block4] > 1:
        return 1200
    # 活四冲四
    if type[block4] > 0 and type[flex4] > 0:
        return 1000
    # 双活三
    if type[flex3] > 1:
        return 200

    # 其他情况
    val = [0, 2, 5, 5, 12, 12]
    score = 0
    for i in range(1, block4 + 1):
        score += val[i] * type[i]

    return score


def create_pval():
    """走法评分表"""
    pval_table = [[[[0 for _ in range(8)] for _ in range(8)] for _ in range(8)] for _ in range(8)]
    for i in range(8):
        for j in range(8):
            for k in range(8):
                for l in range(8):
                    pval_table[i][j][k][l] = get_pval(i, j, k, l)
    return pval_table


def get_key(x, y, i):
    step_x = dx[i]
    step_y = dy[i]
    # 通过异或操作获取序列
    key = board[x - step_x * 4][y - step_y * 4].role ^ \
          (board[x - step_x * 3][y - step_y * 3].role << 2) ^ \
          (board[x - step_x * 2][y - step_y * 2].role << 4) ^ \
          (board[x - step_x * 1][y - step_y * 1].role << 6) ^ \
          (board[x + step_x * 1][y + step_y * 1].role << 8) ^ \
          (board[x + step_x * 2][y + step_y * 2].role << 10) ^ \
          (board[x + step_x * 3][y + step_y * 3].role << 12) ^ \
          (board[x + step_x * 4][y + step_y * 4].role << 14)
    return key


def update_type(x, y):
    for i in range(4):
        for j in range(-4, 5):
            a = x + j * dx[i]
            b = y + j * dy[i]
            if board[a][b].role != Outsider:
                key = get_key(a, b, i)
                board[a][b].pattern[0][i] = pattern_table[key][0]
                board[a][b].pattern[1][i] = pattern_table[key][1]


def initialize(_size):
    global evalute_table, pattern_table, pval_table, zobrist
    global size, board_start, board_end, board

    size = _size
    board_start, board_end = 4, size + 4
    for i in range(max_size + 8):
        for j in range(max_size + 8):
            if i < 4 or i >= board_end or j < 4 or j >= board_end:
                board[i][j].role = Outsider
            else:
                board[i][j].role = Empty

    evalute_table = create_evalute_table()
    pattern_table = create_pattern_table()
    zobrist = init_zobrist()
    pval_table = create_pval()


def move(next):
    """落子在next处"""
    global my, opp, board, zobristkey, zobrist, step
    x, y = next
    board[x][y].role = my
    zobristkey ^= zobrist[my][x][y]
    my ^= 1
    opp ^= 1
    moved[step] = next
    step += 1

    update_type(x, y)
    for i in range(x - 2, x + 3):
        for j in range(y - 2, y + 3):
            board[i][j].nei += 1


def remove():
    """回溯一步棋"""
    global my, opp, board, zobristkey, zobrist, step
    # 先对index复原
    step -= 1
    x, y = moved[step]
    my ^= 1
    opp ^= 1
    board[x][y].role = Empty
    zobristkey ^= zobrist[my][x][y]

    update_type(x, y)
    for i in range(x - 2, x + 3):
        for j in range(y - 2, y + 3):
            board[i][j].nei -= 1


def restart():
    """重新开始"""
    global hashtable, pvstable, step
    hashtable = [0 for _ in range(hash_size)]
    pvstable = [0 for _ in range(pvs_size)]
    while step:
        remove()


def put_chess(next):
    """从棋盘上获取下棋点"""
    x, y = next
    move([x + 4, y + 4])


def is_win():
    """检查最后一步四个方向上是否获胜"""
    c = board[moved[step - 1][0]][moved[step - 1][1]]
    return c.pattern[opp][0] == win or c.pattern[opp][1] == win or c.pattern[opp][2] == win or c.pattern[opp][3] == win


search_depth = 0
best_point = Point()
stop = False


def solve():
    best = search()[:]
    return [best[0] - 4, best[1] - 4]


def search():
    global search_depth, stop, is_lost, best_point, size
    best_move = [0, 0]
    if step == 0:
        best_move[0] = size // 2 + 4
        best_move[1] = size // 2 + 4
        return best_move
    if step <= 2:
        x = moved[0][0] + random.randint(0, step * 2) - step
        y = moved[0][1] + random.randint(0, step * 2) - step
        while board[x][y].role == Outsider or board[x][y].role != Empty:
            x = moved[0][0] + random.randint(0, step * 2) - step
            y = moved[0][1] + random.randint(0, step * 2) - step
        return [x, y]

    stop = False
    best_point.val = 0
    is_lost = [[False for _ in range(max_size + 4)] for _ in range(max_size + 4)]
    # 迭代加深
    for i in range(min_depth, max_depth + 1, 2):
        if stop:
            break
        search_depth = i
        best_point = root_search(search_depth, -10001, 10000)
        if stop or (search_depth >= 10 and get_time() >= 1000 and get_time() * 12 > stop_time()):
            break
    best_move = best_point.pos[:]
    return best_move


def root_search(depth, alpha, beta):
    """从根节点开始搜索"""
    global root_count, is_lost, root_move, stop
    best = Point(val=root_move[0].val)
    best.pos = root_move[0].pos[:]

    if depth == min_depth:
        moves = [[0, 0] for _ in range(64)]
        root_count = get_moves(moves)
        if root_count == 1:
            stop = True
            best.pos = moves[0]
            best.val = 0
            return best

        for i in range(root_count):
            root_move[i].pos = moves[i][:]
    else:
        for i in range(root_count):
            # 把最大的排到最前
            if root_move[i].val > root_move[0].val:
                root_move[0], root_move[i] = root_move[i], root_move[0]

    # 遍历
    val = 0
    update_best = False
    for i in range(root_count):
        p = root_move[i].pos[:]
        if not is_lost[p[0]][p[1]]:
            move(p)
            for _ in range(1):
                if i > 0 and alpha + 1 < beta:
                    val = -alpha_beta(depth - 1, -alpha - 1, -alpha)
                    if val <= alpha or val >= beta:
                        break
                val = -alpha_beta(depth - 1, -beta, -alpha)
            remove()

            root_move[i].val = val

            if stop:
                break

            if val == -10000:
                is_lost[p[0]][p[1]] = True

            if val > alpha:
                alpha = val
                best.pos = p[:]
                best.val = val
                update_best = True

                # 必胜
                if val == 10000:
                    stop = True
                    return best

    return best if update_best else root_move[0]


cnt = 1000


def alpha_beta(depth, alpha, beta):
    global stop
    global cnt
    cnt -= 1
    if cnt <= 0:
        cnt = 1000
        if get_time() + 50 >= stop_time():
            stop = True
            return alpha
    # 别人胜利
    if is_win():
        return -10000
    # 达到最大深度
    if depth <= 0:
        return evaluate()

    # 从zobrist中读值
    val = search_hash(depth, alpha, beta)
    if val != unknown:
        return val

    my_moves = MoveList()
    my_moves.phase = 0
    my_moves.first = True
    p = seek_point(my_moves)
    best = Point()
    best.pos = p[:]
    best.val = -10000
    hashf = hash_alpha
    while p[0] != -1:
        move(p)
        for _ in range(1):
            if (not my_moves.first) and (alpha + 1 < beta):
                val = -alpha_beta(depth - 1, -alpha - 1, -alpha)
                if val <= alpha or val >= beta:
                    break
            val = -alpha_beta(depth - 1, -beta, -alpha)
        remove()

        if stop:
            return best.val

        if val >= beta:
            write_hash(depth, val, hash_beta)
            write_PVS(p)
            return val
        if val > best.val:
            best.val = val
            best.pos = p[:]
            if val > alpha:
                hashf = hash_exact
                alpha = val
        p = seek_point(my_moves)
        my_moves.first = False

    write_hash(depth, best.val, hashf)
    write_PVS(best.pos)

    return best.val


def write_PVS(best):
    global pvstable
    pv = PV()
    pv.key = zobristkey
    pv.best = best[:]
    pvstable[zobristkey % pvs_size] = pv


def evaluate():
    eval = [0, 2, 12, 18, 96, 144, 800, 1200]
    myType = [0] * 8  # 统计我方棋形
    oppType = [0] * 8  # 统计对方棋形

    for i in range(board_start, board_end):
        for j in range(board_start, board_end):
            if board[i][j].nei and board[i][j].role == Empty:
                _block4 = myType[block4]
                for k in range(4):
                    myType[board[i][j].pattern[my][k]] += 1
                    oppType[board[i][j].pattern[opp][k]] += 1
                # FLEX4
                if myType[block4] - _block4 >= 2:
                    myType[block4] -= 2
                    myType[flex4] += 1

    # 我方必胜
    if myType[win] >= 1:
        return 10000
    # 对方下一步不能必胜，我方有活四
    if oppType[win] == 0 and myType[flex4] >= 1:
        return 10000
    # 对方有两种必胜的下法
    if oppType[win] >= 2:
        return -10000

    # 没有必胜，加权求和
    my_score = 0
    opp_score = 0
    for i in range(8):
        my_score += myType[i] * eval[i]
        opp_score += oppType[i] * eval[i]
    #
    return my_score * offen_coef - opp_score


def seek_point(my_moves):
    # 使用pvs表
    if my_moves.phase == 0:
        my_moves.phase = 1
        pv = pvstable[zobristkey % pvs_size]
        # 找到了
        if pv != 0 and pv.key == zobristkey:
            my_moves.hashMove = pv.best
            return pv.best
    # 如果没找到，生成所有可能下法
    if my_moves.phase == 1:
        my_moves.phase = 2
        my_moves.n = get_moves(my_moves.moves)
        my_moves.index = 0
        if not my_moves.first:
            for i in range(my_moves.n):
                if my_moves.moves[i][0] == my_moves.hashMove[0] and my_moves.moves[i][1] == my_moves.hashMove[1]:
                    for j in range(i + 1, my_moves.n):
                        my_moves.moves[j - 1] = my_moves.moves[j]
                    my_moves.n -= 1
                    break
    # 返回所有可能下法
    if my_moves.phase == 2:
        if my_moves.index < my_moves.n:
            my_moves.index += 1
            return my_moves.moves[my_moves.index - 1]
    return [-1, -1]


def get_moves(move):
    global cand
    cand_count = 0  # 候选点个数

    for i in range(board_start, board_end):
        for j in range(board_start, board_end):
            if board[i][j].nei and board[i][j].role == Empty:
                val = point_score(board[i][j])
                if val > 0:
                    cand[cand_count].pos[0] = i
                    cand[cand_count].pos[1] = j
                    cand[cand_count].val = val
                    cand_count += 1

    cand[0:cand_count] = sorted(cand[0:cand_count], key=lambda x: x.val, reverse=True)
    # 剪枝
    move_count = move_pruning(move, cand, cand_count)
    # move_count=0表示不能精确剪枝
    if move_count == 0:
        for i in range(cand_count):
            move[i] = cand[i].pos[:]
            move_count += 1
            if move_count >= max_branch:
                break
    return move_count


def move_pruning(move, cand, cand_count):
    # 有活四
    if cand[0].val >= 2400:
        move[0] = cand[0].pos[:]
        return 1
    move_count = 0
    # 有活三
    if cand[0].val == 1200:
        # 其他活三或冲四
        for i in range(cand_count):
            if cand[i].val == 1200:
                move[move_count] = cand[i].pos[:]
                move_count += 1
            else:
                break

        flag = False
        for i in range(move_count, cand_count):
            p = board[cand[i].pos[0]][cand[i].pos[1]]
            for k in range(4):
                if p.pattern[my][k] == block4 or p.pattern[opp][k] == block4:
                    flag = True
                    break
            if flag:
                move[move_count] = cand[i].pos[:]
                move_count += 1
                if move_count >= max_branch:
                    break

    return move_count


def point_score(c):
    score = [0] * 2
    score[my] = pval_table[c.pattern[my][0]][c.pattern[my][1]][c.pattern[my][2]][c.pattern[my][3]]
    score[opp] = pval_table[c.pattern[opp][0]][c.pattern[opp][1]][c.pattern[opp][2]][c.pattern[opp][3]]

    # 双活三
    if score[my] >= 200 or score[opp] >= 200:
        return score[my] * 2 if score[my] >= score[opp] else score[opp]
    # 其他
    else:
        return score[my] * 2 + score[opp]
