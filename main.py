import pygame
from copy import deepcopy
import sqlite3
import time
import numpy as np

pygame.init()

class GAME:
  def __init__(self):
    self.win = pygame.display.set_mode((720, 560))
    self.__square_boardx = 0
    self.__square_boardy = -70
    self.__square_board_colour = 0
    self.__show_move = True
    self.__home_active = True
    self.__playe_active = False
    self.__data_base_active = False
    self.__game_rules = False
    self.__rule =0
    self.__checking_game_over = False
    self.__extra_seconds = 0
    self.__levels = False 
    self.__timer_active = False 

    self.__step_for_white = 1
    self.__step_for_black = 5
    self.__BLUE = (1, 229, 255)
    self.__KING_COLOR = (255, 208, 0)
    
    self.__game_over = False
    self.__winner = None

    self.__BLACK_turn = Piece("Black", False, (0,0,0)) 
    self.__WHITE_turn = Piece("White", False, (255,255,255))
    self.__WHITE_KING = Piece("White", True, (255,255,255))
    self.__BLACK_KING = Piece("Black", True, (0,0,0))

    
    self.__board_np = [[0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn ,0 ,self.__WHITE_turn], 
                       [self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn, 0], 
                       [0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn], 
                       [0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0], 
                       [self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0], 
                       [0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn], 
                       [self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0]]
    

    
    
    self.__EMPTY_space = 0
    self.__player_turn = self.__BLACK_turn
    
    self.__possible_AI_piece = {}
    self.__AI_level = None
    self.__possible_movements = []
    self.__remove = {}
    self.__show_possible_move = 3
    self.__player_pos = None

     #remove after finish (used in minimax)
    
    # this will create a database
    
    self.__connection = sqlite3.connect('Game_db.db')
    self.__cursor = self.__connection.cursor()

    self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS Game_Table (
            Game_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Player_Turn INTEGER,
            AI INTEGER,
            Day INTEGER,
            Month INTEGER,
            Year INTEGER,
            Hour INTEGER,
            Minute INTEGER,
            time_seconds REAL
        )""")

    self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS Board (
            game_id INTEGER,
            piece INTEGER,
            row INTEGER,
            col INTEGER,
            FOREIGN KEY(game_id) REFERENCES Game_Table(id)
        )""")
    
    self.__connection_levels = sqlite3.connect('levels.db')
    self.__cursor_levels = self.__connection_levels.cursor()

    self.__cursor_levels.execute("""
        CREATE TABLE IF NOT EXISTS Best_times (
            Easy REAL,
            Medium REAL,
            Hard REAL
        )""")
    
    self.__connection.commit() 


  def check_game_over(self):# this will check if the game is over 
    black_lost = True # set them as if they lost, if during this functian a single case is found that would contradict this, the variables will be set to false 
    white_lost = True
    self.__checking_game_over = True 
    
    for row in range(len(self.__board_np)):
      for col in range(len(self.__board_np[row])): # for every piece in the game 
        if self.__board_np[row][col] == self.__BLACK_turn or self.__board_np[row][col] == self.__BLACK_KING: # the piece is a black 
          self.find_next_pos((row, col), self.__board_np) # find the possible moves for that piece ( if any ) 
          if len(self.__possible_movements) != 0: # if that piece has any possible moves 
            self.__possible_movements = []
            black_lost = False # This condradicts black_lost = True and it will change it to False 
          
        
        if self.__board_np[row][col] == self.__WHITE_turn or self.__board_np[row][col] == self.__WHITE_KING:
          self.find_next_pos((row, col), self.__board_np)
          if len(self.__possible_movements) != 0:
            self.__possible_movements = []
            white_lost = False
            
        
    self.__checking_game_over = False    
    if black_lost == True: # check if black lost 
      self.__game_over = True
      self.__winner = "White"
      self.__playe_active = False
      self.game_loop()
  
    elif white_lost == True: # check if white lost 
      self.__game_over = True
      self.__winner = "Black"
      self.__playe_active = False
      self.game_loop()
        
    else:
      self.__game_over = False # no colour has lost which means that game will go on 

  #########################################################################################
  def draw_board(self): # this will draw the game board 
      for row in range(len(self.__board_np)):
        self.__square_boardx = 0
        self.__square_boardy += 70
        self.__square_board_colour -= 1
        for col in range(len(self.__board_np[row])): # loop through the 2D array representing the board 
            self.__square_board_colour += 1
            if self.__square_board_colour % 2 == 0:

                square_colour = (18,252,151)
                pygame.draw.rect(self.win, square_colour,
                                 (self.__square_boardx, self.__square_boardy, 70, 70)) #draw the squares of the game 
                self.__square_boardx += 70

            else:
                square_colour = (252,18,119)
                pygame.draw.rect(self.win, square_colour,
                                 (self.__square_boardx, self.__square_boardy, 70, 70))
                self.__square_boardx += 70

      # Draw home button 
      pygame.draw.rect(self.win, (0,0,0), (655, 20, 45, 45))
      pygame.draw.rect(self.win, (255,255,255), (670, 40, 15, 15))
      pygame.draw.polygon(self.win, (255,255,255), [(665,40),(677, 30),(690,40)])
      pygame.draw.aaline(self.win, (255,255,255), (665,40), (677, 30))
      pygame.draw.aaline(self.win, (255,255,255), (677, 30),(690, 40))
  
      self.__square_boardx = 0
      self.__square_boardy = -70
  
  ##############################################################################################
  def Add_pieces(self): # This will add the pieces to the board 
    circle_corx = 35
    circle_cory = 35
    
    for row in range(len(self.__board_np)):
        for col in range(len(self.__board_np[row])): #loop thriugh the board 
          piece = self.__board_np[row][col]
          
          if piece != 0 and piece != self.__show_possible_move: # check if its not an empty square 
           
            circle_corx = circle_corx + (70 * (col))
            circle_cory = circle_cory + (70 * (row))
            pygame.draw.circle(self.win, piece.get_rgb_colour() , [circle_corx, circle_cory], 30)
            if piece.get_type()[1] == True: # get the type of the piece to check if it is a king 
              pygame.draw.circle(self.win, self.__KING_COLOR, [circle_corx, circle_cory], 10, 5)
                  
            circle_corx = 35
            circle_cory = 35
  
            #Checks for showing the next move 
          if self.__board_np[row][col] == self.__show_possible_move:
              square_x = col * 70
              square_y = row * 70
              pygame.draw.rect(self.win, self.__BLUE, (square_x, square_y, 70, 70), 5)


