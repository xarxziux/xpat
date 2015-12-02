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

#python-chess imports
import chess
import chess.pgn
import chess.uci
import chess.polyglot


#Engine settings
ENGINE_NAME = "stockfish6"
PV_MAX = 5
SEARCH_DEPTH = 10
HASH_SIZE = 128
THREAD_COUNT = 1


#Files
INPUT_FILE = "pgn/gamesin.pgn"
OUTPUT_FILE = "pgn/gamesout.pgn"
BOOK_FILE = "polyglot/Elo2400.bin"
#BOOK_FILE = "pgn/gamesout.pgn"


#General settings
MATE_SCORE = 1000
CP_THRESHOLD = 300


def get_score(eng_score, white_to_move):
    ''' Convert the UCI score to the score from White's viewpoint '''
    
    if (eng_score.mate):
        
        if (white_to_move):
        
            white_score = MATE_SCORE
            
        else:
            
            white_score = -MATE_SCORE
            
    else:
        
        if (white_to_move):
            
            white_score = (int(eng_score.cp))
            
        else:
            
            white_score = (int(-(eng_score.cp)))
            
        if (white_score > MATE_SCORE):
            
            white_score = MATE_SCORE
            
        if (white_score < -MATE_SCORE):
            
            white_score = -MATE_SCORE
            
        
    return white_score


def init_engine (eng_settings):
    '''Engine set-up'''
    
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


def is_book_position (p_book, c_board):
    ''' Checks if the given position is in the given book '''
    
    try:
        
        p_book.find (c_board)
        return True
        
    except IndexError:
        
        return False
        


def evaluate_position (node, eng):
    
    eng.position(node.board())
    eng.go(depth=SEARCH_DEPTH)


def open_book ():
    
    try:
        
        new_book = chess.polyglot.open_reader (BOOK_FILE)
        
    except FileNotFoundError:
        
        return False
        
    #Validate book
    if is_book_position (new_book, chess.Board()):
        
        return new_book
        
    else:
        
        return False
        


def find_match (var_list, match_list):
    
    match_list[0] += 1
    i = 1
    
    for var in var_list[1:]:
        
        if (var_list[0].move == var_list[i].move):
            
            match_list[i] += 1
            return
            
        i += 1
        


def init_match_list ():
    
    match_list = [0]
    
    i = 0
    
    while (i < PV_MAX):
        
        match_list.append (0)
        i += 1
        
    return match_list


def main():
    
    #Engine set-up
    user_eng_settings = {'name' : ENGINE_NAME,
                         'hash' : HASH_SIZE,
                         'multipv' : PV_MAX,
                         'threads' : THREAD_COUNT
                        }
    engine = init_engine (user_eng_settings)
    engine_data = chess.uci.InfoHandler()
    engine.info_handlers.append(engine_data)
    
    score_card = init_match_list()
    #white_match = init_match_list()
    #black_match = init_match_list()
    #print (score_card)
    
    #Book set-up
    #polyglot_book = chess.polyglot.open_reader (BOOK_FILE)
    polyglot_book = open_book ()
    if not polyglot_book:
        
        #open_book returned False
        print ("Bad file name or format for BOOK_FILE.  Exiting.")
        return
    
    pgn_in = open(INPUT_FILE, "r")
    next_game = chess.pgn.read_game(pgn_in)
    
    i = 0
    
    while next_game:
        
        #Skip main() loop for test purposes
        #break
        
        print ("Analysing game ", i+1)
        this_node = next_game.end().parent
        
        while this_node:
            
            #running_board = this_node.board()
            
            #This line checks if the next move results in a book position
            if is_book_position (polyglot_book, this_node.variation(0).board()):
                
                this_node.variation(0).comment = "Book position"
                break
                
            
            #engine.position(this_node.board())
            #engine.go(depth=SEARCH_DEPTH)
            evaluate_position (this_node, engine)
            
            for j in engine_data.info["pv"]:
                
                pvmove = engine_data.info["pv"][j][0]
                pvscore = (get_score (engine_data.info["score"][j], this_node.board().turn))/100
                this_node.add_variation (pvmove,starting_comment = str(pvscore))
                
            find_match(this_node.variations, score_card)
            
            print (".", end = "", flush=True)
            this_node = this_node.parent
            
        print()
        print (score_card)
        print()
        
        next_game.end().comment = ("T5 analysis performed by '" + engine.name + 
                "' using a search depth of " + str(SEARCH_DEPTH) + ".")
        
        with open (OUTPUT_FILE, 'a') as pgn_out:
            
            pgn_out.write(str(next_game))
            pgn_out.write("\n\n")
        
        i += 1
        next_game = chess.pgn.read_game(pgn_in)
        
    print (i, " boards printed.")
    
    engine.quit()
    pgn_in.close()


if __name__ == "__main__":
    #main(sys.argv[1:])
    main()



