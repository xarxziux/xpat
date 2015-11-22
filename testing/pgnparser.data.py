#!/usr/bin/python3

import chess, chess.pgn, chess.uci

pgn = open("schemingmind.pgn")

first_game = chess.pgn.read_game(pgn)

#print "first_game:"
#print dir(first_game)
#print (first_game)    #Print PGN list
'''
first_game:
['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'add_main_variation', 'add_variation', 'board', 'board_cached', 'comment', 'demote', 'end', 'errors', 'export', 'has_variation', 'headers', 'is_main_line', 'is_main_variation', 'move', 'nags', 'parent', 'promote', 'promote_to_main', 'remove_variation', 'root', 'san', 'setup', 'starting_comment', 'starts_variation', 'variation', 'variations']
[Event "For New Members (#94)  10d+1d/m"]
[Site "SchemingMind.com"]
[Date "2014.05.09"]
[Round "-"]
[White "hardpawn"]
[Black "xarxziux"]
[Result "0-1"]
[WhiteElo "1640"]
[BlackElo "1938"]
[ECO "B07m"]
[WhiteCountry "AUS"]
[BlackCountry "IRL"]
[WhiteRD "109"]
[BlackRD "119"]
[GameID "358192"]
[Annotator "Critter 1.6a 64-bit (60 sec)"]

1. e4 d6 2. d4 Nf6 3. Nc3 e5 4. dxe5 dxe5 5. Nf3 Qxd1+ 6. Nxd1 Nxe4 7. Nxe5 Nd7 8. Nf3 Bc5 9. Be3 O-O 10. Bd3 Ndf6 11. O-O Bg4 12. Be2 Bxe3 13. Nxe3 Bxf3 14. Bxf3 Nd2 15. Rfd1 Nxf3+ 16. gxf3 Rfd8 17. c4 c6 18. Nf5 Kf8 19. Nd6 b6 20. Rd3 Rd7 21. Rad1 Rad8 22. b4 c5 23. bxc5 bxc5 24. Kf1 Ne8 25. Ke2 Rxd6 26. R1d2 Rxd3 27. Rxd3 Rxd3 28. Kxd3 Ke7 29. Kc3 Nd6 30. Kb3 Ke6 31. Ka4 Nxc4 32. Kb5 Kd5 33. a4 Nd6+ 34. Ka6 c4 0-1
'''

#print "Variation:"
#print first_game.variation
#print "Variations:"
#print first_game.variations
'''
Variation:
<bound method Game.variation of <chess.pgn.Game object at 0x7f15cd090390>>
Variations:
[<chess.pgn.GameNode object at 0x7f15ccfc8690>]
'''

#print "Variation:"
#print dir(first_game.variation)
#print "Variations:"
#print dir(first_game.variations)
'''
Variation:
['__call__', '__class__', '__cmp__', '__delattr__', '__doc__', '__format__', '__func__', '__get__', '__getattribute__', '__hash__', '__init__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__self__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'im_class', 'im_func', 'im_self']
Variations:
['__add__', '__class__', '__contains__', '__delattr__', '__delitem__', '__delslice__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getslice__', '__gt__', '__hash__', '__iadd__', '__imul__', '__init__', '__iter__', '__le__', '__len__', '__lt__', '__mul__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', '__rmul__', '__setattr__', '__setitem__', '__setslice__', '__sizeof__', '__str__', '__subclasshook__', 'append', 'count', 'extend', 'index', 'insert', 'pop', 'remove', 'reverse', 'sort']
'''

#print "Variation:"
#print first_game.variation(0)
#print "Variations:"
#print first_game.variations(0)
'''
d6 2. d4 Nf6 3. Nc3 e5 4. dxe5 dxe5 5. Nf3 Qxd1+ 6. Nxd1 Nxe4 7. Nxe5 Nd7 8. Nf3 Bc5 9. Be3 O-O 10. Bd3 Ndf6 11. O-O Bg4 12. Be2 Bxe3 13. Nxe3 Bxf3 14. Bxf3 Nd2 15. Rfd1 Nxf3+ 16. gxf3 Rfd8 17. c4 c6 18. Nf5 Kf8 19. Nd6 b6 20. Rd3 Rd7 21. Rad1 Rad8 22. b4 c5 23. bxc5 bxc5 24. Kf1 Ne8 25. Ke2 Rxd6 26. R1d2 Rxd3 27. Rxd3 Rxd3 28. Kxd3 Ke7 29. Kc3 Nd6 30. Kb3 Ke6 31. Ka4 Nxc4 32. Kb5 Kd5 33. a4 Nd6+ 34. Ka6 c4
Variations:
Traceback (most recent call last):
  File "pgnparser.data.py", line 58, in <module>
    print first_game.variations(0)
TypeError: 'list' object is not callable)
'''

