"""
* Developed under python 2.7.6
* Using python-chess library version 0.11.1

Chess Game Analyzer Log

v35
1. Added posNAG to a line on "color is threatening" comments

v34
1. Added option to set hash

v33.0
1. Fixed number of moves in the pv when using white/black is threatening
2. Do not use pv with upperbound and lowerbound
3. Add number of threads used in Annotator

v32
1. Update to PC v0.11.1, use b = chess.Board(), instead of chess.Bitboard()

v31
1. Fixing same move in 2 pv in get_summarized_pv()

v30
1. Identify engine by its id and use it in anotator header

"""

import chess
import sys
from chess import pgn
import os
import subprocess
# from random import randint
import random


# Constants
APP_NAME = "Chess Game Analyzer"
APP_VERSION = "35.0"
INF = 32000
MAX_PLY = 128
BAD_SCORE = -INF
ONLY_MOVE_SCORE = 3.0
ANALYSIS_MARGIN = 10.0
BLUNDER_MARGIN = 0.15
PUZZLE_MARGIN = 0.80
GOOD_SCORE = 1.5
WHITE = 1
BLACK = 0

# Random comment
BAD_COMMENT = {'Not good is',\
               'But not',\
               'Bad is',\
               'Inferior is',\
               'Not reliable is',\
               'Incorrect is',\
               'Unsatisfactory is'}
REASON_COMMENT = {'due to',\
                  'in view of',\
                  'thanks to',\
                  'considering',\
                  'on the grounds of'}
GOOD_COMMENT = {1: 'A good alternative line is',\
                2: 'Better is',\
                3: 'More accurate is',\
                4: 'Superior is',\
                5: 'Excellent is'}
ALTERNATIVE = {'Also playable is',\
               'Another interesting line is',\
               'One that deserves attention is',\
               'A good alternative is',\
               'Also sufficient is',\
               'Worthy of consideration is',\
               'Also practical is',\
               'A fine line to try is',\
               'Also capable is',\
               'Also promising is',\
               'Another modest line is',
               'Another possiblity is'}

def random_reason():
    """ Returns a string as reason comment """
    res = []
    for i in REASON_COMMENT:
        res.append(i)
    random.shuffle(res)
    return res[0]


def random_bad():
    """ Returns a string for bad comment """
    res = []
    for i in BAD_COMMENT:
        res.append(i)
    random.shuffle(res)
    return res[0]


def get_alternative_comment(com, inc):
    """ Returns comment based on index inc """
    if inc >= len(com):
        # Randomize again
        random_alternative()
        inc = 0
    val = com[inc]
    inc += 1
    return (val, inc)


def random_alternative():
    """ Returns a list of comments in a different order.
        Call this once per new game parsed.
    """
    res = []
    for i in ALTERNATIVE:
        res.append(i)
    random.shuffle(res)
    return res


def comment_key(cvalue, hvalue, side_tomove):
    """ Returns a number based on score
        cvalue = computer analysis value
        hvalue = human analysis value
    """    
    comment_num = 2
    if side_tomove == WHITE:
        if cvalue - hvalue >= 4.0:
            comment_num = 5
            # If already lossing
            if cvalue < -1.0:
                comment_num = 1
        elif cvalue - hvalue >= 3.0:
            comment_num = 4
            if cvalue < -1.0:
                comment_num = 1
        elif cvalue - hvalue >= 2.0:
            comment_num = 3
            if cvalue < -1.0:
                comment_num = 1
    else:
        if cvalue - hvalue <= -4.0:
            comment_num = 5
            if cvalue > 1.0:
                comment_num = 1
        elif cvalue - hvalue <= -3.0:
            comment_num = 4
            if cvalue > 1.0:
                comment_num = 1
        elif cvalue - hvalue <= -2.0:
            comment_num = 3
            if cvalue > 1.0:
                comment_num = 1
    return comment_num
        
    
def mate_indicator(d2m):
    """ Returns +/-M for mate score indication """
    
    if d2m > 0:
        return 'White will mate black in %d moves' % abs(d2m)
    elif d2m < 0:
        return 'Black will mate white in %d moves' % abs(d2m)
    return 'None'

def get_engine_detailed_data(data, side):
    """ Will extract score, depth, move and pv from input data """
    
    # data = -0.79/15 20...Qa5 21.Nxd6 Bxa4 22.Bb6 Rxd6 23.Bxa5 Rxd3 24.cxd3 Bxd1
    # data = -0.79/15 21.Nxd6 Bxa4 22.Bb6 Rxd6 23.Bxa5 Rxd3 24.cxd3 Bxd1
    list_value = data.split(' ')
    score_and_depth = list_value[0]
    list_sd = score_and_depth.split('/')
    eval_value = float(list_sd[0])
    # Change sign if side is black
    if side == BLACK:
        eval_value = -1*eval_value
    depth = list_sd[1].strip()
    depth = int(depth)

    move = list_value[1]
    if '...' in move:
        move = move.split('.')
        move = move[3]
    else:
        move = move.split('.')
        move = move[1]
    move = move.strip()

    pvar = ' '.join(list_value[1:])

    return (eval_value, depth, move, pvar)

    
def get_score_and_depth(data, side_to_move):
    """ Will extract score and depth from input data.
        The score in the data is side POV during analysis
    """
    
    # data = -0.79/15 20... Qa5 21. Nxd6 Bxa4 22. Bb6 Rxd6 23. Bxa5 Rxd3 24. cxd3 Bxd1
    d_split = data.split(' ')
    left_val = d_split[0]
    token = left_val.split('/')
    val = float(token[0])
    
    # Change sign from point of view of player
    # We did this because we let the engine analyze
    # the fen + move of the player
    val = -1*val
    
    # Change sign if side is black, because we
    # use white POV in the analyzed output pgn file.
    # Move NAGS !?, ? and others are easier to append by
    # checking whether the value is positive or negative
    if side_to_move == BLACK:
        val = -1*val
    depth = token[1].strip()
    depth = int(depth)

    return (val, depth)
    

