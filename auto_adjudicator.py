#!/usr/bin/python3

import chess, chess.pgn, chess.uci

pgn = open("20games.pgn")

engine = chess.uci.popen_engine("stockfish6")
engine.uci()

engine.setoption({"Hash":512})
engine_data = chess.uci.InfoHandler()
engine.info_handlers.append(engine_data)

while True:

	next_game = chess.pgn.read_game(pgn)
	
	if next_game == None:
	
		break
	
	running_board = next_game.end().board()
	
	engine.position(running_board)
	engine.go(depth=10)
	
	print (running_board)
	print (engine_data.info["score"][1].cp)
	#print (engine_data.info["score"])
	
	print()
	print()
	
print ("20 boards printed.")
	

pgn.close()


