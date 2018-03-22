import pygame
from pygame.locals import *
import utilities as ut
import os

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

maps = []
with open("Resources/Maps/Data.txt") as mapsFile:
    for line in mapsFile.readlines():
        data = line.split(',')
        maps.append(ut.Map(data[0], screen, (int(data[1]), int(data[2])), items, (int(data[3]), int(data[4]))))
map = maps[0] # Map choisie par l'utilisateur

characters = []
with open("Resources/Persos/Data.txt") as charactersFile:
    for line in charactersFile.readlines():
        data = line.split(',')
        characters.append(ut.Perso(data[0], screen, float(data[1]), int(data[2]), map, int(data[3])))
char = characters[0] # Perso choisi par l'utilisateur

drawObstacles = False
def draw(): # Retrace tout les éléments du jeu. Ordre important
    map.draw() # Dessine la map
    map.drawItems() # Dessine les items
    char.draw() # dessine le perso à ses nouvelles coordonnées
    if drawObstacles:
        map.drawObstacles()
    pygame.display.flip() # Rafraichi le jeu

def react():
    global drawObstacles

    pygame.time.Clock().tick(150) # Ralentit la vitesse de la boucle
    key=pygame.key.get_pressed() # liste les appui sur le clavier
    if key[K_UP]: # Appui sur la flèche du haut
        char.mouv("haut")
    if key[K_DOWN]: # Appui sur la flèche du bas
        char.mouv("bas")
    if key[K_LEFT]: # Appui sur la flèche de gauche
        char.mouv("gauche")
    if key[K_RIGHT]: # Appui sur la flèche de droite
        char.mouv("droite")
    if key[K_e]: #Ramasser un item
        char.mouv("ramasser")
    if key[K_F1]: #Afficher les obstacles
        if drawObstacles:
            drawObstacles = False
        else:
            drawObstacles = True

notDone=True
while notDone: # Tant que done est égal à True : 
    draw() # Tout retracé
    react() # Vérifier les coordonnées

    for event in pygame.event.get(): #vérifie tous les événements possibles
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE): # si l'événement est un quitter ou l'utilisateur utilise échap
            notDone = False # sort de la boucle

pygame.quit() # quitte pygame





