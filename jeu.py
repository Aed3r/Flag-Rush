import pygame as pg


#Sprite persos: http://gaurav.munjal.us/Universal-LPC-Spritesheet-Character-Generator/#?=eyes_gray&clothes=formal&formal-shirt=1&formal-pants=1&formal-vest=1&tie=on&hair=plain_raven&hat=none
#region modules
from pygame.locals import *
import utilities as ut
import os
import time
import ctypes
from ctypes import *
import copy
import math
import random
#endregion

#region screen and pygame setup
pg.init() # Initialise pg
pg.event.set_allowed([QUIT, KEYUP, MOUSEBUTTONDOWN]) # Limite la détection de touches
ctypes.windll.user32.SetProcessDPIAware() # Enlève le redimensionnement de l'image sous Windows (https://gamedev.stackexchange.com/a/105820)
screenSize = (windll.user32.GetSystemMetrics(0),windll.user32.GetSystemMetrics(1)) # Récupère la résolution a utilisé ensuite
screen = pg.display.set_mode(screenSize, DOUBLEBUF | FULLSCREEN | HWACCEL | HWSURFACE) # Crée la surface écran avec la résolution indiquée, en plein écran et avec une performance doublé
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
coordsHealthRect=(screenSize[0]/4, 98 * screenSize[1] / 100)
sizeHealthRect=(screenSize[0]/2, 2 * screenSize[1] / 100) 
inventoryBar = ut.List((screenSize[0] / 4, 90 * screenSize[1] / 100), (screenSize[0] / 2,  8 * screenSize[1] / 100), None, screen, 0)
drawHitboxes = False # Booléen définissant si l'on voit les hitboxes ou non
drawPaths = False # Booléen définissant si l'on voit les chemins ou non
drawFPS = False # Booléen définissant si l'on voit les FPS ou non
placeObjects = False # Booléen activant le mode construction
lastFPS = 0.0
fpsFont = pg.font.SysFont("Roboto", 10, False, False) # La police utilisé pour afficher les FPS
gameFont = pg.font.SysFont("Roboto", 50, False, False) # La police utilisé pour afficher les FPS
gamemode = "Classic" # Mode de jeu. Classic: ramasser le plus possible de drapeau avant de mourrir. Against the Clock: Récupérer le plus de drapeau possible dans un temps imparti
gm2TimeLeft = 60 # Secondes restante au joueur pour atteindre le prochain drapeau
gm2StartTime = None # Le temps de la dernière mise à jour
notDone = True # Tant que le joueur veut jouer
selectedMap = 2 # La map choisit par l'utilisateur
selectedChar = 0 # Le personnage choisit par l'utilisateur
selectedItem = 0 # L'item choisie
gunCooldown = 0 # Temps entre chaque tir
baseStep = 5
currentSteps = baseStep
walkIncrease = 0
walkDirection = "Front"
action = "Idle"
#endregion


def loadItems(): # Charge les types d'items dans une liste
      tempItems = [] # Liste temporaire des items
      with open("Resources/Items/Data.txt") as itemsFile:
                  for line in itemsFile.readlines():
                        if line.strip() and not line.strip().isspace():
                              data = line.split(',')
                              if data[1] == "WEAPON": # Dans le cas où l'item est une arme il recoit des caractéristiques supplémentaires sous la forme de la classe 'Weapon'
                                    tempItems.append(ut.Item(data[0], data[1], float(data[2]), ut.Weapon(float(data[3]), int(data[4]), True if data[5] == "True" else False, True if data[6].strip() == "True" else False, int(data[7]), True if data[8].strip() == "True" else False)))
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
                        tempCharacters.append(ut.Perso(data[0], screen, float(data[1]), int(data[2]), int(data[3]), items))
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

