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
search_depth = 10
hash_size = 128
thread_count = 1

#PGN files
pgnin = open("pgn/gamesin.pgn", "r")
pgnout = open("pgn/gamesout.pgn", "a")


def get_score(eng_score, white_to_move):
	
	if (eng_score.mate):
		
		if (white_to_move):
		
			white_score = 1000
			
		else:
			
			white_score = -1000
			
	else:
	
		if (white_to_move):
			
			white_score = (int(eng_score.cp))
			
		else:
			
			white_score = (int(-(eng_score.cp)))
			
		if (white_score > 1000):
			
			white_score = 1000
			
		if (white_score < -1000):
			
			white_score = -1000
			
		
	return white_score


def init_engine (eng_settings):
	'''Engine start-up'''
	
	new_engine = chess.uci.popen_engine(eng_settings['name'])
	new_engine.uci()
	
	if 'hash' in eng_settings:
		
		new_engine.setoption({"Hash":eng_settings['hash']})
		
	if 'threads' in eng_settings:
		
		new_engine.setoption({"Threads":eng_settings['threads']})
		
	if 'multipv' in eng_settings:
		
		new_engine.setoption({"MultiPV":eng_settings['multipv']})
		
	else:
		
		new_engine.setoption({"MultiPV":5})
		
	return new_engine


def main():
	
	#Engine set-up
	user_eng_settings = {'name' : engine_name, 'hash' : hash_size, 'multipv' :
			pv_max, 'threads' : thread_count}
	engine = init_engine (user_eng_settings
	)
	engine_data = chess.uci.InfoHandler()
	engine.info_handlers.append(engine_data)
	
	next_game = chess.pgn.read_game(pgnin)
	
	i = 0
	
	while next_game:
		
		print ("Analysing game ", i+1)
		this_node = next_game.end().parent
		
		while this_node:
			
			#last_node = this_node.end()
			running_board = this_node.board()
			
			#if (running_board.is_checkmate() or (running_board.is_stalemate())):
			#	
			#	pass
			#	
			#else:
			
			engine.position(running_board)
			engine.go(depth=search_depth)
			
			for j in engine_data.info["pv"]:
				
				pvmove = engine_data.info["pv"][j][0]
				pvscore = (get_score (engine_data.info["score"][j], running_board.turn))/100
				this_node.add_variation (pvmove,starting_comment = str(pvscore))
				
			print (".", end = "", flush=True)
			this_node = this_node.parent
			
		print()
		
		pgnout.write(str(next_game))
		pgnout.write("\n\n")
		
		i += 1
		next_game = chess.pgn.read_game(pgnin)
		
	print (i, " boards printed.")
	
	engine.quit()
	pgnin.close()
	pgnout.close()


if __name__ == "__main__":
	#main(sys.argv[1:])
	main()



