import numpy as np
import reversi
import player

def multiple(board):
    b_t = np.transpose(board) # transpose
    b_r = np.rot90(board, 2) # rotate
    b_rt = np.rot90(b_t, 2) # transpose and rotate

    boards = np.array([[board], [b_t], [b_r], [b_rt]])
    return boards

class DQN(player.Player):
    def __init__(self, model, dump_scores=False):
        super().__init__()
        self.model = model
        self.dump_scores = dump_scores

    def select(self, board, color):
        hands = reversi.hands(board, color)
        if len(hands) == 0:
            return None
        
        actions = [multiple(reversi.put(board, color, h)) for h in hands]
        actions = np.array(actions).reshape(-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE)
        colors = np.array([color]*len(actions)).reshape(-1, 1)

        scores = self.model.predict([
            colors,
            actions
        ])

        scores = scores.reshape([-1, 4])
        scores = np.max(scores, axis=1)
        max_hand = np.argmax(scores)
        if self.dump_scores:
            for h, s in zip(hands, scores):
                print("{0}: {1}".format(h, s))
            print("choose:", hands[max_hand])
        return hands[max_hand]

class MiniMaxDQN(player.Player):
    def __init__(self, model, max_depth = 2, dump_scores=False):
        super().__init__()
        self.model = model
        self.max_depth = max_depth
        self.dump_scores = dump_scores

    def select(self, board, color):
        hands = reversi.hands(board, color)
        if len(hands) == 0:
            return None

        actions = [reversi.put(board, color, h) for h in hands]
        scores = self.check_scores(board, color, actions, 1)
        max_hand = np.argmax(scores)
        if self.dump_scores:
            for h, s in zip(hands, scores):
                print("{0}: {1}".format(h, s))
            print("choose:", hands[max_hand])
        return hands[max_hand]

    def check_scores(self, board, color, actions, depth):
        if depth < self.max_depth:
            scores = []
            for action in actions:
                next_color = -color if reversi.can_put(action, -color) else color
                hands = reversi.hands(action, next_color)
                if len(hands) > 0:
                    next_actions = [reversi.put(action, color, h) for h in hands]
                    next_scores = self.check_scores(action, next_color, next_actions, depth+1)
                    max_score = np.max(next_scores)
                    scores.append(max_score * next_color * color)
                else:
                    won = reversi.judge(action)
                    scores.append(won*color)
            return scores
        else:
            actions = [multiple(action) for action in actions]
            actions = np.array(actions).reshape(-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE)
            colors = np.array([color]*len(actions)).reshape(-1, 1)

            scores = self.model.predict([
                colors,
                actions
            ])

            scores = scores.reshape([-1, 4])
            scores = np.max(scores, axis=1)
            return scores
