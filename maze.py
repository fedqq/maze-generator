from tkinter import *
from random import randint

HEIGHT = 1000
WIDTH = 1400
SPACE_SIZE = 20

class MazeGame:
    def __init__(self):
        #Basic Setup

        self.window = Tk()
        self.window.title('Maze Game')
        self.window.resizable(False, False)
        self.window.configure(bg = 'black')

        self.time = 0

        self.canvas = Canvas(self.window, height = HEIGHT, width = WIDTH, relief = RAISED, bg = 'black')
        self.canvas.pack()

        self.timer = Label(self.window, text='', font = ("Arial", 30), bg = "black", fg = "white")
        self.timer.pack()

        self.restart_image = PhotoImage('resources\menu.png')

        self.started = False

        self.bind()

        self.window.mainloop()

    def bind(self):
        self.window.bind('<Button-1>',          lambda e: self.click())
        self.window.bind('<Left>',              lambda e: self.press('left'))
        self.window.bind('<Right>',             lambda e: self.press('right'))
        self.window.bind('<Up>',                lambda e: self.press('up'))
        self.window.bind('<Down>',              lambda e: self.press('down'))
        self.window.bind('<KeyRelease-Left>',   lambda e: self.press('left', False))
        self.window.bind('<KeyRelease-Right>',  lambda e: self.press('right', False))
        self.window.bind('<KeyRelease-Up>',     lambda e: self.press('up', False))
        self.window.bind('<KeyRelease-Down>',   lambda e: self.press('down', False))
        self.window.bind('<Escape>',            lambda e: self.start_solve())

    def press(self, direction, press = True):
        self.start_time = True
        self.keys_pressed[direction] = press

    def click(self):
        if not self.started or self.dead:
            self.start()

    def start_solve(self, first = True):
        self.canvas.delete('player')
        if first:
            self.solve_squares = self.square_list

        self.state = 'solving'
        done = True
        print('start_solve')
        for square in self.solve_squares:
            if square == [1, 1] or square in self.move_combos['1, 1'] or square in self.move_combos['69, 49'] or square == [69, 49]:
                continue
            moves = self.move_combos['{}, {}'.format(square[0], square[1])]
            moves = [move for move in moves if move in self.solve_squares]
            if len(moves) == 1:
                done = False
                self.solve_squares.remove(square)
                self.canvas.create_rectangle(square[0] * SPACE_SIZE - 12, square[1] * SPACE_SIZE - 12, square[0] * SPACE_SIZE + SPACE_SIZE/2 + 2, square[1] * SPACE_SIZE + SPACE_SIZE/2 + 2, fill = 'black')
                self.canvas.update()

        if done:
            print('done')
            self.started = False
        else:
            self.window.after_idle(self.start_solve, False)

    def fix_corners(self):
        for square in self.square_list:
            if len(self.move_combos['{}, {}'.format(square[0], square[1])]) == 1:
                self.canvas.create_rectangle(square[0] * SPACE_SIZE - 7, square[1] * SPACE_SIZE - 7, square[0] * SPACE_SIZE + SPACE_SIZE/2 - 2, square[1] * SPACE_SIZE + SPACE_SIZE/2 - 2, fill = 'white', outline = '')
                self.canvas.update()

    def start(self):
        self.square_list    = []
        self.trip           = []
        self.killed_squares = []
        self.draw_list      = []
        self.coordinates    = [1, 1]
        self.move_combos    = {}
        self.keys_pressed   = {'down': False, 'up': False, 'left': False, 'right': False}

        self.started        = True
        self.start_time     = False
        self.dead           = False
        self.time           = 0
        self.state          = 'drawing'

        self.draw()

    def done_drawing(self):
        self.state = 'playing'
        self.canvas.delete('all')
        self.canvas.create_line(self.draw_list, fill = 'white', width = 15, joinstyle = MITER, capstyle = PROJECTING)
        self.fix_corners()
        self.canvas.create_rectangle(SPACE_SIZE * 68.5, SPACE_SIZE * 48.5, SPACE_SIZE * 68.5 + SPACE_SIZE, SPACE_SIZE * 48.5 + SPACE_SIZE, fill = 'green', outline = '')
        self.window.after_cancel(self.generate_after)
        self.player = Player(self)
        self.check_moves()

    def check_moves(self):
        if self.start_time:
            self.time += 1
            round(self.time)
            self.timer.configure(text = 'Timer: {}'.format('{}.{}'.format(str(self.time)[:-1], str(self.time)[-1])))
        if self.state != 'playing':
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

    def backtrack(self):
        found = False
        index = -1
        while not found:
            if index * -1 not in range(0, len(self.trip) - 1):
                self.done_drawing()
                return
            self.coordinates = self.trip[index]
            if len(self.get_visits(self.coordinates[0], self.coordinates[1])) > 0:
                self.found = True
                self.trip = self.trip[0: index + 1]
                break
            else:
                self.add_move(self.trip[index][0], self.trip[index][1], self.trip[index - 1][0], self.trip[index - 1][1])
                self.draw_list.append([self.trip[index][0] * SPACE_SIZE, self.trip[index][1] * SPACE_SIZE])
                index -= 1

    def draw(self, backtracking = False):
        self.canvas.delete("all")
        if not backtracking:
            self.trip.append(self.coordinates)
            self.square_list.append(self.coordinates)

        self.draw_list.append([self.coordinates[0] * SPACE_SIZE, self.coordinates[1] * SPACE_SIZE])

        visits = self.get_visits(self.coordinates[0], self.coordinates[1])
        if len(visits) == 0:
            self.backtrack()
            if self.state == 'drawing':
                self.generate_after = self.window.after(1, self.draw, True)
            return

        else:
            next_visit = visits[randint(0, len(visits) - 1)]
            self.add_move(self.coordinates[0], self.coordinates[1], next_visit[0], next_visit[1])

        self.coordinates = [next_visit[0], next_visit[1]]
        if self.state == 'drawing':
            self.generate_after = self.window.after(1, self.draw)

    def get_visits(self, row, column):

        combos = [[row - 1, column], [row + 1, column], [row, column - 1], [row, column + 1]]
        return [combo for combo in combos if combo not in self.square_list and combo[0] in range(1, int(WIDTH / SPACE_SIZE)) and combo[1] in range(1, int(HEIGHT / SPACE_SIZE))]

    def add_move(self, baseX, baseY, newX, newY):
        if '{}, {}'.format(baseX, baseY) not in self.move_combos:
            self.move_combos['{}, {}'.format(baseX, baseY)] = []

        self.move_combos['{}, {}'.format(baseX, baseY)].append([newX, newY])

    def check_coordinates(self, x, y, newX, newY):
        return [newX, newY] in self.move_combos['{}, {}'.format(x, y)]

    def end(self, won):
        self.canvas.create_image(0, 0, image = self.restart_image)
        if won:
            self.canvas.create_text(0, 0, text = 'Score', font = ('Helvetica', 16))

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
                if self.x == 79 and self.y == 49:
                    game.win()
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



game = MazeGame()