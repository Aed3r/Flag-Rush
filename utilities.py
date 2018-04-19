import pygame
import copy
import math
import random

class Item: # Définis un objet pouvant être utilisé par le joueur
        def __init__(self, name, type, value, characteristics = None):
                if name.lower == "none":
                        raise ValueError("Ne pas utiliser 'none' comme nom d'item!")
                else:
                        self.name = name
                        self.sprite = pygame.image.load("Resources/Items/Sprites/" + self.name + ".png")
                        self.type = type # Une des options définis par le enum ItemTypes
                        self.value = value # La puissance de l'arme, le nombre de points de vies rétablies...
                        self.rect = self.sprite.get_rect() # Les coordonnées et la taille de l'item. La taille est définis par la taille du sprite de l'item
                        if type == "WEAPON": # Si l'item est du type 'Weapon', charger d'autres caractéristiques
                                self.characteristics = characteristics

        def draw(self, coords, screen):
                screen.blit(self.sprite, coords)

        def __deepcopy__(self, memo): # https://stackoverflow.com/a/15774013
                cls = self.__class__
                result = cls.__new__(cls)
                memo[id(self)] = result
                for k, v in self.__dict__.items():
                        if k == "rect":
                                setattr(result, k, copy.deepcopy(v, memo))
                        else:
                                setattr(result, k, copy.copy(v))
                return result


class Weapon: # Classe auxiliaire pour définir les caractéristiques d'une arme
        def __init__(self, aim = 95, speed = 20, isExplosive = False):
                self.aim = aim # La précision de tir en pourcentage. 100% correspond à une ligne droite
                self.speed = speed # La vitesse du projectile
                self.isExplosive = isExplosive # Définis si le projectile explose sur impact (ce qui fait des dégats plus répandus)


class Hitbox:
        def __init__(self, coords, size):
                self.rect = pygame.Rect(coords, size)

        def draw(self, coords, screen):
                pygame.draw.rect(screen, pygame.Color(191, 63, 63, 127), pygame.Rect(coords[0], coords[1], self.rect.w, self.rect.h))


class Obstacle: # Définis des obstacles en perspective et qui présente une hitbox
        def __init__(self, name, hitbox):
                self.name = name
                self.lowerSprite = pygame.image.load("Resources/Obstacles/Sprites/" + name + "Lower.png").convert_alpha() # La partie basse de l'objet qui doit toujours se trouver derrière le joueur
                self.upperSprite = pygame.image.load("Resources/Obstacles/Sprites/" + name + "Upper.png").convert_alpha() # La partie haute de l'objet qui doit toujours se trouver devant le joueur
                self.rect = self.lowerSprite.get_rect()
                self.hitbox = hitbox # La hitbox associé à l'objet
                self.lowerDrawn = False # Booléen définissant quelle partie de l'objet doit être dessiné. False: partie basse, True: partie haute
        
        def draw(self, coords, screen): # Dessine l'objet en deux parties s'alternant. La partie basse est toujours dessiné avant la partie haute
                if self.lowerDrawn: # Dessiner la partie haute
                        screen.blit(self.upperSprite, coords)
                        self.lowerDrawn = False
                else: # Dessiner la partie basse
                        screen.blit(self.lowerSprite, coords)
                        self.lowerDrawn = True

        def __deepcopy__(self, memo): # https://stackoverflow.com/a/15774013
                cls = self.__class__
                result = cls.__new__(cls)
                memo[id(self)] = result
                for k, v in self.__dict__.items():
                        if k == "rect":
                                setattr(result, k, copy.deepcopy(v, memo))
                        else:
                                setattr(result, k, copy.copy(v))
                return result