def mapSetup():
      global map
      global char
      global maps
      global characters
      global gm2StartTime
      global gm2TimeLeft

      loadMaps()
      map = maps[selectedMap] # Map choisie par l'utilisateur
      char = characters[selectedChar] # Perso choisi par l'utilisateur
      map.players = [char]
      char.map = map
      char.health = 100
      char.score = 0
      gm2TimeLeft = 45
      gm2StartTime = time.time()
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
def draw(noFlip = False): # Retrace tout les éléments du jeu. Ordre important
      global screenRect
      global mapObjects

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

      mapObjects.sort(key = lambda x: x.rect.bottom) # Trie les objets par rapport à leur position la plus basse: du plus petit au plus grand
      map.draw(screenRect, widthSmaller, heightSmaller) # Dessine la map
      map.drawObjects([obj for obj in mapObjects if obj.rect.bottom <= char.rect.bottom], screenRect) # Dessine les objets devont se trouver "en dessous" du joueur
      char.draw(screenRect, walkDirection + action +str(walkIncrease)) # dessine le perso à ses nouvelles coordonnées
      char.drawBullets(screenRect, screen) # Dessine les balles
      map.drawObjects([obj for obj in mapObjects if char.rect.bottom < obj.rect.bottom], screenRect) # Dessine les obstacles devont se trouver "au dessus" du joueur

      if drawHitboxes or drawPaths or placeObjects:
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

      pg.draw.rect(screen,pg.Color("grey"),pg.Rect(coordsHealthRect,sizeHealthRect)) 
      pg.draw.rect(screen,pg.Color(255,0,0),pg.Rect(coordsHealthRect,(sizeHealthRect[0]*char.health/100, sizeHealthRect[1]))) 
      inventoryBar.setItems(char.items)
      inventoryBar.draw()

      scoreSurface = gameFont.render("Score : " + str(char.score), True, pg.Color("black"), pg.Color("white")) # Crée le texte pour afficher le temp restant
      screen.blit(scoreSurface, (screenSize[0] / 2 - scoreSurface.get_size()[0] / 2, 0)) # Ajoute ce texte au millieu en haut de l'écran

      if gamemode == "Against the Clock" and gm2StartTime:
            timeSurface = gameFont.render(str(round(gm2TimeLeft - (time.time() - gm2StartTime))), True, pg.Color("black"), pg.Color("white")) # Crée le texte pour afficher le temp restant
            screen.blit(timeSurface, (screenSize[0] / 2 - timeSurface.get_size()[0] / 2, scoreSurface.get_size()[1])) # Ajoute ce texte au millieu en haut de l'écran
      if not noFlip:
            pg.display.flip() # Rafraichi le jeu

