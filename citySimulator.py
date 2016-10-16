from tkinter import *
import math
from random import randint
import planeVec as pv

root = Tk()
root.title('City Simulator')
canvas = Canvas(root, width = 600, height = 600)
canvas.pack()

regType = dict()#this list contains all the types of regions
lines = list()#this is the list of all line objects in the document
fences = list()#this is the list of all fence objects in the document

#one matrix to map relations between region types in pairs
#each line element should have a set of relationship factors with each region type

#here the standard program parameter definitions begin

#this is the relation of a regiontype with itself
regSelfRelation = 1

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

class regionType:
    def __init__(self, typeName, typeColor, composition):
        self.name = typeName
        self.color = typeColor

        self.comp = composition

        self.compBuffer = list()
        self.makeCompBuffer()

        self.relation = dict()
        self.agglomerationFactor = 0.1

        regType[self.name] = self

    #adds a relation factor relValue between self and regType
    def addRel(self, otherRegType, relvalue):
        relvalue = float(relvalue)
        self.relation[otherRegType.name] = relvalue
        otherRegType.relation[self.name] = relvalue

    #this method appropriately populates the compBuffer list
    def makeCompBuffer(self):
        self.compBuffer = list()

        tempList = list()
        for typeName in self.comp:
            tempList.append([typeName, self.comp[typeName]])

        i = 0
        while i < len(tempList)-1:
            j = 0
            while j < len(tempList)-i-1:
                if tempList[j][1] > tempList[j+1][1]:
                    tempVar = tempList[j][:]
                    tempList[j] = tempList[j+1][:]
                    tempList[j+1] = tempVar

                j += 1

            i += 1

        for temp in tempList:
            i = 0
            while i < temp[1]:
                self.compBuffer.append(temp[0])
                i += 1

    #this method returns the relation factor of this regType with another
    def rel(self, otherRegType):
        if otherRegType is self:
            global regSelfRelation
            return regSelfRelation
        else:
            return self.relation[otherRegType.name]