def save_headers(game, outputFN, engine_name, num_threads, nMoveTime):
    """ Print to file the headers of a game """
    
    hev = game.headers['Event']
    hsit = game.headers['Site']
    hdat = game.headers['Date']
    hro = game.headers['Round']
    hwh = game.headers['White']
    hbl = game.headers['Black']
    hre = game.headers['Result']

    is_white_elo = True
    try:
        hwelo = game.headers['WhiteElo']
    except:
        is_white_elo = False

    is_black_elo = True
    try:
        hbelo = game.headers['BlackElo']
    except:
        is_black_elo = False

    is_eco = True
    try:
        heco = game.headers['ECO']
    except:
        is_eco = False

    is_tc = True
    try:
        htc = game.headers['TimeControl']
    except:
        is_tc = False

    # Save headers
    with open(outputFN, 'a') as f:
        f.write('[Event "%s"]\n' %(hev))
        f.write('[Site "%s"]\n' %(hsit))
        f.write('[Date "%s"]\n' %(hdat))
        f.write('[Round "%s"]\n' %(hro))
        f.write('[White "%s"]\n' %(hwh))
        f.write('[Black "%s"]\n' %(hbl))
        f.write('[Result "%s"]\n' %(hre))
        if is_white_elo:
            f.write('[WhiteElo "%s"]\n' %(hwelo))
        if is_black_elo:
            f.write('[BlackElo "%s"]\n' %(hbelo))
        if is_eco:
            f.write('[ECO "%s"]\n' %(heco))
        if is_tc:
            f.write('[TimeControl "%s"]\n' %(htc))
        f.write('[Annotator "%s (%0.1fs/pos @thread=%d)"]\n\n' %(engine_name, float(nMoveTime)/1000, num_threads))
    

def is_number(s):
    """ Check if input is a number """
    
    try:
        float(s)
        return True
    except ValueError:
        return False

# PosNAG, +/=, =/+ ...
def position_nags(v):
    """ Returns the NAGs based on input value """
    
    nag = "$0"

    if int(100*v) >= INF-MAX_PLY or int(100*v) <= -INF+MAX_PLY:
        return nag
    
    if abs(v) < 0.25:
        nag = "$10" # even
    if v >= 3.0:
        nag = "$18"  # winning
    elif v >= 1.5:
        nag = "$16"  # moderate
    elif v >= 0.25:
        nag = "$14"  # slight
    elif v <= -3.0:
        nag = "$19"
    elif v <= -1.5:
        nag = "$17"
    elif v <= -0.25:
        nag = "$15"

    return nag


# !?, ?!, !, !! ??, ?
def move_nags(s, v1, v2):
    """ Returns move NAGs based on side to move, engine eval and move eval """
    
    nag = "$0"
    if (s == WHITE and v1 - v2 >= +3.0) or (s == BLACK and v1 - v2 <= -3.0):
        nag = "$4"  # ??
        
    elif (s == WHITE and v1 - v2 >= +1.5) or (s == BLACK and v1 - v2 <= -1.5):
        nag = "$2"  # ?

    # If the player move is still winning then use ?! or $6
    if nag != "$0":
        if (s == WHITE and v2 >= GOOD_SCORE) or (s == BLACK and v2 <= -GOOD_SCORE):
            nag = "$6"  # ?!       
        
    return nag


# Converts the uci pv to san pv
def new_lan_to_san(fen, pv):
    """ Converts uci pv to SAN pv format """

    logging = False
    # print isinstance(pv, list)
    # pv is string
    
    # print(pv)
    board = chess.Board(fen)
    side = board.turn
    
    # Store uci pv in a list and update the board
    # then we pop and save the move in san
    # print fen
    # print pv
    
    a = pv.split(' ')
    # print isinstance(a, list)
    for m in a:        
        # print m
        try:
            board.push_uci(m)            
        except ValueError:
            print 'Illegal move'
            
    # Pop the moves, and save it in SAN
    pvSan = []
    for i in range(len(a)):
        san = board.san(board.pop())
        pvSan.append(san)

    # Reverse it
    pvSan = list(reversed(pvSan))
    newPv = ' '.join(pvSan[0:])
    # print(newPv)

    # We put number to our pv 1. e4 e5 2. Nf3 ...
    fmvn = fen.split(' ')
    fmvn = fmvn[-1]
    fmvn = int(fmvn)

    numPv = []
    newPvList = newPv.split(' ')
    if side == WHITE:
        for i, m in enumerate(newPvList):
            if i == 0 or i%2 == 0:  # Even
                c = fmvn + i/2
                b = str(c) + '.' + m
                # print(b),
                numPv.append(b)
            else:
                b = m
                # print(b)
                numPv.append(b)
    # else if side is black
    else:
        for i, m in enumerate(newPvList):
            if i == 0:
                c = fmvn
                b = str(c) + '...' + m
                # print(b)
                numPv.append(b)
            else:
                if i%2 != 0:  # Even
                    c = fmvn + i/2 + 1
                    b = str(c) + '.' + m
                    # print(b),
                    numPv.append(b)
                else:
                    b = m
                    # print(b)
                    numPv.append(b)

    numPv = ' '.join(numPv[0:])

    if logging:
        print '\nSAN pv with num: %s' %(numPv)

    return numPv      

      
def mate_distance_to_value(d):
    """ returns value given distance to mate """
    value = 0
    if d < 0:
        value = -2*d - INF
    elif d > 0:
        value = INF - 2*d + 1
    return value

