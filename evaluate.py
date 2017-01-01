#!/usr/bin/env python

import os, time
import numpy as np
import reversi, player, neural_player

def _main():
    from keras.models import load_model
    PLAY_NUM = 10
    DUMP_BOARD = True

    MODEL_PATH = os.path.join(os.path.dirname(__file__), "./output/best_model.h5")
    model = load_model(MODEL_PATH)

    # player.RandomUniform()
    # player.RandomMTS(100, -1)
    # neural_player.DQN(model, True)
    # neural_player.MiniMaxDQN(model, 2, True)
    target = neural_player.MiniMaxDQN(model, 4, True)
    opponent = player.RandomMTS(30, -1)

    print(play(target, opponent, PLAY_NUM, DUMP_BOARD))


def play(target, opponent, play_num, dump_board):
    # kougo
    players = {
        reversi.BLACK: target,
        reversi.WHITE: opponent
    }
    wons = 0
    for i in range(play_num):
        print("game:", i, end='\n' if dump_board else "\r")

        board = reversi.create_board()
        if dump_board:
            reversi.print_board(board)
        
        turn = reversi.BLACK
        while reversi.can_put(board):
            hand = players[turn].select( board, turn)
            if hand is not None:
                board = reversi.put(board, turn, hand)
                if dump_board:
                    reversi.print_board(board)
            turn = -turn
        
        won = reversi.judge(board)
        target_player = reversi.BLACK if i%2 == 0 else reversi.WHITE
        if dump_board:
            if won == target_player:
                print("Target won")
            elif won == -target_player:
                print("Target lose")
            else:
                print("draw")
        
        if won == target_player:
            wons += 1

        # change
        tmp = players[reversi.BLACK]
        players[reversi.BLACK] = players[reversi.WHITE]
        players[reversi.WHITE] = tmp
    
    if dump_board:
        print("{0} ({1}/{2})".format(wons/PLAY_NUM, wons, PLAY_NUM))
    return wons/play_num

def evaluate_model(model, play_num):
    target = neural_player.DQN(model, False)
    opponent = player.RandomMTS(50, -1)
    return play(target, opponent, play_num, False)

if __name__ == '__main__':
    _main()
