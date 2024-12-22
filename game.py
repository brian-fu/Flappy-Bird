# Brian Fu
# December 2022
# ICS3O0
# Flappy Bird Using Python's Pygame Library

# IMPORTANT -> MAKE SURE ALL MEDIA FILES ARE LOCATED IN THE SAME FOLDER AS THE .py FILE

# Import Libraries:
import pygame
import random


pygame.init() # Initialize Pygame window
pygame.mixer.init()


# INITIALIZE FILE FOR SCORE KEEPING 
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

highScore = 0 
try: #initialize inventory file
    with open("high_score.txt", "r") as file:
        highScore = int(file.readline()) 

# Error handling
except FileNotFoundError:
    with open("high_score.txt", "x") as file: file.write("0")

except ValueError:
    with open("high_score.txt", "w") as file: file.write("0")

# Records score into txt file    
def recordScore():
    global score, highScore
    with open("high_score.txt", "w") as file:
        if score >= highScore:
            file.truncate(0)
            file.write(str(score))



# DEFINING CLASSES 
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

class Window: 
    screen = pygame.display.set_mode()
    width, height = screen.get_size() # Finds the window size of the given monitor and sets variables to it
    floor_Y = (height * 0.90279) # Sets the Y value of the floor

    load = pygame.image.load("background.png")
    background = pygame.transform.scale(load, (width , height)) # Resizes background image to screen size

    load = pygame.image.load("floor.png")
    floor = pygame.transform.scale(load, (width, height * 0.0926)) # Sets the size of the floor

    load = pygame.image.load("control_indicator.png")
    control_indicator = pygame.transform.scale(load, (width * 0.181, height * 0.185)) # Sets the size of the control indicator

    load = pygame.image.load("resume_button.png")
    resume = pygame.transform.scale(load, (width * 0.186, height * 0.185)) # Sets the size of the resume button

    load = pygame.image.load("scoreboard.png")
    scoreboard = pygame.transform.scale(load, (width * 0.26 , height * 0.234)) # Sets the size of the scoreboard

    load = pygame.image.load("new_best.png")
    new_best = pygame.transform.scale(load, (width * 0.0313, height * 0.025)) # Sets the size of the new best indicator


class Bird: 
    x,y = Window.width * 0.1953 , Window.height * 0.478 # x and y position of Bird
    width = Window.width * 0.05208 # Width of the bird
    height = Window.height * 0.06822 # Height of the bird

    load = pygame.image.load("bird.png") 
    img = pygame.transform.scale(load, (width, height)) # Loads the bird image 
    point = pygame.mixer.Sound("point.mp3") # Sound played when the user gets a point
    death = pygame.mixer.Sound("death.mp3") # Sound played when the user dies 

class Pipedown:
    width = Window.width * 0.052
    height = Window.height * 0.3 
    load = pygame.image.load("pipeDown.png") 
    img = pygame.transform.scale(load, (width, height)) # Sets the size of the downward pipe image

class Pipeup:
    width = Window.width * 0.052
    height = Window.height * 0.3
    load = pygame.image.load("pipeUp.png")
    img = pygame.transform.scale(load, (width, height)) # Sets the size of the downward pipe image

class Coin:
    # Loads and sets the size of all the medals (Bronze, Silver, Gold)
    width = Window.width * 0.0469
    height = Window.height * 0.083

    load = pygame.image.load("medal_bronze.png") 
    bronze = pygame.transform.scale(load, (width, height))

    load = pygame.image.load("medal_silver.png")
    silver = pygame.transform.scale(load, (width, height))

    load = pygame.image.load("medal_gold.png")
    gold = pygame.transform.scale(load, (width, height))




# SPAWNING AND MOVING THE PIPES TO THE LEFT 
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

moveSpeed = Window.width * 0.00186 # Rate in which the pipes move to the left

pipe_X = [] # x value of the pipes
def setPipe_X():
    for i in range (10):
        pipe_X.append(((i*0.143 + 1) * Window.width))

# Arrays that stores the images of the pipes 
pipe_upImg = []
pipe_downImg = []

gap = 0.65 # Value of gap between the up and down pipes

# Generates an array with varying sizes of pipes 
def generatePipeSize():
    for i in range (len(pipe_X)):
        # Ensures that the margin of room between each set of pipes is the same throughout 
        tmp = random.randint(int(Window.height * 0.093), int(Window.height * 0.47))
        # Appends an image with a random height value into an array 
        pipe_upImg.append(pygame.transform.scale(Pipeup.img, (Pipeup.width, (tmp))))
        # Appends an image with a height of Window height * gap - up img height to ensure that the margin of room between each pair of pipes is always the same even with varying heights
        pipe_downImg.append(pygame.transform.scale(Pipedown.img, (Pipedown.width, (Window.height * gap - tmp))))

