#!/usr/bin/env python3

import curses
import random
import locale
import sys

class Config:
    XSIZE = 40
    BOARD_HEIGHT = 22
    YSIZE = BOARD_HEIGHT + 1
    MARKS = ['＃', '🚩', '？']
    DIGITS = "　１２３４５６７８９"
    MAX_MINES = 300

    DIRECTIONS = {
        'LEFT': (-1, 0), 'RIGHT': (1, 0),
        'UP': (0, -1), 'DOWN': (0, 1)
    }

    KEY_BINDINGS = {
        '4': 'LEFT', 'h': 'LEFT', 'KEY_LEFT': 'LEFT',
        '6': 'RIGHT', 'l': 'RIGHT', 'KEY_RIGHT': 'RIGHT',
        '8': 'UP', 'k': 'UP', 'KEY_UP': 'UP',
        '2': 'DOWN', 'j': 'DOWN', 'KEY_DOWN': 'DOWN',
    }

class Cell:
    def __init__(self):
        self.mine = False
        self.revealed = False
        self.mark = 0
        self.adjacent = 0

    def display(self, game_over=False):
        if not self.revealed:
            if game_over and not self.mine and self.mark == 1:
                return "Ｘ"
            return Config.MARKS[self.mark]
        if self.mine:
            return "😺"
        return Config.DIGITS[self.adjacent] if self.adjacent < len(Config.DIGITS) else "？"

class Board:
    def __init__(self, mines):
        self.width = Config.XSIZE
        self.height = Config.BOARD_HEIGHT
        self.mines = mines
        self.grid = [[Cell() for _ in range(self.height)] for _ in range(self.width)]
        self.place_mines()
        self.calculate_adjacents()

    def place_mines(self):
        placed = 0
        while placed < self.mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            cell = self.grid[x][y]
            if not cell.mine:
                cell.mine = True
                placed += 1

    def calculate_adjacents(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y].mine:
                    continue
                count = sum(
                    self.grid[nx][ny].mine
                    for dx in (-1, 0, 1)
                    for dy in (-1, 0, 1)
                    if (dx or dy) and 0 <= (nx := x + dx) < self.width and 0 <= (ny := y + dy) < self.height
                )
                self.grid[x][y].adjacent = count

    def reveal(self, x, y):
        cell = self.grid[x][y]
        if cell.revealed or Config.MARKS[cell.mark] != '＃':
            return
        cell.revealed = True
        if cell.adjacent == 0 and not cell.mine:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.reveal(nx, ny)

    def toggle_mark(self, x, y):
        cell = self.grid[x][y]
        if not cell.revealed:
            cell.mark = (cell.mark + 1) % len(Config.MARKS)

    def all_clear(self):
        return all(cell.revealed or cell.mine for row in self.grid for cell in row)

class GameState:
    def __init__(self, board):
        self.board = board
        self.cursor_x = board.width // 2
        self.cursor_y = board.height // 2
        self.game_over = False

class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def draw(self, state: GameState):
        board = state.board
        for x in range(board.width):
            for y in range(board.height):
                self.draw_cell(x, y, state)

    def draw_cell(self, x, y, state: GameState):
        cell = state.board.grid[x][y]
        ch = cell.display(game_over=state.game_over)
        attr = curses.A_REVERSE if (x, y) == (state.cursor_x, state.cursor_y) else 0
        self.stdscr.addstr(y, x * 2, ch, attr)

    def show_message(self, message):
        self.stdscr.addstr(Config.YSIZE - 1, 0, message.ljust(Config.XSIZE * 2))

class Game:
    def __init__(self, stdscr, mines):
        self.stdscr = stdscr
        self.board = Board(mines)
        self.state = GameState(self.board)
        self.renderer = Renderer(stdscr)

    def run(self):
        while True:
            self.renderer.draw(self.state)
            self.stdscr.refresh()

            # ✅ 修正済：ゲームオーバー時は勝利処理をスキップ
            if not self.state.game_over and self.board.all_clear():
                self.handle_win()
                return 0

            key = self.stdscr.getkey()
            if not self.handle_key(key):
                return 1

    def handle_key(self, key):
        action = Config.KEY_BINDINGS.get(key)
        if action:
            dx, dy = Config.DIRECTIONS[action]
            self.state.cursor_x = max(0, min(self.board.width - 1, self.state.cursor_x + dx))
            self.state.cursor_y = max(0, min(self.board.height - 1, self.state.cursor_y + dy))
        elif key in ('z', 'm'):
            self.board.toggle_mark(self.state.cursor_x, self.state.cursor_y)
        elif key == ' ':
            self.handle_reveal()
        elif key == 'q':
            return False
        return True

    def handle_reveal(self):
        x, y = self.state.cursor_x, self.state.cursor_y
        cell = self.board.grid[x][y]
        if cell.mine:
            self.state.game_over = True
            self.reveal_all(show_mines=True)
            self.renderer.draw(self.state)
            self.renderer.show_message("You lose. hit key")
            self.stdscr.refresh()
            self.stdscr.getkey()
        else:
            self.board.reveal(x, y)

    def reveal_all(self, show_mines=False):
        for x in range(self.board.width):
            for y in range(self.board.height):
                cell = self.board.grid[x][y]
                if show_mines:
                    if cell.mine:
                        if cell.mark != 1:
                            cell.revealed = True
                    else:
                        cell.revealed = True
                else:
                    cell.revealed = True

    def handle_win(self):
        for x in range(self.board.width):
            for y in range(self.board.height):
                cell = self.board.grid[x][y]
                if cell.mine:
                    cell.mark = 1
                    cell.revealed = False
                else:
                    cell.revealed = True
        self.renderer.draw(self.state)
        self.renderer.show_message("You win. hit key")
        self.stdscr.refresh()
        self.stdscr.getkey()

def get_mine_count():
    try:
        if len(sys.argv) == 2:
            count = int(sys.argv[1])
            if count > Config.MAX_MINES:
                print("too many nyankos")
                exit(1)
            return count
    except ValueError:
        print("not a number")
        exit(1)
    return 56

def run(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    locale.setlocale(locale.LC_ALL, '')
    mines = get_mine_count()
    game = Game(stdscr, mines)
    game.run()

def main():
    curses.wrapper(run)

if __name__ == "__main__":
    main()

