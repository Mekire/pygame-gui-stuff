import pygame as pg


class Subrect(pg.Rect):
    """This class allows the use of rects relative to other rects (hierarchies).
    Absolute position of the rect within the display surface can always be
    retrieved."""
    def __init__(self, rect, parent="DISPLAY"):
        pg.Rect.__init__(self,rect)
        self.parent = parent

    def rel2parent(self):
        """Give the rectangle relative to the next level up in the hierarchy."""
        if self.parent == "DISPLAY":
            return self
        else:
            return self.move(self.parent.topleft)

    def rel2display(self):
        """Give the absolute position of the rectangle relative to the display.
        Most useful when doing collision tests (with the mouse for example) on
        the window. Image generally shouldn't be blitted via the rect from
        this function as that breaks the window hierarchy. Blitting should
        be done on the parent at location self.subrect."""
        current = self
        x,y = self.x,self.y
        while current.parent != "DISPLAY":
            current = current.parent
            x += current.x
            y += current.y
        return pg.Rect((x,y),self.size)

    def rel2self(self, point):
        """Given a point relative to the display surface, returns a point
        relative to its own window."""
        rel = self.rel2display()
        return (point[0]-rel.x, point[1]-rel.y)
