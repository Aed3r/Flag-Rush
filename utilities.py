import pygame

class Map:
        def __init__(self, baseScreen, backgroundPath, spawnCoords):
                self.baseScreen = baseScreen
                self.backgroundPath = backgroundPath
                self.spawnCoords = spawnCoords
                self.background = None

        def load(self):
                self.background = pygame.image.load("Resources/Maps/" + self.backgroundPath + ".png")
                backgroundSize = self.background.get_rect().size
                self.baseScreen = pygame.display.set_mode(backgroundSize)
                self.baseScreen.blit(self.background, (0, 0))
        
        def mod(self, backgroundNumber):
                self.background = pygame.image.load("Resources/Maps/" + self.backgroundPath + str(backgroundNumber) + ".png")
                self.baseScreen.blit(self.background, (0, 0))

        def getSpawn(self):
                return self.spawnCoords

        def setSpawn(self, spawnCoords):
                self.spawnCoords = spawnCoords

class Perso:
        def__init__(self,fenetre,image,coords):
                        self.fenetre=fenetre
                        self.image=image
                        self.coords=coords
                
        def charge(self):
                self.image=pygame.image.load("Resources/Persos/"+ self.image+".png")
                self.fenetre.blit(self.image, (self.coords))


                
                        

