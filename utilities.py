import pygame

class Item: # Définis un objet pouvant être utilisé par le joueur
        def __init__(self, name, type, value, characteristics = None):
                self.name = name
                self.sprite = pygame.image.load("Resources/Items/Sprites/" + self.name + ".png")
                self.type = type # Une des options définis par le enum ItemTypes
                self.value = value # La puissance de l'arme, le nombre de points de vies rétablies...
                if type == "WEAPON":
                        self.characteristics = characteristics

class Weapon: # Classe auxiliaire pour définir les caractéristiques d'une arme
        def __init__(self, aim = 95, speed = 20, isExplosive = False):
                self.aim = aim # La précision de tir en pourcentage. 100% correspond à une ligne droite
                self.speed = speed # La vitesse du projectile
                self.isExplosive = isExplosive # Définis si le projectile explose sur impact (ce qui fait des dégats plus répandus)

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
                self.rect = self.image.get_rect() # Définis l'image du personnage comme un rectangle
                self.rect = self.rect.move(map.spawnCoords) # Récupère les coordonnées de spawn du perso
                self.speed = speed # Vitesse de déplacement du personnage selon le choix du joueur
                self.maxItems = maxItems # Taille de l'inventaire 
                self.map = map # Map dans laquelle on se trouve
                self.items = []
                self.health = maxHealth # Met le nombre de points de vie de départ au maximum
                self.maxhealth = maxHealth # Points de vie maximum que le perso peut avoir
                self.ammo = 25 # Le perso a 25 munitions au départ de la partie

        def load(self):
                self.fenetre.blit(self.image, self.rect) # Affiche l'image du personnage au niveau du point de spawn

        def mouv(self,action): 
            if action == "haut": 
                self.rect=self.rect.move(0,-self.speed) # déplace le perso vers le haut 
                if self.rect.collidelist(self.map.mapObstacles) != -1: # si le perso se trouve sur un obstacle
                    self.rect=self.rect.move(0,self.speed) # Ramène le perso à la position précédente
            if action=="bas":
                self.rect=self.rect.move(0,self.speed) # déplace le perso vers le bas
                if self.rect.collidelist(self.map.mapObstacles) != -1:
                    self.rect=self.rect.move(0,-self.speed)
            if action=="gauche":
                self.rect=self.rect.move(-self.speed,0) # déplace le perso vers la gauche
                if self.rect.collidelist(self.map.mapObstacles) != -1:
                    self.rect=self.rect.move(self.speed, 0)
            if action=="droite":
                self.rect=self.rect.move(self.speed,0) # déplace le perso vers la droite
                if self.rect.collidelist(self.map.mapObstacles) != -1:
                    self.rect=self.rect.move(-self.speed, 0)
            if action=="ramasser": 
                if len(self.items) <= self.maxItems: # Vérifie que le perso a encore de la place dans son inventaire
                                for k, v in self.map.mapItems.items(): # Cherche dans la liste d'items de cette map (k: coordonnées, v: item)
                                        itemRect = v.sprite.get_rect().move(k)
                                        if self.rect.colliderect(itemRect): # Vérifie si le perso se trouve sur un item
                                                if v.type == "HEALTH" : #verifie que l'item est du type santé
                                                        if self.health < self.maxhealth : #vérifie que le perso n'est pas au max de sa vie
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
         def __init__(self, x, y, map, perso, screen):
             realMouseCoords = pygame.mouse.get_pos()
             screenPos = (perso.rect.x - (screen.width)/2, perso.rect.y - (screen.height)/2)
             screenMouseCoords = realMouseCoords + screenPos
             self.direction =
             self.rect = rect(x, y, 1, 1)
             while not self.rect.collidelist(map.mapObstacles) and not self.rect.colliderect(perso.rect):
                    pygame.self.rect.move(self.rect.x + dircetion[0], self.rect.y + direction[1])

        


class Obstacle:
        def __init__(self, length, width, coords = (0,0)) :
                self.rect = pygame.Rect(coords[0],coords[1], width, length)

        def load(self, screen):
                pygame.draw.rect(screen, pygame.Color(255, 255, 255, 100), self.rect)


























