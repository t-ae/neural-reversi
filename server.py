#!/usr/bin/env python

import json, threading, os
from tornado import ioloop, web, websocket, httpserver
import reversi, player, neural_player

USE_DQN = False
USE_MINIMAX_DQN = False

AI_RANDOM = "RANDOM"
AI_MTS = "MTS"
AI_DQN = "DQN"
AI_MM_DQN = "MM_DQN"

players = {
    AI_RANDOM: player.RandomUniform(),
    AI_MTS: player.RandomMTS(300, -1, True),
}

if USE_DQN or USE_MINIMAX_DQN:
    from keras.models import load_model
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "./output/best_model.h5")
    model = load_model(MODEL_PATH)
    if USE_DQN:
        players[AI_DQN] = neural_player.DQN(model, True)
    if USE_MINIMAX_DQN:
        players[AI_MM_DQN] = neural_player.MiniMaxDQN(model, 2, True)


class WSHandler(websocket.WebSocketHandler):
    __lock = threading.Lock()

    def open(self):
        print("new connection")
        self.now_player = reversi.BLACK
        self.ai = AI_RANDOM
        self.write_message({"command":"init", "size":reversi.BOARD_SIZE, "ai":list(players.keys())})
        self.init_board(reversi.BLACK)

    def on_message(self, message):
        with self.__lock:
            try:
                msg = json.loads(message)
                print(msg)
                if msg["command"] == "put":
                    pos = (msg["position"][0], msg["position"][1])
                    if reversi.can_put(self.board, -self.me, pos):
                        # client put
                        self.board = reversi.put(self.board, -self.me, pos)
                        self.now_player = self.me
                        self.send_update()

                        # server put
                        self.server_put()
                    else:
                        self.send_error("Can't put there.")
                elif msg["command"] == "ai":
                    self.ai = msg["ai"]
                    print("Set AI", self.ai)
                elif msg["command"] == "restart":
                    self.init_board(msg["side"])
                    print("Restart", msg["side"])
                else:
                    self.send_error("invalid command "+msg["command"])
            except (ValueError, KeyError):
                self.send_error("Failed to parse JSON.")


    def on_close(self):
        pass

    def send_error(self, message):
        self.write_message({"command":"error", "message":message})

    def init_board(self, player):
        self.me = -player
        self.board = reversi.create_board()
        self.now_player = reversi.BLACK

        self.send_update()

        if self.me == reversi.BLACK:
            # First hand
            self.server_put()

    def server_put(self):
        player = players[self.ai]
        if player == None:
            self.send_error("Invalid Player:", self.ai)
            return
        cell = player.select(self.board, self.me)
        if cell is None:
            # server pass
            if not reversi.can_put(self.board, -self.me):
                # client pass = end
                self.judge()
                return
            else:
                self.now_player = -self.me
                return

        self.board = reversi.put(self.board, self.me, cell)

        if not reversi.can_put(self.board, -self.me):
            # client pass
            self.send_update()
            self.server_put()
        else:
            self.now_player = -self.me
            self.send_update()

    def send_update(self):
        b = self.board.ravel().astype(int).tolist()
        p = self.now_player
        j = {"command":"update", "player":p, "board": b}
        self.write_message(j)
    
    def judge(self):
        win = reversi.judge(self.board)
        self.write_message({"command":"judge", "winner": win})
        self.now_player = self.me


def make_app():
    return web.Application([
        (r"/ws", WSHandler),
        (r"/(.*)", web.StaticFileHandler,
            {"path": os.path.dirname(__file__)+"/www", "default_filename": "index.html"}),
    ])


if __name__ == "__main__":
    app = make_app()
    http_server = httpserver.HTTPServer(app)
    print("http://127.0.0.1:8888")
    http_server.listen(8888)
    ioloop.IOLoop.current().start()
