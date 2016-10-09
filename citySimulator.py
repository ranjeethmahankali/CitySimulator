from tkinter import *
import math
from random import randint
import planeVec as pv
import scoring as sc

root = Tk()
root.title('City Simulator')
canvas = Canvas(root, width = 600, height = 600)
canvas.pack()

regType = dict()#this list contains all the types of regions
lines = list()#this is the list of all line objects in the document
fences = list()#this is the list of all fence objects in the document

def error(msg):
    print('Error: '+msg)

def exportCanvas(fileName):
    canvas.update()
    canvas.postscript(file = fileName+'.eps', colormode='color')

def sortChildren_random(childList):#sort method o determine the fate of the child spaces.
    #currently this sort method only sorts randomly
    childNum = len(childList)
    weirdChildNum = randint(0, childNum - 1)

    if childList[weirdChildNum].type.name == 'commercial':
        childList[weirdChildNum].type = regType['nonCommercial']
    elif childList[weirdChildNum].type.name == 'nonCommercial':
        childList[weirdChildNum].type = regType['commercial']

def sortChildren_lines(parentReg, lineList):
    #this method will sort according to the connectivity to the lineElements
    flipChildNum = 0

    if parentReg.type.name == 'nonCommercial':
        maxIntSum = 0
        minDistance = math.inf

        c = 0
        while c < len(parentReg.child):
            intSum = 0
            minDist = math.inf
            l = 0
            while l < len(lineList):
                intSum += parentReg.child[c].intercept(lineList[l])
                dist = parentReg.child[c].minDistFromLine(lineList[l])
                if dist < minDist:
                    minDist = dist
                l += 1

            if intSum > maxIntSum:
                maxIntSum = intSum
                flipChildNum = c
            elif intSum == maxIntSum:
                if minDist < minDistance:
                    minDistance = minDist
                    flipChildNum = c

            c += 1

        parentReg.child[flipChildNum].type = regType['commercial']

    elif parentReg.type.name == 'commercial':
        minIntSum = math.inf
        minDistance = 0

        c = 0
        while c < len(parentReg.child):
            intSum = 0
            minDist = math.inf
            l = 0
            while l < len(lineList):
                intSum += parentReg.child[c].intercept(lineList[l])
                dist = parentReg.child[c].minDistFromLine(lineList[l])
                if dist < minDist:
                    minDist = dist
                l += 1

            if intSum < minIntSum:
                minIntSum = intSum
                flipChildNum = c
            elif intSum == minIntSum:
                if minDist > minDistance:
                    minDistance = minDist
                    flipChildNum = c

            c += 1

        parentReg.child[flipChildNum].type = regType['nonCommercial']

class line:#this class is for the line element objects
    def __init__(self, pointArray):
        self.point = pointArray
        self.graphic = None

        #this attribute represents how far up this element is in hierarchy
        #if the value is high then the actual importance is small
        self.scale = 0

        lines.append(self)

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

        #this represents the scale of the region
        #0 is the biggest region and the smaller regions have increasing values
        self.scale = 0

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

    def addChild(self, childReg):
        if not isinstance(childReg, region):
            error('This object is not a region object '
                  'hence cannot be added as a child to another region')
            return

        if not childReg.parent is None:
            error('This space already has a parent so cannot be '
                  'given a new parent')
            return

        self.child.append(childReg)
        childReg.parent = self

        childReg.scale = self.scale + 1

    #this method calculates the intercept of a line object within the region
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

                    iPt = pv.intersectionPt(p1, p2, s1, s2)
                    if not iPt is None:
                        intPt.append(iPt)

                    s += 1

                if len(intPt) >= 2:
                    iSum += pv.mod(pv.vDiff(intPt[0], intPt[1]))

            i += 1
        
        return iSum

    #returns true of the point lies inside the region
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
        #done counting the number of children and decided the weird child in advance

        #print(childNum)

        c = 0
        while c < childNum:
            colNum = c % math.sqrt(childNum)
            rowNum = (c-colNum)/math.sqrt(childNum)
            childPos = [self.pos[0] + colNum*childSize, self.pos[1] + rowNum*childSize]

            newChild = region(childSize, self.type, childPos, False)
            #self.child.append(newChild)
            #newChild.parent = self
            self.addChild(newChild)

            c += 1

        sortChildren_lines(self, lines)#changing the children

        for childRegion in self.child:
            childRegion.tessellate(genNum - 1)

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

    def minDistFromLine(self, lineObj):
        center = pv.vSum(self.pos, [self.size/2, self.size/2])
        return lineObj.minDistFrom(center)

    def scaleDiff(self, region):
        return


class fence:
    #fences are closed polyline which mark our the areas which donot belong to any region or city
    #my intention is to use fences to mark city boundaries and areas in which a city cannot grow or exist
    #like campuses and lakes etc.
    def __init__(self, verticesList):
        self.vertex = verticesList
        self.graphic = None

        vertSum = [0,0]
        for vert in self.vertex:
            vertSum = pv.vSum(vertSum, vert)

        self.center = pv.vPrd(vertSum, 1/len(self.vertex))

        fences.append(self)

    def hasPoint(self, pos):#this method returns a boolean whether pos lies inside this fence or not
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

    def area(self):#this method returns the area of the polygon
        #this method does not work for self interscting polygons, but other wise works for both convex and concave
        i = 0
        ArSum = 0
        while i < len(self.vertex):
            j = (i+1)%len(self.vertex)
            ArSum += self.vertex[i][0]*self.vertex[j][1]
            ArSum -= self.vertex[i][1]*self.vertex[j][0]

            i += 1

        polyArea = abs(ArSum)/2
        return polyArea