#############################################################################################

  def get_board_score(self, board): # this wll calculatethe score of the board 
    white_pieces = 0
    black_pieces = 0
    white_kings = 0
    black_kings = 0

    for row in range(len(board)):
      for piece in board[row]: # loop throgh the game board 
        if piece != 0:
          if piece.get_type() == ("White", False):
            white_pieces = white_pieces + 5 
          if piece.get_type() == ("Black", False):
            black_pieces = black_pieces + 5 
          if piece.get_type() == ("White", True):
            white_kings = white_kings + 8
          if piece.get_type() == ("Black", True):
            black_kings = black_kings + 8 

    
    
    return (white_pieces - black_pieces) + 1.5 * (white_kings - black_kings)
          

###############################################################################################

  def check_for_kings(self, board):
    for col in range(len(board[0])): # checks if any black piece made it to row 0 and turns them into kings 
      if board[0][col] == self.__BLACK_turn:
         board[0][col] = self.__BLACK_KING

    for col in range(len(board[7])): # checks if any white piece made it to row 7 and turns them into kings 
      if board[7][col] == self.__WHITE_turn:
         board[7][col] = self.__WHITE_KING
         
                
###############################################################################################

  
  def get_player_piece(self, pos): 
    #This will get the position of a player piece on the board
      black = [self.__BLACK_turn, self.__BLACK_KING]
      white = [self.__WHITE_turn, self.__WHITE_KING]
    
      if self.__player_turn == self.__BLACK_turn:
        turn = black
      else:
        turn = white
        
      x_pos, y_pos = pos
      row = y_pos // 70
      col = x_pos // 70 
      if col < 8:     
        if self.__is_AI_playing == True or self.__is_AI_playing == False and self.__board_np[row][col] in turn: # return the coordinates of the piece if AI is making a move or the piece that has been selected is part of the player turn
          return ((row, col))
          
      else:
          return (None)


  #######################################################################################

  #This will get the position of what move does the player wants to make and if it is available 
  def get_pos_piece(self, pos):
    x_pos, y_pos = pos
    row = y_pos // 70
    col = x_pos // 70 
    if col < 8: # if the piece tht has been sleceted is on a col greater than 8, it is not part of the game board 
      return (row, col)
    else:
      self.__show_move = True 
      self.__possible_movements = []
      self.__remove = {}
      return (None)

  ######################################################################################
  def find_next_col(self, row, col, move_col_right, move_col_left, row_move, board):
    #This will fin the next col for the piece that has been selected only d the pieece that havs been slecte is the 
    
    if col - move_col_left >= 0 and row + row_move <= 7 and row + row_move >= 0:
      if board[row + row_move][col - move_col_left] == self.__EMPTY_space: # check if the col to the left is empty 
        self.__possible_movements.append((row + row_move, col - move_col_left)) # store the possiblemove 
        self.__remove[(row + row_move, col - move_col_left)] = ((None, None)) # store (None, None) for the piece that would need to be removed as this function does not take into acoun jumping over the opponents piece 
  
    if col + move_col_right <= 7 and row + row_move <= 7 and row + row_move >= 0:
      if board[row + row_move][col + move_col_right] == self.__EMPTY_space: # check if col to the right is empty 
        self.__possible_movements.append((row + row_move, col + move_col_right))# store the possiblemove 
        self.__remove[(row + row_move, col + move_col_right)] = ((None, None))


  ####################################################################################
  def next_col_remove(self, row, col, move_col_right, move_col_left, row_move, jumped_row, board, depth, removed_piece_row, removed_piece_col):
    #This will find the next possible moves of the piece that has been selected ehrn it is jumping over the opponents piece 
    depth -= 1 
    if depth >= 0: # this funct will use recursion so it must have maximum depth 
      black = [self.__BLACK_turn, self.__BLACK_KING]
      white = [self.__WHITE_turn, self.__WHITE_KING]
      
      if self.__player_turn == self.__BLACK_turn:
        turn = black
      else:
        turn = white
      
      if col - move_col_left >= 0 and row + row_move <= 7 and row + row_move >= 0:
        if board[row + row_move][col - move_col_left] == self.__EMPTY_space:# check if the move that the player wants to move to is an empty space
          if board[row + jumped_row][col - 1] not in turn and  board[row + jumped_row][col - 1] != self.__EMPTY_space: #thsi will check that the piece that the player wnats to jump over is noot an empty space nd not its own piece 
            self.__possible_movements.append((row + row_move, col - move_col_left)) # add it to the possible moves that piece seected 
            self.__remove[(row + row_move,col - move_col_left)] = ((row + jumped_row, col - 1 ), (removed_piece_row, removed_piece_col)) # the removable piece to the remove list , this will keep track of what move the and piece needs to be removed according to the move 
            self.next_col_remove( row + row_move, col - move_col_left, move_col_right, move_col_left, row_move, jumped_row, board, depth, row + jumped_row, col - 1 ) #recursively call the function to find possible scenarios where the piece can double jump 
            
      if col + move_col_right <= 7 and row + row_move <= 7 and row + row_move >= 0:
        if board[row + row_move][col + move_col_right] == self.__EMPTY_space:
          if board[row + jumped_row][col + 1] not in turn and board[row + jumped_row][col + 1] != self.__EMPTY_space:
            self.__possible_movements.append((row + row_move, col + move_col_right))
            self.__remove[(row + row_move,col + move_col_right)] = ((row + jumped_row, col + 1 ), (removed_piece_row, removed_piece_col))
            self.next_col_remove( row + row_move, col + move_col_right, move_col_right, move_col_left, row_move, jumped_row, board, depth, row + jumped_row, col + 1 )

  ################################################################################################

  def king_move(self, row, col, board, colour, depth):
    #This will find the next possible moves for a king when it does not look for jumping ver the opponents piece 
    if col + 1 <= 7 and row + 1 <= 7:
      if board[row + 1][col + 1] ==self.__EMPTY_space:
        self.__possible_movements.append((row + 1, col + 1))
        self.__remove[(row + 1, col + 1)] = (None, None)

    if col - 1 >= 0 and row + 1 <= 7:
      if board[row + 1][col - 1] ==self.__EMPTY_space:
        self.__possible_movements.append((row + 1, col - 1))
        self.__remove[(row + 1, col - 1)] = (None, None)

    if col + 1 <= 7 and row - 1 >= 0:
      if board[row - 1][col + 1] ==self.__EMPTY_space:
        self.__possible_movements.append((row - 1, col + 1))
        self.__remove[(row - 1, col + 1)] = (None, None)

    if col - 1 >= 0 and row - 1 >= 0:
      if board[row - 1][col - 1] ==self.__EMPTY_space:
        self.__possible_movements.append((row - 1, col - 1))
        self.__remove[(row - 1, col - 1)] = (None, None)

    if len(self.__possible_movements) < 4: #if the possible moves for the king are less than 4 ( as the king can move 4 ways) it means that it got stopped potentially by a possible jump over the opponents piece 
      self.king_move_take(row, col, board, colour, depth, None, None) #This will call the function that check is the king can jump over the oponents pieces 

  ##################################################################################################
        
  def king_move_take(self, row, col, board, colour, depth, removed_piece_row, removed_piece_col):
    #This will find all the possible moves for a king when it is double jumping and jumping over the opponents piecese 
    depth -= 1
    #This is a recursive function as it needs to check for double jump and it needs a maximum depth
    if depth >= 0:
      
      if colour == self.__BLACK_KING:
        remove_option_list = [self.__WHITE_turn, self.__WHITE_KING]
      
      elif colour == self.__WHITE_KING:
        remove_option_list = [self.__BLACK_turn, self.__BLACK_KING]
      
      if col - 2 >= 0 and row + 2 <= 7:
        if board[row + 2][col - 2] == self.__EMPTY_space: # this will check if the move that it cn make after jumping over a piece is an empty square 
          if board[row + 1][col - 1] in remove_option_list: # This will check if its jumping over the opponents pieces 
            self.__possible_movements.append((row + 2, col - 2)) # add the possible move to the list of possible moves for that piece 
           
            self.__remove[(row + 2,col - 2)] = ((row + 1, col - 1 ), (removed_piece_row, removed_piece_col)) # add the piece tat would nee to be removed is that move is made 
            self.king_move_take(row + 2, col -  2, board, colour, depth, row + 1, col - 1 ) # recyrsively call the function again for a a posssible double jump
      #repeat the process for all 4 directions in wich the king can move 
  
      if col - 2 >= 0 and row - 2 >= 0:
        if board[row - 2][col - 2] == self.__EMPTY_space:
          if board[row - 1][col - 1] in remove_option_list:
            self.__possible_movements.append((row - 2, col - 2))
           
            self.__remove[(row - 2,col - 2)] = ((row - 1, col - 1 ), (removed_piece_row, removed_piece_col))
            self.king_move_take(row - 2, col -  2, board, colour, depth, row - 1, col - 1)
  
      if col + 2 <= 7 and row + 2 <= 7:
        if board[row + 2][col + 2] == self.__EMPTY_space:
          if board[row + 1][col + 1] in remove_option_list:
            self.__possible_movements.append((row + 2, col + 2))
           
            self.__remove[(row + 2,col + 2)] = ((row + 1, col + 1 ), (removed_piece_row, removed_piece_col))
            self.king_move_take(row + 2, col +  2, board, colour, depth, row + 1, col + 1)
  
      if col + 2 <= 7 and row - 2 >= 0:
        if board[row - 2][col + 2] == self.__EMPTY_space:
          if board[row - 1][col + 1] in remove_option_list:
  
            self.__possible_movements.append((row - 2, col + 2))
            
            self.__remove[(row - 2,col + 2)] = ((row - 1, col + 1 ), (removed_piece_row, removed_piece_col))
            self.king_move_take(row - 2, col +  2, board, colour, depth, row - 1, col + 1 )
  
    
  ####################################################################################
  def find_next_pos(self, pos, board):
    # This function is used to call the 4 functins that deal with the moving of the piece 
    # This function will pass the right informtions that are neede to make moves such as curent piece possition and what tipe it is 
    self.__possible_movements = []
    self.__remove ={}
    
    if self.__is_AI_playing == False and self.__checking_game_over == False or self.__is_AI_playing == True and self.__player_turn == self.__BLACK_turn and self.__checking_game_over == False:
      #This will only get the coordinates of the piece if the input is from the players mouse and it needs to translated into rows and columns 
      pos = self.get_player_piece(pos)
   

    if pos != None:  # check if it is a possiblle piece that has been slected 
      row, col = pos
      if board[row][col] != self.__EMPTY_space:
        self.__player_pos = (row, col)
        
        if board[row][col].get_type() == ("White", True): # return the colour and the type of the piece 
          colour = self.__WHITE_KING 
          
          self.king_move(row,col, board, colour, 2) # This will call the funcion that finds the next possible moves for hr king 
  
        if board[row][col].get_type() == ("Black", True):
          colour = self.__BLACK_KING
          self.king_move(row,col, board, colour, 2)
          
        if board[row][col].get_type() == ("Black", False):
          colour = self.__BLACK_turn
          row_move = -1
  
        if board[row][col].get_type() == ("White", False):
          colour =  self.__WHITE_turn
          row_move = 1 

        move_col_right = 1
        move_col_left = 1
        
        if colour == self.__WHITE_turn or colour == self.__BLACK_turn:
          self.find_next_col(row, col, move_col_right, move_col_left, row_move, board) # This will call the functon that finds the next possible moves for a normal piece without jumping over the opponents piece 
  
          
          if len(self.__possible_movements) < 2: # if the length of the possible moves for this normal piece is less than one, ther eis a possibility that the piece an jump over the opponents iece or even double jump
            move_col_right = 2
            move_col_left = 2
            depth = 2
            
            if colour == self.__BLACK_turn:
              row_move = -2
              jumped_row = -1
            else:
              row_move = 2
              jumped_row = 1
    
           
            self.next_col_remove(row, col, move_col_right, move_col_left, row_move, jumped_row, board, depth, None, None) #calls the function that will check for possible double jumps or jump over the opponents piece 
        return self.__possible_movements

  #####################################################################################
      
  def show_next_move(self, pos): # this will show the next possible moves for the piece that has been sleceted 
    self.find_next_pos(pos, self.__board_np) # This will call the function that finds the possible moves for thet piece 
    for pos in self.__possible_movements:# loop through possible moves 
      row, col = pos
      self.__board_np[row][col] = self.__show_possible_move #insert them into the game board 
      self.__show_move = False
      
  #################################################################################
  def clear_possible_movements_board(self): # this will clear the possible moves on the board 
    #this an happen afer the player has moved/wants to move another piece/slected a square the is not part of the possible moves 
    for row in range(len(self.__board_np)):
      for col in range(len(self.__board_np[row])):
        if self.__board_np[row][col] == self.__show_possible_move:
          self.__board_np[row][col] = self.__EMPTY_space #set the square back to empty sqares 
          
  ###################################################################################
  def remove_piece(self, move_made): # this will removes the pieces after the playrer has moved 
    for i in self.__remove[move_made]: #go through the possible removable pieces related to the move that has been made 
      if  isinstance(i, tuple) and  i != (None, None): #if the removable piece is a tuple and it is not (None,None)
        row, col = i
        self.__board_np[row][col] = self.__EMPTY_space #replace that piece on the board with an empty square 
      elif isinstance(i, int)  and  i != None: #if the first element in the remove deictionary is an integer that mean there is only one piece that needs to be removed and the removed dictionary can not be looped as it would break down the piece that needs to be removed into row and columns 
        row, col = self.__remove[move_made]
        self.__board_np[row][col] = self.__EMPTY_space#replace that piece on the board with an empty square 
      
       
  ##################################################################################
  def change_main_player(self): # Thsi will change te main player of the game after a move has been made 
    
    if self.__player_turn == self.__BLACK_turn or self.__player_turn == self.__BLACK_KING:
      self.__player_turn = self.__WHITE_turn
      
    else:
      self.__player_turn = self.__BLACK_turn

  ################################################################################
  def make_move(self, pos):
    #This will make the move selected by the player if it is an availble move 
    self.__next_move = self.get_pos_piece(pos) #gets the next move in rows and columns of the board 
      
    if self.__next_move != None: 
      row, col = self.__next_move

    if self.__player_turn == self.__WHITE_turn and self.__is_AI_playing == True:
      row, col = pos 

    if self.__board_np[row][col] != self.__show_possible_move: #this will check if the move that has been selcted is not part of the possiblemoves for the piece
      self.__possible_movements = []
      self.__remove = {}
      self.__show_move = True
      self.__player_pos = None
      self.clear_possible_movements_board()
      self.show_next_move(pos)
          
    
    for option in self.__possible_movements: ##if the move that has been selected is pat f the possible moves that the piece can make 
      if self.__next_move == option:
        self.remove_piece(option) # remove pieces if needed 
        row_now, col_now = self.__player_pos
        row, col = self.__next_move
        self.__board_np[row][col] = self.__board_np[row_now][col_now] #move the the piece that has originally been selected to the move that square(move) that has been selected by the player 
        self.__board_np[row_now][col_now] = self.__EMPTY_space
        self.__player_pos = None
        self.clear_possible_movements_board() # clear the possible moves on the board 
        self.__possible_movements = []
        self.__remove = {}
        self.__show_move = True
        self.change_main_player()
        self.check_game_over()# check if the game ended after that move
        

  #################################################################################

  def get_pieces(self, board, colour):
    #This will get all the pieces in a board of a sepcific colour 
    pieces = []
    
    if colour == self.__WHITE_turn:
      for row in range(len(board)):
        for col in range(len(board[row])):
          if board[row][col] != 0 and board[row][col].get_type()[0] == "White": #check  if the colour of the piece coresponds with the colour of the argument 
            pieces.append((row,col)) #append the pieces to a list of pieces 

    if colour == self.__BLACK_turn:
      for row in range(len(board)):
        for col in range(len(board[row])):
          if board[row][col] != 0 and board[row][col].get_type()[0] == "Black":
            pieces.append((row,col))
    
    return pieces # return the list of pieces 
    
