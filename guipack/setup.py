import os
import pygame as pg


DEFAULT_RESOURCES = os.path.join(os.path.dirname(__file__),'graphics')
GFX = None


def load_default_images(directory):
    gfx = {}
    for image in os.listdir(directory):
        if image[-3:] in ['png','jpg','bmp']:
            gfx[image[:-4]] = pg.image.load(os.path.join(directory,image))
            gfx[image[:-4]].convert_alpha()
    return gfx