def value_to_mate(value):
    """ return number of move to mate """
    d = 0
    value = int(value)
    if abs(value) < INF - MAX_PLY:
        d = 0
    else:
        if value > 0:
            d = (INF - value + 1) / 2
        elif value < 0:
            d = (-INF-value) / 2
    return d


def get_time_key(item):
    """ Sort time """
    return item[2]


def get_depth_key(item):
    """ Sort depth """
    return item[0]


def analyze_complexity(engineName, fen, hashv, threadsv, movetimev, multipvv, nshortPv):
    """ Position is complex when the engine move changes more than once """

    multipv_num = multipvv
    record = []
    moveChanges = 0
    bestScore = -INF-1
    
    # print('%s' %(engineName[0:-4]))
    
    p = subprocess.Popen(engineName, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.stdin.write("uci\n")
    for eline in iter(p.stdout.readline, ''):
        eline = eline.strip()
        if "uciok" in eline:
            break
    
    p.stdin.write("setoption name Hash value " + str(hashv) + "\n")
    p.stdin.write("setoption name Threads value " + str(threadsv) + "\n")
    p.stdin.write("setoption name Cores value " + str(threadsv) + "\n")
    p.stdin.write("setoption name Max CPUs value " + str(threadsv) + "\n")
    p.stdin.write("setoption name MultiPV value " + str(multipv_num) + "\n")
    
    p.stdin.write("isready\n")
    for rline in iter(p.stdout.readline, ''):
        rline = rline.strip()
        if "readyok" in rline:
            break
    p.stdin.write("ucinewgame\n")
    p.stdin.write("position fen " + fen + "\n")        
    p.stdin.write("go movetime " + str(movetimev) + "\n")  # mt = movetime in ms

    # Parse engine output
    for eline in iter(p.stdout.readline, ''):
        
        a = eline.strip()

        # Process analysis output if there is depth, score and pv
        if "depth" in a and "score" in a and "pv" in a:

            b = a.split(' ')

            i = b.index("depth")
            depthv = int(b[i+1])

            # Translate mate to value
            if "mate" in a:
                i = b.index("score")
                d2m = int(b[i+2])
                scorev = mate_distance_to_value(d2m)
            elif "score cp" in a:
                i = b.index("score")
                scorev = int(b[i+2])

            # Split at pv
            i = b.index("pv")
            c = b[i+1:]
            
            pvv = "None"

            # Shorten pv
            lenPv = len(c)

            if lenPv >= nshortPv:
                cc = b[i+1 : i+1+nshortPv]
                d = ' '.join(cc)
                pvv = d.strip()
            else:
                cc = b[i+1:]
                d = ' '.join(cc)
                pvv = d.strip()

            # Save only a single move from the pv
            singleMove = pvv.split(' ')
            singleMove = singleMove[0]

            # Record everything then sort later
            record.append([depthv, scorev, singleMove])
            
        if "bestmove" in a:
            # print(a)
            bestScore = scorev
            break

    # Quit the engine
    p.stdin.write("quit\n")
    p.stdin.close()
    p.communicate()
    
    # Check the move and score
    for i, item in enumerate(record):

        # Move changes, starts comparison at iteration depth 3
        if item[0] >= 4:
            if record[i][2] != record[i-1][2]:
                moveChanges += 1

    mate = False
    if bestScore != -INF-1 and (bestScore >= INF - MAX_PLY) or (bestScore <= -INF + MAX_PLY):
        mate = True
    return (moveChanges, mate)


def max_depth_in_analysis(analysis_data):
    """ Find maximum depth in the list"""
    
    max_depth = 0
    for item in analysis_data:
        if item[0] > max_depth:
            max_depth = item[0]
            
    return max_depth


def alter_pv(pv):
    """ remove top depth pv """
    new_pv = []
    for n in pv:
        if pv[0][0] == n[0]:
            pass
        else:
            new_pv.append(n)
    return new_pv


def good_pv_depth(pv, mpv):
    """ returns true if depth of top pvs is the same """
    # For 2 pv only
    if mpv == 2:
        if pv[0][0] == pv[1][0]:
            return True
        else:
            return False


def good_pv_moves(pv):
    """ returns true if top pvs moves is not the same,
        applies only to 2 pv
    """
    pvmove1 = pv[0][4]
    pvmove1 = pvmove1.split(' ')
    pvmove1 = pvmove1[0]

    pvmove2 = pv[1][4]
    pvmove2 = pvmove2.split(' ')
    pvmove2 = pvmove2[0]

    if pvmove1 != pvmove2:
        return True
    print 'pv moves are the same'
    return False


def get_summarized_pv(analysis_data, multipvv):
    """ Save the best pv lines return pv list in depth descending order """

    final_pv_list = []

    max_depth = max_depth_in_analysis(analysis_data)
    
    for i in range(max_depth):
        record_depth = []

        # Parse the data and save to new list based on depth
        for item in analysis_data:
            if i+1 == item[0]:
                record_depth.append(item)

        # Sort time
        time_sorted_list = sorted(record_depth, key=get_time_key, reverse=True)

        # In temp list only save the pv with high time for multipv 1 and 2
        temp_list = []
        for j in range(multipvv):            
            ind = j + 1
            # Find the pv with this ind and high time and save it
            for n in time_sorted_list:
                if ind == n[1]:  # multipv 1 or 2
                    temp_list.append(n)
                    break        
        
        for n in temp_list:
            final_pv_list.append(n)
    
    final_pv_list = sorted(final_pv_list, key=get_depth_key, reverse=True)  
    
    # [18, 1, 2356, 3, 'e1g1 c8a6 d3a6 a8a6 f3d2 e4d2 c2d2']
    # [17, 1, 1920, 12, 'd1e2 g7g5 f4g3 f8f7 e1g1 e4g3 h2g3']
    # [17, 2, 1920, 3, 'e1g1 c8a6 d3a6 a8a6 f3d2 e4d2 c2d2']
    # [16, 1, 1654, 5, 'e1g1 c8a6 d3a6 a8a6 f3d2 e4d2 d1d2']
    # [16, 2, 1654, 0, 'd1e2 g7g5 f4g3 f8f7 e1g1 e4g3 f2g3']

    # Filter out same pv move if multipv > 1 at given depth
    if multipvv > 1:
        # Make sure that multipv is the same as num pvs at same depth
        # and pv moves among multipv are not the same
        trials = 0
        while True and len(final_pv_list) > 1:
            if trials >= 3:
                print 'trials: %d' % trials
            trials += 1
            if good_pv_depth(final_pv_list, multipvv):
                if good_pv_moves(final_pv_list):
                    break
                else:
                    new_pv = alter_pv(final_pv_list)
                    final_pv_list = []
                    final_pv_list = new_pv
            else:
                new_pv = alter_pv(final_pv_list)
                final_pv_list = []
                final_pv_list = new_pv
    
    return final_pv_list


def analyze_fen(engineName, fen, hashv, threadsv, movetimev, multipvv, nshortPv):
    """ This will output engine analysis in a list
        and the score returned is side POV
    """
    
    multipv_num = multipvv
    record = []
    
    # print('%s' %(engineName[0:-4]))
    
    p = subprocess.Popen(engineName, stdin=subprocess.PIPE,\
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.stdin.write("uci\n")
    for eline in iter(p.stdout.readline, ''):
        eline = eline.strip()
        if "uciok" in eline:
            break
    
    p.stdin.write("setoption name Hash value " + str(hashv) + "\n")
    p.stdin.write("setoption name Threads value " + str(threadsv) + "\n")
    p.stdin.write("setoption name Cores value " + str(threadsv) + "\n")
    p.stdin.write("setoption name Max CPUs value " + str(threadsv) + "\n")
    p.stdin.write("setoption name MultiPV value " + str(multipv_num) + "\n")
    
    p.stdin.write("isready\n")
    for rline in iter(p.stdout.readline, ''):
        rline = rline.strip()
        if "readyok" in rline:
            break
    p.stdin.write("ucinewgame\n")
    p.stdin.write("position fen " + fen + "\n")

    # New command so that only 1 depth will be reported
    p.stdin.write("go movetime " + str(movetimev) + "\n")

    # Parse engine output
    for eline in iter(p.stdout.readline, ''):
        
        engine_output = eline.strip()

        # Process engine analysis output
        if "depth" in engine_output\
                    and "score" in engine_output\
                    and "time" in engine_output\
                    and "pv" in engine_output\
                    and not "upperbound" in engine_output\
                    and not "lowerbound" in engine_output:

            b = engine_output.split(' ')

            i = b.index("depth")
            depthv = int(b[i+1])
               
            if "multipv" in engine_output:
                i = b.index("multipv")
                multipvv = int(b[i+1])
            else:
                multipvv = 1
               
            i = b.index("time")
            timev = int(b[i+1])

            # Translate mate to value
            if "mate" in engine_output:
                i = b.index("score")
                d2m = int(b[i+2])
                scorev = mate_distance_to_value(d2m)
            else:
                i = b.index("score")
                scorev = int(b[i+2])

            # Split at pv
            i = b.index("pv")
            c = b[i+1:]
            
            pvv = "None"

            # Shorten pv
            lenPv = len(c)

            # If score is mate save all pv otherwise use nshortPv
            if lenPv >= nshortPv and abs(scorev) < INF-MAX_PLY:
                cc = b[i+1 : i+1+nshortPv]
                d = ' '.join(cc)
                pvv = d.strip()
            else:
                cc = b[i+1:]
                d = ' '.join(cc)
                pvv = d.strip()

            # Record everything then sort later
            record.append([depthv, multipvv, timev, scorev, pvv])
            
        if "bestmove" in engine_output:
            break

    # Quit the engine
    p.stdin.write("quit\n")
    p.stdin.close()
    p.communicate()

    # Save the engine analysis

    final_list = get_summarized_pv(record, multipvv)

    old_depth = 0
    return_list = []
    save_cnt = 0
    for n in final_list:
        
        scorev = n[3]

        # Convert LAN pv to san
        san_pv = new_lan_to_san(fen, n[4])

        analysis_line = ("%+0.2f/%d %s" %(float(n[3])/100, n[0], san_pv))

        # Before saving the second pv make sure that the depth of the first pv
        # is the same with the depth of the second pv
        if save_cnt == 1:
            if old_depth == n[0]:                
                return_list.append(analysis_line)
                save_cnt += 1
            else:
                # Replace the old item
                return_list[0] = analysis_line
        elif save_cnt == 0:
            return_list.append(analysis_line)
            save_cnt += 1

            if multipvv == 1:
                break
            
        if save_cnt == 2:
            break
            
        old_depth = n[0]
        
    return return_list


def prompt_user():
    """ Asks user for initial data """
    num_threads = 1
    ms_time = 1000
    num_hash = 32
    
    engine_file = raw_input('enter engine filename? ')
    if not os.path.isfile(engine_file):
        print 'engine file is not found'
        return (None, None, None, num_threads, num_hash, ms_time, 2, 80)
        
    pgn_file = raw_input('enter pgn filename? ')
    if not os.path.isfile(pgn_file):
        print 'pgn file is not found'
        return (None, None, None, num_threads, num_hash, ms_time, 2, 80)

    num_threads = int(raw_input('enter number of threads to be used by the engine? '))
    if num_threads < 1:
        num_threads = 1
    elif num_threads > 32:
        num_threads = 32

    num_hash = int(raw_input('enter Hash in mb? '))
    if num_hash < 1:
        num_hash = 1
    elif num_hash > 16384:
        num_hash = 16384

    ms_time = int(raw_input('enter analysis time/pos in ms? '))
    if ms_time < 10:
        ms_time = 10
    elif ms_time > 5*60*60*1000:
        ms_time = 5*60*60*1000  # 5 hrs max / move

    start_fmvn = int(raw_input('enter the move number to start the analysis? '))
    if start_fmvn < 1:
        start_fmvn = 1
        
    end_fmvn = int(raw_input('enter the move number to end the analysis? '))
    if end_fmvn < 1:
        end_fmvn = 1

    return (1, engine_file, pgn_file, num_threads, num_hash,\
            ms_time, start_fmvn, end_fmvn)


def get_engine_id(enginefn):
    """ Returns id name of an engine """
    engine_idname = 'Engine'
    p = subprocess.Popen(enginefn, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.stdin.write("uci\n")
    for eline in iter(p.stdout.readline, ''):
        eline = eline.strip()
        if "id name" in eline:
            a = eline.split(' ')
            engine_idname = ' '.join(a[2:])
        if "uciok" in eline:
            break
    # Quit the engine
    p.stdin.write("quit\n")
    p.stdin.close()
    p.communicate()

    return engine_idname  
           

# Start here
def main(argv):
    """ Main starts """
    print '%s v%s\n' %(APP_NAME, APP_VERSION)

    # Init
    sEngine = "Stockfish 6.exe"
    nHash = 32  # Default engine hash size
    nThreads = 1
    nMoveTime = 1000
    nMultiPv = 1
    nshortPv = 7
    startFmvn = 2
    lastFmvn = 200
    outputFN = "analyzedGame.pgn"
    gameCnt = 0
    MOVE_CHANGES = 3
    complexityTime = 1000
    flag = 1

    # User input
    flag, sEngine, pgn_file, nThreads, nHash, nMoveTime,\
          startFmvn, lastFmvn = prompt_user()
    if flag is None:
        raw_input("Press enter key to exit")
        sys.exit(1)

    engine_id = get_engine_id(sEngine)
        
    complexityTime = nMoveTime

    # Open pgn file for reading
    ifo = open(pgn_file, 'r')
    alt_index = 0

    # Read the games in the pgn file one by one
    game = chess.pgn.read_game(ifo) 
    while game != None:
        gameCnt += 1
        print '\nGame %d\n' %(gameCnt)

        # Randomize alternate comment
        ALTER_COM = random_alternative()

        # Save result header for writing at end of a game
        try:
            hre = game.headers['Result']
        except:
            hre = '*'

        # Save headers to output file
        save_headers(game, outputFN, engine_id, nThreads, nMoveTime)  
        
        game_node = game
        # Loop thru the main moves and comments on this game
        while len(game_node.variations):
            side = game_node.board().turn

            fmvn = game_node.board().fullmove_number
            fmvn = int(fmvn)
            
            next_node = game_node.variation(0)
            move = next_node.move
            sanMove = game_node.board().san(move)
            # print('san move: %s' %(sanMove))

            strFEN = str(game_node.board().fen())
            # strEPD = str(game_node.board().epd(sm = move.uci()))
            # print(strEPD)
            puzzleEpd = str(game_node.board().epd(bm=sanMove))

            # Show fen in console
            print 'FEN: %s' %(strFEN)
            print 'Player move: %s' %(sanMove)
            
            # uciGameMove = str(move.uci())
            # print('UCI_Move: %s' %(uciGameMove))

            # Init
            threat_depth = 0
            threatValue = BAD_SCORE
            anaValue = BAD_SCORE
            anaValue2 = BAD_SCORE
            gameMoveValue = BAD_SCORE
            anaPvMove = "None"
            isOnlyMove = False
            moveChanges = 0
            showVars = False
            matePos = False

            # Analyze pos if fmvn is within startFmvn and lastFmvn input from user
            if fmvn >= startFmvn and fmvn <= lastFmvn:

                # (0) Get the score of the game move by running the engine.
                # Invert the score after the analysis since we are analyzing fen + move,
                # and invert the score if current side is black too
                # because we use white POV (point of view) and engine is analyzing at side POV

                # Use temp so we will not mess with the current board
                tempBoard = game_node.board()
                tempBoard.push(move)  # make the move on the temp board
                # Don't send position to analyze without a legal move
                if not game_node.board().is_checkmate()\
                       and not game_node.board().is_stalemate()\
                       and not tempBoard.is_checkmate()\
                       and not tempBoard.is_stalemate():
                    tFEN = str(tempBoard.fen())  
                    mpv = 1

                    # Get the score/depth pv <moves> in a list, list[0] = 1st pv,
                    # list[1] = 2nd pv, for multipv 2. The expected return value is,
                    # "+0.89/11 32. Nc6 Nh5 33. Qf2 Qd1 34. Nb4", for nshortPv = 5
                    gameMoveAnalysisList = analyze_fen(sEngine,\
                                                       tFEN,\
                                                       nHash,\
                                                       nThreads,\
                                                       nMoveTime,\
                                                       mpv,\
                                                       nshortPv)
                    gameMoveAnalysis = gameMoveAnalysisList[0]
                    
                    # The return value is from the point of view of the opponent,
                    # so we must negate it before comparing with engine analysis score
                    # gameMoveValue is in pawn unit and is of type float
                    # gameMoveValue is converted by get_score_and_depth() from
                    # point of view of the player now and also white pov
                    gameMoveValue, gameMoveDepth = get_score_and_depth(gameMoveAnalysis, side)

                    # Write to console as update
                    print 'Engine analysis of player move: %+0.2f/%d\n'\
                              %(gameMoveValue, gameMoveDepth)
                    
                # Analyze position to get engine recommendation

                # (1) Get complexity of the position using multipv 1,
                # use 1s or nominal search time entered by user
                if (gameMoveValue > -0.15 and side == WHITE)\
                           or (gameMoveValue < 0.15 and side == BLACK):
                    complexityMultiPV = 1
                    moveChanges, matePos = analyze_complexity(sEngine,\
                                    strFEN, nHash, nThreads,\
                                    complexityTime,\
                                    complexityMultiPV, nshortPv)                

                # (2) Get the engine analysis when engine is to move in this position
                if not game_node.board().is_checkmate()\
                           and not game_node.board().is_stalemate():
                    nMultiPv = 2
                    
                    # Increase engine time when move changes >= 3
                    newAllocTime = nMoveTime
                    if moveChanges >= 3:
                        newAllocTime = 3*nMoveTime

                    # If position has mate score then we extend the pv length,
                    # this is only applicable for pv1
                    pvLen = nshortPv
                    if matePos:
                        pvLen = 200  # nshortPv                        
                        
                    analysisList = analyze_fen(sEngine, strFEN,\
                                    nHash, nThreads, newAllocTime, nMultiPv, pvLen)

                    # Get score, depth, and pv of the 1st pv line from multipv
                    analysisData = analysisList[0]
                    anaValue, anaDepth, anaPvMove, anaPv = get_engine_detailed_data(analysisData, side)
                    
                    # Get score, depth and pv of the 2nd pv if there is
                    # There is a possibility that a multi pv will not return 2nd pv
                    if len(analysisList) > 1:
                        analysisData2 = analysisList[1]
                        anaValue2, anaDepth2, anaPvMove2,\
                                   anaPv2 = get_engine_detailed_data(analysisData2, side)

                    # Create puzzle                 
                    if moveChanges >= 3 and abs(anaValue - anaValue2) >= PUZZLE_MARGIN and\
                           ((anaValue > +0.20 and side == WHITE) or\
                            (anaValue < -0.20 and side == BLACK)):
                        with open('puzzle.epd', 'a') as puz_fo:
                            puz_fo.write(puzzleEpd + '\n')                    

                # (3) Check if analysis will be written to pgn file
                if anaPvMove == sanMove or gameMoveValue == BAD_SCORE or anaValue == BAD_SCORE\
                           or (abs(gameMoveValue) >= ANALYSIS_MARGIN and abs(anaValue) >= ANALYSIS_MARGIN)\
                           or ((anaValue - gameMoveValue < BLUNDER_MARGIN and side == WHITE) or\
                               (anaValue - gameMoveValue > -BLUNDER_MARGIN and side == BLACK)):
                    showVars = False

                    # If move is the same add only move comment to the main line
                    if anaPvMove == sanMove:
                        # Get the engine pvscore2 and compare it with score1 to see the forced move
                        if side == WHITE:
                            if anaValue - anaValue2 >= ONLY_MOVE_SCORE and anaValue2 <= 0.5:
                                isOnlyMove = True
                        else:
                            if anaValue - anaValue2 <= -ONLY_MOVE_SCORE and anaValue2 >= -0.5:
                                isOnlyMove = True                          
                        
                else:
                    showVars = True

                    # Find the threat of the last move of opp by doing a null move
                    # from this current position. If this value is positive then
                    # the current side to move is in trouble because by doing
                    # nothing the opponent gains score. This will also detect initiative
                    if not game_node.board().is_check() and not game_node.board().is_stalemate():
                        tempBoardt = game_node.board()
                        tempBoardt.push(move.null())  # Send null move
                        tFENt = str(tempBoardt.fen())  
                        nMultiPv = 1
                        gameMoveThreatList = analyze_fen(sEngine, tFENt, nHash,\
                                            nThreads, nMoveTime, nMultiPv, nshortPv)
                        # print 'gameMoveThreatList: %s' % gameMoveThreatList
                        gameMoveThreat = gameMoveThreatList[0]
                        threatPvStr = gameMoveThreat.split(' ')
                        threatPv = ' '.join(threatPvStr[1:])
                        threatEval = threatPvStr[0]
                        threatValue = threatEval.split('/')
                        threat_depth = threatValue[1]
                        threat_depth = int(threat_depth)

                        # If score is positive we are in trouble
                        threatValue = float(threatValue[0])

            # (4) Write the moves, comments, NAG's to a file in a pgn format
            # Do not write main alternative moves, but show bad move lines
            if not showVars:
                with open(outputFN, 'a') as f:
                    # If position is complex and engine bestmove is the same with player move then add !
                    if (moveChanges >= MOVE_CHANGES) and anaPvMove == sanMove and anaValue != BAD_SCORE and\
                            anaValue2 != BAD_SCORE:

                        # Write inferior line but not lossing and not winning
                        if (anaValue - anaValue2 >= 0.30 and anaValue - anaValue2 <= 1.5 and anaValue2 < 1.0 and side == WHITE) or\
                                   (anaValue - anaValue2 <= -0.30 and\
                                    anaValue - anaValue2 >= -1.5 and\
                                    anaValue2 > 1.0 and side == BLACK):
                            posNag = position_nags(anaValue2)
                            gamePosNag = position_nags(gameMoveValue)

                            # Break down anaPv2 to get the first move in the pv and add some
                            # nags and comments, then assemble again                       
                            # $6 = ?!, $2 = ?
                            if (anaValue - anaValue2 >= 0.80 and side == WHITE) or\
                                   (anaValue - anaValue2 <= -0.80 and side == BLACK):
                                badMoveNag = "$2" 
                            else:
                                badMoveNag = "$6"

                            # Get the move in pv2 and add a NAG
                            anaPv2Rev = anaPv2.split(' ')
                            pv2_move = anaPv2Rev[0]
                            pv2_move = pv2_move + ' ' + badMoveNag  + ' { ' + random_reason() + ' } '
                            mvRem = ' '.join(anaPv2Rev[1:-1])
                            newAnaPv2 = pv2_move + ' ' + mvRem

                            # Get random bad comment and append it before the pv2
                            badComment = random_bad()

                            # Write the bad variation depends on white and black
                            if side == WHITE:
                                f.write('%d. %s %s {%+0.2f/%d} ({%s} %s %s {%+0.2f/%d}) '\
                                        %(fmvn, game_node.board().san(next_node.move),\
                                        gamePosNag, gameMoveValue, gameMoveDepth,\
                                        badComment, newAnaPv2, posNag, anaValue2, anaDepth2))
                            else:
                                f.write('%s %s {%+0.2f/%d} ({%s} %s %s {%+0.2f/%d}) '\
                                        %(game_node.board().san(next_node.move),\
                                        gamePosNag, gameMoveValue, gameMoveDepth,\
                                        badComment, newAnaPv2, posNag, anaValue2, anaDepth2))
                        else:
                            # If critical use !! = $3 or ! = $1
                            if (anaValue >= 1.5 and anaValue2 <= -0.5) or\
                                   (anaValue <= -1.5 and anaValue2 >= +0.5):
                                if side == WHITE:
                                    f.write('%d. %s %s ' %(fmvn, game_node.board().san(next_node.move), "$3"))
                                else:
                                    f.write('%s %s ' %(game_node.board().san(next_node.move), "$3"))
                            else:
                                if side == WHITE:
                                    f.write('%d. %s %s ' %(fmvn, game_node.board().san(next_node.move), "$1"))
                                else:
                                    f.write('%s %s ' %(game_node.board().san(next_node.move), "$1"))
                    else:
                        if isOnlyMove:
                            f.write('%d. %s %s ' %(fmvn, game_node.board().san(next_node.move), "$8"))
                        else:
                            f.write('%d. %s ' %(fmvn, game_node.board().san(next_node.move)))

            # Else write the pv as suggested by the engine      
            else:
                assert showVars

                # Position NAG
                PvPosNag = position_nags(anaValue)

                # game pos and move NAG
                gameMoveNag = move_nags(side, anaValue, gameMoveValue)
                gamePosNag = position_nags(gameMoveValue)

                # Select a comment based on diff between engine score and game move score
                com_key = comment_key(anaValue, gameMoveValue, side)
                goodComment = GOOD_COMMENT[com_key]

                with open(outputFN, 'a') as f:

                    # If game move pos assessment is a mate due to perhaps of
                    # a blunder then show +/-M, instead of score/depth
                    move_score_val = "%+0.2f" % gameMoveValue
                    posGameMoveComment = str(move_score_val) + '/' + str(gameMoveDepth)                  
                    if (int(100*gameMoveValue) >= INF-MAX_PLY) or (int(100*gameMoveValue) <= -INF+MAX_PLY):
                        assert gameMoveValue != BAD_SCORE
                        num_mate = value_to_mate(100*gameMoveValue)
                        assert num_mate != 0
                        smate = mate_indicator(num_mate)
                        posGameMoveComment = smate

                    # If pv1 score is a mate then show +/-M, instead of score/depth
                    pv1_score_val = "%+0.2f" % anaValue
                    posPv1Comment = str(pv1_score_val) + '/' + str(anaDepth)
                    pv1MateScore = False
                    if (int(100*anaValue) >= INF-MAX_PLY and side == WHITE) or\
                               (int(100*anaValue) <= -INF+MAX_PLY and side == BLACK):
                        assert anaValue != BAD_SCORE
                        num_mate = value_to_mate(100*anaValue)
                        assert num_mate != 0
                        smate = mate_indicator(num_mate)                        
                        posPv1Comment = smate
                        pv1MateScore = True

                    # Add NAG to main alternative move depending on the pv and game move analysis value
                    if (anaValue - gameMoveValue >= 0.80 and anaValue >= -0.50 and side == WHITE)\
                           or (anaValue - gameMoveValue <= -0.80\
                                and anaValue <= +0.50 and side == BLACK):
                        pv1_move_nag = "$1"  # ! or good move
                        
                        # Break down the pv to get the first move
                        pv1_split = anaPv.split(' ')

                        # Get the first move in the pv including the move number
                        pv1_move = pv1_split[0]

                        # Insert the pv1_move_nag after the first move
                        if pv1MateScore:
                            new_mv = pv1_move + ' ' + pv1_move_nag + ' ' + '{with mate attack} '
                        else:
                            new_mv = pv1_move + ' ' + pv1_move_nag + ' '

                        # Reconstruct the pv line
                        new_anaPv = new_mv + ' '.join(pv1_split[1:])

                        # Write the game move and pv variation
                        if side == WHITE:
                            if pv1MateScore:
                                f.write('\n%d. %s %s %s {%s} ({%s} %s %s) '\
                                        %(fmvn, game_node.board().san(next_node.move), gameMoveNag,\
                                        gamePosNag, posGameMoveComment,\
                                        goodComment, new_anaPv, PvPosNag))
                            else:
                                f.write('\n%d. %s %s %s {%s} ({%s} %s %s {%s}) '\
                                        %(fmvn, game_node.board().san(next_node.move), gameMoveNag,\
                                        gamePosNag, posGameMoveComment,\
                                        goodComment, new_anaPv, PvPosNag, posPv1Comment))
                        else:
                            if pv1MateScore:
                                f.write('\n%s %s %s {%s} ({%s} %s %s) '\
                                        %(game_node.board().san(next_node.move), gameMoveNag,\
                                        gamePosNag, posGameMoveComment,\
                                        goodComment, new_anaPv, PvPosNag))
                            else:
                                f.write('\n%s %s %s {%s} ({%s} %s %s {%s}) '\
                                        %(game_node.board().san(next_node.move), gameMoveNag,\
                                        gamePosNag, posGameMoveComment,\
                                        goodComment, new_anaPv, PvPosNag, posPv1Comment))
                    else:
                        if side == WHITE:
                            f.write('\n%d. %s %s %s {%s} ({%s} %s %s {%s}) '\
                                    %(fmvn, game_node.board().san(next_node.move), gameMoveNag,\
                                    gamePosNag, posGameMoveComment,\
                                    goodComment, anaPv, PvPosNag, posPv1Comment))                          
                        else:
                            f.write('\n%s %s %s {%s} ({%s} %s %s {%s}) '\
                                    %(game_node.board().san(next_node.move), gameMoveNag,\
                                    gamePosNag, posGameMoveComment,\
                                    goodComment, anaPv, PvPosNag, posPv1Comment))

                    # If the game move is not the same to that of pv2 then write it to the game as variation,
                    # depending on the pv2 score and game move score
                    if anaPvMove2 != sanMove and anaValue2 != BAD_SCORE:
                        
                        # Get pos nag of pv2
                        pv2PosNag = position_nags(anaValue2)
                        
                        # If pv2 score is equal or better than the game move score then write
                        # it as a playable move, otherwise write it as a mistake
                        if (side == WHITE and anaValue2 >= gameMoveValue) or\
                                   (side == BLACK and anaValue2 <= gameMoveValue):
                            if (side == WHITE and anaValue2 >= -ONLY_MOVE_SCORE) or\
                                       (side == BLACK and anaValue2 <= +ONLY_MOVE_SCORE):
                                
                                # If pv1 showed that this has a mate score then check
                                # if pv2 is also showing mate score, otherwise cut the pv2 length
                                # to the user specified pv length to be shown in variation, as we
                                # know we extend the pv length when there is a mate score from pv1
                                if (int(100*anaValue2) >= INF-MAX_PLY and side == WHITE) or\
                                       (int(100*anaValue2) <= -INF+MAX_PLY and side == BLACK):

                                    # Convert score to mate number
                                    num_mate = value_to_mate(100*anaValue2)
                                    assert num_mate != 0
                                    smate = mate_indicator(num_mate)
                                    posPv2Comment = smate
                                    com_val, alt_index = get_alternative_comment(ALTER_COM, alt_index)
                                    f.write('\n({ %s } %s %s {%s}) '\
                                            %(com_val, anaPv2, pv2PosNag, posPv2Comment))
                                else:
                                    
                                    # Reduce the pv length to user specified pv length
                                    new_ana_pv2 = anaPv2.split(' ')
                                    new_ana_pv2 = ' '.join(new_ana_pv2[:nshortPv])
                                    com_val, alt_index = get_alternative_comment(ALTER_COM, alt_index)
                                    f.write('\n({ %s } %s %s {%+0.2f/%d}) '\
                                            %(com_val, new_ana_pv2, pv2PosNag, anaValue2, anaDepth2))
                        else:
                            # Add move nag to the first move of pv2
                            new_ana_pv2 = anaPv2.split(' ')
                            if len(new_ana_pv2) >= 2:
                                new_anaPvMove2 = anaPvMove2 + ' $2 { %s } ' % random_reason()

                                # Cut 1 ply at end of pv, to emphasize that the other side is the last mover
                                new_ana_pv2 = new_anaPvMove2 + ' '.join(new_ana_pv2[1:-1])
                            else:
                                new_ana_pv2 = anaPv2

                            badComment = random_bad()
                            f.write('\n({ %s } %s %s {%+0.2f/%d}) '\
                                    %(badComment, new_ana_pv2, pv2PosNag, anaValue2, anaDepth2))

                    # Print the threat pv if score of opponent or last move is good
                    if threatValue > 0.0 and threatValue != BAD_SCORE:
                        
                        # Translate threatValue to white pov
                        # Use side == WHITE because we do a null move
                        wpov_threatValue = threatValue
                        if side == WHITE:
                            wpov_threatValue = -1*threatValue
                        if int(100*threatValue) >= +INF-MAX_PLY:
                            num_mate = value_to_mate(100*threatValue)
                            if side == WHITE:
                                f.write('\n({Black is threatening mate in %d with} %d. %s %s) '\
                                        %(abs(num_mate), fmvn, '--', threatPv))
                            else:
                                f.write('\n({White is threatening mate in %d with} %d. %s %s) '\
                                        %(abs(num_mate), fmvn, '--', threatPv))
                        else:
                            posNag = position_nags(wpov_threatValue)
                            if side == WHITE:
                                f.write('\n({Black is threatening} %d. %s %s %s {%+0.2f/%d}) '\
                                        %(fmvn, '--', threatPv, posNag, wpov_threatValue, threat_depth))
                            else:
                                f.write('\n({White is threatening} %d. %s %s %s {%+0.2f/%d}) '\
                                        %(fmvn, '--', threatPv, posNag, wpov_threatValue, threat_depth))

            game_node = next_node

        # Print result at the end of notation
        with open(outputFN, 'a') as output_fo:
            output_fo.write(hre + '\n\n')

        # Read another game
        game = chess.pgn.read_game(ifo)

    ifo.close()

    print "\nDone!!"
    raw_input("Press enter key to exit")


if __name__ == "__main__":
    main(sys.argv[1:])