def react():
      global f1Pressed
      global gm2StartTime
      global gm2TimeLeft
      global selectedItem
      global gunCooldown
      global walkIncrease
      global walkDirection
      global currentSteps
      global action

      char.mouvBullets()

      key=pg.key.get_pressed() # liste les appui sur le clavier
      if key[K_w]: # Appui sur la flèche du haut
            char.mouv("haut", screenRect, 0, lastFPS)
            walkDirection = "Back"
      if key[K_s]: # Appui sur la flèche du bas
            char.mouv("bas", screenRect, 0, lastFPS)
            walkDirection = "Front"
      if key[K_a]: # Appui sur la flèche de gauche
            char.mouv("gauche", screenRect, 0, lastFPS)
            walkDirection = "Left"
      if key[K_d]: # Appui sur la flèche de droite
            char.mouv("droite", screenRect, 0, lastFPS)
            walkDirection = "Right"
      if key[K_e]: #Ramasser un item
            char.mouv("ramasser", screenRect)

      if key[K_w] or key[K_s] or key[K_a] or key[K_d]:
            currentSteps += 1
            action = "Walk"
            if walkIncrease == 0:
                  walkIncrease = 1
      else:
            action = "Idle"
            walkIncrease = 0
            currentSteps = 0
      if currentSteps > baseStep:
            currentSteps = 0
            walkIncrease += 1
      if walkIncrease > 8:
            walkIncrease = 1
            
      if gunCooldown <= 0:
            if char.items[selectedItem].type == "WEAPON" and pg.mouse.get_pressed()[0] == 1:
                  if char.items[selectedItem].characteristics.isAutomatic:
                        char.mouv('tirer', screenRect, selectedItem)
                        gunCooldown = char.items[selectedItem].characteristics.cooldown
      else:
            gunCooldown -= 1

      if not placeObjects:
            map.moveEnemies(lastFPS)

      for enemy in char.rect.collidelistall([x.rect for x in map.enemies]):
            char.health-=1
            if char.health < 0:
                  char.health = 0
      if char.health == 0:
            if gamemode == "Classic":
                  print("perdu!")
                  menuFin()
            elif gamemode == "Against the Clock":
                  char.health = 100
                  char.rect.topleft = map.spawnCoords
                  gm2TimeLeft -= 10

      if gamemode == "Against the Clock" and gm2TimeLeft - (time.time() - gm2StartTime) <= 0:
            print("perdu!")
            menuFin()

      if char.rect.colliderect(map.objectifObject.rect):
            tempItem = None
            if char.score == 0:
                  tempItem = copy.deepcopy(next(x for x in items if x.name == "Pistol"))
            elif char.score == 5:
                  tempItem = copy.deepcopy(next(x for x in items if x.name == "Shotgun")) 
            elif char.score == 10:
                  tempItem = copy.deepcopy(next(x for x in items if x.name == "Assault Rifle")) 
            elif char.score == 15:
                  tempItem = copy.deepcopy(next(x for x in items if x.name == "Minigun"))  
            elif char.score == 20:
                  print("gagné!")     
                  menuDepart()        
            elif str(char.score)[-1:] == "1" or str(char.score)[-1:] == "3" or str(char.score)[-1:] == "7" or str(char.score)[-1:] == "9":
                  tempItem = copy.deepcopy(next(x for x in items if x.name == "Health Pack"))
            elif len(str(char.score)) == 1 and (str(char.score)[-1:] == "2" or str(char.score)[-1:] == "4" or str(char.score)[-1:] == "6" or str(char.score)[-1:] == "8"):
                  tempItem = copy.deepcopy(next(x for x in items if x.name == "Ammo"))
            elif len(str(char.score)) == 2 and (str(char.score)[-1:] == "2" or str(char.score)[-1:] == "4" or str(char.score)[-1:] == "6" or str(char.score)[-1:] == "8"):
                  tempItem = copy.deepcopy(next(x for x in items if x.name == "Big Ammo"))
            elif str(char.score)[-1:] == "5":
                  tempItem = copy.deepcopy(next(x for x in items if x.name == "Claymore"))
            if tempItem:
                  tempItem.rect.topleft = map.objectifObject.rect.topleft
            map.items.append(tempItem)

            map.randomObjectifCoords()

            if gamemode == "Against the Clock":
                  gm2TimeLeft += 20 # Ajoute trente secondes au cooldown
                  gm2StartTime = time.time()

            char.score += 1

            for n in range(char.score):
                  tempEnemy = copy.deepcopy(enemies[0])
                  tempEnemy.rect.center = map.objectifObject.rect.center
                  tempEnemy.map = map
                  tempEnemy.pathFinder = ut.PathFinder(map.hitboxes, max(tempEnemy.rect.width, tempEnemy.rect.height), tempEnemy.viewingRadius)
                  map.enemies.append(tempEnemy)

      if placeObjects:
            map.objectPlacer("update", screenRect) # Met à jour l'emplacement de l'objet "fantôme" en fonction des coordonnées de la souris

      selectedItem = inventoryBar.selectionIndex

      for enemy in map.enemies:
            if enemy.health <= 0:
                  map.enemies.remove(enemy)

      for explosive in [x for x in map.items if x.type == "EXPLOSIVE" and x.rect.collidelist(map.enemies) != -1 and x.pickedUpOnce == True]:
            for obj in map.enemies + [char]:
                  if math.sqrt(math.pow(obj.rect.x - explosive.rect.x, 2) + math.pow(obj.rect.y - explosive.rect.y, 2)) <= explosive.value * 3:
                        obj.health -= explosive.value
                        map.items.remove(explosive)

      updateMapOBJs()

