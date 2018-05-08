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

#region variables
items = []
obstacles = []
enemies = []
characters = []
maps = []
char = None
map = None
mapObjects = [] # Liste de tout les objets de la map
widthSmaller = None # Booléen définissant si la largeur de la map est plus petite que celle de l'écran
heightSmaller = None # Booléen définissant si la hauteur de la map est plus petite que celle de l'écran

drawHitboxes = False # Booléen définissant si l'on voit les hitboxes ou non
drawPaths = False # Booléen définissant si l'on voit les chemins ou non
drawFPS = False # Booléen définissant si l'on voit les FPS ou non
placeObjects = False # Booléen activant le mode construction
lastFPS = 0.0
fpsFont = pg.font.SysFont("Roboto", 10, False, False) # La police utilisé pour afficher les FPS
#endregion


def loadItems(): # Charge les types d'items dans une liste
      tempItems = [] # Liste temporaire des items
      with open("Resources/Items/Data.txt") as itemsFile: 
                  for line in itemsFile.readlines():
                        if line.strip() and not line.strip().isspace():
                              data = line.split(',')
                              if data[1] == "WEAPON": # Dans le cas où l'item est une arme il recoit des caractéristiques supplémentaires sous la forme de la classe 'Weapon'
                                    tempItems.append(ut.Item(data[0], data[1], float(data[2]), ut.Weapon(float(data[3]), int(data[4]), data[5], data[6])))
                              else:
                                    tempItems.append(ut.Item(data[0], data[1], float(data[2])))
      return tempItems

def loadObstacles(): # Charge les obstacles dans une liste
      tempObstacles = [] # Liste temporaire des obstacles
      with open("Resources/Obstacles/Data.txt") as obstaclesFile:
            for line in obstaclesFile.readlines():
                  if line.strip() and not line.strip().isspace():
                        data = line.split(',')
                        tempObstacles.append(ut.Obstacle(data[0], ut.Hitbox((int(data[1]), int(data[2])), (int(data[3]), int(data[4])))))
      return tempObstacles

def loadMaps(): # Charge les maps dans une liste
      global items
      global obstacles
      global enemies

      tempMaps = [] # Liste temporaire des maps
      with open("Resources/Maps/Data.txt") as mapsFile:
            for line in mapsFile.readlines():
                  if line.strip() and not line.strip().isspace():
                        data = line.split(',')
                        tempMaps.append(ut.Map(data[0], screen, items, obstacles, (int(data[1]), int(data[2])), enemies))
      return tempMaps

def loadCharacters(): # Charge les différents charactères dans une liste
      tempCharacters = []
      with open("Resources/Persos/Data.txt") as charactersFile:
            for line in charactersFile.readlines():
                  if line.strip() and not line.strip().isspace():
                        data = line.split(',')
                        tempCharacters.append(ut.Perso(data[0], screen, float(data[1]), int(data[2]), int(data[3])))
      return tempCharacters

def loadEnemies(): # Charge les différents ennemis dans une liste
      tempEnemies = []
      with open("Resources/Enemies/Data.txt") as enemiesFile:
            for line in enemiesFile.readlines():
                  if line.strip() and not line.strip().isspace():
                        data = line.split(',')
                        tempItems = [x for x in items if any([i for i in data[4:] if i == x.name])] # Compréhension de liste qui filtre les items ayant les mêmes nom que ceux indiqué dans data au déla de l'index 5
                        tempEnemies.append(ut.Enemy(data[0], screen, map, int(data[1]), int(data[2]), int(data[3]), int(data[4]), tempItems))
      return tempEnemies

def loadResources():
      global items
      global obstacles
      global enemies
      global maps
      global characters

      items = loadItems()
      obstacles = loadObstacles()
      enemies = loadEnemies()
      maps = loadMaps()
      characters = loadCharacters()

def mapSetup(chosenMap, chosenChar):
      global map
      global char
      global maps
      global characters

      loadMaps()
      map = maps[chosenMap] # Map choisie par l'utilisateur
      char = characters[chosenChar] # Perso choisi par l'utilisateur
      map.players = [char]
      char.map = map
      for player in map.players:
            player.rect.topleft = map.spawnCoords
      updateMapOBJs() # Récupère tous les objets de la map active et les tris
      if map.size[0] < screenSize[0]:
            widthSmaller = True # La largeur de la map est plus petite que celle de l'écran
      else:
            widthSmaller = False
      if map.size[1] < screenSize[1]:
            heightSmaller = True # La hauteur de la map est plus petite que celle de l'écran
      else:
            heightSmaller = False


