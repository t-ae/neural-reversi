#!/usr/bin/env python

import os, re, glob
import numpy as np
import reversi

FILES_DIR = os.path.dirname(__file__)

GGF_PATH = os.path.join(FILES_DIR, "./ggf/*.ggf")
OUTPUT_DIR = os.path.join(FILES_DIR, "./record_ggf")

TYPE_REGEX = re.compile(r"TY\[8\]")
HAND_REGEX = re.compile(r"\](W|B)\[([ABCDEFGHabcdefgh][12345678])")
def decode_line(line):
    if TYPE_REGEX.search(line) is None:
        raise Exception("Type is not 8")

    board = reversi.create_board()
    boards = []
    colors = []
    hands = HAND_REGEX.findall(line)
    boards.append(board)
    for h in hands:
        # reversi.print_board(board)
        # print(h)
        color = reversi.BLACK if h[0] == "B" else reversi.WHITE
        x, y = reversi.coord_to_xy(h[1])
        if not reversi.can_put(board, color, (x, y)):
            raise Exception("cant put")
        board = reversi.put(board, color, (x, y))
        boards.append(board)
        colors.append(color)

    if reversi.can_put(board):
        raise Exception("not finished")

    won = reversi.judge(board)
    boards = np.array(boards).reshape([-1, 8, 8])
    colors = np.array(colors).reshape([-1, 1])

    return boards, colors, won

def save_record(filename, boards, colors, won):
    score = won

    X_board = np.array(boards).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])
    X_color = np.array(colors).reshape([-1, 1])

    path = os.path.join(OUTPUT_DIR, "{0}.npz".format(filename))

    np.savez(path,
             X_board=X_board,
             X_color=X_color,
             y_won=won)
    # check
    try:
        np.load(path)
    except:
        os.remove(path)


ggfs = glob.glob(GGF_PATH)
for ggf_path in ggfs:
    print("extract:", ggf_path)
    filename_prefix = os.path.basename(ggf_path)
    with open(ggf_path) as f:
        number = 0
        for line in f:
            print("number:", number, end='\r')
            try:
                boards, colors, won = decode_line(line)
                filename = filename_prefix + "_" + str(number)
                save_record(filename, boards, colors, won)
                number += 1
            except:
                continue

    print("extract {0} records".format(number))