###################################################################################

  def simulation_board(self, piece, move, board, remove):
    #this will simulate the board depending on the piece selected to move, the move and the board 
    #this will be used when simulating board for the minimax algorithm 
    row_now, col_now = piece
    row, col = move 
    
    board[row][col] = board[row_now][col_now] #make the move 
    board[row_now][col_now] = self.__EMPTY_space # remove the piece that has been moved from the old position 
    self.check_for_kings(board) # check if any pieces have turned into kings 
    self.__remove = remove

    #this will remove pieces that have been jumped 
    for i in self.__remove[move]: 
      if isinstance(i, tuple) and  i != (None, None):
        row, col = i
        board[row][col] = self.__EMPTY_space 
      elif isinstance(i, int) and  i != None: 
        row, col = self.__remove[move]
        board[row][col] = self.__EMPTY_space

    return move, board #return the new board and the move that lead to this new board 

##################################################################################
    
  def get_moves(self, board, colour):
    #This will get the pieces of a colour , moves they can make and removable pieces for the moves that they can make 
    #this will be used by the AI 
    moves = []
    pieces = self.get_pieces(board,colour) # get all the pieces of a specfic colour 
    
    for piece in pieces: #loop through the pieces 
      self.__possible_movements = []
      self.__remove ={}
      for move in self.find_next_pos(piece, board): # find ll the moves for these pieces 
        moves.append((piece, move, self.__remove)) #add all of them to a list 
    self.__possible_movements = []
    self.__remove ={}  
    return  moves #reurn the list 
