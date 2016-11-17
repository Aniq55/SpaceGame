import pygame
from gameobjects import *
from imageLoader import *

pygame.init()
music=pygame.mixer.Sound("sounds/intro.wav")
music.play(-1)
explosion=pygame.mixer.Sound("sounds/explosion.wav")

clock= pygame.time.Clock()
screen= pygame.display.set_mode((800,600))

gameObjects= []


background= Background("images/Nebula1.bmp", screen.get_width(), screen.get_height())

player= Player("images/Hunter1.bmp",2, (25,1,23,23), explosion)
gameObjects.append(player)

waveManager= WaveManager()


enemies=[]
for i in range(3):
    enemy= Enemy("images/SpacStor.bmp", 1, (101,13,91,59), (screen.get_width()+80, screen.get_height()+67), player, waveManager)
    enemies.append(enemy)
    gameObjects.append(enemy)
    player.collisionGroup.append(enemy)

asteroids=[]
for i in range(5):
    asteroid= Asteroid("images/Rock2a.bmp",1, (6,3,80,67), (screen.get_width()+80, screen.get_height()+67))
    asteroids.append(asteroid)
    gameObjects.append(asteroid)
#    player.collisionGroup.append(asteroid)

scoreboardFrames= []
numbersWidth= 30
for i in range(0,10):
    scoreboardFrames.append(imageLoader("images/numbers.bmp",1,(numbersWidth*i,0,30,49)))
    scoreboardFrames[i].set_colorkey((0,0,0))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
            
    #Update Wave Manager
    waveManager.update()
    
    #Update Objects
    for gameObject in gameObjects:
        gameObject.update()
            
    #Render
    if player.collision:
        screen.fill((30,10,0))
    else:
        screen.blit(background.image, (0,0))
    for gameObject in gameObjects:
        screen.blit(gameObject.image, (gameObject.rect.x, gameObject.rect.y))

    #Render out Score
    lastDigit= waveManager.score %10
    secondDigit= int((waveManager.score/10)) %10
    firstDigit= int((waveManager.score/100)) %10
    screen.blit(scoreboardFrames[firstDigit], (0,0))
    screen.blit(scoreboardFrames[secondDigit], (30,0))
    screen.blit(scoreboardFrames[lastDigit], (60,0))

    #Render out current wave
    lastDigit= waveManager.currentWave %10
    secondDigit= int((waveManager.currentWave/10)) %10
    firstDigit= int((waveManager.currentWave/100)) %10
    screen.blit(scoreboardFrames[firstDigit], (710,0))
    screen.blit(scoreboardFrames[secondDigit], (740,0))
    screen.blit(scoreboardFrames[lastDigit], (770,0))
    
    pygame.display.flip()

    #Waste Extra Work
    clock.tick(60)
 
