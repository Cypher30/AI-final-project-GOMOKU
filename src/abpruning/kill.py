import random
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG
import copy

from functools import chain ###我新import的

class dot:
    def __init__(self, value=None, action=None, step=None):
        self.value = value  # 估计出的值
        self.action = action  # 位置
        self.step = step    #第几步棋

lastMaxPoint = []
lastMinPoint = []

##找到所有比目标分数大的位置
##注意，不止要找自己的，还要找对面的，
def finaMax(player, score):
    global lastMaxPoint
    global lastMinPoint
    result = []
    fives = [] #存放成五关键点的坐标
    for i in range(pp.width):
        for j in range(pp.height):
            if isFree(i, j):
                p = dot(action = [i, j])
                ##防对面冲四
                if humScore[i, j] >= S.FIVE: ###!!此时只计算对手这里下棋能得到的进攻分数能不能大于等于五连的分（评分不考虑我们的黑棋）
                    #hum-人类对手【白子，com-ai自己【黑子
                    p.value = S.FIVE
                    p.value = p.value * -1 if player == 1 else p.value * 1
                    fives.append(p.action)
                elif comScore[i, j]>= S.FIVE:##!!
                    p.value = S.FIVE
                    p.value = p.value * -1 if player == 2 else p.value * 1
                    fives.append(p.action)
                else: 
                    if ((not lastMaxPoint) or (i == lastMaxPoint[0] or j == lastMaxPoint[1] or (abs(i-lastMaxPoint[0]) == abs(j-lastMaxPoint[1])))):
                        s = comScore[i, j] if player == 1 else humScore[i, j]
                        p.value = s
                        if s >= score:
                            result.append(p)
    ## 能连五，则直接返回
    ##但是注意不要碰到连五就返回，而是把所有连五的点都考虑一遍，不然可能出现自己能连却防守别人的问题
    if len(fives):
        return fives
    sorted(results, key=lambda s: s.value, reverse=True)
    return result


##找到所有比目标分数大的位置
###这是MIN层，所以己方分数要变成负数
def finaMin(player, score):
    global lastMaxPoint
    global lastMinPoint
    result = []
    fives = [] #存放成五关键点的坐标
    fours = [];
    blockedfours = [];
    for i in range(pp.width):
        for j in range(pp.height):
            if isFree(i, j):
                p = dot(action = [i, j])
                s1 = comScore[i, j] if player == 1 else humScore[i, j]
                s2 = humScore[i, j] if player == 1 else comScore[i, j]
                if s1 >= S.FIVE:
                    p.value = -1*s1
                    return [p]
        
                if s2 >= S.FIVE:
                    p.value = s2
                    fives.append(p)
                    continue

                if s1 >= S.FOUR:
                    p.value = -1*s1
                    fours.insert(0,p)
                    continue
                if s2 >= S.FOUR:
                    p.value = s2
                    fours.append(p)
                    continue

                if s1 >= S.BLOCKED_FOUR:
                    p.value = -1*s1
                    blockedfours.insert(0,p)
                    continue

                if s2 >= S.BLOCKED_FOUR:
                    p.value = s2
                    blockedfours.append(p)
                    continue


                if s1 >= score or s2 >= score:
                    p.action = [i, j]
                    p.value = s1
                    result.append(p)
    if len(fives):
        return fives
   ##注意冲四，因为虽然冲四的分比活四低，但是他的防守优先级是和活四一样高的，否则会忽略冲四导致获胜的走法
    if len(fours):
       return list(chain(fours,blockedfours))
     ##注意对结果进行排序
     ##因为fours可能不存在，这时候不要忽略了 blockedfours
    result = list(chain(result,blockedfours))

def max(player, deep, totalDeep):
    if deep <= 1: 
        return False
    points = findMax(player, MAX_SCORE)
    if len(points) and points[0].value >= S.FOUR:
       return [points[0]]##为了减少一层搜索，活四就行了。
    if len(points) == 0:
        return False
    for i in range(len(points)):
        p = points[i]
        board.put(p, player)#######！！！在棋盘下子p点
        ##如果是防守对面的冲四，那么不用记下来
        if not p.value <= -1*S.FIVE:
            lastMaxPoint = p.action
        role = 1 if player == 2 else 2
        m = min(role, deep-1)
        board.remove(p)#######！！！在棋盘上移除棋子p，记得撤销zobrist操作！
        if m:
            if len(m):
                m.insert(0,p)
                return m
            else:
                return [p]
    return False

##只要有一种方式能防守住，就可以了
def min(player, deep, totalDeep):
    if deep <= 1: 
        return False
    points = findMin(player, MIN_SCORE)
    if len(points) and -1 * points[0].value >= S.FOUR:
       return False
    cands = []
    for i in range(len(points)):
        p = points[i]
        board.put(p, player)
        lastMinPoint = p.action
        role = 1 if player == 2 else 2
        m = max(role, deep-1)
        board.remove(p)
        if m:
            if len(m):
                m.insert(0,p)
                cands.append(m)
                continue
            else:
                return False##只要有一种能防守住
    result = cands[math.floor(len(cands)*random.uniform(0, 1))]#防不住，随机走一个
    return result

##迭代加深
def deeping(player, deep, totalDeep):
    global lastMaxPoint
    global lastMinPoint
    for i in range(1,deep+1):
        lastMaxPoint = []
        lastMinPoint = []
        result = max(player, i, deep)
        if result:
            if len(result):
                break
    return result;

#base
def vcx(role, deep, onlyFour):
    if deep <= 0:
        return False
    if onlyFour:
        ##计算冲四赢的
        MAX_SCORE = S.BLOCKED_FOUR 
        MIN_SCORE = S.FIVE
        result = deeping(role, deep, deep)
        if result:
            result[0].value = S.FOUR
            return result
        return False
    else:##计算通过 活三 赢的；
        MAX_SCORE = S.THREE
        MIN_SCORE = S.BLOCKED_FOU
        result = deeping(role, deep, deep)
        if result:
            result[0].value = S.THREE*2 ##连续冲三赢，就等于是双三
        return result
    return False

###连续冲四
def vcf(player, deep):
    result = vcx(role, deep, True)
    return result


###连续冲三
def vct(player, deep):
    result = vcx(role, deep, False)
    return result






