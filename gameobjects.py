import pygame
from imageLoader import *
import random
import math

playerRespawnDelay= 120 #Ticks (Frames till the event)

class Background(pygame.sprite.Sprite):
    def __init__(self,image, width, height):
        self.originalAsset= pygame.image.load(image)
        self.image= pygame.transform.scale(self.originalAsset, (width,height) )
        self.rect= self.image.get_rect()

    def update(self):
        return
    
class Player(pygame.sprite.Sprite):
    def __init__(self, image, scale, clip, explosionSFX):
        self.asset= imageLoader(image, scale, clip)
        self.image= self.asset
        self.imageColorKey= (0,0,0)
        self.explosionColorKey= 0x454e5b
        self.rect= self.image.get_rect()
        self.rect.x= 400
        self.rect.y= 300
        self.velocityX= 0
        self.velocityY= 0
        self.accelerationX= 0.0
        self.accelerationY= 0.0
        self.thrust= 0.5
        self.damping= 0.3
        self.angle= 0
        self.maxVelocity= 6
        self.collision= False
        self.collisionGroup= []
        self.isWaitingToRespawn=False
        self.waitingToRespawn= 0
        self.explosionSFX= explosionSFX
        self.loadExplosionAnimation()
        self.onSpawn()

    def loadExplosionAnimation(self):
        self.explosionFrames= []
        self.explosionCurrentFrame= 0
        frameWidth= 24
        for i in range(0,6):
            self.explosionFrames.append(imageLoader("images/Explode4.bmp", 2, (frameWidth*i,0,24,25)))

    def onSpawn(self):
        self.reset()

    def onDeath(self):
        self.isWaitingToRespawn=True
        self.waitingToRespawn= playerRespawnDelay
        self.explosionCurrentFrame= 0
        self.explosionSFX.play()

    def reset(self):
        self.rect.x= 400
        self.rect.y= 300
        self.velocityX= 0
        self.velocityY= 0
        self.accelerationX= 0.0
        self.accelerationY= 0.0
        self.collision= False
    
    def update(self):
        #Process Delayed Events
        if self.isWaitingToRespawn:
            #Update Explosion animation (Player is Dead)
            if self.explosionCurrentFrame <= len(self.explosionFrames)-1:
                self.image= self.explosionFrames[self.explosionCurrentFrame]
                self.image.set_colorkey(self.explosionColorKey)
                self.explosionCurrentFrame+=1
            else:
                pygame.Surface((0,0))
                
            self.waitingToRespawn-= 1
            if self.waitingToRespawn<=0:
                self.isWaitingToRespawn= False
                self.reset()
        else:        
            #Process Player Input
            control= self.getPlayerInput()
            angle= self.processControls(control)
            self.image= pygame.transform.rotate(self.asset, self.angle)
            self.image.set_colorkey(self.imageColorKey)

            #Collision Detection
            self.checkForCollision()
            
            #Update Physics
            self.updatePhysics()

    def checkForCollision(self):
        for gameObject in self.collisionGroup:
            self.collision = self.rect.colliderect(gameObject.rect)
            if self.collision:
                self.onDeath()
                for gameObject in self.collisionGroup:
                    gameObject.onDeath()
                break

    def getPlayerInput(self):
        up= pygame.key.get_pressed()[pygame.K_UP]
        right= pygame.key.get_pressed()[pygame.K_RIGHT]
        down= pygame.key.get_pressed()[pygame.K_DOWN]        
        left= pygame.key.get_pressed()[pygame.K_LEFT]
        
        return up, left, down, right

    def updatePhysics(self):
        self.velocityX+= self.accelerationX
        self.velocityY+= self.accelerationY
        
        #Apply Damping Horizontal
        if self.velocityX< 0 -  self.damping:
            self.velocityX+= self.damping
        elif self.velocityX> 0+ self.damping:
            self.velocityX-= self.damping
        else:
            self.velocityX=0

        #Apply Damping Horizontal
        if self.velocityY< 0 -  self.damping:
            self.velocityY+= self.damping
        elif self.velocityY> 0+ self.damping:
            self.velocityY-= self.damping
        else:
            self.velocityY=0

        #Terminal Velocity
        if self.velocityX> self.maxVelocity:
            self.velocityX= self.maxVelocity
        if self.velocityX< self.maxVelocity*-1:
            self.velocityX= self.maxVelocity*-1        
        if self.velocityY> self.maxVelocity:
            self.velocityY= self.maxVelocity
        if self.velocityY< self.maxVelocity*-1:
            self.velocityY= self.maxVelocity*-1  
        
        self.rect.x+= self.velocityX
        self.rect.y+= self.velocityY

    def processControls(self, control):
        #self.angle=0
        
        if control[0]==1 and control[1]==0 and control[2]== 0 and control[3]==0:
            self.angle= 0
        elif control[0]==1 and control[1]==1 and control[2]== 0 and control[3]==0:
            self.angle= 45
        elif control[0]==0 and control[1]==1 and control[2]== 0 and control[3]==0:
            self.angle= 90
        elif control[0]==0 and control[1]==1 and control[2]== 1 and control[3]==0:
            self.angle= 135
        elif control[0]==0 and control[1]==0 and control[2]== 1 and control[3]==0:
            self.angle= 180
        elif control[0]==0 and control[1]==0 and control[2]== 1 and control[3]==1:
            self.angle= 225
        elif control[0]==0 and control[1]==0 and control[2]== 0 and control[3]==1:
            self.angle= 270
        elif control[0]==1 and control[1]==0 and control[2]== 0 and control[3]==1:
            self.angle= 315
        
        self.accelerationX= self.thrust*(control[3]-control[1])
        self.accelerationY= self.thrust*(control[2]-control[0])


        
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, scale, clip, bounds, gameObjectTarget, waveManager):
        self.image= imageLoader(image,scale, clip)
        self.image.set_colorkey(0x454e5b)           #makes bg transparent
        self.rect= self.image.get_rect()
        self.rect.x= 200
        self.rect.y= 500
        self.velocityX= 0
        self.velocityY= 0
        self.damping= 0.3
        self.maxVelocity= 4
        self.thrust= 0.5
        self.accelerationX= 0
        self.accelerationY= 0
        self.boundX= bounds[0]
        self.boundY= bounds[1]
        self.isWaitingToRespawn= False
        self.waitingToRespawn= 0
        self.target= gameObjectTarget
        self.state=1
        self.waveManager= waveManager
        self.reset()
        
    def onSpawn(self):
        self.reset()
    
    def onDeath(self):
        self.isWaitingToRespawn= True
        self.waitingToRespawn= playerRespawnDelay
        self.waveManager.enemyHasDied()

    def reset(self):
        if self.waveManager.allowSpawn():
            self.rect.x= -1*random.randrange(0,self.boundX)
            self.rect.y= -1*random.randrange(0,self.boundY)
            self.velocityX= 0
            self.velocityY= 0
            self.state=1
            self.waveManager.enemyHasSpawned()
        else:
            self.resetOffScreen()
            self.waveManager.addWaitingSpawn(self)

    def resetOffScreen(self):
        self.rect.x= self.boundX
        self.rect.y= self.boundY
        
    def update(self):
        #Process Delayed Events
        if self.isWaitingToRespawn:
            self.waitingToRespawn-= 1
            if self.waitingToRespawn<=0:
                self.isWaitingToRespawn= False
                self.reset()
        else:
            self.processStates()
            
            #Apply Damping Horizontal
            if self.velocityX< 0 -  self.damping:
                self.velocityX+= self.damping
            elif self.velocityX> 0+ self.damping:
                self.velocityX-= self.damping
            else:
                self.velocityX=0

            #Apply Damping Vertical
            if self.velocityY< 0 -  self.damping:
                self.velocityY+= self.damping
            elif self.velocityY> 0+ self.damping:
                self.velocityY-= self.damping
            else:
                self.velocityY=0
                
            #Terminal Velocity
            if self.velocityX> self.maxVelocity:
                self.velocityX= self.maxVelocity
            if self.velocityX< self.maxVelocity*-1:
                self.velocityX= self.maxVelocity*-1        
            if self.velocityY> self.maxVelocity:
                self.velocityY= self.maxVelocity
            if self.velocityY< self.maxVelocity*-1:
                self.velocityY= self.maxVelocity*-1  

            #Update Position
            self.rect.x+= self.velocityX
            self.rect.y+= self.velocityY

            #Check the Enemy Bound
            if self.rect.x > self.boundX or self.rect.y>self.boundY:
                self.onDeath()
                
    def processStates(self):
        #Get Target Vector
        targetVectorX= self.target.rect.x - self.rect.x
        targetVectorY= self.target.rect.y - self.rect.y
        distance= math.sqrt((targetVectorX)**2+(targetVectorY)**2)
        targetVectorX /= distance
        targetVectorY /= distance
        #State 1- Search
        if self.state==1:
            #Check if Target is in range
            if distance<= 300:
                self.state=2
            else:
                self.velocityX+= self.thrust
            self.velocityY+= self.thrust
        #State 2- Chase Player
        elif self.state==2:
            #Check if Target is out of range
            if distance>300:
                self.state==3
            else:
                #Appy Target Thrust
                self.velocityX+= targetVectorX*self.thrust
                self.velocityY+= targetVectorY*self.thrust
        #State 3- Lost Chase
        elif self.state==3:
            self.velocityX+= self.thrust
            self.velocityY+= self.thrust
            
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, image, scale, clip, bounds):
        self.image= imageLoader(image, scale, clip)
        self.image.set_colorkey(0x454e5b)
        self.rect= self.image.get_rect()
        self.rect.x= 100
        self.rect.y= 400
        self.velocityX= 6
        self.velocityY= 6
        self.accelerationX= 0
        self.accelerationY= 0
        self.boundX= bounds[0]
        self.boundY= bounds[1]
        self.isWaitingToRespawn= False
        self.waitingToRespawn= 0
        self.onSpawn()

    def onSpawn(self):
        self.reset()
    
    def onDeath(self):
        self.isWaitingToRespawn= True
        self.waitingToRespawn= playerRespawnDelay
    
    def reset(self):
        self.rect.x= -1*random.randrange(0,self.boundX)
        self.rect.y= -1*random.randrange(0,self.boundY)
        
    def update(self):
        #Process Delayed Events
        if self.isWaitingToRespawn:
            self.waitingToRespawn-= 1
            if self.waitingToRespawn<=0:
                self.isWaitingToRespawn= False
                self.reset()
        else:
            self.velocityX+= self.accelerationX
            self.velocityY+= self.accelerationY
            self.rect.x+= self.velocityX
            self.rect.y+= self.velocityY

            if self.rect.x > self.boundX or self.rect.y>self.boundY:
                self.onDeath()

class WaveManager():
    def __init__(self):
        self.currentWave= 1
        self.enemySpawnedCount= 0
        self.enemyDeathCount= 0
        self.enemiesPerWave= 3
        self.waitingToSpawn= []
        self.score= 0
        
    def allowSpawn(self):
        if self.enemySpawnedCount >= self.enemiesPerWave:
            return False
        else:
            return True

    def enemyHasSpawned(self):
        self.enemySpawnedCount+=1

    def enemyHasDied(self):
        self.enemyDeathCount+=1
        self.score+=1
        if self.enemyDeathCount == self.enemiesPerWave:
            self.nextWave()

    def nextWave(self):
        self.enemySpawnedCount= 0
        self.enemyDeathCount= 0
        self.enemiesPerWave+=3
        self.currentWave+=1

    def addWaitingSpawn(self,gameObject):
        self.waitingToSpawn.append(gameObject)

    def update(self):
        if self.allowSpawn():
            for gameObject in self.waitingToSpawn:
                gameObject.reset()



















        
