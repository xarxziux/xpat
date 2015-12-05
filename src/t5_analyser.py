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
SEARCH_DEPTH = 10
HASH_SIZE = 128
THREAD_COUNT = 1


#Files
INPUT_FILE = "pgn/gamesin.pgn"
OUTPUT_FILE = "pgn/gamesout.pgn"
BOOK_FILE = "polyglot/Elo2400.bin"
#BOOK_FILE = "pgn/gamesout.pgn"


#Tx settings
PV_MAX = 5
PV_MIN = 3
CP_POSITION_CUTOFF = 200
CP_PV_CUTOFF = 100


#General settings
MATE_SCORE = 1000
CP_THRESHOLD = 300


def get_score(eng_score):
    ''' Convert the UCI score output to an integer value bound by +/- MATE_SCORE '''
    
    if (eng_score.mate):
        
        return -MATE_SCORE
            
    else:
        
        return_score = (int(eng_score.cp))
            
        if (return_score > MATE_SCORE):
            
            return_score = MATE_SCORE
            
        if (return_score < -MATE_SCORE):
            
            return_score = -MATE_SCORE
            
    return return_score


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


def check_game_end (node):
    ''' Checks whether the given position is a legal end '''
    ''' If the game is a legal, as opposed to an agreed, end, then no engine
        evaluation is necessary '''
    
    if (node.board().is_stalemate() or
            node.board().is_insufficient_material() or
            node.board().can_claim_draw()
            ):
        
        return (True, 0)
        
    if (node.board().is_checkmate()):
        
        return (True, -(MATE_SCORE))
            
    return (False, 0)


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
        


def find_match (pvs, match_list):
    ''' Check if the move played is among the PV choices found by the engine '''
    
    #First ignore positions with less than PV_MIN variations
    if (len(pvs) < (PV_MIN + 1)):
        
        match_list[1] += 1
        return False
        
    #Check if the score of the top choice falls outside the position threshold
    if (abs(pvs[1][1]) >= CP_POSITION_CUTOFF):
        
        match_list[1] += 1
        return False
        
    #Check if the score of PV_MIN falls outside the PV cutoff
    if (pvs[1][1] - pvs[PV_MIN][1] > CP_PV_CUTOFF):
        
        match_list[1] += 1
        return False
        
    match_list[0] += 1
    
    i = 2
    
    for var in pvs[1:]:
        
        if (pvs[0][0] == var[0]):
            
            match_list[i] += 1
            return True
            
        i += 1
    return False


def init_match_list ():
    ''' Sets up the match list '''
    ''' The first element is the number of move counted.
        The second is the number of moves rejected.
        Subsequent items show the matches for T1, T2, T3, etc. '''
    
    match_list = [0,0]
    
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
    
    white_match = init_match_list()
    black_match = init_match_list()
    
    #Book set-up
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
        this_node = next_game.end()
        pv_list = []
        
        if is_book_position (polyglot_book, this_node.board()):
            
            this_node.comment = "Book position"
            break
            
        legal_end = check_game_end(this_node)
        
        if legal_end[0]:
            
            pv_list.append ((this_node.move, -(legal_end[1])))
            
        else:
            
            evaluate_position (this_node, engine)
            pv_list.append ((this_node.move, -(get_score (engine_data.info["score"][1]))))
            #print (engine_data.info["score"])
            #end_score = -(get_score (engine_data.info["score"][1]))
            #pv_list.append ((this_node.move, end_score))
            
        this_node = this_node.parent
        
        while this_node:
            
            #This line checks if the next move results in a book position
            if is_book_position (polyglot_book, this_node.variation(0).board()):
                
                this_node.variation(0).comment = "Book position"
                break
                
            evaluate_position (this_node, engine)
            
            for next_pv in engine_data.info["pv"]:
                
                pv_move = engine_data.info["pv"][next_pv][0]
                pv_score = (get_score (engine_data.info["score"][next_pv]))
                pv_list.append ((pv_move, pv_score))
                
                output_score = pv_score/100
                
                if not (this_node.board().turn):
                    
                    output_score = -output_score
                    
                this_node.add_variation (pv_move, starting_comment = str(output_score))
                
            if (this_node.board().turn):
                
                #print ("pv_list =", pv_list)
                find_match(pv_list, white_match)
                
            else:
                
                #print ("pv_list =", pv_list)
                find_match(pv_list, black_match)
                
            print (".", end = "", flush=True)
            pv_list = [(this_node.move, -(pv_list[1][1]))]
            this_node = this_node.parent
            
        print()
        print (white_match)
        print (black_match)
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



