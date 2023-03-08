from tkinter import *
from random import randint
from tkextrafont import Font
from copy import copy

HEIGHT = 1000
WIDTH = 1400
SPACE_SIZE = 20

class MazeGame:
    def __init__(self):
        """
        Initialises the game object, without actually starting the game
        """

        self.window = Tk()
        self.window.title('Maze Generator')
        self.window.resizable(False, False)
        self.window.configure(bg = 'black')

        self.time = 0
        self.dots = 0
        
        self.font = Font(file = 'resources/upheavtt.ttf', family = 'Upheaval TT -BRK-', size = 50)

        self.game_started       = False
        self.lost_game          = False
        self.game_over          = False
        self.done_drawing       = False

        self.show_after = None

        self.canvas = Canvas(self.window, height = HEIGHT, width = WIDTH, relief = RAISED, bg = 'black')
        self.canvas.pack()

        self.timer = Label(self.window, text='', font = ("Arial", 30), bg = "black", fg = "white")
        self.timer.pack()

        self.start_menu_img = PhotoImage(file = 'resources\menu.png')
        self.canvas.create_image(0, 0, image = self.start_menu_img, anchor = NW)

        self.end_img = PhotoImage(file = 'resources\end_menu.png')

        self.window.bind('<Button-1>',          lambda e: self.click())
        self.window.bind('<Left>',              lambda e: self.press_key('left'))
        self.window.bind('<Right>',             lambda e: self.press_key('right'))
        self.window.bind('<Up>',                lambda e: self.press_key('up'))
        self.window.bind('<Down>',              lambda e: self.press_key('down'))
        self.window.bind('<KeyRelease-Left>',   lambda e: self.press_key('left', False))
        self.window.bind('<KeyRelease-Right>',  lambda e: self.press_key('right', False))
        self.window.bind('<KeyRelease-Up>',     lambda e: self.press_key('up', False))
        self.window.bind('<KeyRelease-Down>',   lambda e: self.press_key('down', False))
        self.window.bind('<Escape>',            lambda e: self.show_solution())

        self.window.mainloop()

    def start(self):
        """
        Starts the game by creating the loading text and starting the draw maze process
        """

        self.canvas.delete('all')
        self.font.configure(size = 70)
        self.load_label = self.canvas.create_text(WIDTH / 2, HEIGHT / 2, text = 'Loading...', fill = 'white', font = self.font)

        if self.show_after != None:
            self.window.after_cancel(self.show_after)

        self.moves              = {}
        self.keys_pressed       = {'down': False, 'up': False, 'left': False, 'right': False}
        
        self.draw_squares       = [[1, 1]]
        self.solution           = [[1, 1]]
        self.coordinates        = [1, 1]
        self.final_solution     = []

        self.game_started       = True
        self.lost_game          = False
        self.game_over          = False
        self.done_drawing       = False
        self.run_timer          = False

        self.time               = -1
        self.time_tick()

        self.start_draw()
        self.dot_loop()

    def dot_loop(self):
        """
        A loop, called after 350 ms by the after function, to update the loading text
        """
        self.canvas.itemconfig(self.load_label, text = f"Loading{('.' * self.dots)[:-1]}")
        if self.dots == 4:
            self.dots = 1
        else:
            self.dots += 1
        
        self.dot_after = self.window.after(350, self.dot_loop)

    def time_tick(self):
        """
        Function called to update the timer variable and text
        """
        self.time += 1
        self.timer.configure(text = f'Timer: {str(self.time)[:-1]}.{str(self.time)[-1]}')

    def finish_drawing(self):
        """
        Function called when the drawing is done
        Fixes the corners, creates the player and end goal, and shows the maze line
        """
        self.window.after_cancel(self.dot_after)
        self.window.after_cancel(self.generate_after)
        
        self.canvas.delete('all')
        self.canvas.create_line([[a[0] * SPACE_SIZE, a[1] * SPACE_SIZE] for a in self.draw_squares], fill = 'white', width = 15, joinstyle = MITER, capstyle = PROJECTING)

        self.mark_moves()
        
        for square in [end for end in self.draw_squares if len(self.moves[f'{end[0]}, {end[1]}']) == 1]:
            self.canvas.create_rectangle(
                                            square[0] * SPACE_SIZE - 7, 
                                            square[1] * SPACE_SIZE - 7, 
                                            square[0] * SPACE_SIZE + 8, 
                                            square[1] * SPACE_SIZE + 8, 
                                            fill = 'white',
                                            outline = ''
                                        )

        self.canvas.create_rectangle(
                                        SPACE_SIZE * 68.5, 
                                        SPACE_SIZE * 48.5, 
                                        SPACE_SIZE * 68.5 + SPACE_SIZE - 5, 
                                        SPACE_SIZE * 48.5 + SPACE_SIZE - 5, 
                                        fill = 'green', 
                                        outline = ''
                                    )

        self.player = Player(self)
        self.done_drawing = True
        self.check_moves()

    def check_moves(self):
        """
        Loop called every 100 ms to check which keys are being pressed and move the player in that direction
        Necessary to stop debounce time
        """
        if self.run_timer:
            self.time_tick()
        if self.game_over or not self.done_drawing and self.game_started:
            return
        if self.keys_pressed['down']:
            self.player.move('down', self)
        if self.keys_pressed['up']:
            self.player.move('up', self)
        if self.keys_pressed['left']:
            self.player.move('left', self)
        if self.keys_pressed['right']:
            self.player.move('right', self)

        self.window.after(100, self.check_moves)

    def mark_moves(self):
        """
        Marks moves in the moves dictionary
        Works by looping over the drawn squares list and adding the current to the move list of the one just before it, and vice versa
        """
        for index in range(len(self.draw_squares) - 1):
            square = self.draw_squares[index]
            if index + 1 == len(self.draw_squares):
                return
            next_square = self.draw_squares[index + 1]
            self.mark_move(square, next_square)
            if index == 0:
                continue
            next_square = self.draw_squares[index - 1]
            self.mark_move(square, next_square)

    def mark_move(self, square1, square2):
        """
        Function called to mark a move, only ever called by mark_moves()

        Args:
            square1 (list): square to which the object will be added
            square2 (list): square to add to the list of square 1
        """
        string = f'{square1[0]}, {square1[1]}'
        if string not in self.moves:
            self.moves[string] = []
        if square2 not in self.moves[string] and square2 != square1:
            self.moves[string].append(square2)

    def start_draw(self):
        """
        Function to start drawing the maze
        Finds the current possible moves, chooses one and goes there
        If there are no moves possible, backtracks until there are
        """
        done_drawing = True
        possible_visits = self.get_visits(self.coordinates[0], self.coordinates[1])

        if len(possible_visits) == 0:
            still_solution = copy(self.solution)
            still_solution.reverse()
            for solution_square in still_solution:
                if len(self.get_visits(solution_square[0], solution_square[1])) == 0:
                    if solution_square == [1, 1]:
                        break
                    self.solution.remove(solution_square)
                    self.draw_squares.append(solution_square)

                else:
                    done_drawing = False
                    self.coordinates = solution_square
                    self.draw_squares.append(solution_square)
                    break

            if not done_drawing:
                self.generate_after = self.window.after_idle(self.start_draw)
            else:
                self.finish_drawing()

        else:
            next_visit = possible_visits[randint(0, len(possible_visits) - 1)]
            if next_visit == [69, 49]:
                self.final_solution = copy(self.solution)
            possible_visits.remove(next_visit)

            self.solution.append(next_visit)
            self.coordinates = next_visit
            self.draw_squares.append(next_visit)
            self.generate_after = self.window.after_idle(self.start_draw)

    def get_visits(self, row, column):
        """
        Function to get the possible moves from a certain square
        Only returns squares inside the grid and not found in drawn squares

        Args:
            row (int): the row of the square to be tested
            column (int): the column of the square to be tested

        Returns:
            list: list of possible squares to visit from the square provided in the parameters
        """
        return [
                    combo for combo in 
                    [   
                        [row - 1, column], 
                        [row + 1, column], 
                        [row, column - 1], 
                        [row, column + 1]
                    ] 
                    if  combo not in self.draw_squares and
                        combo[0] in range(1, int(WIDTH / SPACE_SIZE)) and
                        combo[1] in range(1, int(HEIGHT / SPACE_SIZE))
                ]

    def check_coordinates(self, x, y, new_x, new_y):
        """
        Checks if the the player can move form one square to another square

        Args:
            x (int): the x position of the current square
            y (int): the y position of the current square
            new_x (int): the x position of the square we want to check the move to
            new_y (int): the y position of the square we want to check the move to

        Returns:
            bool: whether the player can move from [x, y] to [new_x, new_y]
        """
        return [new_x, new_y] in self.moves[f'{x}, {y}']

    def finish_game(self, won):
        """
        Function to finish the game

        Args:
            won (bool): whether the game ended because the player reached the end or if the player showed the solution
        """
        self.run_timer = False
        self.game_over = True
        self.lost_game = not won
        self.show_after = self.window.after(1000, self.show_restart)

    def show_restart(self):
        """
        Function to show the restart menu
        Called 1000 ms after finishing the game
        """
        self.canvas.create_image(0, 0, image = self.end_img, anchor = NW)
        self.font.configure(size = 110)
        if self.lost_game:
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 - 100, text = 'You Lost', fill = 'white', font = self.font)
            self.canvas.update()
        else:
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 - 100, text = 'GG!', fill = 'white', font = self.font)
        self.canvas.create_text(WIDTH / 2, HEIGHT / 2 + 100, text = 'Time: {}.{}'.format(str(self.time)[:-1], str(self.time)[-1]), fill = 'white', font = self.font)

    def press_key(self, direction, pressed = True):
        """
        Function called once a key is pressed or released

        Args:
            direction (string): the direction of key pressed or released : 'left', 'right', 'up', 'down'
            press (bool, optional): whether the key was pressed or released. Defaults to True.
        """
        if not self.game_over and self.game_started:
            self.run_timer = True
        self.keys_pressed[direction] = pressed
    
    def show_solution(self):
        """
        Function called to show the solution
        Only called once the escape key is pressed
        """
        self.canvas.delete('line')
        self.canvas.create_line([[a[0] * SPACE_SIZE, a[1] * SPACE_SIZE] for a in self.final_solution], fill = 'black', width = 25, joinstyle = MITER, capstyle = PROJECTING)
        self.canvas.create_line([[a[0] * SPACE_SIZE, a[1] * SPACE_SIZE] for a in self.final_solution], fill = '#03a9fc', width = 15, joinstyle = MITER, capstyle = PROJECTING)
        self.finish_game(False)

    def click(self):
        """
        Simple function to handle clicks, and start or restart the game
        """
        if not self.game_started or self.game_over:
            self.start()

