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

#Settings
white_threshold = 70
black_threshold = -50

def start_engine (eng_name, eng_hash=False):
	'''Engine start-up'''
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

	engine = start_engine("stockfish6", 1024)
	engine_data = chess.uci.InfoHandler()
	engine.info_handlers.append(engine_data)
	
	next_game = chess.pgn.read_game(pgnin)
	
	i = 0
	
	while next_game:
		
		end_node = next_game.end()
		running_board = end_node.board()
		
		if not ((running_board.is_checkmate()) or (running_board.is_stalemate())):
			
			print ("Analysing game ", i+1)
			engine.position(running_board)
			engine.go(depth=search_depth)
			print ("Analysis complete.")
			print()
			print()
			
			pv_score = get_score(engine_data.info["score"][1], running_board.turn)
			end_node.parent.add_variation(end_node.move, starting_comment = (engine_name +
					" " + str(engine_data.info["depth"]) + ": " + str(pv_score)))
			end_node.parent.variation(1).add_variation (engine_data.info["pv"][1][0])
			#end_node.add_variation (, starting_comment = (engine.name +
			
			if ((pv_score >= white_threshold) and (next_game.headers["Result"] != '1-0')):
				
				next_game.headers["Result"] = "1-0"
				end_node.comment = end_node.comment + " - auto-adjusted to 1-0"
				
			elif ((pv_score <= black_threshold) and (next_game.headers["Result"] != '0-1')):
				
				next_game.headers["Result"] = "0-1"
				end_node.comment = end_node.comment + " - auto-adjusted to 0-1"
				
			elif ((pv_score < white_threshold) and (pv_score > black_threshold) and (next_game.headers["Result"] != "1/2-1/2")):
				
				next_game.headers["Result"] = "1/2-1/2"
				end_node.comment = end_node.comment + " - auto-adjusted to 1/2-1/2"
				
			else:
				
				end_node.comment = end_node.comment + " - auto-adjudicator detects no result change necessary"
				
		#print ("Writing to output file.")
		pgnout.write (str(next_game))
		#print ("Written!")
		#print()
		#print()
		pgnout.write ("\n\n")
		
		i += 1
		next_game = chess.pgn.read_game(pgnin)
		
	print (i, " boards printed.")
	
	engine.quit()
	pgnin.close()
	pgnout.close()


if __name__ == "__main__":
	#main(sys.argv[1:])
	main()



