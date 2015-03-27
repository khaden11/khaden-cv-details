import pygame
from easypg import colours
from easypg.sprites import Sprite

#screen variables used in camera settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
HALF_WIDTH = int(SCREEN_WIDTH / 2)
HALF_HEIGHT = int(SCREEN_HEIGHT / 2)

SIZE = [SCREEN_WIDTH,SCREEN_HEIGHT]
screen = pygame.display.set_mode(SIZE)


class PLAYER(Sprite):
    """Player class detects movement of player, collisions and animation
    states the player should be in"""
    images = {}
    def __init__(self, x, y):
        #http://www.vg-resource.com/archive/index.php?thread-23452-8.html
        #This is where the character spritesheet is to find
        super().__init__(screen, 'GAMECHARTRIAL.zip', state = 'stand')
        self.vx = 0
        self.vy = 0
        self.onGround = False
        self.rect.center = (x,y)
        #initialise self.death variables to be used in game
        self.falldeath = False
        self.playerdeath = False
        #initiate variables to count killed enemies/coins collected to
        # add to score
        self.enemieskilled = 0
        self.collected = 0
        self.extralives = 0
        #variable is set to true when player enters exit door
        self.levelcomplete = False
        #variable for bouncing on jumppad
        self.bounce = False

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, up, down, left, right, platforms, fallblocks, fallsound,\
               jumppads, boing, collectibles, ding, enemies, enemydeath_sound, \
               exitdoor, allsprites, heartlist):
        """Update is passed all information from running game to see what
        the player update should do"""
        #the following logic detects different states of the player - whether
        #on ground, jumping, moving left or right etc and sets the animated
        #state accordingly
        if up:
            #only jump if on the ground
            if self.onGround:
                self.vy -= 11
                if self.state == 'walk':
                    self.state = 'jumpr'
                    self.sequence = self.images[self.state][self.direction]
                if self.state == 'walkl':
                    self.state = 'jumpl'
                    self.sequence = self.images[self.state][self.direction]
                if self.state == 'stand':
                    self.state = 'jumpr'
                    self.sequence = self.images[self.state][self.direction]
                if self.state == 'standl':
                    self.state = 'jumpl'
                    self.sequence = self.images[self.state][self.direction]                    
                self.onGround = False
        if left and self.state == 'jumpr':
            self.state = 'jumpl'
            self.sequence = self.images[self.state][self.direction]            
        if right and self.state == 'jumpl':
            self.state = 'jumpr'
            self.sequence = self.images[self.state][self.direction]
        if up and right:
            self.state = 'jumpr'
            self.sequence = self.images[self.state][self.direction]
        if self.onGround and self.state == 'jumpl':
            self.state = 'standl'
            self.sequence = self.images[self.state][self.direction]
        if self.onGround and self.state == 'jumpr':
            self.state = 'stand'
            self.sequence = self.images[self.state][self.direction]
        if down:
            pass
        if left and self.onGround:
            self.state = 'walkl'
            self.sequence = self.images[self.state][self.direction]
        if left:
            self.vx = -8
        if right and self.onGround:
            self.state = 'walk'
            self.sequence = self.images[self.state][self.direction]
        if right:
            self.vx = 8
        if not(left or right):
            if self.state == 'walk':
                self.state = 'stand'
                self.sequence = self.images[self.state][self.direction]
            if self.state == 'walkl':
                self.state = 'standl'
                self.sequence = self.images[self.state][self.direction]
        if self.bounce:
            if self.state == 'stand' or self.state == 'walk' or \
               self.state == 'jumpr':
                self.state = 'jumpr'
                self.sequence = self.images[self.state][self.direction]
                self.bounce = False
            if self.state == 'standl' or self.state == 'walkl' \
               or self.state == 'jumpl':
                self.state = 'jumpl'
                self.sequence = self.images[self.state][self.direction]
                self.bounce = False
        if not self.onGround:
            if self.vy >= 3:
                if self.state == 'standl':
                    self.state = 'jumpl'
                    self.sequence = self.images[self.state][self.direction]
                if self.state == 'stand':
                    self.state = 'jumpr'
                    self.sequence = self.images[self.state][self.direction]
            #set change in y for gravity against the jump
            self.vy += 0.7
            # max falling speed
            if self.vy > 100:
                self.vy = 100
        if up:
            if self.bounce:
                #makes sure the jump pads don't add velocity on top
                #of a normal jump
                self.vy = -20
        if not(left or right):
            self.vx = 0
        #check for if player has fallen off screen
        self.fall(fallblocks, fallsound)
        #check for if collectible is collected
        self.collect_coin(collectibles, allsprites, ding)
        #check for extra life collected
        self.collect_life(heartlist, allsprites, ding)
        #check for if player walks through the exit door
        self.exit_level(exitdoor)
        #create x velocity and check for collisions
        self.rect.left += self.vx
        self.collide(self.vx, 0, platforms)
        self.enemy_collide(self.vx, 0, enemies, enemydeath_sound,\
                            allsprites)
        #create y velocity and check for collisions if in the air
        self.rect.top += self.vy
        self.onGround = False;
        self.collide(0, self.vy, platforms)
        self.jumppad_collide(0, self.vy, jumppads, boing)
        #check for if player is killed or kills an enemy
        self.enemy_collide(0, self.vy, enemies, enemydeath_sound,\
                        allsprites)

    def collide(self, vx, vy, platforms):
        """Check if player collides with platform and which direction he is
        going in, in which the player position is then set by which side
        collided"""
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if vx > 0:
                    self.rect.right = p.rect.left
                if vx < 0:
                    self.rect.left = p.rect.right
                if vy > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.vy = 0
                if vy < 0:
                    self.rect.top = p.rect.bottom

    def jumppad_collide(self, vx, vy, jumppads, boing):
        """Checks player collision with a jump pad, which then makes the player
        bounce in the air"""
        for p in jumppads:
            if pygame.sprite.collide_rect(self, p):
                if vy > 0:
                    self.rect.bottom = p.rect.top
                    self.vy = -20
                    boing.play()
                    self.bounce = True
            if p.rect.left-30 < self.rect.left < p.rect.left+30:
                if self.rect.bottom == p.rect.top:
                    self.vy = -20
                    boing.play()
                    self.bounce = True

    def enemy_collide(self, vx, vy, enemies, enemydeath_sound,\
                      allsprites):
        """The values in self.vy and self.vx statements were a lot of trial and
        error as there is no easy way in pygameto detect if the player landed on
        an enemies head."""
        for e in enemies:
            if pygame.sprite.collide_mask(self, e):
                if vy > 0:
                    enemydeath_sound.play()
                    self.vy = -11
                    enemies.remove(e)
                    allsprites.remove(e)
                    self.enemieskilled += 1
                if vx > 0:
                    self.playerdeath = True
                if vx < 0:
                    self.playerdeath = True
                if vx == 0:
                    if vy == 0:
                        self.playerdeath = True

    def collect_coin(self, collectibles, allsprites, ding):
        """Detects and removes coin if collided and collected by player"""
        for c in collectibles:
            if pygame.sprite.collide_rect(self, c):
                ding.play()
                self.collected += 1
                collectibles.remove(c)
                allsprites.remove(c)

    def collect_life(self, heartlist, allsprites, ding):
        """Detects and removes heart if collided and collected by player"""
        for heart in heartlist:
            if pygame.sprite.collide_rect(self, heart):
                ding.play()
                self.extralives += 1
                heartlist.remove(heart)
                allsprites.remove(heart)      

    def fall(self, fallblocks, fallsound):
        """Detects if collides with fallblock, which then sets falldeath to
        true"""
        for block in fallblocks:
            if pygame.sprite.collide_rect(self, block):
                fallsound.play()
                self.falldeath = True

    def exit_level(self, exitdoor):
        """Detects if player collides with door and sets end level to true"""
        for e in exitdoor:
            if pygame.sprite.collide_rect(self, e):
                self.levelcomplete = True
            
