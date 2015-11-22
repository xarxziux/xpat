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
pv_max = 5
search_depth = 20
hash_size = 128

#PGN files
pgnin = open("pgn/gamesin.pgn", "r")
pgnout = open("pgn/gamesout.pgn", "a")

#Engine set-up
engine = chess.uci.popen_engine(engine_name)
engine.uci()
engine.setoption({"Hash":hash_size})
engine.setoption({"MultiPV":pv_max})
engine_data = chess.uci.InfoHandler()
engine.info_handlers.append(engine_data)

next_game = chess.pgn.read_game(pgnin)

i = 0

while next_game:
	
	print ("Analysing game ", i+1)
	this_node = next_game
	
	while this_node.variations:
		
		running_board = this_node.board()
		
		#Section not required yet
		#if (running_board.is_checkmate()):
		#	
		#	if (running_board.turn):
		#		
		#		this_node.comment = "White is in checkmate."
		#		
		#	else:
		#		
		#		this_node.comment = "Black is in checkmate."
		#		
		#	break
		#	
		#elif (running_board.is_stalemate()):
		#	
		#	this_node.comment = "Position is stalemate."
		#	break
		#	
		#else:
		
		engine.position(running_board)
		engine.go(depth=search_depth)
		
		for j in engine_data.info["pv"]:
			
			pvmove = engine_data.info["pv"][j][0]
			pvscore = engine_data.info["score"][j].cp
			
			if not running_board.turn:
				
				pvscore = -pvscore
				
			this_node.add_variation (pvmove,starting_comment = str(pvscore))
			
		print (".", end = "")
		this_node = this_node.variation(0)
		
	pgnout.write(str(next_game))
	pgnout.write("\n\n")
	next_game = chess.pgn.read_game(pgnin)
	
	i += 1
	next_game = chess.pgn.read_game(pgnin)
	
print (i, " boards printed.")

engine.quit()
pgnin.close()
pgnout.close()