#print "Variation:"
#print first_game.variation(0)
#print first_game.variation(1)
#print first_game.variation(2)
'''
Variation:
d6 2. d4 Nf6 3. Nc3 e5 4. dxe5 dxe5 5. Nf3 Qxd1+ 6. Nxd1 Nxe4 7. Nxe5 Nd7 8. Nf3 Bc5 9. Be3 O-O 10. Bd3 Ndf6 11. O-O Bg4 12. Be2 Bxe3 13. Nxe3 Bxf3 14. Bxf3 Nd2 15. Rfd1 Nxf3+ 16. gxf3 Rfd8 17. c4 c6 18. Nf5 Kf8 19. Nd6 b6 20. Rd3 Rd7 21. Rad1 Rad8 22. b4 c5 23. bxc5 bxc5 24. Kf1 Ne8 25. Ke2 Rxd6 26. R1d2 Rxd3 27. Rxd3 Rxd3 28. Kxd3 Ke7 29. Kc3 Nd6 30. Kb3 Ke6 31. Ka4 Nxc4 32. Kb5 Kd5 33. a4 Nd6+ 34. Ka6 c4
Traceback (most recent call last):
  File "pgnparser.data.py", line 70, in <module>
    print first_game.variation(1)
  File "/usr/local/lib/python2.7/dist-packages/chess/pgn.py", line 180, in variation
    raise KeyError("variation not found")
KeyError: 'variation not found'
'''

#print "Variation:"
#print first_game.variation(0)(0)
'''
Variation:
Traceback (most recent call last):
  File "pgnparser.data.py", line 84, in <module>
    print first_game.variation(0)(0)
TypeError: 'GameNode' object is not callable
'''

node = first_game
running_board = chess.Board()

#print "node:"
#print node
#print "running_board:"
#print running_board
'''
node:
[Event "For New Members (#94)  10d+1d/m"]
[Site "SchemingMind.com"]
[Date "2014.05.09"]
[Round "-"]
[White "hardpawn"]
[Black "xarxziux"]
[Result "0-1"]
[WhiteElo "1640"]
[BlackElo "1938"]
[ECO "B07m"]
[WhiteCountry "AUS"]
[BlackCountry "IRL"]
[WhiteRD "109"]
[BlackRD "119"]
[GameID "358192"]
[Annotator "Critter 1.6a 64-bit (60 sec)"]

1. e4 d6 2. d4 Nf6 3. Nc3 e5 4. dxe5 dxe5 5. Nf3 Qxd1+ 6. Nxd1 Nxe4 7. Nxe5 Nd7 8. Nf3 Bc5 9. Be3 O-O 10. Bd3 Ndf6 11. O-O Bg4 12. Be2 Bxe3 13. Nxe3 Bxf3 14. Bxf3 Nd2 15. Rfd1 Nxf3+ 16. gxf3 Rfd8 17. c4 c6 18. Nf5 Kf8 19. Nd6 b6 20. Rd3 Rd7 21. Rad1 Rad8 22. b4 c5 23. bxc5 bxc5 24. Kf1 Ne8 25. Ke2 Rxd6 26. R1d2 Rxd3 27. Rxd3 Rxd3 28. Kxd3 Ke7 29. Kc3 Nd6 30. Kb3 Ke6 31. Ka4 Nxc4 32. Kb5 Kd5 33. a4 Nd6+ 34. Ka6 c4 0-1
running_board:
r n b q k b n r
p p p p p p p p
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
P P P P P P P P
R N B Q K B N R
'''
















#'''
engine = chess.uci.popen_engine("stockfish6")
engine.uci()

PVTot = 5
#engine.setoption({"Hash":512}, {"MultiPV":PVTot})
engine.setoption({"MultiPV":PVTot})
engine.setoption({"Hash":512})

engine_data = chess.uci.InfoHandler()
engine.info_handlers.append(engine_data)
#print dir(engine.infohandlers)

move_count = 1
white_to_move = True


while node.variations:
    next_node = node.variation(0)
    
    if white_to_move:
      print ("White move "),
      print (move_count, ":", node.move),
      #print (": "),
      white_to_move = False
    else:
      print ("Black move"),
      print (move_count, ":", node.move),
      #print (": "),
      white_to_move = True
      move_count = move_count + 1
      
    #print (node.move)
    #print
    running_board = node.board()
    #print(running_board)
    engine.position(running_board)
    engine.go(depth=10)
    #print engine.bestmove
    #print engine_data.info[1]

    for i in range(1,PVTot+1):
         
         if i in engine_data.info["pv"]:
             #print engine_data.info["pv"][i]
             #print ("PV %i: %s, score: %i") % (i, engine_data.info["pv"][i][0], engine_data.info["score"][i].cp) 
             print ("PV", i,":", engine_data.info["pv"][i][0], "score: ", engine_data.info["score"][i].cp) 
             #print 
             #print
    
    #print engine.multipv
    #print engine_data.BestMove
    #print engine_data.pv(3)
    #print (running_board)
    
    print()
    print()
    #game_list = game_list + " " + node.board().san(next_node.move)
    #print(node.board().san(next_node.move))
    #print (game_list)
    node = next_node

#print engine_data.info
#print engine_data.pv(1)
#print engine_data.pv(2)
#print engine_data.pv(3)




#'''
engine.quit()
pgn.close()


