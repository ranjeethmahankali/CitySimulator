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

        #print(a1, a2, b1, b2)

        if checkA <= 0 and checkB <=0 :
            return intPt
        else:
            #this means the infinite lines intersect but the segments don't
            return None

class line:#this class is for the line element objects
    def __init__(self, pointArray):
        self.point = pointArray
        self.graphic = None

    def minDistFrom(self, pos):#returns the minimum distance from pos to this line object
        i = 0
        minDist = math.inf
        while i < len(self.point)-1:
            a = self.point[i]
            b = self.point[i+1]

            dt = pv.lineDist(a,b,pos)
            pt = pv.vSum(pos, dt)

            if pv.dot(pv.vDiff(pt,a),pv.vDiff(pt,b)) <= 0:
                distance = pv.mod(dt)
            else:
                dtA = pv.mod(pv.vDiff(pos,a))
                dtB = pv.mod(pv.vDiff(pos,b))

                distance = min(dtA, dtB)

            if distance < minDist:
                minDist = distance

            i += 1

        return minDist

    def render(self):#this method renders the line element on screen
        #render the line element here
        self.graphic = canvas.create_line(self.point, fill='black', width = 2)

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

        if deg45 >= angle or angle > 7*deg45:
            return 0
        
        elif deg45 < angle <= 3*deg45:
            return 1
        
        elif 3*deg45 < angle <= 5*deg45:
            return 2
        
        elif 5* deg45 < angle <= 7*deg45:
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
            #print(i, iSum)
            p1 = lineObj.point[i]
            p2 = lineObj.point[i+1]

            if self.hasPoint(p1) and self.hasPoint(p2):
                iSum += pv.mod(pv.vDiff(p2,p1))
            else:
                s = 0
                intPt = list()
                while s < len(sq) and len(intPt) <= 2:
                    s1 = sq[s]
                    s2 = sq[(s+1)%4]

                    iPt = intersectionPt(p1, p2, s1, s2)
                    if not iPt is None:
                        intPt.append(iPt)

                    s += 1

                if len(intPt) >= 2:
                    iSum += pv.mod(pv.vDiff(intPt[0], intPt[1]))

            i += 1
        
        return iSum

    def hasPoint(self, pos): #returns true or false on whether the point pos is in the region or not
        checkXLims = self.pos[0] <= pos[0] <= self.pos[0] + self.size
        checkYLims = self.pos[1] <= pos[1] <= self.pos[1] + self.size

        return checkXLims and checkYLims

    def tessellate(self, genNum=1):
        self.delete()
        #deleting any previous renderings of this region
        if genNum <= 0:
            #self.render()
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
        if len(self.child) == 0:
            endPos = [self.pos[0]+self.size, self.pos[1]+self.size]
            self.graphic = canvas.create_rectangle(self.pos[0], self.pos[1], endPos[0], endPos[1], fill=self.type.color, outline = self.type.color)
        else:
            for ch in self.child:
                ch.render()

    def delete(self):
        canvas.delete(self.graphic)
        self.graphic = None

class fence:
    #fences are closed polyline which mark our the areas which donot belong to any region or city
    #my intention is to use fences to mark city boundaries and areas in which a city cannot grow or exist
    #like campuses and lakes etc.
    def __init__(self, verticesList):
        self.vertex = verticesList
        self.graphic = None

    def hasPoint(self, pos):#this method returns a boolean whether pos lies inside this fence or not
        #need to do research about figuring out how to verify whether a
        #point lies inside a random polygon
        crossCount = 0 #counting the number of times the polugon is crossed
        rayVec = [1,0] # I am about to write a ray casting algorithm to the right

        i = 0
        while i < len(self.vertex):
            v1 = self.vertex[i]
            v2 = self.vertex[(i+1)%len(self.vertex)]

            lineVec = pv.unitV(pv.vDiff(v2,v1))

            lineCross = pv.vCross(rayVec, lineVec)
            if lineCross == 0:
                #the lines are parallel
                i += 1
                # the increment of i is neccessary because this is a while loop not for loop
                # continue statement doesnot automatically do it
                continue

            othCross = pv.vCross(pv.vDiff(v1,pos),lineVec)
            param = othCross/lineCross

            if param == 0:
                return True
            if param > 0:
                #checking if atleast one of the vertices lie below the threshold (look up oneNote notebook)
                if v1[1] < pos[1] or v2[1] < pos[1]:
                    crossCount += 1

            i += 1

        if crossCount%2 == 0:
            return False
        else:
            return True

    def render(self):#renders the fence on canvas
        #the self.vertex array is not a cyclic list so the polygon will not be closed
        self.graphic = canvas.create_polygon(self.vertex, fill='black', stipple = 'gray75')


commercialComp = {'commercial':8, 'nonCommercial':1}
nonCommercialComp = {'nonCommercial':8, 'commercial':1}

commercial = regionType('commercial', '#ff0000', 1, commercialComp)
nonCommercial = regionType('nonCommercial', '#0000ff', -1, nonCommercialComp)

city = region(600, nonCommercial, [0,0], False)
city.tessellate(3)
city.render()

NH9 = line([[0,60],[200,150],[400,450],[600,540]])
NH9.render()

print(NH9.minDistFrom([350,250]))

campus = fence([[100,200],[200,100],[300,200],[300,400],[200,300],[100,300]])
campus.render()

root.mainloop()
#quit()