from tkinter import *
import math
from random import randint
import planeVec as pv

root = Tk()
root.title('City Simulator')
canvas = Canvas(root, width = 600, height = 600)
canvas.pack()

regType = dict()#this list contains all the types of regions

def exportCanvas(fileName):
    canvas.update()
    canvas.postscript(file = fileName+'.eps', colormode='color')

def regionRatio():#this method converts the percentage of zones into fractal ratios
    return 0

class line:#this class is for the line element objects
    def __init__(self, pointArray, affinity):
        self.point = pointArray
        self.aff = affinity
        self.graphic = None

    def render(self):#this method renders the line element on screen
        #render the line element here
        self.graphic = canvas.create_line(self.point, fill='black', width = 3)

    def delete(self):
        canvas.delete(self.graphic)
        self.graphic = None

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
        self.parent = None

        if toRender:
            self.render()

    def hasPoint(pos): #returns true or false on whether the point pos is in the region or not
        checkXLims = pos[0] >= self.pos[0] and pos[0] <= self.pos[0]+self.size
        checkYLims = pos[1] >= self.pos[1] and pos[1] <= self.pos[1]+self.size
        
        if checkXLims and checkYLims:
            return True
        else:
            return False

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
            newChild.parent = self

            newChild.tessellate(genNum-1)

            #print(str(c+1)+'th child at '+str(childPos))

            c += 1
            

    def render(self):
        endPos = [self.pos[0]+self.size, self.pos[1]+self.size]
        self.graphic = canvas.create_rectangle(self.pos[0], self.pos[1], endPos[0], endPos[1], fill=self.type.color, outline = self.type.color)
        #print(self.pos, self.size)

    def delete(self):
        canvas.delete(self.graphic)
        self.graphic = None
        

commercialComp = {'commercial':8, 'nonCommercial':1}
nonCommercialComp = {'nonCommercial':8, 'commercial':1}

commercial = regionType('commercial', '#ff0000', 1, commercialComp)
nonCommercial = regionType('nonCommercial', '#0000ff', -1, nonCommercialComp)

city = region(600, nonCommercial, [0,0], False)
#city.tessellate(2)

testLine = line([[50,50],[100,50],[50,100],[100,100]],1)
#testLine.render()

root.mainloop()

#quit()
