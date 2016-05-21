from tkinter import *
import math
from random import randint

root = Tk()
canvas = Canvas(root, width = 600, height = 600)
canvas.pack()

regType = dict()#this list contains all the types of regions

def regionRatio():#this method converts the percentage of zones into fractal ratios
    return 0

class lines:#this class is for the line element objects
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
    def __init__(self, regSize, regType, regPosition, toRender = True):
        self.size = regSize
        self.type = regType
        self.pos = regPosition
        self.graphic = None

        self.child = [] #this is a list of children of this region

        if toRender:
            self.render()

    def tessellate(self, genNum=1):
        if genNum <= 0:
            self.render()
            return 0

        #now counting the number of childrem
        childNum = 0
        for rType in self.type.comp:
            childNum += self.type.comp[rType]

        childSize = self.size/math.sqrt(childNum)
        weirdChildNum = randint(0,childNum-1)
        #done counting the number of childrem

        #print(childNum)

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

            newChild = region(childSize, childType, childPos, False)
            self.child.append(newChild)

            newChild.tessellate(genNum-1)

            #print(str(c+1)+'th child at '+str(childPos))

            c += 1
            

    def render(self):
        endPos = [self.pos[0]+self.size, self.pos[1]+self.size]
        self.graphic = canvas.create_rectangle(self.pos[0], self.pos[1], endPos[0], endPos[1], fill=self.type.color, outline = self.type.color)
        #print(self.pos, self.size)
        

commercialComp = {'commercial':8, 'nonCommercial':1}
nonCommercialComp = {'nonCommercial':8, 'commercial':1}

commercial = regionType('commercial', '#ff0000', 1, commercialComp)
nonCommercial = regionType('nonCommercial', '#0000ff', -1, nonCommercialComp)

city = region(600, nonCommercial, [0,0], False)
city.tessellate(1)

root.mainloop()

#quit()