def updateMapOBJs(): # Récupère tous les objets de la map active et les tris
      global mapObjects
      mapObjects = map.items + map.obstacles + map.enemies # Liste de tout les objets de la map


def menuDepart():
      global notDone
      fondMenu=pg.image.load("Resources/Menus/BackgroundMenu.png")
      fondMenu=pg.transform.scale(fondMenu, screenSize)

      partsHeight = screenSize[1] / 7
      logo = pg.image.load("Resources/Menus/Title.png")

      buttonSize = (screenSize[0] * 10 / 100, screenSize[1] * 5 / 100)
      boutonJouer=ut.Bouton((screenSize[0] / 2 - buttonSize[0]/2, partsHeight * 3),"Jouer",buttonSize,screen, alphaSurface)
      boutonQuitter=ut.Bouton((screenSize[0] / 2 - buttonSize[0]/2, partsHeight * 6),"Quitter",buttonSize,screen, alphaSurface)
      boutonOptions=ut.Bouton((screenSize[0] / 2 - buttonSize[0]/2, partsHeight * 4),"Options",buttonSize,screen, alphaSurface)

      notDone1=True
      while notDone1:
            alphaSurface.fill((255,255,255,0))
            screen.blit(fondMenu,(0,0))
            screen.blit(logo, (screenSize[0] / 2 - logo.get_size()[0] / 2, partsHeight - logo.get_size()[1] / 2))
            boutonJouer.draw(pg.mouse.get_pos())
            boutonQuitter.draw(pg.mouse.get_pos())
            boutonOptions.draw(pg.mouse.get_pos())
            screen.blit(alphaSurface, (0, 0))
            pg.display.flip()
            for event in pg.event.get():
                  if event.type==MOUSEBUTTONDOWN and event.button==1:
                        if boutonJouer.rect.collidepoint(event.pos[0],event.pos[1]):
                              mapSetup()
                              notDone = True
                              jeu()
                              notDone1=False
                        elif boutonQuitter.rect.collidepoint(event.pos[0],event.pos[1]):
                              notDone1=False
                              notDone = False
                        elif boutonOptions.rect.collidepoint(event.pos[0],event.pos[1]):
                              menuOptions()

def menuFin():
      global notDone
      alphaSurface.fill((0,0,0,50))

      font=pg.font.SysFont("Roboto", 200, True)
      goText=font.render("GAME OVER", 1, (255,0,0))

      partsHeight = screenSize[1] / 7
      buttonSize = (screenSize[0] * 15 / 100, screenSize[1] * 5 / 100)
      boutonMenu=ut.Bouton((screenSize[0] / 2 - buttonSize[0]/2, partsHeight * 3),"Retour au Menu",buttonSize,screen, alphaSurface)
      boutonQuitter=ut.Bouton((screenSize[0] / 2 - buttonSize[0]/2, partsHeight * 5),"Quitter",buttonSize,screen, alphaSurface)

      notDone2=True
      while notDone2:
            draw(True)
            screen.blit(alphaSurface, (0, 0))
            screen.blit(goText, (screenSize[0] / 2 - goText.get_size()[0] / 2, partsHeight - goText.get_size()[1] / 2))
            boutonMenu.draw(pg.mouse.get_pos())
            boutonQuitter.draw(pg.mouse.get_pos())
            screen.blit(alphaSurface, (0, 0))
            pg.display.flip()

            for event in pg.event.get():
                  if event.type==MOUSEBUTTONDOWN and event.button==1:
                        if boutonMenu.rect.collidepoint(event.pos[0],event.pos[1]):
                              menuDepart()
                              notDone2=False
                        if boutonQuitter.rect.collidepoint(event.pos[0],event.pos[1]):
                              notDone2=False
                              notDone = False

