#########################################
#########################################
##                                     ##
##    ####    ####   ##  ##  ######    ##
##   ##  ##  ##  ##  ######  ##        ##
##   ##      ##  ##  ##  ##  ##        ##
##   ##      ######  ##  ##  ######    ##
##   ## ###  ##  ##  ##  ##  ##        ##
##   ##  ##  ##  ##  ##  ##  ##        ##
##    ####   ##  ##  ##  ##  ######    ##
##                                     ##
##          by Kieran Haden            ##
#########################################
#########################################

#Workaround for uni error in importing easypg module
import sys
sys.path.append("/export/mailgrp3_e/um10kh/py3./lib/python3.3/site-packages")

#import relevant modules
import pygame
from pygame import *
#easypg is used for colours module and Sprite classes
import easypg
from easypg import colours
#time is used for time.sleep function
import time
#gameclasses includes player, enemy and camera classes
import gameclasses
#ground blocks includes platform and background classes
import groundblocks
#specialblocks include jump pads, hearts, coins and fallblocks
import specialblocks
#pygbutton is a python file downloaded from http://www.pygame.org/project-PygButton-2709-.html
#this is used for easy to place button for the user interface
import pygbutton
#the ps3 file takes a controller and creates a dictionary to recognise it
#as a ps3 controller
import ps3trial

##import levelrandomgenerator

#create global screen variables
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
HALF_WIDTH = int(SCREEN_WIDTH / 2)
HALF_HEIGHT = int(SCREEN_HEIGHT / 2)

SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
FLAGS = 0
DEPTH = 32

