#!/usr/bin/python3

import chess, chess.pgn, chess.uci

pgnin = open("20games.pgn")
#pgnout = open("20games_out.pgn", "a")

engine = chess.uci.popen_engine("stockfish6")
engine.uci()

engine.setoption({"Hash":512})
engine_data = chess.uci.InfoHandler()
engine.info_handlers.append(engine_data)

next_game = chess.pgn.read_game(pgnin)

i = 0



while next_game:

	end_node = next_game.end()
	running_board = end_node.board()
	
	print ("Analysing game ", i+1)
	
	if (running_board.is_checkmate()):
		
		if (running_board.turn):
			
			print ("Black is in checkmate.")
			
		else:
			
			print ("White is in checkmate.")
			
		i += 1
		next_game = chess.pgn.read_game(pgnin)
		continue
		
	elif (running_board.is_stalemate()):
		
		print ("Position is stalemate.")
		print()
		i += 1
		next_game = chess.pgn.read_game(pgnin)
		continue
		
	engine.position(running_board)
	engine.go(depth=10)
	
	print ("Result = ", next_game.headers["Result"])
	
	if (running_board.turn):
		
		print ("Score =", engine_data.info["score"][1].cp)
		
	else:
		
		print ("Score =", -(engine_data.info["score"][1].cp))
		
	print ()
	
	i += 1
	next_game = chess.pgn.read_game(pgnin)
	
print (i, " boards printed.")
	
engine.quit()
pgnin.close()
#pgnout.close()





