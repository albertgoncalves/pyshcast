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
    ".....................####......#..###############..#....." \
    "..............##.....#..#......#...................#....." \
    ".....#.....#...##....####......#...................#....." \
    "......#....#....##.............#####################....." \
    "......#....#.....##......................................" \
    "........................................................."

FOV_RADIUS = max(WIDTH, HEIGHT)
FOV_RADIUS_FLIP = -FOV_RADIUS
FOV_RADIUS_SQ = FOV_RADIUS * FOV_RADIUS

K = 0.495

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


def do_cast_light(cx, cy, row, start, end, xx, xy, yx, yy):
    if start < end:
        return
    for dy in range(row, FOV_RADIUS_FLIP - 1, -1):
        blocked = False
        for dx in range(dy - 1, 1):
            # NOTE: `l_slope` and `r_slope` store the slopes of the left and
            # right extremities of the square we're considering.
            r_slope = (dx + K) / (dy - K)
            if start < r_slope:
                continue
            l_slope = (dx - K) / (dy + K)
            if l_slope < end:
                break
            else:
                # NOTE: Translate the `(dx, dy)` coordinates into map
                # coordinates.
                x = cx + (dx * xx) + (dy * xy)
                y = cy + (dx * yx) + (dy * yy)
                # NOTE: Our light beam is touching this square.
                if ((dx * dx) + (dy * dy)) < FOV_RADIUS_SQ:
                    if (0 <= x) and (x < WIDTH) and (0 <= y) \
                            and (y < HEIGHT):
                        LIGHT[(WIDTH * y) + x] = True
                if blocked:
                    # NOTE: We're scanning a row of blocked squares.
                    if get_blocked(x, y):
                        new_start = r_slope
                        continue
                    else:
                        blocked = False
                        start = new_start
                else:
                    if get_blocked(x, y) and (FOV_RADIUS_FLIP < dy):
                        # NOTE: This is a blocking square. Start a child scan.
                        blocked = True
                        do_cast_light(
                            cx,
                            cy,
                            dy - 1,
                            start,
                            l_slope,
                            xx,
                            xy,
                            yx,
                            yy,
                        )
                        new_start = r_slope
        # NOTE: Row is scanned. Do next row unless last square was blocked.
        if blocked:
            break


def do_fov(cx, cy):
    do_cast_light(cx, cy, -1, 1.0, 0.0, 1, 0, 0, 1)
    do_cast_light(cx, cy, -1, 1.0, 0.0, 1, 0, 0, -1)
    do_cast_light(cx, cy, -1, 1.0, 0.0, -1, 0, 0, 1)
    do_cast_light(cx, cy, -1, 1.0, 0.0, -1, 0, 0, -1)
    do_cast_light(cx, cy, -1, 1.0, 0.0, 0, 1, 1, 0)
    do_cast_light(cx, cy, -1, 1.0, 0.0, 0, 1, -1, 0)
    do_cast_light(cx, cy, -1, 1.0, 0.0, 0, -1, 1, 0)
    do_cast_light(cx, cy, -1, 1.0, 0.0, 0, -1, -1, 0)


def do_display(screen, cx, cy):
    for y in range(HEIGHT):
        y_index = WIDTH * y
        for x in range(WIDTH):
            if (x == cx) and (y == cy):
                character = PLAYER
            elif LIGHT[y_index + x]:
                character = MAP[y_index + x]
            else:
                character = UNSEEN
            screen.addstr(y, x, character)
            LIGHT[y_index + x] = False
    screen.refresh()


def main():
    try:
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.keypad(1)
        (cx, cy) = (28, 7)
        while True:
            do_fov(cx, cy)
            do_display(screen, cx, cy)
            key = screen.getch()
            if key == LOWER_Q:
                break
            elif key == UP:
                move_y = cy - 1
                if (0 <= move_y) and (MAP[(WIDTH * move_y) + cx] == FLOOR):
                    cy = move_y
            elif key == DOWN:
                move_y = cy + 1
                if (move_y < HEIGHT) and (MAP[(WIDTH * move_y) + cx] == FLOOR):
                    cy = move_y
            elif key == LEFT:
                move_x = cx - 1
                if (0 <= move_x) and (MAP[(WIDTH * cy) + move_x] == FLOOR):
                    cx = move_x
            elif key == RIGHT:
                move_x = cx + 1
                if (move_x < WIDTH) and (MAP[(WIDTH * cy) + move_x] == FLOOR):
                    cx = move_x
    finally:
        screen.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()


if __name__ == "__main__":
    main()
