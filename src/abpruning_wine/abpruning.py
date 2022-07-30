import pisqpipe as pp
import random
import win32api

WIN = 7
FLEX4 = 6
BLOCK4 = 5
FLEX3 = 4
BLOCK3 = 3
FLEX2 = 2
BLOCK2 = 1
Ntype = 8
MaxSize = 20
MaxMoves = 40
hashSize = 1 << 22
pvsSize = 1 << 20
MaxDepth = 20
MinDepth = 2

hash_exact = 0
hash_alpha = 1
hash_beta = 2
unknown = -20000

cnt = 1000

Pieces = {
    "White": 0,
    "Black": 1,
    "Empty": 2,
    "Outside": 3
}

dx = [1, 0, 1, 1]
dy = [0, 1, 1, -1]

class Pos:
    def __init__(self):
        self.x = 0
        self.y = 0

class Point:
    def __init__(self):
        self.p = Pos()
        self.val = 0

class Cell:
    def __init__(self):
        self.piece = 0
        self.IsCand = 0
        self.pattern = [[0 for _ in range(4)] for _ in range(2)]

class Hashe:
    def __init__(self):
        self.key = 0
        self.depth = 0
        self.hashf = 0
        self.val = 0

class Pv:
    def __init__(self):
        self.key = 0
        self.best = Pos()

class Line:
    def __init__(self):
        self.n = 0
        self.moves = [Pos() for _ in range(MaxDepth)]

class MoveList:
    def __init__(self):
        self.phase = 0
        self.n = 0
        self.index = 0
        self.first = False
        self.hashMove = Pos()
        self.moves = [Pos() for _ in range(64)]