###################################################################################
  
  def minimax(self, board, depth, isMaximizing):
    #This will caluclate rturn the best board the the AI can get to depending on the next  board that can be made form there 
    #This will create a tree of all possible boards from all the possible moves on the board
    
    if depth == 0: # return the current board and its score when the depth of the algorithm is 0 
      return self.get_board_score(board), board
    
      
    elif isMaximizing == True: # if the algorihm is maximizing so when the AI is tryin to maximize the score of the board 
      max_score = float("-inf") # the best score found by the AI when it first starts is negative infinity 
      best_move = None # no best moves have been found so far 
      
      for piece, move, remove in self.get_moves(board, self.__WHITE_turn): # get all the pssible pieces and moves white can make 
        new_board = deepcopy(board) # make a deepcopy of the board, to change it and calculate the new score of the board without changing the original board 
        move, new_board = self.simulation_board(piece, move, new_board, remove) # simulate all the boards 
        score = self.minimax(new_board, depth -1, False)[0] # call the minimax function but this time when it is mnimizing ( when black is trying to minimize the score), it only needs the first value returned (the score)
        if score >= max_score:
          max_score = score 
         #change the best score that the AI has found with the new one if it is greater than the original 
         #if the score has changed 
          best_move = new_board # best move needs to be updated to the move that has lead to that score 
       
      return max_score, best_move # return the current max score and best move 

    elif isMaximizing == False: # for when the minimizing if on the same process will be applyed but the AI will try to find th best move that would lead to to minimising the score as this would be most likly the move that the player will make 
      min_score = float("inf")
      best_move = None
      for piece, move, remove in self.get_moves(board, self.__BLACK_turn):
        
        new_board = deepcopy(board)
        move, new_board = self.simulation_board(piece, move, new_board, remove)
        score = self.minimax(new_board, depth -1, True)[0]
        if score <= min_score:
          min_score = score 
          best_move = new_board
        
       
      return min_score, best_move
  

