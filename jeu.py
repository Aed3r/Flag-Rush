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
                if data[1] == "WEAPON":
                    items.append(ut.Item(data[0], data[1], float(data[2]), ut.Weapon(float(data[3]), int(data[4]), data[5])))
                else:
                    items.append(ut.Item(data[0], data[1], float(data[2])))


Green = ut.Map("Green", screen, (1000, 1000), items, (500,500)) # Défini une map de taille 1000 sur 1000 et fait apparaître le perso au point (500,500)
Green.load()


perso=ut.Perso("hero", screen, 1, 5, Green, 100) # Défini un perso de vitesse 1, qui peut avoir 5 items à la fois et qui a 100 point de vie max
perso.load()

pygame.display.flip() # Rafraichi le jeu
done=True
while done: # Tant que done est égal à True : 
        pygame.time.delay(5) # Freeze le programme pendant 5ms pour ralentir le perso
        key=pygame.key.get_pressed() # liste les appui sur le clavier
        if key[K_UP]: # Appui sur la flèche du haut
            perso.mouv("haut")
        if key[K_DOWN]: # Appui sur la flèche du bas
            perso.mouv("bas")
        if key[K_LEFT]: # Appui sur la flèche de gauche
            perso.mouv("gauche")
        if key[K_RIGHT]: # Appui sur la flèche de droite
            perso.mouv("droite")
        if key[K_e]: #Ramasser un item
            perso.mouv("ramasser")

        for event in pygame.event.get(): #vérifie tous les événements possibles
            if event.type==pygame.QUIT: # si l'événement est un quitter
                done = False # sort de la boucle

        Green.load() # recharge la map
        perso.load() # recharge le perso à ses nouvelles coordonnées
        Green.mapObstacles[0].load(screen) # recharge les obstacles
        pygame.display.flip() # Rafraichi le jeu
pygame.quit() # quitte pygame





