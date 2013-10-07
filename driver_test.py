"""
This file illustrates an example usage of the MoveWindow, ScrollWindow,
and Subrect classes.

-Written by Sean McKiernan
"""

import os
import sys
import pygame as pg

from guipack import scrollwindow, movewindow
from guipack.subrect import Subrect


class Control(object):
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = 60
        self.win = self.make_win()

    def make_win(self):
        """Setup a movable window that contains a scroll window."""
        window_args = {"text"       : "Fruits and Vegetables",
                       "font"       : FONT,
                       "text_color" : (255,255,255)}
        win = movewindow.MoveWindow(Subrect((50,50,200,300)),**window_args)
##        win = movewindow.MoveWindow(Subrect((50,50,200,300)),background=FRAC,
##                                    **window_args)
        bar_subrect = Subrect((25,45,150,230),win.subrect)
        bar = scrollwindow.ScrollWindow(bar_subrect, gen_content(), FONT)
        win.content.append(bar)
        return win

    def event_loop(self):
        for event in pg.event.get():
            keys = pg.key.get_pressed()
            if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                self.done = True
            get = self.win.get_events(event)
            if get:
                print(get) ##Just printing for example purposes
                pg.event.clear()
                return get

    def main_loop(self):
        while not self.done:
            self.event_loop()
            self.screen.fill((25, 155, 255))
            self.win.update(self.screen)
            pg.display.update()
            self.clock.tick(self.fps)


def gen_content():
    """Just getting sample content from a file."""
    with open("test_content.txt") as myfile:
        return [line.strip() for line in myfile.readlines()]


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption("GUI Example")
    pg.display.set_mode((700, 600))
    FONT = pg.font.SysFont("timesnewroman", 15)
    FRAC = pg.image.load("frac.jpg").convert()
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
