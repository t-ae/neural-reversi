#!/usr/bin/env python

import os, time
import numpy as np
import reversi
import player

DUMP_BOARD = False
DUMP_SEARCH = False

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "record")

# player.RandomUniform()
# player.RandomMTS(100, -1, DUMP_SEARCH)
players = {
    reversi.BLACK: player.RandomUniform(),
    reversi.WHITE: player.RandomUniform()
}

def save_record(boards, colors, won):
    score = won

    X_board = np.array(boards).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])
    X_color = np.array(colors).reshape([-1, 1])

    now = int(round(time.time()*1000))
    path = os.path.join(OUTPUT_DIR, "{0}.npz".format(now))

    np.savez(path,
             X_board=X_board,
             X_color=X_color,
             y_won=won)
    # check
    try:
        np.load(path)
    except:
        os.remove(path)

for i in range(1, 9999999):
    print("game:", i, end='\n' if DUMP_BOARD else "\r")

    board = reversi.create_board()
    if DUMP_BOARD:
        reversi.print_board(board)

    boards = []
    colors = []

    turn = reversi.BLACK
    while reversi.can_put(board):

        hand = players[turn].select(board, turn)
        if hand is not None:
            # append
            boards.append(board)
            colors.append(turn)
            # put
            board = reversi.put(board, turn, hand)

            if DUMP_BOARD:
                reversi.print_board(board)
        turn = -turn

    won = reversi.judge(board)
    boards.append(board)
    if DUMP_BOARD:
        print("won:", won)

    save_record(boards, colors, won)

    # change
    tmp = players[reversi.BLACK]
    players[reversi.BLACK] = players[reversi.WHITE]
    players[reversi.WHITE] = tmp