################################################################################
  def data_base(self):
    #this will add to the data base when a game is saved 

    data = list(time.gmtime()) # this will get the day and time 
    if self.__is_AI_playing == True: #store in the database if the AI is playin or not 
      ai = self.__AI_level
    else:
      ai = 0

    if self.__player_turn== self.__BLACK_turn: # check if whose turn is it 
      player_turn =1
    else:
      player_turn =2

    if self.__timer_active == True: #if the timer ws active durng the game 
      self.__end_time = time.time() #find the time now 
      sec = (self.__end_time - self.__start_time) + self.__extra_seconds #calulate in seconds the time ince the game has started and add extra seconds (if the game was continued from the saved games it will add the time of the the game before it has originally saved)
      self.__extra_seconds = 0 
      self.__timer_active = False

    else:
      sec = 0
      
    #save these details about the game into the Game_Table
    sqlite_query = """INSERT INTO Game_Table 
                            (Player_Turn, AI, Day, Month, Year, Hour, Minute, time_seconds) 
                            VALUES 
                            (?, ?, ?, ?, ?, ?, ?, ?);""" 

    
    data = (player_turn, ai, data[2], data[1], data[0], data[3], data[4], sec)
    self.__cursor.execute(sqlite_query, data)
    
    self.__cursor.execute("SELECT * FROM Game_Table")
    data_base = self.__cursor.fetchall()
    
    # add data to the Board table:
    #This will get the game id from the game table and use it in the board_table
    game_id = data_base[len(data_base)-1][0]
    for row in range(len(self.__board_np)):
      for col in range(len(self.__board_np[row])): #loop through the board 
        if self.__board_np[row][col] != self.__EMPTY_space and self.__board_np[row][col] != self.__show_possible_move:
          if self.__board_np[row][col] == self.__BLACK_turn: #create a value fr each piece 
            piece = 1
          elif self.__board_np[row][col] == self.__BLACK_KING: 
            piece = 2
          elif self.__board_np[row][col] == self.__WHITE_turn:
            piece = 3
          elif self.__board_np[row][col] == self.__WHITE_KING: 
            piece = 4
          self.__cursor.execute("INSERT INTO Board VALUES (%s, %s, %s, %s)" % (game_id, piece, row, col)) #save the row, column and the piece 
    
    self.__connection.commit() 
    

    # reset the game info 
    self.__possible_movements = []
    self.__remove = {}
    self.__show_move = True
    self.__player_pos = None
    self.__player_turn = self.__BLACK_turn
    self.clear_possible_movements_board() 
    self.__possible_AI_piece = {}
    self.__board_np = [[0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn ,0 ,self.__WHITE_turn], 
                       [self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn, 0], 
                       [0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn], 
                       [0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0], 
                       [self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0], 
                       [0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn], 
                       [self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0]]
    
    self.__home_active = True

##################################################################################
  
  def saved_games(self):
    #This will display the savd games 
    self.__HOME_PAGE = pygame.image.load('paint/saved_games.png') # load the image 
    self.win.blit(self.__HOME_PAGE, (0, 0))

    # Draw the home button 
    pygame.draw.rect(self.win, (0,0,0), (655, 20, 45, 45))
    pygame.draw.rect(self.win, (255,255,255), (670, 40, 15, 15))
    pygame.draw.polygon(self.win, (255,255,255), [(665,40),(677, 30),(690,40)])
    pygame.draw.aaline(self.win, (255,255,255), (665,40), (677, 30))
    pygame.draw.aaline(self.win, (255,255,255), (677, 30),(690, 40))

    #instuctions for how o select a game:
    text = pygame.font.SysFont('arial',20)
    text_surface = text.render("Select the game you want to play by left clicking on the game number : )", True, (0,0,0))
    text_surface2 = text.render("To delete a game right click on the game ID", True, (0,0,0))
    self.win.blit(text_surface,(15, 10))
    self.win.blit(text_surface2,(15, 32))

    self.__cursor.execute("SELECT * FROM Game_Table") 
    data_base = self.__cursor.fetchall() #get all the data from the Game Table
    
    for i in range(len(data_base)):
      if i <= 3: #only show the last 4 saved games 
        text = pygame.font.SysFont('arial',30)
        game = str(data_base[i][0]) #the id of the game
        date = str(data_base[i][3]) + "/" + str(data_base[i][4]) +"/" + str(data_base[i][5]) #the data when the game was saved 
        time_game = str(data_base[i][6]) + ":" + str(data_base[i][7]) #the time when the game was saved 
        
        text_surface_1 = text.render(game, True, (0,0,0))
        text_surface_2 = text.render(date, True, (0,0,0))
        text_surface_3 = text.render(time_game, True, (0,0,0))
        self.win.blit(text_surface_1,(98, 163 + i * 90))
        self.win.blit(text_surface_2,(200, 163 + i * 90))
        self.win.blit(text_surface_3,(450, 163 + i * 90))

    #find out what game has been selected 
    for event in pygame.event.get():
      if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
          pos = event.pos
          x, y = pos #get the x and y position of the mouse when pressed 
          if x > 70 and x < 160 and y > 138 and y < 490:
            game = (y - 138) // 88 # find the game id
            if game <= len(data_base) -1:
              #create the new game 
              id = data_base[game][0] # set the id
              if data_base[game][2] != 0: # if the ai in the data base is true: set ai as true, get the extra seconds from the data base
                self.__is_AI_playing = True 
                self.__AI_level = data_base[game][2]
                self.__extra_seconds = data_base[game][8]
                self.__start_time = time.time() #restart the start clock so when game is finished calulate end - start + extra seconds 
                self.__timer_active = True
                
              elif data_base[game][2] == 0:
                self.__is_AI_playing = False
                
              if data_base[game][1] == 1:
                self.__player_turn = self.__BLACK_turn
              else:
                self.__player_turn = self.__WHITE_turn
              
              self.__board_np = [[0, 0, 0, 0, 0, 0, 0, 0], 
                                  [0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0], 
                                  [0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0], 
                                  [0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0], 
                                  [0, 0, 0, 0, 0, 0, 0, 0]]
                
              
              self.__cursor.execute("SELECT Board.*, Game_Table.Game_ID  FROM Board, Game_Table WHERE Board.Game_ID = Game_Table.Game_ID AND Game_Table.Game_ID = %s" % (id)) #get all data from the Board table where the id of the piece saved in the board table mathches the ID of saved game
              board_data_base = self.__cursor.fetchall()
              for i in range(len(board_data_base)):
                #recreate the board using the pieces saved and their roe and col 
                if board_data_base[i][1] == 1:
                  self.__board_np[board_data_base[i][2]][board_data_base[i][3]] = self.__BLACK_turn
                elif board_data_base[i][1] == 2:
                  self.__board_np[board_data_base[i][2]][board_data_base[i][3]] = self.__BLACK_KING
                elif board_data_base[i][1] == 3:
                  self.__board_np[board_data_base[i][2]][board_data_base[i][3]] = self.__WHITE_turn
                elif board_data_base[i][1] == 4:
                  self.__board_np[board_data_base[i][2]][board_data_base[i][3]] = self.__WHITE_KING
              #delete the game that has been selected from the data base 
              self.__cursor.execute("DELETE FROM Board WHERE Game_ID = ?" , [(id)])
              self.__cursor.execute("DELETE FROM Game_Table WHERE Game_ID = ?", [(id)])
              
              self.__connection.commit() 
  
              self.__playe_active = True
              self.__home_active = False
              self.__data_base_active = False
  
          elif x >= 655 and x <= 700 and y >= 20 and y <= 65: #if the player did not click on the id of a game and clicked on the home button 
            self.__playe_active = False
            self.__home_active = True
            self.__data_base_active = False

        if event.button == 3:
          pos = event.pos
          x, y = pos #get the x and y position of the mouse when pressed 
          if x > 70 and x < 160 and y > 138 and y < 490:
            game = (y - 138) // 88 # find the game id
            if game <= len(data_base) -1:
              id = data_base[game][0] # set the id
              #delete the game that has been selected from the data base 
              self.__cursor.execute("DELETE FROM Board WHERE Game_ID = ?" , [(id)])
              self.__cursor.execute("DELETE FROM Game_Table WHERE Game_ID = ?", [(id)])

    self.__connection.commit() 
    
  