class Enemy:
        def __init__(self, name, screen, map, speed, health, viewingRadius, reactionTime, weapons):
                self.name = name
                self.sprite = pygame.image.load("Resources/Enemies/Sprites/" + name + ".png").convert_alpha() 
                self.rect = self.sprite.get_rect()
                self.screen = screen
                self.speed = speed
                self.map = map
                self.health = health
                self.viewingRadius = viewingRadius
                self.reactionTime = reactionTime
                self.weapons = weapons
                self.pathFinder = PathFinder(self.map.hitboxes, max(self.rect.width, self.rect.height))
                self.lastPlayerPos = None

        def draw(self, coords, screen):
                screen.blit(self.sprite, coords)

        def distanceBetween(self, pointA, pointB):
                return math.sqrt(math.pow(pointA[0] - pointB[0], 2) + math.pow(pointA[1] - pointB[1], 2))

        def atan2Normalized(self, y, x): # https://stackoverflow.com/a/10343477
                result = math.atan2(y, x)
                if result < 0:
                        result += 2 * math.pi
                return result

        def randomPath(self):
                dest = None
                while not dest or any([x for x in self.map.hitboxes if x.rect.collidepoint(dest)]):
                        randomAngle = random.randint(0, 360)
                        randomDistance = random.randint(self.speed, self.viewingRadius)
                        dest = (round(self.rect.centerx + randomDistance * math.cos(randomAngle * math.pi / 180)), round(self.rect.centery + randomDistance * math.sin(randomAngle * math.pi / 180)))
                self.pathFinder.findBest(self.rect.center, dest)
        
        def moveTowards(self, coords):
                angle = self.atan2Normalized((self.rect.centery - coords[1]), (coords[0] - self.rect.centerx))
                coords = (self.speed * round(math.cos(angle), 5), -self.speed * round(math.sin(angle), 5))
                self.rect.move_ip(coords[0], coords[1])

        def move(self):
                radiusPlayers = [x for x in self.map.players if self.distanceBetween(self.rect.center, x.rect.center) <= self.viewingRadius]
                radiusPlayers.sort(key = lambda x: self.distanceBetween(self.rect.center, x.rect.center))
                if any(radiusPlayers):
                        if self.lastPlayerPos:
                                if self.distanceBetween(self.lastPlayerPos, radiusPlayers[0].rect.center) >= self.reactionTime or self.rect.center == self.lastPlayerPos:
                                        self.pathFinder.findBest(self.rect.center, radiusPlayers[0].rect.center)  
                                        self.lastPlayerPos = radiusPlayers[0].rect.center
                        else:   
                                self.pathFinder.findBest(self.rect.center, radiusPlayers[0].rect.center)  
                                self.lastPlayerPos = radiusPlayers[0].rect.center
                elif (not self.pathFinder.path and self.rect.center == self.pathFinder.finish) or not self.pathFinder.finish:
                                self.randomPath()
               
                if self.pathFinder.path:        
                        if self.distanceBetween(self.rect.center, self.pathFinder.path[0].rect.center) <= self.speed:
                                self.pathFinder.path.pop(0)
                        else:
                                self.moveTowards(self.pathFinder.path[0].rect.center)
                else:
                        if self.distanceBetween(self.rect.center, self.pathFinder.finish) <= self.speed:
                                self.rect.center = self.pathFinder.finish
                        else:
                                self.moveTowards(self.pathFinder.finish)                       


