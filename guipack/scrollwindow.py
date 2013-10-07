"""
An attempt to make a window with an attached scrollbar as generically as
possible.  A skin set can be created to customize the look of your window.

Free for all purposes. No warranty expressed or implied.

-Sean "Mekire" McKiernan
"""

import sys
import os
import pygame as pg

from . import setup
from .subrect import Subrect


class ScrollWindow(object):
    def __init__(self,subrect,content,font,**kwargs):
        """Create a scrollbar window with location and size defined by
        rect (x,y,width,height). Content is the list of strings to display
        in the scroll-window.  Various key-word arguments can also be used
        to further customize the menu (see process_kwargs for the complete
        list)."""
        if setup.GFX == None:
            setup.GFX = setup.load_default_images(setup.DEFAULT_RESOURCES)
        self.subrect = subrect
        self.content = content
        self.font = font
        self.highlight_index = None
        self.process_kwargs(kwargs)
        self.rendered = self.render_content((0,0,0))
        self.set_bg_image()
        self.gen_bar_details()

    def process_kwargs(self,kwargs):
        """All of the following can be used as keyword arguments.  Any or all
        of them can be passed to the init by keyword, or a dict of them can be
        passed via the **dict keyword unpacking syntax."""
        self.kwargs = {"background" : None,
            "bg_color"              : (255,255,255),
            "text_color"            : (0,0,0),
            "highlight"             : True,
            "highlight_color"       : (0,0,0,100),
            "highlight_text_color"  : (255,255,0),
            "bar_bg_image"          : setup.GFX["bar_bg"],
            "bar_button_images" : [setup.GFX["button"].subsurface((0,0,24,25)),
                                  setup.GFX["button"].subsurface((0,25,24,25))],
            "bar_slider_image" : setup.GFX["bar"]}
        for kwarg in kwargs:
            if kwarg in self.kwargs:
                self.kwargs[kwarg] = kwargs[kwarg]
            else:
                raise AttributeError("Invalid keyword: {}".format(kwarg))

    def set_bg_image(self):
        """If an image has been suplied via keyword "background", use that
        image; otherwise fill the background surface with the background color.
        (background changable via keyword "bg_color")"""
        if not self.kwargs["background"]:
            self.kwargs["background"] = pg.Surface(self.subrect.size)
            self.kwargs["background"].convert_alpha()
            self.kwargs["background"].fill(self.kwargs["bg_color"])
            resize = setup.GFX["alph_grad"].copy()
            resize = pg.transform.smoothscale(resize,self.subrect.size)
            self.kwargs["background"].blit(resize,(0,0))
        self.image = pg.Surface(self.subrect.size).convert()

    def render_content(self,color):
        """Prerender the menu content."""
        render_list = []
        for item in self.content:
            color = self.kwargs["text_color"]
            render_list.append(self.font.render(item,1,color))
        return render_list

    def activate_highlight(self):
        """Sets the highlight_index to the currently highlighted item.  If no
        items are currently highlighted, highlight_index is set to None.
        Highlighting can be disabled by setting keyword "highlight" to False."""
        if self.kwargs["highlight"] and not self.Bar.drag:
            mouse = pg.mouse.get_pos()
            colly = self.subrect.rel2display().collidepoint(mouse)
            if colly and not self.Bar.subrect.rel2display().collidepoint(mouse):
                relative = self.subrect.rel2self(mouse)[1]
                offset = relative//self.height_per_option
                self.highlight_index = self.index + offset
            else:
                self.highlight_index = None

    def gen_bar_details(self):
        """Calculate some needed bar related variables and create a ScrollBar
        instance."""
        self.index = 0
        self.height_per_option = self.rendered[0].get_size()[1]
        self.options_per_page = self.subrect.height//self.height_per_option
        if self.kwargs["bar_button_images"]:
            but_size = self.kwargs["bar_button_images"][0].get_size()
        else:
            but_size = (self.rendered[0].get_height(),)*2
        bar_r = Subrect((self.subrect.width-but_size[0],0,but_size[0],
                         self.subrect.height),self.subrect)
        self.Bar = _ScrollBar(bar_r,but_size,self.options_per_page,
                              len(self.content),self.kwargs)

    def update_bar_rect(self):
        """Update location of bar_rect. If dragging find new index."""
        if self.Bar.drag:
            mouse_y = pg.mouse.get_pos()[1]
            next_ind = self.Bar.drag[1]+int((mouse_y-
                                          self.Bar.drag[0])//self.Bar.perindex)
            if next_ind <= 0:
                self.index = 0
            elif next_ind > len(self.content)-self.options_per_page:
                self.index = len(self.content)-self.options_per_page
            else:
                self.index = next_ind
        self.Bar.slider_rect.y = ( self.Bar.button_size[1]
                                 +(self.index*self.Bar.perindex))
        if self.index == len(self.content)-self.options_per_page:
            self.Bar.slider_rect.y = ( self.Bar.subrect.height
                                      -self.Bar.button_size[1]
                                      -self.Bar.slider_rect.height)

    def update_content(self):
        """Blit the content highlighting if called for."""
        to_render = self.rendered[self.index:self.index+self.options_per_page]
        for i,item in enumerate(to_render):
            if self.index+i == self.highlight_index:
                temp = pg.Surface((self.subrect.width,item.get_height()))
                temp.convert_alpha()
                temp.fill(self.kwargs["highlight_color"])
                temp.blit(self.font.render(self.content[self.index+i], 1,
                          self.kwargs["highlight_text_color"]),(5,0))
                self.image.blit(temp,(0,i*self.height_per_option))
            else:
                self.image.blit(item,(5,i*self.height_per_option))

    def update(self,Surf):
        """Update entire window."""
        self.activate_highlight()
        self.update_bar_rect()
        self.image.blit(self.kwargs["background"],(0,0))
        self.update_content()
        self.Bar.update(self.image)
        Surf.blit(self.image,self.subrect)

    def get_events(self,event):
        """Process events for window.  This must be passed events from the main
        event loop of your program.  A selected content string will be returned
        if clicked while highlighted."""
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.highlight_index != None:
                    try:
                        return self.content[self.highlight_index]
                    except IndexError:
                        pass
                elif (self.Bar.subrect.rel2display().collidepoint(event.pos)
                            and len(self.content) > self.options_per_page):
                    if self.on_arrow_click(event):
                        pass
                    else:
                        self.on_bar_click(event)
            elif self.subrect.rel2display().collidepoint(event.pos):
                self.on_scroll_wheel(event)
        elif event.type == pg.MOUSEBUTTONUP:
            self.Bar.drag = False

    def on_scroll_wheel(self,event):
        if event.button == 4:
            #Scroll wheel up.
            if self.index:
                self.index -= 1
        elif event.button == 5:
            #Scroll wheel down.
            if self.index < len(self.content)-self.options_per_page:
                self.index += 1

    def on_arrow_click(self,event):
        buttons = self.Bar.button_rects
        if buttons[0].rel2display().collidepoint(event.pos):
            #User clicks up arrow.
            if self.index:
                self.index -= 1
            return 1
        elif buttons[1].rel2display().collidepoint(event.pos):
            #User clicks down arrow.
            if self.index < len(self.content)-self.options_per_page:
                self.index += 1
            return 1
        return 0

    def on_bar_click(self,event):
        slider = self.Bar.slider_rect
        if slider.rel2display().collidepoint(event.pos):
            #User clicks slide bar.
            self.Bar.drag = (event.pos[1],self.index)
        elif event.pos[1] < slider.rel2display().y:
            #User clicks area above slide bar.
            if self.index - self.options_per_page > 0:
                self.index -= self.options_per_page
            else:
                self.index = 0
        elif event.pos[1] > slider.rel2display().bottom:
            #User clicks area below slide bar.
            max_index = len(self.content)-self.options_per_page
            if self.index+self.options_per_page < max_index:
                self.index += self.options_per_page
            else:
                self.index = max_index


class _ScrollBar(object):
    def __init__(self,subrect,button_size,opts_per,length,kwarg_dict):
        """Contains details of target rects and how to draw the scroll bar
        itself."""
        self.subrect = subrect
        self.opts_per = opts_per
        self.length = float(length)
        self.kwargs = kwarg_dict
        self.button_size = button_size
        rect_one = Subrect(((0,0),self.button_size),self.subrect)
        rect_two = Subrect(((0,self.subrect.height-self.button_size[1]),
                           self.button_size), self.subrect)
        self.button_rects = [rect_one,rect_two]
        self.barsize,self.perindex = self.make_bar()
        self.slider_rect = Subrect((0,self.button_size[1],self.button_size[0],
                                    self.barsize),self.subrect)
        self.drag = False

    def make_bar(self):
        """Calculate size of bar and the number of pixels between items in the
        list."""
        total_bar_height = self.subrect.height - 2*self.button_size[1]
        if self.length > self.opts_per:
            barsize  = total_bar_height*(self.opts_per/self.length)
            perindex = total_bar_height/self.length
            if barsize < 10:
                barsize = 10
        else:
            barsize = total_bar_height
            perindex = 10
        return barsize,perindex

    def make_image(self):
        """Draw all elements of the scroll bar. Defaults are used if images
        have not been provided."""
        temp = pg.Surface(self.subrect.size).convert()
        if self.kwargs["bar_bg_image"]:
            resize = pg.transform.smoothscale(self.kwargs["bar_bg_image"],
                                              self.subrect.size)
            temp.blit(resize,(0,0))
        else:
            temp.fill(0)
        if self.kwargs["bar_button_images"]:
            temp.blit(self.kwargs["bar_button_images"][0],self.button_rects[0])
            temp.blit(self.kwargs["bar_button_images"][1],self.button_rects[1])
        else:
            temp.fill((255,0,0),self.button_rects[0])
            temp.fill((255,0,0),self.button_rects[1])
        if self.kwargs["bar_slider_image"]:
            temp.blit(self.bar_from_image(),self.slider_rect)
        else:
            temp.fill((0,0,255),self.slider_rect)
            inner = self.slider_rect.inflate((-2,-2))
            temp.fill(-1,inner)
        self.image = temp

    def bar_from_image(self):
        """Creates a slider of the needed size based on a slider image.
        It is a little bit hacky and would probably need to be edited a bit
        for different slider images. Currently it fills the whole slider with
        a strip from the image at coordinates (0,4), then draws the center of
        the slider image, and finally draws the top and bottom two pixel strips
        at the top and bottom."""
        raw = self.kwargs["bar_slider_image"]
        raw_rect = raw.get_rect()
        center = raw.subsurface((0,4,raw_rect.width,raw_rect.height-8))
        filler = raw.subsurface((0,4,raw_rect.width,1))
        top = raw.subsurface((0,0,raw_rect.width,2))
        bottom = raw.subsurface((0,raw_rect.height-2,raw_rect.width,2))
        bar_img = pg.Surface(self.slider_rect.size).convert()
        image_center_rect = center.get_rect(center=bar_img.get_rect().center)
        for j in range(self.slider_rect.height):
            bar_img.blit(filler,(0,j))
        bar_img.blit(center,image_center_rect) #middle of bar
        bar_img.blit(top,(0,0)) #top of bar
        bar_img.blit(bottom,(0,self.slider_rect.height-2))
        return bar_img

    def update(self,surface):
        self.make_image()
        surface.blit(self.image,self.subrect)