# Calls functions to initialize pipes
setPipe_X()
generatePipeSize()

# Updates the position and size of the pipes
def updatePipe():
    for i in range (len(pipe_X)):
        pipe_X[i] -= moveSpeed # Pipe moves to the left at the rate of the movement speed 

        # Checks if ith pipe is off the screen 
        if pipe_X[i] <= -(Window.width * 0.10417):
            # If it is, moves the pipe from the very left to off the screen on the right
            pipe_X[i] = (Window.width * 1.328125)
            # Generates new pipe sizes for the ith pipe that is off the screen (Ensures that there is variation in the pipe positions)
            tmp = random.randint(int(Window.height * 0.093), int(Window.height * 0.47))
            pipe_upImg[i] = (pygame.transform.scale(Pipeup.img, (Pipeup.width, (tmp))))
            pipe_downImg[i] = (pygame.transform.scale(Pipedown.img, (Pipedown.width, (Window.height * gap - tmp))))

# x position of the 2 floor images - First one starts on screen and second one starts just off screen and both move to the left at the same rate as the pipes
floor_X = [0,(Window.width)]
def moveFloor():
    global floor_X
    for i in range (len(floor_X)):
        floor_X[i] -= moveSpeed
        # Checks if the entire image of the floor is off the screen
        if floor_X[i] <= -(Window.width):
            # Sets the position of the ith image to just off the screen
            floor_X[i] = Window.width
        



# COLLISION DETECTION
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
deathSoundPlayed = False # Bool variable to ensure that the death sound is only played once upon dying 
point_passed = False # Bool variable to ensure that each point is only counted once
new_best = False # Bool variable that is used to determine whether the user achieved a new best

# Checks to see if user has collided with any obstacle / floor & roof
def checkCollision():
    global active, alive, deathSoundPlayed, point_passed, score, highScore, floor_move, dead, new_best
    for i in range(len(pipe_X)):
        # Collision detection for roof and floor
        if (Bird.y < 0 or Bird.y > Window.floor_Y - Bird.height) or ((Bird.x >= (pipe_X[i] - Window.width * 0.038) # Collision detection for pipes
        and Bird.x <= (pipe_X[i] + Window.width * 0.038)) and ((Bird.y < (Window.height - pipe_upImg[i].get_height() - Window.height* 0.18)) and (Bird.y > pipe_downImg[i].get_height())) == False): 
            active, alive = False, False # Switches bool variables which stops the movement of objects
            # Ensures that the deathsound is only played once
            if not deathSoundPlayed:
                Bird.death.play() # Death sound
                dead, deathSoundPlayed, floor_move = True, True, False 
                recordScore() # Score is recorded
            if Bird.y > Window.floor_Y - Bird.height:
                    Jump.falling = False # Once the bird reaches the ground, it stops Jump.falling is set to false to prevent the bird from falling through the floor

        elif ((Bird.x >= (pipe_X[i] - Window.width * 0.02) and Bird.x <= (pipe_X[i] + Window.width * 0.038)) and ((Bird.y < (Window.height - pipe_upImg[i].get_height() - Window.height* 0.18)) and (Bird.y > pipe_downImg[i].get_height())) == True):
            if not point_passed: # Bool flag that ensures the sound is only played once, and the score is only increased by one
                Bird.point.play()
                point_passed = True
                score += 1
                if active and score > highScore: # Checks and updates high score
                    highScore = score
                    new_best = True
        
        # Checks to see if the bird is a little bit ahead of the previous pipe, if yes, the point_passed variable is switched back to false
        elif (Bird.x >= (pipe_X[i] + Window.width * 0.038) and Bird.x <= (pipe_X[i] + Window.width * 0.04)):
            point_passed = False




# JUMPING
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

class Jump:
    jumping, falling = False, False # Bool variables for whether the bird is jumping or falling
    strength = Window.height * 0.0107 # Strength of the jump
    speed = 0 # Speed that the bird is moving at
    sound = pygame.mixer.Sound("jump.mp3") # Jump sound that plays each time the user jumps
    sound.set_volume(0.25) # Lowers volume of jump sound

# Variables used to store jumping values when game is paused
class Pause:
    jumping, falling, speed = 0, 0, 0