screenRect = None
def draw(): # Retrace tout les éléments du jeu. Ordre important
      global screenRect 

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
      map.drawObjects([obj for obj in mapObjects if obj.rect.bottom <= char.rect.bottom], screenRect) # Dessine les objets devont se trouver "en dessous" du joueur
      char.draw(screenRect) # dessine le perso à ses nouvelles coordonnées
      char.drawBullets(screenRect, screen) # Dessine les balles
      map.drawObjects([obj for obj in mapObjects if char.rect.bottom < obj.rect.bottom], screenRect) # Dessine les obstacles devont se trouver "au dessus" du joueur

      alphaSurface.fill((255,255,255,0)) # Enlève ce qu'il se trouvait sur la surface alpha auparavant
      if drawHitboxes:
            map.drawObjects(map.hitboxes, screenRect, True, alphaSurface) # Déssine les hitbox de la map si ils ne sont pas déjà affichés
      if drawPaths:
            map.drawObjects([item for sublist in [x.nodes for x in [x.pathFinder for x in map.enemies]] for item in sublist], screenRect, True, alphaSurface) # Récupère tous les nodes de tous les pathFinder d'ennemis et les dessine en transparence (https://stackoverflow.com/a/952952)
            for enemy in map.enemies:
                  enemy.pathFinder.drawPath(alphaSurface, screenRect.topleft) # Affiche les chemins de tous les ennemis de la map
      if drawFPS:
            fpsSurface = fpsFont.render(str(lastFPS), True, pg.Color("black"), pg.Color("white")) # Crée le texte pour afficher les FPS
            screen.blit(fpsSurface, (screenSize[0] - fpsSurface.get_size()[0], 0)) # Ajoute se texte au coin en haut à droite de l'écran
      if placeObjects:
            if type(map.objectToPlace[0]) is pg.Rect:
                  pg.draw.rect(alphaSurface, pg.Color(191, 63, 63, 127), map.objectToPlace[0].move(-screenRect[0], -screenRect[1]))
            elif map.objectToPlace[0] == "delete":
                  screen.blit(pg.image.load("Resources/Menus/Supprimer.png").convert_alpha(), (map.objectToPlace[1][0] - screenRect[0], map.objectToPlace[1][1] - screenRect[1]))
            else:
                  screen.blit(map.objectToPlace[0].sprite, (map.objectToPlace[1][0] - screenRect[0], map.objectToPlace[1][1] - screenRect[1]))
      if drawHitboxes or drawPaths or placeObjects:
            screen.blit(alphaSurface, (0, 0)) # Dessine la couche semi-transparente qui contient les hitbox et les chemins
      pg.display.flip() # Rafraichi le jeu

def react():
      global drawInfo
      global f1Pressed

      char.mouvBullets()

      key=pg.key.get_pressed() # liste les appui sur le clavier
      if key[K_UP]: # Appui sur la flèche du haut
            char.mouv("haut", screenRect)
      if key[K_DOWN]: # Appui sur la flèche du bas
            char.mouv("bas", screenRect)
      if key[K_LEFT]: # Appui sur la flèche de gauche
            char.mouv("gauche", screenRect)
      if key[K_RIGHT]: # Appui sur la flèche de droite
            char.mouv("droite", screenRect)
      if key[K_e]: #Ramasser un item
            char.mouv("ramasser", screenRect)
      if not placeObjects:
            map.moveEnemies()

      if placeObjects:
            map.objectPlacer("update", screenRect) # Met à jour l'emplacement de l'objet "fantôme" en fonction des coordonnées de la souris

def updateMapOBJs(): # Récupère tous les objets de la map active et les tris
      global mapObjects
      mapObjects = map.items + map.obstacles + map.enemies # Liste de tout les objets de la map
      mapObjects.sort(key = lambda x: x.rect.bottom) # Trie les objets par rapport à leur position la plus basse: du plus petit au plus grand


def menuDepart():
      fondMenu=pg.image.load("Resources/Menus/BackgroundMenuDepart.png")
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
                              mapSetup(2, 0)
                              jeu()
                              notDone=False
                        if boutonQuitter.rect.collidepoint(event.pos[0],event.pos[1]):
                              pg.quit() # quitte pygame
                              notDone=False

def menuFin():
      notDone2=True
      fondMenu2=pg.image.load("Resources/Menus/BackgroundMenuFin.png")
      fondMenu2=pg.transform.scale(fondMenu2,screenSize)
      screen.blit(fondMenu2,(0,0))
      boutonMenu=ut.Bouton((600,300),"Retour au Menu",(500,100),screen)
      boutonMenu.draw()
      boutonQuitter=ut.Bouton((800,500),"Quitter",(200,100),screen)
      boutonQuitter.draw()
      pg.display.flip()
      while notDone2:
            for event in pg.event.get():
                  if event.type==MOUSEBUTTONDOWN and event.button==1:
                        if boutonMenu.rect.collidepoint(event.pos[0],event.pos[1]):
                              menuDepart()
                              notDone2=False
                        if boutonQuitter.rect.collidepoint(event.pos[0],event.pos[1]):
                              notDone2=False
                              pg.quit() # quitte pygame

