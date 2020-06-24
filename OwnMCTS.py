# -*- coding: utf-8 -*-

import math
import random
import chess 
import chess.svg 
import chess.engine
from IPython.display import display
import time
import matplotlib.pyplot as plt

def rollout(startboard):
    #Tahtanin pozisyonundan oyun bitene kadar rastgele hamleler yapiyor. Oyun bitiminde puani geri donduruyor.
    for x in range(0,1):
        board = chess.Board(startboard.fen())
        while (not board.is_game_over(claim_draw=False)):
            randomMove = random.choice([move for move in board.legal_moves]) # Yapilabilecek hamlelerden rastgele hamleler seciliyor.
            board.push_uci(randomMove.uci())
        result = board.result()
        #print(result)
        if (result == '1/2-1/2'):
            # print("Berabere")
            scor = 0.5
        else:
            if (result == '1-0'):
                # print("Zafer1")
                scor = 1
            else:
                # print("Zafer2")
                scor = 0
    return scor

class Node:
    
    def __init__(self, move = None, parent = None, board = None):
        self.move = move
        self.board = board
        self.parent = parent
        self.childs = []
        self.score = 0
        self.playouts = 0
        self.vUntriedMoves = [move for move in board.legal_moves]
        self.col = board.turn
        
    def setScore(self,value): # Scoru ve hamle sayisini tutuyor.
        self.playouts += 1
        self.score += value
        
    def SelectChild(self):
        eps = float(1e-6) # 0 a bolunme hatasi vermemesi icin.

        #Wi = c.score - > stands for the number of wins for the node considered after the i-th move 
        #ni = c.playouts ->  stands for the number of simulations for the node considered after the i-th move 
        #Ni = self(parent).playouts ->  stands for the total number of simulations after the i-th move run by the parent node of the one considered
        #c = Exp ->  is the exploration parameter—theoretically equal to √2; in practice usually chosen empirically
       

        # selectedMove = sorted(self.childs, key = lambda c: c.score/(c.playouts + eps) + Exp * math.sqrt(math.log(self.playouts)/(c.playouts+eps)))[-1]
        selectedMove = sorted(self.childs, key = lambda c: c.score/(c.playouts + eps) + math.sqrt(2*math.log(self.playouts)/(c.playouts+eps)))[-1]
        return selectedMove
           
    def AddChild(self, randomMove, board):
        newNode = Node(move = randomMove, parent = self, board = board)
        self.vUntriedMoves.remove(randomMove)
        self.childs.append(newNode)
        return newNode

   
def MCTS(rootfen,itermax, verbose = False):
    root = Node(board = chess.Board(rootfen))
    
    for i in range(itermax):
        node = root
        board = chess.Board(rootfen).copy()
        
        #Selection
        while (node.vUntriedMoves == []) and (node.childs != []):
            node = node.SelectChild()
            board.push_uci(node.move.uci())
        
        #Expand
        if node.vUntriedMoves != []:
            randomMove = random.choice(node.vUntriedMoves)
            board.push_uci(randomMove.uci())
            node = node.AddChild(randomMove,chess.Board(board.fen())) #Secilen dugum ekleniyor.
            
        #Simulation
        result = rollout(chess.Board(board.fen()))
        
        #Backprobagtion
        while node != None:
            if node.col:
                node.setScore(result)
                node = node.parent
            else:
                node.setScore(1-result)
                node = node.parent
      
    return sorted(root.childs, key = lambda c: c.playouts)[-1].move # En iyi hamle geri donduruluyor.



# TODOS
# Yapilan her hamlaenin stockfish scorunu sakla, tablolastir. ++ 
# Farkli iterasyon ve expolaration paremetrelerininin, hesaplama suresini sakla, karsilastir. +
# Rapor, Video + 


board = chess.Board()

# YZ nin yaptigi hamleler, stockfish satranc motoruyla degerlendirilmektedir.
engine = chess.engine.SimpleEngine.popen_uci("/home/robotic/Downloads/stockfish-11-linux/stockfish-11-linux/src/stockfish")

# board.push_uci(MCTS(board.fen(),iterN).uci())

# info = engine.analyse(board, chess.engine.Limit(time=0.1))
# print(info)

# # print(float(str(info["score"])))

WhiteStockScore = [] # Beyazin hamlerinin stockFish scoru
BlackStockScore = [] # Siyahin hamlelerinin stockFish scoru
WhiteTimes = [] #   Beyazin hamle hesaplama suresi
BlackTimes = [] #   Siyahin hamle hesaplama suresi

iterN =  100 # - > iteration number

while (not board.is_game_over(claim_draw=False)):
    if (board.turn):

        info = engine.analyse(board, chess.engine.Limit(time=0.1))
        puan = str(info["score"])
        if puan.startswith('#'):
            puan = puan.replace("#","")
        WhiteStockScore.append(float(puan))


        startTime = time.time()
        board.push_uci(MCTS(board.fen(),iterN).uci())
        endTime = time.time()
        
        WhiteTimes.append(endTime-startTime)

        print("--------------")
       
        display(board)
        if board.is_checkmate():
            print("Beyaz Kazandi")
            break
    else:

        info = engine.analyse(board, chess.engine.Limit(time=0.1))

        puan = str(info["score"])
        if puan.startswith('#'):
            puan = puan.replace("#","")

        BlackStockScore.append(float(puan))


        # move = input("Hamleni yap")
        startTime = time.time()
        move = MCTS(board.fen(),10).uci()
        endTime = time.time()
        board.push_uci(move)
        BlackTimes.append(endTime-startTime)
        print("--------------")
        display(board)

        if board.is_checkmate():
            print("Siyah Kazandi")


if(board.is_checkmate() == False):
    print("Berabere")

engine.quit()

#Tablolari Bas.

f = plt.figure(1)
plt.plot(WhiteStockScore)
plt.ylabel('WhiteScore')
plt.xlabel('chessMove')
# f.show()

g = plt.figure(2)
plt.plot(BlackStockScore)
plt.ylabel('BlackScore')
plt.xlabel('chessMove')
# g.show()

h = plt.figure(3)
plt.plot(WhiteTimes)
plt.ylabel('White calculation times')
plt.xlabel('chess move')
# h.show()

e = plt.figure(4)
plt.plot(BlackTimes)
plt.ylabel('Black calculation times')
plt.xlabel('chess move')
# e.show()

plt.show()