class Game():
    #define level number variables, lives and level scores outside the
    #init loop so when next level is initialised, these variables stay constant
    levelnumber = 1
    levelscore = 0
    lives = 3  

    #main menu variables defined outside __init__ so when game restarts, the
    #main menu doesn't open
    mainmenu = True

    def __init__(self):
        """Running the __init__ function will reset all the game variables
        and restart the current level"""
        #create bg surface to be drawn to screen
        self.bg = pygame.Surface(SIZE).convert()
        
        #initialise joystick
        self.joysticks = []
        for i in range(0, pygame.joystick.get_count()):
            self.joysticks.append(pygame.joystick.Joystick(i))
            self.joysticks[-1].init()
        
        #create groups and sprites, allsprites is ordered to determine what
        #appears on top of what in game
        self.playergroup = pygame.sprite.Group()
        self.allsprites = pygame.sprite.OrderedUpdates()

        #create empty lists for level building
        self.enemies = []
        self.collectibles = []
        self.fallblocks = []
        self.jumppads = []
        self.platforms = []
        self.exitdoor = []
        self.heartlist = []

        #set pygame font for in-game text
        self.font = pygame.font.SysFont("debussy.tff", 30)
        self.mediumfont = pygame.font.SysFont("debussy.tff", 50)
        self.largefont = pygame.font.SysFont("debussy.tff", 70)

        #define extra colours to be used for main menus
        self.BROWN = (72,39,21)
        self.CREAM = (255,206,173)
        
        #set up score/health/time variables,score is in the __init__ function
        #as it resets everytime you die or restart game
        self.score = 0
        self.timer = 50

        #ALL FOLLOWING LOOP VARIABLES ARE SET UP TO CONTROL GAME LOGIC
        #set up level win conditions
        self.levelcomplete = False
        self.levelcompleteloop = False
        self.gamecomplete = False

        #set up game over variables
        self.gameover = False
        self.gameoverloop = False

        #set up game paused variables
        self.gamepaused = False
        self.gamepause_loop = False

        #set up enter name for high score screen
        self.enternamescreen = False
        self.enternameloop = False
        self.initialsname = ""
        self.listcomplete = False

        #set up screen for highscore addition
        self.gamecompscore = False

        #set up instructions screen loop variables
        self.instructions = False

        #set up sound effects for in game events
        self.boing = pygame.mixer.Sound('gamesounds\\boing.ogg')
        self.ding = pygame.mixer.Sound('gamesounds\\ding.ogg')
        self.deathsound = pygame.mixer.Sound('gamesounds\\enemydeath.ogg')
        self.fallsound = pygame.mixer.Sound("gamesounds\\falling.ogg")
        
        #create level/platforms
        self.x = self.y = 0

        if self.levelnumber == 1:
            self.level = [
                "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
                "P1                                                                   P",
                "P                                                                    P",
                "P                                                                    P",
                "P                                                                    P",
                "P                                                                    P",
                "P                                                                    P",
                "P                                                              X     P",
                "P               PP                                                   P",
                "P       CE           C                                      PPPPPPP  P",
                "P      PPPPPP        PP                        C  EC  C              P",
                "P                                            PPPPPPPPPPP             P",
                "P                          PP                                        P",
                "P                                      PPP                           P",
                "P                               PPPP                                 P",
                "P                               P  P                                 P",
                "P                      PJPPPPP  P  P                                 P",
                "P                  PP           P  P                                 P",
                "P           E                   P  P   C              C              P",
                "PPPPPPPPPPPPPPPPP               P   JPPPPPPPPPPPPPPPPPPPPJPPPP       P",
                "P               P               P                            P       P",
                "P               P               P                            P       P",
                "P               P               P                            P       P",
                "                 FFFFFFFFFFFFFFF           FFFFFFF            FFFFFFFP",]
        if self.levelnumber == 2:
            self.level = [
                "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
                "P2                                                                     P",
                "P                                                                      P",
                "P                                                                      P",
                "P                                                                      P",
                "P                                            C    C                    P",
                "P                                      C               C               P",
                "P                                      E       E       E               P",
                "P                                 PPPPPPPPPPPPPPPPPPPPPPPPPPPP         P",
                "P                             C                                        P",
                "P                            PP                                  E     P",
                "P                                 CC                            PPPPP  P",
                "P                                 PP                                   P",
                "P                       C                CH                 P C        P",
                "P                      PPJ                                   PPP       P",
                "P                                    C        C                        P",
                "P                 PPP                    E           E           E     P",
                "P                       C            C        C                 PPPPP  P",
                "P                      PPP                                             P",
                "P                                    C        C             P C        P",
                "P                 PPP                J        J              PPP       P",
                "P                                                                      P",
                "PPPPPPPPPPPPPPPPPPP                                               X    P",
                "Pgggggggggggggggggg                                                    P",
                "Pgggggggggggggggggg                                            PPPPPPPPP",
                "Pgggggggggggggggggg                                            P       P",
                "                   FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFP",]
        if self.levelnumber == 3:
            self.level = [
                "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
                "P3                                                                                                                           P",
                "P                                                                                                                            P",
                "P                                                                                                                            P",
                "P                                                                                                                            P",
                "P                                                                                                                            P",
                "P                                                                                       PPPPPPPPPPP                          P",
                "P                                                                                     PP           PPP                       P",
                "P                                                                                   PP                PP                     P",
                "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP    C               PPPPPPPPPPPPPPPPPPPPPP",
                "P                                                                                    C                                       P",
                "P                                                                                        E   C  E  C                         P",
                "P                          C                                                          PPPPPPPPPPPPPPPP      C                P",
                "P                     C                      P C                      CC           C                    PPP      C           P",
                "P                          P     C  E  C    PP    C                C      C                                   PP      X      P",
                "P      C              P                    P P   PP              PPPP    PPPP                                                P",
                "PPPPPPPPPPPP    PPP          PPPPPPPPPPPPPP P       PPPPPPPPPP                 PPPJ                             PPPPPPPPPPPPPP",
                "P          P    PPP          P             P        P        P                 PPPP                             P            P",
                "P          P                 P            P         P        P                                                  P            P",
                "P          P                 P           P          P        P                                                  P            P",
                "P          P                 P           P          P        PH                                                 P            P",
                "P           FFFFFFFFFFFFFFFFF             FFFFFFFFFF          JFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF             P",]
            
        
        #build the level, looping over columns and rows, if 'letter' appears then
        #append to the specified list and add to sprite list for drawing to the
        #screen later. Then move on one character, until you hit the end
        #of a row, then move onto the next row. This is done by adding 32 to
        #the x and y variables within the loops

        for row in self.level:
            for col in row:
                ###ALL THE SPRITES USED IN THE LEVEL BUILDING ARE FOUND IN
                ###gameclasses.py, specialblocks.py and groundblocks.py
                
                #depending on the level, create the background in the top left
                #corner, add them first to be drawn below everything else
                if col == "1":
                    p = groundblocks.BACK1(self.x, self.y)
                    self.allsprites.add(p)
                if col == "2":
                    p = groundblocks.BACK2(self.x, self.y)
                    self.allsprites.add(p)
                if col == "3":
                    p = groundblocks.BACK3(self.x, self.y)
                    self.allsprites.add(p)

                
                #create platforms - will detect player collision on all sides
                #Since the background contains the platform art, these square
                #platforms will not be drawn in allsprites.
                if col == "P":
                    p = groundblocks.Platform(self.x, self.y)
                    self.platforms.append(p)
                #create blocks that detect when the player hits the top of them
                #these are placed at the bottom of levels to detect when a player
                #has fallen
                if col == "F":
                    p = specialblocks.Fallblock(self.x, self.y)
                    self.fallblocks.append(p)
                #create coins that detect a player collision for them to be
                #collected. These are added to allsprites to be drawn to the
                #screen
                if col == "C":
                    p = specialblocks.Collectible(self.x+4, self.y+4)
                    self.collectibles.append(p)
                    self.allsprites.add(p)
                #heart has similar aspects to the collectible sprite but when
                #collected gives an extra life instead of extra score
                if col == "H":
                    p = specialblocks.Heart(self.x+4, self.y+4)
                    self.heartlist.append(p)
                    self.allsprites.add(p)                    
                #jumppad acts as a spring for the player to reach higher places
                #This acts when a player collision is detected with the top of
                #this object
                if col == "J":
                    p = specialblocks.Jumppad(self.x, self.y)
                    self.jumppads.append(p)
                #Exit door detects player collision and then activates level
                #complete variables
                if col == "X":
                    p = specialblocks.Exit_door(self.x, self.y)
                    self.exitdoor.append(p)
                    self.allsprites.add(p)
                #Enemies are moving sprites that will only die if the bottom of
                #the player collides with the top of the enemy
                if col == "E":
                    p = gameclasses.Enemyblock(self.x, self.y-13)
                    self.enemies.append(p)
                    
                self.x += 32
            self.y += 32
            self.x = 0
        #add enemies to allsprites at the end to make them appear above
        #items such as collectibles
        for e in self.enemies:
            self.allsprites.add(e)
            
        #create total level width and height variables
        self.level_width = len(self.level[0])*32
        self.level_height = len(self.level)*32

        #add camera class (found in gameclasses)
        self.camera = gameclasses.Camera(gameclasses.camera_rect, \
                                         self.level_width, self.level_height)

        #create player sprite- place at a different position depending on the
        #level number
        if self.levelnumber == 1:
            self.player = gameclasses.PLAYER(100,550)
        if self.levelnumber == 2:
            self.player = gameclasses.PLAYER(100,580)
        if self.levelnumber == 3:
            self.player = gameclasses.PLAYER(112, 470)
        self.playergroup.add(self.player)
        self.allsprites.add(self.player)
            
        #create player direction variables for movement
        self.up = self.down = self.left = self.right = False
        
        #set up pygame clock for FPS
        self.clock = pygame.time.Clock()
        
    def game_logic(self):
        """Running game logic checks for events in game such as player input,
        level win/game over conditions etc"""
        #set FPS for self.clock
        self.clock.tick(30)

        #using variables activated when an event occurs to the player, check
        #for player death and restart level with one less life
        if self.player.falldeath == True:
            time.sleep(1)
            self.lives -= 1
            self.__init__()
        if self.player.playerdeath == True:
            time.sleep(1)
            self.lives -= 1
            self.__init__()
        #if all lives are over, set game over variables equal to true
        if self.lives == -1:
            self.gameover = True
            self.gameoverloop = True

        #check level complete conditions, return False to stop running
        if self.player.levelcomplete == True and self.levelnumber < 3:
            self.levelcomplete = True
            self.levelcompleteloop = True

        #if third level complete send player to game complete screen    
        if self.player.levelcomplete == True and self.levelnumber == 3:
            self.gamecomplete = True            

                
        #check events in game, return False to quit game loop, other basic keys
        #used for movement
        for e in pygame.event.get():
            if e.type == QUIT or \
               (e.type == KEYDOWN and e.key == K_ESCAPE) or \
                e.type == JOYBUTTONDOWN and e.dict == {'button': 0, 'joy': 0}:
                return False           

            #p button and start button used to start pause game variables
            if e.type == KEYDOWN and e.key == K_p or \
               e.type == JOYBUTTONDOWN and e.dict == {'button': 3, 'joy': 0}:
                self.gamepaused = True
                self.gamepause_loop = True

            #up button sets up to true for jumping
            if (e.type == KEYDOWN and e.key == K_UP) or \
                (e.type == KEYDOWN and e.key == K_SPACE) or \
                e.type == JOYBUTTONDOWN and e.dict == {'button': 14, 'joy': 0}:
                    self.up = True
            if (e.type == KEYUP and e.key == K_UP) or \
                (e.type == KEYUP and e.key == K_SPACE) or \
                e.type == JOYBUTTONUP and e.dict == {'button': 14, 'joy': 0}:
                self.up = False

            #right button sets right to true
            if (e.type == KEYDOWN and e.key == K_LEFT) or\
               e.type == JOYBUTTONDOWN and e.dict == {'button': 7, 'joy': 0}:
                self.left = True
            if e.type == KEYUP and e.key == K_LEFT or\
               e.type == JOYBUTTONUP and e.dict == {'button': 7, 'joy': 0}:
                self.left = False

            #left button sets left tot true  
            if e.type == KEYDOWN and e.key == K_RIGHT or\
               e.type == JOYBUTTONDOWN and e.dict == {'button': 5, 'joy': 0}:
                self.right = True
            if e.type == KEYUP and e.key == K_RIGHT or\
               e.type == JOYBUTTONUP and e.dict == {'button': 5, 'joy': 0}:
                self.right = False
                    
        return True

    def display_update(self, screen):
        """Updates things to do with the display in game such as updating sprites
        scores, time, extra live variables etc"""
        #if the game is not over and the level is not complete
        if not self.gameover:
            #clear all sprites first
            self.allsprites.clear(screen, self.bg)
            #call camera update in relation to player position
            self.camera.update(self.player)
            #update player with all variables (sounds, other items, movement etc)
            self.player.update(self.up, self.down, self.left, self.right, \
                               self.platforms, self.fallblocks, self.fallsound, \
                               self.jumppads, self.boing, self.collectibles, \
                               self.ding, self.enemies, self.deathsound, \
                               self.exitdoor, self.allsprites\
                               ,self.heartlist)
            #check state and animate player using gameclasses.py
            self.player.check_state()
            self.player.animate()
            #update all enemies movement
            for e in self.enemies:
                e.update()
                e.check_state()
                e.animate()
            #update score depending on the enemies killed etc
            self.score = (self.player.enemieskilled *50) + \
                         (self.player.collected*10)
            #if collect a heart then add 1 to lives
            if self.player.extralives == 1:
                self.lives +=1
                self.player.extralives = 0
            #basic score logic - saves score when level is completed to access
            #for later levels
            if self.levelcomplete:
                self.score = self.score + (3*int("{:.0f}".format(self.timer)))
                self.levelscore = self.levelscore + self.score
                self.score = self.levelscore
            if self.gamecomplete:
                self.score = self.score + (3*int("{:.0f}".format(self.timer)))
            if not self.levelcomplete:
                self.score += self.levelscore
            self.timer -= 1/30
            #check if timer reaches zero, set gameover equal to true
            if self.timer <= 0:
                self.timer = 0
                time.sleep(1)
                self.lives -= 1
                self.__init__()
            #draw everything to screen in regards to what is in the camera rectangle
            for e in self.allsprites:
                screen.blit(e.image, self.camera.apply(e))
            #draw UI information to screen - score, health, items collected,
            #time left etc, format time for no decimal places, format score to fit
            #nicely on screen then blit all to screen
            healthtext = self.font.render("Lives : {0}".format(self.lives), \
                                          True, colours.BLACK)
            scoretext = self.font.render("Score: {0}".format(self.score), \
                                         True, colours.BLACK)
            timetext = self.font.render("Time left : {:.0f}".format(self.timer)\
                                        , True, colours.BLACK)
            screen.blit(healthtext, [30, 30])
            screen.blit(scoretext, [30, 80])
            screen.blit(timetext, [SCREEN_WIDTH-160, 30])
        pygame.display.update()




    def menuscreen(self, screen):
        """A function to draw the main menu screen with event loop"""
        #load menu bg, text and graphics
        menubg = pygame.image.load("menuscreen.bmp")
        bgrect = menubg.get_rect()
        screen.blit(menubg, bgrect)
        pygame.draw.rect(screen, self.CREAM, [215,125,375,415], 0)
        pygame.draw.rect(screen, self.BROWN, [215,125,375,415], 5)
        mainmenutext = self.largefont.render("JUNGLE RUN"\
                                        , True, self.BROWN)
        #if self.joysticks statement detects if a joystick exists or not
        if self.joysticks == []:
            #different text for button prompts depending on controller
            #or keyboard control
            playbutton = pygbutton.PygButton((\
            (SCREEN_WIDTH // 2 - 30), (SCREEN_HEIGHT // 2 - 50), \
            60, 40), 'PLAY')
        if self.joysticks != []:
            playbutton = pygbutton.PygButton((\
            (SCREEN_WIDTH // 2 - 30), (SCREEN_HEIGHT // 2 - 50), \
            80, 40), 'PLAY (X)')
        if self.joysticks == []:
            instructbutton = pygbutton.PygButton((\
            (SCREEN_WIDTH // 2 - 70), (SCREEN_HEIGHT // 2 + 50),\
            140, 40), 'INSTRUCTIONS')
        if self.joysticks != []:
            instructbutton = pygbutton.PygButton((\
            (SCREEN_WIDTH // 2 - 72.5), (SCREEN_HEIGHT // 2 + 50),\
            165, 40), 'INSTRUCTIONS ([])')
        if self.joysticks == []:
            exitbutton = pygbutton.PygButton((\
            (SCREEN_WIDTH // 2 - 30), (SCREEN_HEIGHT // 2 + 150), \
            60, 40), 'EXIT')
        if self.joysticks != []:
            exitbutton = pygbutton.PygButton((\
            (SCREEN_WIDTH // 2 - 30), (SCREEN_HEIGHT // 2 + 150), \
            80, 40), 'EXIT (O)')
        
        allButtons = (playbutton, instructbutton, exitbutton)

        while True:
            #in the main menu events, detect clicks in menu buttons and set certain
            #screen variables to true to change the current game screen
            for event in pygame.event.get():
                if event.type == QUIT or \
                   (event.type == KEYDOWN and event.key == K_ESCAPE) or\
                    (event.type == JOYBUTTONDOWN and event.dict == {'joy': 0, 'button': 0}) or\
                    (event.type == JOYBUTTONDOWN and event.dict == {'joy': 0, 'button': 13}) or\
                    'click' in exitbutton.handleEvent(event):
                    return False       

                if 'click' in playbutton.handleEvent(event) or \
                   (event.type == KEYDOWN and event.key == K_SPACE) or\
                    (event.type == JOYBUTTONDOWN and event.dict == {'joy': 0, 'button': 14}):
                    self.ding.play()
                    self.mainmenu = False
                    self.mainmenuloop = False
                    return True

                if 'click' in instructbutton.handleEvent(event) or \
                    (event.type == JOYBUTTONDOWN and event.dict == {'joy': 0, 'button': 15}):                   
                    self.instruction_loop = True
                    self.instructions = True
                    return True

            #blit text and buttons to the screen        
            screen.blit(mainmenutext, [SCREEN_WIDTH // 2 -\
                (mainmenutext.get_width() // 2) , 150])
            for b in allButtons:
                b.draw(screen)
            
            pygame.display.update()


    def instruction_screen(self, screen):
        """A function to draw the instructions screen with event loop"""
        #create bg, text and graphics
        menubg = pygame.image.load("menuscreen.bmp")
        bgrect = menubg.get_rect()
        screen.blit(menubg, bgrect)
        pygame.draw.rect(screen, self.CREAM, [65,65,670,515], 0)
        pygame.draw.rect(screen, self.BROWN, [65,65,670,515], 5)

        #initialise buttons
        if self.joysticks == []:
            backbutton = pygbutton.PygButton((\
            (SCREEN_WIDTH // 2 - 75), (SCREEN_HEIGHT // 2 + 185), \
            150, 40), 'BACK TO MENU')
        if self.joysticks != []:
            backbutton = pygbutton.PygButton((\
            (SCREEN_WIDTH // 2 - 85), (SCREEN_HEIGHT // 2 + 185), \
            170, 40), 'BACK TO MENU (O)')
        allButtons = (backbutton)

        #set up text lines for instructions screen
        keyboard = self.font.render("Keyboard",True,self.BROWN)
        spacetext = self.font.render("SPACE = Jump", True, self.BROWN)
        lefttext = self.font.render("LEFT ARROW = Left", True, self.BROWN)
        righttext = self.font.render("RIGHT ARROW = Right", True, self.BROWN)
        ptext = self.font.render("P BUTTON = Pause", True, self.BROWN)
        esctext = self.font.render("ESCAPE BUTTON = Quit", True, self.BROWN)

        controllertext = self.font.render("Controller", True, self.BROWN)        
        Xtext = self.font.render("X = Jump", True, self.BROWN)
        leftbtext = self.font.render("LEFT ARROW = Left", True, self.BROWN)
        rightbtext = self.font.render("RIGHT ARROW = Right", True, self.BROWN)
        starttext = self.font.render("START BUTTON = Pause", True, self.BROWN)
        selecttext = self.font.render("SELECT = Quit", True, self.BROWN)

        #blit all text to screen
        screen.blit(keyboard, [100, 110])
        screen.blit(spacetext, [100, 200])
        screen.blit(lefttext, [100, 250])           
        screen.blit(righttext, [100, 300])
        screen.blit(ptext, [100, 350])
        screen.blit(esctext, [100, 400])
        
        screen.blit(controllertext, [450, 110])
        screen.blit(Xtext, [450, 200])
        screen.blit(leftbtext, [450, 250])           
        screen.blit(rightbtext, [450, 300])
        screen.blit(starttext, [450, 350])
        screen.blit(selecttext, [450, 400])
        
        while True: # instructions loop
            #detects either quit or button press
            for event in pygame.event.get():
                if event.type == QUIT or \
                   (event.type == KEYDOWN and event.key == K_ESCAPE) or\
                    (event.type == JOYBUTTONDOWN and event.dict == {'joy': 0, 'button': 0}):
                    return False       

                if 'click' in backbutton.handleEvent(event) or \
                    (event.type == JOYBUTTONDOWN and event.dict == {'joy': 0, 'button': 13}):
                    self.instructions = False
                    return True
                else:
                    True
            #blit button in update loop so changes graphics on click
            backbutton.draw(screen)
                
            pygame.display.update()

    def gamepause_screen(self, screen):
        """Draw the pause function to the screen"""
        #set up pause text
        pause_text = self.largefont.render("PAUSED", True, colours.BLACK)
        x = (SCREEN_WIDTH // 2) - (pause_text.get_width() // 2)
        y = (SCREEN_HEIGHT // 2) - (pause_text.get_height() // 2)
        #blit to screen
        screen.blit(pause_text, [x, y-150])
        pygame.display.update()

    def gamepause_logic(self):
        """Detect unpause or quit after game is paused"""
        keys = pygame.key.get_pressed()
        #pause loop detects quit or unpause
        for e in pygame.event.get():
            if e.type == QUIT:
                return False
            if keys[pygame.K_ESCAPE]:
                return False
            if e.type == KEYDOWN and e.key == K_p or \
            (e.type == JOYBUTTONDOWN and e.dict == {'button': 3, 'joy': 0}):
                return True




    def level_complete_screen(self, screen):
        """if the game is over by the player falling/being killed by enemy,
        print option of quitting, restarting the level or going back to main
        menu"""
        #sets up text for level complete
        levelcomplete_text = self.largefont.render("LEVEL COMPLETE", True, colours.BLACK)
        if self.joysticks == []:
            restart_text = self.font.render("press space to continue to next level"\
                                    , True, colours.BLACK)
            esc_text = self.font.render("press esc to quit", True, colours.BLACK)
        if self.joysticks != []:
            restart_text = self.font.render("press X to continue to next level"\
                                    , True, colours.BLACK)
            esc_text = self.font.render("press O to quit", True, colours.BLACK)
        x = (SCREEN_WIDTH // 2) - (levelcomplete_text.get_width() // 2)
        y = (SCREEN_HEIGHT // 2) - (levelcomplete_text.get_height() // 2)
        #blit all text to screen
        screen.blit(levelcomplete_text, [x, y-150])
        screen.blit(restart_text, [(SCREEN_WIDTH // 2) - \
                                 (restart_text.get_width() // 2), (y+150)])
        screen.blit(esc_text, [(SCREEN_WIDTH // 2) - \
                               (esc_text.get_width() // 2), (y+250)])
        pygame.display.update()
        
    def level_complete_logic(self):
        """Detect whether player wants to quit or go to next level"""
        keys = pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type == QUIT or keys[pygame.K_ESCAPE] or\
                (e.type == JOYBUTTONDOWN and e.dict == {'button': 13, 'joy': 0}):
                return False
            #if go to next level, add 1 to self.levelnumber and reset all other
            #variables by doing self.__init__()
            if keys[pygame.K_SPACE] or \
                (e.type == JOYBUTTONDOWN and e.dict == {'button': 14, 'joy': 0}):
                self.levelnumber += 1
                self.__init__()
        return True



        
    def game_over_screen(self, screen):
        """if the game is over by the player falling/being killed by enemy,
        print option of quitting, restarting the level or going back to main
        menu"""
        #set up text and graphics variables
        menubg = pygame.image.load("menuscreen.bmp")
        bgrect = menubg.get_rect()
        screen.blit(menubg, bgrect)
        pygame.draw.rect(screen, (255,206,173), [215,70,375,525], 0)
        pygame.draw.rect(screen, (72,39,21), [215,70,375,525], 5)
        gameover_text = self.largefont.render("GAME OVER", True, colours.BLACK)
        lives_text = self.font.render("You ran out of lives!", True, colours.BLACK)
        #set up text depending on controller existence
        if self.joysticks == []:
            restart_text = self.font.render("press r to restart game"\
                                    , True, colours.BLACK)
            esc_text = self.font.render("press esc to quit", True, colours.BLACK)
        if self.joysticks != []:
            restart_text = self.font.render("press square to restart game"\
                                    , True, colours.BLACK)
            esc_text = self.font.render("press O to quit", True, colours.BLACK)    
        x = (SCREEN_WIDTH // 2) - (gameover_text.get_width() // 2)
        y = (SCREEN_HEIGHT // 2) - (gameover_text.get_height() // 2)
        #blit everything to screen
        screen.blit(gameover_text, [x, y-200])
        screen.blit(lives_text, [(SCREEN_WIDTH // 2) - \
                                 (lives_text.get_width() // 2), y-50])        
        screen.blit(restart_text, [(SCREEN_WIDTH // 2) - \
                                 (restart_text.get_width() // 2), (y+175)])
        screen.blit(esc_text, [(SCREEN_WIDTH // 2) - \
                               (esc_text.get_width() // 2), (y+250)])
        pygame.display.update()

    def game_over_logic(self):
        """Detects if player wants to quit or restart whole game"""
        keys = pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type == QUIT or keys[pygame.K_ESCAPE] or \
                (e.type == JOYBUTTONDOWN and e.dict == {'button': 13, 'joy': 0})or\
                (e.type == JOYBUTTONDOWN and e.dict == {'button': 0, 'joy': 0}):               
                return False

            if keys[pygame.K_r] or \
               (e.type == JOYBUTTONDOWN and e.dict == {'joy': 0, 'button': 15}):
                #if restart game then reset all level variables including score
                #so player starts at level 1 with no score
                self.lives = 3
                self.levelnumber = 1
                self.score = 0
                self.levelscore = 0
                self.__init__()
        return True




    def gamecomplete_screen(self, screen):
        """If player completes level 3, go to level complete screen, which has
        high score details, whether a player wants to quit or restart whole game"""
        #create graphics and text variables
        menubg = pygame.image.load("menuscreen.bmp")
        bgrect = menubg.get_rect()
        screen.blit(menubg, bgrect)
        pygame.draw.rect(screen, self.CREAM, [160,95,485,455], 0)
        pygame.draw.rect(screen, self.BROWN, [160,95,485,455], 5)
        gameover_text = self.largefont.render("GAME COMPLETE", True, self.BROWN)
        if self.joysticks == []:
            restart_text = self.font.render("press r to restart game"\
                                    , True, self.BROWN)
            esc_text = self.font.render("press esc to quit", True, self.BROWN)
        if self.joysticks != []:
            restart_text = self.font.render("press square to restart game"\
                                    , True, self.BROWN)
            esc_text = self.font.render("press circle to quit", True, self.BROWN)
        x = (SCREEN_WIDTH // 2) - (gameover_text.get_width() // 2)
        y = (SCREEN_HEIGHT // 2) - (gameover_text.get_height() // 2)
        #blit text to screen
        screen.blit(gameover_text, [x, y-175])
        screen.blit(restart_text, [(SCREEN_WIDTH // 2) - \
                                 (restart_text.get_width() // 2), (y+175)])
        screen.blit(esc_text, [(SCREEN_WIDTH // 2) - \
                               (esc_text.get_width() // 2), (y+210)])
        high_score = 0

        #reads in the current high scores and checks to see if current score
        #is a high score or not

        f = open("high_score.txt", "r")
        line_list = f.readlines()

        trimmed_line_list = []
        scores = []

        for line in line_list:
            trimmed_line_list.append(line.strip())
        for line in trimmed_line_list:
            line = line.split()
            scores.append("".join(line[0]))
        f.close()
        
        current_score = self.score

        #if statement sets highscore variables if it is a highscore
        if current_score > int(scores[2]):
            highscore = True
            if highscore == True:
                gothighscore = "You got a new high score!"
                FINALLIST = " ---- "+(" ---- ".join(trimmed_line_list))+" ---- "

        #if not a highscore the highscore list is left as it is - the FINALLIST
        #variable is a modified version of the highscore.txt file to print nicely
        #onto the screen
        if current_score <= int(scores[2]):
            highscore = False
            if highscore == False:
                gothighscore = "You have not got a new high score, try again"
                f = open("high_score.txt", "w")
                FINALTRIMLIST = []
                for line in line_list:
                    FINALTRIMLIST.append(line.strip())
                FINALLIST = " ---- "+(" ---- ".join(FINALTRIMLIST))+" ---- "
                f.write("".join(line_list))
                f.close()

        #create high score related text    
        highscoretitle = self.mediumfont.render("Highscores"\
                                                  , True, self.BROWN)
        currenthighscores = self.font.render((str("".join(FINALLIST)))\
                                                  , True, self.BROWN)
        currentscoretext = self.font.render("Your score = "+str(current_score),\
                                            True, self.BROWN)
        highscoretext = self.font.render(gothighscore\
                                                  , True, self.BROWN)
        enternametext = self.font.render("******Press space to enter name******", True,\
                                         self.BROWN)

        #if you get a highscore then print out press space to enter name text
        if gothighscore == "You got a new high score!":
            screen.blit(enternametext,[(SCREEN_WIDTH // 2) - \
                                 (enternametext.get_width() // 2), (y-5)])

        #blit rest of high score text information to screen
        screen.blit(highscoretitle, [(SCREEN_WIDTH // 2) - \
                                 (highscoretitle.get_width() // 2), (y+50)])
        screen.blit(currenthighscores, [(SCREEN_WIDTH // 2) - \
                                 (currenthighscores.get_width() // 2), (y+100)])
        screen.blit(currentscoretext, [(SCREEN_WIDTH // 2) - \
                                 (currentscoretext.get_width() // 2), (y-100)])
        screen.blit(highscoretext, [(SCREEN_WIDTH // 2) - \
                                 (highscoretext.get_width() // 2), (y-65)])


        pygame.display.update()


    def gamecomplete_logic(self):
        """Game complete screen logic - detects whether player wants to enter name
        if they have a high score, fully restart game if not or quit game"""
        keys = pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type == QUIT or keys[pygame.K_ESCAPE] or \
                (e.type == JOYBUTTONDOWN and e.dict == {'button': 13, 'joy': 0}):               
                return False
            #if space or x pressed, go to enter name screen for high score
            if keys[pygame.K_SPACE] or\
                (e.type == JOYBUTTONDOWN and e.dict == {'button': 14, 'joy': 0}):
                self.enternamescreen = True
            if keys[pygame.K_r] or \
               (e.type == JOYBUTTONDOWN and e.dict == {'joy': 0, 'button': 15}):
                self.lives = 3
                self.levelnumber = 1
                self.score = 0
                self.levelscore = 0
                self.__init__()
        return True

    def entername_screen(self,screen):
        """Screen with a keyboard of buttons for player to enter name with"""
        #setup graphics and screen text
        menubg = pygame.image.load("menuscreen.bmp")
        bgrect = menubg.get_rect()
        screen.blit(menubg, bgrect)
        pygame.draw.rect(screen, self.CREAM, [215,125,375,365], 0)
        pygame.draw.rect(screen, self.BROWN, [215,125,375,365], 5)
        mainmenutext = self.mediumfont.render("ENTER INITIALS"\
                                        , True, self.BROWN)
        #set up button for each letter of the alphabet
        abutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 155), (SCREEN_HEIGHT // 2 - 50), \
        30, 40), 'A')
        bbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 115), (SCREEN_HEIGHT // 2 - 50), \
        30, 40), 'B')
        cbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 75), (SCREEN_HEIGHT // 2 - 50),\
        30, 40), 'C')
        dbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 35), (SCREEN_HEIGHT // 2 - 50),\
        30, 40), 'D')
        ebutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 5), (SCREEN_HEIGHT // 2 - 50), \
        30, 40), 'E')
        fbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 45), (SCREEN_HEIGHT // 2 - 50), \
        30, 40), 'F')
        gbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 85), (SCREEN_HEIGHT // 2 - 50), \
        30, 40), 'G')
        hbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 125), (SCREEN_HEIGHT // 2 - 50), \
        30, 40), 'H')
        ibutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 155), (SCREEN_HEIGHT // 2), \
        30, 40), 'I')
        jbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 115), (SCREEN_HEIGHT // 2), \
        30, 40), 'J')
        kbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 75), (SCREEN_HEIGHT // 2), \
        30, 40), 'K')
        lbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 35), (SCREEN_HEIGHT // 2), \
        30, 40), 'L')
        mbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 5), (SCREEN_HEIGHT // 2), \
        30, 40), 'M')
        nbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 45), (SCREEN_HEIGHT // 2), \
        30, 40), 'N')
        obutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 85), (SCREEN_HEIGHT // 2), \
        30, 40), 'O')
        pbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 125), (SCREEN_HEIGHT // 2), \
        30, 40), 'P')
        qbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 155), (SCREEN_HEIGHT // 2 + 50), \
        30, 40), 'Q')
        rbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 115), (SCREEN_HEIGHT // 2 + 50), \
        30, 40), 'R')
        sbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 75), (SCREEN_HEIGHT // 2 + 50),\
        30, 40), 'S')
        tbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 35), (SCREEN_HEIGHT // 2 + 50),\
        30, 40), 'T')
        ubutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 5), (SCREEN_HEIGHT // 2 + 50), \
        30, 40), 'U')
        vbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 45), (SCREEN_HEIGHT // 2 + 50), \
        30, 40), 'V')
        wbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 85), (SCREEN_HEIGHT // 2 + 50), \
        30, 40), 'W')
        xbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 125), (SCREEN_HEIGHT // 2 + 50), \
        30, 40), 'X')
        ybutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 155), (SCREEN_HEIGHT // 2 + 100), \
        30, 40), 'Y')
        zbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 115), (SCREEN_HEIGHT // 2 + 100), \
        30, 40), 'Z')
        #create delete and enter button for nice UI
        deletebutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 - 75), (SCREEN_HEIGHT // 2 + 100), \
        110, 40), 'DELETE')
        enterbutton = pygbutton.PygButton((\
        (SCREEN_WIDTH // 2 + 45), (SCREEN_HEIGHT // 2 + 100), \
        110, 40), 'ENTER')
        
        allButtons = (abutton, bbutton, cbutton, dbutton, ebutton\
                        ,fbutton, gbutton, hbutton, ibutton, jbutton\
                        ,kbutton, lbutton, mbutton, nbutton, obutton\
                        ,pbutton, qbutton, rbutton, sbutton, tbutton\
                        ,ubutton, vbutton, wbutton, xbutton, ybutton\
                        ,zbutton, deletebutton, enterbutton)

        #create initials variable to be printed to screen later
        initials = []
        initialstext = self.font.render(str(initials),True\
                                                ,self.BROWN)
        while True:
            for event in pygame.event.get():
                if event.type == QUIT or \
                   (event.type == KEYDOWN and event.key == K_ESCAPE) or\
                    (event.type == JOYBUTTONDOWN and event.dict == {'joy': 0, 'button': 1}):
                    return False
                #detects clicks in buttons and appends that letter to initials
                if 'click' in abutton.handleEvent(event):
                    initials.append("A")
                if 'click' in bbutton.handleEvent(event):
                    initials.append("B")
                if 'click' in cbutton.handleEvent(event):
                    initials.append("C")
                if 'click' in dbutton.handleEvent(event):
                    initials.append("D")
                if 'click' in ebutton.handleEvent(event):
                    initials.append("E")
                if 'click' in fbutton.handleEvent(event):
                    initials.append("F")
                if 'click' in gbutton.handleEvent(event):
                    initials.append("G")
                if 'click' in hbutton.handleEvent(event):
                    initials.append("H")
                if 'click' in ibutton.handleEvent(event):
                    initials.append("I")
                if 'click' in jbutton.handleEvent(event):
                    initials.append("J")
                if 'click' in kbutton.handleEvent(event):
                    initials.append("K")
                if 'click' in lbutton.handleEvent(event):
                    initials.append("L")
                if 'click' in mbutton.handleEvent(event):
                    initials.append("M")
                if 'click' in nbutton.handleEvent(event):
                    initials.append("N")
                if 'click' in obutton.handleEvent(event):
                    initials.append("O")
                if 'click' in pbutton.handleEvent(event):
                    initials.append("P")
                if 'click' in qbutton.handleEvent(event):
                    initials.append("Q")
                if 'click' in rbutton.handleEvent(event):
                    initials.append("R")
                if 'click' in sbutton.handleEvent(event):
                    initials.append("S")
                if 'click' in tbutton.handleEvent(event):
                    initials.append("T")
                if 'click' in ubutton.handleEvent(event):
                    initials.append("U")
                if 'click' in vbutton.handleEvent(event):
                    initials.append("V")
                if 'click' in wbutton.handleEvent(event):
                    initials.append("W")
                if 'click' in xbutton.handleEvent(event):
                    initials.append("X")
                if 'click' in ybutton.handleEvent(event):
                    initials.append("Y")
                if 'click' in zbutton.handleEvent(event):
                    initials.append("Z")
                #remove last letter inputted into initials if delete is pressed
                if 'click' in deletebutton.handleEvent(event):
                    if len(initials) != 0:
                        initials.remove(initials[-1])
                #if entered, sets the initials variable to the game class for
                #later use and quits from the enter name screen
                if 'click' in enterbutton.handleEvent(event):
                    if len(initials) == 3:
                        self.initialsname = ".".join(initials)
                        return False
                #for initials if length is zero, draw a blank rectangle
                if len(initials) == 0:
                    pygame.draw.rect(screen, self.CREAM, [350,220,100,25], 0)
                #draw intials to screen if anything has been added or taken away from the string
                if len(initials) == 1:
                    pygame.draw.rect(screen, self.CREAM, [350,220,100,25], 0)
                    firstinitial = ("".join(initials))
                    initialstext = self.font.render(str(firstinitial),True\
                                                ,self.BROWN)                    
                    screen.blit(initialstext, [HALF_WIDTH - \
                                                   initialstext.get_width()//2, 225])
                if len(initials) == 2:
                    pygame.draw.rect(screen, self.CREAM, [350,220,100,25], 0)
                    twoinitial = (".".join(initials))
                    initialstext = self.font.render(str(twoinitial),True\
                                                ,self.BROWN)                    
                    screen.blit(initialstext, [HALF_WIDTH - \
                                                   initialstext.get_width()//2 , 225])
                if len(initials) == 3:
                    pygame.draw.rect(screen, self.CREAM, [350,220,100,25], 0)                    
                    threeinitial = (".".join(initials))
                    initialstext = self.font.render(str(threeinitial),True\
                                                ,self.BROWN)
                    screen.blit(initialstext, [HALF_WIDTH - \
                                                   initialstext.get_width()//2 , 225])
                #dont let initials get longer than 3 letters long
                if len(initials) == 4:
                    initials = initials[0:3]

            #blit buttons and text within update loop
            screen.blit(mainmenutext, [SCREEN_WIDTH // 2 -\
                    (mainmenutext.get_width() // 2) , 150])
            for b in allButtons:
                    b.draw(screen)
                
            pygame.display.update()

    def highscore_screen(self,screen):
        """If player has entered name, new high scores appear and player can then
        quit game"""
        #setup graphics and text variables
        menubg = pygame.image.load("menuscreen.bmp")
        bgrect = menubg.get_rect()
        screen.blit(menubg, bgrect)
        pygame.draw.rect(screen, self.CREAM, [160,95,485,455], 0)
        pygame.draw.rect(screen, self.BROWN, [160,95,485,455], 5)
        gameover_text = self.largefont.render("GAME COMPLETE", True, self.BROWN)
        if self.joysticks == []:
            esc_text = self.font.render("press esc to quit", True, self.BROWN)
        if self.joysticks != []:
            esc_text = self.font.render("press circle to quit", True, self.BROWN)
        x = (SCREEN_WIDTH // 2) - (gameover_text.get_width() // 2)
        y = (SCREEN_HEIGHT // 2) - (gameover_text.get_height() // 2)
        screen.blit(gameover_text, [x, y-175])

        screen.blit(esc_text, [(SCREEN_WIDTH // 2) - \
                               (esc_text.get_width() // 2), (y+210)])
        high_score = 0

        #code to read in, check and write the highscore and name to a .txt file,
        #which is then printed out on screen

        f = open("high_score.txt", "r")
        line_list = f.readlines()

        trimmed_line_list = []
        scores = []

        #gets trimmed line list and a scores list
        for line in line_list:
            trimmed_line_list.append(line.strip())
        for line in trimmed_line_list:
            line = line.split()
            scores.append("".join(line[0]))
        f.close()

        #sets current score to current game score
        current_score = self.score

        #gets FINALLIST, removes bottom score and adds new one
        if current_score > int(scores[2]):
            highscore = True
            if highscore == True:
                FINALLIST = " ---- "+(" ---- ".join(trimmed_line_list))+" ---- "
                name = self.initialsname
                for line in trimmed_line_list:
                    line = line.split()
                    if line[0] == scores[2]:
                        trimmed_line_list.remove(("  ".join(line)))
                        
                    
                newhighscore_list = []
                trimmed_line_list.append(str(current_score)+"  "+name)
                newhighscore_list = trimmed_line_list
                
                f = open("high_score.txt", "w")
                f.write("\n".join(trimmed_line_list))
                f.close()

                #opens current file, sorts scores and names into order
                #and writes them back to the file
                f = open("high_score.txt", "r")
                
                line_list = f.readlines()
                trimmed_newline_list = []
                newscores = []
                FINALLIST = []

                for line in line_list:
                    trimmed_newline_list.append(line.strip())
                for line in trimmed_newline_list:
                    line = line.split()
                    newscores.append("".join(line[0]))
                f.close()
                newscores = sorted(newscores, key=int, reverse = True)

                for score in newscores:
                    for line in trimmed_newline_list:
                        if score == ((line.split())[0]):
                            FINALLIST.append(line)
                            trimmed_newline_list.remove(line)
                            break
                f = open("high_score.txt", "w")
                f.write("\n".join(FINALLIST))
                f.close()
                #creates final FINALLIST variable
                FINALLIST = " ---- "+(" ---- ".join(FINALLIST))+" ---- "
                self.listcomplete = True

        #create text variables
        highscoretitle = self.mediumfont.render("Highscores"\
                                                  , True, self.BROWN)
        highscoretext = self.font.render("WELL DONE!!"\
                                                  , True, self.BROWN)
        completetext = self.font.render("YOU HAVE COMPLETED THE GAME!"\
                                                  , True, self.BROWN)
        currenthighscores = self.font.render((str("".join(FINALLIST)))\
                                                  , True, self.BROWN)

        #blit text to screen
        screen.blit(highscoretitle, [(SCREEN_WIDTH // 2) - \
                                 (highscoretitle.get_width() // 2), (y-50)])
        screen.blit(currenthighscores, [(SCREEN_WIDTH // 2) - \
                                 (currenthighscores.get_width() // 2), (y)])
        screen.blit(highscoretext, [(SCREEN_WIDTH // 2) - \
                                 (highscoretext.get_width() // 2), (y+75)])
        screen.blit(completetext, [(SCREEN_WIDTH // 2) - \
                                 (completetext.get_width() // 2), (y+125)])

        pygame.display.update()


    def highscore_logic(self):
        #self.__init__() will quit game at this point as in the loop, running
        #will already be set to false - see below
        keys = pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type == QUIT or keys[pygame.K_ESCAPE] or \
                (e.type == JOYBUTTONDOWN and e.dict == {'button': 13, 'joy': 0}):               
                self.__init__()
        return True
                                

def game_run():
    #initialise pygame
    pygame.init()
    #load main game theme
    pygame.mixer.music.load("maintheme.ogg")
    #set pygame display
    screen = pygame.display.set_mode(SIZE, FLAGS, DEPTH)
    pygame.display.set_caption('JUNGLE RUN!')
    #create instance of Game class
    game = Game()
    #create running loop variable - when it ends, pygame quits
    running = True
    #play music then loop round game until it is quit
    pygame.mixer.music.play(-1)
    #create running loop, run game and check for if running is true
    while running:
        running = game.game_logic()
        game.display_update(screen)
        #while mainmenu run mainmenu with logic, if it goes into instructions
        #then run instructions with logic, if it goes into the game then
        #these variables will be set to false and it will go back to the
        #game running loop
        while game.mainmenu:
            running = game.menuscreen(screen)
            while game.instructions:
                running = game.instruction_screen(screen)
                if running == False:
                    game.instructions = False
            if running == False:
                game.mainmenu = False
        #if game paused, then game pause loop activates, print pause once, then
        #checking for either an unpause or a quit
        while game.gamepause_loop:
            while game.gamepaused:
                game.gamepause_screen(screen)
                game.gamepaused = False
                break
            running = game.gamepause_logic()
            #quits pause loop but can either be running or not affecting next logic
            if running == True:
                game.gamepause_loop = False
            if running == False:
                game.gamepause_loop = False
        #if level complete, start levelcomplete loop, which prints
        #level complete UI to the screen once, then checks for button presses to
        #break out of the loop
        while game.levelcompleteloop:
            while game.levelcomplete:
                if game.levelnumber < 3:
                    game.level_complete_screen(screen)
                    game.levelcomplete = False
                    time.sleep(1)
                    break
            running = game.level_complete_logic()
            if not running:
                game.levelcompleteloop = False                
        #if level complete, start levelcomplete loop, which prints
        #level complete UI to the screen once, then checks for button presses to
        #break out of the loop - to quit or restart game
        while game.gameoverloop:
            while game.gameover:
                game.game_over_screen(screen)
                game.gameover = False
                time.sleep(1)
                break
            running = game.game_over_logic()
            if not running:
                game.gameoverloop = False
        #set game complete loop up with game complete screen and options to quit
        #or go to enter name screen
        while game.gamecomplete:
            game.gamecomplete_screen(screen)
            running = game.gamecomplete_logic()
            if game.enternamescreen:
                game.gamecomplete = False
            if not running:
                game.gamecomplete = False
        #start new loop to enter name, if you enter name, the else statement
        #will be activated and the game will show you your score. Then
        #when the user presses quit, the game will quit as running has already been
        #set to false
        while game.enternamescreen:
            if running:
                running = game.entername_screen(screen)
            else:
                if not game.listcomplete:
                    game.highscore_screen(screen)
                game.highscore_logic()

    pygame.quit()
    
game_run()
