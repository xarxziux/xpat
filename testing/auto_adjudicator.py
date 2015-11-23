#!/usr/bin/python3

#Copyright 2015 Alan Delaney

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import chess, chess.pgn, chess.uci

#Engine settings
engine_name = "stockfish6"
search_depth = 10
hash_size = 1024

#PGN files
pgnin = open("pgn/gamesin.pgn", "r")
pgnout = open("pgn/gamesout.pgn", "a")
dataout = open("pgn/dataout.txt", "a")

def start_engine (eng_name, eng_hash=False):
	'''Engine set-up'''
	new_engine = chess.uci.popen_engine(eng_name)
	new_engine.uci()
	
	if eng_hash:
		
		new_engine.setoption({"Hash":eng_hash})
		
	return new_engine


def get_score(eng_score, white_to_move):
	
	if (eng_score.mate):
		
		if (white_to_move):
		
			white_score = 1000
			
		else:
			
			white_score = -1000
			
	else:
	
		if (white_to_move):
			
			white_score = int(eng_score.cp)
			
		else:
			
			white_score = int(-(eng_score.cp))
			
	return white_score


def main():

	engine = start_engine("stockfish6", 128)
	engine_data = chess.uci.InfoHandler()
	engine.info_handlers.append(engine_data)
	
	next_game = chess.pgn.read_game(pgnin)
	
	i = 0
	
	while next_game:
		
		this_node = next_game.end()
		
		running_board = this_node.board()
		
		if (running_board.is_checkmate()):
			
			print (str(next_game.headers["White"]), "V", str(next_game.headers["Black"]))
			engine.position(running_board)
			engine.go(depth=search_depth)
			print (engine_data.info["score"][1])
			
			if running_board.turn:
				
				print ("White checkmates.")
				print()
				print()
				
			else:
				
				print ("Black checkmates.")
				print()
				print()
				
		elif (running_board.is_stalemate()):
			
			print (next_game.headers["White"], "V", next_game.headers["Black"])
			engine.position(running_board)
			engine.go(depth=search_depth)
			print (engine_data.info["score"][1])
			print ("Stalemate.")
			print()
			print()
			
		else:
			
			print (next_game.headers["White"], "V", next_game.headers["Black"])
			print ("Analysing game ", i+1)
			engine.position(running_board)
			engine.go(depth=search_depth)
			#print ("Analysis complete."	)
			
			#dataout.write (str(engine_data.info))
			
			pv_score = get_score(engine_data.info["score"][1], running_board.turn)
			print (engine_data.info["score"][1])
			print ("Score:", str(pv_score))
			print ("Result:", next_game.headers["Result"])
			print (pv_score - 20)
			
			if (pv_score > 20):
				
				print (pv_score, "< 20.")
				next_game.headers["Result"] = "1-0"
				print ("Result:", next_game.headers["Result"])
				
			else:
				
				print (pv_score, "< 20.")
			
			print()
			print()
			
			
		i += 1
		next_game = chess.pgn.read_game(pgnin)
		
	print (i, " boards printed.")
	
	engine.quit()
	pgnin.close()
	pgnout.close()


if __name__ == "__main__":
	#main(sys.argv[1:])
	main()



