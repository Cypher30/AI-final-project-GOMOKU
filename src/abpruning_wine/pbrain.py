
import copy
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG
import abpruning as abpruning
import random

# pp.infotext = infotext
MAX_BOARD = 100
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
AI = abpruning.AI()


def brain_init():
	if pp.width < 5 or pp.height < 5:
		pp.pipeOut("ERROR size of the board")
		return
	if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
		pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
		return
	global AI
	AI.board.SetSize(pp.width)
	pp.pipeOut("OK")

def brain_restart():
	# f = open("D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt", "a")
	# print("Hit restart!", file=f)
	# f.close()
	for x in range(pp.width):
		for y in range(pp.height):
			board[x][y] = 0
	global AI
	AI.board.ReStart()
	# f = open("D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt", "a")
	# print("Finish restart!", file=f)
	# f.close()
	pp.pipeOut("OK")

def isFree(x, y):
	return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

def brain_my(x, y):
	global AI
	# f = open("D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt", "a")
	# print("Hit brain_my", file=f)
	# f.close()
	if isFree(x,y):
		board[x][y] = 1
		# f = open("D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt", "a")
		# print("Hit before next", file=f)
		# f.close()
		next = abpruning.Pos()
		next.x = x
		next.y = y
		# f = open("D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt", "a")
		# print("Hit before makemove", file=f)
		# f.close()
		AI.PutChess(next)
		# f = open("D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt", "a")
		# print("Finish brain_my", file=f)
		# f.close()
	else:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	# f = open("D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt", "a")
	# print("Hit brain_opp", file=f)
	# f.close()
	global AI
	if isFree(x,y):
		board[x][y] = 2
		next = abpruning.Pos()
		next.x = x
		next.y = y
		AI.PutChess(next)
		# f = open("D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt", "a")
		# print("Finish brain_opp", file=f)
		# f.close()
	else:
		pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
	if isFree(x,y):
		board[x][y] = 3
	else:
		pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
	global AI
	if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
		AI.board.Undo()
		board[x][y] = 0
		return 0
	return 2


def brain_turn():
	global AI
	# f = open("D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt", "a")
	# print("Hit brain_turn", file=f)
	# f.close()
	if pp.terminateAI:
		return
	# copy_board = copy.deepcopy(board)
	bestmove = AI.GetBestMove()
	# f = open("D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.txt", "a")
	# print("Finish bestmove", file=f)
	# print(bestmove.x, file=f)
	# print(bestmove.y, file=f)
	# f.close()
	x = bestmove.x
	y = bestmove.y
	# x=random.randint(0, pp.width-1)
    # y=random.randint(0, pp.width-1)
	pp.do_mymove(x, y)

def brain_end():
	pass

def brain_about():
	pp.pipeOut(pp.infotext)

if DEBUG_EVAL:
	import win32gui
	def brain_eval(x, y):
		# TODO check if it works as expected
		wnd = win32gui.GetForegroundWindow()
		dc = win32gui.GetDC(wnd)
		rc = win32gui.GetClientRect(wnd)
		c = str(board[x][y])
		win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
		win32gui.ReleaseDC(wnd, dc)

######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################

# define a file for logging ...
DEBUG_LOGFILE = "D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning_wine/test.log"
# ...and clear it initially
with open(DEBUG_LOGFILE,"w") as f:
	pass

# define a function for writing messages to the file
def logDebug(msg):
	with open(DEBUG_LOGFILE,"a") as f:
		f.write(msg+"\n")
		f.flush()

# define a function to get exception traceback
def logTraceBack():
	import traceback
	with open(DEBUG_LOGFILE,"a") as f:
		traceback.print_exc(file=f)
		f.flush()
	raise

# use logDebug wherever
# use try-except (with logTraceBack in except branch) to get exception info
# an example of problematic function
# def brain_turn():
# 	logDebug("some message 1")
# 	try:
# 		logDebug("some message 2")
# 		1. / 0. # some code raising an exception
# 		logDebug("some message 3") # not logged, as it is after error
# 	except:
# 		logTraceBack()

######################################################################

# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
	pp.brain_eval = brain_eval

def main():
	pp.main()

if __name__ == "__main__":
	main()