class Board:
    def __init__(self):
        self.step = 0
        self.size = pp.width
        self.b_start = 0
        self.b_end = 0
        self.zobristKey = 0
        self.zobrist = [[[random.getrandbits(64) for _ in range(MaxSize + 4)] for _ in range(MaxSize + 4)] for _ in range(0, 2)]
        self.hashTable = [Hashe() for _ in range(hashSize)]
        self.pvsTable = [Pv() for _ in range(pvsSize)]
        self.typeTable = [[[[0 for _ in range(3)] for _ in range(6)] for _ in range(6)] for _ in range(10)]
        self.patternTable = [[0 for _ in range(2)] for _ in range(65536)]
        self.pval = [[[[0 for _ in range(8)] for _ in range(8)] for _ in range(8)] for _ in range(8)]
        self.cell = [[Cell() for _ in range(MaxSize + 8)] for _ in range(MaxSize + 8)]
        self.remMove = [Pos() for _ in range(MaxSize * MaxSize)]
        self.cand = [Point() for _ in range(256)]
        self.IsLose = [[False for _ in range(MaxSize + 4)] for _ in range(MaxSize + 4)]
        self.who = Pieces["Black"]
        self.opp = Pieces["White"]
        self.rootMove = [Point() for _ in range(64)]
        self.rootCount = 0
        self.ply = 0
        self.InitChessType()

    def InitChessType(self):
        for i in range(10):
            for j in range(6):
                for k in range(6):
                    for l in range(3):
                        self.typeTable[i][j][k][l] = self.GenerateAssist(i, j, k, l)

        for key in range(65536):
            self.patternTable[key][0] = self.LineType(0, key)
            self.patternTable[key][1] = self.LineType(1, key)

        for i in range(8):
            for j in range(8):
                for k in range(8):
                    for l in range(8):
                        self.pval[i][j][k][l] = self.GetPval(i, j, k, l)

    def GetPval(self, a, b, c, d):
        type = [0 for _ in range(8)]
        type[a] += 1
        type[b] += 1
        type[c] += 1
        type[d] += 1
        if type[WIN] > 0:
            return 5000
        if type[FLEX4] > 0 or type[BLOCK4] > 1:
            return 1200
        if type[BLOCK4] > 0 and type[FLEX3] > 0:
            return 1000
        if type[FLEX3] > 1:
            return 200

        val = [0, 2, 5, 5, 12, 12]
        score = 0
        for i in range(1, BLOCK4 + 1):
            score += val[i] * type[i]

        return score

    def LineType(self, role, key):
        line_left = [0 for _ in range(9)]
        line_right = [0 for _ in range(9)]
        for i in range(9):
            if i == 4:
                line_left[i] = role
                line_right[i] = role
            else:
                line_left[i] = key & 3
                line_right[8 - i] = key & 3
                key >>= 2

        p1 = self.ShortLine(line_left)
        p2 = self.ShortLine(line_right)

        if p1 == BLOCK3 and p2 == BLOCK3:
            return self.CheckFlex3(line_left)
        elif p1 == BLOCK4 and p2 == BLOCK4:
            return self.CheckFlex4(line_left)
        else:
            return max(p1, p2)

    def ShortLine(self, line):
        kong = 0
        block = 0
        len = 1
        len2 = 1
        count = 1
        who = line[4]
        for k in range(5, 9):
            if line[k] == who:
                if kong + count > 4:
                    break
                count += 1
                len += 1
                len2 = kong + count
            elif line[k] == Pieces["Empty"]:
                len += 1
                kong += 1
            else:
                if line[k - 1] == who:
                    block += 1
                break
        kong = len2 - count
        for k in range(3, -1, -1):
            if line[k] == who:
                if kong + count > 4:
                    break
                count += 1
                len += 1
                len2 = kong + count
            elif line[k] == Pieces["Empty"]:
                len += 1
                kong += 1
            else:
                if line[k + 1] == who:
                    block += 1
                break

        return self.typeTable[len][len2][count][block]

    def CheckFlex3(self, line):
        role = line[4]
        for i in range(0, 9):
            if line[i] == Pieces["Empty"]:
                line[i] = role
                type = self.CheckFlex4(line)
                line[i] = Pieces["Empty"]
                if type == FLEX4:
                    return FLEX3

        return BLOCK3

    def CheckFlex4(self, line):
        five = 0
        role = line[4]
        for i in range(0, 9):
            if line[i] == Pieces["Empty"]:
                count = 0
                for j in range(i - 1, -1, -1):
                    if line[j] != role:
                        break
                    count += 1
                for j in range(i + 1, 9):
                    if line[j] != role:
                        break
                    count += 1
                if count >= 4:
                    five += 1

        return FLEX4 if five >= 2 else BLOCK4

    def GenerateAssist(self, len, len2, count, block):
        if len >= 5 and count > 1:
            if count == 5:
                return WIN
            if len > 5 and len2 < 5 and block == 0:
                if count == 2:
                    return FLEX2
                elif count == 3:
                    return FLEX3
                elif count == 4:
                    return FLEX4
            else:
                if count == 2:
                    return BLOCK2
                elif count == 3:
                    return BLOCK3
                elif count == 4:
                    return BLOCK4
        return 0

    def SetSize(self, _size):
        self.size = _size
        self.b_start = 4
        self.b_end = _size + 4
        for i in range(MaxSize + 8):
            for j in range(MaxSize + 8):
                if i < 4 or i >= _size + 4 or j < 4 or j >= _size + 4:
                    self.cell[i][j].piece = Pieces["Outside"]
                else:
                    self.cell[i][j].piece = Pieces["Empty"]

    def MakeMove(self, next=Pos()):
        x, y = next.x, next.y

        self.ply += 1
        self.cell[x][y].piece = self.who
        self.zobristKey ^= self.zobrist[self.who][x][y]
        self.who ^= 1
        self.opp ^= 1
        self.remMove[self.step] = next
        self.step += 1
        self.UpdateType(x, y)
        for i in range(x - 2, x + 3):
            self.cell[i][y - 2].IsCand += 1
            self.cell[i][y - 1].IsCand += 1
            self.cell[i][y].IsCand += 1
            self.cell[i][y + 1].IsCand += 1
            self.cell[i][y + 2].IsCand += 1

    def DelMove(self):
        self.step -= 1
        x = self.remMove[self.step].x
        y = self.remMove[self.step].y

        self.ply -= 1
        self.who ^= 1
        self.opp ^= 1
        self.zobristKey ^= self.zobrist[self.who][x][y]
        self.cell[x][y].piece = Pieces["Empty"]
        self.UpdateType(x, y)
        for i in range(x - 2, x + 3):
            self.cell[i][y - 2].IsCand -= 1
            self.cell[i][y - 1].IsCand -= 1
            self.cell[i][y].IsCand -= 1
            self.cell[i][y + 1].IsCand -= 1
            self.cell[i][y + 2].IsCand -= 1

    def Undo(self):
        if self.step >= 2:
            self.DelMove()
            self.DelMove()
        elif self.step == 1:
            self.DelMove()

    def ReStart(self):
        self.pvsTable = [Pv() for _ in range(pvsSize)]
        self.hashTable = [Hashe() for _ in range(hashSize)]
        while self.step:
            self.DelMove()

    def CheckXy(self, x, y):
        return self.cell[x][y].piece != Pieces["Outside"]

    def UpdateType(self, x, y):
        for i in range(4):
            a = x + dx[i]
            b = y + dy[i]
            for j in range(4):
                if not self.CheckXy(a, b):
                    break
                key = self.GetKey(a, b, i)
                self.cell[a][b].pattern[0][i] = self.patternTable[key][0]
                self.cell[a][b].pattern[1][i] = self.patternTable[key][1]
                a += dx[i]
                b += dy[i]

            a = x - dx[i]
            b = y - dy[i]
            for k in range(0, 4):
                if not self.CheckXy(a, b):
                    break
                key = self.GetKey(a, b, i)
                self.cell[a][b].pattern[0][i] = self.patternTable[key][0]
                self.cell[a][b].pattern[1][i] = self.patternTable[key][1]
                a -= dx[i]
                b -= dy[i]

    def GetKey(self, x, y, i):
        stepX = dx[i]
        stepY = dy[i]
        key = (self.cell[x - stepX * 4][y - stepY * 4].piece) ^ \
              (self.cell[x - stepX * 3][y - stepY * 3].piece << 2) ^ \
              (self.cell[x - stepX * 2][y - stepY * 2].piece << 4) ^ \
              (self.cell[x - stepX * 1][y - stepY * 1].piece << 6) ^ \
              (self.cell[x + stepX * 1][y + stepY * 1].piece << 8) ^ \
              (self.cell[x + stepX * 2][y + stepY * 2].piece << 10) ^ \
              (self.cell[x + stepX * 3][y + stepY * 3].piece << 12) ^ \
              (self.cell[x + stepX * 4][y + stepY * 4].piece << 14)
        return key

    def color(self, _step):
        return _step & 1

    def TypeCount(self, c, role, type):
        type[c.pattern[role][0]] += 1
        type[c.pattern[role][1]] += 1
        type[c.pattern[role][2]] += 1
        type[c.pattern[role][3]] += 1

    def IsType(self, c, role, type):
        return c.pattern[role][0] == type or c.pattern[role][1] == type or c.pattern[role][2] == type or c.pattern[role][3] == type

    def CheckWin(self):
        c = self.cell[self.remMove[self.step - 1].x][self.remMove[self.step - 1].y]
        return c.pattern[self.opp][0] == WIN or c.pattern[self.opp][1] == WIN or c.pattern[self.opp][2] == WIN or c.pattern[self.opp][3] == WIN

