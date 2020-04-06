#!/usr/bin/env python3

import curses

WIDTH = 57
HEIGHT = 16
LIGHT = [False] * (WIDTH * HEIGHT)
MAP = \
    "...........#............................................." \
    "...........#........#...................................." \
    ".....................#..................................." \
    "....####..............#.................................." \
    ".......#.......................#####################....." \
    ".......#...........................................#....." \
    ".......#...........##..............................#....." \
    "####........#......##..........##################..#....." \
    "...#...........................#................#..#....." \
    "...#............#..............#................#..#....." \
    "...............................#..###############..#....." \
    ".....................####......#...................#....." \
    ".....#.....#.........#..#......#...................#....." \
    "......#....#.........####......#####################....." \
    "......#....#............................................." \
    "........................................................."

FOV_RADIUS = max(WIDTH, HEIGHT)
FOV_RADIUS_SQ = FOV_RADIUS * FOV_RADIUS

PLAYER = "@"
UNSEEN = " "
WALL = "#"
FLOOR = "."

LOWER_Q = 113
UP = 259
DOWN = 258
LEFT = 260
RIGHT = 261


def get_blocked(x, y):
    return (
       (x < 0)
       or (y < 0)
       or (WIDTH <= x)
       or (HEIGHT <= y)
       or (MAP[(WIDTH * y) + x] == WALL)
    )


def do_cast_light(cx, cy, row, start, end, id_, xx, xy, yx, yy):
    if start < end:
        return
    for j in range(row, FOV_RADIUS + 1):
        (dx, dy) = (-j - 1, -j)
        blocked = False
        while dx <= 0:
            dx += 1
            # Translate the `dx, dy` coordinates into map coordinates
            (X, Y) = (
                cx + (dx * xx) + (dy * xy),
                cy + (dx * yx) + (dy * yy)
            )
            # `l_slope` and `r_slope` store the slopes of the left and
            # right extremities of the square we're considering
            (l_slope, r_slope) = (
                (dx - 0.5) / (dy + 0.5),
                (dx + 0.5) / (dy - 0.5)
            )
            if start < r_slope:
                continue
            elif l_slope < end:
                break
            else:
                # Our light beam is touching this square
                if ((dx * dx) + (dy * dy)) < FOV_RADIUS_SQ:
                    if (0 <= X) and (X < WIDTH) and (0 <= Y) \
                            and (Y < HEIGHT):
                        LIGHT[(WIDTH * Y) + X] = True
                if blocked:
                    # We're scanning a row of blocked squares
                    if get_blocked(X, Y):
                        new_start = r_slope
                        continue
                    else:
                        blocked = False
                        start = new_start
                else:
                    if get_blocked(X, Y) and (j < FOV_RADIUS):
                        # This is a blocking square, start a child scan
                        blocked = True
                        do_cast_light(
                            cx,
                            cy,
                            j + 1,
                            start,
                            l_slope,
                            id_ + 1,
                            xx,
                            xy,
                            yx,
                            yy,
                        )
                        new_start = r_slope
        # Row is scanned, do next row unless last square was blocked
        if blocked:
            break


def do_fov(x, y):
    do_cast_light(x, y, 1, 1.0, 0.0, 0, 1, 0, 0, 1)
    do_cast_light(x, y, 1, 1.0, 0.0, 0, 1, 0, 0, -1)
    do_cast_light(x, y, 1, 1.0, 0.0, 0, -1, 0, 0, 1)
    do_cast_light(x, y, 1, 1.0, 0.0, 0, -1, 0, 0, -1)
    do_cast_light(x, y, 1, 1.0, 0.0, 0, 0, 1, 1, 0)
    do_cast_light(x, y, 1, 1.0, 0.0, 0, 0, 1, -1, 0)
    do_cast_light(x, y, 1, 1.0, 0.0, 0, 0, -1, 1, 0)
    do_cast_light(x, y, 1, 1.0, 0.0, 0, 0, -1, -1, 0)


def do_display(screen, X, Y):
    for y in range(HEIGHT):
        y_width = WIDTH * y
        for x in range(WIDTH):
            if (x == X) and (y == Y):
                character = PLAYER
            elif LIGHT[y_width + x]:
                character = MAP[y_width + x]
            else:
                character = UNSEEN
            screen.addstr(y, x, character)
            LIGHT[y_width + x] = False
    screen.refresh()


def main():
    try:
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.keypad(1)
        (x, y) = (28, 7)
        while True:
            do_fov(x, y)
            do_display(screen, x, y)
            key = screen.getch()
            if key == LOWER_Q:
                break
            elif key == UP:
                move_y = y - 1
                if (0 <= move_y) and (MAP[(WIDTH * move_y) + x] == FLOOR):
                    y = move_y
            elif key == DOWN:
                move_y = y + 1
                if (move_y < HEIGHT) and (MAP[(WIDTH * move_y) + x] == FLOOR):
                    y = move_y
            elif key == LEFT:
                move_x = x - 1
                if (0 <= move_x) and (MAP[(WIDTH * y) + move_x] == FLOOR):
                    x = move_x
            elif key == RIGHT:
                move_x = x + 1
                if (move_x < WIDTH) and (MAP[(WIDTH * y) + move_x] == FLOOR):
                    x = move_x
    finally:
        screen.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()


if __name__ == "__main__":
    main()
