"""
This class creates a window with a handle by which it can be dragged around.
"""

import pygame as pg

from . import setup
from .subrect import Subrect


class MoveWindow(object):
    def __init__(self,subrect,**kwargs):
        if setup.GFX == None:
            setup.GFX = setup.load_default_images(setup.DEFAULT_RESOURCES)
        self.subrect = subrect
        self.content = []
        self.drag = False
        self.process_kwargs(kwargs)
        self.prep_images()
        self.make_image()

    def process_kwargs(self,kwargs):
        """All of the following can be used as keyword arguments. Any or all of
        them can be passed to the init by keyword, or a dict of them can be
        passedvia the **dict keyword unpacking syntax."""
        self.kwargs = {"background"  : None,
                        "bg_color"   : (50,50,200),
                        "handle_img" : setup.GFX["handle"],
                        "text"       : None,
                        "font"       : None,
                        "text_color" : (0,0,0),
                        "clamp"      : True} #clamp subrect within the parent
        for kwarg in kwargs:
            if kwarg in self.kwargs:
                self.kwargs[kwarg] = kwargs[kwarg]
            else:
                raise AttributeError("Invalid keyword: {}".format(kwarg))

    def prep_images(self):
        """Prepares the background and handle images."""
        if not self.kwargs["background"]:
            self.kwargs["background"] = pg.Surface(self.subrect.size)
            self.kwargs["background"].convert_alpha()
            self.kwargs["background"].fill(self.kwargs["bg_color"])
            resize = setup.GFX["alph_grad"].copy()
            resize = pg.transform.smoothscale(resize,self.subrect.size)
            self.kwargs["background"].blit(resize,(0,0))
        self.make_handle()

    def make_handle(self):
        """Creates the correct sized handle image from an image.  Not very
        general and would probably need to be edited for other specific handle
        images."""
        dimen = self.subrect.width,self.kwargs["handle_img"].get_height()
        self.handle = pg.Surface(dimen).convert_alpha()
        self.handle.fill((0,0,0,0))
        start_rect = pg.Rect(0,0,6,dimen[1])
        end_rect = pg.Rect(self.kwargs["handle_img"].get_width()-6,0,6,dimen[1])
        self.handle.blit(self.kwargs["handle_img"],start_rect,start_rect)
        self.handle.blit(self.kwargs["handle_img"],(dimen[0]-6,0),end_rect)
        stretch_rect = (6,0,self.kwargs["handle_img"].get_width()-12,dimen[1])
        stretch_piece = self.kwargs["handle_img"].subsurface(stretch_rect)
        stretch = pg.transform.smoothscale(stretch_piece,(dimen[0]-12,dimen[1]))
        self.handle.blit(stretch,(6,0))
        self.render_text()
        self.handle_rect = Subrect(self.handle.get_rect(),self.subrect)

    def render_text(self):
        """Render and blit required text labels."""
        if self.kwargs["text"]:
            temp = self.kwargs["font"].render(self.kwargs["text"], 1,
                                              self.kwargs["text_color"])
            text_rect = temp.get_rect(center = self.handle.get_rect().center)
            self.handle.blit(temp,text_rect)

    def make_image(self):
        """Draw the background, handle, and any content items contained in
        the window."""
        temp = pg.Surface(self.subrect.size).convert_alpha()
        temp.fill((0,0,0,0))
        temp.blit(self.kwargs["background"],(0,self.handle_rect.height))
        temp.blit(self.handle,self.handle_rect)
        for obj in self.content:
            obj.update(temp)
        self.image = temp

    def update(self,surface):
        """Update and draw the window to the target surface."""
        if self.drag:
            self.subrect.move_ip(pg.mouse.get_rel())
            if self.kwargs["clamp"]:
                try:
                    self.subrect.clamp_ip(self.subrect.parent)
                except TypeError:
                    self.subrect.clamp_ip(pg.display.get_surface().get_rect())
        self.make_image()
        surface.blit(self.image,self.subrect)

    def get_events(self,event):
        """Process events and return any needed results back up to the
        caller."""
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.handle_rect.rel2display().collidepoint(event.pos):
                    self.drag = True
                    pg.mouse.get_rel()
        elif event.type == pg.MOUSEBUTTONUP:
            self.drag = False
        for obj in self.content:
            get = obj.get_events(event)
            if get:
                return get
