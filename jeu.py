import pygame as pg

#region modules
from pygame.locals import *
import utilities as ut
import os
import time
import ctypes
from ctypes import *
#endregion


#region screen and pygame setup
pg.init() # Initialise pg
pg.event.set_allowed([QUIT, KEYUP, MOUSEBUTTONDOWN]) # Limite la détection de touches
ctypes.windll.user32.SetProcessDPIAware() # Enlève le redimensionnement de l'image sous Windows (https://gamedev.stackexchange.com/a/105820)
screenSize = (windll.user32.GetSystemMetrics(0),windll.user32.GetSystemMetrics(1)) # Récupère la résolution a utilisé ensuite 
screen = pg.display.set_mode(screenSize, DOUBLEBUF | FULLSCREEN) # Crée la surface écran avec la résolution indiquée, en plein écran et avec une performance doublé
screen.set_alpha(None) # Enlève la couche alpha de l'écran afin d'améliorer la performance du jeu
alphaSurface = pg.Surface(screenSize, pg.SRCALPHA) # Crée une surface qui servira a dessiner des objets avec de la transparence au dessus de l'écran définit auparavant (https://stackoverflow.com/a/6350227)
alphaSurface.fill((255,255,255,0)) # Rend la surface semi-transparente
#endregion


def loadItems(): # Charge les types d'items dans une liste
    tempItems = [] # Liste temporaire des items
    with open("Resources/Items/Data.txt") as itemsFile: 
            for line in itemsFile.readlines():
                    data = line.split(',')
                    if data[1] == "WEAPON": # Dans le cas où l'item est une arme il recoit des caractéristiques supplémentaires sous la forme de la classe 'Weapon'
                        tempItems.append(ut.Item(data[0], data[1], float(data[2]), ut.Weapon(float(data[3]), int(data[4]), data[5])))
                    else:
                        tempItems.append(ut.Item(data[0], data[1], float(data[2])))
    return tempItems

def loadObstacles(): # Charge les obstacles dans une liste
    tempObstacles = [] # Liste temporaire des obstacles
    with open("Resources/Obstacles/Data.txt") as obstaclesFile:
        for line in obstaclesFile.readlines():
            data = line.split(',')
            tempObstacles.append(ut.Obstacle(data[0], ut.Hitbox((int(data[1]), int(data[2])), (int(data[3]), int(data[4])))))
    return tempObstacles

def loadMaps(): # Charge les maps dans une liste
    tempMaps = [] # Liste temporaire des maps
    with open("Resources/Maps/Data.txt") as mapsFile:
        for line in mapsFile.readlines():
            data = line.split(',')
            tempMaps.append(ut.Map(data[0], screen, (int(data[1]), int(data[2])), items, obstacles, (int(data[3]), int(data[4]))))
    return tempMaps

def loadCharacters(): # Charge les différents charactères dans une liste
    tempCharacters = []
    with open("Resources/Persos/Data.txt") as charactersFile:
        for line in charactersFile.readlines():
            data = line.split(',')
            tempCharacters.append(ut.Perso(data[0], screen, float(data[1]), int(data[2]), int(data[3]), map))
    return tempCharacters

def loadEnemies(): # Charge les différents ennemis dans une liste
    tempEnemies = []
    with open("Resources/Enemies/Data.txt") as enemiesFile:
        for line in enemiesFile.readlines():
            data = line.split(',')
            tempItems = [x for x in items if any([i for i in data[4:] if i == x.name])] # Compréhension de liste qui filtre les items ayant les mêmes nom que ceux indiqué dans data au déla de l'index 5
            tempEnemies.append(ut.Enemy(data[0], screen, map, int(data[1]), int(data[2]), int(data[3]), int(data[4]), tempItems))
    return tempEnemies


