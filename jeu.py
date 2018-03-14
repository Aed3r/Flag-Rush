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


Green = ut.Map("Green", screen, (1000, 1000), items, (500,500))
Green.load()


perso=ut.Perso("hero", screen, 3, 5, Green)
perso.load()

pygame.display.flip() # Rafraichi le jeu
pygame.key.set_repeat(1,15)
done=True
while done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = False
                elif event.type == pygame.KEYDOWN:
                        perso.mouv(event)
        Green.load()
        perso.load()
        Green.mapObstacles[0].load(screen)
        pygame.display.flip() # Rafraichi le jeu     
pygame.quit()
                        
        
        

        
