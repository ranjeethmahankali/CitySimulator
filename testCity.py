import citySimulator as cs

commercialComp = {'commercial':7, 'nonCommercial':1, 'industrial': 1}
nonCommercialComp = {'nonCommercial':8, 'commercial':1}
industrialComp = {'nonCommercial':1, 'industrial':6, 'commercial':2}

commercial = cs.regionType('commercial', '#ff0000', commercialComp)
nonCommercial = cs.regionType('nonCommercial', '#0000ff', nonCommercialComp)
industrial = cs.regionType('industrial', '#00ff00', industrialComp)

#print(nonCommercial.compBuffer)

#assigning relation factors
commercial.addRel(nonCommercial, -0.1)
commercial.addRel(industrial, 1)
industrial.addRel(nonCommercial, -0.9)

city = cs.region(600, nonCommercial, [0,0], False)


NH9 = cs.line([[0,60],[200,150],[400,450],[600,540]])
NH9.relation['commercial'] = 100
NH9.relation['nonCommercial'] = -100
NH9.relation['industrial'] = -20

musi = cs.line([[0,350],[600,250]],'#00ffff')
musi.relation['commercial'] = 100
musi.relation['nonCommercial'] = -100
musi.relation['industrial'] = -20

campus = cs.fence([[100,200],[200,100],[300,200],[300,400],[200,300],[100,300]])

city.tessellate(50)
city.render()

NH9.render()
musi.render()

#campus.render()
cs.root.mainloop()
#print(campus.area())