class Map: # Définis une carte jouable 
        def __init__(self, name, screen, objectifCoords, items, obstacles, spawnCoords):
                self.name = name
                self.screen = screen # La fenètre principale
                self.background = pygame.image.load("Resources/Maps/Sprites/" + self.name + ".png").convert() # Charge l'image de fond d'écran
                self.size = self.background.get_size() # Définis la taille de la map à partir de l'image de fond d'écran
                self.objectifCoords = objectifCoords # Où se trouve l'objectif à atteindre
                self.items = [] # Dictionnaire de tous les items de la map. Clés: coordonnées de l'objet, Valeur: instance de le classe Item définissant l'objet en question
                with open("Resources/Maps/Items/" + self.name + ".txt") as itemsFile: # Récupère et assigne les items pour cette map
                        for line in itemsFile.readlines():
                                data = line.strip().split(',')
                                for item in items: # Retrouve l'items grâce au nom
                                        if item.name == data[0]:
                                                temp = copy.deepcopy(item) # Recrée l'item dans une nouvelle variable afin de pouvoir le modifier sans modifier l'original
                                                temp.rect.move_ip(int(data[1]), int(data[2])) # Change les coordonnées de la copie de l'item aux coordonnées définies
                                                self.items.append(temp)
                                                break
                self.hitboxes = [] # Récupère les hitbox de cette map
                with open("Resources/Maps/Hitboxes/" + self.name + ".txt") as hitboxFile:
                        for line in hitboxFile.readlines():
                                data = line.split(',')
                                self.hitboxes.append(Hitbox((int(data[0]), int(data[1])), (int(data[2]), int(data[3]))))
                self.hitboxes.append(Hitbox((0, -1000), (self.size[0], 1000)))
                self.hitboxes.append(Hitbox((0, self.size[1]), (self.size[0], 1000)))
                self.hitboxes.append(Hitbox((-1000, -1000), (1000, self.size[1] + 2000)))
                self.hitboxes.append(Hitbox((self.size[0], -1000), (1000, self.size[1] + 2000)))

                self.obstacles = [] # Récupère les obstacles de cette map
                with open("Resources/Maps/Obstacles/" + self.name + ".txt") as obstaclesFile: # Récupère les obstacles pour cette map
                        for line in obstaclesFile.readlines():
                                data = line.strip().split(',')
                                for obstacle in obstacles: # Retrouve l'obstacle grâce au nom
                                        if obstacle.name == data[0]:
                                                temp = copy.deepcopy(obstacle) # Recrée l'obstacle dans une nouvelle variable afin de pouvoir le modifier sans modifier l'original
                                                temp.rect.move_ip(int(data[1]), int(data[2])) # Change les coordonnées de la copie de l'obstacle aux coordonnées définies
                                                self.obstacles.append(temp)
                                                self.hitboxes.append(Hitbox((temp.hitbox.rect.left + temp.rect.left, temp.hitbox.rect.top + temp.rect.top), temp.hitbox.rect.size)) # Ajoute aux hitbox de la map celle correspondant à cette obstacle. Les coordonnées sont définie par la hitbox au sein de l'obstacle et par l'emplacement de l'obstacle
                                                break
                self.enemies = [] # Liste des ennemis de cette map
                self.players = [] # Liste des joueurs de la map

        def appendEnemies(self, enemies):
                with open("Resources/Maps/Enemies/" + self.name + ".txt") as enemiesFile:
                        for line in enemiesFile.readlines():
                                data = line.strip().split(',')
                                for enemy in enemies: # Retrouve l'ennemis grâce au nom
                                        if enemy.name == data[0]:
                                                temp = copy.copy(enemy) # Recrée l'ennemis dans une nouvelle variable afin de pouvoir le modifier sans modifier l'original
                                                temp.rect.move_ip(int(data[1]), int(data[2])) # Change les coordonnées de la copie de l'ennemis aux coordonnées définies
                                                temp.fCoords = temp.rect.center
                                                self.enemies.append(temp)
                                                break

        def draw(self, screenRect, widthSmaller, heightSmaller): # Charge la map
                chosenX = 0 # Le côté gauche de la map
                chosenY = 0 # Le côté haut de la map
                chosenXs = screenRect.x # Le côté gauche de l'écran
                chosenYs = screenRect.y # Le côté haut de l'écran
                if widthSmaller: # Si la largeur de la map est inférieure à celle de l'écran
                        chosenX = screenRect.width / 2 - self.size[0] / 2 # Centre la map sur l'écran
                        chosenXs = 0
                if heightSmaller: # Si l'hauteur de la map est inférieure à celle de l'écran
                        chosenY = screenRect.height / 2 - self.size[1] / 2 # Centre la map sur l'écran
                        chosenYs = 0
                self.screen.blit(self.background, (chosenX, chosenY), pygame.Rect((chosenXs, chosenYs), screenRect.size)) # Affiche l'image de la map

        def mod(self, backgroundNumber): # Met à jour l'image de la map sans avoir a créer une nouvelle instance de cette classe
                self.background = pygame.image.load("Resources/Maps/Sprites/" + self.backgroundPath + str(backgroundNumber) + ".png")
                self.screen.blit(self.background, (0, 0))

        def drawObjects(self, objects, screenRect, isTransparent = False, alphaSurface = None): # Calcul les coordonnés écran d'une liste d'objets devant suivre une syntaxe stricte
                if objects: # Vérifie que la liste donnée n'est pas vide
                        for obj in objects: 
                                if screenRect.colliderect(obj.rect): # Sélectionne tout les objets en collision avec le rectangle de l'écran, c'est à dire ceux qui devont être affiché
                                        if isTransparent:
                                                obj.draw((obj.rect.x - screenRect.x, obj.rect.y - screenRect.y), alphaSurface) # Place les objets à déssiner sur leurs emplacements écran
                                        else:
                                                obj.draw((obj.rect.x - screenRect.x, obj.rect.y - screenRect.y), self.screen) # Place les objets à déssiner sur leurs emplacements écran

        def moveEnemies(self):
                for enemy in self.enemies:
                        enemy.move()


