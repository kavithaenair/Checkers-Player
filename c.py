import pygame, sys
from pygame import QUIT, MOUSEBUTTONDOWN

pygame.font.init()
##COLORS##
#             R    G    B 
WHITE    = (153,  76,   0)
BLUE     = (  0,   0, 255)
RED      = (255,   0,   0)
BLACK    = (  0,   0,   0)
GOLD     = (255, 215,   0)
HIGH     = (160, 190, 255)
##DIRECTIONS##
NORTHWEST = "northwest"
NORTHEAST = "northeast"
SOUTHWEST = "southwest"
SOUTHEAST = "southeast"

class Game:
	"""The main game control."""
	def __init__(s):
		s.graphics = Graphics()
		s.board = Board()
		
		s.turn = BLUE
		s.selected_piece = None # a board location. 
		s.hop = False
		s.selected_legal_moves = []

	def setup(s):
		"""Draws the window and board at the beginning of the game"""
		s.graphics.setup_window()

	def event_loop(s):
		"""The event loop. This is where events are triggered (like a mouse click) and then effect the game state."""
		s.mouse_pos = s.graphics.board_coords(pygame.mouse.get_pos()) # what square is the mouse in?
		if s.selected_piece != None:
			s.selected_legal_moves = s.board.legal_moves(s.selected_piece, s.hop)

		for event in pygame.event.get(): #returns eventlist which it gets from the queue

			if event.type == QUIT:
				s.terminate_game()

			if event.type == MOUSEBUTTONDOWN:
				if s.hop == False:
					if s.board.location(s.mouse_pos).occupant != None and s.board.location(s.mouse_pos).occupant.color == s.turn:
						s.selected_piece = s.mouse_pos

					elif s.selected_piece != None and s.mouse_pos in s.board.legal_moves(s.selected_piece):

						s.board.move_piece(s.selected_piece, s.mouse_pos)
					
						if s.mouse_pos not in s.board.adjacent(s.selected_piece):
							s.board.remove_piece((s.selected_piece[0] + (s.mouse_pos[0] - s.selected_piece[0]) / 2, s.selected_piece[1] + (s.mouse_pos[1] - s.selected_piece[1]) / 2))
						
							s.hop = True
							s.selected_piece = s.mouse_pos

						else:
							s.end_turn()

				if s.hop == True:					
					if s.selected_piece != None and s.mouse_pos in s.board.legal_moves(s.selected_piece, s.hop):
						s.board.move_piece(s.selected_piece, s.mouse_pos)
						s.board.remove_piece((s.selected_piece[0] + (s.mouse_pos[0] - s.selected_piece[0]) / 2, s.selected_piece[1] + (s.mouse_pos[1] - s.selected_piece[1]) / 2))

					if s.board.legal_moves(s.mouse_pos, s.hop) == []:
							s.end_turn()

					else:
						s.selected_piece = s.mouse_pos


	def update(s):
		"""Calls on the graphics class to update the game display."""
		s.graphics.update_display(s.board, s.selected_legal_moves, s.selected_piece)

	def terminate_game(s):
		"""Quits the program and ends the game."""
		pygame.quit()
		sys.exit

	def main(s):
		""""This executes the game and controls its flow."""
		s.setup()

		while True: # main game loop
			s.event_loop()
			s.update()

	def end_turn(s):
		"""End the turn. Switches the current player. 
		end_turn() also checks for and game and resets a lot of class attributes."""
		if s.turn == BLUE:
			s.turn = RED
		else:
			s.turn = BLUE

		s.selected_piece = None
		s.selected_legal_moves = []
		s.hop = False

		if s.check_for_endgame():
			if s.turn == BLUE:
				s.graphics.draw_message("RED WINS!")
			else:
				s.graphics.draw_message("BLUE WINS!")

	def check_for_endgame(s):
		"""Checks to see if a player has run out of moves or pieces. If so, then return True. Else return False."""
		for x in range(8):
			for y in range(8):
				if s.board.location((x,y)).color == BLACK and s.board.location((x,y)).occupant != None and s.board.location((x,y)).occupant.color == s.turn:
					if s.board.legal_moves((x,y)) != []:
						return False

		return True

