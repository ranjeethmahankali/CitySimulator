#this is the 2d vector functions library
import math

def dist(x1,y1,x2,y2):#returns the distance between the two points
    return math.sqrt(((x2-x1)**2)+((y2-y1)**2))

def lineAngle(x0,y0,x1,y1):#returns the inclination of the line with positive x-axis in radians
    angle = None

    if x1 > x0:
        if y1 > y0:
            angle = math.atan((y1-y0)/(x1-x0))
        elif y1 == y0:
            angle = 0;
        else:
            angle = math.atan((y1-y0)/(x1-x0)) + (2*math.pi)
    elif x1 == x0:
        if y1 > y0:
            angle = math.pi/2
        elif y1 == y0:
            angle = None
        else:
            angle = (3*math.pi)/2
    else:
        if y1 > y0:
            angle = math.atan((y1-y0)/(x1-x0)) + math.pi
        elif y1 == y0:
            angle = math.pi
        else:
            angle = math.atan((y1-y0)/(x1-x0)) + math.pi

    return angle

def mod(vec):#returns the magnitude of a vector
    return math.sqrt((vec[0]**2)+(vec[1]**2))

def dot(vec1, vec2):#returns the dot product of these two vectors
    return (vec1[0]*vec2[0])+(vec1[1]*vec2[1])

def cosAng(vec1, vec2):#returns the cos of the angle between these two vectors
    if (mod(vec1) != 0 and mod(vec2) != 0):
        return dot(vec1,vec2)/(mod(vec1)*mod(vec2))
    else:
        return None
        print("Division by zero in cosAng function")

def vPrd(vec, sc):#returnss the product of the vector with scalar
    return [vec[0]*sc, vec[1]*sc]

def vSum(vec1, vec2):#returns the su of the two vectors
    return [vec1[0]+vec2[0], vec1[1]+vec2[1]]

def vDiff(vec1, vec2):#returns vec1-vec2
    return [vec1[0]-vec2[0], vec1[1]-vec2[1]]

def unitV(vec):#returns the unit vector parallel to the given vector
    length = mod(vec)
    if length == 0:
        return [0,0]
    else:
        return [vec[0]/length, vec[1]/length]

def lineDist(p1, p2, p):#gives a vector that is a perpendicular dropped from p to the line joining p1 and p2
    line = vDiff(p2, p1) #line joining p1 to p2
    vec = vDiff(p, p1) #line joining p1 to p

    uLine = unitV(line) #unit vector along line vector
    length = dot(line, vec)/mod(line) #length of component of vec along line

    dLine = vPrd(uLine, length)

    return vDiff(dLine, vec)

def vCross(v1, v2):
    #this method returns the cross product of the two vectors v1 and v2
    #in the order v1 x v2
    #since this is a plane vector library and all the vectors are 2D, the cross product
    #is always perpendicular to the place and has no way to be represented in this library
    #which doesn't supprt a third term in the ordered pair.
    #hence This method will only return the magnitude of the cross product

    return (v1[0]*v2[1] - v1[1]*v2[0])

