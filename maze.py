from tkinter import *
from random import randint

HEIGHT = 500
WIDTH = 800
SPACE_SIZE = 20

class MazeGame:
    def __init__(self):
        #Basic Setup

        self.window = Tk()
        self.window.title('Maze Game')
        self.window.resizable(False, False)

        self.canvas = Canvas(self.window, height = HEIGHT, width = 800, relief = RAISED, bg = 'black')
        self.canvas.pack()

        self.started = False

        self.bind()

        self.window.mainloop()

    def bind(self):
        self.window.bind('<Button-1>', lambda e: self.click())

    def click(self):
        if not self.started or self.dead:
            self.start()

    def start(self):
        self.square_list    = []
        self.trip           = []
        self.draw_list      = []
        self.move_combos    = {}
        self.coordinates    = [1, 1]
        self.started = True
        self.dead = False
        self.state = 'drawing'

        self.draw()

    def done_drawing(self):
        self.state = 'playing'
        self.canvas.delete('all')
        self.canvas.create_line(self.draw_list, fill = 'white', width = 15, joinstyle = BEVEL, capstyle = PROJECTING)
        self.window.after_cancel(self.generate_after)
        print(self.move_combos['1, 5'])

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


game = MazeGame()