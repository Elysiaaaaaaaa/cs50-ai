"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    cnt = 0
    for row in board:
        for cell in row:
            if cell == "X":
                cnt += 1
            elif cell == "O":
                cnt -= 1
    if cnt <= 0:
        return 'X'
    else:
        return 'O'


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    ans = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                ans.add(tuple([i, j]))
    return ans

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i,j = action
    if i < 0 or i > 2 or j < 0 or j > 2:
        raise Exception("Invalid action")
    if board[i][j] != EMPTY:
        raise Exception("Invalid action")
    tmp = copy.deepcopy(board)
    tmp[i][j] = player(board)
    return tmp

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != EMPTY:
            return board[i][0]
        if board[0][i] ==  board[1][i] == board[2][i] != EMPTY:
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    flag = True
    if winner(board) == None:
        for i in range(3):
            for j in range(3):
                if board[i][j] == EMPTY:
                    flag = False
                    break
    return flag

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == "X":
        return 1
    elif win == "O":
        return -1
    else:
        return 0


def val_minimax(board):

    if terminal(board):
        return utility(board),[None]
    ans = [None]

    if player(board) == "X":
        v = -math.inf
        for a in actions(board):
            tmp = result(board, a)
            vv,aa = val_minimax(tmp)
            if vv > v:
                v = vv
                ans = [a] + aa
    else:
        v = math.inf
        for a in actions(board):
            tmp = result(board, a)
            vv,aa = val_minimax(tmp)
            if vv < v:
                v = vv
                ans = [a] + aa
    return v,ans

def minimax(board,act=[]):
    """
    Returns the optimal action for the current player on the board.
    """
    v, act = val_minimax(board)
    return act[0]
