# Change log

###[unreleased] 2015-12-01
### Added
 - Engine and search depth info added to end of game
   
 - Polyglot book functionality added

### Changed
 - Placed pgn output inside a "with" block instead of keeping it open all the time
   
 - Minor code clean-ups

###[unreleased] 2015-11-25
### Added
 - .gitattributes to prevent the /testing and /external dircectories from being
   added to future releases

### Changed
 - Fixed get_score to limit the return value between -1000 and +1000 
   centipawns.
   
   - Changed the logic of get_score to return an integer value for centipawns 
   instead of a floating-point value for pawns.  Fixed the pv_score value in main 
   to reflect this.
   
 -  Sent engine initialisation to separate function.
 
 # [0.0.1] - 2015-11-25
 - v0.0.1 released
 
 
 