#%%
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import pickle

BOARD_ROWS = 3
BOARD_COLS = 3

#%%

# get unique hash of current board state
def getHash(board):
        return str(board.reshape(BOARD_COLS*BOARD_ROWS))

class State:
    def __init__(self, p1, p2):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.p1 = p1
        self.p2 = p2
        self.isEnd = False
        self.boardHash = None
        # init p1 plays first
        self.playerSymbol = 1

        positions = []
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                positions.append((i, j))  # need to be tuple
        self.allPositions = positions
    
    def winner(self):
        # row
        for i in range(BOARD_ROWS):
            if sum(self.board[i, :]) == 3:
                self.isEnd = True
                return 1
            if sum(self.board[i, :]) == -3:
                self.isEnd = True
                return -1
        # col
        for i in range(BOARD_COLS):
            if sum(self.board[:, i]) == 3:
                self.isEnd = True
                return 1
            if sum(self.board[:, i]) == -3:
                self.isEnd = True
                return -1
        # diagonal
        diag_sum1 = sum([self.board[i, i] for i in range(BOARD_COLS)])
        diag_sum2 = sum([self.board[i, BOARD_COLS-i-1] for i in range(BOARD_COLS)])
        # diag_sum = max(diag_sum1, diag_sum2)
        if max(diag_sum1, diag_sum2) == 3:
            self.isEnd = True
            return 1
        if min(diag_sum1, diag_sum2) == -3:
            self.isEnd = True
            return -1
        
        # tie
        # no available positions
        if len(self.__availablePositions()) == 0:
            self.isEnd = True
            return 0
        # not end
        self.isEnd = False
        return None
    
    def __availablePositions(self):
        positions = []
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if self.board[i, j] == 0:
                    positions.append((i, j))  # need to be tuple
        return positions
    
    def updateState(self, position):
        """
        make an action in the game with current player
        return
            state: ndarray
            free positions: list of tuples
            reward: integer
            end: boolean
            next player: Player
        """
        self.board[position] = self.playerSymbol
        # self.showBoard()
        # switch to another player
        self.playerSymbol = -1 if self.playerSymbol == 1 else 1

        win = self.winner()
        reward = 0
        if win is not None:
            # either win, lost, or draw
            if win == 1 or win == -1: reward = win
            else: reward = 0.5

        next_player = self.p1 if self.playerSymbol == 1 else self.p2
        return self.board, self.__availablePositions(), reward, self.isEnd, next_player
    
    # board reset
    def reset(self):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol = 1

    # play with human
    def play(self):
        while not self.isEnd:
            # Player 1
            positions = self.__availablePositions()
            p1_action = self.p1.chooseAction(positions, self.board)
            # take action and upate board state
            self.updateState(p1_action)
            self.showBoard()
            # check board status if it is end
            win = self.winner()
            if win is not None:
                if win == 1:
                    print(self.p1.name, "wins!")
                else:
                    print("tie!")
                self.reset()
                break

            else:
                # Player 2
                positions = self.__availablePositions()
                p2_action = self.p2.chooseAction(positions)

                self.updateState(p2_action)
                self.showBoard()
                win = self.winner()
                if win is not None:
                    if win == -1:
                        print(self.p2.name, "wins!")
                    else:
                        print("tie!")
                    self.reset()
                    break

    def showBoard(self):
        # p1: x  p2: o
        for i in range(0, BOARD_ROWS):
            print('-------------')
            out = '| '
            for j in range(0, BOARD_COLS):
                if self.board[i, j] == 1:
                    token = 'x'
                if self.board[i, j] == -1:
                    token = 'o'
                if self.board[i, j] == 0:
                    token = ' '
                out += token + ' | '
            print(out)
        print('-------------')    

class Player:
    def __init__(self, name, symbol, exp_rate=0.3):
        self.name = name
        self.symbol = symbol
        self.states = []  # record all positions taken
        self.lr = 0.2
        self.exp_rate = exp_rate
        self.decay_gamma = 0.9
        self.states_value = {}  # state -> value
    
    def chooseAction(self, positions, current_board, i=1):
        if len(positions) == 0: return None

        if np.random.uniform(0, 1) <= self.exp_rate*0.999**i:
            # take random action
            action = positions[np.random.choice(len(positions))]
        else:
            value_max = -999
            for p in positions:
                next_board = current_board.copy()
                next_board[p] = self.symbol
                V = self.states_value.get(getHash(next_board))

                # random gernerate a value if this is a new state to introduce randomness
                value = np.random.uniform(-.1, .1) if V is None else V
                # print("value", value)
                if value >= value_max:
                    value_max = value
                    action = p
        # print("{} takes action {}".format(self.name, action))
        return action
    
    # at the end of game, backpropagate and update states value
    def Update_ValueFunction(self, reward):
        for i, st in enumerate(reversed(self.states)):
            if self.states_value.get(st) is None:
                self.states_value[st] = 0

            R = reward if i==0 else self.decay_gamma*reward
            self.states_value[st] += (R - self.states_value[st]) * self.lr
            reward = self.states_value[st]
        # print(self.states_value)
    
    # append a hash state
    def addState(self, state):
        self.states.append(state)
            
    def reset(self):
        self.states = []
        
    def savePolicy(self):
        fw = open('policy_' + str(self.name), 'wb')
        pickle.dump(self.states_value, fw)
        fw.close()

    def loadPolicy(self, file):
        fr = open(file,'rb')
        self.states_value = pickle.load(fr)
        fr.close()

class HumanPlayer:
    def __init__(self, name):
        self.name = name 
    
    def chooseAction(self, positions):
        while True:
            row = int(input("Input your action row:"))
            col = int(input("Input your action col:"))
            action = (row, col)
            if action in positions:
                return action
    
    # append a hash state
    def addState(self, state):
        pass
    
    # at the end of game, backpropagate and update states value
    def Update_ValueFunction(self, reward):
        pass
            
    def reset(self):
        pass

#%%
p1 = Player("p1",1)
p2 = Player("p2",-1)

game = State(p1, p2)
rewards = []
avg_rewards = []

print("training...")
progress_bar = tqdm(range(20000), desc="Avg Reward: 0")
for i in progress_bar:
    end = False
    current_player = p1
    state = game.board
    action = current_player.chooseAction(game.allPositions, state)

    while not end:
        new_state, available_action, reward, end, next_player = game.updateState(action)
        if game.winner(): break

        current_player.addState(getHash(state))
        new_action = next_player.chooseAction(available_action, new_state, i)

        action = new_action
        state = new_state
        current_player = next_player
     
    rewards.append(reward)

    p1.Update_ValueFunction(reward)
    p2.Update_ValueFunction(-reward)
    p1.reset()
    p2.reset()
    game.reset()

    if (i+1) % 1000 == 0:
        avg_reward = sum(rewards[-1000:]) / 1000  # Calculate the average of the last 1000 rewards
        avg_rewards.append(avg_reward)
        progress_bar.set_description(f"Avg Reward: {avg_reward}")

#%%
plt.figure(figsize=(10, 5))
plt.plot(avg_rewards, label='Moving Average Reward per game')
plt.xlabel('Games')
plt.ylabel('Reward')
plt.title('Moving Average of Reward Progress Over Game')
plt.legend()
plt.show()

p1.savePolicy()
p2.savePolicy()
#%%
p1 = Player("computer", 1, exp_rate=0)
p1.loadPolicy("policy_p1")

p2 = HumanPlayer("human")

game = State(p1, p2)
game.play()
# %%
p1.states_value
# %%