def menuPause():
      global gm2StartTime
      global notDone
      notDone3=True

      partsHeight = screenSize[1] / 7
      buttonSize = (screenSize[0] * 15 / 100, screenSize[1] * 5 / 100)

      logo = pg.image.load("Resources/Menus/Title.png")

      boutonJouer=ut.Bouton((partsHeight, partsHeight * 3),"Retour au Jeu",buttonSize,screen, alphaSurface)
      boutonMenu=ut.Bouton((partsHeight, partsHeight * 4),"Retour au Menu",buttonSize,screen, alphaSurface)     
      boutonQuitter=ut.Bouton((partsHeight, partsHeight * 6),"Quitter",buttonSize,screen, alphaSurface)
      
      pg.display.flip()
      while notDone3:
            draw(True)
            alphaSurface.fill((255,255,255,0))
            screen.blit(logo, (partsHeight, partsHeight - logo.get_size()[1] / 2))
            boutonJouer.draw(pg.mouse.get_pos())
            boutonMenu.draw(pg.mouse.get_pos())
            boutonQuitter.draw(pg.mouse.get_pos())
            screen.blit(alphaSurface, (0, 0))
            pg.display.flip()

            for event in pg.event.get():
                  if event.type==MOUSEBUTTONDOWN and event.button==1:
                        if boutonJouer.rect.collidepoint(event.pos[0],event.pos[1]):
                              gm2StartTime = time.time()
                              notDone3=False
                        if boutonMenu.rect.collidepoint(event.pos[0],event.pos[1]):
                              menuDepart()
                              notDone3=False
                        if boutonQuitter.rect.collidepoint(event.pos[0],event.pos[1]):
                              notDone3=False     
                              notDone = False

def menuOptions():
      global gamemode
      global selectedChar
      global selectedMap
      notDone4=True
      fondMenu=pg.image.load("Resources/Menus/BackgroundMenu.png")
      fondMenu=pg.transform.scale(fondMenu,screenSize)

      partsHeight = round(screenSize[1] / 7)
      mapText = gameFont.render("Map :", True, pg.Color("white"), pg.Color("black"))
      mapsSelection = ut.List((0, partsHeight), (screenSize[0], partsHeight), maps, screen, selectedMap)

      charText = gameFont.render("Personnage :", True, pg.Color("white"), pg.Color("black"))
      charsSelection = ut.List((0, partsHeight * 3), (screenSize[0], partsHeight), characters, screen, selectedChar)

      gmText = gameFont.render("Mode de jeu :", True, pg.Color("white"), pg.Color("black"))
      if gamemode == "Against the Clock":
            gamemodeButton=ut.Bouton((round(screenSize[0] / 2 - 250), partsHeight * 5 + partsHeight / 4), "Contre la montre", (500, partsHeight / 2), screen, alphaSurface)
      elif gamemode == "Classic":
            gamemodeButton=ut.Bouton((round(screenSize[0] / 2 - 250), partsHeight * 5 + partsHeight / 4), "Classique", (500, partsHeight / 2), screen, alphaSurface)

      backButton=ut.Bouton((partsHeight, partsHeight * 6 + partsHeight / 4), "Retour", (500,partsHeight / 2), screen, alphaSurface)

      pg.display.flip()
      tempPos = (0, 0)
      while notDone4:
            alphaSurface.fill((255,255,255,0))
            screen.blit(fondMenu,(0,0))
            screen.blit(mapText, (round(screenSize[0] / 2 - mapText.get_size()[0] / 2), round(partsHeight / 2 - mapText.get_size()[1] / 2 + partsHeight * 0)))
            mapsSelection.draw()
            screen.blit(charText, (round(screenSize[0] / 2 - charText.get_size()[0] / 2), round(partsHeight / 2 - charText.get_size()[1] / 2 + partsHeight * 2)))
            charsSelection.draw()
            screen.blit(gmText, (round(screenSize[0] / 2 - gmText.get_size()[0] / 2), round(partsHeight / 2 - gmText.get_size()[1] / 2 + partsHeight * 4)))
            gamemodeButton.draw(pg.mouse.get_pos())
            backButton.draw(pg.mouse.get_pos())
            screen.blit(alphaSurface, (0, 0))
            pg.display.flip()

            for event in pg.event.get():          
                  if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        if gamemodeButton.rect.collidepoint(event.pos) and gamemode == "Classic":
                              gamemode = "Against the Clock"
                              gamemodeButton.text = "Contre la montre"
                        elif gamemodeButton.rect.collidepoint(event.pos) and gamemode == "Against the Clock":
                              gamemode = "Classic"
                              gamemodeButton.text = "Classique"
                        elif backButton.rect.collidepoint(event.pos):
                              notDone4 = False  
                        mapsSelection.updateIndex(event.pos, 0, True)
                        charsSelection.updateIndex(event.pos, 0, True)      
                  elif event.type == MOUSEMOTION:
                        mapsSelection.updateIndex(event.pos, 0, False)
                        charsSelection.updateIndex(event.pos, 0, False)
      selectedMap = mapsSelection.selectionIndex
      selectedChar = charsSelection.selectionIndex