class Graphics:
	def __init__(s):
		s.caption = "Checkers Players"

         	s.fps = 60
         	s.clock = pygame.time.Clock()

		s.window_size = 600
		s.screen = pygame.display.set_mode((s.window_size, s.window_size))
	        s.background = pygame.image.load('board.png')

		s.square_size = s.window_size / 8
		s.piece_size = s.square_size / 2

		s.message = False

	def setup_window(s):
		"""This initializes the window and sets the caption at the top."""
		pygame.init()
		pygame.display.set_caption(s.caption)

	def update_display(s, board, legal_moves, selected_piece):
		"""This updates the current display."""
		s.screen.blit(s.background, (0,0))
		
		s.highlight_squares(legal_moves, selected_piece)
		s.draw_board_pieces(board)

		if s.message:
			s.screen.blit(s.text_surface_obj, s.text_rect_obj)

		pygame.display.update()
		s.clock.tick(s.fps)

	def draw_board_squares(s, board):
		"""Takes a board object and draws all of its squares to the display"""
		for x in range(8):
			for y in range(8):
				pygame.draw.rect(s.screen, board[x][y].color, (x * s.square_size, y * s.square_size, s.square_size, s.square_size), )
	
	def draw_board_pieces(s, board):
		"""Takes a board object and draws all of its pieces to the display"""
		for x in range(8):
			for y in range(8):
				if board.matrix[x][y].occupant != None:
					pygame.draw.circle(s.screen, board.matrix[x][y].occupant.color, s.pixel_coords((x,y)), s.piece_size) 

					if board.location((x,y)).occupant.king == True:
						pygame.draw.circle(s.screen, GOLD, s.pixel_coords((x,y)), int (s.piece_size / 2), s.piece_size / 4)


	def pixel_coords(s, board_coords):
		"""Takes in a tuple of board coordinates (x,y) 
		and returns the pixel coordinates of the center of the square at that location."""
		return (board_coords[0] * s.square_size + s.piece_size, board_coords[1] * s.square_size + s.piece_size)

	def board_coords(s, (pixel_x, pixel_y)):
		"""Does the reverse of pixel_coords(). Takes in a tuple of of pixel coordinates and returns what square they are in."""
		return (pixel_x / s.square_size, pixel_y / s.square_size)	

	def highlight_squares(s, squares, origin):
		"""Squares is a list of board coordinates. 
		highlight_squares highlights them."""
		for square in squares:
			pygame.draw.rect(s.screen, HIGH, (square[0] * s.square_size, square[1] * s.square_size, s.square_size, s.square_size))	

		if origin != None:
			pygame.draw.rect(s.screen, HIGH, (origin[0] * s.square_size, origin[1] * s.square_size, s.square_size, s.square_size))

	def draw_message(s, message):
		"""Draws message to the screen. """
		s.message = True
		s.font_obj = pygame.font.Font('freesansbold.ttf', 44)
		s.text_surface_obj = s.font_obj.render(message, True, HIGH, BLACK)#draw text on new surface
		s.text_rect_obj = s.text_surface_obj.get_rect()
		s.text_rect_obj.center = (s.window_size / 2, s.window_size / 2)

