import pygame
from easypg import colours

class Fallblock(pygame.sprite.Sprite):
    """Detect whether a player has fallen off screen"""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32, 32))
        self.image.convert()
        self.image.fill(colours.AQUA)
        self.rect = pygame.rect.Rect(x, y, 32, 32)
        
    def update(self):
        pass

class Jumppad(pygame.sprite.Sprite):
    """Jumppad blocks shoot player up in the air when stood on top of"""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32, 32))
        self.image.convert()
        self.image.fill(colours.MAROON)
        self.rect = pygame.rect.Rect(x, y, 32, 32)
        
    def update(self):
        pass        

class Collectible(pygame.sprite.Sprite):
    """Collectibles increase in game score when collected"""
    image = pygame.image.load("coin.png") 
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = Collectible.image
        self.image.convert()
        self.rect = pygame.rect.Rect(x, y, 24, 24)


    def update(self):
        pass
    
class Heart(pygame.sprite.Sprite):
    """Collectibles increase in game score when collected"""
    image = pygame.image.load("heart.png") 
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = Heart.image
        self.image.convert()
        self.rect = pygame.rect.Rect(x, y, 24, 24)
        
    def update(self):
        pass
    
class Exit_door(pygame.sprite.Sprite):
    """Door which player can step in to complete the level"""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32, 64))
        self.image.convert()
        self.image.fill(colours.BLACK)
        self.rect = pygame.rect.Rect(x, y, 32, 64)

    def update(self):
        pass

class Spike(pygame.sprite.Sprite):
    """Detect whether a player has fallen off screen"""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32, 32))
        self.image.convert()
        self.image.fill(colours.GREY)
        self.rect = pygame.rect.Rect(x, y, 32, 32)
        
    def update(self):
        pass