def menuPause():
      notDone3=True
      boutonJouer=ut.Bouton((600,300),"Retour au Jeu",(500,100),screen)
      boutonJouer.draw()
      boutonMenu=ut.Bouton((600,500),"Retour au Menu",(500,100),screen)
      boutonMenu.draw()
      boutonQuitter=ut.Bouton((600,700),"Quitter",(200,100),screen)
      boutonQuitter.draw()
      pg.display.flip()
      while notDone3:
            for event in pg.event.get():
                  if event.type==MOUSEBUTTONDOWN and event.button==1:
                        if boutonJouer.rect.collidepoint(event.pos[0],event.pos[1]):
                              jeu()
                              notDone3=False
                        if boutonMenu.rect.collidepoint(event.pos[0],event.pos[1]):
                              menuDepart()
                              notDone3=False
                        if boutonQuitter.rect.collidepoint(event.pos[0],event.pos[1]):
                              notDone3=False
                              pg.quit() # quitte pygame

def jeu():
      global notDone
      global drawHitboxes
      global drawPaths
      global drawFPS
      global placeObjects
      global lastFPS

      notDone = True # Vrai tant que l'utilisateur souhaite jouer
      while notDone: # Tant que done est égal à True :
            startTime = time.time() # temps de début de la boucle en s
            draw() # Tout retracé
            react() # Vérifier les coordonnées
            for event in pg.event.get(): #vérifie tous les événements possibles
                  if event.type == QUIT: # si l'événement est un quitter
                        notDone = False # sort de la boucle
                        pg.quit()
                  elif event.type == MOUSEBUTTONUP: # Si la souris est utilisé
                        if event.button == 1 and not placeObjects:
                              char.mouv('tirer', screenRect)
                        elif event.button == 1 and placeObjects: # Place un nouvel objet
                              map.objectPlacer("place", screenRect)  
                              updateMapOBJs()		
                        elif event.button == 4 and placeObjects: # Modifie l'objet a placer
                              map.objectPlacer("scrollUp", screenRect)
                        elif event.button == 5 and placeObjects: # Modifie l'objet a placer
                              map.objectPlacer("scrollDown", screenRect)				
                  elif event.type == KEYUP: # Si le clavier est utilisé. Permet l'activation du menu pause ou des fonctions caché (pour afficher, dans l'ordre, les hitboxes, les chemins, les FPS, le placeur d'objets et changer l'image de fonc en fonction des objets placé)
                        if event.key == K_ESCAPE and placeObjects:
                              placeObjects = False
                        elif event.key == K_ESCAPE:
                              menuPause()
                        elif event.key == K_F9 and not drawHitboxes:
                              drawHitboxes = True
                        elif event.key == K_F9 and drawHitboxes:
                              drawHitboxes = False
                        elif event.key == K_F10 and not drawPaths:
                              drawPaths = True
                        elif event.key == K_F10 and drawPaths:
                              drawPaths = False
                        elif event.key == K_F11 and not drawFPS:
                              drawFPS = True
                        elif event.key == K_F11 and drawFPS:
                              drawFPS = False
                        elif event.key == K_F12 and not placeObjects:
                              map.reset(enemies, items, False)
                              placeObjects = True
                        elif event.key == K_F12 and placeObjects:
                              placeObjects = False
                        elif event.key == K_F8 and placeObjects:
                              map.reset(enemies, items, False)
                              tempSurface = pg.Surface(map.size)
                              tempSurface.blit(map.background, (0, 0))
                              pg.image.save(tempSurface, "Resources/Maps/Sprites/" + map.name + "Backup.png")
                              for obj in map.items + map.obstacles + map.enemies:
                                    tempSurface.blit(obj.sprite, obj.rect.topleft)
                              pg.image.save(tempSurface, "Resources/Maps/Sprites/" + map.name + ".png")
                              os.remove("Resources/Maps/Enemies/" + map.name + ".txt")
                              os.remove("Resources/Maps/Items/" + map.name + ".txt")
                              os.remove("Resources/Maps/Obstacles/" + map.name + ".txt")
                              open("Resources/Maps/Enemies/" + map.name + ".txt", 'w')
                              open("Resources/Maps/Items/" + map.name + ".txt", 'w')
                              open("Resources/Maps/Obstacles/" + map.name + ".txt", 'w')
                              mapSetup(2, 0)

            pg.time.Clock().tick_busy_loop(120) # Limite les FPS au maximum indiqué
            lastFPS = round(1.0 / (time.time() - startTime), 2) # Calcul le nombre d'image par seconde. FPS = 1 / temps de la boucle


loadResources()

menuDepart()






