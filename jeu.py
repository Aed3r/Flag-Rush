import pygame
import utilities as ut

pygame.init()
screenSize = width, height = 1000, 1000
screen = pygame.display.set_mode(screenSize)

items = []

with open("Resources/Items/Data.txt") as itemsFile: # Charge les types d'items dans une liste
        for line in itemsFile.readlines():
                data = line.split(',')
                items.append(ut.Item(data[0], data[1], float(data[2])))

Green = ut.Map("Green", screen, (1000, 1000), items)
Green.load()

perso=ut.Perso(screen, "hero_spritesheet",500,500)
perso.charge()

done=False
while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
                elif event.type == pygame.KEYDOWN:
                        Green.load()
                        perso.mouv(event)
                        
                
                pygame.display.flip()        

                        
        
        

        