class Board:
	def __init__(s):
		s.matrix = s.new_board()

	def new_board(s):
		"""Create a new board matrix."""
		# initialize squares and place them in matrix
		matrix = [[None] * 8 for i in range(8)]
		for x in range(8):
			for y in range(8):
				if (x % 2 != 0) and (y % 2 == 0):
					matrix[y][x] = Square(WHITE)
				elif (x % 2 != 0) and (y % 2 != 0):
					matrix[y][x] = Square(BLACK)
				elif (x % 2 == 0) and (y % 2 != 0):
					matrix[y][x] = Square(WHITE)
				elif (x % 2 == 0) and (y % 2 == 0): 
					matrix[y][x] = Square(BLACK)

		# initialize the pieces and put them in the appropriate squares

		for x in range(8):
			for y in range(3):
				if matrix[x][y].color == BLACK:
					matrix[x][y].occupant = Piece(RED)
			for y in range(5, 8):
				if matrix[x][y].color == BLACK:
					matrix[x][y].occupant = Piece(BLUE)

		return matrix

	def rel(s, dir, (x,y)):
		"""Returns the coordinates one square in a different direction to (x,y)."""
		if dir == NORTHWEST: 
			return (x - 1, y - 1)
		elif dir == NORTHEAST:
			return (x + 1, y - 1)
		elif dir == SOUTHWEST:
			return (x - 1, y + 1)
		elif dir == SOUTHEAST:
			return (x + 1, y + 1)
		else:
			return 0

	def adjacent(s, (x,y)):
		"""Returns a list of squares locations that are adjacent (on a diagonal) to (x,y)."""
        	return [s.rel(NORTHWEST, (x,y)), s.rel(NORTHEAST, (x,y)),s.rel(SOUTHWEST, (x,y)),s.rel(SOUTHEAST, (x,y))]

	def location(s, (x,y)):
		"""Takes a set of coordinates as arguments and returns s.matrix[x][y]
		This can be faster than writing something like s.matrix[coords[0]][coords[1]]"""
		return s.matrix[x][y]

	def blind_legal_moves(s, (x,y)):
		"""Returns a list of blind legal move locations from a set of coordinates (x,y) on the board. 
		If that location is empty, then blind_legal_moves() return an empty list."""
		if s.matrix[x][y].occupant != None:
			
			if s.matrix[x][y].occupant.king == False and s.matrix[x][y].occupant.color == BLUE:
				blind_legal_moves = [s.rel(NORTHWEST, (x,y)), s.rel(NORTHEAST, (x,y))]
				
			elif s.matrix[x][y].occupant.king == False and s.matrix[x][y].occupant.color == RED:
				blind_legal_moves = [s.rel(SOUTHWEST, (x,y)), s.rel(SOUTHEAST, (x,y))]

			else:
				blind_legal_moves = [s.rel(NORTHWEST, (x,y)), s.rel(NORTHEAST, (x,y)), s.rel(SOUTHWEST, (x,y)), s.rel(SOUTHEAST, (x,y))]

		else:
			blind_legal_moves = []

		return blind_legal_moves

	def legal_moves(s, (x,y), hop = False):
		"""Returns a list of legal move locations from a given set of coordinates (x,y) on the board.
		If that location is empty, then legal_moves() returns an empty list."""

		blind_legal_moves = s.blind_legal_moves((x,y)) 
		legal_moves = []

		if hop == False:
			for move in blind_legal_moves:
				if s.on_board(move):
						if s.location(move).occupant == None:
							legal_moves.append(move)

						elif s.location(move).occupant.color != s.location((x,y)).occupant.color and s.on_board((move[0] + (move[0] - x), move[1] + (move[1] - y))) and s.location((move[0] + (move[0] - x), move[1] + (move[1] - y))).occupant == None: # is this location filled by an enemy piece?
							legal_moves.append((move[0] + (move[0] - x), move[1] + (move[1] - y)))

		else: # hop == True
			for move in blind_legal_moves:
				if s.on_board(move) and s.location(move).occupant != None:
					if s.location(move).occupant.color != s.location((x,y)).occupant.color and s.on_board((move[0] + (move[0] - x), move[1] + (move[1] - y))) and s.location((move[0] + (move[0] - x), move[1] + (move[1] - y))).occupant == None: # is this location filled by an enemy piece?
						legal_moves.append((move[0] + (move[0] - x), move[1] + (move[1] - y)))

		return legal_moves

	def remove_piece(s, (x,y)):
		"""Removes a piece from the board at position (x,y). """
		s.matrix[x][y].occupant = None

	def move_piece(s, (start_x, start_y), (end_x, end_y)):
		"""Move a piece from (start_x, start_y) to (end_x, end_y)."""
		s.matrix[end_x][end_y].occupant = s.matrix[start_x][start_y].occupant
		s.remove_piece((start_x, start_y))

		s.king((end_x, end_y))

	def is_end_square(s, coords):
		"""Is passed a coordinate tuple (x,y), and returns true or 
		false depending on if that square on the board is an end square."""
		if coords[1] == 0 or coords[1] == 7:
			return True
		else:
			return False

	def on_board(s, (x,y)):
		"""Checks to see if the given square (x,y) lies on the board.
		If it does, then on_board() return True. Otherwise it returns false."""
		if x < 0 or y < 0 or x > 7 or y > 7:
			return False
		else:
			return True

	def king(s, (x,y)):
		"""Takes in (x,y), the coordinates of square to be considered for kinging.
	If it meets the criteria, then king() kings the piece in that square and kings it."""
		if s.location((x,y)).occupant != None:
			if (s.location((x,y)).occupant.color == BLUE and y == 0) or (s.location((x,y)).occupant.color == RED and y == 7):
				s.location((x,y)).occupant.king = True 

class Piece:
	def __init__(s, color, king = False):
		s.color = color
		s.king = king

class Square:
	def __init__(s, color, occupant = None):
		s.color = color # color is either BLACK or WHITE
		s.occupant = occupant # occupant is a Square object

def main():
	game = Game()
	game.main()
main()