class Enemyblock(Sprite):
    """Creates enemy sprite on screen"""
    images = {}
    def __init__(self, x, y):
        super().__init__(screen, 'MONKEY.zip', state = 'walkr')
        #http://piq.codeus.net/picture/45307/8_bit_monkey was used for the
        #initial monkey file, which i then adapted to make into an animation
        self.vx = 5
        self.rect = pygame.rect.Rect(x, y, 27, 34)
        self.x = x

        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self):
        """Moves enemy left and right by a certain amount, changing animation
        states as it moves"""
        self.rect.centerx += self.vx
        if self.rect.left < self.x-40:
            self.vx *= -1
            self.state = 'walkr'
            self.sequence = self.images[self.state][self.direction]
            
        if self.rect.right > self.x+110:
            self.vx *= -1
            self.state = 'walkl'
            self.sequence = self.images[self.state][self.direction]
            
class Camera(object):
    """Creates camera to keep track of player in relation to screen and adds
    a lag to the camera to make it work nicely within the game"""
    #This camera function was extremely difficult to get my head around so
    #adapted a version that was found from a tutorial online
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.rect.Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

def camera_rect(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h

    l = min(-32, l)                           # stop scrolling at the left
    l = max(-(camera.width-SCREEN_WIDTH)+32, l)   # stop scrolling at the right
    t = max(-(camera.height-SCREEN_HEIGHT)+32, t) # stop scrolling at the bottom
    t = min(-32, t)                           # stop scrolling at the top
    return pygame.rect.Rect(l, t, w, h)
