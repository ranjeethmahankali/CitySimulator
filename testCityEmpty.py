import citySimulator as cs

commercialComp = {'commercial':7, 'nonCommercial':1, 'industrial': 1}
nonCommercialComp = {'nonCommercial':8, 'commercial':1}
industrialComp = {'nonCommercial':1, 'industrial':8}

commercial = cs.regionType('commercial', '#ff0000', commercialComp)
nonCommercial = cs.regionType('nonCommercial', '#0000ff', nonCommercialComp)
industrial = cs.regionType('industrial', '#ff0000', industrialComp)

#assigning relation factors
commercial.addRel(nonCommercial, 0.1)
commercial.addRel(industrial, 1)
industrial.addRel(nonCommercial, 0.1)

city = cs.region(600, nonCommercial, [0,0], False)

city.tessellate(4)
city.render()

#campus.render()

cs.root.mainloop()
#print(campus.area())