# Rate the bird falls at
gravity = Window.height * 0.000648 

# Updates values while jumping
def updateJump():
    if Jump.jumping:
        Bird.y -= Jump.speed # Bird's y position is updated based on jump speed
        Jump.speed -= gravity # Jump speed decreases the higher it goes
        if Jump.speed <= 0:
            # Start falling when the jumping speed becomes zero or negative
            Jump.falling = True
            Jump.jumping = False

    elif Jump.falling:
        Bird.y += Jump.speed # Bird's y position is updated based on jump speed
        Jump.speed += gravity # Acceleration due to gravity 

# Variable changes when user 
def jumpClicked():
    Jump.jumping = True
    Jump.speed = Jump.strength
    Jump.sound.play()

    
 

# RESTARTING, PAUSING, RESUMING GAME
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

paused = False # Bool variable that determines if game is paused or not

def pauseGame():
    global alive, active, floor_move, paused
    # Temporarily stores the movement values 
    Pause.jumping = Jump.jumping
    Pause.falling = Jump.falling
    Pause.speed = Jump.speed
    # Sets all movement off
    paused, alive, floor_move, active, Jump.jumping, Jump.falling, Jump.speed = True, False, False, False, False, False, 0

    
def resumeGame():
    # Resumes the game by re-assigning the movement variables with the previous values stored in the pause class
    global alive, active, floor_move, paused
    Jump.jumping = Pause.jumping
    Jump.falling = Pause.falling
    Jump.speed = Pause.speed
    alive, floor_move, active, paused = True, True, True, False # Variables are re assigned 

def restartGame():
    global pipe_X, pipe_upImg, pipe_downImg, active, alive, floor_move, isIdling, startScreen, score, deathSoundPlayed, point_passed, paused, dead, new_best
    # Resets the pipe positions and sizes and new locations and sizes are generated 
    pipe_X, pipe_upImg, pipe_downImg = [], [], []
    setPipe_X()
    generatePipeSize()
    # Resets bool variables
    Jump.jumping, Jump.falling, deathSoundPlayed, point_passed, active, paused, dead, new_best = False, False, False, False, False, False, False, False
    alive, floor_move, isIdling, startScreen  = True, True, True, True
    Jump.speed, score = 0, 0
    Bird.x, Bird.y = (Window.width * 0.1953), (Window.height * 0.478) # Resets Bird Position
   
# When game is paused, checks if the user clicks on the resume button 
def checkClick():
    mouse_pos = pygame.mouse.get_pos()
    if (mouse_pos[0] >= (Window.width * 0.186 + Window.resume.get_width())) and (mouse_pos[0] <= (Window.width * 0.186 + Window.resume.get_width() * 2)) and (mouse_pos[1] >= (Window.height * 0.185 + Window.resume.get_height())
    and mouse_pos[1] <= (Window.height * 0.185 + 2 * Window.resume.get_height())):
        resumeGame()

# Idle animatation at the start of the game that moves the bird up and down
idleVal = 0
def idling():
    global idleVal
    if idleVal < 50:
        Bird.y -= 0.5 # Moves the bird upward
        idleVal += 1
    elif idleVal >= 50 and idleVal <= 100:
        Bird.y += 0.5 # Moves the bird downward
        idleVal += 1
    else: idleVal = 0  # Resets value so the bird goes back to moving upward


# DRAWING SCREEN
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

# initialize fonts
score_font = pygame.font.Font("text.ttf", round(Window.width * 0.052))
subtitle_font = pygame.font.Font("text.ttf", round(Window.width * 0.015))
menu_font = pygame.font.Font("text.ttf", round(Window.width * 0.026))
title_font = pygame.font.Font("title.ttf", round(Window.width * 0.15625))
score = 0

# Text that is constant 
title_txt = title_font.render("Brifus Flappy Bird", True, (255,255,255))
pause_txt = subtitle_font.render("[ESC] to pause", True, (255,255,255))
restart_txt = subtitle_font.render("[ENTER] to restart", True, (255,255,255))
exit_txt = subtitle_font.render("[BACKSPACE] to exit", True, (255,255,255))

# Displays the commands available to the user
def showControls():
    screen.blit(exit_txt, (0, 0))
    screen.blit(pause_txt, (0, Window.height * 0.037))
    screen.blit(restart_txt, (0, Window.height * 0.074))

