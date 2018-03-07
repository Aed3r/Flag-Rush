import pygame

class Map:
        def __init__(self, baseScreen, backgroundPath, spawnCoords, objectifCoords):
                self.baseScreen = baseScreen
                self.backgroundPath = backgroundPath
                self.spawnCoords = spawnCoords
                self.background = None
                self.objectifCoords = objectifCoords

        def load(self):
                self.background = pygame.image.load("Resources/Maps/" + self.backgroundPath + ".png")
                backgroundSize = self.background.get_rect().size
                self.baseScreen = pygame.display.set_mode(backgroundSize)
                self.baseScreen.blit(self.background, (0, 0))
                pygame.display.flip()
        
        def mod(self, backgroundNumber):
                self.background = pygame.image.load("Resources/Maps/" + self.backgroundPath + str(backgroundNumber) + ".png")
                self.baseScreen.blit(self.background, (0, 0))
                pygame.display.flip()

        def getSpawn(self):
                return self.spawnCoords

        def setSpawn(self, spawnCoords):
                self.spawnCoords = spawnCoords

        def getObjectif(self):
                return self.objectifCoords

        def setObjectif(self, objectifCoords):
                self.objectifCoords = objectifCoords

class Perso:
        def __init__(self,fenetre,image,perso_x,perso_y):
                self.fenetre=fenetre
                self.image=image
                self.perso_x = perso_x
                self.perso_y = perso_y
                
        def charge(self):
                self.image=pygame.image.load("Resources/Persos/"+ self.image+".png")
                self.fenetre.blit(self.image, (self.perso_x,self.perso_y))
                pygame.display.flip()

        def mouv(self, event, carte):
                if event.type == pygame.K_z:
                        self.perso_x += 3
                        self.fenetre.blit(self.image, (self.perso_x,self.perso_y))
                        pygame.display.flip()
                if event.type == pygame.K_s:
                        self.perso_x-=3
                        self.fenetre.blit(self.image, (self.perso_x,self.perso_y))
                        pygame.display.flip()
                if event.type == pygame.K_q:
                        self.perso_y+=3 
                        self.fenetre.blit(self.image, (self.perso_x,self.perso_y))
                        pygame.display.flip()
                if event.type == pygame.K_d:
                        self.perso_y-=3
                        self.fenetre.blit(self.image, (self.perso_x,self.perso_y))
                        pygame.display.flip()
                if event.type == pygame.MOUSEBUTTONUP:
                        carte.mod(2)

        
        




        
        

                


        

                
        

                



                
                        