class Perso:
        def __init__(self, name, fenetre, speed, maxItems, maxHealth, map):
                self.name = name
                self.fenetre = fenetre
                self.sprite = pygame.image.load("Resources/Persos/Sprites/" + name + ".png").convert_alpha() 
                self.rect = self.sprite.get_rect() # Définis l'image du personnage comme un rectangle
                self.speed = speed # Vitesse de déplacement du personnage selon le choix du joueur
                self.maxItems = maxItems # Taille de l'inventaire 
                self.map = map # Map dans laquelle on se trouve
                self.items = []
                self.health = maxHealth # Met le nombre de points de vie de départ au maximum
                self.maxhealth = maxHealth # Points de vie maximum que le perso peut avoir
                self.ammo = 25 # Le perso a 25 munitions au départ de la partie

        def draw(self, screenRect):
                chosenX = screenRect.w / 2 # Coordonnée X du joueur au centre de l'écran
                chosenY = screenRect.h / 2 # Coordonnée Y du joueur au centre de l'écran

                if screenRect.x <= 0 or screenRect.right == self.map.size[0]: # L'écran se trouve collé contre le bord droit ou gauche
                        chosenX = self.rect.x - screenRect.x # Coordonnée X écran du joueur
                if screenRect.y <= 0 or screenRect.bottom == self.map.size[1]: # L'écran se trouve collé contre le bord haut ou bas
                        chosenY = self.rect.y - screenRect.y # Coordonnée Y écran du joueur
                self.fenetre.blit(self.sprite, (chosenX, chosenY)) # Affiche l'image du personnage aux coordonnées écran

        def mouv(self, action): 
            if action == "haut": 
                self.rect.move_ip(0, -self.speed) # déplace le perso vers le haut 
                if self.rect.collidelist(self.map.hitboxes) != -1: # si le perso se trouve sur un hitbox
                    self.rect.move_ip(0, self.speed) # Ramène le perso à la position précédente
            if action == "bas":
                self.rect.move_ip(0, self.speed) # déplace le perso vers le bas
                if self.rect.collidelist(self.map.hitboxes) != -1:
                    self.rect.move_ip(0, -self.speed)
            if action == "gauche":
                self.rect.move_ip(-self.speed, 0) # déplace le perso vers la gauche
                if self.rect.collidelist(self.map.hitboxes) != -1:
                    self.rect.move_ip(self.speed, 0)
            if action == "droite":
                self.rect.move_ip(self.speed, 0) # déplace le perso vers la droite
                if self.rect.collidelist(self.map.hitboxes) != -1:
                    self.rect.move_ip(-self.speed, 0)
            if action=="ramasser": 
                if len(self.items) <= self.maxItems: # Vérifie que le perso a encore de la place dans son inventaire
                                for item in self.map.items: # Cherche dans la liste d'items de cette map
                                        if self.rect.colliderect(item.rect): # Vérifie si le perso se trouve sur un item
                                                if item.type == "HEALTH": #verifie que l'item est du type santé
                                                        if self.health < self.maxhealth : #vérifie que le perso n'est pas au max de sa vie
                                                                self.health = self.health + item.value #ajoute la valeur de l'item santé à la santé du perso
                                                                if self.health >= self.maxhealth :  # verifie si le niveau de santé ajouté dépasse la valeur maximale de santé
                                                                        self.health = self.maxhealth    #ramène le niveau de santé au maximum
                                                elif item.type == "AMMO":
                                                        self.ammo = self.ammo + item.value
                                                elif item.type == "WEAPON":
                                                    self.items.append(item) # Ajoute l'item à l'inventaire du perso

                                                self.map.items.remove(item) # Enlève l'item de la map
                                                break # Sort de la boucle
       