# Pop ups when user dies
def showMenu():
    showControls() # Displays controls
    
    menu_score = menu_font.render(str(score), True, (255,255,255)) # Updates the scores to be displayed 
    menu_highScore = menu_font.render(str(highScore), True, (255,255,255))

    screen.blit(Window.scoreboard, (Window.width * 0.3646, Window.height * 0.3241)) # Displays scoreboard

    # Determines what medal to display based off user's score
    if score >= 0 and score <= 15:
        screen.blit(Coin.bronze, (Window.width * 0.3974, Window.height * 0.4139))
    elif score > 15 and score < 30:
        screen.blit(Coin.silver, (Window.width * 0.3974, Window.height * 0.4139))
    elif score >= 30:
        screen.blit(Coin.gold, (Window.width * 0.3974, Window.height * 0.4139))

    if new_best: 
        screen.blit(Window.new_best, (Window.width * 0.521, Window.height * 0.4454)) # If the user achieved a new high score, "New Best" indicator 

    screen.blit(menu_score, (Window.width * 0.573, Window.height * 0.394)) # Displays score
    screen.blit(menu_highScore, (Window.width * 0.573, Window.height * 0.481)) # Displays high score

# Function that draws the screen
def drawScreen():
    global title_txt, pause_txt, restart_txt, exit_txt
    screen.fill((0,0,0)) # Clears the screen 
 
    screen.blit(Window.background, (0, 0)) # Sets the background

    for i in range (len(floor_X)):
        screen.blit(Window.floor, (floor_X[i], Window.floor_Y)) # Sets position of floor

    # Sets position of pipe
    for i in range (len(pipe_X)):
        screen.blit(pipe_upImg[i], (pipe_X[i], (Window.height - pipe_upImg[i].get_height() - Window.height* 0.09259)))
        screen.blit(pipe_downImg[i], (pipe_X[i], 0))

    # Updates the score text
    score_txt = score_font.render(str(score), True, (255,255,255))
    highScore_txt = subtitle_font.render("High Score: " + str(highScore), True, (255,255,255))

    # Sets the position of the score text
    if not startScreen and not dead:
        screen.blit(score_txt, ((Window.width / 2.2), (Window.height * 0.19)))
        screen.blit(highScore_txt, ((Window.width / 2.4), (Window.height * 0.3)))
    
    # Sets bird position
    screen.blit(Bird.img, (Bird.x, Bird.y))
    
    # Sets position of title and controls 
    if startScreen:
        screen.blit(Window.control_indicator, (Window.width / 2.65, Window.height * 0.45))
        screen.blit(title_txt, ((Window.width / 6.8), (Window.height * 0.2)))
        showControls()
    
    # Sets position of resume key and displays controls
    if paused:
        screen.blit(Window.resume, ((Window.width / 2.65, Window.height * 0.4)))
        showControls()

    # Calls function that shows menu upon death 
    if dead:
        showMenu()
    
    # Flips the screen
    pygame.display.flip()
    # Sets the frame rate
    clock.tick(60)


# INITIALIZE FOR MAIN GAME LOOP 
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
pygame.display.set_caption("Brifu's Flappy Bird") # Sets window caption
window_size = (Window.width, Window.height) # Sets window size
screen = pygame.display.set_mode(window_size) # Initializes screen 


# Bool for main game loop
active = False
alive = True
floor_move = True 
isIdling = True
startScreen = True
dead = False 

clock = pygame.time.Clock()

running = True
# MAIN GAME LOOP
while running:
    # Handle events
    for event in pygame.event.get(): 
        if (event.type == pygame.KEYDOWN): # Checks for keydown
            if alive: # If user is alive, program will look for further keypresses 
                if (event.key == pygame.K_SPACE): 
                    if not active: # Initial bool variable that checks to see if board is moving
                        active, floor_move, isIdling, startScreen,  = True, True, False, False
                    jumpClicked()

            # If the game isn't on the start screen, it will allow the user to pause and resume the game
            if not startScreen:
                if event.key == pygame.K_ESCAPE and alive: # Pauses the game
                    pauseGame()

            if event.key == pygame.K_RETURN: # Restarts the game
                restartGame()

            if event.key == pygame.K_BACKSPACE: # Exits the game
                pygame.quit()
                quit()
            
           
        # Same thing as when when the user clicks space just for mouse button
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            if alive: 
                if not active: # Initial bool variable that checks to see if board is moving
                    active, floor_move, isIdling, startScreen,  = True, True, False, False
                jumpClicked()

            elif paused:
                checkClick()

    updateJump()
        
    drawScreen()
    
    checkCollision() 
    
    if active: updatePipe()
    
    if floor_move: moveFloor() 

    if isIdling: idling()
        
        