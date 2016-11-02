import pygame
import math
from random import randint

pygame.init()
canvas = pygame.display.set_mode((600,600))#this will return pygame.surface object

regType = dict()#this list contains all the types of regions

def regionRatio():#this method converts the percentage of zones into fractal ratios
    return 0

class lines:
    def __init__(self, endPt1, endPt2, affinity):
        self.end1 = endPt1
        self.end2 = endPt2
        self.aff = affinity

    def render(self):#this method renders the line element on screen
        #render it here and remove the following return 0 statement
        return 0

class regionType:
    def __init__(self, typeName, typeColor, affinity, composition):
        self.name = typeName
        self.color = typeColor
        self.aff = affinity

        self.comp = composition

        regType[self.name] = self

class region:
    def __init__(self, regSize, regType, regPosition):
        self.size = regSize
        self.type = regType
        self.pos = regPosition

        self.child = [] #this is a list of children of this region

        self.render()

    def tessellate(self, genNum=1):
        if genNum <= 0:
            return 0
        
        childNum = 0
        for rType in self.type.comp:
            childNum += self.type.comp[rType]

        childSize = self.size/math.sqrt(childNum)
        weirdChildNum = randint(0,childNum-1)

        c = 0
        while c < childNum:
            colNum = c % math.sqrt(childNum)
            rowNum = (c-colNum)/math.sqrt(childNum)
            childPos = [self.pos[0] + colNum*childSize, self.pos[1] + rowNum*childSize]

            childType = self.type

            if c == weirdChildNum:
                if self.type.name == 'commercial':
                    childType = regType['nonCommercial']
                elif self.type.name == 'nonCommercial':
                    childType = regType['commercial']

            newChild = region(childSize, childType, childPos)
            self.child.append(newChild)

            newChild.tessellate(genNum-1)

            #print(str(c+1)+'th child at '+str(childPos))

            c += 1
            

    def render(self):
        canvas.fill(self.type.color, rect=[self.pos[0], self.pos[1], self.size, self.size])
        pygame.display.flip()

white = (255,255,255)
red = (255,0,0)
blue = (0,0,255)
black = (0,0,0)

commercialComp = {'commercial':8, 'nonCommercial':1}
nonCommercialComp = {'nonCommercial':8, 'commercial':1}

commercial = regionType('commercial', red, 1, commercialComp)
nonCommercial = regionType('nonCommercial', blue, -1, nonCommercialComp)

city = region(600, nonCommercial, [0,0])
city.tessellate(5)

exitCanvas = False
while not exitCanvas:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exitCanvas = True

pygame.quit()
#quit()