#################################################################################

  def is_data_base_empty(self):
    #THis wll check if any games have been saved 
    #the saved game butto will only be displayed if there is at east on game saved 
    self.__cursor.execute("SELECT * FROM Game_Table")
    data_base = self.__cursor.fetchall()
    
    if data_base == []:
      return True
    else:
      return False
    
  
##################################################################################

  def start_new_game(self):
    #This will start a new game 
    #it will controll all the functions of the game while it is beeing played 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            self.__game_over = True
          
        if event.type == pygame.MOUSEBUTTONDOWN:
          # This will check to see if the player is black or white and there are two people playing
          
          if self.__player_turn == self.__BLACK_turn or self.__player_turn == self.__BLACK_KING or self.__player_turn == self.__WHITE_turn or self.__player_turn == self.__WHITE_KING and self.__is_AI_playing == False:

            #show the moves for the piece clicked by the player 
            if self.__show_move == True and event.pos[0] < 560 and event.pos[1] < 560:
              self.show_next_move(event.pos)
              
              
            # This will check if you clicked on the save button  
            if event.pos[0] >= 655 and event.pos[0] <= 700 and event.pos[1] >= 20 and event.pos[1] <= 65: 
              self.data_base()

            #if the possible moves for a piece are beeing desplaued (show_move == False) then the piece that has been slected could be the piece that the playerwants to move to 
            elif self.__show_move == False and event.pos[0] < 560 and event.pos[1] < 560:
              self.make_move(event.pos)
           
    self.win.fill((102,232,117))
    self.draw_board() # draw the board 
    self.Add_pieces()# draw the pieces 
    self.check_for_kings(self.__board_np) 
    
    if self.__player_turn == self.__WHITE_turn and self.__is_AI_playing == True: # if the AI has to move now 
      score, new_board = self.minimax(self.__board_np, self.__AI_level, True) #call the inimax function tet will return the bestmove that the AI can make 

      #This extra step is necessary as the deepcopy of the board changes the objects from which the game board is made 
      for row in range(len(new_board)):
        for col in range(len(new_board[row])): #loopthrough the new board 
          if new_board[row][col] != 0: #if the square  is not an empty space 
            if new_board[row][col].get_type() == ("Black", False): #get the type of the piece 
              new_board[row][col] = self.__BLACK_turn #add the new piece to the board 
            
            if new_board[row][col].get_type() == ("Black", True):
              new_board[row][col] = self.__BLACK_KING
            
            if new_board[row][col].get_type() == ("White", False):
              new_board[row][col] = self.__WHITE_turn 
            
            if new_board[row][col].get_type() == ("White", True):
              new_board[row][col] = self.__WHITE_KING
            
           
      self.__board_np = new_board #create the new board 
      self.check_for_kings(self.__board_np)
      self.check_game_over()
      self.change_main_player() 

##################################################################

  def game_rules(self):
    #This will display the rules of the game 
    for event in pygame.event.get():
      if event.type == pygame.MOUSEBUTTONDOWN:
        pos = event.pos
        x, y = pos #get the x and y position of where the player clicked on the game rules pages 

        if x>= 303 and y>= 511 and x<= 400 and y <= 555: #if the player clicked on the arrow that points to the next page of rules 
          self.__rule += 1

    #depending on the rule count 
    #it will vhang the page that dsiplayes that rule 
    if self.__rule == 0:
      page = pygame.image.load('paint/Rule_nr1.png')
      
    elif self.__rule == 1:
      page = pygame.image.load('paint/Rule_nr2.png')
      
    elif self.__rule == 2:
      page = pygame.image.load('paint/Rule_nr3.png')
      
    if self.__rule <= 2:
      self.win.blit(page, (0, 0))

    if self.__rule == 3: #if the rule has went up to 3, the player will be sent back to the home menu 
      self.__rule = 0
      self.__game_rules = False
      self.__home_active = True
    

      
