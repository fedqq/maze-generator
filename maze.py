from tkinter import *
from random import randint
from tkextrafont import Font
from copy import copy

HEIGHT = 1000
WIDTH = 1400
SPACE_SIZE = 20

class MazeGame:
    def __init__(self):
        #Basic Setup

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
        self.drawing_finished   = False

        self.show_after = None

        self.canvas = Canvas(self.window, height = HEIGHT, width = WIDTH, relief = RAISED, bg = 'black')
        self.canvas.pack()

        self.timer = Label(self.window, text='', font = ("Arial", 30), bg = "black", fg = "white")
        self.timer.pack()

        self.start_menu_img = PhotoImage(file = 'resources\menu.png')
        self.canvas.create_image(0, 0, image = self.start_menu_img, anchor = NW)

        self.end_img = PhotoImage(file = 'resources\end_menu.png')

        self.bind()

        self.window.mainloop()

    def bind(self):
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

    def start(self):
        self.canvas.delete('all')
        self.font.configure(size = 70)
        self.load_label = self.canvas.create_text(WIDTH / 2, HEIGHT / 2, text = 'Loading...', fill = 'white', font = self.font)

        if not self.show_after == None:
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
        self.drawing_finished   = False
        self.run_timer          = False

        self.time               = -1
        self.time_tick()

        self.start_draw()
        self.dot_loop()

    def dot_loop(self):
        self.canvas.itemconfig(self.load_label, text = 'Loading{}'.format(('.' * self.dots)[:-1]))
        if self.dots == 4:
            self.dots = 1
        else:
            self.dots += 1
        
        self.dot_after = self.window.after(350, self.dot_loop)

    def time_tick(self):
        self.time += 1
        self.timer.configure(text = 'Timer: {}.{}'.format(str(self.time)[:-1], str(self.time)[-1]))

    def done_drawing(self):
        self.window.after_cancel(self.dot_after)
        self.window.after_cancel(self.generate_after)
        
        self.canvas.delete('all')
        self.canvas.create_line([[a[0] * SPACE_SIZE, a[1] * SPACE_SIZE] for a in self.draw_squares], fill = 'white', width = 15, joinstyle = MITER, capstyle = PROJECTING)

        self.mark_moves()
        self.canvas.create_rectangle(
                                        SPACE_SIZE * 68.5, 
                                        SPACE_SIZE * 48.5, 
                                        SPACE_SIZE * 68.5 + SPACE_SIZE - 5, 
                                        SPACE_SIZE * 48.5 + SPACE_SIZE - 5, 
                                        fill = 'green', 
                                        outline = ''
                                    )
        
        for square in [end for end in self.draw_squares if len(self.moves['{}, {}'.format(end[0], end[1])]) == 1]:
            self.canvas.create_rectangle(
                                            square[0] * SPACE_SIZE - 7, 
                                            square[1] * SPACE_SIZE - 7, 
                                            square[0] * SPACE_SIZE + 15 - 7, 
                                            square[1] * SPACE_SIZE + 15 - 7, 
                                            fill = 'white',
                                            outline = ''
                                        )

        self.player = Player(self)
        self.drawing_finished = True
        self.check_moves()

    def check_moves(self):
        if self.run_timer:
            self.time_tick()
        if self.game_over or not self.drawing_finished and self.game_started:
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
        string = '{}, {}'.format(square1[0], square1[1])
        if string not in self.moves:
            self.moves[string] = []
        if square2 not in self.moves[string] and square2 != square1:
            self.moves[string].append(square2)

    def start_draw(self):
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
                self.done_drawing()

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
        return [combo for combo in [[row - 1, column], [row + 1, column], [row, column - 1], [row, column + 1]] 
                    if  combo not in self.draw_squares 
                        and combo[0] in range(1, int(WIDTH / SPACE_SIZE)) 
                        and combo[1] in range(1, int(HEIGHT / SPACE_SIZE))
                ]

    def add_move(self, baseX, baseY, newX, newY):
        string = '{}, {}'.format(baseX, baseY)
        if string not in self.move_combos:
            self.move_combos[string] = []
        self.move_combos[string].append([newX, newY])

        string = '{}, {}'.format(newX, newY)
        if string not in self.move_combos:
            self.move_combos[string] = []
        if not [baseX, baseY] in self.move_combos[string]:
            self.move_combos[string].append([baseX, baseY])

    def check_coordinates(self, x, y, newX, newY):
        return [newX, newY] in self.moves['{}, {}'.format(x, y)]

    def end(self, won):
        self.run_timer = False
        self.game_over = True
        self.lost_game = not won
        self.show_after = self.window.after(1000, self.show_restart)

    def show_restart(self):
        self.canvas.create_image(0, 0, image = self.end_img, anchor = NW)
        self.font.configure(size = 110)
        if self.lost_game:
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 - 100, text = 'You Lost', fill = 'white', font = self.font)
            self.canvas.update()
        else:
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 - 100, text = 'GG!', fill = 'white', font = self.font)
        self.canvas.create_text(WIDTH / 2, HEIGHT / 2 + 100, text = 'Time: {}.{}'.format(str(self.time)[:-1], str(self.time)[-1]), fill = 'white', font = self.font)

    #Functions called when keys or mouse button are pressed
    def press_key(self, direction, press = True):
        if not self.game_over and self.game_started:
            self.run_timer = True
        self.keys_pressed[direction] = press
    
    def show_solution(self):
        self.canvas.create_line([[a[0] * SPACE_SIZE, a[1] * SPACE_SIZE] for a in self.final_solution], fill = 'black', width = 25, joinstyle = MITER, capstyle = PROJECTING)
        self.canvas.create_line([[a[0] * SPACE_SIZE, a[1] * SPACE_SIZE] for a in self.final_solution], fill = '#03a9fc', width = 15, joinstyle = MITER, capstyle = PROJECTING)
        self.end(False)

    def click(self):
        if not self.game_started or self.game_over:
            self.start()

class Player:
    def __init__(self, game):
        self.x, self.y = 1, 1
        game.canvas.create_rectangle(   self.x * SPACE_SIZE - SPACE_SIZE / 2, 
                                        self.y * SPACE_SIZE  - SPACE_SIZE / 2, 
                                        self.x * SPACE_SIZE + SPACE_SIZE / 2, 
                                        self.y * SPACE_SIZE + SPACE_SIZE / 2, 
                                        fill = '#c20404', 
                                        tag = 'player')
    
    def move(self, direction, game):
        if direction == 'left':
            if game.check_coordinates(self.x, self.y, self.x - 1, self.y):
                self.x -= 1
                game.canvas.move('player', -SPACE_SIZE, 0)
        elif direction == 'right':
            if game.check_coordinates(self.x, self.y, self.x + 1, self.y):
                self.x += 1
                game.canvas.move('player', SPACE_SIZE, 0)
        elif direction == 'up':
            if game.check_coordinates(self.x, self.y, self.x, self.y - 1):
                self.y -= 1
                game.canvas.move('player', 0, -SPACE_SIZE)
        elif direction == 'down':
            if game.check_coordinates(self.x, self.y, self.x, self.y + 1):
                self.y += 1
                game.canvas.move('player', 0, SPACE_SIZE)
                
        if self.x == 69 and self.y == 49:
            game.end(True)

game = MazeGame()