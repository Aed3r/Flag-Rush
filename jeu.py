import pygame
import utilities as ut

pygame.init()
screenSize = width, height = 1000, 1000
screen = pygame.display.set_mode(screenSize)

Green = ut.Map(screen, "Green", (0, 0))
Green.load()

backIndex = 0

done = False
while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
                elif event.type == pygame.MOUSEMOTION:
                        backIndex += 1
                        if backIndex == 3:
                                Green.load()
                                backIndex = 0
                        else:
                                Green.mod(backIndex)
        
        pygame.display.flip()

        
