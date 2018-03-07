import pygame
import utilities as ut

pygame.init()
screenSize = width, height = 1000, 1000
screen = pygame.display.set_mode(screenSize)

Green = ut.Map(screen, "Green", (0, 0))
Green.load()

perso=ut.Perso(screen, "hero_spritesheet",500,500)
perso.charge()

done=False
while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
                else:
                        perso.mouv(event)
                
                pygame.display.flip()        

                        
        
        

        