class PathFinder:
        def __init__(self, hitboxes, precision):
                self.start = None
                self.finish = None
                self.hitboxes = hitboxes
                self.precision = precision
                self.nodes = []
                self.path = []

        def nodeInHitbox(self, rect):
                if rect.collidelistall(self.hitboxes):
                                return True
                return False

        def addNeighbourNodes(self, node):
                # Vérifie que la node à la droite n'existe pas déja
                nextNodeCoords = (node.rect.x + node.rect.width, node.rect.y)
                if not [x for x in self.nodes if nextNodeCoords == x.rect.topleft] and not self.nodeInHitbox(pygame.Rect(nextNodeCoords, (node.rect.width, node.rect.height))): 
                        # Ajoute la node de droite si elle n'existe pas déja
                        self.nodes.append(Node(len(self.nodes), nextNodeCoords, node.rect.width, node, 1, self.start, self.finish))

                # Vérifie que la node à la gauche n'existe pas déja
                nextNodeCoords = (node.rect.x - node.rect.width, node.rect.y)
                if not [x for x in self.nodes if nextNodeCoords == x.rect.topleft] and not self.nodeInHitbox(pygame.Rect(nextNodeCoords, (node.rect.width, node.rect.height))): 
                        # Ajoute la node de gauche si elle n'existe pas déja
                        self.nodes.append(Node(len(self.nodes), nextNodeCoords, node.rect.width, node, 1, self.start, self.finish))

                # Vérifie que la node au dessus n'existe pas déja
                nextNodeCoords = (node.rect.x, node.rect.y - node.rect.width)
                if not [x for x in self.nodes if nextNodeCoords == x.rect.topleft] and not self.nodeInHitbox(pygame.Rect(nextNodeCoords, (node.rect.width, node.rect.height))): 
                        # Ajoute la node au dessus si elle n'existe pas déja
                        self.nodes.append(Node(len(self.nodes), nextNodeCoords, node.rect.width, node, 1, self.start, self.finish))

                # Vérifie que la node en dessous n'existe pas déja
                nextNodeCoords = (node.rect.x, node.rect.y + node.rect.width)
                if not [x for x in self.nodes if nextNodeCoords == x.rect.topleft] and not self.nodeInHitbox(pygame.Rect(nextNodeCoords, (node.rect.width, node.rect.height))): 
                        # Ajoute la node en dessous si elle n'existe pas déja
                        self.nodes.append(Node(len(self.nodes), nextNodeCoords, node.rect.width, node, 1, self.start, self.finish))

                # Vérifie que la node à la droite en haut n'existe pas déja
                nextNodeCoords = (node.rect.x + node.rect.width, node.rect.y - node.rect.width)
                if not [x for x in self.nodes if nextNodeCoords == x.rect.topleft] and not self.nodeInHitbox(pygame.Rect(nextNodeCoords, (node.rect.width, node.rect.height))): 
                        # Ajoute la node à la droite en haut si elle n'existe pas déja
                        self.nodes.append(Node(len(self.nodes), nextNodeCoords, node.rect.width, node, 1, self.start, self.finish))

                # Vérifie que la node à la droite en bas n'existe pas déja
                nextNodeCoords = (node.rect.x + node.rect.width, node.rect.y + node.rect.width)
                if not [x for x in self.nodes if nextNodeCoords == x.rect.topleft] and not self.nodeInHitbox(pygame.Rect(nextNodeCoords, (node.rect.width, node.rect.height))): 
                        # Ajoute la node à la droite en bas si elle n'existe pas déja
                        self.nodes.append(Node(len(self.nodes), nextNodeCoords, node.rect.width, node, 1, self.start, self.finish))

                # Vérifie que la node à la gauche en haut n'existe pas déja
                nextNodeCoords = (node.rect.x - node.rect.width, node.rect.y - node.rect.width)
                if not [x for x in self.nodes if nextNodeCoords == x.rect.topleft] and not self.nodeInHitbox(pygame.Rect(nextNodeCoords, (node.rect.width, node.rect.height))): 
                        # Ajoute la node à la gauche en haut si elle n'existe pas déja
                        self.nodes.append(Node(len(self.nodes), nextNodeCoords, node.rect.width, node, 1, self.start, self.finish))

                # Vérifie que la node à la gauche en bas n'existe pas déja
                nextNodeCoords = (node.rect.x - node.rect.width, node.rect.y + node.rect.width)
                if not [x for x in self.nodes if nextNodeCoords == x.rect.topleft] and not self.nodeInHitbox(pygame.Rect(nextNodeCoords, (node.rect.width, node.rect.height))): 
                        # Ajoute la node à la gauche en bas si elle n'existe pas déja
                        self.nodes.append(Node(len(self.nodes), nextNodeCoords, node.rect.width, node, 1, self.start, self.finish))

                node.state = 2
                
        def closestNode(self):
                smallestLTlist = []
                for node in list(filter(lambda x: x.state == 1, self.nodes)):
                        if smallestLTlist:
                                if node.totalLength < smallestLTlist[0].totalLength:
                                        smallestLTlist = [node]
                                elif node.totalLength == smallestLTlist[0].totalLength:
                                        smallestLTlist.append(node)
                        else:
                                smallestLTlist.append(node)
                if len(smallestLTlist) > 1:
                        smallestELlist = []
                        for node in smallestLTlist:
                                if smallestELlist:
                                        if node.endLength < smallestELlist[0].endLength:
                                                smallestELlist = [node]
                                        elif node.endLength == smallestELlist[0].endLength:
                                                smallestELlist.append(node)
                                else:
                                        smallestELlist.append(node)
                        return smallestELlist[0]
                else:
                        return smallestLTlist[0]
        
        def findBest(self, start, finish):
                self.start = start
                self.finish = finish
                self.path = []
                self.nodes = [Node(0, (self.start[0] - self.precision / 2, self.start[1] - self.precision / 2), self.precision, None, 1, self.start, finish)]

                while not [x for x in self.nodes if x.rect.colliderect(pygame.Rect(self.finish[0] - self.precision / 2, self.finish[1] - self.precision / 2, self.precision, self.precision))] and len(self.nodes) < 200:
                        closest = self.closestNode()
                        self.addNeighbourNodes(closest)
                current_node = self.closestNode()
                while current_node.number != 0:
                        self.path.append(current_node)
                        current_node = current_node.parent
                return self.path.reverse()     

        def drawPath(self, screen, screenCoords):
                if self.path:
                        lastNode = None
                        for node in self.path:
                                pygame.draw.circle(screen, pygame.Color("red"), (node.rect.center[0] - screenCoords[0], node.rect.center[1] - screenCoords[1]), 10)
                                if lastNode:
                                        pygame.draw.line(screen, pygame.Color("red"), (node.rect.center[0] - screenCoords[0], node.rect.center[1] - screenCoords[1]), (lastNode.rect.center[0] - screenCoords[0], lastNode.rect.center[1] - screenCoords[1]), 5)
                                lastNode = node
                        pygame.draw.line(screen, pygame.Color("red"), (lastNode.rect.center[0] - screenCoords[0], lastNode.rect.center[1] - screenCoords[1]), (self.finish[0] - screenCoords[0], self.finish[1] - screenCoords[1]), 5)
                        pygame.draw.circle(screen, pygame.Color("yellow"), (self.finish[0] - screenCoords[0], self.finish[1] - screenCoords[1]), 5)


