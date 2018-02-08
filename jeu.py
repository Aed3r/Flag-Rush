import pygame as pg

pg.init()
screen = pg.display.set_mode((400, 300))
done = False

while not done:
        for event in pg.event.get():
                if event.type == pg.QUIT:
                        done = True
        
        pg.display.flip()

class Map:
    def __init__(self, background, spawn):
        self.background = background
        self.spawn = spawn
    
    def load():
        
