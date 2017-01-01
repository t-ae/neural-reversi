#!/usr/bin/env python

import numpy as np

EMPTY = 0
BLACK = 1
WHITE = -1

# BOARD_SIZE = 6
BOARD_SIZE = 8

__range = range(BOARD_SIZE)
__positions = [(x, y) for x in __range for y in __range]
__ds = [(dx, dy) for dx in [0, -1, 1] for dy in [0, -1, 1]][1:]

def create_board():
    board = np.zeros([BOARD_SIZE, BOARD_SIZE], dtype=int)
    board[BOARD_SIZE//2-1, BOARD_SIZE//2-1] = WHITE
    board[BOARD_SIZE//2, BOARD_SIZE//2] = WHITE
    board[BOARD_SIZE//2-1, BOARD_SIZE//2] = BLACK
    board[BOARD_SIZE//2, BOARD_SIZE//2-1] = BLACK
    return board

def print_board(board):
    for y in range(-1, BOARD_SIZE):
        for x in range(-1, BOARD_SIZE):
            if x == -1 and y == -1:
                print(" ", end="")
            elif x == -1:
                print("12345678"[y], end="")
            elif y == -1:
                print(" "+"ABCDEFGH"[x], end="")
            elif board[y, x] == BLACK:
                print(" X", end="")
            elif board[y, x] == WHITE:
                print(" O", end="")
            else:
                print(" .", end="")
        print("")

def is_in_board(position):
    return 0 <= position[0] and position[0] < BOARD_SIZE and 0 <= position[1] and position[1] < BOARD_SIZE

def can_put(board, color=None, position=None):
    if color is None:
        return can_put(board, BLACK) or can_put(board, WHITE)
    elif position is None:
        for pos in __positions:
            if can_put(board, color, pos):
                return True
        return False
    elif not is_in_board(position) or board[position[1], position[0]] != EMPTY:
        return False
    else:
        for ds in __ds:
            if __can_put_sub(board, color, position, ds):
                return True
        return False

def __can_put_sub(board, color, position, ds, r=False):
    now_pos = (position[0] + ds[0], position[1] + ds[1])
    if not is_in_board(now_pos):
        return False
    if board[now_pos[1], now_pos[0]] == EMPTY:
        return False
    elif board[now_pos[1], now_pos[0]] == color:
        return r
    else:
        return __can_put_sub(board, color, now_pos, ds, True)

def put(board, color, position):
    board = board.copy()
    if board[position[1], position[0]] != EMPTY:
        raise Exception("Try to put invalid place.")
    board[position[1], position[0]] = color
    for ds in __ds:
        __put_sub(board, color, position, ds)
    return board

def __put_sub(board, color, position, ds):
    now_pos = (position[0] + ds[0], position[1] + ds[1])
    if not is_in_board(now_pos):
        return False
    elif board[now_pos[1], now_pos[0]] == EMPTY:
        return False
    elif board[now_pos[1], now_pos[0]] == color:
        return True
    elif __put_sub(board, color, now_pos, ds):
        board[now_pos[1], now_pos[0]] = color
        return True
    else:
        return False

def judge(board):
    sum_stones = np.sum(board)
    if sum_stones > 0:
        return BLACK
    elif sum_stones < 0:
        return WHITE
    else:
        return EMPTY

def hands(board, color):
    hands = []
    for pos in __positions:
        if can_put(board, color, pos):
            hands.append(pos)
    return hands

def xy_to_coord(xy):
    x = xy[0]
    y = xy[1]
    return "ABCDEFGH"[x]+"12345678"[y]

def coord_to_xy(coord):
    x = "ABCDEFGH".find(coord[0])
    if x == -1:
        x = "abcdefgh".find(coord[0])
    y = "12345678".find(coord[1])
    return x, y
