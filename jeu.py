import pygame
from pygame.locals import *
import utilities as ut

pygame.init()
screenSize = width, height = 1000, 1000
screen = pygame.display.set_mode(screenSize)

items = []

with open("Resources/Items/Data.txt") as itemsFile: # Charge les types d'items dans une liste
        for line in itemsFile.readlines():
                data = line.split(',')
                if data(data[1] == "WEAPON"):
                    items.append(ut.Item(data[0], data[1], float(data[2]), ut.Weapon(float(data[3]), int(data[4]), data[5])))
                else:
                    items.append(ut.Item(data[0], data[1], float(data[2])))


Green = ut.Map("Green", screen, (1000, 1000), items, (500,500))
Green.load()


perso=ut.Perso("hero", screen, 1, 5, Green, 100)
perso.load()

pygame.display.flip() # Rafraichi le jeu
done=True
while done:
        pygame.time.delay(5)
        key=pygame.key.get_pressed()
        if key[K_UP]:
            perso.mouv("haut")
        if key[K_DOWN]:
            perso.mouv("bas")
        if key[K_LEFT]:
            perso.mouv("gauche")
        if key[K_RIGHT]:
            perso.mouv("droite")
        if key[K_e]: #Ramasser un item
            perso.mouv("ramasser")

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                done = False

        Green.load()
        perso.load()
        Green.mapObstacles[0].load(screen)
        pygame.display.flip() # Rafraichi le jeu
pygame.quit()





