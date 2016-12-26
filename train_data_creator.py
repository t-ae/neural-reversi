
import numpy as np
import reversi

class TrainDataCreator:

    def __init__(self, model, gamma, epsilon, epsilon_d, epsilon_min):
        self.model = model
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_d = epsilon_d
        self.epsilon_min = epsilon_min

    def curve(self, l):
        x = np.arange(l).astype(float)
        x[3:] = 1.1
        x[0:3] = 0.01 * (x[0:3] + 1) # 0.01, 0.02, 0.03
        return x

    def get_partial(self, record):
        try:
            npz = np.load(record)
            X_board = npz["X_board"][:-1]
            X_color = npz["X_color"]
            X_action = npz["X_board"][1:]
            y_won = npz["y_won"]

            l = len(X_color)
            boards = []
            colors = []

            mask = np.random.uniform(0, 1, l) < self.curve(l)
            boards = np.array(X_board[mask]) # [-1, BOARD_SIZE, BOARD_SIZE]
            colors = np.array(X_color[mask]) # [-1, 1]
            actions = np.array(X_action[mask])
            
            rs = np.zeros([len(colors)]).reshape([-1, 1])
            rs[-1] = colors[-1]*y_won

            return boards, colors, actions, rs
        except:
            return np.zeros([0, reversi.BOARD_SIZE, reversi.BOARD_SIZE]),\
                   np.zeros([0, 1]),\
                   np.zeros([0, reversi.BOARD_SIZE, reversi.BOARD_SIZE]),\
                   np.zeros([0, 1])

    def multiple(self, board):
        b_t = np.transpose(board) # transpose
        b_r = np.rot90(board, 2) # rotate
        b_rt = np.rot90(b_t, 2) # transpose and rotate

        boards = np.array([[board], [b_t], [b_r], [b_rt]])
        return boards

    def create_train_data(self, records, start):
        record_boards = []
        record_colors = []
        record_actions = []
        record_rs = np.zeros([0, 1])
        for record_index in range(start, len(records)):
            record = records[record_index]
            boards, colors, actions, rs= self.get_partial(record)
            record_boards.append(boards)         # [-1, BOARD_SIZE, BOARD_SIZE]
            record_colors.append(colors)         # [-1, 1]
            record_actions.append(actions)       # [-1, BOARD_SIZE, BOARD_SIZE]
            record_rs = np.append(record_rs, rs) # [-1, 1]
            if len(record_rs) > 8192: # data will multiple 4 times later
                break
        else:
            # reach end of records
            return record_index+1, None
        record_boards = np.concatenate(record_boards).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])
        record_colors = np.concatenate(record_colors).reshape([-1, 1])
        record_actions = np.concatenate(record_actions).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])
        return record_index+1, self.__create_train_data(record_boards, record_colors, record_actions, record_rs)
    
    def __create_train_data(self, boards, colors, actions, rs):
        # for train
        X_boards = []
        X_colors = []
        X_actions = []
        # for calculate Rs
        pred_boards = []
        pred_colors = []
        pred_actions = []
        num_action_primes = []
        turn_change = []
        
        for b, c, a, in zip(boards, colors, actions):
            X_boards.append(self.multiple(b))
            X_colors.append([c]*4)
            X_actions.append(self.multiple(a))

            next_c = -c if reversi.can_put(a, -c) else c
            hands = reversi.hands(a, next_c)
            if np.random.uniform(0,1) < self.epsilon and len(hands) > 0:
                # e-greedy
                hands = [hands[np.random.choice(np.arange(len(hands)))]]
            num_action_primes.append(len(hands)*4)
            turn_change.append(c*next_c)
            for hand in hands:
                action_prime = reversi.put(a, next_c, hand)
                pred_boards.append(self.multiple(a))
                pred_colors.append([next_c]*4)
                pred_actions.append(self.multiple(action_prime))

        # predict
        pred_boards = np.array(pred_boards).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])
        pred_colors = np.array(pred_colors).reshape([-1, 1])
        pred_actions = np.array(pred_actions).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])

        preds = self.model.predict([pred_boards, pred_colors, pred_actions], verbose=1)
        
        # calculate Rs
        Rs = np.hstack([rs.reshape([-1,1])]*4).astype(float) # [-1, 4]
        start = 0
        for i in range(len(num_action_primes)):
            num = num_action_primes[i]
            if num > 0:
                r_max = np.max(preds[start:start+num])
                Rs[i] += self.gamma * r_max * turn_change[i]
                start += num
        
        # reshape
        X_boards = np.array(X_boards).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])
        X_colors = np.array(X_colors).reshape([-1, 1])
        X_actions = np.array(X_actions).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])
        y_Rs = Rs.reshape([-1, 1])

        # reduce
        self.epsilon = max(self.epsilon-self.epsilon_d, self.epsilon_min)

        return X_boards, X_colors, X_actions, y_Rs


    def load_test_record(self, path):
        npz = np.load("./test_record.npz")
        boards = []
        actions = []
        for board, action in zip(npz["X_board"], npz["X_action"]):
            b = self.multiple(board)
            boards.append(b)
            a = self.multiple(action)
            actions.append(a)
        test_board = np.array(boards).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])
        test_color = np.hstack([npz["X_color"]]*4).reshape([-1, 1])
        test_action = np.array(actions).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])
        
        return test_board, test_color, test_action
