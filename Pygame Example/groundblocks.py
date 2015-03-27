import pygame
from easypg import colours

class Platform(pygame.sprite.Sprite):
    """Basic platform for player to jump on"""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32, 32))
        self.image.convert()
        self.image.fill(colours.RED)
        self.rect = pygame.rect.Rect(x, y, 32, 32)

class BACK1(pygame.sprite.Sprite):
    """Background image for level 1"""
    image = pygame.image.load("level1background.bmp")
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = BACK1.image
        self.image.convert()
        self.rect = pygame.rect.Rect(x, y, 32, 32)
        
class BACK2(pygame.sprite.Sprite):
    """Background image for level 2"""
    image = pygame.image.load("level2background.bmp")
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = BACK2.image
        self.image.convert()
        self.rect = pygame.rect.Rect(x, y, 32, 32)
        
class BACK3(pygame.sprite.Sprite):
    """Background image for level 3"""
    image = pygame.image.load("level3background.bmp")
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = BACK3.image
        self.image.convert()
        self.rect = pygame.rect.Rect(x, y, 32, 32)