drawHitboxes = False # Booléen définissant si les hitbox sont affiché ou non
def draw(): # Retrace tout les éléments du jeu. Ordre important
    if widthSmaller: # Lorsque la largeur de la map est plus petite que la largeur de l'écran
        chosenX = map.size[0] / 2 - screenSize[0] / 2 # L'emplacement X du rectangle écran définit par rapport à la map pour que celle-ci soit centré
        pg.draw.rect(screen, pg.Color(0, 0, 0), pg.Rect((0, 0), screenSize)) # Déssine le fond de l'écran en noir pour que les anciens éléments ne réapparaisse pas
    else:
        chosenX = char.rect.left - screenSize[0] / 2 # L'emplacement X du rectangle écran définit par rapport au charactère pour que celui-ci soit centré
    if heightSmaller: # Lorsque l'hauteur de la map est plus petite que l'hauteur de l'écran
        chosenY = map.size[1] / 2 - screenSize[1] / 2 # L'emplacement X du rectangle écran définit par rapport à la map pour que celle-ci soit centré
        pg.draw.rect(screen, pg.Color(0, 0, 0), pg.Rect((0, 0), screenSize)) # Déssine le fond de l'écran en noir pour que les anciens éléments ne réapparaisse pas
    else:
        chosenY = char.rect.top - screenSize[1] / 2 # L'emplacement X du rectangle écran définit par rapport au charactère pour que celui-ci soit centré

    screenRect = pg.Rect((chosenX, chosenY), screenSize) # Détermine la taille et les coordonnées de l'écran selon la map choisie et le charactère

    if not widthSmaller: # Lorsque la largeur de la map est plus grande que celle de l'écran
        if screenRect.x < 0: # Evite que l'écran dépasse le bord haut de la map
            screenRect.x = 0
        elif screenRect.right > map.size[0]: # Evite que l'écran dépasse le bord droit de la map
            screenRect.x = map.size[0] - screenRect.width
    if not heightSmaller: # Lorsque l'hauteur de la map est plus grande que celle de l'écran
        if screenRect.y < 0: # Evite que l'écran dépasse le bord bas de la map
            screenRect.y = 0
        elif screenRect.bottom > map.size[1]: # Evite que l'écran dépasse le bord gauche de la map
            screenRect.y = map.size[1] - screenRect.height

    map.draw(screenRect, widthSmaller, heightSmaller) # Dessine la map
    map.drawObjects(map.obstacles, screenRect) # Dessine les obstacles tel que des bâtiments. Le premier appel dessine la partie basse des obstacles coorespondant à la hitbox
    map.drawObjects(map.items, screenRect) # Dessine les items
    char.draw(screenRect) # dessine le perso à ses nouvelles coordonnées
    map.drawObjects(map.enemies, screenRect) # Dessine les ennemis
    map.drawObjects(map.obstacles, screenRect) # Le deuxième appel dessine la partie haute des obstacles. Les deux appels simule la perspective
    if drawHitboxes:
        alphaSurface.fill((255,255,255,0)) # Enlève ce qu'il se trouvait sur la surface auparavant
        map.drawObjects(map.hitboxes, screenRect, True, alphaSurface) # Déssine les hitbox de la map si ils ne sont pas déjà affichés
        map.drawObjects([item for sublist in [x.nodes for x in [x.pathFinder for x in map.enemies]] for item in sublist], screenRect, True, alphaSurface) # Récupère tous les nodes de tous les pathFinder d'ennemis et les dessine en transparence (https://stackoverflow.com/a/952952)
        for enemy in map.enemies:
            enemy.pathFinder.drawPath(alphaSurface, screenRect.topleft)
        screen.blit(alphaSurface, (0, 0)) # Dessine la couche semi-transparente qui contient les hitbox et les chemins
    pg.display.flip() # Rafraichi le jeu

f1Pressed = False # Booléen définissant si la touche F1 est appuyé ou non
def react():
    global drawHitboxes
    global f1Pressed

    key=pg.key.get_pressed() # liste les appui sur le clavier
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
    if key[K_F1]: #Afficher les hitbox
        if not drawHitboxes and not f1Pressed: # Les hitbox ne sont jusque là pas affichés et l'utilisateur n'a auparavant pas appuyé sur F1
            drawHitboxes = True # Afficher les hitbox
        elif drawHitboxes and not f1Pressed: # Les hitbox sont affichés et l'utilisateur n'a auparavant pas appuyé sur F1
            drawHitboxes = False # Ne plus afficher les hitbox
        f1Pressed = True
    else:
        f1Pressed = False
    map.moveEnemies()


#region resources setup
items = loadItems()

obstacles = loadObstacles()

maps = loadMaps()
map = maps[2] # Map choisie par l'utilisateur

enemies = loadEnemies()
map.appendEnemies(enemies)

characters = loadCharacters()
char = characters[0] # Perso choisi par l'utilisateur
map.players = characters

widthSmaller = False # Booléen définissant si la largeur de la map est plus petite que celle de l'écran
heightSmaller = False # Booléen définissant si la hauteur de la map est plus petite que celle de l'écran
if map.size[0] < screenSize[0]:
    widthSmaller = True # La largeur de la map est plus petite que celle de l'écran
if map.size[1] < screenSize[1]:
    heightSmaller = True # La hauteur de la map est plus petite que celle de l'écran
#endregion


#region menu and game fonctions
def menuDepart():
    fondMenu=pg.image.load("Resources/Menus/BackgroundMenuDépart.png")
    fondMenu=pg.transform.scale(fondMenu,screenSize)
    screen.blit(fondMenu,(0,0))
    boutonJouer=ut.Bouton((750,200),"Jouer",(200,100),screen)
    boutonJouer.draw()
    boutonQuitter=ut.Bouton((750,500),"Quitter",(200,100),screen)
    boutonQuitter.draw()
    boutonOptions=ut.Bouton((750,800),"Options",(200,100),screen)
    boutonOptions.draw()
    pg.display.flip()
    notDone=True
    while notDone:
        for event in pg.event.get():
            if event.type==MOUSEBUTTONDOWN and event.button==1:
                if boutonJouer.rect.collidepoint(event.pos[0],event.pos[1]):
                    jeu()
                    notDone=False
                if boutonQuitter.rect.collidepoint(event.pos[0],event.pos[1]):
                    notDone=False

def jeu():
    global notDone  
    notDone = True # Vrai tant que l'utilisateur souhaite jouer
    while notDone: # Tant que done est égal à True : 
        startTime = time.time() # temps de début de la boucle en s
        draw() # Tout retracé
        react() # Vérifier les coordonnées
        for event in pg.event.get(): #vérifie tous les événements possibles
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE): # si l'événement est un quitter ou l'utilisateur utilise échap
                notDone = False # sort de la boucle
            if event.type ==MOUSEBUTTONDOWN and event.button==3:
                menuDepart()
                
        pg.time.Clock().tick_busy_loop(120) # Limite les FPS au maximum indiqué
        print("FPS: ", round(1.0 / (time.time() - startTime), 2)) # FPS = 1 / temps de la boucle
#endregion

menuDepart()

pg.quit() # quitte pygame






