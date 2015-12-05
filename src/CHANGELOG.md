# Change log

###[unreleased] 2015-12-05
###Added
 - experimental T5 analysis.

###Changed
 - script logic to keep all scores the same sign as the UCI protocol, only
   changing them to the score from White's viewpoint when printing to the PGN
   file.
   
 - logic of get_score, find_match, and main routines to use tuples instead of
   dictionaries for several structures.
   
###[unreleased] 2015-12-03
###Changed
 - basic move-matching capability to separate scores for black and white.

###Added
 - check_game_end routine and extra logic for treating the final position.
   
 - next_move_score variable for checking the score of the move played to cp
   and engine-matching calculations.


###[unreleased] 2015-12-02
###Changed
 - is_book_position function to accepts a node instead of a board.  Reverted
   back to original setting - I can't ses how to send the starting node instead
   of a board to this function for opening book validation.
   
 - hard-coding of mate score to a settable value.
   
 - variable names for all settings to uppercase.
   
###Added
 - basic move-matching capability.  Largely untested and not fully implemented
   yet but it appears to be working.
   
 - evaluate_position function to de-clutter main() loop.
   
 - open_book function to handle "file not found" exceptions and perform basic
   book validation.
   
###Removed
 - running_board variable from main() loop.  Function and function
   calls changed to accomodate this.
 
###[0.0.2] 2015-12-01
### v0.0.2 released - exclusion of testing/ and external/ directories
   successful.


###[unreleased] 2015-12-01
### Added
 - engine and search depth info to end of game.
   
 - Polyglot book functionality.

### Changed
 - Placed pgn output inside a "with" block instead of keeping it open all the
   time.
   
 - Minor code clean-ups.


###[unreleased] 2015-11-25
### Added
 - .gitattributes to prevent the /testing and /external dircectories from being
   added to future releases.

### Changed
 - get_score to limit the return value between -1000 and +1000 
   centipawns.
   
 - the logic of get_score to return an integer value for centipawns.
   instead of a floating-point value for pawns.  Fixed the pv_score value in
   main() to reflect this.
   
 - Sent engine initialisation to separate function.


###[0.0.1] - 2015-11-25
### v0.0.1 released.


