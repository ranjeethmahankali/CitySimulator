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

def intersectionPt(a1, a2, b1, b2):
    #this method returns the point of intersection of two lines.
    #one is a segment from a1 to a2 and the other one is a segment from b1 to b2

    uA = pv.unitV(pv.vDiff(a2,a1))
    uB = pv.unitV(pv.vDiff(b2,b1))
    UAxUB = pv.vCross(uA, uB)

    if UAxUB == 0:
        #the lines are parallel so there is no interesection
        return None
    else:
        aParam = (pv.vCross(pv.vDiff(b1,a1),uB))/UAxUB

        intPt = pv.vSum(a1, pv.vPrd(uA, aParam))
        #the above point is the intersection point but now we have to check
        #if it lies on both the segments

        checkA = pv.dot(pv.vDiff(intPt, a1), pv.vDiff(intPt, a2))
        checkB = pv.dot(pv.vDiff(intPt, b1), pv.vDiff(intPt, b2))

        if checkA <= 0 and checkB <=0 :
            return intPt
        else:
            #this means the infinite lines intersect but the segments don't
            return None
    

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

    def relPosOf(self, pt):#this returns the relative position of the point pt
        # w.r.t this region. Look up the notebook for more on the relative position
        center = pv.vSum(self.pos, [self.size/2, self.size/2])

        angle = pv.lineAngle(center[0], center[1], pt[0], pt[1])

        deg45 = math.pi/4

        if angle <= deg45 and angle > 7*deg45:
            return 0
        
        elif angle > deg45 and angle <= 3*deg45:
            return 1
        
        elif angle > 3*deg45 and angle <= 5*deg45:
            return 2
        
        elif angle > 5* deg45 and angle <= 7*deg45:
            return 3
        

    def intercept(self, lineObj):
        #corners of the sqaure region
        sq = list()
        sq.append([self.pos[0]+self.size, self.pos[1]])
        sq.append([self.pos[0]+self.size, self.pos[1]+self.size])
        sq.append([self.pos[0], self.pos[1]+self.size])
        sq.append(self.pos)
        
        iSum = 0 #this is the sum of intercepts that we will continue to increment
        
        i = 0
        while i < len(lineObj.point)-1:
            p1 = lineObj.point[i]
            p2 = lineObj.point[i+1]

            if self.hasPoint(p1) and self.hasPoint(p2):
                iSum += pv.mod(pv.vDiff(p2,p1))

            else:
                #check for p1
                rPos1 = self.relPos(p1)
                s1 = sq[rPos1]
                s2 = sq[(rPos1+1)%4]
                intPt1 = intersectionPt(s1,s2,p1,p2)

                rPos2 = self.relPos(p2)

                s1 = sq[rPos2]
                s2 = sq[(rPos2+1)%4]

                intPt2 = intersectionPt(s1,s2,p1,p2)

                if intPt1 is None and intPt2 is None:
                    iSum += 0
                elif intPt1 is None:
                    #do something over here

                
                
            i += 1
        
        return 0

    def hasPoint(self, pos): #returns true or false on whether the point pos is in the region or not
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

testLine = line([[50,50],[100,50],[50,100],[100,100]],1)

root.mainloop()

#quit()
