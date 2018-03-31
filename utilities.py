import pygame
import copy

class Item: # Définis un objet pouvant être utilisé par le joueur
        def __init__(self, name, type, value, characteristics = None):
                self.name = name
                self.sprite = pygame.image.load("Resources/Items/Sprites/" + self.name + ".png")
                self.type = type # Une des options définis par le enum ItemTypes
                self.value = value # La puissance de l'arme, le nombre de points de vies rétablies...
                self.rect = self.sprite.get_rect() # Les coordonnées et la taille de l'item. La taille est définis par la taille du sprite de l'item
                if type == "WEAPON": # Si l'item est du type 'Weapon', charger d'autres caractéristiques
                        self.characteristics = characteristics

        def draw(self, coords, screen):
                screen.blit(self.sprite, coords)


class Weapon: # Classe auxiliaire pour définir les caractéristiques d'une arme
        def __init__(self, aim = 95, speed = 20, isExplosive = False):
                self.aim = aim # La précision de tir en pourcentage. 100% correspond à une ligne droite
                self.speed = speed # La vitesse du projectile
                self.isExplosive = isExplosive # Définis si le projectile explose sur impact (ce qui fait des dégats plus répandus)


class Map: # Définis une carte jouable
        def __init__(self, name, screen, objectifCoords, items, spawnCoords = (0, 0)):
                self.name = name
                self.screen = screen # La fenètre principale
                self.background = pygame.image.load("Resources/Maps/Sprites/" + self.name + ".png").convert() # Charge l'image de fond d'écran
                self.size = self.background.get_size() # Définis la taille de la map à partir de l'image de fond d'écran
                self.spawnCoords = spawnCoords # Où le joueur apparait en début de partie
                self.objectifCoords = objectifCoords # Où se trouve l'objectif à atteindre
                self.mapItems = [] # Dictionnaire de tous les items de la map. Clés: coordonnées de l'objet, Valeur: instance de le classe Item définissant l'objet en question
                with open("Resources/Maps/Items/" + self.name + ".txt") as mapItemsFile: # Récupère et assigne les items pour cette map
                        for line in mapItemsFile.readlines():
                                data = line.strip().split(',')
                                for item in items: # Retrouve l'items grâce au nom
                                        if item.name == data[0]:
                                                temp = copy.copy(item) # Recrée l'item dans une nouvelle variable afin de pouvoir le modifier sans modifier l'original
                                                temp.rect = temp.rect.move(int(data[1]), int(data[2])) # Change les coordonnées de la copie de l'item aux coordonnées définies
                                                self.mapItems.append(temp)
                                                break
                self.mapObstacles = [] # Récupère les obstacles de cette map
                with open("Resources/Maps/Obstacles/" + self.name + ".txt") as obstacleFile:
                        for line in obstacleFile.readlines():
                                data = line.split(',')
                                self.mapObstacles.append(Obstacle(int(data[0]), int(data[1]), (int(data[2]), int(data[3]))))


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

        def drawObjects(self, objects, screenRect): # Calcul les coordonnés écran d'une liste d'objets devant suivre une syntaxe stricte
                if objects: # Vérifie que la liste donnée n'est pas vide
                        for obj in objects: 
                                if screenRect.colliderect(obj.rect): # Sélectionne tout les objets en collision avec le rectangle de l'écran, c'est à dire ceux qui devont être affiché
                                        obj.draw((obj.rect.x - screenRect.x, obj.rect.y - screenRect.y), self.screen) # Place les objets à déssiner sur leurs emplacements écran
                        
        def drawObstacles(self, screenRect): # Pour déssiner les obstacles
                self.drawObjects(self.mapObstacles, screenRect)

        def drawItems(self, screenRect): # Pour déssiner les items
                self.drawObjects(self.mapItems, screenRect)


class Perso:
        def __init__(self, name, fenetre, speed, maxItems, map, maxHealth):
                self.name = name
                self.fenetre = fenetre
                self.sprite = pygame.image.load("Resources/Persos/Sprites/" + name + ".png").convert_alpha() 
                self.rect = self.sprite.get_rect() # Définis l'image du personnage comme un rectangle
                self.rect = self.rect.move(map.spawnCoords) # Récupère les coordonnées de spawn du perso
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
                self.rect = self.rect.move(0, -self.speed) # déplace le perso vers le haut 
                if self.rect.collidelist(self.map.mapObstacles) != -1 or self.rect.y < 0: # si le perso se trouve sur un obstacle
                    self.rect = self.rect.move(0, self.speed) # Ramène le perso à la position précédente
            if action == "bas":
                self.rect=self.rect.move(0, self.speed) # déplace le perso vers le bas
                if self.rect.collidelist(self.map.mapObstacles) != -1 or self.rect.bottom > self.map.size[1]:
                    self.rect = self.rect.move(0, -self.speed)
            if action == "gauche":
                self.rect = self.rect.move(-self.speed, 0) # déplace le perso vers la gauche
                if self.rect.collidelist(self.map.mapObstacles) != -1 or self.rect.x < 0:
                    self.rect = self.rect.move(self.speed, 0)
            if action == "droite":
                self.rect = self.rect.move(self.speed, 0) # déplace le perso vers la droite
                if self.rect.collidelist(self.map.mapObstacles) != -1 or self.rect.right > self.map.size[0]:
                    self.rect=self.rect.move(-self.speed, 0)
            if action=="ramasser": 
                if len(self.items) <= self.maxItems: # Vérifie que le perso a encore de la place dans son inventaire
                                for item in self.map.mapItems: # Cherche dans la liste d'items de cette map
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

                                                self.map.mapItems.remove(item) # Enlève l'item de la map
                                                break # Sort de la boucle


class Bullet :
         def __init__(self, x, y, map, perso, screen):
             realMouseCoords = pygame.mouse.get_pos()
             screenPos = (perso.rect.x - (screen.width)/2, perso.rect.y - (screen.height)/2)
             screenMouseCoords = realMouseCoords + screenPos
             #self.direction =
             self.rect = rect(x, y, 1, 1)
             while not self.rect.collidelist(map.mapObstacles) and not self.rect.colliderect(perso.rect):
                    pygame.self.rect.move(self.rect.x + dircetion[0], self.rect.y + direction[1])


class Obstacle:
        def __init__(self, width, length, coords):
                self.rect = pygame.Rect(coords[0],coords[1], width, length)

        def draw(self, coords, screen):
                pygame.draw.rect(screen, pygame.Color(191, 63, 63), pygame.Rect(coords[0], coords[1], self.rect.w, self.rect.h))


























