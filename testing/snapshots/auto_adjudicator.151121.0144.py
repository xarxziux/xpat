#!/usr/bin/python3

import chess, chess.pgn, chess.uci

pgnin = open("20games.pgn")
#pgnout = open("20games_out.pgn", "a")

#engine = chess.uci.popen_engine("stockfish6")
#engine.uci()

#engine.setoption({"Hash":512})
#engine_data = chess.uci.InfoHandler()
#engine.info_handlers.append(engine_data)

next_game = chess.pgn.read_game(pgnin)

i = 0


end_node = next_game.end()
#end_node = next_game.end().parent

next_game.add_variation (chess.Move.from_uci("d2d4"))

#end_node = next_game.end().parent

last_move = end_node.move
print("Last move =", last_move)

#end_node.parent.add_variation (chess.Move.from_uci("c4d4"),"","Last move")
end_node.parent.add_variation (chess.Move.from_uci(str(last_move)),starting_comment="Last move")
#next_game.add_variation (chess.Move(["d2","d4"]))

# print (end_node)
print (next_game)
print()
print()
print("end_node =", end_node)
print (end_node.parent)
print (end_node.move)
print (end_node.san())
#print()
#print()
#print (end_node.move)
#print (chess.Move.from_uci(end_node.move))


#print next_game.end().move

#next_game = next_game.end

#print (next_game)

#while next_game:
	
	#print (end_node.board())
	
	#print (next_game)
	
	#	if next_game == None:
	#			
	#		break
	
	#running_board = next_game.end().parent.board()
	
	#engine.position(running_board)
	#engine.go(depth=10)
	
	# j = 0
	
	# while j < 10:
	
		# print (next_game)
		# print()
		# print (next_game.variation(0))
		# print()
		# print()
		# next_move = next_game.variation(0)
		
		# #print (next_move)
		
		# next_game = next_move
		
		# j += 1

		
	#print (next_game)
	#print (running_board)
	#print ("Game ", i+1, ":")
	#print ("Result = ", next_game.headers["Result"])
	
	#if (running_board.turn):
	#	print (engine_data.info["score"][1].cp)
	#
	#else:
	#
	#	print (-(engine_data.info["score"][1].cp))
	#	
	#print (running_board.is_checkmate())
	#print (running_board.is_stalemate())
	
	#if (not (running_board.is_checkmate() or running_board.is_stalemate())):
		#print (engine_data.info["pv"][1][0])
		#next_game.add_variation(str(engine_data.info["pv"][1][0]), "", "Stockfish 6 " + str(engine_data.info["score"][1].cp))
	#print()
	#print()
	#next_game.add_variation()
	#print (next_game, file=pgnout, end="\n\n")
	#print (next_game)
	#pgnout.write (str(next_game))
	#pgnout.write ("\n\n")
	
	#i += 1
	#next_game = chess.pgn.read_game(pgnin)
	
#print (i, " boards printed.")
	
#engine.quit()
pgnin.close()
#pgnout.close()



