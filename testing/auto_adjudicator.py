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

#Engine set-up
engine = chess.uci.popen_engine(engine_name)
engine.uci()
engine.setoption({"Hash":hash_size})
engine_data = chess.uci.InfoHandler()
engine.info_handlers.append(engine_data)

next_game = chess.pgn.read_game(pgnin)

i = 0

while next_game:
	
	this_node = next_game.end()
	
	running_board = this_node.board()
		
	if (running_board.is_checkmate() or (running_board.is_stalemate())):
		
		next_game = chess.pgn.read_game(pgnin)
		continue
		
	print ("Analysing game ", i+1)
	engine.position(running_board)
	engine.go(depth=search_depth)
	print ("Analysis complete."	)
	
	dataout.write (str(engine_data.info)	)
	
	print ("Data written.")
	
	i += 1
	next_game = chess.pgn.read_game(pgnin)
	
	print ("Back to top.")
	
print (i, " boards printed.")

engine.quit()
pgnin.close()
pgnout.close()