########################
  
  def home(self):
    #this will display the home menu and all the button thet is has 
    for event in pygame.event.get():
      if event.type == pygame.MOUSEBUTTONDOWN:
        pos = event.pos
        x, y = pos

        if x >= 255 and x <= 455 and y >= 340 and y <= 390:# this will check if the plyer hs clicked on the 1 Player button 
          self.__is_AI_playing = True
          self.__playe_active = True
          self.__home_active = False 
          self.__levels = True
          self.__start_time = time.time()
          self.__timer_active = True

        elif x >= 255 and x <= 455 and y >= 430 and y <= 480: #This will check if the player has clickd on the 2 Players button 
          self.__is_AI_playing = False
          self.__playe_active = True
          self.__home_active = False

        elif x >= 245 and x <= 465 and y >= 250 and y <= 300: #This will check if the player has clicked on the saved games button 
          self.__home_active = False
          self.__playe_active = False
          self.__data_base_active = True

        if x >= 20 and x <= 220 and y >= 340 and y <= 580: # This will check if the player has clicked on the Game Rules button 
          self.__game_rules = True 
          self.__playe_active = False
          self.__home_active = False 
          
          
         
    HOME_PAGE = pygame.image.load('paint/CHECKERS_HOME_PAGE.png') #this will load the background image of the home page 
    self.win.blit(HOME_PAGE, (0, 0))

    #draw the buttons of the game 
    pygame.draw.rect(self.win, (10,10,10), (255, 430, 200, 50))
    pygame.draw.rect(self.win, (10,10,10), (255, 340, 200, 50))
    pygame.draw.rect(self.win, (10,10,10), (20, 340, 200, 140))
   
    
    if self.is_data_base_empty() == False: #This wil only draw te the saved games button if the data base is not empty ( at least one game has been save )
      pygame.draw.rect(self.win, (10,10,10), (245, 250, 220, 50))
      text = pygame.font.SysFont('arial',30)
      text_surface = text.render("Continue Game", True, (255,255,255))
      self.win.blit(text_surface,(253, 260))

    #Add text to each button 
    text = pygame.font.SysFont('arial',30)
    text_surface = text.render("1 Player", True, (255,255,255))
    self.win.blit(text_surface,(295, 350))

    text_surface = text.render("2 Player", True, (255,255,255))
    self.win.blit(text_surface,(295, 440))

    text_surface = text.render("Game Rules", True, (255,255,255))
    self.win.blit(text_surface,(35, 400))

#####################################################################################
  def save_best_time(self, level, time):
    #This will save a new best time 
    self.__cursor_levels.execute("SELECT * FROM Best_times") #this will get all the best times from the Best_times table  
    data_base = self.__cursor_levels.fetchall()

    self.__cursor_levels.execute("DELETE FROM Best_times") # delete existing data in the data base
    
    if data_base == []: #if the list of the data the has just been fetched is empty the simply insert the time of the game 
      if level == 1:
        self.__cursor_levels.execute("INSERT INTO Best_times (Easy) VALUES (?);", (time,))
      if level == 2:
        self.__cursor_levels.execute("INSERT INTO Best_times (Medium) VALUES (?);", (time,))
      if level == 3:
        self.__cursor_levels.execute("INSERT INTO Best_times (Hard) VALUES (?);", (time,))
       
    elif level == 1 and data_base != []: # check if data base is not emty 
      if data_base[0][0] == None or data_base[0][0] > time: # if there is a time saved for the level then compare it with th current time and insert the best one   
        #repeat the prcess for the 3 different levels 
        self.__cursor_levels.execute("INSERT INTO Best_times (Easy, Medium, Hard) VALUES (?, ?, ?);", (time, data_base[0][1], data_base[0][2]))

      else:
        self.__cursor_levels.execute("INSERT INTO Best_times (Easy, Medium, Hard) VALUES (?, ?, ?);", (data_base[0][0], data_base[0][1], data_base[0][2]))
      
    elif level == 2 and data_base != []:
      if data_base[0][1] == None or data_base[0][1] > time:
        self.__cursor_levels.execute("INSERT INTO Best_times (Easy, Medium, Hard ) VALUES (?, ?,?);", (data_base[0][0], time, data_base[0][2]))

      else:
        self.__cursor_levels.execute("INSERT INTO Best_times (Easy, Medium, Hard) VALUES (?, ?, ?);", (data_base[0][0], data_base[0][1], data_base[0][2]))
     
    elif level == 3 and data_base != []:
      if data_base[0][2] == None or data_base[0][2] > time:
        self.__cursor_levels.execute("INSERT INTO Best_times (Easy, Medium, Hard ) VALUES (?, ?,?);", (data_base[0][0], data_base[0][1], time))
     
      else:
        self.__cursor_levels.execute("INSERT INTO Best_times (Easy, Medium, Hard) VALUES (?, ?, ?);", (data_base[0][0], data_base[0][1], data_base[0][2]))
      
    
    self.__connection_levels.commit()