def jeu():
      global notDone
      global drawHitboxes
      global drawPaths
      global drawFPS
      global placeObjects
      global lastFPS
      global gm2TimeLeft
      global gunCooldown
      global selectedItem

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
                        if event.button == 1:
                              if not placeObjects and char.items[selectedItem].type == "EXPLOSIVE":
                                    char.items[selectedItem].rect.topleft = char.rect.center
                                    map.items.append(char.items[selectedItem])
                                    char.items.remove(char.items[selectedItem])
                                    selectedItem = 0
                                    inventoryBar.selectionIndex = 0
                              elif not placeObjects and char.items[selectedItem].type == "WEAPON":
                                    if not char.items[selectedItem].characteristics.isAutomatic:
                                          if gunCooldown <= 0:
                                                char.mouv('tirer', screenRect, selectedItem)
                                                gunCooldown = char.items[selectedItem].characteristics.cooldown
                              elif placeObjects: # Place un nouvel objet
                                    map.objectPlacer("place", screenRect)
                                    updateMapOBJs()
                              inventoryBar.updateIndex(event.pos, 0, True)
                        elif event.button == 4:
                              if placeObjects: # Modifie l'objet a placer
                                    map.objectPlacer("scrollUp", screenRect)
                              else:
                                    inventoryBar.updateIndex(None, 1, False)
                        elif event.button == 5:
                              if placeObjects: # Modifie l'objet a placer
                                    map.objectPlacer("scrollDown", screenRect)
                              else:
                                    inventoryBar.updateIndex(None, 2, False)
                  elif event.type == KEYUP: # Si le clavier est utilisé. Permet l'activation du menu pause ou des fonctions caché (pour afficher, dans l'ordre, les hitboxes, les chemins, les FPS, le placeur d'objets et changer l'image de fonc en fonction des objets placé)
                        if event.key == K_ESCAPE and placeObjects:
                              placeObjects = False
                        elif event.key == K_ESCAPE:
                              gm2TimeLeft = gm2TimeLeft - (time.time() - gm2StartTime)
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
                              tempSurface.blit(map.sprite, (0, 0))
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
                              mapSetup()

            pg.time.Clock().tick_busy_loop(120) # Limite les FPS au maximum indiqué
            lastFPS = round(1.0 / (time.time() - startTime), 2) # Calcul le nombre d'image par seconde. FPS = 1 / temps de la boucle


loadResources()

menuDepart()

pg.quit() # quitte pygame