class Node:
        def __init__(self, number, coords, precision, parent, state, startPoint, endPoint):
                self.number = number
                self.rect = pygame.Rect(coords, (precision, precision))
                self.parent = parent # Node parent
                self.state = state # Etat du node. 1: à analyser        2: déjà analysé
                self.startLength = math.sqrt(pow(startPoint[0] - self.rect.centerx, 2) + pow(startPoint[1] - self.rect.centery, 2))
                self.endLength = math.sqrt(pow(endPoint[0] - self.rect.centerx, 2) + pow(endPoint[1] - self.rect.centery, 2))
                self.totalLength = self.startLength + self.endLength

        def draw(self, coords, screen):
                if self.number == 0:
                        chosenColor = pygame.Color(244, 238, 65, 127)
                elif self.state == 2:
                        chosenColor = pygame.Color(107, 244, 66, 127)
                elif self.state == 1:
                        chosenColor = pygame.Color(65, 244, 241, 127)

                pygame.draw.rect(screen, chosenColor, pygame.Rect(coords, (self.rect.width, self.rect.height)))


class Bullet :
         def __init__(self, map, perso, screen, screenRect):
             screenMouseCoords = pygame.mouse.get_pos() #on obtient les coordonées de la souris

             realMouseCoords = screenMouseCoords + screenRect.topleft #on obtient les coordonnées réelles du curseur (pas dans le repère de la map)
             bulletSpeed = perso.items[0].characteristics.speed   #on défini un coefficient de vitesse pour la balle
             direction = ((realMouseCoords.x - perso.rect.center.x, realMouseCoords.y)*bulletSpeed - (perso.rect.center.y)*bulletSpeed) #on défini des composantes de direction pour la balle
             self.rect = rect(perso.center,(1, 1))   #on défini le rectangle lié à la balle
             while not self.rect.collidelist(map.hitboxes):    #on vérifie que la balle ne collisionne pas d'hitboxes
                    pygame.self.rect.move_ip(direction[0], direction[1])  #on donne la trajectoire à la balle


class Bouton:
        def __init__(self,coords,text,size,screen):
                self.rect=pygame.Rect(coords,size)
                self.coords=coords
                self.size=size
                self.screen=screen
                self.text=text
                
        def draw(self):
                pygame.draw.rect(self.screen,pygame.Color(255,0,0), pygame.Rect(self.coords[0], self.coords[1], self.rect.size[0],self.rect.size[1]))
                font=pygame.font.SysFont("Times New Roman",50,bold=False,italic=False) 
                texte=font.render(self.text,1,(0,0,0))
                self.screen.blit(texte,(self.coords[0]+30,self.coords[1]+30))