########################################################################################
  
  def levels(self):
    #this will disply the levels of the AI and the best time it took to solve each on of them
    for event in pygame.event.get():
      if event.type == pygame.MOUSEBUTTONDOWN:
        pos = event.pos
        x, y = pos # the possition of the mouse when it has been pressed 

        if x > 21 and x < 286: #check if it was within the possible buttons for each level 
          # check for each level if it was within the right y coordinates of the button 
          if y > 139 and y < 226:
            self.__AI_level = 1 # slect the level of the game ( this will be te depth of the minimax algorithm )
            self.__levels = False
            
          if y > 269 and y < 357:
            self.__AI_level = 2
            self.__levels = False

          if y > 403 and y < 490:
            self.__AI_level = 3
            self.__levels = False
            
    levels = pygame.image.load('paint/LEVELS.png') #display the levels
    self.win.blit(levels, (0,0))

    self.__cursor_levels.execute("SELECT * FROM Best_times") # get the best times
    data_base = self.__cursor_levels.fetchall()
    if data_base != []:
      for i in range(len(data_base[0])):
        if data_base[0][i] != None:
          #the best  time is saved in seconds soit must be turned into minutes and seconds 
          seconds = data_base[0][i]
          seconds = round(seconds)
          min = seconds // 60
          sec = seconds - (min*60)
          
          #siplay the best times 
          text = pygame.font.SysFont('arial',26)
          time = "min: " + str(min) + ", seconds: " + str(sec)
          time = text.render(time, True, (0,0,0))
          self.win.blit(time,(414, 160 + i * 140))
         
  ################################################################################################  
  def end_game_stats(self):
    #This will display the end of game stats stating who the winne was 
    for event in pygame.event.get():
      if event.type == pygame.MOUSEBUTTONDOWN:
        if event.pos[0] >= 655 and event.pos[0] <= 700 and event.pos[1] >= 20 and event.pos[1] <= 65: #check if th player has clicked on the home button 
          self.__home_active = True
          self.__game_over = False
    
    if self.__is_AI_playing == True: # this will check if the game that has just been finished was afainst an AI 
      
      if self.__winner == "White":
        end = pygame.image.load('paint/You Lost!.png') #if white was the winner of the game display this 
      elif self.__winner == "Black":
        end = pygame.image.load('paint/You Won!.png')#if black is the winner display his 
        if self.__timer_active == True:
          self.__end_time = time.time() #get the time when the game ended , this can be used to save a new best time 
          self.save_best_time(self.__AI_level, (self.__end_time - self.__start_time) + self.__extra_seconds ) #call the function that saves the best time for each level of the AI
          self.__timer_active = False
          self.__extra_seconds = 0
        
    else:
      #this is for when 2Player game has ended 
      if self.__winner == "White":
        end = pygame.image.load('paint/Player 2 Won!.png')
      elif self.__winner == "Black":
        end = pygame.image.load('paint/Player 1 Won!.png')
      
    self.win.blit(end, (0, 0))
    
    # Draw home button 
    pygame.draw.rect(self.win, (0,0,0), (655, 20, 45, 45))
    pygame.draw.rect(self.win, (255,255,255), (670, 40, 15, 15))
    pygame.draw.polygon(self.win, (255,255,255), [(665,40),(677, 30),(690,40)])
    pygame.draw.aaline(self.win, (255,255,255), (665,40), (677, 30))
    pygame.draw.aaline(self.win, (255,255,255), (677, 30),(690, 40))
  
    # reset the game info 
    self.__possible_movements = []
    self.__remove = {}
    self.__show_move = True
    self.__player_pos = None
    self.__player_turn = self.__BLACK_turn
    self.clear_possible_movements_board() 
    self.__possible_AI_piece = {}
    self.__AI_level = None
    self.__board_np = [[0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn ,0 ,self.__WHITE_turn], 
                       [self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn, 0], 
                       [0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn, 0, self.__WHITE_turn], 
                       [0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0], 
                       [self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0], 
                       [0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn], 
                       [self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0, self.__BLACK_turn, 0]]

##################################################################################
  
  def game_loop(self):
    # is the game loop 
    #it will change between the windows of the game   
    if self.__home_active == True:
      self.home()

    elif self.__playe_active == True and self.__levels == True:
      self.levels()
    
    elif self.__playe_active == True:
      self.start_new_game()

    elif self.__data_base_active == True:
      self.saved_games()

    elif self.__game_over == True:
      self.end_game_stats()

    elif self.__game_rules == True:
      self.game_rules()
      
    pygame.display.flip()

################### game loop ########################

class Piece:
  def __init__(self, colour, king, colour_rgb):
    self.__colour = colour
    self.__king = king
    self.__colour_rgb = colour_rgb

  def get_rgb_colour(self):
    #This will return the the colour oof the piece in rgb form 
    return self.__colour_rgb

  def get_type(self):
    #this will return the colour of the piece as a string "WHite"/"Black " and if the piece is a king or not 
    return (self.__colour, self.__king)


class CUBE:
  def __init__(self):
    self.win = pygame.display.set_mode((720, 560))
    
    self.cube = [[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1 , 1, 1],[-1, -1, -1],[1, -1, -1],[1, 1, -1], [-1, 1,-1]]
    self.dict = {0:[1,3,4], 2:[1,3,6], 5:[4,6,1], 7:[6,3,4]}
    self.loading =0
    self.loaded = False

    
  def draw(self):
    #This function will draw the cube on the screen 
    for base in self.dict:#for point in the dictionary that connects the points together forming the lins of the cube 
      for point in self.dict[base]: #for point that can be connected to that point through a line forming a cube 
        #draw a line connected from the point in the cube list of points (that forms a cube) to the next point 
        #every point will be scaled to the dimensions of the window 
        #perspective will also be applied to the points, making the back side of the square smaller than the front side 
        pygame.draw.line(self.win, (255, 255, 255), (self.cube[base][0]/(2-self.cube[base][2]/2) * 100 + 360, self.cube[base][1]/(2-self.cube[base][2]/2) *100 + 280) , (self.cube[point][0]/(2-self.cube[point][2]/2)*100+360, self.cube[point][1]/(2-self.cube[point][2]/2)*100+280),5)
        
    #this will draw the loading square under the cube 
    pygame.draw.rect(self.win, (255, 255, 255), (315, 490, 110 , 20), 4)
    pygame.draw.rect(self.win, (255, 255, 255), (315, 490, self.loading, 20))
    self.loading += 0.01
    if self.loading >= 110:
      self.loaded = True
  
  ########################################################################################################
  def rotate_y(self, ang):
    #this function will find the next coordinates in 3d after the spin is applyed to every point in the cube list 
    new_cube = []
    #create a rotation matrix for the y spin 
    spin_y = [[np.cos(ang), 0, -np.sin(ang)],
              [0,1,0],
              [np.sin(ang), 0, np.cos(ang)]]
  
    for i in range(len(self.cube)): #for ponint forming the cube (the points are made of x,y,z)
      point = np.dot(self.cube[i] ,spin_y ) # times the matrices together 
      new_cube.append(point) #append the new point 
  
    self.cube = new_cube
  
  ########################################################################################################
  def rotate_z(self, ang):
    #this function will find the next coordinates in 3d after the spin is applyed to every point in the cube list
    new_cube = []
    #create a rotation matrix for the Z spin 
    spin_z = [[np.cos(ang), np.sin(ang), 0],
              [-np.sin(ang), np.cos(ang), 0],
              [0,0,1]]
    
    for i in range(len(self.cube)):
      point = np.dot(self.cube[i], spin_z)
      new_cube.append(point)
  
    self.cube = new_cube
  ########################################################################################################
  def is_loaded(self):
    #return True if the loading screen has ended 
    return self.loaded

  #####################################################################################
  def cube_spin(self):
    self.win.fill((0,0,0))
    self.rotate_y(0.0005)
    self.rotate_z(0.0005)
    self.draw()
      
    pygame.display.update() 


loading = CUBE() #create the loading screen object (cube)
while loading.is_loaded() == False:
  loading.cube_spin()

time.sleep(0.7)
Game = GAME() 
while True:
  Game.game_loop()

