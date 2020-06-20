#!/usr/bin/python3

import curses
import random
import locale
import select
import sys


xsize = 40
ysize = 23
vvram = [[0 for i in range(ysize)] for j in range(xsize)]
mask = [["＃" for i in range(ysize)] for j in range(xsize)]
itod = "　１２３４５６７８９"
ac = "＃＠？"


def getkey():
    c = stdscr.getkey()
    if c == 'KEY_UP':
        c = '8'
    elif c == 'KEY_DOWN':
        c = '2'
    elif c == 'KEY_RIGHT':
        c = '6'
    elif c == 'KEY_LEFT':
        c = '4'
    return c


def putchar(x, y, a):
    stdscr.addstr(y, x*2, a, curses.A_REVERSE)


def putcharr(x, y, a):
    stdscr.addstr(y, x*2, a)


def putmines(n):
    for i in range(n):
        while(True):
            (x, y) = (random.randint(0, xsize-1), random.randint(0, ysize-1))
            if (vvram[x][y] == 0):
                vvram[x][y] = '*'
                break
#


def calccell(x, y):
    if (vvram[x][y] == 0):
        cnt = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if x+dx >= 0 and y+dy >= 0 and x+dx < xsize and y+dy < ysize:
                    cnt += 1 if vvram[x+dx][y+dy] == '*' else 0
        vvram[x][y] = cnt
        return(cnt)


def reveal(x, y):
    if mask[x][y] != ' ':
        mask[x][y] = ' '
        if vvram[x][y] == 0:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if x+dx >= 0 and y+dy >= 0 and x+dx < xsize and y+dy < ysize:
                        reveal(x+dx, y+dy)


def cursor(x, y):
    putcharr(x, y, retchar(x, y))


def printmines():
    for x in range(xsize):
        for y in range(ysize):
            c = vvram[x][y]
            if c == '*':
                putchar(x, y, "＊")
            elif (c >= 0 and c <= 9):
                putchar(x, y, itod[c])


def retchar(x, y):
    m = mask[x][y]
    if m in ac:
        return(m)
    else:
        c = vvram[x][y]
        if c >= 0 and c <= 9:
            return(itod[c])


def drawchar(x, y):
    putchar(x, y, retchar(x, y))


def drawscreen():
    for x in range(xsize):
        for y in range(ysize):
            drawchar(x, y)


def calcfield():
    for x in range(xsize):
        for y in range(ysize):
            calccell(x, y)


def endcheck():
    c = 0
    for x in range(xsize):
        for y in range(ysize):
            c += 1 if mask[x][y] in ac else 0
    return(c == mines)


def mainloop():
    (x, y) = (xsize//2, ysize//2)
    while True:
        drawscreen()
        if endcheck():
            putchar(0, 23, "You win. hit key")
            getkey()
            return(0)
        cursor(x, y)
        stdscr.refresh()
        c = getkey()
        if c == '4':
            x = x-(1 if x != 0 else 0)
        elif c == '6':
            x = x+(1 if x != xsize-1 else 0)
        elif c == '8':
            y = y-(1 if y != 0 else 0)
        elif c == '2':
            y = y+(1 if y != ysize-1 else 0)
        elif (c == 'z' or c=='m') and mask[x][y] != ' ':
            mask[x][y] = ac[(ac.index(mask[x][y])+1) % 3]
        elif c == ' ':
            if vvram[x][y] == '*':
                printmines()
                putchar(x, y, "Ｘ")
                putchar(0, 23, "You lose. hit key")
                getkey()
                return(-1)
            reveal(x, y)
        elif c == 'q':
            return(1)


def game():
    putmines(mines)
    calcfield()
    mainloop()
    return

def main():
    try:
        game()
    except (Exception, KeyboardInterrupt) as e:
        curses.endwin()
        raise e
    else:
        curses.endwin()

argvs = sys.argv
argc = len(argvs)

if argc == 2:
    mines = int(argvs[1])
    if mines > 300:
        print("too many mines")
        exit(1)
else:
    mines = 60

locale.setlocale(locale.LC_ALL, '')
stdscr = curses.initscr()
stdscr.keypad(True)
curses.curs_set(0)
main()