class AI:
    def __init__(self):
        self.board = Board()
        self.eval = [0, 2, 12, 18, 96, 144, 800, 1200]
        self.total = 0
        self.hashCount = 0
        self.searchDepth = 0
        self.ThinkTime = 0
        self.bestPoint = Point()
        self.bestLine = Line()
        self.start = 0
        self.stopThink = False
        self.cnt = 1000

    def MainSearch(self):
        self.total = 0
        self.hashCount = 0
        bestMove = Pos()
        _step = self.board.step
        if _step == 0:
            bestMove.x = int(self.board.size / 2) + 4
            bestMove.y = int(self.board.size / 2) + 4
            return bestMove
        if _step == 1 or _step == 2:
            while 1:
                rx = self.board.remMove[0].x + random.randint(0, 2 << 16 - 1) % (_step * 2 + 1) - _step
                ry = self.board.remMove[0].y + random.randint(0, 2 << 16 - 1) % (_step * 2 + 1) - _step
                if self.board.CheckXy(rx, ry) and self.board.cell[rx][ry].piece == Pieces["Empty"]:
                    break

            bestMove.x = rx
            bestMove.y = ry
            return bestMove

        self.stopThink = False
        self.bestPoint.val = 0
        self.board.ply = 0
        self.board.IsLose = [[False for _ in range(MaxSize + 4)] for _ in range(MaxSize + 4)]
        for i in range(MinDepth, MaxDepth + 1, 2):
            self.searchDepth = i
            self.bestPoint = self.RootSearch(self.searchDepth, -10001, 10000, self.bestLine)
            f = open("D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt", "a")
            print(i, file=f)
            print(self.stopThink, file=f)
            f.close()
            if self.stopThink or (self.searchDepth >= 10 and self.GetTime() >= 1000 and self.GetTime() * 12 > self.StopTime()):
                break

        bestMove = self.bestPoint.p

        return bestMove

    def RootSearch(self, depth, alpha, beta, pline):
        best = self.board.rootMove[0]
        line = Line()

        if depth == MinDepth:
            moves = [Pos() for _ in range(64)]
            self.board.rootCount = self.GenerateMove(moves)
            if self.board.rootCount == 1:
                f = open(
                    "D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt",
                    "a")
                print("set stop think at rootCount", file=f)
                f.close()
                self.stopThink = True
                best.p = moves[0]
                best.val = 0
                pline.n = 0
                return best

            for i in range(0, self.board.rootCount):
                self.board.rootMove[i].p = moves[i]

        else:
            for i in range(1, self.board.rootCount):
                if self.board.rootMove[i].val > self.board.rootMove[0].val:
                    temp = self.board.rootMove[0]
                    self.board.rootMove[0] = self.board.rootMove[i]
                    self.board.rootMove[i] = temp

        for i in range(0, self.board.rootCount):
            p = self.board.rootMove[i].p
            if not self.board.IsLose[p.x][p.y]:
                line.n = 0
                self.board.MakeMove(p)
                while 1:
                    if i > 0 and alpha + 1 < beta:
                        val = -self.AlphaBeta(depth - 1, -alpha - 1, -alpha, line)
                        if val <= alpha or val >= beta:
                            break
                    val = -self.AlphaBeta(depth - 1, -beta, -alpha, line)
                    if True:
                        break
                self.board.DelMove()

                self.board.rootMove[i].val = val

                if self.stopThink:
                    break

                if val == -10000:
                    self.board.IsLose[p.x][p.y] = True

                if val > alpha:
                    alpha = val
                    best.p = p
                    best.val = val
                    pline.moves[0] = p
                    for j in range(0, line.n):
                        pline.moves[j + 1] = line.moves[j]
                    pline.n = line.n + 1
                    if val == 10000:
                        f = open(
                            "D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt",
                            "a")
                        print("setStopthink at val", file=f)
                        f.close()
                        self.stopThink = True
                        return best

        return best

    def GetTime(self):
        return win32api.GetTickCount() - pp.start_time

    def StopTime(self):
        return min(pp.info_timeout_turn, int(pp.info_time_left / 7))

    def GenerateMove(self, move):
        candCount = 0
        _b_start = self.board.b_start
        _b_end = self.board.b_end
        for i in range(_b_start, _b_end):
            for j in range(_b_start, _b_end):
                if self.board.cell[i][j].IsCand and self.board.cell[i][j].piece == Pieces["Empty"]:
                    val = self.EvaluateMove(self.board.cell[i][j])
                    if val > 0:
                        self.board.cand[candCount].p.x = i
                        self.board.cand[candCount].p.y = j
                        self.board.cand[candCount].val = val
                        candCount += 1

        self.board.cand[0:candCount] = sorted(self.board.cand[0:candCount], key=lambda x: x.val, reverse=True)
        moveCount = self.CutMoveList(move, candCount)
        if moveCount == 0:
            for i in range(candCount):
                move[i] = self.board.cand[i].p
                moveCount += 1
                if moveCount >= MaxMoves:
                    break

        return moveCount

    def CutMoveList(self, move, candCount):
        cand = self.board.cand
        if cand[0].val >= 2400:
            move[0] = cand[0].p
            return 1
        moveCount = 0
        if cand[0].val == 1200:
            for i in range(candCount):
                if cand[i].val == 1200:
                    move[moveCount] = cand[i].p
                    moveCount += 1
                else:
                    break

            for i in range(moveCount, candCount):
                p = self.board.cell[cand[i].p.x][cand[i].p.y]
                if self.board.IsType(p, self.board.who, BLOCK4) or self.board.IsType(p, self.board.opp, BLOCK4):
                    move[moveCount] = cand[i].p
                    moveCount += 1
                    if moveCount >= MaxMoves:
                        break

        return moveCount

    def EvaluateMove(self, c):
        score = [0, 0]
        who = self.board.who
        opp = self.board.opp
        score[who] = self.board.pval[c.pattern[who][0]][c.pattern[who][1]][c.pattern[who][2]][c.pattern[who][3]]
        score[opp] = self.board.pval[c.pattern[opp][0]][c.pattern[opp][1]][c.pattern[opp][2]][c.pattern[opp][3]]

        if score[who] >= 200 or score[opp] >= 200:
            return 2 * score[who] if score[who] >= score[opp] else score[opp]
        else:
            return score[who] * 2 + score[opp]

    def AlphaBeta(self, depth, alpha, beta, pline):
        self.total += 1
        self.cnt -= 1
        if self.cnt <= 0:
            self.cnt = 1000
            if self.GetTime() + 50 >= self.StopTime():
                f = open(
                    "D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt",
                    "a")
                print("setstopthink at time", file=f)
                f.close()
                self.stopThink = True
                return alpha

        if self.board.CheckWin():
            return -10000

        if depth <= 0:
            return self.evaluate()

        val = self.ProbeHash(depth, alpha, beta)
        if val != unknown:
            self.hashCount += 1
            return val

        line = Line()
        moveList = MoveList()
        moveList.phase = 0
        moveList.first = True
        p = self.GetNextMove(moveList)
        best = Point()
        best.p = p
        best.val = -10000
        hashf = hash_alpha
        while p.x != -1:
            line.n = 0
            self.board.MakeMove(p)
            while 1:
                if (not moveList.first) and (alpha + 1 < beta):
                    val = -self.AlphaBeta(depth - 1, -alpha - 1, -alpha, line)
                    if val <= alpha or val >= beta:
                        break
                val = -self.AlphaBeta(depth - 1, -beta, -alpha, line)
                if True:
                    break
            self.board.DelMove()

            if self.stopThink:
                return best.val

            if val >= beta:
                self.RecordHash(depth, val, hash_beta)
                self.RecordPVS(p)
                return val

            if val > best.val:
                best.val = val
                best.p = p
                if val > alpha:
                    hashf = hash_exact
                    alpha = val
                    pline.moves[0] = p
                    for j in range(line.n):
                        pline.moves[j + 1] = line.moves[j]
                    pline.n = line.n + 1

            p = self.GetNextMove(moveList)
            moveList.first = False

        self.RecordHash(depth, best.val, hashf)
        self.RecordPVS(best.p)

        return best.val

    def evaluate(self):
        whoType = [0 for _ in range(8)]
        oppType = [0 for _ in range(8)]
        _b_start = self.board.b_start
        _b_end = self.board.b_end
        for i in range(_b_start, _b_end):
            for j in range(_b_start, _b_end):
                if self.board.cell[i][j].IsCand and self.board.cell[i][j].piece == Pieces["Empty"]:
                    block4_temp = whoType[BLOCK4]
                    self.board.TypeCount(self.board.cell[i][j], self.board.who, whoType)
                    self.board.TypeCount(self.board.cell[i][j], self.board.who, oppType)
                    if whoType[BLOCK4] - block4_temp >= 2:
                        whoType[BLOCK4] -= 2
                        whoType[FLEX4] += 1

        if whoType[WIN] >= 1:
            return 10000
        if oppType[WIN] >= 2:
            return -10000
        if oppType[WIN] == 0 and whoType[FLEX4] >= 1:
            return 10000

        whoScore = 0
        oppScore = 0
        for i in range(1, 8):
            whoScore += whoType[i] * self.eval[i]
            oppScore += oppType[i] * self.eval[i]
        return whoScore * 1.2 - oppScore

    def ProbeHash(self, depth, alpha, beta):
        phashe = self.board.hashTable[self.board.zobristKey & (hashSize - 1)]
        if phashe.key == self.board.zobristKey:
            if phashe.depth >= depth:
                if phashe.hashf == hash_exact:
                    return phashe.val
                elif phashe.hashf == hash_alpha and phashe.val <= alpha:
                    return phashe.val
                elif phashe.hashf == hash_beta and phashe.val >= beta:
                    return phashe.val

        return unknown

    def GetNextMove(self, moveList):
        if moveList.phase == 0:
            moveList.phase = 1
            e = self.board.pvsTable[self.board.zobristKey % pvsSize]
            if e.key == self.board.zobristKey:
                moveList.hashMove = e.best
                return e.best

        if moveList.phase == 1:
            moveList.phase = 2
            moveList.n = self.GenerateMove(moveList.moves)
            moveList.index = 0
            if not moveList.first:
                for i in range(moveList.n):
                    if moveList.moves[i].x == moveList.hashMove.x and moveList.moves[i].y == moveList.hashMove.y:
                        for j in range(i + 1, moveList.n):
                            moveList.moves[j - 1] = moveList.moves[j]
                        moveList.n -= 1
                        break

        if moveList.phase == 2:
            if moveList.index < moveList.n:
                moveList.index += 1
                return moveList.moves[moveList.index - 1]

        p = Pos()
        p.x, p.y = -1, -1
        return p

    def RecordHash(self, depth, val, hashf):
        phashe = self.board.hashTable[self.board.zobristKey & (hashSize - 1)]
        phashe.key = self.board.zobristKey
        phashe.val = val
        phashe.hashf = hashf
        phashe.depth = depth

    def RecordPVS(self, best):
        e = self.board.pvsTable[self.board.zobristKey % pvsSize]
        e.key = self.board.zobristKey
        e.best = best

    def PutChess(self, next=Pos()):
        next.x += 4
        next.y += 4
        self.board.MakeMove(next)

    def GetBestMove(self):
        best = self.MainSearch()
        best.x -= 4
        best.y -= 4
        return best


if __name__ == "__main__":
    board = [[0 for _ in range(20)] for _ in range(20)]
    test = AI()
    test.board.SetSize(20)
    board[10][10] = 2
    next = Pos()
    next.x = 10
    next.y = 10
    test.PutChess(next)
    board[10][11] = 1
    next.x = 10
    next.y = 11
    test.PutChess(next)
    board[11][10] = 2
    next.x = 11
    next.y = 10
    test.PutChess(next)
    bestmove = test.GetBestMove()










