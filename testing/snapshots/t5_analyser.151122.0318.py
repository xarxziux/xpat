#!/usr/bin/python3

#Copyright 2015 xarxziux

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

PVTot = 5

#pgnin = open("20games.pgn", "r")
#pgnout = open("20games_out.pgn", "a")

pgnin = open("testversions/testgame.pgn", "r")
pgnout = open("testversions/testoutput.pgn", "a")

dataout = open("testversions/testdata.txt", "a")

engine = chess.uci.popen_engine("stockfish6")
engine.uci()

engine.setoption({"Hash":512})
engine.setoption({"MultiPV":PVTot})
engine_data = chess.uci.InfoHandler()
engine.info_handlers.append(engine_data)

next_game = chess.pgn.read_game(pgnin)

i = 0

while next_game:
#while i < 1:
	
	print ("Analysing game ", i+1)
	this_node = next_game
	
	while this_node.variations:
		
		#next_node = this_node.variation(0)
		
		running_board = this_node.board()
		
		if (running_board.is_checkmate()):
			
			if (running_board.turn):
				
				this_node.comment = "White is in checkmate."
				
			else:
				
				this_node.comment = "Black is in checkmate."
				
			break
			
		elif (running_board.is_stalemate()):
			
			this_node.comment = "Position is stalemate."
			break
			
		#else:
		
		#next_game.add_variation (chess.Move.from_uci("0000"), starting_comment = "No comment!")
		#next_node.comment = "No comment!"
		
		engine.position(running_board)
		engine.go(depth=10)
		
		i = 0
		
		for i in engine_data.info["pv"]:
			
			pvmove = engine_data.info["pv"][i][0]
			pvscore = engine_data.info["score"][i].cp
			
			if not running_board.turn:
				
				pvscore = -pvscore
				
			this_node.add_variation (pvmove,starting_comment = str(pvscore))
			
		#print
		#print ("Result = ", next_game.headers["Result"])
		#dataout.write (str(engine_data.info))
		
		# for i in range(1,PVTot+1):
		
		# if i in engine_data.info["pv"]:
		# #print engine_data.info["pv"][i]
		# #print ("PV %i: %s, score: %i") % (i, engine_data.info["pv"][i][0], engine_data.info["score"][i].cp) 
		# print ("PV", i,":",engine_data.info["pv"][i][0], "score:", engine_data.info["score"][i].cp) 
		# #print()
		# #print()
		
		#this_node = next_node
		this_node = this_node.variation(0)
		
	pgnout.write(str(next_game))
	pgnout.write("\n\n")
	next_game = chess.pgn.read_game(pgnin)
	
	# if (running_board.turn):
		
		# print (engine_data.info)
		# #print ("Score =", engine_data.info["score"][1].cp)
		
	# else:
		
		# print ("Score =", engine_data.info)
		# #print ("Score =", -(engine_data.info["score"][1]))
		# #print ("Score =", -(engine_data.info["score"][1].cp))
		
	i += 1
	next_game = chess.pgn.read_game(pgnin)
	
print (i, " boards printed.")

engine.quit()
pgnin.close()
#pgnout.close()
dataout.close()