class region:
    def __init__(self, regSize, rType, regPosition, toRender = True):
        self.size = regSize
        self.type = rType
        #this pos attribute is the postition of the top left corner
        self.pos = regPosition
        self.center = pv.vSum(self.pos, [self.size/2, self.size/2])
        #this is the index in the 3x3 matrix among it's siblings
        #for example the middle one is [2,2]
        self.posMat = None
        #the id of the graphic if and when created
        self.graphic = None

        #this contains the scores of this region w.r.t each regiontype with
        #the name of the regiontype as the key of the dictionary
        self.score = dict()
        global regType
        for typeName in regType:
            self.score[typeName] = 0

        #this represents the scale of the region
        #0 is the biggest region and the smaller regions have increasing values
        self.scale = 0

        self.child = [] #this is a list of children of this region
        self.parent = None

        if toRender:
            self.render()

    # this returns the relative position of the point pt
    # w.r.t this region. Look up the notebook for more on the relative position
    def relPosOf(self, pt):
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

    #this method adds childReg as a child to this region with all the necessary
    #changes and updates propogated and all exceptions handled
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

    #breaks the region into its children and also assigns types to children
    def tessellate(self, genNum=1):
        self.delete()
        #deleting any previous renderings of this region
        if genNum <= 0:
            #self.render()
            return

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
            #newly created children are made of same type as the parent

            self.addChild(newChild)

            c += 1

        #assigning new types to children
        #sortChildren_lines(self, lines)#old mechanism
        self.sortChildren()#new mechanism

        for childRegion in self.child:
            childRegion.tessellate(genNum - 1)

    #renders the region onto the canvas
    def render(self):
        if len(self.child) == 0:
            endPos = [self.pos[0]+self.size, self.pos[1]+self.size]
            self.graphic = canvas.create_rectangle(self.pos[0], self.pos[1], endPos[0], endPos[1], fill=self.type.color, outline = self.type.color)
        else:
            for ch in self.child:
                ch.render()

    #deletes the region from the canvas only
    def delete(self):
        canvas.delete(self.graphic)
        self.graphic = None

    #returns the minimum distance of this region's center from a line object
    def minDistFromLine(self, lineObj):
        center = pv.vSum(self.pos, [self.size/2, self.size/2])
        return lineObj.minDistFrom(center)

    #returns the difference in scales of this and another region
    def scaleDiff(self, otherReg):
        diff = self.scale - otherReg.scale
        return diff

    #this method calculates and assigns scores to all the children
    def evaluate_lines(self):
        global regType

        #evaluation based on linear elements - begins
        global lines
        for typeName in regType:
            for ln in lines:
                iLen = self.intercept(ln)
                if iLen == 0: iLen = 1
                #reason for above line
                #if iLen is 0 then it makes the minDist comparisons meaningless
                #that is why we want it to be a non zero value but small

                d = ln.minDistFrom(self.center)
                diffNum = abs(self.scale - ln.scale)

                scoreVal = ln.relation[typeName]*iLen
                if d == 0: d = 1#this line is merely to handle the zero division
                scoreVal /= math.pow(d,diffNum)

                self.score[typeName] += scoreVal

        # evaluation based on linear elements - ends
    #this method calculates and assigns scores to all the children
    def evaluate(self):
        global regType

        #evaluation based on linear elements - begins
        global lines
        for typeName in regType:
            for ln in lines:
                iLen = self.intercept(ln)
                if iLen == 0: iLen = 1
                #reason for above line
                #if iLen is 0 then it makes the minDist comparisons meaningless
                #that is why we want it to be a non zero value but small

                d = ln.minDistFrom(self.center)
                diffNum = abs(self.scale - ln.scale)

                scoreVal = ln.relation[typeName]*iLen
                if d == 0: d = 1#this line is merely to handle the zero division
                scoreVal /= math.pow(d,diffNum)

                self.score[typeName] += scoreVal
        # evaluation based on linear elements - ends

        baseReg = None
        if not self.parent is None:
            if not self.parent.parent is None:
                baseReg = self.parent.parent
            else:
                baseReg = self.parent
        else:
            baseReg = self

        while True:
            for ch in baseReg.child:
                scDiff = self.scaleDiff(ch)
                if scDiff >= 0 and (not ch is self.parent):
                    scoreVal = ch.size #making proportional to size
                    d = pv.mod(pv.vDiff(self.center, ch.center))
                    if d == 0:d = 1

                    scoreVal /= math.pow(d,scDiff+1)
                    scoreVal *= ch.type.agglomerationFactor

                    #self.score[ch.type.name] += scoreVal
                    for typeName in regType:
                        self.score[typeName] += regType[typeName].rel(ch.type)*scoreVal

            if baseReg.parent is None:
                break
            else:
                baseReg = baseReg.parent

    #this method first evaluates and then assigns types to all the children
    def sortChildren(self):
        for ch in self.child:
            #ch.evaluate_lines()
            ch.evaluate()
        #above loop scored all the children and now we can begin sorting them

        #each member of this dictionary is a list while the keys are the names
        #of the region types. Each list has the children sorted in descending
        #order of scores w.r.t to the region type whose name is the key
        scoreBuffer = dict()

        for typeName in self.type.comp:
            scoreBuffer[typeName] = self.child[:]
            #now sorting them according to score - begins
            i = 0
            while i < len(scoreBuffer[typeName])-1:
                j = 0
                while j < len(scoreBuffer[typeName])-i-1:
                    if scoreBuffer[typeName][j].score[typeName] < scoreBuffer[typeName][j+1].score[typeName]:
                        temp = scoreBuffer[typeName][j]
                        scoreBuffer[typeName][j] = scoreBuffer[typeName][j+1]
                        scoreBuffer[typeName][j+1] = temp
                        #above 3 lines swapped the two schildren based on their scores

                    j += 1

                i += 1

        for typeName in self.type.compBuffer:
            selectedChild = scoreBuffer[typeName][0]
            selectedChild.type = regType[typeName]

            for tName in scoreBuffer:
                scoreBuffer[tName].remove(selectedChild)

class line:#this class is for the line element objects
    def __init__(self, pointArray):
        self.point = pointArray
        self.graphic = None

        #this attribute represents how far up this element is in hierarchy
        #if the value is high then the actual importance is small
        self.scale = 0

        #this contains the relationship factor of thsi line with each regionType
        #the names of the regionTypes are the keys in the dictionary
        self.relation = dict()

        global lines
        lines.append(self)

    # returns the minimum distance from pos to this line object
    def minDistFrom(self, pos):
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

    # this method renders the line element on screen
    def render(self):
        #render the line element here
        self.graphic = canvas.create_line(self.point, fill='black', width = 2)

    #deletes the graphic of the line from the canvas only
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

        vertSum = [0,0]
        for vert in self.vertex:
            vertSum = pv.vSum(vertSum, vert)

        self.center = pv.vPrd(vertSum, 1/len(self.vertex))

        fences.append(self)

    #this method needs some serious fixing
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

            #checking if the point is on the perimeter
            if param == 0:
                return True
            elif param > 0:
                #checking if atleast one of the vertices lie below the threshold (look up oneNote notebook)
                if v1[1] < pos[1] or v2[1] < pos[1]:
                    crossCount += 1

            i += 1

        if crossCount%2 == 0:
            return False
        else:
            return True

    # renders the fence on canvas
    def render(self):
        self.graphic = canvas.create_polygon(self.vertex, fill='black', stipple = 'gray75')

    # this method returns the area of the polygon
    # this method does not work for self interscting polygons, but other wise works for both convex and concave
    def area(self):
        i = 0
        ArSum = 0
        while i < len(self.vertex):
            j = (i+1)%len(self.vertex)
            ArSum += self.vertex[i][0]*self.vertex[j][1]
            ArSum -= self.vertex[i][1]*self.vertex[j][0]

            i += 1

        polyArea = abs(ArSum)/2
        return polyArea