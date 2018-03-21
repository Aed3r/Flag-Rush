import pygame

class Item: # Définis un objet pouvant être utilisé par le joueur
        def __init__(self, name, type, value):
                self.name = name
                self.sprite = pygame.image.load("Resources/Items/Sprites/" + self.name + ".png")
                self.type = type # Une des options définis par le enum ItemTypes
                self.value = value # La puissance de l'arme, le nombre de points de vies rétablies...

class Weapon: # Classe auxiliaire pour définir les caractéristiques d'une arme
        def __init__(self, aim = 95, speed = 20, isExplosive = False, power = 1):
                self.aim = aim # La précision de tir en pourcentage. 100% correspond à une ligne droite
                self.speed = speed # La vitesse de la balle 
                self.isExplosive = isExplosive # Définis si le projectile explose sur impact (ce qui fait des dégats plus répandus)
                self.power = power # La puissance du projectile. Correspond au nombre d'ennemis qu'elle peut traverser

class Map: # Définis une carte jouable
        def __init__(self, name, baseScreen, objectifCoords, items, spawnCoords = (0, 0)):
                self.name = name
                self.baseScreen = baseScreen # La fenètre principale
                self.background = pygame.image.load("Resources/Maps/Sprites/" + self.name + ".png")
                backgroundSize = self.background.get_rect().size # Récupère la taille de l'image de la map
                self.baseScreen = pygame.display.set_mode(backgroundSize) # Définis la taille de la fenètre par rapport à la map
                self.spawnCoords = spawnCoords # Où le joueur apparait en début de partie
                self.objectifCoords = objectifCoords # Où se trouve l'objectif à atteindre
                self.mapItems = {} # Dictionnaire de tous les items de la map. Clés: coordonnées de l'objet, Valeur: instance de le classe Item définissant l'objet en question
                with open("Resources/Maps/Data/" + self.name + ".txt") as mapItemsFile: # Récupère et assigne les items pour cette map
                        for line in mapItemsFile.readlines():
                                data = line.strip().split(',')
                                for item in items: # Retrouve l'items grâce au nom
                                        if item.name == data[0]:
                                                self.mapItems[(int(data[1]), int(data[2]))] = item # dictionary[key] = value
                self.mapObstacles = []
                with open("Resources/Maps/Obstacles/" + self.name + ".txt") as obstacleFile:
                        for line in obstacleFile.readlines():
                                data = line.split(',')
                                self.mapObstacles.append(Obstacle(int(data[0]), int(data[1]), (int(data[2]), int(data[3]))))


        def load(self): # Charge la map
                self.baseScreen.blit(self.background, (0, 0)) # Affiche l'image de la map
                for k, v in self.mapItems.items(): # Itère le dictionnaire des items présents sur cette map
                         self.baseScreen.blit(v.sprite, k) # Affiche l'image de l'items aux coordonées définies

        def mod(self, backgroundNumber): # Met à jour l'image de la map sans avoir a créer une nouvelle instance de cette classe
                self.background = pygame.image.load("Resources/Maps/Sprites/" + self.backgroundPath + str(backgroundNumber) + ".png")
                self.baseScreen.blit(self.background, (0, 0))

class Perso:
        def __init__(self, name, fenetre, speed, maxItems, map, maxHealth):
                self.name = name
                self.fenetre = fenetre
                self.image = pygame.image.load("Resources/Persos/" + name + ".png").convert_alpha()
                self.rect = self.image.get_rect()
                self.rect = self.rect.move(map.spawnCoords)
                self.speed = speed
                self.maxItems = maxItems
                self.map = map
                self.items = []
                self.health = maxHealth
                self.maxhealth = maxHealth
                self.ammo = 0

        def load(self):
                self.fenetre.blit(self.image, self.rect)

        def mouv(self,action):
            if action == "haut":
                self.rect=self.rect.move(0,-self.speed)
                if self.rect.collidelist(self.map.mapObstacles) != -1:
                    self.rect=self.rect.move(0,self.speed)
            if action=="bas":
                self.rect=self.rect.move(0,self.speed)
                if self.rect.collidelist(self.map.mapObstacles) != -1:
                    self.rect=self.rect.move(0,-self.speed)
            if action=="gauche":
                self.rect=self.rect.move(-self.speed,0)
                if self.rect.collidelist(self.map.mapObstacles) != -1:
                    self.rect=self.rect.move(self.speed, 0)
            if action=="droite":
                self.rect=self.rect.move(self.speed,0)
                if self.rect.collidelist(self.map.mapObstacles) != -1:
                    self.rect=self.rect.move(-self.speed, 0)
            if action=="ramasser":
                if len(self.items) <= self.maxItems: # Vérifie que le perso a encore de la place dans son inventaire
                                for k, v in self.map.mapItems.items(): # Cherche dans la liste d'items de cette map (k: coordonnées, v: item)
                                        itemRect = v.sprite.get_rect().move(k)
                                        if self.rect.colliderect(itemRect): # Vérifie si le perso se trouve sur un item
                                                if v.type == "HEALTH" : #verifie que l'item est du type santé
                                                        if self.health <= self.maxhealth : #vérifie que le perso n'est pas au max de sa vie
                                                                self.health = self.health + v.value #ajoute la valeur de l'item santé à la santé du perso
                                                                if self.health >= self.maxhealth :  # verifie si le niveau de santé ajouté dépasse la valeur maximale de santé
                                                                        self.health = self.maxhealth    #ramène le niveau de santé au maximum
                                                elif v.type == "AMMO" :
                                                        self.ammo = self.ammo + v.value
                                                elif v.type == "WEAPON" :
                                                    self.items.append(v) # Ajoute l'item à l'inventaire du perso

                                                del self.map.mapItems[k] # Enlève l'item de la map
                                                break # Sort de la boucle, sinon crash car dictionnaire modifié

class Bullet :
         def __init__(self, coords, direction, map, perso):
             self.direction = direction
             self.rect = rect(coords[0],coords[1], 1, 1)
             while not self.rect.collidelist(map.mapObstacles) and not self.rect.colliderect(perso.rect):
                    pygame.rect.move(direction[0], direction[1])

class Obstacle:
        def __init__(self, length, width, coords = (0,0)) :
                self.rect = pygame.Rect(coords[0],coords[1], width, length)

        def load(self, screen):
                pygame.draw.rect(screen, pygame.Color(255, 255, 255, 100), self.rect)


























