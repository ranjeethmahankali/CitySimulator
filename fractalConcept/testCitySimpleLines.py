import citySimulator as cs

commercialComp = {'commercial':7, 'nonCommercial':1, 'industrial': 1}
nonCommercialComp = {'nonCommercial':8, 'commercial':1}
industrialComp = {'nonCommercial':1, 'industrial':8}

commercial = cs.regionType('commercial', '#ff0000', commercialComp)
nonCommercial = cs.regionType('nonCommercial', '#0000ff', nonCommercialComp)
industrial = cs.regionType('industrial', '#ff0000', industrialComp)

#print(nonCommercial.compBuffer)

#assigning relation factors
commercial.addRel(nonCommercial, 0.1)
commercial.addRel(industrial, 1)
industrial.addRel(nonCommercial, 0.1)

city = cs.region(600, nonCommercial, [0,0], False)

testLineV = cs.line([[300,0],[300,600]])
testLineV.relation['commercial'] = 100
testLineV.relation['nonCommercial'] = -100
testLineV.relation['industrial'] = 100

'''
NH9 = cs.line([[0,60],[200,150],[400,450],[600,540]])
NH9.relation['commercial'] = 100
NH9.relation['nonCommercial'] = -100
NH9.relation['industrial'] = -20

musi = cs.line([[0,350],[600,250]])
musi.relation['commercial'] = 100
musi.relation['nonCommercial'] = -100
musi.relation['industrial'] = -20

campus = cs.fence([[100,200],[200,100],[300,200],[300,400],[200,300],[100,300]])
'''

city.tessellate(4)
city.render()
testLineV.render()

'''
NH9.render()
musi.render()
'''
#campus.render()

cs.root.mainloop()
#print(campus.area())