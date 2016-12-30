import math, random
import numpy as np
import reversi

class Player:
    def __init__(self):
        pass

    def select(self, board, color):
        return None

class StdInput(Player):
    def __init__(self):
        super().__init__()

    def select(self, board, color):
        if len(reversi.hands(board, color)) == 0:
            return None
        return self.ask(board, color)

    def ask(self, board, color):
        print("you are", "X" if color == reversi.BLACK else "O")
        while True:
            s = input("input position (ex. A3):")
            if len(s) == 2:
                x = "ABCDEFGH".find(s[0])
                y = "12345678".find(s[1])
                if reversi.can_put(board, color, (x, y)):
                    return (x, y)
                else:
                    print("Can't put there'")

class RandomUniform(Player):
    def __init__(self):
        super().__init__()

    def select(self, board, color):
        return self.select_randomly(board, color)

    def select_randomly(self, board, color):
        hands = reversi.hands(board, color)
        if len(hands) == 0:
            return None
        else:
            choice = random.randrange(len(hands))
            return hands[choice]


class RandomMTS(Player):
    def __init__(self, playout_num=100, max_depth=-1, dump_nodes=False):
        super().__init__()
        self.playout_num = playout_num
        self.max_depth = max_depth
        self.dump_nodes = dump_nodes

    def select(self, board, color):
        return self.search_and_select(board,
                                      color,
                                      self.playout_num,
                                      self.max_depth)

    def search_and_select(self, board, color, playout_num, max_depth):
        root_node = MTSNode(None, board, color, max_depth)
        for i in range(playout_num):
            node = root_node

            while len(node.hands) == 0 and len(node.children) > 0:
                node = node.select_node()

            if len(node.hands) > 0:
                node = node.expand_child()

            win = self.playout(node.board, node.color)
            node.backpropagate(win)
        move = root_node.select_move()
        if self.dump_nodes:
            root_node.dump()
            if move is None:
                print("pass")
            else:
                print("select:", reversi.coord_to_board(move))
        return move

    def playout(self, board, color):
        board = np.copy(board)
        pass_count = 0
        while True:
            hands = reversi.hands(board, color)

            if len(hands) > 0:
                choice = random.randrange(len(hands))
                hand = hands[choice]
                board = reversi.put(board, color, hand)
                pass_count = 0
            else:
                pass_count += 1
                if pass_count > 1:
                    break
            color = -color
        return reversi.judge(board)

class MTSNode:
    def __init__(self, parent, board, color, max_depth=-1, move = None):
        self.parent = parent

        self.board = board
        self.color = color

        self.move = move
        self.max_depth = max_depth

        self.children = []
        if max_depth == 0:
            self.hands = []
        else:
            self.hands = reversi.hands(self.board, self.color)
            if len(self.hands) == 0 and reversi.can_put(board):
                # pass
                self.hands.append(None)

        # number of wins of oppent(=-self.color)
        self.opponent_total_wins = 0
        self.total_playouts = 0

    def expand_child(self):
        move = self.hands.pop(random.randrange(len(self.hands)))
        if move is None:
            child = MTSNode(self, self.board, -self.color, self.max_depth-1, None)
        else:
            board = reversi.put(self.board, self.color, move)
            child = MTSNode(self, board, -self.color, self.max_depth-1, move)
        self.children.append(child)
        return child

    def select_node(self):
        max_score = -9999
        ret = None
        for child in self.children:
            ucb = self.ucb(child)
            if max_score <= ucb:
                max_score = ucb
                ret = child
        return ret

    def select_move(self):
        if not self.parent is None:
            raise Exception("selectMove is only for rootNode.")
        if len(self.children) == 0 and len(self.hands) == 0:
            return None
        else:
            ret = None
            max_score = -10000
            for child in self.children:
                score = child.opponent_total_wins / child.total_playouts
                if score >= max_score:
                    ret = child
                    max_score = score
            return ret.move

    def ucb(self, child):
        c = 1
        return child.opponent_total_wins / child.total_playouts \
                + c * np.sqrt(math.log(self.total_playouts) / child.total_playouts)

    def backpropagate(self, win):
        node = self
        while not node is None:
            if node.color == -win:
                node.opponent_total_wins += 1
            node.total_playouts += 1
            node = node.parent

    def get_root_node(self):
        node = self
        while not node.parent is None:
            node = node.parent
        return node

    def print_route(self):
        node = self
        while not node.parent is None:
            print(node.move, end="<-")
            node = node.parent
            print("")

    def dump(self, ucb=0, pad=0):
        print("- "*pad, end="")
        mv = reversi.coord_to_board(self.move) if self.move is not None else None
        print("{0}:{1} {2:.3f}({3}/{4}) ucb:{5:.3f}".format(
            "BLACK" if self.color == reversi.BLACK else "WHITE",
            mv,
            self.opponent_total_wins/self.total_playouts,
            self.opponent_total_wins,
            self.total_playouts,
            ucb))
        for child in self.children:
            child.dump(self.ucb(child), pad+1)
