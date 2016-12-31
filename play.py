#!/usr/bin/env python

import os, random, time
import reversi, player, neural_player

DUMP_SEARCH = True
DUMP_TIME = True

def load_dqn_model():
    from keras.models import load_model
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "./output/best_model.h5")
    model = load_model(MODEL_PATH)
    return model

# opponent = player.RandomUniform()
opponent = player.RandomMTS(1000, -1, DUMP_SEARCH)
# opponent = neural_player.DQN(load_dqn_model(), DUMP_SEARCH)
# opponent = neural_player.MiniMaxDQN(load_dqn_model(), 2, DUMP_SEARCH)


player_color = reversi.BLACK if bool(random.getrandbits(1)) else reversi.WHITE
players = {
    player_color: player.StdInput(),
    -player_color: opponent
}

board = reversi.create_board()
reversi.print_board(board)
turn = reversi.BLACK
while reversi.can_put(board):
    start = time.time()
    hand = players[turn].select(board, turn)
    if DUMP_TIME:
        print("elapsed time: {0} sec".format(time.time()-start))
    if hand is not None:
        board = reversi.put(board, turn, hand)
        reversi.print_board(board)
    turn = -turn

won = reversi.judge(board)
if won == player_color:
    print("you won")
elif won == -player_color:
    print("you lose")
else:
    print("draw")