class Player:
    def __init__(self, game):
        """
        Initializes a player object at [1, 1]

        Args:
            game (MazeGame): the main game object, needed to access the canvas and other members
        """
        self.x, self.y = 1, 1
        self.past_path = [[1, 1], [1, 1]]
        self.double_path = [[1, 1], [1, 1]]
        game.canvas.create_rectangle(   self.x * SPACE_SIZE - SPACE_SIZE / 2, 
                                        self.y * SPACE_SIZE  - SPACE_SIZE / 2, 
                                        self.x * SPACE_SIZE + SPACE_SIZE / 2, 
                                        self.y * SPACE_SIZE + SPACE_SIZE / 2, 
                                        fill = '#c20404', 
                                        tag = 'player')
    
    def move(self, direction, game):
        """
        Moves the player in the specified direction
        Does not assume the player can actually move in that direction
        Updates the line objects

        Args:
            direction (string): The direction the player should move in
            game (MazeGame): the main game object...
        """
        moved = False
        if direction == 'left':
            if game.check_coordinates(self.x, self.y, self.x - 1, self.y):
                moved = True
                self.x -= 1
                game.canvas.move('player', -SPACE_SIZE, 0)
        elif direction == 'right':
            if game.check_coordinates(self.x, self.y, self.x + 1, self.y):
                moved = True
                self.x += 1
                game.canvas.move('player', SPACE_SIZE, 0)
        elif direction == 'up':
            if game.check_coordinates(self.x, self.y, self.x, self.y - 1):
                moved = True
                self.y -= 1
                game.canvas.move('player', 0, -SPACE_SIZE)
        elif direction == 'down':
            if game.check_coordinates(self.x, self.y, self.x, self.y + 1):
                moved = True
                self.y += 1
                game.canvas.move('player', 0, SPACE_SIZE)
                
        if self.x == 69 and self.y == 49:
            game.finish_game(True)

        if moved:
            obj = [self.x, self.y]
            self.double_path.append(obj)
            if obj in self.past_path:
                index = self.past_path.index(obj)
                self.past_path = self.past_path[:index + 1]
            else:
                self.past_path.append(obj)

        game.canvas.delete('line')
        if len(self.past_path) < 2:
            self.past_path = [[1, 1], [1, 1]]

        for square_index in range(len(self.double_path[1:-1])):
            if self.double_path[square_index - 1] == self.double_path[square_index + 1]:
                x = self.double_path[square_index][0] * SPACE_SIZE - 7
                y = self.double_path[square_index][1] * SPACE_SIZE - 7
                game.canvas.create_rectangle(x, y, x + 15, y + 15, fill = '#f7554f', tag = 'line', outline = '')
        
        game.canvas.create_line([[a[0] * SPACE_SIZE, a[1] * SPACE_SIZE] for a in self.double_path], fill = '#f7554f', width = 15, joinstyle = MITER, capstyle = PROJECTING, tag = 'line')
        game.canvas.create_line([[a[0] * SPACE_SIZE, a[1] * SPACE_SIZE] for a in self.past_path], fill = '#69f57e', width = 15, joinstyle = MITER, capstyle = PROJECTING, tag = 'line')
            
        game.canvas.tag_raise('player')

game = MazeGame()